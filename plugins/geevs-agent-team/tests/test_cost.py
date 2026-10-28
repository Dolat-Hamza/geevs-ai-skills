import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "hooks"))
import cost  # noqa: E402

USAGE = {
    "input_tokens": 1000,
    "cache_creation_input_tokens": 2000,
    "cache_read_input_tokens": 10000,
    "output_tokens": 500,
}


def entry(ts, msg_id, usage, model="claude-sonnet-5-5", sidechain=False):
    return json.dumps(
        {
            "type": "assistant",
            "timestamp": ts,
            "isSidechain": sidechain,
            "message": {"id": msg_id, "model": model, "usage": usage},
        }
    )


class Prices(unittest.TestCase):
    def test_family_lookup(self):
        self.assertEqual(cost.prices("claude-sonnet-5-5")[0], 2.0)
        self.assertEqual(cost.prices("claude-haiku-5-5")[4], 0.50)

    def test_unknown_model_uses_most_expensive(self):
        self.assertEqual(cost.prices("mystery"), cost.PRICES["fable"])
        self.assertEqual(cost.prices(None), cost.PRICES["fable"])


class UsageUsd(unittest.TestCase):
    def test_sonnet_five_minute_writes(self):
        # 1000*2 + 2000*2.5 + 10000*0.1 + 500*10 = 13000 per million
        self.assertAlmostEqual(cost.usage_usd(USAGE, "claude-sonnet-5-5"), 0.013)

    def test_one_hour_default_ttl(self):
        # writes at 4.0 instead of 2.5: 2000 + 8000 + 1000 + 5000 = 16000
        self.assertAlmostEqual(cost.usage_usd(USAGE, "claude-sonnet-5-5", "1h"), 0.016)

    def test_explicit_split_wins_over_default(self):
        usage = {**USAGE, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 2000}}
        self.assertAlmostEqual(cost.usage_usd(usage, "claude-sonnet-5-5", "5m"), 0.016)

    def test_missing_fields_count_as_zero(self):
        self.assertEqual(cost.usage_usd({}, "claude-opus-5-5"), 0)


class Transcript(unittest.TestCase):
    def test_counts_main_entries_after_start_once(self):
        lines = [
            entry("2026-10-29T09:00:00.000Z", "old", USAGE),
            entry("2026-10-29T10:00:00.000Z", "a", USAGE),
            entry("2026-10-29T10:00:00.000Z", "a", USAGE),
            entry("2026-10-29T10:05:00.000Z", "side", USAGE, sidechain=True),
            "not json",
            json.dumps({"type": "user", "timestamp": "2026-10-29T10:06:00.000Z"}),
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write("\n".join(lines))
        self.assertAlmostEqual(cost.transcript_usd(f.name, "2026-10-29T09:30:00.000Z"), 0.016)

    def test_missing_transcript_is_zero(self):
        self.assertEqual(cost.transcript_usd("/no/such/file", ""), 0.0)


class AgentTranscript(unittest.TestCase):
    def test_sums_all_entries_once_with_models(self):
        lines = [entry("t", "a", USAGE), entry("t", "a", USAGE), entry("t", "b", USAGE, model="claude-haiku-5-5")]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write("\n".join(lines))
        usd, models = cost.agent_transcript_usd(f.name)
        self.assertAlmostEqual(usd, 0.013 + cost.usage_usd(USAGE, "claude-haiku-5-5"))
        self.assertEqual(models, ["claude-haiku-5-5", "claude-sonnet-5-5"])


class RunTotal(unittest.TestCase):
    def test_sums_agents_and_takes_latest_main_snapshot(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(
                "\n".join(
                    json.dumps(e)
                    for e in [
                        {"main_usd": 0.5},
                        {"agent_id": "r1", "usd": 0.2},
                        {"main_usd": 0.9},
                        {"agent_id": "b1", "usd": 0.4},
                        {"agent_id": "b1", "usd": 1.1},
                        {"agent_id": "x1", "usd": None},
                    ]
                )
            )
        self.assertAlmostEqual(cost.run_total(f.name), 2.2)

    def test_missing_log_is_zero(self):
        self.assertEqual(cost.run_total("/no/such/file"), 0.0)


if __name__ == "__main__":
    unittest.main()
