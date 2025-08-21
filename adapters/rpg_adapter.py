
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import re, time

@dataclass
class RPGEvent:
    t: float
    verb: str
    ctx: Dict[str, Any]

class RPGAdapter:
    def __init__(self):
        self.areas: Dict[str, Dict[str, float]] = {
            "Market": {"security": 45.0, "prosperity": 55, "control": 50, "culture": 50, "ecology": 50},
            "Harbor": {"security": 38.0, "prosperity": 48, "control": 52, "culture": 46, "ecology": 49},
        }
        self.npcs: Dict[str, Dict[str, Any]] = {
            "N1": {"name":"Aella", "beliefs":{"player=arsonist": 0.8}},
            "N2": {"name":"Boros", "beliefs":{"player=arsonist": 0.6}},
        }
        self.knobs = {"memory_half_life": 240, "prestige_half_life": 480, "area_half_life": 720}
        self._dsl_rule = ""
        self.timeline: List[RPGEvent] = []

    def area_bump(self, area: str, dim: str, delta: float):
        a = self.areas.setdefault(area, {"security":50,"prosperity":50,"control":50,"culture":50,"ecology":50})
        a[dim] = float(a.get(dim, 50)) + float(delta)
        self.timeline.append(RPGEvent(time.time(), "AreaBump", {"area":area,"dim":dim,"delta":delta}))

    def rumor(self, hypothesis: str, source: str, polarity: int, reliability: float):
        for npc in self.npcs.values():
            b = npc.setdefault("beliefs", {})
            v = b.get(hypothesis, 0.5)
            b[hypothesis] = max(0.0, min(1.0, v + (0.05 * polarity * reliability)))
        self.timeline.append(RPGEvent(time.time(), "RumorInjected", {"hypothesis":hypothesis,"source":source,"polarity":polarity,"reliability":reliability}))

    def dsl_load(self, rule: str):
        self._dsl_rule = rule
        self.timeline.append(RPGEvent(time.time(), "DSLLoaded", {"size":len(rule)}))

    def dsl_exec(self, area: str, outcome: str):
        txt = self._dsl_rule or ""; ok = "OUTCOMES" in txt and ("area." in txt); applied=[]
        if ok:
            lines = txt.splitlines(); pick=False
            for ln in lines:
                if re.match(rf"\s*{re.escape(outcome)}\s*:", ln): pick=True; continue
                if pick and re.match(r"\s*\w+\s*:", ln): break
                if pick:
                    m = re.search(r"area\.(\w+)\s*([+\-]=)\s*([\-\d\.]+)", ln)
                    if m:
                        dim, op, num = m.group(1), m.group(2), float(m.group(3))
                        self.area_bump(area, dim, num if op=="+=" else -num)
                        applied.append((dim, num if op=="+=" else -num))
            self.timeline.append(RPGEvent(time.time(), "EncounterCommitted", {"area":area,"outcome":outcome,"applied":applied}))
        return {"matched": bool(ok), "applied": applied}

    def make_savegame(self) -> Dict[str, Any]:
        return {
            "areas": self.areas, "npcs": self.npcs, "knobs": self.knobs,
            "timeline": [asdict(e) for e in self.timeline],
        }

    def load_savegame(self, data: Dict[str, Any]):
        self.areas = data.get("areas", {}); self.npcs = data.get("npcs", {}); self.knobs = data.get("knobs", self.knobs)
        self.timeline = [RPGEvent(**e) for e in data.get("timeline", [])]
