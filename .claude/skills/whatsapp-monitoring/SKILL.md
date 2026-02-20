---
name: whatsapp-monitoring
description: Monitor WhatsApp messages via webhook or mock simulation and create alerts in the vault. Use this for processing WhatsApp notifications or checking message status.
user-invocable: true
allowed-tools: Read, Write, Glob, Bash(python *)
---

# WhatsApp Monitoring Skill

Monitor WhatsApp messages and create structured alerts in the Obsidian vault.

## Two Modes

### Mode 1: Mock Watcher (Demo/Testing)
Simulates incoming WhatsApp and LinkedIn messages for testing.
```bash
cd ai-employee-watcher && python mock_watcher.py
```

### Mode 2: Real WhatsApp via Twilio Webhook
Receives real WhatsApp messages via Twilio's WhatsApp Sandbox.
```bash
cd ai-employee-watcher && python whatsapp_server.py
```
Requires: Twilio account, ngrok for tunneling, Flask.

## Alert Format
```markdown
# WhatsApp Message
**Priority:** high/normal/low

## Details
**From:** Sender Name
**Received:** YYYY-MM-DD HH:MM:SS

## Message
Message content here

## Actions
- [ ] Reply
- [ ] Ignore
- [ ] Archive
```

## Processing WhatsApp Alerts
1. Read alerts from `AI_Employee_Vault/Inbox/WH_*.md`
2. Determine priority and required action
3. If reply needed, draft response
4. Move to `Done/` when processed

## Priority Keywords
These keywords in messages trigger high priority:
- "urgent", "asap", "help", "payment", "invoice"
