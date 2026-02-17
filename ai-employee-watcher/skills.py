"""
Agent Skills for Personal AI Employee
These are callable functions that Claude Code can use
"""

import os
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'

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
        write_vault_file("Inbox/new_task.md", "# Task\\nDetails here")
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
    inbox_count = len(list_vault_folder("Inbox"))
    needs_action_count = len(list_vault_folder("Needs_Action"))
    done_count = len(list_vault_folder("Done"))
    
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
# Export all skills for Claude Code
# ================================================================
__all__ = [
    'read_vault_file',
    'write_vault_file',
    'list_vault_folder',
    'get_inbox_summary',
    'move_vault_file',
    'create_inbox_item',
    'update_dashboard_stats'
]