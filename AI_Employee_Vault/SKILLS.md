# Agent Skills - Personal AI Employee

This document defines all available skills that Claude Code can use to manage this Obsidian vault.

## Available Skills

### 1. read_vault_file(filepath)
**Purpose:** Read any file from the vault  
**Input:** File path relative to vault (e.g., "Dashboard.md")  
**Output:** File contents  
**Example:** `read_vault_file("Inbox/task.md")`

### 2. write_vault_file(filepath, content)
**Purpose:** Write or update a vault file  
**Input:** File path and content string  
**Output:** Success confirmation  
**Example:** `write_vault_file("Inbox/new.md", "# Task\nDetails")`

### 3. list_vault_folder(folder)
**Purpose:** List all files in a folder  
**Input:** Folder name ("Inbox", "Done", etc.)  
**Output:** List of filenames  
**Example:** `list_vault_folder("Inbox")`

### 4. get_inbox_summary()
**Purpose:** Get statistics about inbox  
**Input:** None  
**Output:** Dict with count, files, oldest item  
**Example:** `get_inbox_summary()`

### 5. move_vault_file(filename, from_folder, to_folder)
**Purpose:** Move files between folders  
**Input:** Filename and source/destination folders  
**Output:** Success message  
**Example:** `move_vault_file("task.md", "Inbox", "Done")`

### 6. create_inbox_item(title, content, priority)
**Purpose:** Create new inbox tasks  
**Input:** Title, description, priority level  
**Output:** Created filename  
**Example:** `create_inbox_item("Review", "Check docs", "high")`

### 7. update_dashboard_stats()
**Purpose:** Auto-update dashboard with current counts  
**Input:** None  
**Output:** Updated dashboard confirmation  
**Example:** `update_dashboard_stats()`

## How Claude Code Uses These Skills

When you interact with Claude Code, you can say:
- "Show me what's in my inbox" → Uses `list_vault_folder("Inbox")`
- "Create a task to review the contract" → Uses `create_inbox_item()`
- "Update my dashboard" → Uses `update_dashboard_stats()`
- "Move task.md to Done" → Uses `move_vault_file()`

## Implementation
All skills are implemented in: `ai-employee-watcher/skills.py`