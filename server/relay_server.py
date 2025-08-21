
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, threading, time, os

try:
    from .metrics import REGISTRY, Timer
    from .world import EventBus, Adapter
    from .persistence import SnapshotManager
    from .ratelimit import RateLimiter
except ImportError:
    from metrics import REGISTRY, Timer
    from world import EventBus, Adapter
    from persistence import SnapshotManager
    from ratelimit import RateLimiter

DATA_DIR = os.environ.get("ORACLE_DATA_DIR", "./data")
RATE_PER_SEC = float(os.environ.get("ORACLE_RATE_PER_SEC", "3.0"))
RATE_CAP     = int(os.environ.get("ORACLE_RATE_CAP", "5"))
DSL_LIMIT    = int(os.environ.get("ORACLE_DSL_LIMIT", "16"))
BUS_MAX      = int(os.environ.get("ORACLE_BUS_MAX", "1000"))
SNAPSHOT_EVERY = int(os.environ.get("ORACLE_SNAPSHOT_EVERY", "120"))

bus = EventBus(max_events=BUS_MAX)
world = Adapter(bus)
snaps = SnapshotManager(DATA_DIR)
limiter = RateLimiter(rate_per_sec=RATE_PER_SEC, capacity=RATE_CAP)
active_dsl = []

def recover_on_start():
    try:
        lst = snaps.list_snapshots()
        if lst:
            latest = lst[-1]
            obj = snaps.load_snapshot(latest)
            world.from_snapshot(obj["world"]); last_seq = int(obj.get("last_seq", 0))
            tail = snaps.wal_tail_since(last_seq)
            for e in tail: bus.append(e["verb"], e["context"])
            print(f"[recover] {latest} last_seq={last_seq}, replayed={len(tail)}")
        else:
            print("[recover] no snapshots; fresh start")
    except Exception as e:
        print("[recover] failed:", e)

recover_on_start()

def cors(handler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

def send_json(handler, code, data):
    body = json.dumps(data).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type","application/json"); cors(handler)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers(); handler.wfile.write(body)

class App(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204); cors(self); self.end_headers()

    def do_GET(self):
        REGISTRY.counter("http_requests_total","HTTP").inc(1, labels={"m":"GET","p":self.path})
        if self.path.startswith("/show/snapshot"):
            return send_json(self,200,world.snapshot())
        if self.path.startswith("/events/since/"):
            try: seq=int(self.path.split("/",3)[3])
            except: seq=0
            return send_json(self,200,{"events":bus.since(seq)})
        if self.path == "/metrics":
            data = REGISTRY.render_prometheus().encode("utf-8")
            self.send_response(200); self.send_header("Content-Type","text/plain; version=0.0.4")
            cors(self); self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data); return
        if self.path.startswith("/events/stream"):
            self.send_response(200); self.send_header("Content-Type","text/event-stream")
            self.send_header("Cache-Control","no-cache"); self.send_header("Connection","keep-alive"); cors(self)
            self.end_headers(); last=0
            try:
                while True:
                    items = bus.wait_stream(last, timeout=0.5)
                    for e in items:
                        last = e.seq
                        payload = json.dumps({"seq": e.seq, "verb": e.verb, "context": e.context})
                        self.wfile.write(f"data: {payload}\n\n".encode("utf-8")); self.wfile.flush()
                        snaps.wal_append({"seq": e.seq, "verb": e.verb, "context": e.context})
                    time.sleep(0.05)
            except Exception:
                return
        if self.path.startswith("/admin/list"):
            return send_json(self,200,{"snapshots":snaps.list_snapshots()})
        self.send_response(404); self.end_headers()

    def do_POST(self):
        REGISTRY.counter("http_requests_total","HTTP").inc(1, labels={"m":"POST","p":self.path})
        n = int(self.headers.get("content-length","0") or "0")
        raw = self.rfile.read(n).decode("utf-8") if n>0 else "{}"
        obj = json.loads(raw or "{}")

        if self.path == "/area_bump":
            key = f"area_bump:{obj.get('name','Market')}"
            if not limiter.allow(key):
                REGISTRY.counter("rate_limited_total","Ratelimited").inc(1, labels={"k":key})
                return send_json(self,429,{"ok":False,"error":"rate limit"})
            area=obj.get("name","Market"); dim=obj.get("dim","security"); delta=float(obj.get("delta",0))
            world.area_bump(area, dim, delta)
            return send_json(self,200,{"ok":True})

        if self.path == "/rumor":
            key = "rumor"
            if not limiter.allow(key):
                REGISTRY.counter("rate_limited_total","Ratelimited").inc(1, labels={"k":key})
                return send_json(self,429,{"ok":False,"error":"rate limit"})
            world.rumor(obj.get("hypothesis","h"), obj.get("source","src"), int(obj.get("polarity",1)), float(obj.get("reliability",0.9)))
            return send_json(self,200,{"ok":True})

        if self.path == "/knob":
            world.knob(obj.get("name","area_half_life"), float(obj.get("value",240)))
            return send_json(self,200,{"ok":True})

        if self.path == "/dsl_load":
            if len(active_dsl) >= DSL_LIMIT:
                return send_json(self,429,{"ok":False,"error":"too many DSL rules"})
            rule = obj.get("rule",""); active_dsl.append(rule); world.dsl_load(rule)
            return send_json(self,200,{"ok":True, "active": len(active_dsl)})

        if self.path == "/dsl_exec":
            res = world.dsl_exec(obj.get("area","Market"), obj.get("outcome","calm"))
            return send_json(self,200,res)

        if self.path == "/admin/snapshot":
            path = snaps.save_snapshot(world.snapshot(), bus.last_seq, obj.get("name"))
            return send_json(self,200,{"ok":True,"path":path})

        if self.path == "/admin/restore":
            name = obj.get("name"); 
            if not name: return send_json(self,400,{"ok":False,"error":"name required"})
            data = snaps.load_snapshot(name); world.from_snapshot(data["world"])
            snap_seq = int(data.get("last_seq", 0)); bus.drop_until(snap_seq); snaps.wal_compact(snap_seq)
            return send_json(self,200,{"ok":True,"last_seq":snap_seq})

        if self.path == "/admin/compact":
            lst = snaps.list_snapshots()
            if not lst: return send_json(self,400,{"ok":False,"error":"no snapshots"})
            latest = lst[-1]; meta = snaps.load_snapshot(latest); keep_seq = int(meta.get("last_seq", 0))
            snaps.wal_compact(keep_seq); bus.drop_until(keep_seq)
            retain = int(obj.get("retain", 5))
            if len(lst) > retain:
                import os
                for p in lst[0:len(lst)-retain]:
                    try: os.remove(p)
                    except: pass
            return send_json(self,200,{"ok":True,"kept_after_seq":keep_seq})

        return send_json(self,404,{"error":"unknown"})

def snapshot_daemon(interval_sec=SNAPSHOT_EVERY, retain=5):
    while True:
        try:
            path = snaps.save_snapshot(world.snapshot(), bus.last_seq, name="auto")
            lst = snaps.list_snapshots()
            if len(lst) > retain:
                import os
                for p in lst[0:len(lst)-retain]:
                    try: os.remove(p)
                    except: pass
            meta = snaps.load_snapshot(lst[-1]); snaps.wal_compact(int(meta.get("last_seq", 0))); bus.drop_until(int(meta.get("last_seq", 0)))
            print("[auto-snapshot]", path)
        except Exception as e:
            print("[auto-snapshot] error:", e)
        time.sleep(interval_sec)

def serve(host="127.0.0.1", port=8011):
    t = threading.Thread(target=snapshot_daemon, daemon=True); t.start()
    httpd = HTTPServer((host, port), App)
    print(f"[serve] Relay ready at http://{host}:{port} (data dir: {DATA_DIR})")
    httpd.serve_forever()

if __name__ == "__main__":
    serve()
