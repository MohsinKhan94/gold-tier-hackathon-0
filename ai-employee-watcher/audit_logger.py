"""
Structured Audit Logger - Gold Tier
Logs every AI action in structured JSON format to AI_Employee_Vault/Logs/YYYY-MM-DD.json.
Retains 90+ days of logs. Used across all skills and MCP servers.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Retention period in days
RETENTION_DAYS = 90


def log_audit(
    action_type: str,
    target: str = "",
    parameters: dict = None,
    result: str = "success",
    actor: str = "claude_code",
    approval_status: str = "",
    approved_by: str = "",
    error_message: str = "",
    metadata: dict = None,
) -> dict:
    """
    Log a structured JSON audit entry.

    Args:
        action_type: Type of action (e.g., 'email_send', 'invoice_create', 'odoo_query')
        target: Target of the action (e.g., email address, customer name, invoice ID)
        parameters: Action parameters dict
        result: 'success', 'failure', 'pending', 'blocked'
        actor: Who performed the action (default 'claude_code')
        approval_status: 'approved', 'pending', 'rejected', or empty
        approved_by: 'human', 'auto', or empty
        error_message: Error details if result is 'failure'
        metadata: Additional context

    Returns:
        The log entry dict
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": actor,
        "target": target,
        "parameters": parameters or {},
        "result": result,
    }

    if approval_status:
        entry["approval_status"] = approval_status
    if approved_by:
        entry["approved_by"] = approved_by
    if error_message:
        entry["error_message"] = error_message
    if metadata:
        entry["metadata"] = metadata

    # Write to daily JSON log file
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{date_str}.json"

    entries = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, IOError):
            entries = []

    entries.append(entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, default=str)

    return entry


def get_audit_log(date_str: str = None) -> list:
    """
    Read audit log entries for a given date.

    Args:
        date_str: Date in YYYY-MM-DD format. Defaults to today.

    Returns:
        List of log entry dicts
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    log_file = LOGS_PATH / f"{date_str}.json"
    if not log_file.exists():
        return []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def get_audit_summary(date_str: str = None) -> dict:
    """
    Get a summary of audit log entries for a given date.

    Args:
        date_str: Date in YYYY-MM-DD format. Defaults to today.

    Returns:
        Summary dict with counts by action type and result
    """
    entries = get_audit_log(date_str)
    if not entries:
        return {"date": date_str or datetime.now().strftime("%Y-%m-%d"), "total": 0, "by_action": {}, "by_result": {}}

    by_action = {}
    by_result = {}

    for entry in entries:
        action = entry.get("action_type", "unknown")
        result = entry.get("result", "unknown")

        by_action[action] = by_action.get(action, 0) + 1
        by_result[result] = by_result.get(result, 0) + 1

    return {
        "date": date_str or datetime.now().strftime("%Y-%m-%d"),
        "total": len(entries),
        "by_action": by_action,
        "by_result": by_result,
    }


def cleanup_old_logs():
    """
    Remove audit log files older than RETENTION_DAYS.
    Called during scheduled maintenance.
    """
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed = 0

    for log_file in LOGS_PATH.glob("*.json"):
        try:
            # Parse date from filename (YYYY-MM-DD.json)
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()
                removed += 1
        except (ValueError, OSError):
            continue

    return removed


if __name__ == "__main__":
    # Demo / test
    print("=== Audit Logger Test ===")

    entry = log_audit(
        action_type="test_action",
        target="test_target",
        parameters={"key": "value"},
        result="success",
        metadata={"test": True},
    )
    print(f"Logged: {json.dumps(entry, indent=2)}")

    summary = get_audit_summary()
    print(f"\nToday's summary: {json.dumps(summary, indent=2)}")

    removed = cleanup_old_logs()
    print(f"\nCleanup: removed {removed} old log files")
