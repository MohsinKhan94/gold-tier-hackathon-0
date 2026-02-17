"""Quick check and update"""
from skills import update_dashboard_stats, get_inbox_summary

# Update dashboard
result = update_dashboard_stats()
print(f"\n{result}\n")

# Show inbox details
summary = get_inbox_summary()
print(f"📥 Inbox Items ({summary['count']}):")
for file in summary['files']:
    print(f"   - {file}")
print()