# Vestaboard Scheduler

A lightweight Python scheduler that cycles quotes and wave interstitials on a
[Vestaboard](https://www.vestaboard.com/) display.

Designed to run via cron on macOS or Raspberry Pi OS with no platform-specific
dependencies. Only `requests` and `python-dotenv` are required.

## Setup

```bash
cd vestaboard-scheduler
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set VESTABOARD_API_KEY=<your key>
```

## How it works

Each cron invocation runs one **30-minute cycle**:

1. Send a quote (shows for 29 minutes)
2. Send a wave interstitial (shows for 1 minute)

Quotes come from `quotes.csv` (one quote per row, plain text). The full list is
shuffled, then cycled through completely before reshuffling. Shuffle state is
persisted to `state.json` so cron invocations don't repeat quotes.

Waves are procedurally generated sine patterns mapped to the 6×22 grid using
six Vestaboard colours (red, orange, yellow, green, blue, violet).

The scheduler only runs between 08:00 and 20:00 local time; outside those
hours it exits immediately.

## Preview (no API calls)

`preview.py` renders frames in the terminal so you can test without sending to
the board:

```bash
python preview.py quote "Your quote text here"
python preview.py wave
python preview.py next   # peek at the next scheduled quote
```

## Cron setup

Add this to your crontab (`crontab -e`):

```cron
*/30 8-19 * * * /absolute/path/to/venv/bin/python /absolute/path/to/vestaboard-scheduler/main.py
```

This fires every 30 minutes between 08:00 and 19:30, giving the last cycle
just enough time to finish at 20:00. The `8-19` range is inclusive on both
ends in cron syntax.

The script always runs to completion (~30 minutes of `sleep`), so successive
cron jobs briefly overlap at the boundary. The 15-second API rate limit is
never approached.

## Logs

Weekly log files are written to `logs/YYYY-Www.log`, e.g. `logs/2026-W21.log`.
Each line is timestamped and tagged with one of `QUOTE`, `WAVE`, `WARN`, or
`ERROR`.

## Adding a new message source

Sources are zero-arg callables that return `(characters, log_callback)`:

```python
# scheduler.py
def my_source():
    characters = build_6x22_grid_somehow()
    return characters, lambda: logger.log_quote("my custom content")
```

Then call `_run_source(my_source)` from `run_cycle()` wherever you want it in
the rotation.

## Project files

```
vestaboard-scheduler/
├── main.py          # cron entry point
├── scheduler.py     # cycle logic and source dispatch
├── quotes.py        # CSV loader, shuffle state, word wrap
├── waves.py         # sine-wave frame generator
├── vestaboard.py    # API client (send + VBML)
├── logger.py        # weekly log file writer
├── preview.py       # CLI preview tool
├── quotes.csv       # user-editable quote list
├── .env.example     # template for your API key
├── requirements.txt
└── README.md
```

`state.json` and `logs/` are created at runtime and are gitignored.
