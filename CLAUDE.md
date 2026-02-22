# Personal AI Employee - Gold Tier

This is a **Gold Tier AI Employee** project for the Panaversity Hackathon 0. It is an autonomous AI agent that manages personal affairs and business operations 24/7 using Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Project Owner
- **Email:** sherankhan666@gmail.com
- **Odoo:** localhost:8069 (database: ai_employee, Docker containers: odoo + odoo-db)

## Architecture Overview

```
External Sources (Gmail, WhatsApp, Files, LinkedIn, Odoo, Facebook, Instagram, Twitter)
    |
    v
Perception Layer (Python Watchers in ai-employee-watcher/)
    |
    v  Creates .md files
Obsidian Vault (AI_Employee_Vault/)
    |
    v
Reasoning Layer (Claude Code + 17 Agent Skills + Ralph Wiggum Loop)
    |
    v
MCP Servers (gmail, odoo, social) -> External APIs
```

## Key Directories

- `ai-employee-watcher/` - All Python scripts (watchers, MCP servers, orchestration)
- `AI_Employee_Vault/` - Obsidian vault (Inbox, Done, Logs, Briefings, Social_Posts, etc.)
- `.claude/skills/` - 17 Agent Skills (SKILL.md files)
- `.claude/settings.local.json` - MCP servers config + Ralph Wiggum stop hook

## MCP Servers (4 servers, 36 tools)

| Server | File | Tools |
|--------|------|-------|
| gmail | `ai-employee-watcher/gmail_mcp_server.py` | 4 tools: send_email, draft_email, search_emails, list_recent_emails |
| odoo | `ai-employee-watcher/odoo_mcp_server.py` | 16 tools: customers, vendors, products, invoices, sale orders, CRM leads, account balance |
| social | `ai-employee-watcher/social_mcp_server.py` | 16 tools: Facebook posting/insights, Instagram image/carousel posting, Twitter tweets/polls/search |
| github | npx @modelcontextprotocol/server-github | GitHub operations |

All MCP servers use `mcp.server.fastmcp.FastMCP` with `@mcp.tool()` decorators and `stdio` transport.

## Agent Skills (17 total)

**Bronze/Silver (10):** vault-operations, file-monitoring, email-monitoring, whatsapp-monitoring, linkedin-posting, plan-generator, dashboard-updater, human-approval, inbox-manager, email-sending

**Gold (7):** odoo-accounting, facebook-posting, instagram-posting, twitter-posting, ceo-briefing, audit-logger, error-recovery

## Gold Tier Infrastructure Scripts

| Script | Purpose |
|--------|---------|
| `odoo_mcp_server.py` | Odoo ERP via JSON-RPC (invoices, CRM, sales, accounting) |
| `social_mcp_server.py` | Facebook (Meta Graph API), Instagram, Twitter (API v2) |
| `audit_logger.py` | Structured JSON logging -> Logs/YYYY-MM-DD.json (90-day retention) |
| `retry_handler.py` | Exponential backoff retry, failed action queue, NEVER auto-retries payments |
| `watchdog_monitor.py` | Process health monitor, auto-restart crashed watchers (max 5 attempts) |
| `orchestrator.py` | Cross-domain event routing (classifies inbox items as business/personal/social) |
| `ceo_briefing.py` | Weekly CEO briefing from Odoo financials + vault tasks -> Briefings/ |
| `ralph_wiggum.py` | Stop hook - loops Claude until task moves to Done/ (max 10 iterations) |
| `start_gold.py` | Master launcher with watchdog + scheduled tasks |

## Vault Folder Structure

```
AI_Employee_Vault/
  Inbox/             - Raw incoming items (emails, WhatsApp, files)
  Needs_Action/      - Items requiring processing
  Pending_Approval/  - Awaiting human sign-off
  Approved/          - Human-approved actions ready to execute
  Done/              - Completed items
  Logs/              - Markdown logs + JSON audit logs
  Briefings/         - CEO Monday briefings
  Social_Posts/      - LinkedIn/social media drafts
  Quarantine/        - Corrupted files isolated here
  Dashboard.md       - Live status dashboard
  Plan.md            - Auto-generated daily plan
  Business_Goals.md  - Revenue targets and KPIs
  SKILLS.md          - Full skills documentation
  Company_Handbook.md - Rules of engagement
```

## Environment Variables (.env)

```
GEMINI_API_KEY, ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD,
FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID, INSTAGRAM_BUSINESS_ID,
TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_BEARER_TOKEN,
TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
```

## Important Conventions

- **MCP Server Pattern:** Use `FastMCP` from `mcp.server.fastmcp`, `@mcp.tool()` decorator, return JSON strings, `mcp.run(transport="stdio")`
- **Skill Pattern:** `.claude/skills/<name>/SKILL.md` with YAML frontmatter (name, description, user-invocable, allowed-tools)
- **Logging:** All actions logged to `AI_Employee_Vault/Logs/` (markdown for human review + JSON for audit)
- **Human-in-the-loop:** Sensitive actions (payments, social posts, emails) go through Pending_Approval/ -> Approved/ workflow
- **Error Handling:** Every MCP tool wraps in try/except and returns `{"status": "error", "error": "message"}` on failure
- **Odoo JSON-RPC:** Domain must be wrapped as `[domain]` in search_read calls. Connection at localhost:8069/jsonrpc.

## How to Start

1. Start Odoo: `docker start odoo-db odoo`
2. Launch all services: `python ai-employee-watcher/start_gold.py`
3. Or use individual MCP tools via Claude Code directly

## Hackathon Context

This project follows the Panaversity Hackathon 0 spec (`hackathon.txt`). Gold Tier requirements are in `gold-tier.md`. The system implements all 11 Gold Tier requirements: Odoo ERP, Facebook/Instagram/Twitter, multiple MCP servers, CEO briefing, error recovery, audit logging, Ralph Wiggum loop, documentation, and all features as Agent Skills.
