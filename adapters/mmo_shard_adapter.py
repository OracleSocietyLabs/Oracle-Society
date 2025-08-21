
from __future__ import annotations
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time, uuid

@dataclass(frozen=True)
class OutEvent:
    event_id: str
    shard_seq: int
    ts: float
    shard: str
    verb: str
    context: Dict[str, Any]

class KafkaStub:
    """Replace with real Kafka producer (e.g., confluent-kafka)."""
    def __init__(self, topic: str = "oracle_events"): self.topic = topic
    def send(self, topic: str, value: dict, key: Optional[bytes] = None): pass
    def flush(self): pass

class MMOShardAdapter:
    """
    One adapter per shard/region.
    - Publishes authoritative events to Kafka with idempotency info
    - Mirrors events to local bus so the Phase 15 Designer UI can see them live
    """
    def __init__(self, bus, shard_id: str = "shard-1", producer: Optional[KafkaStub] = None):
        self.bus = bus
        self.shard_id = shard_id
        self.areas: Dict[str, Dict[str, float]] = {}
        self.npcs: Dict[str, Dict[str, Any]] = {}
        self.knobs: Dict[str, float] = {}
        self.producer = producer or KafkaStub()
        self._seq = 0
        self._dsl_rule = ""

    # ---------- state I/O ----------
    def snapshot(self) -> Dict[str, Any]:
        return {"shard": self.shard_id, "areas": self.areas, "npcs": self.npcs, "knobs": self.knobs}

    def from_snapshot(self, state: Dict[str, Any]):
        self.areas = dict(state.get("areas", {}))
        self.npcs  = dict(state.get("npcs", {}))
        self.knobs = dict(state.get("knobs", {}))

    # ---------- internal helpers ----------
    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _emit(self, verb: str, ctx: Dict[str, Any], key: Optional[str] = None):
        ev = OutEvent(
            event_id=str(uuid.uuid4()),
            shard_seq=self._next_seq(),
            ts=time.time(),
            shard=self.shard_id,
            verb=verb,
            context=ctx,
        )
        payload = {
            "event_id": ev.event_id,
            "shard_seq": ev.shard_seq,
            "ts": ev.ts,
            "shard": ev.shard,
            "verb": ev.verb,
            "context": ev.context,
        }
        # Kafka publish (with partition key if provided)
        try:
            self.producer.send(self.producer.topic, payload, key=(key.encode() if key else None))
        except Exception as e:
            # optional: log/metric; we still push to local bus so tools see the attempt
            pass
        # Mirror to local EventBus (Phase 11)
        self.bus.append(verb, {"shard": ev.shard, "event_id": ev.event_id, "shard_seq": ev.shard_seq, **ctx})
        return ev

    # ---------- game-facing API ----------
    def area_bump(self, name: str, dim: str, delta: float):
        a = self.areas.setdefault(name, {"security":50,"prosperity":50,"control":50,"culture":50,"ecology":50})
        a[dim] = float(a.get(dim, 50)) + float(delta)
        self._emit("AreaBump", {"area": name, "dim": dim, "delta": float(delta), "new": a[dim]}, key=name)

    def rumor(self, hypothesis: str, source: str, polarity: int, reliability: float):
        # Optional local belief nudge if this shard is authoritative:
        for npc in self.npcs.values():
            beliefs = npc.setdefault("beliefs", {})
            v = float(beliefs.get(hypothesis, 0.5))
            beliefs[hypothesis] = max(0.0, min(1.0, v + 0.05 * polarity * reliability))
        self._emit("RumorInjected", {
            "hypothesis": hypothesis, "source": source,
            "polarity": polarity, "reliability": reliability
        }, key=hypothesis)

    def knob(self, name: str, value: float):
        self.knobs[name] = float(value)
        self._emit("KnobSet", {"name": name, "value": float(value)}, key=name)

    def dsl_load(self, rule: str):
        self._dsl_rule = rule or ""
        self._emit("DSLLoaded", {"size": len(self._dsl_rule)})

    def dsl_exec(self, area: str, outcome: str):
        # Keep adapter side effect-free aside from signaling; authoritative logic applies downstream
        ev = self._emit("EncounterCommitted", {"area": area, "outcome": outcome}, key=area)
        return {"matched": bool(self._dsl_rule), "applied": [], "event_id": ev.event_id}

    # ---------- ops ----------
    def flush(self):
        try: self.producer.flush()
        except Exception: pass
