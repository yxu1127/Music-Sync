#!/usr/bin/env python3
"""Run the downloader on a schedule. Press Ctrl+C to stop."""

import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler


def run_download():
    """Run the download pipeline."""
    from src.orchestrator import run

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new tracks...")
    try:
        summary = run()
        total = sum(s["downloaded"] for s in summary.values())
        if total > 0:
            print(f"  Downloaded {total} track(s).")
        else:
            print("  No new tracks.")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    from src.config import load_config

    config = load_config()
    interval = config.get("schedule", {}).get("interval_minutes", 30)

    print(f"YouTube Music Downloader - Running every {interval} minutes")
    print("Press Ctrl+C to stop\n")

    scheduler = BlockingScheduler()
    scheduler.add_job(run_download, "interval", minutes=interval)

    # Run immediately on start, then on schedule
    run_download()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nStopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
