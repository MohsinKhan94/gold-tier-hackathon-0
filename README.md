# Personal AI Employee - Gold Tier

> **Panaversity Hackathon 0** | An autonomous AI agent that manages personal affairs and business operations 24/7 using Claude Code as the reasoning engine and Obsidian as the management dashboard.

**17 Agent Skills** | **4 MCP Servers** | **37 MCP Tools** | **Odoo ERP** | **Facebook + Instagram + Twitter** | **CEO Briefings** | **Audit Logging** | **Error Recovery**

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                       │
│  Gmail  │ WhatsApp │ Files │ LinkedIn │ Odoo ERP         │
│  Facebook │ Instagram │ Twitter/X                        │
└────┬─────────┬────────┬───────┬──────────┬───────────────┘
     │         │        │       │          │
     v         v        v       v          v
┌──────────────────────────────────────────────────────────┐
│              PERCEPTION LAYER (Python Watchers)           │
│  Gmail Watcher │ WhatsApp Watcher │ File Watcher         │
│  Creates .md files in Obsidian Vault                     │
└──────────────────────┬───────────────────────────────────┘
                       │
                       v
┌──────────────────────────────────────────────────────────┐
│              OBSIDIAN VAULT (Knowledge Base)              │
│  Inbox/ → Needs_Action/ → Pending_Approval/ → Done/     │
│  Dashboard.md │ Plan.md │ Business_Goals.md │ SKILLS.md  │
│  Logs/ (JSON audit) │ Briefings/ │ Social_Posts/         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       v
┌──────────────────────────────────────────────────────────┐
│              REASONING LAYER (Claude Code)                │
│  17 Agent Skills (.claude/skills/)                       │
│  Ralph Wiggum Stop Hook (autonomous task loop)           │
│  Cross-Domain Orchestrator (event routing)               │
└──────────────────────┬───────────────────────────────────┘
                       │
                       v
┌──────────────────────────────────────────────────────────┐
│              ACTION LAYER (4 MCP Servers, 37 Tools)      │
│  Gmail MCP (4)  │ Odoo MCP (16) │ Social MCP (16)       │
│  GitHub MCP (npx)                                        │
└──────┬──────────────┬──────────────────┬─────────────────┘
       │              │                  │
       v              v                  v
   Gmail API    Odoo ERP (Docker)   Meta Graph API
                localhost:8069      Twitter API v2
```

```
┌──────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                          │
│  start_gold.py    → Master launcher                      │
│  watchdog_monitor → Health monitor, auto-restart          │
│  retry_handler    → Exponential backoff, retry queue      │
│  orchestrator     → Cross-domain event routing            │
│  ralph_wiggum     → Stop hook (loop until task complete)  │
│  ceo_briefing     → Weekly CEO briefing generator         │
│  audit_logger     → Structured JSON logging (90-day)      │
└──────────────────────────────────────────────────────────┘
```

---

## Gold Tier Requirements Checklist

All **11 Gold Tier requirements** from the Panaversity Hackathon 0 spec are implemented:

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Full Cross-Domain Integration | Done | `orchestrator.py` routes events across personal/business domains |
| 2 | Odoo ERP Integration via MCP | Done | `odoo_mcp_server.py` with 16 JSON-RPC tools |
| 3 | Facebook & Instagram Integration | Done | `social_mcp_server.py` via Meta Graph API |
| 4 | Twitter/X Integration | Done | `social_mcp_server.py` via Twitter API v2 |
| 5 | Multiple MCP Servers | Done | 4 MCP servers (Gmail, Odoo, Social, GitHub) |
| 6 | Weekly CEO Briefing | Done | `ceo_briefing.py` → `Briefings/` folder |
| 7 | Error Recovery & Graceful Degradation | Done | `watchdog_monitor.py` + `retry_handler.py` |
| 8 | Comprehensive Audit Logging | Done | `audit_logger.py` → JSON logs with 90-day retention |
| 9 | Ralph Wiggum Loop | Done | `ralph_wiggum.py` stop hook (max 10 iterations) |
| 10 | Documentation | Done | This README + `CLAUDE.md` + `SKILLS.md` |
| 11 | All Features as Agent Skills | Done | 17 skills in `.claude/skills/` |

---

## Features by Tier

### Bronze Tier (Foundation)
- 24/7 File Monitoring with auto-alerting
- Obsidian vault with Dashboard, Plan, Skills
- 7 core Agent Skills (vault-ops, file/email/whatsapp monitoring, plan, dashboard, inbox)

### Silver Tier (Functional Assistant)
- Gmail MCP Server for sending/drafting/searching emails
- LinkedIn posting with approval workflow
- Human-in-the-loop for sensitive actions (payments, social posts, emails)
- WhatsApp monitoring
- Plan.md auto-generation loop
- Scheduled task runner

### Gold Tier (Autonomous Employee)
- **Odoo ERP Integration** — 16 MCP tools for invoices, customers, vendors, sales orders, CRM leads, accounting
- **Social Media MCP** — 16 tools for Facebook, Instagram, and Twitter/X posting + engagement metrics
- **Cross-Domain Orchestrator** — Routes events across personal/business domains automatically
- **CEO Monday Briefing** — Weekly business report from Odoo financials + vault tasks + social metrics
- **Structured Audit Logging** — JSON logs for every AI action with 90-day retention
- **Error Recovery & Watchdog** — Auto-restart crashed processes, exponential backoff retry, never auto-retry payments
- **Ralph Wiggum Loop** — Stop hook keeps Claude Code working until task moves to Done/

---

## Agent Skills (17)

| # | Skill | Tier | Description |
|---|-------|------|-------------|
| 1 | `vault-operations` | Bronze | Read, write, list, move vault files |
| 2 | `file-monitoring` | Bronze | Monitor Watch_This_Folder for new files |
| 3 | `email-monitoring` | Bronze | Gmail alerts to vault |
| 4 | `whatsapp-monitoring` | Silver | WhatsApp message alerts |
| 5 | `linkedin-posting` | Silver | Draft and post to LinkedIn |
| 6 | `plan-generator` | Silver | Auto-generate Plan.md from inbox |
| 7 | `dashboard-updater` | Silver | Update Dashboard.md live stats |
| 8 | `human-approval` | Silver | Approval workflow for sensitive actions |
| 9 | `inbox-manager` | Silver | Triage and process inbox items |
| 10 | `email-sending` | Silver | Send/draft/search via Gmail MCP |
| 11 | `odoo-accounting` | Gold | Odoo ERP — invoices, CRM, sales, accounting |
| 12 | `facebook-posting` | Gold | Post to Facebook, engagement metrics, page insights |
| 13 | `instagram-posting` | Gold | Post images/carousels, engagement metrics |
| 14 | `twitter-posting` | Gold | Tweets, polls, search, engagement metrics |
| 15 | `ceo-briefing` | Gold | Weekly CEO business briefing from Odoo + vault |
| 16 | `audit-logger` | Gold | Structured JSON audit log viewer |
| 17 | `error-recovery` | Gold | Watchdog, retry queue, health checks |

---

## MCP Servers (4 Servers, 37 Tools)

### Gmail MCP — 4 tools
`send_email` · `draft_email` · `search_emails` · `list_recent_emails`

### Odoo MCP — 16 tools
| Category | Tools |
|----------|-------|
| Customers | `list_customers`, `create_customer` |
| Vendors | `list_vendors`, `create_vendor` |
| Products | `search_products`, `create_product` |
| Invoices | `create_invoice`, `list_invoices`, `get_invoice`, `confirm_invoice` |
| Sale Orders | `create_sale_order`, `list_sale_orders`, `confirm_sale_order` |
| Accounting | `get_account_balance` |
| CRM | `list_crm_leads`, `create_crm_lead` |

### Social MCP — 16 tools
| Platform | Tools |
|----------|-------|
| Facebook | `post_to_facebook`, `get_facebook_page_info`, `get_facebook_posts`, `get_facebook_insights` |
| Instagram | `post_to_instagram`, `post_carousel_to_instagram`, `get_instagram_profile`, `get_instagram_media`, `get_instagram_insights` |
| Twitter/X | `post_tweet`, `post_tweet_with_poll`, `delete_tweet`, `get_twitter_user_info`, `get_tweet_metrics`, `search_recent_tweets` |
| Cross-platform | `get_social_engagement_summary` |

### GitHub MCP
`npx @modelcontextprotocol/server-github` — GitHub operations

---

## Gold Tier Infrastructure

| Script | Purpose |
|--------|---------|
| `start_gold.py` | Master launcher — starts all services with watchdog + scheduled tasks |
| `orchestrator.py` | Cross-domain event routing — classifies inbox items as business/personal/social |
| `odoo_mcp_server.py` | Odoo ERP MCP — 16 tools via JSON-RPC to localhost:8069 |
| `social_mcp_server.py` | Social Media MCP — Facebook (Meta Graph API), Instagram, Twitter (API v2) |
| `ceo_briefing.py` | Weekly CEO briefing from Odoo financials + vault tasks → `Briefings/` |
| `audit_logger.py` | Structured JSON logging → `Logs/YYYY-MM-DD.json` (90-day retention) |
| `retry_handler.py` | Exponential backoff retry, failed action queue, **never auto-retries payments** |
| `watchdog_monitor.py` | Process health monitor, auto-restart crashed watchers (max 5 attempts) |
| `ralph_wiggum.py` | Stop hook — loops Claude until task moves to `Done/` (max 10 iterations) |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Reasoning Engine | Claude Code |
| Knowledge Base | Obsidian (local Markdown vault) |
| ERP System | Odoo Community Edition (Docker) |
| Email | Gmail API (OAuth 2.0) |
| Social Media | Meta Graph API (Facebook/Instagram), Twitter API v2 |
| MCP Framework | FastMCP (Python, stdio transport) |
| Watchers | Python (watchdog, gmail API, requests) |
| Database | PostgreSQL (Odoo backend, Docker) |
| Package Manager | UV (Python) |

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js v24+ LTS
- Docker Desktop
- Claude Code CLI
- Obsidian

### 1. Clone and Install
```bash
git clone https://github.com/MohsinKhan94/gold-tier-hackathon-0.git
cd gold-tier-hackathon-0
cd ai-employee-watcher
uv sync
```

### 2. Start Odoo (Docker)
```bash
# First time setup:
docker run -d --name odoo-db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:15
docker run -d --name odoo -p 8069:8069 --link odoo-db:db -e HOST=db -e USER=odoo -e PASSWORD=odoo -t odoo:17.0

# Subsequent starts:
docker start odoo-db odoo
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
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_BUSINESS_ID=your_business_id
TWITTER_API_KEY=your_key
TWITTER_API_KEY_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 4. Gmail Setup
Place `credentials.json` from Google Cloud Console in `ai-employee-watcher/`.
Run `python gmail_watcher.py` once to complete the OAuth flow.

### 5. Configure Claude Code MCP Servers
Update `.claude/settings.local.json` with your GitHub PAT:
```json
{
  "mcpServers": {
    "gmail": { "command": "python", "args": ["ai-employee-watcher/gmail_mcp_server.py"] },
    "odoo": { "command": "python", "args": ["ai-employee-watcher/odoo_mcp_server.py"] },
    "social": { "command": "python", "args": ["ai-employee-watcher/social_mcp_server.py"] },
    "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_PAT" } }
  }
}
```

### 6. Launch Gold Tier
```bash
python ai-employee-watcher/start_gold.py
```
This starts all watcher processes with watchdog monitoring, scheduled tasks (CEO briefing, audit cleanup, cross-domain scan), and health monitoring with auto-restart.

---

## Vault Folder Structure

```
AI_Employee_Vault/
├── Inbox/              → Raw incoming items (emails, WhatsApp, files)
├── Needs_Action/       → Items requiring processing
├── Pending_Approval/   → Awaiting human sign-off
├── Approved/           → Human-approved actions ready to execute
├── Done/               → Completed items
├── Logs/               → Markdown logs + JSON audit logs (90-day retention)
├── Briefings/          → CEO Monday briefings
├── Social_Posts/       → LinkedIn/social media drafts
├── Quarantine/         → Corrupted files isolated here
├── Dashboard.md        → Live status dashboard
├── Plan.md             → Auto-generated daily plan
├── Business_Goals.md   → Revenue targets and KPIs
└── SKILLS.md           → Full skills documentation
```

---

## Project Structure

```
gold-tier-hackathon-0/
├── .claude/
│   ├── settings.local.json              # MCP servers + hooks config
│   └── skills/                          # 17 Agent Skills
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
│       ├── odoo-accounting/             # Gold
│       ├── facebook-posting/            # Gold
│       ├── instagram-posting/           # Gold
│       ├── twitter-posting/             # Gold
│       ├── ceo-briefing/                # Gold
│       ├── audit-logger/                # Gold
│       └── error-recovery/              # Gold
├── AI_Employee_Vault/                   # Obsidian vault
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Done/
│   ├── Logs/                            # JSON audit logs
│   ├── Briefings/                       # CEO briefings
│   ├── Social_Posts/
│   ├── Quarantine/
│   ├── Dashboard.md
│   ├── Business_Goals.md
│   ├── Plan.md
│   └── SKILLS.md
├── ai-employee-watcher/                 # All Python scripts
│   ├── gmail_mcp_server.py              # Gmail MCP Server
│   ├── odoo_mcp_server.py               # Odoo MCP Server (Gold)
│   ├── social_mcp_server.py             # Social MCP Server (Gold)
│   ├── audit_logger.py                  # Structured JSON logging (Gold)
│   ├── retry_handler.py                 # Exponential backoff retry (Gold)
│   ├── watchdog_monitor.py              # Process health monitor (Gold)
│   ├── orchestrator.py                  # Cross-domain routing (Gold)
│   ├── ceo_briefing.py                  # CEO Weekly Briefing (Gold)
│   ├── ralph_wiggum.py                  # Stop Hook loop (Gold)
│   ├── start_gold.py                    # Master launcher (Gold)
│   ├── start_silver.py                  # Silver Tier launcher
│   ├── scheduled_task.py                # Periodic task runner
│   ├── skills.py                        # Python skill functions
│   ├── file_watcher.py                  # File system watcher
│   ├── gmail_watcher.py                 # Gmail watcher
│   ├── mock_watcher.py                  # WhatsApp/LinkedIn mock
│   └── linkedin_poster.py              # LinkedIn poster
├── CLAUDE.md                            # Project instructions for Claude Code
├── .env                                 # API keys (gitignored)
├── .gitignore
├── gold-tier.md                         # Gold tier requirements reference
└── README.md                            # This file
```

---

## Security Measures

- **Local-first**: All data stored locally in Obsidian vault — no cloud dependencies for core data
- **Human-in-the-loop**: Payments, social posts, and sensitive emails require explicit approval via `Pending_Approval/` → `Approved/` workflow
- **Never auto-retry payments**: Failed payment actions are queued for manual review, never retried automatically
- **Audit trail**: Every action logged in structured JSON with 90-day retention
- **File quarantine**: Corrupted files isolated in `Quarantine/` instead of crashing the system
- **Credential safety**: API keys in `.env` (gitignored), OAuth tokens excluded from version control

---

## Lessons Learned

1. **Odoo JSON-RPC quirk**: The `search_read` method requires domain as `[domain]` (list wrapping), not just `domain` directly
2. **FastMCP stdio**: MCP servers communicate over stdin/stdout — never print debug output in MCP server files
3. **Watchdog vs watcher**: Don't confuse the `watchdog` Python library (file system events) with the watchdog monitor (process health)
4. **Ralph Wiggum safety valve**: Always have a max iteration limit to prevent infinite loops
5. **Cross-domain routing**: Simple keyword matching is effective enough for event classification — no LLM needed for routing
6. **Docker networking**: Odoo needs its PostgreSQL container linked — start `odoo-db` before `odoo`
7. **GitHub push protection**: Never commit API tokens or credentials — use `.env` and `.gitignore`
8. **MCP server pattern**: `FastMCP` + `@mcp.tool()` decorator + `stdio` transport is the standard pattern for all servers

---

## Hackathon Context

This project was built for the **Panaversity Hackathon 0** — building autonomous Digital FTEs (Full-Time Equivalents) using Claude Code and Obsidian. The system implements a complete Gold Tier AI Employee that can autonomously manage personal affairs, business operations, social media presence, and ERP accounting.

**Built with Claude Code** — the AI reasoning engine that powers all 17 agent skills and coordinates across 4 MCP servers.
