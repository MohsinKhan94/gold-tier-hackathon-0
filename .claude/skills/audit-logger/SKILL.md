---
name: audit-logger
description: View and manage structured JSON audit logs of all AI Employee actions. Use this to check action history, review what the AI has done, or verify compliance.
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Bash(python *audit_logger*)
---

# Audit Logger Skill

View and manage structured JSON audit logs for every action the AI Employee takes.

## Log Format

Every action is logged as a JSON entry in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-02-20T10:30:00",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": {"subject": "Invoice #123"},
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

## Operations

### View Today's Log
Read `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

### Get Summary
Run `python ai-employee-watcher/audit_logger.py` for today's summary

### View Specific Date
Read `AI_Employee_Vault/Logs/2026-02-19.json` (any date)

### Cleanup Old Logs
Logs older than 90 days are auto-cleaned by the scheduler

## Action Types Logged

- `email_send`, `email_draft`, `email_search`
- `odoo_*` (all Odoo operations)
- `cross_domain_classification`
- `ceo_briefing_generated`
- `watchdog_*` (process health events)
- `quarantine_file`
- `social_post`, `linkedin_post`

## When to Use

- User asks "What did the AI do today?"
- Reviewing actions before/after a specific time
- Compliance checking
- Debugging failed actions
