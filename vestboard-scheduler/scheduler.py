"""Cycle controller: one quote + one wave per 30 min, guarded to 8am-8pm.

Sources follow a simple pluggable shape: a zero-arg callable that returns
``(characters, log_callback)``. ``characters`` is a 6x22 grid of integers;
``log_callback`` is invoked after a successful send so the source decides
what to log. Add a new message type by writing a new source function.
"""

import time
from datetime import datetime

import logger
import quotes
import vestaboard
import waves

QUOTE_DURATION_SECONDS = 29 * 60
WAVE_DURATION_SECONDS = 60
DAY_START_HOUR = 8
DAY_END_HOUR = 20  # exclusive — last cycle starts at 19:30, ends at 20:00


def within_active_hours():
    """True when current local time is between 8am and 8pm."""
    hour = datetime.now().hour
    return DAY_START_HOUR <= hour < DAY_END_HOUR


def quote_source():
    """Source: a centered, word-wrapped quote rendered via VBML."""
    text = quotes.next_quote()
    lines = quotes.wrap_quote(text)
    if len(lines) > quotes.MAX_LINES:
        logger.log_warning(
            f"Quote wraps to {len(lines)} lines (>{quotes.MAX_LINES}): {text}"
        )
    template = "\n".join(lines)
    characters = vestaboard.compose_vbml(template)
    return characters, lambda: logger.log_quote(text)


def wave_source():
    """Source: a procedurally generated sine wave frame."""
    grid, params = waves.generate_wave()
    return grid, lambda: logger.log_wave(**params)


def _run_source(source):
    """Build a frame from a source, send it, and log on success."""
    try:
        characters, log_on_success = source()
    except Exception as exc:
        logger.log_error(f"source {source.__name__} failed to build: {exc}")
        return
    try:
        vestaboard.send_characters(characters)
    except vestaboard.VestaboardError as exc:
        logger.log_error(str(exc), status_code=exc.status_code, body=exc.body)
        return
    except Exception as exc:
        logger.log_error(f"send for {source.__name__} failed: {exc}")
        return
    try:
        log_on_success()
    except Exception as exc:
        logger.log_error(f"log callback for {source.__name__} failed: {exc}")


def run_cycle():
    """Run one quote-then-wave cycle. Exits early if outside active hours."""
    if not within_active_hours():
        return
    _run_source(quote_source)
    time.sleep(QUOTE_DURATION_SECONDS)
    if not within_active_hours():
        return
    _run_source(wave_source)
    time.sleep(WAVE_DURATION_SECONDS)
