# Vestaboard Scheduler

A lightweight Python scheduler that cycles quotes and wave interstitials on a
[Vestaboard](https://www.vestaboard.com/) display.

Designed to run via cron on macOS or Raspberry Pi OS with no platform-specific
dependencies. Only `requests` and `python-dotenv` are required.

---

## How it works

The scheduler is a small Python script. Each time it runs, it performs one
**30-minute cycle** on your Vestaboard:

1. Send a quote (stays on the board for ~29 minutes)
2. Send a wave interstitial (stays on the board for ~1 minute)

Then the script exits. A scheduler called **cron** (built into macOS and
Linux) starts the script again every 30 minutes between 8 AM and 8 PM. So you
get a new quote every half hour with a brief wave animation in between.

Quotes come from `quotes.csv` — a plain text file you can edit, one quote per
row. The script shuffles the full list, then cycles through it completely
before reshuffling. The shuffle position is saved to `state.json` so quotes
don't repeat across runs.

Waves are procedurally generated sine patterns mapped to the 6×22 grid using
six Vestaboard colours (red, orange, yellow, green, blue, violet).

Outside of 8 AM – 8 PM the script exits immediately, so the board stays quiet
overnight.

---

## What you'll need

- A Mac (or Raspberry Pi) with **Python 3.10 or newer**. To check, open
  Terminal and run `python3 --version`. If it prints something like
  `Python 3.10.x` or higher, you're good.
- A Vestaboard with a **Read/Write API key** (a 32-character hex string).
  Generate one from the board's settings page at
  [web.vestaboard.com](https://web.vestaboard.com).
- Comfort opening **Terminal** (the macOS app) and pasting commands. That's
  the only tool you'll need beyond a text editor.

---

## One-time setup

Open Terminal and `cd` into the project folder:

```bash
cd /path/to/vestaboard_scheduler
```

(Replace the path with wherever you cloned the repo.)

### 1. Create a virtual environment

A **virtual environment** ("venv") is a self-contained folder that holds the
Python libraries this project needs, isolated from the rest of your system.
It prevents version conflicts with other Python projects.

```bash
python3 -m venv venv
```

This creates a `venv/` folder inside the project. You only need to do this
once.

### 2. Activate the venv

"Activating" tells your terminal to use the Python inside `venv/` instead of
your system Python:

```bash
source venv/bin/activate
```

Your prompt will change to show `(venv)` at the start — that's how you know
it's active. You'll need to do this every time you open a new terminal to
work on the project. (Cron handles activation automatically — see below.)

### 3. Install the dependencies

With the venv active, install the two libraries the script uses:

```bash
pip install -r requirements.txt
```

You only need to do this once per venv.

### 4. Set up your API key

Copy the example env file and fill in your key:

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the placeholder with your
Vestaboard Read/Write key:

```
VESTABOARD_API_KEY=your_32_character_hex_key_here
```

Save and close. **Don't commit `.env` to git** — it's already in `.gitignore`.

### 5. Create the logs folder

```bash
mkdir -p logs
```

The script creates `logs/` on its own, but the cron line below redirects
errors into `logs/cron.err` *before* the script starts. If the folder
doesn't exist yet, that redirect fails and cron never runs the script.

---

## Test it without sending to the board

The `preview.py` tool renders frames in your terminal using coloured text
blocks. **No API calls are made**, so it's safe to run as often as you like.

Make sure the venv is active (`source venv/bin/activate`), then try:

```bash
python preview.py quote "Hello from the Vestaboard"
python preview.py wave
python preview.py next
```

- `quote "..."` — shows how a given quote would look on the board
- `wave` — generates a random wave pattern and renders it
- `next` — shows what the *next* scheduled quote would be, based on the
  current shuffle state in `state.json`

If your terminal shows colourful blocks of text, the rendering pipeline
works.

---

## Test it by sending to the board

Once preview looks right, send a real message:

```bash
python main.py
```

This runs **one full 30-minute cycle**: it sends a quote, waits 29 minutes,
sends a wave, waits 1 minute, then exits. Your board should update within a
few seconds of running the command.

If you just want to verify the API key works without waiting 30 minutes,
press **Ctrl+C** after the quote appears on the board — that aborts the
script. The first send is the meaningful test.

If something goes wrong, check `logs/YYYY-Www.log` (a file named after the
current ISO week, e.g. `logs/2026-W21.log`). API errors are logged with the
HTTP status code and response body.

---

## Schedule it with cron

**Cron** is a tool that comes with macOS (and Linux) that runs commands on a
schedule. You give it a line of configuration — a **crontab entry** —
describing *when* to run *what*.

### ⚠️ Important: cron will not wake your Mac

Cron is just a background program. If your Mac is **asleep, shut down, or
the user is logged out**, cron does not fire. It does **not** wake or turn
on the computer.

This means:

- If your Mac is asleep at 2 PM, the 2 PM quote will be skipped.
- If your Mac is off overnight, nothing happens — which is fine, since the
  schedule is 8 AM – 8 PM anyway. But if your Mac is still asleep at 8 AM,
  the first quote won't fire until you wake it.

**Workarounds (optional):**

1. In **System Settings → Lock Screen**, set "Turn display off on power
   adapter when inactive" to `Never`, or at least longer than 30 minutes,
   so the Mac stays awake during the day.
2. In **System Settings → Energy** (or **Battery → Options**), enable
   "Prevent automatic sleeping when the display is off" if your Mac is
   plugged in.
3. Or schedule automatic wake times in **System Settings → Battery →
   Schedule** (older macOS) or via `pmset` in Terminal. For example, to
   wake the Mac at 7:55 AM every weekday:

   ```bash
   sudo pmset repeat wakeorpoweron MTWRF 07:55:00
   ```

This is the kind of project that's better suited to a **Mac Mini that's
always on**, or a **Raspberry Pi**, which is part of why the script is
designed to be cross-platform.

### Add the cron job

1. Find the **absolute paths** to your project's Python and `main.py`.
   With the venv active, run:

   ```bash
   which python
   pwd
   ```

   The first prints the path to the venv's Python (something like
   `/Users/you/.../vestaboard_scheduler/venv/bin/python`). The second
   prints the project folder.

2. Open your crontab in an editor:

   ```bash
   crontab -e
   ```

   This opens the **crontab file** in your default terminal editor
   (usually `vim` or `nano`). If you've never set `EDITOR`, you'll get
   `vim` — to use `nano` instead, run `export EDITOR=nano` before
   `crontab -e`.

3. Add this line (replacing the three paths with what `which python` and
   `pwd` printed — the third path is just `pwd` + `/logs/cron.err`):

   ```cron
   */30 8-19 * * * /absolute/path/to/vestaboard_scheduler/venv/bin/python /absolute/path/to/vestaboard_scheduler/main.py >> /absolute/path/to/vestaboard_scheduler/logs/cron.err 2>&1
   ```

   The `>> .../logs/cron.err 2>&1` part captures any errors cron itself
   produces (e.g. "module not found") into a file you can read. Without
   this, cron failures vanish silently — see *Common gotchas* below.

4. Save and exit.
   - In **nano**: press `Ctrl+O`, then `Enter` to save, then `Ctrl+X` to exit.
   - In **vim**: press `Esc`, then type `:wq` and press `Enter`.

   If cron accepts the file, you'll see `crontab: installing new crontab`.

### What that line means

```
*/30  8-19  *  *  *   /path/to/python  /path/to/main.py
 ─┬─  ─┬─  ┬  ┬  ┬
  │    │   │  │  └── day of week  (* = any)
  │    │   │  └───── month        (* = any)
  │    │   └──────── day of month (* = any)
  │    └──────────── hour         (8-19 = 8 AM through 7 PM, inclusive)
  └───────────────── minute       (*/30 = every 30 minutes, i.e. :00 and :30)
```

So the job fires at 8:00, 8:30, 9:00, … 19:00, 19:30 every day. The last
cycle starts at 19:30 and finishes around 20:00.

Cron jobs briefly overlap at the half-hour boundary (the previous cycle is
still doing its final 1-minute wave when the next cycle starts). The
15-second API rate limit is never approached, so this is fine.

### macOS quirk: Full Disk Access

On modern macOS, cron jobs are sandboxed and may not be able to read files in
folders like `Documents/`. If your job doesn't seem to be running, grant
Full Disk Access to `cron`:

1. Open **System Settings → Privacy & Security → Full Disk Access**.
2. Click **+**, press `Cmd+Shift+G`, type `/usr/sbin/cron`, hit Enter, then
   select `cron` and click Open.
3. Make sure the toggle next to `cron` is on.

### Verify the cron job

- List your crontab: `crontab -l`
- After the next half-hour mark, check that the log file updated:
  `ls -lt logs/` should show a recent timestamp.
- Watch the live log: `tail -f logs/$(date +%G-W%V).log`

### Stop / change / remove the cron job

- Edit: `crontab -e`
- Remove the line, save, and exit to disable. Or `crontab -r` to remove the
  entire crontab.

---

## Common gotchas

### Cron runs but the log file stays empty

Symptom: `crontab -l` shows your job, the half-hour ticks come and go, but
`logs/YYYY-Www.log` doesn't get any new entries.

Most likely cause: **cron is using the wrong Python.** This project's
dependencies (`requests`, `python-dotenv`) live inside `vestaboard_scheduler/venv/`.
If your crontab points at a different Python — say, a venv in your home
folder, or system Python — that interpreter won't have those packages
installed, and the script will crash on `import requests` before it can
write anything to its own log.

**How to confirm:** check `logs/cron.err` (created by the `>> ... 2>&1`
redirect in the recommended crontab line). If it contains
`ModuleNotFoundError: No module named 'requests'`, this is the problem.

**How to fix:**

1. With the project venv active (`source venv/bin/activate`), run
   `which python` — copy the path it prints.
2. Run `crontab -e` and make sure the path before `main.py` is exactly
   that.

This is easy to get wrong because `python3` on macOS is usually on your
`PATH` and it's tempting to just type that into the crontab — but cron
doesn't know about your project's venv unless you spell out its absolute
path.

### Cron ticks are missed when the Mac is asleep

Cron does not wake a sleeping Mac (see the warning earlier in this section).
If you set the schedule to fire at 8 AM and your Mac doesn't wake until
8:45, the 8:00 and 8:30 quotes are skipped — they don't queue up.

### Paths with spaces

If the folder you cloned into has a space anywhere in its path (e.g.
`Documents/My Projects/...`), the crontab line will break unless you quote
it. Wrap every path that contains a space in single quotes:

```cron
*/30 8-19 * * * '/Users/you/My Projects/vestaboard_scheduler/venv/bin/python' '/Users/you/My Projects/vestaboard_scheduler/main.py' >> '/Users/you/My Projects/vestaboard_scheduler/logs/cron.err' 2>&1
```

---

## Logs

Weekly log files are written to `logs/YYYY-Www.log`, e.g. `logs/2026-W21.log`.
Each line is timestamped and tagged with one of `QUOTE`, `WAVE`, `WARN`, or
`ERROR`.

Example:

```
[2026-05-19 14:00:03] QUOTE  | The only way to do great work is to love what you do.
[2026-05-19 14:29:18] WAVE   | [graphic: wave_frame] freq=0.42 amp=2.10 phase=1.55 palette=[66, 67, 68]
```

---

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

---

## Project files

```
vestaboard_scheduler/
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
├── LICENSE
└── README.md
```

`state.json`, `logs/`, `.env`, and `venv/` are created locally and are
gitignored.

---

## License

Released under the [MIT License](LICENSE).
