# Agent Skills - Personal AI Employee

This document defines all available skills that Claude Code can use to manage this Obsidian vault.
All AI functionality is implemented as **Claude Code Agent Skills** in `.claude/skills/`.

## Agent Skills (.claude/skills/)

| Skill | Description | Invocation |
|-------|------------|------------|
| vault-operations | Read, write, list, move vault files | `/vault-operations` |
| file-monitoring | Monitor Watch_This_Folder for new files | `/file-monitoring` |
| email-monitoring | Monitor Gmail and create email alerts | `/email-monitoring` |
| whatsapp-monitoring | Monitor WhatsApp messages | `/whatsapp-monitoring` |
| linkedin-posting | Draft, approve, and post to LinkedIn | `/linkedin-posting` |
| plan-generator | Generate Plan.md from inbox items | `/plan-generator` |
| dashboard-updater | Update Dashboard.md with live stats | `/dashboard-updater` |
| human-approval | Approval workflow for sensitive actions | `/human-approval` |
| inbox-manager | Triage and process inbox items | `/inbox-manager` |
| email-sending | Send, draft, search emails via Gmail MCP | `/email-sending` |

## MCP Servers

| Server | Transport | Tools | File |
|--------|-----------|-------|------|
| gmail | stdio | send_email, draft_email, search_emails, list_recent_emails | `ai-employee-watcher/gmail_mcp_server.py` |

**Configuration:** `.claude/settings.local.json` registers the Gmail MCP server with Claude Code.

### Gmail MCP Tools
- **send_email(to, subject, body, cc?, bcc?)** - Send an email via Gmail API
- **draft_email(to, subject, body)** - Create a draft in Gmail
- **search_emails(query, max_results?)** - Search emails with Gmail query syntax
- **list_recent_emails(max_results?)** - List recent unread emails

All actions are logged to `AI_Employee_Vault/Logs/email_actions_*.md`.

## Python Skill Functions (ai-employee-watcher/skills.py)

### 1. read_vault_file(filepath)
**Purpose:** Read any file from the vault
**Example:** `read_vault_file("Inbox/task.md")`

### 2. write_vault_file(filepath, content)
**Purpose:** Write or update a vault file
**Example:** `write_vault_file("Inbox/new.md", "# Task\nDetails")`

### 3. list_vault_folder(folder)
**Purpose:** List all files in a folder
**Example:** `list_vault_folder("Inbox")`

### 4. get_inbox_summary()
**Purpose:** Get statistics about inbox
**Example:** `get_inbox_summary()`

### 5. move_vault_file(filename, from_folder, to_folder)
**Purpose:** Move files between folders
**Example:** `move_vault_file("task.md", "Inbox", "Done")`

### 6. create_inbox_item(title, content, priority)
**Purpose:** Create new inbox tasks
**Example:** `create_inbox_item("Review", "Check docs", "high")`

### 7. update_dashboard_stats()
**Purpose:** Auto-update dashboard with current counts
**Example:** `update_dashboard_stats()`

### 8. generate_plan()
**Purpose:** Reads Inbox, categorizes items, and creates Plan.md with priorities.
**Example:** `generate_plan()`

### 9. create_approval_request(action, description, details)
**Purpose:** Create a human-in-the-loop approval request for sensitive actions
**Example:** `create_approval_request("payment", "Pay invoice #123", "Amount: $500")`

### 10. check_approved_actions()
**Purpose:** List approved actions ready for execution
**Example:** `check_approved_actions()`

### 11. process_approved_action(filename)
**Purpose:** Execute an approved action and archive it
**Example:** `process_approved_action("APPROVAL_payment_20260219.md")`

## How Claude Code Uses These Skills

When you interact with Claude Code, you can say:
- "Show me what's in my inbox" -> Uses `/inbox-manager`
- "Create a plan for today" -> Uses `/plan-generator`
- "Update my dashboard" -> Uses `/dashboard-updater`
- "Draft a LinkedIn post" -> Uses `/linkedin-posting`
- "Check for approved actions" -> Uses `/human-approval`
- "Send an email to X" -> Uses `/email-sending` (MCP)
- "Draft a reply to this email" -> Uses `/email-sending` (MCP)
- "Search my emails for invoices" -> Uses `/email-sending` (MCP)

## Implementation
- Agent Skills: `.claude/skills/<skill-name>/SKILL.md`
- Python functions: `ai-employee-watcher/skills.py`
- Watchers: `ai-employee-watcher/file_watcher.py`, `mock_watcher.py`, `gmail_watcher.py`
- Poster: `ai-employee-watcher/linkedin_poster.py`
- MCP Server: `ai-employee-watcher/gmail_mcp_server.py`
- Scheduler: `ai-employee-watcher/scheduled_task.py`
