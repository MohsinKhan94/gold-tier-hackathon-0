"""
Scheduled Task Runner - Silver Tier
Run this via Windows Task Scheduler or cron for periodic operations.

Windows Task Scheduler Setup:
  1. Open Task Scheduler (taskschd.msc)
  2. Create Basic Task -> "AI Employee Update"
  3. Trigger: Daily at 8:00 AM (or desired interval)
  4. Action: Start a Program
     - Program: python (or full path to python.exe)
     - Arguments: scheduled_task.py
     - Start in: <path to ai-employee-watcher folder>
  5. Save and enable

Linux/Mac cron:
  # Run every hour
  0 * * * * cd /path/to/ai-employee-watcher && python scheduled_task.py >> /tmp/ai-employee.log 2>&1

  # Run daily at 8 AM
  0 8 * * * cd /path/to/ai-employee-watcher && python scheduled_task.py --daily >> /tmp/ai-employee.log 2>&1
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from skills import (
    generate_plan,
    update_dashboard_stats,
    get_inbox_summary,
    check_approved_actions,
    process_approved_action
)

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'


def run_scheduled_update():
    """Run all periodic update tasks."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Running scheduled update...")

    # 1. Update dashboard stats
    print("  Updating dashboard...")
    result = update_dashboard_stats()
    print(f"  {result}")

    # 2. Generate plan from inbox
    print("  Generating plan...")
    result = generate_plan()
    print(f"  {result}")

    # 3. Check inbox summary
    summary = get_inbox_summary()
    print(f"  Inbox: {summary['count']} items")

    # 4. Process any approved actions
    approved = check_approved_actions()
    if approved:
        print(f"  Processing {len(approved)} approved action(s)...")
        for action_file in approved:
            result = process_approved_action(action_file)
            print(f"    {result}")
    else:
        print("  No pending approved actions.")

    # 5. Log the run
    log_path = VAULT_PATH / "Logs"
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"

    log_entry = f"\n- **{now}**: Scheduled update completed. Inbox: {summary['count']} items. Approved actions: {len(approved)}.\n"

    with open(log_file, 'a', encoding='utf-8') as f:
        if log_file.stat().st_size == 0 if log_file.exists() else True:
            f.write(f"# AI Employee Log - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(log_entry)

    print(f"  Logged to {log_file.name}")
    print(f"[{now}] Scheduled update complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Employee Scheduled Task")
    parser.add_argument('--daily', action='store_true', help='Run daily briefing mode')
    args = parser.parse_args()

    run_scheduled_update()
