
import time, threading
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: int):
        self.rate = rate_per_sec; self.capacity = capacity
        self.tokens = capacity; self.last = time.time()
        self.lock = threading.Lock()
    def allow(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last
            self.last = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

class RateLimiter:
    def __init__(self, rate_per_sec=3.0, capacity=5):
        self.rate = rate_per_sec; self.cap = capacity
        self.buckets = defaultdict(lambda: TokenBucket(self.rate, self.cap))
    def allow(self, key: str) -> bool:
        return self.buckets[key].allow()
