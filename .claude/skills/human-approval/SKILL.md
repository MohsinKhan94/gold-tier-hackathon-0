---
name: human-approval
description: Handle the human-in-the-loop approval workflow for sensitive actions like payments, external posts, and email sends. Use this when an action requires human authorization before execution.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Bash(ls *), Bash(mv *)
---

# Human-in-the-Loop Approval Skill

For sensitive actions, create an approval request file instead of acting directly.

## Folder Structure
```
AI_Employee_Vault/
  Pending_Approval/    # Items awaiting human decision
  Approved/            # Human-approved items ready for execution
```

## When to Require Approval
- Financial transactions over $50
- Sending emails to new contacts
- Publishing social media posts
- Deleting or moving files outside the vault
- Any action flagged in Company_Handbook.md

## Creating an Approval Request

Write a file to `AI_Employee_Vault/Pending_Approval/` with this format:

```markdown
---
type: approval_request
action: [payment/email_send/social_post/file_delete]
created: YYYY-MM-DDTHH:MM:SSZ
expires: YYYY-MM-DDTHH:MM:SSZ
status: pending
---

# Approval Required: [Action Description]

## Details
- **Action:** What will happen
- **Target:** Who/what is affected
- **Reason:** Why this action is needed

## To Approve
Move this file to the `Approved/` folder.

## To Reject
Delete this file or move to `Done/` with a rejection note.
```

## Processing Approved Items
1. Check `AI_Employee_Vault/Approved/` for new files
2. Read the approval request details
3. Execute the approved action
4. Log the result
5. Move the file to `Done/`

## Security Rules
- Never auto-approve sensitive actions
- Log all approval decisions
- Expired requests must be re-created
- Always confirm the action with the user before executing
