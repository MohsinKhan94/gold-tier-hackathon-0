"""
CEO Weekly Briefing Generator - Gold Tier
Generates a Monday Morning CEO Briefing by reading:
- Business_Goals.md for targets
- Odoo API for revenue, expenses, invoices
- Done/ folder for completed tasks this week
- Social media metrics (if available)

Outputs: AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md

Scheduled to run Sunday night via Task Scheduler or cron.
Can also be triggered manually.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
VAULT_PATH = BASE_DIR.parent / "AI_Employee_Vault"
BRIEFINGS_PATH = VAULT_PATH / "Briefings"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
GOALS_FILE = VAULT_PATH / "Business_Goals.md"

BRIEFINGS_PATH.mkdir(parents=True, exist_ok=True)

# Import Odoo client and audit logger
sys.path.insert(0, str(BASE_DIR))
try:
    from odoo_mcp_server import OdooClient
    odoo = OdooClient()
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    odoo = None

try:
    from audit_logger import log_audit, get_audit_summary
except ImportError:
    def log_audit(**kwargs): pass
    def get_audit_summary(d=None): return {"total": 0}


def get_odoo_weekly_summary() -> dict:
    """Query Odoo for this week's financial data."""
    if not ODOO_AVAILABLE:
        return {"error": "Odoo not available"}

    try:
        odoo.authenticate()

        # Date range: last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        # Invoices created this week
        invoices = odoo.search_read(
            "account.move",
            [["move_type", "=", "out_invoice"], ["create_date", ">=", week_ago]],
            ["name", "partner_id", "amount_total", "state", "payment_state"],
            limit=100,
        )

        total_invoiced = sum(inv.get("amount_total", 0) for inv in invoices)
        posted_invoices = [inv for inv in invoices if inv.get("state") == "posted"]
        paid_invoices = [inv for inv in invoices if inv.get("payment_state") == "paid"]
        draft_invoices = [inv for inv in invoices if inv.get("state") == "draft"]

        # Sale orders this week
        orders = odoo.search_read(
            "sale.order",
            [["create_date", ">=", week_ago]],
            ["name", "partner_id", "amount_total", "state"],
            limit=100,
        )
        total_orders = sum(o.get("amount_total", 0) for o in orders)

        # CRM leads this week
        leads = odoo.search_read(
            "crm.lead",
            [["create_date", ">=", week_ago]],
            ["name", "expected_revenue", "stage_id"],
            limit=100,
        )
        total_pipeline = sum(l.get("expected_revenue", 0) for l in leads)

        # Customer count
        customers = odoo.search_read(
            "res.partner",
            [["customer_rank", ">", 0]],
            ["id"],
            limit=None,
        )

        # Account balance
        receivable = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "asset_receivable"], ["parent_state", "=", "posted"]],
            ["balance"],
            limit=None,
        )
        total_receivable = sum(line.get("balance", 0) for line in receivable)

        revenue_lines = odoo.search_read(
            "account.move.line",
            [["account_id.account_type", "=", "income"], ["parent_state", "=", "posted"]],
            ["balance"],
            limit=None,
        )
        total_revenue = abs(sum(line.get("balance", 0) for line in revenue_lines))

        return {
            "period": f"{week_ago} to {today}",
            "invoices_created": len(invoices),
            "invoices_posted": len(posted_invoices),
            "invoices_paid": len(paid_invoices),
            "invoices_draft": len(draft_invoices),
            "total_invoiced": round(total_invoiced, 2),
            "sale_orders": len(orders),
            "total_orders": round(total_orders, 2),
            "new_leads": len(leads),
            "pipeline_value": round(total_pipeline, 2),
            "total_customers": len(customers),
            "accounts_receivable": round(total_receivable, 2),
            "total_revenue": round(total_revenue, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_completed_tasks_this_week() -> list:
    """Get tasks completed this week from Done/ folder."""
    tasks = []
    week_ago = datetime.now() - timedelta(days=7)

    if not DONE_PATH.exists():
        return tasks

    for f in DONE_PATH.iterdir():
        if f.is_file() and f.suffix == ".md":
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime >= week_ago:
                    tasks.append({
                        "name": f.stem,
                        "completed": mtime.strftime("%Y-%m-%d %H:%M"),
                    })
            except OSError:
                continue

    return sorted(tasks, key=lambda x: x["completed"], reverse=True)


def get_audit_weekly_summary() -> dict:
    """Summarize audit log activity for the week."""
    total_actions = 0
    by_type = {}

    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        summary = get_audit_summary(date)
        total_actions += summary.get("total", 0)
        for action, count in summary.get("by_action", {}).items():
            by_type[action] = by_type.get(action, 0) + count

    return {"total_actions": total_actions, "by_type": by_type}


def identify_bottlenecks(completed_tasks: list, odoo_data: dict) -> list:
    """Identify potential bottlenecks and issues."""
    bottlenecks = []

    # Draft invoices not sent
    if odoo_data.get("invoices_draft", 0) > 0:
        bottlenecks.append(f"{odoo_data['invoices_draft']} draft invoice(s) not yet posted - revenue delayed")

    # Receivable too high
    if odoo_data.get("accounts_receivable", 0) > 0 and odoo_data.get("invoices_paid", 0) == 0:
        bottlenecks.append(f"Outstanding receivable of {odoo_data['accounts_receivable']} with no payments collected")

    # Low task completion
    if len(completed_tasks) < 3:
        bottlenecks.append(f"Only {len(completed_tasks)} tasks completed this week - check for blockers")

    # No new leads
    if odoo_data.get("new_leads", 0) == 0:
        bottlenecks.append("No new CRM leads this week - increase outreach efforts")

    return bottlenecks


def generate_suggestions(odoo_data: dict, bottlenecks: list) -> list:
    """Generate proactive suggestions based on data."""
    suggestions = []

    if odoo_data.get("invoices_draft", 0) > 0:
        suggestions.append("Post all draft invoices to start the payment clock")

    if odoo_data.get("new_leads", 0) == 0:
        suggestions.append("Schedule LinkedIn posts to generate inbound leads")

    if odoo_data.get("total_customers", 0) < 5:
        suggestions.append("Focus on client acquisition - target 5+ active customers")

    if not bottlenecks:
        suggestions.append("All systems running smoothly - consider expanding service offerings")

    return suggestions


def generate_briefing() -> str:
    """Generate the full Monday Morning CEO Briefing."""
    now = datetime.now()
    # Target Monday date (next Monday if not Monday)
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.hour >= 12:
        days_until_monday = 7
    monday_date = (now + timedelta(days=days_until_monday)).strftime("%Y-%m-%d")

    # Gather data
    odoo_data = get_odoo_weekly_summary()
    completed_tasks = get_completed_tasks_this_week()
    audit_summary = get_audit_weekly_summary()
    bottlenecks = identify_bottlenecks(completed_tasks, odoo_data) if "error" not in odoo_data else []
    suggestions = generate_suggestions(odoo_data, bottlenecks) if "error" not in odoo_data else []

    # Read business goals
    goals_content = ""
    if GOALS_FILE.exists():
        goals_content = GOALS_FILE.read_text(encoding="utf-8")

    # Build briefing
    briefing = f"""# Monday Morning CEO Briefing
**Date:** {monday_date}
**Generated:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**Period:** Last 7 days

---

## Financial Summary
"""

    if "error" in odoo_data:
        briefing += f"\n> Odoo data unavailable: {odoo_data['error']}\n"
    else:
        briefing += f"""
| Metric | Value |
|--------|-------|
| Total Invoiced | {odoo_data.get('total_invoiced', 0):,.2f} |
| Invoices Posted | {odoo_data.get('invoices_posted', 0)} |
| Invoices Paid | {odoo_data.get('invoices_paid', 0)} |
| Draft Invoices | {odoo_data.get('invoices_draft', 0)} |
| Sale Orders | {odoo_data.get('sale_orders', 0)} (Total: {odoo_data.get('total_orders', 0):,.2f}) |
| Accounts Receivable | {odoo_data.get('accounts_receivable', 0):,.2f} |
| Total Revenue (All Time) | {odoo_data.get('total_revenue', 0):,.2f} |

## CRM Pipeline

| Metric | Value |
|--------|-------|
| New Leads This Week | {odoo_data.get('new_leads', 0)} |
| Pipeline Value | {odoo_data.get('pipeline_value', 0):,.2f} |
| Total Customers | {odoo_data.get('total_customers', 0)} |
"""

    # Completed tasks
    briefing += f"\n## Tasks Completed ({len(completed_tasks)})\n\n"
    if completed_tasks:
        for task in completed_tasks[:15]:
            briefing += f"- {task['name']} ({task['completed']})\n"
    else:
        briefing += "No tasks completed this week.\n"

    # AI Activity
    briefing += f"\n## AI Employee Activity\n\n"
    briefing += f"- **Total Actions This Week:** {audit_summary.get('total_actions', 0)}\n"
    if audit_summary.get("by_type"):
        briefing += "- **Breakdown:**\n"
        for action, count in sorted(audit_summary["by_type"].items(), key=lambda x: x[1], reverse=True)[:10]:
            briefing += f"  - {action}: {count}\n"

    # Bottlenecks
    briefing += "\n## Bottlenecks & Issues\n\n"
    if bottlenecks:
        for b in bottlenecks:
            briefing += f"- {b}\n"
    else:
        briefing += "No major bottlenecks identified.\n"

    # Suggestions
    briefing += "\n## Proactive Suggestions\n\n"
    if suggestions:
        for s in suggestions:
            briefing += f"- {s}\n"

    briefing += "\n---\n*Generated by AI Employee - Gold Tier*\n"

    return briefing


def save_briefing():
    """Generate and save the briefing to the vault."""
    briefing = generate_briefing()
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_Monday_Briefing.md"
    filepath = BRIEFINGS_PATH / filename

    filepath.write_text(briefing, encoding="utf-8")

    log_audit(
        action_type="ceo_briefing_generated",
        target=str(filepath),
        parameters={"filename": filename},
    )

    return filepath


if __name__ == "__main__":
    print("=== Generating CEO Monday Briefing ===")
    filepath = save_briefing()
    print(f"Briefing saved to: {filepath}")
    print()
    print(filepath.read_text(encoding="utf-8"))
