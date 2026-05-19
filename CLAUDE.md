# Vestaboard Automation — Project Rules

## Project overview
A lightweight Python scheduler that cycles quotes and wave interstitials on a Vestaboard display. Runs via cron on Mac (prototype) and must migrate to Mac Mini or Raspberry Pi without changes.

---

## Core principles

- **Keep it simple.** Prefer the most readable solution over the clever one.
- **Stay lean.** No frameworks, no heavy dependencies. Only `requests` and `python-dotenv`.
- **Cross-platform always.** No Mac-specific APIs or paths. Must run identically on Raspberry Pi OS.
- **Fail gracefully.** API failures should be logged and skipped — never crash the scheduler.
- **Ask before restructuring.** If you think the architecture should change, flag it and wait for confirmation before proceeding.

---

## Language & style

- Python 3.10+
- Snake case for all variables and functions
- Constants in ALL_CAPS at the top of each module
- One responsibility per module — keep files focused
- No inline comments explaining what the code does; only comments explaining *why* when the reason isn't obvious
- Docstrings on all public functions

---

## Project structure

```
vestaboard/
├── main.py              # Entry point, main scheduler loop
├── scheduler.py         # Timing logic, 8am–8pm guard, cycle management
├── quotes.py            # Quote loader, shuffle-cycle logic, word wrapping
├── waves.py             # Wave pattern generator → 6×22 character array
├── vestaboard.py        # API client (send_characters)
├── logger.py            # Weekly log file handler
├── preview.py           # CLI preview tool (terminal ANSI output)
├── quotes.csv           # User-maintained quote list (plain text, one per row)
├── state.json           # Shuffle state — persists between cron runs (auto-generated)
├── .env                 # VESTABOARD_API_KEY (never commit)
├── .env.example         # Template for .env
├── logs/                # Weekly log files (YYYY-Www.log)
├── requirements.txt
└── README.md
```

Do not create files outside this structure without flagging it first.

---

## Environment

- API key stored in `.env` as `VESTABOARD_API_KEY`
- Never hardcode credentials
- `.env` must never be committed — ensure it is in `.gitignore`

---

## API behaviour

- All messages sent as character arrays via `POST https://cloud.vestaboard.com/`
- Quotes formatted via VBML (`POST https://vbml.vestaboard.com/compose`) before sending — VBML returns the character array
- VBML requires no authentication
- Respect the rate limit: no more than 1 message every 15 seconds
- On any API failure: log the error with status code and response body, then continue

---

## Quotes

- Source: `quotes.csv` — plain text, one quote per row, no markup
- The app constructs the VBML payload from the raw string
- Word-wrap to 22 columns before sending to VBML, breaking at word boundaries
- Center horizontally and vertically: `justify: center`, `align: center`
- Log a warning if a quote wraps beyond 6 lines
- Shuffle the full list before cycling; do not repeat until the full list is exhausted
- Persist shuffle state to `state.json` between cron runs

---

## Wave interstitials

- Procedurally generated sine wave mapped to 6×22 grid
- Use only `math` from the standard library — no numpy
- Randomize each time: frequency, amplitude, phase offset, color palette
- Colors limited to Vestaboard color codes: 63 (red), 64 (orange), 65 (yellow), 66 (green), 67 (blue), 68 (violet)
- Output is a 6×22 nested list of integers

---

## Logging

- Location: `logs/YYYY-Www.log` (ISO week numbering, auto-created)
- Format: `[YYYY-MM-DD HH:MM:SS] TYPE   | CONTENT`
- Quote entry: full quote text
- Wave entry: `[graphic: wave_frame] freq={f:.2f} amp={a:.2f} phase={p:.2f} palette={colors}`
- Error entry: error message, status code, and response body

---

## Preview tool (`preview.py`)

A CLI-only testing tool. No API calls made. Three commands:

- `python preview.py quote "Your quote text"` — renders quote in terminal using ANSI
- `python preview.py wave` — generates and renders a random wave frame
- `python preview.py next` — shows what the next scheduled message would be without sending

---

## Out of scope (do not build unless explicitly asked)

- Animation or multi-frame sequences
- AI-generated content
- External data sources (weather, calendar, etc.)
- Web UI or dashboard
- Push notifications or alerts
