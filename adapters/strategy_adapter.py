
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import re, copy

@dataclass
class TurnEvent:
    turn: int
    verb: str
    ctx: Dict[str, Any]

class StrategyAdapter:
    def __init__(self):
        self.turn = 0
        self.provinces: Dict[str, Dict[str, float]] = {
            "Market": {"security": 42.0, "prosperity": 55, "control": 50},
            "Harbor": {"security": 37.0, "prosperity": 48, "control": 52},
        }
        self.knobs = {"area_half_life": 720}
        self._dsl_rules: Dict[str, str] = {}
        self.events: List[TurnEvent] = []
        self._turn_snapshots: Dict[int, Dict[str, Any]] = {0: self._snapshot_state()}

    def next_turn(self):
        self.turn += 1
        self._turn_snapshots[self.turn] = self._snapshot_state()

    def area_bump(self, province: str, dim: str, delta: float):
        p = self.provinces.setdefault(province, {"security":50,"prosperity":50,"control":50})
        p[dim] = float(p.get(dim, 50)) + float(delta)
        self.events.append(TurnEvent(self.turn, "AreaBump", {"province":province,"dim":dim,"delta":delta}))

    def dsl_load(self, name: str, rule: str):
        self._dsl_rules[name] = rule
        self.events.append(TurnEvent(self.turn, "DSLLoaded", {"name":name,"size":len(rule)}))

    def dsl_exec(self, name: str, province: str, outcome: str):
        txt = self._dsl_rules.get(name, ""); applied=[]
        if "OUTCOMES" in txt and ("area." in txt):
            lines = txt.splitlines(); pick=False
            for ln in lines:
                if re.match(rf"\s*{re.escape(outcome)}\s*:", ln): pick=True; continue
                if pick and re.match(r"\s*\w+\s*:", ln): break
                if pick:
                    m = re.search(r"area\.(\w+)\s*([+\-]=)\s*([\-\d\.]+)", ln)
                    if m:
                        dim, op, num = m.group(1), m.group(2), float(m.group(3))
                        self.area_bump(province, dim, num if op=="+=" else -num)
                        applied.append((dim, num if op=="+=" else -num))
            self.events.append(TurnEvent(self.turn, "EncounterCommitted", {"province":province,"rule":name,"outcome":outcome,"applied":applied}))
        return {"matched": bool(applied), "applied": applied}

    def autosave(self) -> Dict[str, Any]:
        return {"turn": self.turn, "provinces": self.provinces, "knobs": self.knobs, "events": [asdict(e) for e in self.events]}

    def load(self, data: Dict[str, Any]):
        self.turn = data.get("turn", 0); self.provinces = data.get("provinces", {})
        self.knobs = data.get("knobs", self.knobs); self.events = [TurnEvent(**e) for e in data.get("events", [])]
        self._turn_snapshots[self.turn] = self._snapshot_state()

    def undo_to_turn(self, t: int):
        if t not in self._turn_snapshots:
            raise ValueError("No snapshot for turn %d" % t)
        snap = self._turn_snapshots[t]
        self.turn = t
        self.provinces = copy.deepcopy(snap["provinces"])
        self.events.append(TurnEvent(self.turn, "UndoToTurn", {"turn": t}))

    def _snapshot_state(self) -> Dict[str, Any]:
        return {"provinces": copy.deepcopy(self.provinces), "knobs": dict(self.knobs)}
