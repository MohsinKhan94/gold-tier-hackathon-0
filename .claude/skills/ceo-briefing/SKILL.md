---
name: ceo-briefing
description: Generate the Monday Morning CEO Briefing by pulling data from Odoo ERP, completed tasks, audit logs, and business goals. Use this when the user asks for a business summary, weekly report, or CEO briefing.
user-invocable: true
allowed-tools:
  - mcp: odoo
  - Read
  - Write
  - Glob
  - Bash(python *ceo_briefing*)
---

# CEO Weekly Briefing Skill

Generate a comprehensive Monday Morning CEO Briefing with financial data from Odoo, task completion stats, and proactive suggestions.

## How It Works

1. **Read Business_Goals.md** for revenue targets and KPIs
2. **Query Odoo** for weekly financial data (invoices, sales, receivables, leads)
3. **Scan Done/ folder** for tasks completed this week
4. **Read audit logs** for AI activity summary
5. **Identify bottlenecks** (draft invoices, unpaid receivables, low activity)
6. **Generate suggestions** (proactive actions for the week)
7. **Save to Briefings/** as `YYYY-MM-DD_Monday_Briefing.md`

## Trigger

- Runs automatically: Sunday night at 22:00 via start_gold.py scheduler
- Manual trigger: `python ai-employee-watcher/ceo_briefing.py`
- User asks: "Generate CEO briefing", "Weekly business summary", "How's the business?"

## Output Format

The briefing includes:
- Financial Summary (invoiced, paid, receivable, revenue)
- CRM Pipeline (leads, pipeline value, customers)
- Tasks Completed this week
- AI Employee Activity stats
- Bottlenecks & Issues
- Proactive Suggestions

## When to Use

- User asks for a business report or weekly summary
- Monday morning status check
- Before business meetings or planning sessions
- Reviewing AI Employee performance
