"""Procedural pattern generators for the Vestaboard 6x22 grid.

Each pattern is a zero-arg function returning ``(grid, params)`` where
``grid`` is a 6x22 list of Vestaboard colour codes and ``params`` is a
dict with a uniform shape: ``pattern`` (name), ``palette`` (the colours
used), and ``detail`` (a human-readable string of the random parameters,
for logging). ``generate_wave`` picks a registered pattern at random.
"""

import math
import random

ROWS = 6
COLS = 22
COLORS = [63, 64, 65, 66, 67, 68]  # red, orange, yellow, green, blue, violet — rainbow order

# Sine pattern
FREQ_RANGE = (0.25, 1.20)
AMP_RANGE = (1.20, 2.50)
PHASE_RANGE = (0.0, 2 * math.pi)
PALETTE_SIZE_RANGE = (3, 5)

# Plasma pattern
PLASMA_FREQ_RANGE = (0.20, 0.60)
PLASMA_PALETTE_SIZE_RANGE = (4, 6)


def _rainbow_slice(size):
    """A contiguous run of the rainbow (optionally reversed) for smooth gradients."""
    start = random.randint(0, len(COLORS) - size)
    palette = COLORS[start:start + size]
    if random.random() < 0.5:
        palette = palette[::-1]
    return palette


def generate_sine():
    """A single sine line; cells coloured by distance from the line."""
    freq = random.uniform(*FREQ_RANGE)
    amp = random.uniform(*AMP_RANGE)
    phase = random.uniform(*PHASE_RANGE)
    palette_size = random.randint(*PALETTE_SIZE_RANGE)
    palette = random.sample(COLORS, palette_size)

    grid = [[0] * COLS for _ in range(ROWS)]
    center_row = (ROWS - 1) / 2
    max_distance = len(palette) - 1
    for col in range(COLS):
        y = center_row + amp * math.sin(freq * col + phase)
        for row in range(ROWS):
            distance = abs(row - y)
            color_index = min(int(distance), max_distance)
            grid[row][col] = palette[color_index]

    detail = f"freq={freq:.2f} amp={amp:.2f} phase={phase:.2f}"
    return grid, {"pattern": "sine", "palette": palette, "detail": detail}


def generate_plasma():
    """A smooth 2D colour field from summed sines (classic plasma)."""
    fx = random.uniform(*PLASMA_FREQ_RANGE)
    fy = random.uniform(*PLASMA_FREQ_RANGE)
    fd = random.uniform(*PLASMA_FREQ_RANGE)
    fr = random.uniform(*PLASMA_FREQ_RANGE)
    px = random.uniform(*PHASE_RANGE)
    py = random.uniform(*PHASE_RANGE)
    pd = random.uniform(*PHASE_RANGE)
    pr = random.uniform(*PHASE_RANGE)
    cx = random.uniform(0, COLS - 1)
    cy = random.uniform(0, ROWS - 1)

    palette = _rainbow_slice(random.randint(*PLASMA_PALETTE_SIZE_RANGE))

    grid = [[0] * COLS for _ in range(ROWS)]
    last_index = len(palette) - 1
    for row in range(ROWS):
        for col in range(COLS):
            dist = math.hypot(col - cx, row - cy)
            v = (
                math.sin(col * fx + px)
                + math.sin(row * fy + py)
                + math.sin((col + row) * fd + pd)
                + math.sin(dist * fr + pr)
            )
            normalized = (v + 4) / 8  # v spans [-4, 4] -> [0, 1]
            color_index = min(int(normalized * len(palette)), last_index)
            grid[row][col] = palette[color_index]

    detail = f"fx={fx:.2f} fy={fy:.2f} fd={fd:.2f} fr={fr:.2f}"
    return grid, {"pattern": "plasma", "palette": palette, "detail": detail}


PATTERNS = {
    "sine": generate_sine,
    "plasma": generate_plasma,
}


def generate_wave(name=None):
    """Generate a frame from a registered pattern (random unless ``name`` given).

    Returns ``(grid, params)``. Raises ``KeyError`` for an unknown name.
    """
    if name is None:
        name = random.choice(list(PATTERNS))
    return PATTERNS[name]()
