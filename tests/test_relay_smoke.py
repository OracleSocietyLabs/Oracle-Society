
import threading, time, json, urllib.request
from server.relay_server import serve

def _json(url, data=None):
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type":"application/json"}, method="POST")
    else:
        req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=2) as r:
        ct = r.headers.get("Content-Type","")
        body = r.read()
        return json.loads(body.decode("utf-8")) if "application/json" in ct else body.decode("utf-8")

def test_relay_endpoints():
    t = threading.Thread(target=serve, kwargs={"host":"127.0.0.1","port":8022}, daemon=True)
    t.start(); time.sleep(0.4)
    base = "http://127.0.0.1:8022"
    snap = _json(base + "/show/snapshot")
    assert "areas" in snap
    _json(base + "/area_bump", {"name":"Market","dim":"security","delta":-2})
    evs = _json(base + "/events/since/0")
    assert "events" in evs
