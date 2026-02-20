---
name: inbox-manager
description: Process, triage, and manage items in the vault Inbox. Use this to review inbox items, move them to appropriate folders, create new tasks, or get an inbox summary.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls *), Bash(mv *)
---

# Inbox Manager Skill

Triage and process items in `AI_Employee_Vault/Inbox/`.

## Operations

### Get Inbox Summary
List all files in `AI_Employee_Vault/Inbox/` and report:
- Total count
- Breakdown by type (Email, WhatsApp, File Alert, Task)
- Oldest unprocessed item

### Triage an Item
1. Read the item from Inbox
2. Determine category and priority
3. Move to appropriate folder:
   - High priority requiring action -> `Needs_Action/`
   - Completed/processed -> `Done/`
   - Needs human decision -> `Pending_Approval/`

### Create New Inbox Item
Write a new markdown file to `AI_Employee_Vault/Inbox/` with:
```markdown
# [Priority Emoji] Title

**Created:** YYYY-MM-DD HH:MM:SS
**Priority:** high/normal/low
**Source:** manual/email/whatsapp/file

## Details
Description of the item

## Action Required
- [ ] Review
- [ ] Take action
- [ ] Mark as done

---
*Created by AI Agent*
```

### Bulk Process
Process all inbox items at once:
1. Read each item
2. Categorize by priority
3. Move high-priority to Needs_Action
4. Move low-priority informational items to Done
5. Update Dashboard after processing

## Priority Indicators
- High: Contains "urgent", "asap", "payment", "invoice", from VIP
- Normal: Standard emails, messages, file alerts
- Low: Newsletters, notifications, test items
