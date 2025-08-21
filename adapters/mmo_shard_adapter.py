
from typing import Dict, Any

class KafkaStub:
    """Replace with real Kafka producer (e.g., confluent-kafka)."""
    def __init__(self, topic: str = "oracle_events"): self.topic = topic
    def send(self, topic: str, value: dict): pass
    def flush(self): pass

class MMOShardAdapter:
    """One adapter per shard/region. Wire snapshots to object storage and events to Kafka."""
    def __init__(self, bus, shard_id: str = "shard-1", producer: KafkaStub | None = None):
        self.bus = bus
        self.shard_id = shard_id
        self.areas: Dict[str, Dict[str, float]] = {}
        self.npcs: Dict[str, Dict[str, Any]] = {}
        self.knobs: Dict[str, float] = {}
        self.producer = producer or KafkaStub()

    def snapshot(self) -> Dict[str, Any]:
        return {"shard": self.shard_id, "areas": self.areas, "npcs": self.npcs, "knobs": self.knobs}

    def from_snapshot(self, state: Dict[str, Any]):
        self.areas = dict(state.get("areas", {}))
        self.npcs  = dict(state.get("npcs", {}))
        self.knobs = dict(state.get("knobs", {}))

    def area_bump(self, name: str, dim: str, delta: float):
        a = self.areas.setdefault(name, {"security":50,"prosperity":50,"control":50,"culture":50,"ecology":50})
        a[dim] = float(a.get(dim, 50)) + float(delta)
        ev = {"shard": self.shard_id, "verb": "AreaBump", "area": name, "dim": dim, "delta": float(delta)}
        self.producer.send(self.producer.topic, ev)
        self.bus.append("AreaBump", ev)

    def rumor(self, hypothesis: str, source: str, polarity: int, reliability: float):
        ev = {"shard": self.shard_id, "verb": "RumorInjected", "hypothesis": hypothesis, "source": source, "polarity": polarity, "reliability": reliability}
        self.producer.send(self.producer.topic, ev); self.bus.append("RumorInjected", ev)

    def knob(self, name: str, value: float):
        self.knobs[name] = value
        ev = {"shard": self.shard_id, "verb": "KnobSet", "name": name, "value": value}
        self.producer.send(self.producer.topic, ev); self.bus.append("KnobSet", ev)

    def dsl_load(self, rule: str):
        ev = {"shard": self.shard_id, "verb": "DSLLoaded", "size": len(rule)}
        self.producer.send(self.producer.topic, ev); self.bus.append("DSLLoaded", ev)
        self._dsl_rule = rule

    def dsl_exec(self, area: str, outcome: str):
        # stub: producer-only signal; rely on authoritative shard to apply results
        ev = {"shard": self.shard_id, "verb": "EncounterCommitted", "area": area, "outcome": outcome}
        self.producer.send(self.producer.topic, ev); self.bus.append("EncounterCommitted", ev)
        return {"matched": True, "applied": []}
