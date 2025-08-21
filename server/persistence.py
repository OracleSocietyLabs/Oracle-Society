
from pathlib import Path
from typing import Dict, Any, List
import json, time

class SnapshotManager:
    def __init__(self, data_dir: str = "./data"):
        self.base = Path(data_dir)
        self.snap_dir = self.base / "snapshots"
        self.base.mkdir(parents=True, exist_ok=True)
        self.snap_dir.mkdir(parents=True, exist_ok=True)
        self.wal_path = self.base / "events.jsonl"

    def save_snapshot(self, world_state: Dict[str, Any], last_seq: int, name: str | None = None) -> str:
        ts = time.strftime("%Y%m%d-%H%M%S")
        nm = (name or "auto").replace("/", "_")
        path = self.snap_dir / f"{ts}-{nm}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"last_seq": last_seq, "world": world_state}, f)
        return str(path)

    def list_snapshots(self) -> List[str]:
        return sorted([str(p) for p in self.snap_dir.glob("*.json")])

    def load_snapshot(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def wal_append(self, event: dict):
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def wal_tail_since(self, seq: int) -> List[dict]:
        out = []
        if not self.wal_path.exists(): return out
        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                if int(obj.get("seq", 0)) > seq:
                    out.append(obj)
        return out

    def wal_compact(self, keep_after_seq: int):
        if not self.wal_path.exists(): return
        tmp = self.wal_path.with_suffix(".tmp")
        with open(self.wal_path, "r", encoding="utf-8") as f, open(tmp, "w", encoding="utf-8") as out:
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                if int(obj.get("seq", 0)) > keep_after_seq:
                    out.write(json.dumps(obj) + "\n")
        tmp.replace(self.wal_path)
