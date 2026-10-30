"""Cron entry point. Runs one quote-then-wave cycle and exits."""

from scheduler import run_cycle


if __name__ == "__main__":
    run_cycle()
