"""Estimated USD cost of model usage, from Claude usage objects and session transcripts."""

import json

# USD per million tokens: input, 5m cache write, 1h cache write, cache read, output.
# Source: https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-29).
PRICES = {
    "opus": (4.0, 5.0, 8.0, 0.20, 20.0),
    "sonnet": (2.0, 2.5, 4.0, 0.10, 10.0),
    "haiku": (0.10, 0.125, 0.20, 0.01, 0.50),
    "fable": (10.0, 12.5, 20.0, 0.25, 50.0),
}
FALLBACK = "fable"


def prices(model):
    name = (model or "").lower()
    return next((p for family, p in PRICES.items() if family in name), PRICES[FALLBACK])


def write_split(usage, default_ttl):
    split = usage.get("cache_creation") or {}
    five, hour = split.get("ephemeral_5m_input_tokens"), split.get("ephemeral_1h_input_tokens")
    if five is None and hour is None:
        total = usage.get("cache_creation_input_tokens") or 0
        return (0, total) if default_ttl == "1h" else (total, 0)
    return five or 0, hour or 0


def usage_usd(usage, model, default_ttl="5m"):
    p_in, p_w5, p_w1, p_read, p_out = prices(model)
    w5, w1 = write_split(usage, default_ttl)
    total = (usage.get("input_tokens") or 0) * p_in
    total += w5 * p_w5 + w1 * p_w1
    total += (usage.get("cache_read_input_tokens") or 0) * p_read
    total += (usage.get("output_tokens") or 0) * p_out
    return total / 1_000_000


def json_lines(path):
    """Parsed JSON objects from a JSONL file; missing files and bad lines are skipped."""
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(entry, dict):
                    yield entry
    except OSError:
        return


def transcript_usd(path, since):
    """Main-session spend recorded in a transcript at or after the ISO timestamp `since`."""
    seen = {}
    for entry in json_lines(path):
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict) or "usage" not in message:
            continue
        if entry.get("isSidechain") or entry.get("timestamp", "") < since:
            continue
        seen[message.get("id") or len(seen)] = usage_usd(message["usage"], message.get("model"), "1h")
    return sum(seen.values())


def run_total(spend_log):
    """Sum of agent spend plus the latest main-session snapshot in a spend.jsonl log."""
    agents, main = 0.0, 0.0
    for entry in json_lines(spend_log):
        agents += entry.get("usd") or 0
        main = entry.get("main_usd", main)
    return round(agents + main, 4)
