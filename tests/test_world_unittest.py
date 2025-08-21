
import unittest
from server.world import EventBus, Adapter

class TestWorld(unittest.TestCase):
    def test_event_bus_basic(self):
        bus = EventBus(max_events=3)
        self.assertEqual(bus.last_seq, 0)
        bus.append("X", {"a":1}); bus.append("Y", {"b":2})
        self.assertEqual(len(bus.since(0)), 2)
        bus.append("Z", {"c":3}); bus.append("W", {"d":4})
        self.assertEqual(len(bus.since(0)), 3)
        self.assertEqual(bus.since(0)[0]["verb"], "Y")

    def test_adapter_area_bump(self):
        bus = EventBus()
        ad = Adapter(bus)
        before = ad.areas["Market"]["security"]
        ad.area_bump("Market","security", +5)
        self.assertEqual(ad.areas["Market"]["security"], before + 5)

if __name__ == "__main__":
    unittest.main()
