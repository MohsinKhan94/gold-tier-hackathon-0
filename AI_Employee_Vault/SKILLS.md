# Agent Skills - Personal AI Employee (Gold Tier)

This document defines all available skills that Claude Code can use to manage this Obsidian vault.
All AI functionality is implemented as **Claude Code Agent Skills** in `.claude/skills/`.

## Agent Skills (.claude/skills/)

### Bronze + Silver Skills (10)
| Skill | Description | Invocation |
|-------|------------|------------|
| vault-operations | Read, write, list, move vault files | `/vault-operations` |
| file-monitoring | Monitor Watch_This_Folder for new files | `/file-monitoring` |
| email-monitoring | Monitor Gmail and create email alerts | `/email-monitoring` |
| whatsapp-monitoring | Monitor WhatsApp messages | `/whatsapp-monitoring` |
| linkedin-posting | Draft, approve, and post to LinkedIn | `/linkedin-posting` |
| plan-generator | Generate Plan.md from inbox items | `/plan-generator` |
| dashboard-updater | Update Dashboard.md with live stats | `/dashboard-updater` |
| human-approval | Approval workflow for sensitive actions | `/human-approval` |
| inbox-manager | Triage and process inbox items | `/inbox-manager` |
| email-sending | Send, draft, search emails via Gmail MCP | `/email-sending` |

### Gold Skills (7)
| Skill | Description | Invocation |
|-------|------------|------------|
| odoo-accounting | Manage Odoo ERP - invoices, customers, vendors, sales, CRM | `/odoo-accounting` |
| facebook-posting | Post to Facebook, view engagement, get page insights | `/facebook-posting` |
| instagram-posting | Post images/carousels to Instagram, view engagement | `/instagram-posting` |
| twitter-posting | Post tweets, create polls, search, get metrics | `/twitter-posting` |
| ceo-briefing | Generate Monday Morning CEO Briefing from Odoo + vault data | `/ceo-briefing` |
| audit-logger | View/manage structured JSON audit logs | `/audit-logger` |
| error-recovery | Monitor system health, watchdog, retry queue | `/error-recovery` |

**Total: 17 Agent Skills**

## MCP Servers

| Server | Transport | Tools | File |
|--------|-----------|-------|------|
| gmail | stdio | 4 tools (email send/draft/search) | `gmail_mcp_server.py` |
| odoo | stdio | 16 tools (ERP operations) | `odoo_mcp_server.py` |
| social | stdio | 17 tools (Facebook/Instagram/Twitter) | `social_mcp_server.py` |

**Configuration:** `.claude/settings.local.json`

### Gmail MCP Tools (4)
- **send_email(to, subject, body, cc?, bcc?)** - Send an email
- **draft_email(to, subject, body)** - Create a draft
- **search_emails(query, max_results?)** - Search emails
- **list_recent_emails(max_results?)** - List recent unread

### Odoo MCP Tools (16)
**Customers:**
- **list_customers(limit?)** - List customers
- **create_customer(name, email?, phone?, street?, city?, country?)** - Create customer

**Vendors:**
- **list_vendors(limit?)** - List vendors
- **create_vendor(name, email?, phone?)** - Create vendor

**Products:**
- **search_products(name?, limit?)** - Search products
- **create_product(name, price?, product_type?)** - Create product

**Invoices:**
- **create_invoice(customer_name, product_name, quantity?, price_unit?)** - Create invoice
- **list_invoices(state?, limit?)** - List invoices
- **get_invoice(invoice_id)** - Get invoice details
- **confirm_invoice(invoice_id)** - Post a draft invoice

**Sale Orders:**
- **create_sale_order(customer_name, product_name, quantity?, price_unit?)** - Create sale order
- **list_sale_orders(limit?)** - List sale orders
- **confirm_sale_order(order_id)** - Confirm quotation

**Accounting:**
- **get_account_balance()** - Financial summary (receivable, payable, revenue, expenses)

**CRM:**
- **list_crm_leads(limit?)** - List CRM leads
- **create_crm_lead(name, customer_name?, email?, phone?, expected_revenue?)** - Create lead

### Social MCP Tools (17)
**Facebook (4):**
- **post_to_facebook(message, link?)** - Post to Facebook Page
- **get_facebook_page_info()** - Get page info and followers
- **get_facebook_posts(limit?)** - Get posts with engagement
- **get_facebook_insights(period?, metric?)** - Get page analytics

**Instagram (5):**
- **post_to_instagram(image_url, caption?)** - Post image to Instagram
- **post_carousel_to_instagram(image_urls, caption?)** - Post carousel (2-10 images)
- **get_instagram_profile()** - Get profile info and followers
- **get_instagram_media(limit?)** - Get posts with engagement
- **get_instagram_insights(media_id)** - Get post insights

**Twitter/X (6):**
- **post_tweet(text)** - Post a tweet (280 char max)
- **post_tweet_with_poll(text, options, duration_minutes?)** - Tweet with poll
- **delete_tweet(tweet_id)** - Delete a tweet
- **get_twitter_user_info()** - Get profile info
- **get_tweet_metrics(tweet_id)** - Get tweet engagement
- **search_recent_tweets(query, limit?)** - Search recent tweets

**Cross-Platform (1):**
- **get_social_engagement_summary()** - Combined engagement across all platforms

All social actions are logged to `AI_Employee_Vault/Logs/social_actions_*.md`.

## Gold Tier Infrastructure

### Cross-Domain Orchestrator (`orchestrator.py`)
Routes events across personal/business domains. Classifies inbox items and enriches with Odoo data.

### Watchdog Monitor (`watchdog_monitor.py`)
Monitors all watcher processes, auto-restarts crashed ones (max 5 retries), health logging.

### Retry Handler (`retry_handler.py`)
Exponential backoff retry for API calls. Queues failed actions. **Never auto-retries payments.**

### CEO Briefing (`ceo_briefing.py`)
Weekly briefing pulling from Odoo, Done/ tasks, audit logs, and Business_Goals.md.

### Audit Logger (`audit_logger.py`)
Structured JSON logging for every action. 90-day retention. Stored in Logs/YYYY-MM-DD.json.

### Ralph Wiggum Stop Hook (`ralph_wiggum.py`)
Keeps Claude Code running until task is complete. Max 10 iterations safety valve.

### Master Launcher (`start_gold.py`)
Launches all Gold Tier services with watchdog, scheduled tasks (CEO briefing, audit cleanup, cross-domain scan).

## Python Skill Functions (ai-employee-watcher/skills.py)

1. **read_vault_file(filepath)** - Read any vault file
2. **write_vault_file(filepath, content)** - Write to vault
3. **list_vault_folder(folder)** - List folder contents
4. **get_inbox_summary()** - Inbox statistics
5. **move_vault_file(filename, from, to)** - Move between folders
6. **create_inbox_item(title, content, priority)** - Create inbox task
7. **update_dashboard_stats()** - Update dashboard counts
8. **generate_plan()** - Generate Plan.md
9. **create_approval_request(action, description, details)** - Request approval
10. **check_approved_actions()** - List approved actions
11. **process_approved_action(filename)** - Execute approved action

## How Claude Code Uses These Skills

- "Show me what's in my inbox" -> `/inbox-manager`
- "Create a plan for today" -> `/plan-generator`
- "Create an invoice for Test Corp" -> `/odoo-accounting`
- "List my customers in Odoo" -> `/odoo-accounting`
- "How's the business doing?" -> `/ceo-briefing`
- "What did the AI do today?" -> `/audit-logger`
- "Is everything running OK?" -> `/error-recovery`
- "Send an email to X" -> `/email-sending`
- "Draft a LinkedIn post" -> `/linkedin-posting`

## Implementation Files

```
ai-employee-watcher/
├── gmail_mcp_server.py     # Gmail MCP Server
├── odoo_mcp_server.py      # Odoo MCP Server (Gold)
├── social_mcp_server.py    # Social Media MCP Server (Gold)
├── audit_logger.py         # Structured JSON logging (Gold)
├── retry_handler.py        # Exponential backoff retry (Gold)
├── watchdog_monitor.py     # Process health monitor (Gold)
├── orchestrator.py         # Cross-domain routing (Gold)
├── ceo_briefing.py         # CEO Weekly Briefing (Gold)
├── ralph_wiggum.py         # Stop Hook loop (Gold)
├── start_gold.py           # Gold Tier launcher (Gold)
├── start_silver.py         # Silver Tier launcher
├── scheduled_task.py       # Periodic task runner
├── skills.py               # Python skill functions
├── file_watcher.py         # File system watcher
├── gmail_watcher.py        # Gmail watcher
├── mock_watcher.py         # WhatsApp/LinkedIn mock
├── linkedin_poster.py      # LinkedIn poster
├── linkedin_real.py        # Real LinkedIn API
├── plan_loop.py            # Continuous plan regeneration
└── whatsapp_server.py      # WhatsApp webhook
```
