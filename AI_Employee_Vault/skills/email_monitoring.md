# Agent Skill: Email Monitoring

## Status
🟡 Planned (Gmail API integration pending)

## Description
Monitor Gmail inbox and create Obsidian notes for new emails

## Capabilities
- Authenticate with Gmail API
- Fetch unread emails
- Parse email metadata (from, subject, date)
- Write structured notes to Inbox folder

## Implementation
**File:** `ai-employee-watcher/gmail_watcher.py` (future)

## Current Alternative
Using file system monitoring as Bronze Tier requirement

## Trigger
Runs every 60 seconds via Python watcher script

## Input
None (autonomous monitoring)

## Output
Markdown file in `/Inbox` folder with email details

## Dependencies
- Google Gmail API
- Python `google-api-python-client`
- OAuth2 credentials

## Usage Example
```python
# Future implementation
from gmail_watcher import monitor_gmail
monitor_gmail()
```