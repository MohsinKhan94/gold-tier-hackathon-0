# Personal AI Employee - Gold Tier

An autonomous AI agent that manages personal affairs and business operations 24/7. Integrates with Gmail, WhatsApp, LinkedIn, and **Odoo ERP** for full-stack business automation using Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Architecture

```
EXTERNAL SOURCES
Gmail | WhatsApp | Files | LinkedIn | Odoo ERP
  |        |        |        |          |
  v        v        v        v          v
PERCEPTION LAYER (Python Watchers)
Gmail Watcher | WhatsApp Watcher | File Watcher | LinkedIn Monitor
  |
  v  Creates .md files
OBSIDIAN VAULT (Local)
  /Inbox/            Raw incoming items
  /Needs_Action/     Items requiring processing
  /Pending_Approval/ Awaiting human sign-off
  /Approved/         Human-approved actions
  /Done/             Completed items
  /Logs/             Structured JSON audit logs
  /Briefings/        CEO Monday briefings
  /Social_Posts/     LinkedIn drafts & posts
  /Quarantine/       Corrupted files (isolated)
  Dashboard.md | Business_Goals.md | Plan.md | SKILLS.md
  |
  v
REASONING LAYER (Claude Code)
  14 Agent Skills (.claude/skills/)
  Ralph Wiggum Stop Hook (autonomous task loop)
  Cross-Domain Orchestrator (event routing)
  |
  v
MCP SERVERS (Action Layer)
  Gmail MCP (4 tools)  |  Odoo MCP (16 tools)
  |                       |
  v                       v
Gmail API           Odoo (localhost:8069)
  |
  v
ORCHESTRATION LAYER
  start_gold.py     Master launcher
  Watchdog          Health monitor, auto-restart
  Retry Handler     Exponential backoff
  Scheduled Tasks   CEO briefing, audit cleanup
```

## Features

### Bronze Tier (Foundation)
- 24/7 File Monitoring with auto-alerting
- Obsidian vault with Dashboard, Plan, Skills
- 7 core Agent Skills (vault-ops, file/email/whatsapp monitoring, plan, dashboard, inbox)

### Silver Tier (Functional Assistant)
- Gmail MCP Server for sending/drafting/searching emails
- LinkedIn posting with approval workflow
- Human-in-the-loop for sensitive actions
- WhatsApp monitoring (mock)
- Plan.md auto-generation loop
- Scheduled task runner

### Gold Tier (Autonomous Employee)
- **Odoo ERP Integration** - 16 MCP tools for invoices, customers, vendors, sales, CRM, accounting
- **Social Media MCP** - 17 tools for Facebook, Instagram, and Twitter/X posting + engagement metrics
- **Cross-Domain Orchestrator** - Routes events across personal/business domains
- **CEO Monday Briefing** - Weekly business report from Odoo + vault data
- **Structured Audit Logging** - JSON logs for every AI action (90-day retention)
- **Error Recovery & Watchdog** - Auto-restart crashed processes, retry with backoff
- **Ralph Wiggum Loop** - Stop hook keeps Claude Code working until task is complete
- **17 Agent Skills** total, **4 MCP Servers**, **37 MCP tools**

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Reasoning Engine | Claude Code (Gemini API) |
| Knowledge Base | Obsidian (local Markdown) |
| ERP System | Odoo Community Edition (Docker) |
| Social APIs | Meta Graph API (Facebook/Instagram), Twitter API v2 |
| MCP Framework | FastMCP (Python, stdio transport) |
| Watchers | Python (watchdog, gmail API, requests) |
| Database | PostgreSQL (Odoo backend, Docker) |
| Package Manager | UV (Python) |

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js v24+ LTS
- Docker Desktop
- Claude Code CLI
- Obsidian

### 1. Clone and Install
```bash
git clone <repo-url>
cd bronze-tier
cd ai-employee-watcher
uv sync
```

### 2. Start Odoo (Docker)
```bash
docker start odoo-db odoo
# Or first time:
# docker run -d --name odoo-db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:15
# docker run -d --name odoo -p 8069:8069 --link odoo-db:db -e HOST=db -e USER=odoo -e PASSWORD=odoo -t odoo:17.0
```
Then open http://localhost:8069 and create database `ai_employee`.

### 3. Configure Environment
Create `.env` in the project root:
```env
GEMINI_API_KEY=your_key
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USER=your_email
ODOO_PASSWORD=your_password
```

### 4. Gmail Setup
Place `credentials.json` from Google Cloud Console in `ai-employee-watcher/`.
Run `python gmail_watcher.py` once to complete OAuth flow.

### 5. Launch Gold Tier
```bash
python ai-employee-watcher/start_gold.py
```

This starts:
- All watcher processes with watchdog monitoring
- Scheduled tasks (CEO briefing, audit cleanup, cross-domain scan)
- Health monitoring with auto-restart

## Agent Skills (14)

| # | Skill | Type | Description |
|---|-------|------|-------------|
| 1 | vault-operations | Bronze | Read, write, list, move vault files |
| 2 | file-monitoring | Bronze | Monitor Watch_This_Folder |
| 3 | email-monitoring | Bronze | Gmail alerts to vault |
| 4 | whatsapp-monitoring | Silver | WhatsApp message alerts |
| 5 | linkedin-posting | Silver | Draft and post to LinkedIn |
| 6 | plan-generator | Silver | Auto-generate Plan.md |
| 7 | dashboard-updater | Silver | Update Dashboard.md stats |
| 8 | human-approval | Silver | Approval workflow |
| 9 | inbox-manager | Silver | Triage inbox items |
| 10 | email-sending | Silver | Send/draft/search via Gmail MCP |
| 11 | odoo-accounting | Gold | Odoo ERP (invoices, CRM, sales) |
| 12 | facebook-posting | Gold | Post to Facebook, engagement metrics |
| 13 | instagram-posting | Gold | Post images/carousels to Instagram |
| 14 | twitter-posting | Gold | Tweet, polls, search, metrics |
| 15 | ceo-briefing | Gold | Weekly CEO business briefing |
| 16 | audit-logger | Gold | Structured JSON audit logs |
| 17 | error-recovery | Gold | Watchdog, retry, health checks |

## MCP Servers

### Gmail MCP (4 tools)
`send_email`, `draft_email`, `search_emails`, `list_recent_emails`

### Odoo MCP (16 tools)
`list_customers`, `create_customer`, `list_vendors`, `create_vendor`, `search_products`, `create_product`, `create_invoice`, `list_invoices`, `get_invoice`, `confirm_invoice`, `create_sale_order`, `list_sale_orders`, `confirm_sale_order`, `get_account_balance`, `list_crm_leads`, `create_crm_lead`

### Social MCP (17 tools)
**Facebook:** `post_to_facebook`, `get_facebook_page_info`, `get_facebook_posts`, `get_facebook_insights`
**Instagram:** `post_to_instagram`, `post_carousel_to_instagram`, `get_instagram_profile`, `get_instagram_media`, `get_instagram_insights`
**Twitter/X:** `post_tweet`, `post_tweet_with_poll`, `delete_tweet`, `get_twitter_user_info`, `get_tweet_metrics`, `search_recent_tweets`
**Cross-platform:** `get_social_engagement_summary`

## Security Measures

- **Local-first**: All data stored locally in Obsidian vault
- **Human-in-the-loop**: Payments, social posts, and sensitive emails require approval
- **Never auto-retry payments**: Failed payment actions are queued for manual review
- **Audit trail**: Every action logged in structured JSON
- **File quarantine**: Corrupted files isolated instead of crashing the system
- **Credential safety**: API keys in `.env` (gitignored), OAuth tokens in pickle files

## Lessons Learned

1. **Odoo JSON-RPC quirk**: The `search_read` method requires domain as `[domain]` (list wrapping), not just `domain` directly
2. **FastMCP stdio**: MCP servers communicate over stdin/stdout - never print debug output in MCP server files
3. **Watchdog vs watcher**: Don't confuse the `watchdog` Python library (file system events) with the watchdog monitor (process health)
4. **Ralph Wiggum safety valve**: Always have a max iteration limit to prevent infinite loops
5. **Cross-domain routing**: Simple keyword matching is effective enough for event classification - no LLM needed for routing
6. **Docker networking**: Odoo needs its PostgreSQL container linked - start `odoo-db` before `odoo`

## Project Structure

```
bronze-tier/
├── .claude/
│   ├── settings.local.json          # MCP servers + hooks config
│   └── skills/                      # 14 Agent Skills
│       ├── vault-operations/
│       ├── file-monitoring/
│       ├── email-monitoring/
│       ├── whatsapp-monitoring/
│       ├── linkedin-posting/
│       ├── plan-generator/
│       ├── dashboard-updater/
│       ├── human-approval/
│       ├── inbox-manager/
│       ├── email-sending/
│       ├── odoo-accounting/         # Gold
│       ├── facebook-posting/        # Gold
│       ├── instagram-posting/       # Gold
│       ├── twitter-posting/         # Gold
│       ├── ceo-briefing/            # Gold
│       ├── audit-logger/            # Gold
│       └── error-recovery/          # Gold
├── AI_Employee_Vault/               # Obsidian vault
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Done/
│   ├── Logs/                        # JSON audit logs
│   ├── Briefings/                   # CEO briefings
│   ├── Social_Posts/
│   ├── Quarantine/
│   ├── Dashboard.md
│   ├── Business_Goals.md
│   ├── Plan.md
│   └── SKILLS.md
├── ai-employee-watcher/             # All Python scripts
│   ├── gmail_mcp_server.py
│   ├── odoo_mcp_server.py           # Gold
│   ├── social_mcp_server.py         # Gold (Facebook/Instagram/Twitter)
│   ├── audit_logger.py              # Gold
│   ├── retry_handler.py             # Gold
│   ├── watchdog_monitor.py          # Gold
│   ├── orchestrator.py              # Gold
│   ├── ceo_briefing.py              # Gold
│   ├── ralph_wiggum.py              # Gold
│   ├── start_gold.py                # Gold
│   ├── start_silver.py
│   ├── scheduled_task.py
│   ├── skills.py
│   └── ... (watchers, posters)
├── .env                             # API keys (gitignored)
├── gold-tier.md                     # Gold tier requirements
├── hackathon.txt                    # Hackathon spec
└── README.md                        # This file
```
