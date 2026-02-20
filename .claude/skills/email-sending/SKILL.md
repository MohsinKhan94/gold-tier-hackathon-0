---
name: email-sending
description: Send, draft, and search emails using the Gmail MCP server. Supports human-in-the-loop approval for sensitive sends.
user-invocable: true
allowed-tools:
  - mcp: gmail
  - Read
  - Write
  - Edit
  - Glob
  - Bash(mv *)
  - Bash(ls *)
---

# Email Sending Skill (MCP)

Send, draft, and search emails using the Gmail MCP server.

## Available MCP Tools

The `gmail` MCP server provides these tools:

### `send_email`
Send an email via Gmail.
- **to** (required): Recipient email address
- **subject** (required): Email subject line
- **body** (required): Email body (plain text)
- **cc** (optional): CC recipients, comma-separated
- **bcc** (optional): BCC recipients, comma-separated

### `draft_email`
Create an email draft in Gmail (does not send).
- **to** (required): Recipient email address
- **subject** (required): Email subject line
- **body** (required): Email body (plain text)

### `search_emails`
Search Gmail with a query string.
- **query** (required): Gmail search query (e.g. `from:boss@company.com is:unread`)
- **max_results** (optional): Max results, default 5

### `list_recent_emails`
List recent unread emails.
- **max_results** (optional): Max results, default 10

## Human-in-the-Loop Workflow

For sending emails (not drafts or searches), follow the approval workflow:

1. **Create approval request** in `AI_Employee_Vault/Pending_Approval/`:
   ```markdown
   # Email Send Request
   **Action:** send_email
   **To:** recipient@example.com
   **Subject:** Subject line
   **Body Preview:** First 200 chars...
   **Status:** PENDING APPROVAL

   Move this file to Approved/ to send.
   ```

2. **Wait for human approval** - user moves file to `Approved/`
3. **Execute send** using the `send_email` MCP tool
4. **Log and archive** - move approval file to `Done/`

## When to Use

- User asks to send or reply to an email
- User asks to draft an email for review
- User asks to search or find specific emails
- Processing an approved email send action from the approval workflow

## Safety Rules

- Always use `draft_email` first if unsure about content
- Never send emails without user confirmation for new/unknown recipients
- Log all send actions to `AI_Employee_Vault/Logs/`
- For bulk sends, always create approval requests first
