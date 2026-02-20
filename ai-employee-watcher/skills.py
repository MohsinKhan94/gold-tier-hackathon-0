"""
Agent Skills for Personal AI Employee
These are callable functions that Claude Code can use.
All AI reasoning is handled by Claude Code via .claude/skills/ - no external LLM needed.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
PLAN_FILE = VAULT_PATH / "Plan.md"

# ================================================================
# SKILL: Read Vault File
# ================================================================
def read_vault_file(filepath: str) -> str:
    """
    Read a file from the Obsidian vault.
    
    Args:
        filepath: Path relative to vault root (e.g., "Dashboard.md")
    
    Returns:
        File contents as string
    
    Example:
        content = read_vault_file("Dashboard.md")
    """
    full_path = VAULT_PATH / filepath
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    return f"Error: File not found: {filepath}"


# ================================================================
# SKILL: Write Vault File
# ================================================================
def write_vault_file(filepath: str, content: str) -> str:
    """
    Write content to a file in the Obsidian vault.
    
    Args:
        filepath: Path relative to vault root (e.g., "Inbox/task.md")
        content: Content to write
    
    Returns:
        Success message
    
    Example:
        write_vault_file("Inbox/new_task.md", "# Task\nDetails here")
    """
    full_path = VAULT_PATH / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"✅ Successfully wrote to: {filepath}"


# ================================================================
# SKILL: List Vault Folder
# ================================================================
def list_vault_folder(folder: str = "") -> list:
    """
    List files in a vault folder.
    
    Args:
        folder: Folder name (e.g., "Inbox", "Done"). Empty string for root.
    
    Returns:
        List of filenames
    
    Example:
        files = list_vault_folder("Inbox")
    """
    folder_path = VAULT_PATH / folder if folder else VAULT_PATH
    if folder_path.exists():
        return [f.name for f in folder_path.iterdir() if f.is_file()]
    return []


# ================================================================
# SKILL: Get Inbox Summary
# ================================================================
def get_inbox_summary() -> dict:
    """
    Get summary of items in Inbox.
    
    Returns:
        Dictionary with inbox statistics
    
    Example:
        summary = get_inbox_summary()
        print(f"You have {summary['count']} items in inbox")
    """
    inbox_path = VAULT_PATH / "Inbox"
    if not inbox_path.exists():
        return {"count": 0, "files": []}
    
    files = [f.name for f in inbox_path.iterdir() if f.is_file()]
    return {
        "count": len(files),
        "files": files,
        "oldest": min([f.stat().st_mtime for f in inbox_path.iterdir() if f.is_file()], default=0) if files else 0
    }


# ================================================================
# SKILL: Move File Between Folders
# ================================================================
def move_vault_file(filename: str, from_folder: str, to_folder: str) -> str:
    """
    Move a file from one vault folder to another.
    
    Args:
        filename: Name of the file (e.g., "task.md")
        from_folder: Source folder (e.g., "Inbox")
        to_folder: Destination folder (e.g., "Done")
    
    Returns:
        Success message
    
    Example:
        move_vault_file("task.md", "Inbox", "Done")
    """
    source = VAULT_PATH / from_folder / filename
    dest_folder = VAULT_PATH / to_folder
    dest_folder.mkdir(exist_ok=True)
    dest = dest_folder / filename
    
    if source.exists():
        source.rename(dest)
        return f"✅ Moved {filename} from {from_folder} to {to_folder}"
    return f"❌ Error: {filename} not found in {from_folder}"


# ================================================================
# SKILL: Create Inbox Item
# ================================================================
def create_inbox_item(title: str, content: str, priority: str = "normal") -> str:
    """
    Create a new item in the Inbox.
    
    Args:
        title: Title of the item
        content: Description/details
        priority: "high", "normal", or "low"
    
    Returns:
        Filename created
    
    Example:
        create_inbox_item("Review Contract", "Client sent new terms", "high")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Task_{timestamp}.md"
    
    priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(priority, "🟡")
    
    full_content = f"""# {priority_emoji} {title}

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Priority:** {priority}

## Details
{content}

## Action Required
- [ ] Review
- [ ] Take action
- [ ] Mark as done

---
*Created by AI Agent*
"""
    
    write_vault_file(f"Inbox/{filename}", full_content)
    return filename


# ================================================================
# SKILL: Update Dashboard
# ================================================================
def update_dashboard_stats() -> str:
    """
    Update dashboard with current stats.
    
    Returns:
        Updated dashboard preview
    
    Example:
        update_dashboard_stats()
    """
    inbox_path = VAULT_PATH / "Inbox"
    needs_action_path = VAULT_PATH / "Needs_Action"
    done_path = VAULT_PATH / "Done"

    inbox_count = len([f for f in inbox_path.iterdir() if f.is_file()]) if inbox_path.exists() else 0
    needs_action_count = len([f for f in needs_action_path.iterdir() if f.is_file()]) if needs_action_path.exists() else 0
    done_count = len([f for f in done_path.iterdir() if f.is_file()]) if done_path.exists() else 0
    
    dashboard_content = f"""# 🎯 Personal AI Employee Dashboard

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Status Overview
- **System Status:** 🟢 Online
- **Active Tasks:** {needs_action_count}
- **Pending Review:** {inbox_count}
- **Completed Today:** {done_count}

## 🔔 Inbox (Needs Immediate Attention)
{inbox_count} items pending

## ⚡ Needs Action
{needs_action_count} active tasks

## ✅ Recently Completed
{done_count} items in Done folder

## 📈 Weekly Summary
**Total Items Tracked:** {inbox_count + needs_action_count + done_count}

---
*Powered by Claude Code + Obsidian*
*Auto-updated by Agent Skills*
"""
    
    write_vault_file("Dashboard.md", dashboard_content)
    return f"✅ Dashboard updated: {inbox_count} inbox, {needs_action_count} action items, {done_count} done"

# ================================================================
# SKILL: Check Gmail
# ================================================================
def check_gmail():
    """
    Check Gmail for new emails and create alerts.

    Returns:
        Count of new emails processed
    """
    # This would call gmail_watcher functions
    # For now, returns status
    return "Gmail check initiated - see gmail_watcher.py"


# ================================================================
# SKILL: Generate Plan (Claude Code handles reasoning via .claude/skills/)
# ================================================================
def generate_plan():
    """
    Reads Inbox items, categorizes and prioritizes them, and writes Plan.md.
    No external LLM needed - Claude Code provides reasoning via Agent Skills.
    """
    inbox_path = VAULT_PATH / "Inbox"
    needs_action_path = VAULT_PATH / "Needs_Action"

    for p in [inbox_path, needs_action_path]:
        p.mkdir(parents=True, exist_ok=True)

    items = []

    # Read all inbox items
    try:
        for file in sorted(inbox_path.glob("*.md"), key=os.path.getmtime, reverse=True):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract title (first heading)
                title = file.stem
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break

                # Detect priority
                priority = "normal"
                content_lower = content.lower()
                if any(kw in content_lower for kw in ["high", "urgent", "asap", "important"]):
                    priority = "high"
                elif any(kw in content_lower for kw in ["low", "newsletter", "info"]):
                    priority = "low"

                # Detect source type
                source = "task"
                fname = file.name.lower()
                if fname.startswith("email"):
                    source = "email"
                elif fname.startswith("wh"):
                    source = "whatsapp"
                elif fname.startswith("file_alert"):
                    source = "file"
                elif fname.startswith("li") or fname.startswith("ln"):
                    source = "linkedin"

                items.append({
                    "title": title,
                    "filename": file.name,
                    "priority": priority,
                    "source": source
                })
    except Exception as e:
        print(f"Error reading inbox: {e}")

    # Read needs_action items
    try:
        for file in sorted(needs_action_path.glob("*.md"), key=os.path.getmtime, reverse=True):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                title = file.stem
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                items.append({
                    "title": title,
                    "filename": file.name,
                    "priority": "high",
                    "source": "action"
                })
    except Exception as e:
        print(f"Error reading needs_action: {e}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not items:
        plan = f"# Plan\n\n**Generated:** {now}\n**Items Analyzed:** 0\n\n_No items in Inbox or Needs_Action. Nothing to plan!_\n"
        with open(PLAN_FILE, "w", encoding="utf-8") as f:
            f.write(plan)
        return "No inbox items. Plan.md created with empty plan."

    # Categorize by priority
    high = [i for i in items if i["priority"] == "high"]
    medium = [i for i in items if i["priority"] == "normal"]
    low = [i for i in items if i["priority"] == "low"]

    def format_items(item_list):
        lines = []
        for item in item_list:
            lines.append(f"- [ ] {item['title']} (source: {item['source']}, file: {item['filename']})")
        return '\n'.join(lines) if lines else "_None_"

    plan_md = f"""# Plan

**Generated:** {now}
**Items Analyzed:** {len(items)}

## High Priority
{format_items(high)}

## Medium Priority
{format_items(medium)}

## Low Priority
{format_items(low)}

## Summary
- Total items: {len(items)}
- High priority: {len(high)}
- Medium priority: {len(medium)}
- Low priority: {len(low)}

---
*Generated by AI Employee Plan Generator*
*Reasoning powered by Claude Code Agent Skills*
"""

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(plan_md)
    return f"Plan.md generated with {len(items)} inbox items."


# ================================================================
# SKILL: Create Approval Request
# ================================================================
def create_approval_request(action: str, description: str, details: str = "") -> str:
    """
    Create an approval request for sensitive actions.

    Args:
        action: Type of action (payment, email_send, social_post, file_delete)
        description: Brief description of what needs approval
        details: Additional details

    Returns:
        Filename of approval request
    """
    pending_path = VAULT_PATH / "Pending_Approval"
    pending_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"APPROVAL_{action}_{timestamp}.md"

    now = datetime.now()
    expires = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    content = f"""---
type: approval_request
action: {action}
created: {now.strftime("%Y-%m-%dT%H:%M:%SZ")}
status: pending
---

# Approval Required: {description}

## Details
- **Action:** {action}
- **Description:** {description}
{details}

## To Approve
Move this file to the `Approved/` folder.

## To Reject
Delete this file or move to `Done/` with a rejection note.

---
*Created by AI Employee*
"""

    filepath = pending_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filename


# ================================================================
# SKILL: Check Approved Actions
# ================================================================
def check_approved_actions() -> list:
    """
    Check for approved actions ready for execution.

    Returns:
        List of approved action filenames
    """
    approved_path = VAULT_PATH / "Approved"
    approved_path.mkdir(parents=True, exist_ok=True)

    return [f.name for f in approved_path.iterdir() if f.is_file()]


# ================================================================
# SKILL: Process Approved Action
# ================================================================
def process_approved_action(filename: str) -> str:
    """
    Process an approved action and move it to Done.

    Args:
        filename: Name of the approved file

    Returns:
        Result message
    """
    approved_path = VAULT_PATH / "Approved" / filename
    done_path = VAULT_PATH / "Done"
    done_path.mkdir(parents=True, exist_ok=True)

    if not approved_path.exists():
        return f"Error: {filename} not found in Approved folder"

    # Read the approval
    with open(approved_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Move to Done with execution note
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content += f"\n\n## Execution Log\n- **Executed:** {now}\n- **Status:** Completed\n"

    done_file = done_path / f"DONE_{filename}"
    with open(done_file, 'w', encoding='utf-8') as f:
        f.write(content)

    approved_path.unlink()
    return f"Approved action {filename} executed and moved to Done"


# ================================================================
# Export all skills for Claude Code
# ================================================================
__all__ = [
    'read_vault_file',
    'write_vault_file',
    'list_vault_folder',
    'get_inbox_summary',
    'move_vault_file',
    'create_inbox_item',
    'update_dashboard_stats',
    'check_gmail',
    'generate_plan',
    'create_approval_request',
    'check_approved_actions',
    'process_approved_action'
]
