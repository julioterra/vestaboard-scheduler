"""Quote loader with shuffle-cycle persistence and word wrapping."""

import csv
import json
import random
import textwrap
from pathlib import Path

QUOTES_FILE = Path(__file__).parent / "quotes.csv"
STATE_FILE = Path(__file__).parent / "state.json"
COLUMN_WIDTH = 22
MAX_LINES = 6


def load_quotes():
    """Read all non-empty quotes from quotes.csv."""
    if not QUOTES_FILE.exists():
        return []
    with QUOTES_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row[0].strip() for row in reader if row and row[0].strip()]


def _load_state():
    if STATE_FILE.exists():
        with STATE_FILE.open(encoding="utf-8") as f:
            return json.load(f)
    return {"remaining": []}


def _save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _refill_if_empty(remaining, quotes):
    # Drop quotes that were removed from the source since the last shuffle.
    remaining = [q for q in remaining if q in quotes]
    if not remaining:
        remaining = quotes[:]
        random.shuffle(remaining)
    return remaining


def next_quote():
    """Return the next quote, advancing and persisting the shuffle state."""
    quotes = load_quotes()
    if not quotes:
        raise RuntimeError(f"No quotes found in {QUOTES_FILE}")
    state = _load_state()
    remaining = _refill_if_empty(state.get("remaining", []), quotes)
    quote = remaining.pop(0)
    _save_state({"remaining": remaining})
    return quote


def peek_next_quote():
    """Return what next_quote() would return, without consuming it.

    If the deck is empty, reshuffle and persist the new deck so that a
    subsequent call to next_quote() returns the same quote shown here.
    """
    quotes = load_quotes()
    if not quotes:
        raise RuntimeError(f"No quotes found in {QUOTES_FILE}")
    state = _load_state()
    remaining = _refill_if_empty(state.get("remaining", []), quotes)
    if remaining != state.get("remaining", []):
        _save_state({"remaining": remaining})
    return remaining[0]


def wrap_quote(text):
    """Word-wrap a quote to 22 columns, breaking at word boundaries."""
    return textwrap.wrap(
        text,
        width=COLUMN_WIDTH,
        break_long_words=False,
        break_on_hyphens=False,
    )
