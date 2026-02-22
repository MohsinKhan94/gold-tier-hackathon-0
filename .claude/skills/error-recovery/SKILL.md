---
name: error-recovery
description: Monitor system health, manage the retry queue, check watchdog status, and handle error recovery. Use this when checking system health, viewing failed actions, or troubleshooting issues.
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Bash(python *watchdog*)
  - Bash(python *retry_handler*)
---

# Error Recovery Skill

Monitor and manage the AI Employee's error recovery systems including the watchdog, retry queue, and quarantine.

## Components

### Watchdog Monitor (`watchdog_monitor.py`)
- Monitors all watcher processes (Gmail, File, WhatsApp, LinkedIn, Plan Loop)
- Auto-restarts crashed processes (up to 5 attempts)
- Logs health status to `AI_Employee_Vault/Logs/watchdog_health.json`

### Retry Handler (`retry_handler.py`)
- Exponential backoff retry for transient errors (API timeouts, network issues)
- Queues failed actions in `AI_Employee_Vault/Logs/retry_queue.json`
- **NEVER auto-retries payment actions** - requires fresh human approval

### File Quarantine
- Corrupted/problematic files are moved to `AI_Employee_Vault/Quarantine/`
- Metadata file (.meta.json) explains why the file was quarantined

## Operations

### Check System Health
Read `AI_Employee_Vault/Logs/watchdog_health.json` for current process status

### View Retry Queue
Read `AI_Employee_Vault/Logs/retry_queue.json` for queued failed actions

### Check Service Availability
Run `python -c "from retry_handler import is_service_available; print(is_service_available('odoo'))"`

### View Quarantined Files
List `AI_Employee_Vault/Quarantine/` folder

## When to Use

- User asks "Is everything running OK?"
- Checking why a service failed
- Reviewing queued actions after an outage
- Investigating quarantined files
- System health dashboard
