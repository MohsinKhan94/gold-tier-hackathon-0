---
name: email-monitoring
description: Monitor Gmail inbox for new emails, analyze their priority and category, and create structured alerts in the vault. Use this when checking emails or processing email notifications.
user-invocable: true
allowed-tools: Read, Write, Glob, Bash(python *)
---

# Email Monitoring Skill

Monitor Gmail for new unread emails and create intelligent alerts in the Obsidian vault.

## How It Works
1. `gmail_watcher.py` authenticates with Gmail API using OAuth2
2. Polls for unread emails every 60 seconds
3. For each new email, analyzes priority and category
4. Creates a structured markdown alert in `AI_Employee_Vault/Inbox/`

## To Start Gmail Watcher
```bash
cd ai-employee-watcher && python gmail_watcher.py
```

## Prerequisites
- `credentials.json` from Google Cloud Console in `ai-employee-watcher/`
- Gmail API enabled in Google Cloud project
- First run will open browser for OAuth consent

## Email Alert Format
```markdown
# [Category] - Subject Line
**Priority:** High/Medium/Low

## Email Details
**From:** sender@example.com
**Subject:** Subject line
**Received:** YYYY-MM-DD HH:MM:SS

## AI Analysis
**Summary:** One sentence summary
**Suggested Action:** What to do

## Actions
- [ ] Suggested action
- [ ] Reply if needed
- [ ] Archive or Delete
```

## Email Categories
- **VIP**: From important contacts
- **Action Required**: Needs response/action
- **Newsletter**: Informational subscriptions
- **Spam**: Unwanted messages
- **Info**: General information

## Processing Emails
1. Read alerts from `AI_Employee_Vault/Inbox/Email_*.md`
2. Take suggested action or override
3. Move to `Done/` when processed
