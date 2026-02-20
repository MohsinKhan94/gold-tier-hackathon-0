"""
Start Silver Tier - Orchestration Script
Launches all Silver Tier components concurrently.
"""

import subprocess
import sys
import time
import signal
from pathlib import Path

# Paths to scripts
BASE_DIR = Path(__file__).parent
SCRIPTS = [
    ("File Watcher", BASE_DIR / "file_watcher.py"),
    ("Mock Watcher", BASE_DIR / "mock_watcher.py"),
    ("LinkedIn Poster", BASE_DIR / "linkedin_poster.py"),
    ("Plan Loop", BASE_DIR / "plan_loop.py")
]

# Optional scripts if credentials exist
GMAIL_SCRIPT = BASE_DIR / "gmail_watcher.py"
GMAIL_CREDS = BASE_DIR / "credentials.json"
GMAIL_TOKEN = BASE_DIR / "gmail_token.pickle"

if GMAIL_CREDS.exists() or GMAIL_TOKEN.exists():
    SCRIPTS.append(("Gmail Watcher", GMAIL_SCRIPT))
else:
    print("Gmail credentials not found. Gmail Watcher will not start.")
    print("  (Add credentials.json to ai-employee-watcher/ to enable)")

processes = []


def signal_handler(sig, frame):
    print("\n\nStopping all services...")
    for p in processes:
        p.terminate()
    print("All services stopped.")
    sys.exit(0)


def main():
    print("=" * 60)
    print("STARTING SILVER TIER AI EMPLOYEE")
    print("=" * 60)

    # Register signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # Run initial scheduled update
    print("\nRunning initial update...")
    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR / "scheduled_task.py")],
            cwd=str(BASE_DIR),
            timeout=30
        )
    except Exception as e:
        print(f"  Initial update error: {e}")

    # Start processes
    print("\nStarting background services...")
    for name, script in SCRIPTS:
        print(f"  Starting {name}...")
        try:
            p = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(BASE_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            processes.append(p)
            print(f"    PID: {p.pid}")
        except Exception as e:
            print(f"  Failed to start {name}: {e}")

    print(f"\nAll systems go! ({len(processes)} services running)")
    print("  (Check the new console windows for logs)")
    print("  Press Ctrl+C in this window to stop everything.\n")

    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for p in list(processes):
                if p.poll() is not None:
                    print(f"A subprocess (PID {p.pid}) has stopped unexpectedly.")
                    processes.remove(p)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
