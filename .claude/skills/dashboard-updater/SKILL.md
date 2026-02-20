---
name: dashboard-updater
description: Update the Dashboard.md with current counts from Inbox, Needs_Action, Done, and Social_Posts folders. Use this after processing items or when the user asks for a status update.
user-invocable: true
allowed-tools: Read, Write, Glob
---

# Dashboard Updater Skill

Update `AI_Employee_Vault/Dashboard.md` with live statistics from all vault folders.

## How to Update Dashboard

1. Count files in each folder:
   - `AI_Employee_Vault/Inbox/*.md`
   - `AI_Employee_Vault/Needs_Action/*.md`
   - `AI_Employee_Vault/Done/*.md`
   - `AI_Employee_Vault/Social_Posts/Drafts/*.md`
   - `AI_Employee_Vault/Social_Posts/Approved/*.md`
   - `AI_Employee_Vault/Social_Posts/Posted/*.md`
   - `AI_Employee_Vault/Pending_Approval/*.md`

2. Write updated Dashboard.md:

```markdown
# Personal AI Employee Dashboard

**Last Updated:** YYYY-MM-DD HH:MM:SS

## Status Overview
- **System Status:** Online
- **Active Tasks:** [needs_action_count]
- **Pending Review:** [inbox_count]
- **Completed:** [done_count]

## Inbox
[inbox_count] items pending

## Needs Action
[needs_action_count] active tasks

## Recently Completed
[done_count] items in Done folder

## Social Media
- Drafts: [drafts_count]
- Approved: [approved_count]
- Posted: [posted_count]

## Pending Approval
[pending_approval_count] items awaiting human approval

## Weekly Summary
**Total Items Tracked:** [total]

---
*Powered by Claude Code + Obsidian*
*Auto-updated by Agent Skills*
```

## When to Update
- After processing inbox items
- After moving files between folders
- When user asks for status
- On scheduled intervals
