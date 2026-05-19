"""Weekly log file writer. Format: [YYYY-MM-DD HH:MM:SS] TYPE    | CONTENT"""

from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
TYPE_WIDTH = 7


def _current_log_file():
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return LOG_DIR / f"{year}-W{week:02d}.log"


def _write(entry_type, content):
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {entry_type:<{TYPE_WIDTH}} | {content}\n"
    with _current_log_file().open("a") as f:
        f.write(line)


def log_quote(text):
    """Log a sent quote."""
    _write("QUOTE", text)


def log_wave(freq, amp, phase, palette):
    """Log a sent wave frame with its parameters."""
    content = (
        f"[graphic: wave_frame] freq={freq:.2f} amp={amp:.2f} "
        f"phase={phase:.2f} palette={palette}"
    )
    _write("WAVE", content)


def log_warning(message):
    """Log a non-fatal warning (e.g. quote wraps beyond 6 lines)."""
    _write("WARN", message)


def log_error(message, status_code=None, body=None):
    """Log an error with optional status code and response body."""
    parts = [message]
    if status_code is not None:
        parts.append(f"status={status_code}")
    if body is not None:
        parts.append(f"body={body}")
    _write("ERROR", " ".join(parts))
