
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional

def _label_key(labels: Optional[Dict[str,str]]):
    if not labels: return tuple()
    return tuple(sorted((str(k), str(v)) for k,v in labels.items()))

@dataclass
class Counter:
    name: str; help: str = ""
    _values: Dict[Tuple[Tuple[str,str], ...], float] = field(default_factory=dict)
    def inc(self, amount: float = 1.0, labels: Optional[Dict[str,str]] = None):
        key = _label_key(labels); self._values[key] = self._values.get(key, 0.0) + float(amount)
    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} counter"]
        for key, val in self._values.items():
            if key:
                lbl = ",".join(f"{k}=\"{v}\"" for k,v in key); lines.append(f"{self.name}{{{lbl}}} {val}")
            else:
                lines.append(f"{self.name} {val}")
        return "\n".join(lines)

@dataclass
class Histogram:
    name: str; help: str = ""
    buckets: List[float] = field(default_factory=lambda: [5, 10, 25, 50, 100, 250, 500, 1000])
    _counts: Dict[Tuple[Tuple[str,str], ...], List[int]] = field(default_factory=dict)
    _sum: Dict[Tuple[Tuple[str,str], ...], float] = field(default_factory=dict)
    _observations: Dict[Tuple[Tuple[str,str], ...], int] = field(default_factory=dict)
    def observe(self, value_ms: float, labels: Optional[Dict[str,str]] = None):
        key = _label_key(labels)
        if key not in self._counts:
            self._counts[key] = [0] * (len(self.buckets) + 1)
            self._sum[key] = 0.0; self._observations[key] = 0
        idx = 0
        while idx < len(self.buckets) and value_ms > self.buckets[idx]: idx += 1
        self._counts[key][idx] += 1; self._observations[key] += 1; self._sum[key] += value_ms
    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} histogram"]
        for key, counts in self._counts.items():
            cum = 0
            for i in range(len(self.buckets)+1):
                cum += counts[i]
                le = "+Inf" if i == len(self.buckets) else str(self.buckets[i])
                if key:
                    lbl = ",".join(f"{k}=\"{v}\"" for k,v in key) + f",le=\"{le}\""
                    lines.append(f"{self.name}_bucket{{{lbl}}} {cum}")
                else:
                    lines.append(f"{self.name}_bucket{{le=\"{le}\"}} {cum}")
            sumv = self._sum[key]; cnt = self._observations[key]
            if key:
                lbl = ",".join(f"{k}=\"{v}\"" for k,v in key)
                lines.append(f"{self.name}_sum{{{lbl}}} {sumv}")
                lines.append(f"{self.name}_count{{{lbl}}} {cnt}")
            else:
                lines.append(f"{self.name}_sum {sumv}")
                lines.append(f"{self.name}_count {cnt}")
        return "\n".join(lines)

class Registry:
    def __init__(self):
        self.counters: Dict[str, Counter] = {}
        self.hists: Dict[str, Histogram] = {}
    def counter(self, name: str, help: str = "") -> Counter:
        if name not in self.counters: self.counters[name] = Counter(name, help)
        return self.counters[name]
    def histogram(self, name: str, help: str = "", buckets=None) -> Histogram:
        if name not in self.hists:
            h = Histogram(name, help)
            if buckets is not None: h.buckets = buckets
            self.hists[name] = h
        return self.hists[name]
    def render_prometheus(self) -> str:
        parts = [c.render() for c in self.counters.values()] + [h.render() for h in self.hists.values()]
        return "\n".join(parts) + "\n"

REGISTRY = Registry()

class Timer:
    def __init__(self):
        import time; self.t0 = time.time()
    def ms(self):
        import time; return (time.time()-self.t0)*1000.0
