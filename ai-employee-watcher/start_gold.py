"""
Start Gold Tier - Master Orchestration Script
Launches all Gold Tier components with watchdog health monitoring.
Includes scheduled tasks for CEO briefing, audit log cleanup, and cross-domain processing.
"""

import subprocess
import sys
import time
import signal
import schedule
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
VAULT_PATH = BASE_DIR.parent / "AI_Employee_Vault"

sys.path.insert(0, str(BASE_DIR))


def run_scheduled_task():
    """Run the periodic scheduled task."""
    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR / "scheduled_task.py")],
            cwd=str(BASE_DIR),
            timeout=60,
        )
    except Exception as e:
        print(f"  Scheduled task error: {e}")


def run_ceo_briefing():
    """Generate the weekly CEO briefing."""
    try:
        from ceo_briefing import save_briefing
        filepath = save_briefing()
        print(f"  CEO Briefing generated: {filepath.name}")
    except Exception as e:
        print(f"  CEO Briefing error: {e}")


def run_audit_cleanup():
    """Clean up old audit logs."""
    try:
        from audit_logger import cleanup_old_logs
        removed = cleanup_old_logs()
        if removed:
            print(f"  Cleaned up {removed} old audit log files")
    except Exception as e:
        print(f"  Audit cleanup error: {e}")


def run_cross_domain_scan():
    """Run cross-domain orchestrator scan."""
    try:
        from orchestrator import scan_inbox_for_cross_domain
        results = scan_inbox_for_cross_domain()
        business = sum(1 for r in results if "business" in r.get("classification", {}).get("domains", []))
        urgent = sum(1 for r in results if r.get("classification", {}).get("is_urgent", False))
        if results:
            print(f"  Cross-domain scan: {len(results)} items ({business} business, {urgent} urgent)")
    except Exception as e:
        print(f"  Cross-domain scan error: {e}")


def main():
    print("=" * 60)
    print("  STARTING GOLD TIER AI EMPLOYEE")
    print("=" * 60)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Run initial updates
    print("[1/4] Running initial scheduled update...")
    run_scheduled_task()

    # Step 2: Run initial cross-domain scan
    print("[2/4] Running cross-domain scan...")
    run_cross_domain_scan()

    # Step 3: Run audit cleanup
    print("[3/4] Cleaning up old logs...")
    run_audit_cleanup()

    # Step 4: Start watchdog with all processes
    print("[4/4] Starting watchdog monitor...")
    print()

    try:
        from watchdog_monitor import Watchdog
        watchdog = Watchdog()
    except ImportError:
        print("ERROR: watchdog_monitor.py not found")
        sys.exit(1)

    # Register all watcher processes
    watchdog.add_process("File Watcher", "file_watcher.py")
    watchdog.add_process("Mock Watcher", "mock_watcher.py")
    watchdog.add_process("LinkedIn Poster", "linkedin_poster.py")
    watchdog.add_process("Plan Loop", "plan_loop.py")

    # Gmail watcher (optional)
    if (BASE_DIR / "credentials.json").exists() or (BASE_DIR / "gmail_token.pickle").exists():
        watchdog.add_process("Gmail Watcher", "gmail_watcher.py")

    # Start all processes
    watchdog.start_all()

    # Setup scheduled tasks
    schedule.every(5).minutes.do(run_scheduled_task)
    schedule.every().sunday.at("22:00").do(run_ceo_briefing)
    schedule.every().day.at("03:00").do(run_audit_cleanup)
    schedule.every(10).minutes.do(run_cross_domain_scan)

    print()
    print("=" * 60)
    print("  GOLD TIER AI EMPLOYEE ACTIVE")
    print("=" * 60)
    print()
    print("  Services:")
    for m in watchdog.monitors:
        status = "RUNNING" if m.is_alive() else "FAILED"
        print(f"    [{status}] {m.name}")
    print()
    print("  Scheduled Tasks:")
    print("    - Periodic update: every 5 minutes")
    print("    - Cross-domain scan: every 10 minutes")
    print("    - CEO Briefing: Sunday at 22:00")
    print("    - Audit cleanup: daily at 03:00")
    print()
    print("  Press Ctrl+C to stop everything.")
    print()

    # Signal handler
    def signal_handler(sig, frame):
        print("\n\nShutting down Gold Tier AI Employee...")
        watchdog.stop_all()
        print("All services stopped. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Main loop: run scheduled tasks and watchdog health checks
    try:
        while True:
            schedule.run_pending()
            health = watchdog.check_health()
            alive = sum(1 for p in health["processes"] if p["status"] == "running")
            total = len(health["processes"])

            if health.get("restarts", 0) > 0 or health.get("failures", 0) > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Health: {alive}/{total} running | "
                      f"Restarts: {health['restarts']} | Failures: {health['failures']}")

            time.sleep(30)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
