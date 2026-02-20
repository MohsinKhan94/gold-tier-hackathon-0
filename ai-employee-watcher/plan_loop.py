"""
Plan Loop - Silver Tier
Periodically generates Plan.md based on Inbox items.
No external LLM needed - Claude Code handles reasoning via Agent Skills.
"""

import time
from skills import generate_plan, update_dashboard_stats


def main():
    print("=" * 60)
    print("PLAN GENERATOR LOOP - Silver Tier")
    print("=" * 60)

    interval = 60  # Check every 60 seconds for demo

    print(f"Generating plan every {interval} seconds...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            print("Generating Plan.md...")
            result = generate_plan()
            print(f"  {result}")

            print("Updating Dashboard...")
            dashboard_res = update_dashboard_stats()
            print(f"  {dashboard_res}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nPlan Loop stopped")


if __name__ == "__main__":
    main()
