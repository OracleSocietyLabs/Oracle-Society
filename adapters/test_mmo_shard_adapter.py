import unittest
from server.world import EventBus
from mmo_shard_adapter import MMOShardAdapter, KafkaStub


class TestMMOShardAdapter(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus(max_events=50)
        self.kafka_msgs = []

        class StubKafka(KafkaStub):
            def send(s, topic, value, key=None):
                self.kafka_msgs.append((topic, value, key))
            def flush(s): pass

        self.adapter = MMOShardAdapter(self.bus, shard_id="test-shard", producer=StubKafka())

    def test_area_bump_emits_event(self):
        self.adapter.area_bump("Market", "security", 5)
        evs = self.bus.since(0)
        self.assertTrue(any(e["verb"] == "AreaBump" for e in evs))
        self.assertEqual(self.adapter.areas["Market"]["security"], 55.0)

    def test_rumor_injects_belief(self):
        self.adapter.npcs = {"N1": {"name": "Aella", "beliefs": {"player=thief": 0.5}}}
        self.adapter.rumor("player=thief", "tavern", 1, 0.9)
        val = self.adapter.npcs["N1"]["beliefs"]["player=thief"]
        self.assertNotEqual(val, 0.5)
        evs = self.bus.since(0)
        self.assertTrue(any(e["verb"] == "RumorInjected" for e in evs))

    def test_knob_set(self):
        self.adapter.knob("area_half_life", 123)
        self.assertEqual(self.adapter.knobs["area_half_life"], 123.0)
        evs = self.bus.since(0)
        self.assertTrue(any(e["verb"] == "KnobSet" for e in evs))

    def test_dsl_load_and_exec(self):
        rule = "WHEN something\nOUTCOMES:\n  calm:\n    area.security += 5"
        self.adapter.dsl_load(rule)
        result = self.adapter.dsl_exec("Market", "calm")
        self.assertIn("event_id", result)
        evs = self.bus.since(0)
        verbs = [e["verb"] for e in evs]
        self.assertIn("DSLLoaded", verbs)
        self.assertIn("EncounterCommitted", verbs)

    def test_kafka_messages_recorded(self):
        self.adapter.area_bump("Harbor", "prosperity", 10)
        self.assertTrue(self.kafka_msgs, "Kafka stub did not capture messages")
        topic, value, key = self.kafka_msgs[-1]
        self.assertIn("verb", value)
        self.assertEqual(topic, "oracle_events")


if __name__ == "__main__":
    unittest.main()
