"""CLI preview of Vestaboard frames using ANSI colors. No API calls made."""

import sys

import quotes
import waves

ROWS = 6
COLS = 22

COLOR_BG = {
    63: "\x1b[48;5;196m",   # red
    64: "\x1b[48;5;208m",   # orange
    65: "\x1b[48;5;226m",   # yellow
    66: "\x1b[48;5;46m",    # green
    67: "\x1b[48;5;33m",    # blue
    68: "\x1b[48;5;129m",   # violet
}
BLANK_BG = "\x1b[48;5;235m"
TEXT_FG = "\x1b[38;5;255m"
RESET = "\x1b[0m"


def _render_color_cell(code):
    if code in COLOR_BG:
        return f"{COLOR_BG[code]}  {RESET}"
    return f"{BLANK_BG}  {RESET}"


def _render_text_cell(ch):
    if not ch or ch == " ":
        return f"{BLANK_BG}  {RESET}"
    return f"{BLANK_BG}{TEXT_FG}{ch.upper()} {RESET}"


def _print_grid(grid, render_cell):
    border = "+" + "-" * (COLS * 2) + "+"
    print(border)
    for row in grid:
        cells = "".join(render_cell(c) for c in row)
        print(f"|{cells}|")
    print(border)


def _compose_text_grid(lines):
    """Centre word-wrapped lines on a 6x22 grid of single chars."""
    visible = lines[:ROWS]
    vertical_pad = (ROWS - len(visible)) // 2
    grid = [[" "] * COLS for _ in range(ROWS)]
    for i, line in enumerate(visible):
        text = line[:COLS]
        left_pad = (COLS - len(text)) // 2
        for j, ch in enumerate(text):
            grid[vertical_pad + i][left_pad + j] = ch
    return grid


def render_quote(text):
    """Render a quote locally (word-wrap + centre) without hitting VBML."""
    lines = quotes.wrap_quote(text)
    if len(lines) > quotes.MAX_LINES:
        print(f"WARNING: quote wraps to {len(lines)} lines (>{quotes.MAX_LINES})")
    grid = _compose_text_grid(lines)
    _print_grid(grid, _render_text_cell)


def cmd_quote(args):
    if not args:
        print('Usage: preview.py quote "Your text"')
        sys.exit(1)
    render_quote(" ".join(args))


def cmd_wave(_args):
    grid, params = waves.generate_wave()
    _print_grid(grid, _render_color_cell)
    print(
        f"freq={params['freq']:.2f} amp={params['amp']:.2f} "
        f"phase={params['phase']:.2f} palette={params['palette']}"
    )


def cmd_next(_args):
    text = quotes.peek_next_quote()
    print("Next scheduled: QUOTE")
    print(f"Content: {text}")
    print()
    render_quote(text)
    print()
    print("Followed 29 min later by a wave interstitial (random).")


COMMANDS = {"quote": cmd_quote, "wave": cmd_wave, "next": cmd_next}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print("Usage:")
        print('  preview.py quote "Your text"')
        print("  preview.py wave")
        print("  preview.py next")
        sys.exit(1)
    COMMANDS[argv[1]](argv[2:])


if __name__ == "__main__":
    main(sys.argv)
