"""Procedural sine-wave frame generator for the Vestaboard 6x22 grid."""

import math
import random

ROWS = 6
COLS = 22
COLORS = [63, 64, 65, 66, 67, 68]  # red, orange, yellow, green, blue, violet

FREQ_RANGE = (0.25, 1.20)
AMP_RANGE = (1.20, 2.50)
PHASE_RANGE = (0.0, 2 * math.pi)
PALETTE_SIZE_RANGE = (3, 5)


def generate_wave():
    """Generate a random wave frame.

    Returns a tuple ``(grid, params)`` where ``grid`` is a 6x22 list of
    Vestaboard colour codes and ``params`` is a dict of the parameters
    used (freq, amp, phase, palette) for logging.
    """
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

    params = {"freq": freq, "amp": amp, "phase": phase, "palette": palette}
    return grid, params
