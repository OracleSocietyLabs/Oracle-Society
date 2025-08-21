
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import threading, re

@dataclass
class Event:
    seq: int; verb: str; context: Dict[str, Any]

class EventBus:
    def __init__(self, max_events=500):
        self._seq = 0
        self._events: List[Event] = []
        self._cv = threading.Condition()
        self.max_events = max_events
    @property
    def last_seq(self) -> int: return self._seq
    def append(self, verb: str, ctx: Dict[str, Any]):
        with self._cv:
            self._seq += 1
            if len(self._events) >= self.max_events:
                self._events.pop(0)
            ev = Event(self._seq, verb, dict(ctx))
            self._events.append(ev)
            self._cv.notify_all()
            return ev
    def since(self, seq: int) -> List[dict]:
        with self._cv: return [asdict(e) for e in self._events if e.seq > seq]
    def wait_stream(self, start_seq: int, timeout: float = 0.5) -> List[Event]:
        with self._cv:
            if any(e.seq > start_seq for e in self._events):
                return [e for e in self._events if e.seq > start_seq]
            self._cv.wait(timeout=timeout)
            return [e for e in self._events if e.seq > start_seq]
    def drop_until(self, seq: int):
        with self._cv: self._events = [e for e in self._events if e.seq > seq]

class Adapter:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.areas: Dict[str, Dict[str, float]] = {
            "Market": {"security": 40.0, "prosperity": 55, "control": 50, "culture": 50, "ecology": 50},
            "Harbor": {"security": 35.0, "prosperity": 48, "control": 52, "culture": 46, "ecology": 49},
            "Temple": {"security": 42.0, "prosperity": 52, "control": 54, "culture": 53, "ecology": 51},
        }
        self.npcs: Dict[str, Dict[str, Any]] = {
            "N1": {"name":"Aella", "beliefs":{"player=arsonist": 0.8, "guild=thieves":0.2}},
            "N2": {"name":"Boros", "beliefs":{"player=arsonist": 0.6, "guild=thieves":0.1}},
            "N3": {"name":"Cato",  "beliefs":{"player=arsonist": 0.4, "guild=thieves":0.3}},
        }
        self.knobs = {"memory_half_life": 240, "prestige_half_life": 480, "area_half_life": 720, "relation_half_life": 240, "affect_half_life": 90}
        self._dsl_rule = ""
    def from_snapshot(self, state: dict):
        self.areas = state["areas"]; self.npcs = state["npcs"]; self.knobs = state["knobs"]
    def snapshot(self) -> Dict[str, Any]:
        return {"areas": self.areas, "npcs": self.npcs, "knobs": self.knobs}
    def area_bump(self, name: str, dim: str, delta: float):
        a = self.areas.setdefault(name, {"security":50,"prosperity":50,"control":50,"culture":50,"ecology":50})
        a[dim] = float(a.get(dim, 50)) + float(delta)
        self.bus.append("AreaBump", {"area": name, "dim": dim, "delta": float(delta)})
    def rumor(self, hypothesis: str, source: str, polarity: int, reliability: float):
        for npc in self.npcs.values():
            b = npc.setdefault("beliefs", {})
            v = b.get(hypothesis, 0.5)
            b[hypothesis] = max(0.0, min(1.0, v + (0.05 * polarity * reliability)))
        self.bus.append("RumorInjected", {"hypothesis": hypothesis, "source": source, "polarity": polarity, "reliability": reliability})
    def knob(self, name: str, value: float):
        self.knobs[name] = value; self.bus.append("KnobSet", {"name": name, "value": value})
    def dsl_load(self, rule: str):
        self._dsl_rule = rule; self.bus.append("DSLLoaded", {"size": len(rule)})
    def dsl_exec(self, area: str, outcome: str) -> Dict[str, Any]:
        txt = self._dsl_rule or ""; ok = "OUTCOMES" in txt and ("area." in txt); applied = []
        if ok:
            lines = txt.splitlines(); pick = False
            for ln in lines:
                if re.match(rf"\s*{re.escape(outcome)}\s*:", ln): pick = True; continue
                if pick and re.match(r"\s*\w+\s*:", ln): break
                if pick:
                    m = re.search(r"area\.(\w+)\s*([+\-]=)\s*([\-\d\.]+)", ln)
                    if m:
                        dim, op, num = m.group(1), m.group(2), float(m.group(3))
                        self.area_bump(area, dim, num if op=="+=" else -num)
                        applied.append((dim, num if op=="+=" else -num))
            self.bus.append("EncounterCommitted", {"area": area, "outcome": outcome, "applied": applied})
        return {"matched": bool(ok), "applied": applied}
