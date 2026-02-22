 Gold Tier: Autonomous Employee - Full Architecture & Explanation

  What You Already Have (Bronze + Silver)

  Your current project already includes:
  - Obsidian Vault with Dashboard.md, SKILLS.md, folder structure (Inbox, Done, etc.)
  - 10 Agent Skills (vault-operations, file-monitoring, email-monitoring, whatsapp-monitoring, linkedin-posting,
  plan-generator, dashboard-updater, human-approval, inbox-manager, email-sending)
  - Watchers: Gmail watcher, file watcher, mock WhatsApp watcher
  - MCP Server: Gmail MCP for sending/drafting/searching emails
  - LinkedIn posting, Plan.md generation, Human-in-the-loop approval
  - Scheduling via scheduled_task.py and start_silver.py

  ---
  Gold Tier Requirements (What You Need to Build)

  Gold adds 11 new requirements on top of Silver. Let me break down each one:

  1. Full Cross-Domain Integration (Personal + Business)

  What it means: Right now your system handles personal stuff (Gmail, WhatsApp) and some business stuff (LinkedIn)        
  separately. Gold requires them to work together. Example: A WhatsApp message from a client triggers an invoice lookup in   Odoo, which triggers an email, which logs to the accounting system.

  Architecture: A unified orchestrator that routes events across domains. A client WhatsApp message about "invoice" should   flow through WhatsApp Watcher -> Claude reasoning -> Odoo lookup -> Email MCP -> Audit log.

  ---
  2. Odoo Community ERP Integration via MCP Server

  What it means: Install https://www.odoo.com/ (self-hosted, free, open-source ERP) and connect it to your AI Employee via   an MCP server using Odoo's JSON-RPC API.

  Why Odoo: It gives you a real accounting/invoicing/CRM system instead of just markdown files. Your AI Employee becomes a   real business tool.

  Architecture:
  Claude Code  <-->  Odoo MCP Server  <-->  Odoo 19+ (localhost:8069)
                     (JSON-RPC API)

  Key capabilities the MCP server should expose:
  - Create/read invoices
  - Log transactions
  - Check balances
  - List customers/vendors
  - Create purchase/sale orders

  Reference MCP: The hackathon doc links to https://github.com/AlanOgic/mcp-odoo-adv

  ---
  3. Facebook & Instagram Integration

  What it means: Post content to Facebook and Instagram (like you already do with LinkedIn), plus generate engagement     
  summaries.

  Architecture:
  - Use Meta Graph API (Facebook/Instagram share the same API)
  - New MCP server or extend existing social posting skill
  - New agent skill: facebook-posting, instagram-posting
  - Summary generator that pulls engagement metrics (likes, comments, reach)

  ---
  4. Twitter (X) Integration

  What it means: Same as above but for Twitter/X.

  Architecture:
  - Use Twitter API v2 (OAuth 2.0)
  - New MCP server for X
  - New agent skill: twitter-posting
  - Summary of engagement/impressions

  ---
  5. Multiple MCP Servers for Different Action Types

  What it means: You currently have 1 MCP server (Gmail). Gold needs multiple specialized servers:

  Proposed MCP Servers:

  ┌─────────────┬──────────────────────────────────────┐
  │ MCP Server  │               Purpose                │
  ├─────────────┼──────────────────────────────────────┤
  │ gmail-mcp   │ Email (already done)                 │
  ├─────────────┼──────────────────────────────────────┤
  │ odoo-mcp    │ Accounting, invoices, CRM            │
  ├─────────────┼──────────────────────────────────────┤
  │ social-mcp  │ Facebook, Instagram, Twitter posting │
  ├─────────────┼──────────────────────────────────────┤
  │ browser-mcp │ Web automation via Playwright        │
  └─────────────┴──────────────────────────────────────┘

  Config in .claude/settings.local.json:
  {
    "mcpServers": {
      "gmail": { ... },
      "odoo": { "command": "python", "args": ["odoo_mcp_server.py"] },
      "social": { "command": "python", "args": ["social_mcp_server.py"] }
    }
  }

  ---
  6. Weekly Business & Accounting Audit with CEO Briefing

  What it means: Every Sunday night (scheduled), the AI Employee autonomously:
  1. Reads Business_Goals.md for targets
  2. Queries Odoo for the week's transactions/revenue
  3. Checks Done/ folder for completed tasks
  4. Identifies bottlenecks (tasks that took too long)
  5. Scans for unused subscriptions
  6. Generates a Monday_Morning_CEO_Briefing.md

  Architecture:
  Scheduled Task (Sunday night cron/Task Scheduler)
      |
      v
  Claude Code reads:
      - Business_Goals.md (targets)
      - Odoo API (revenue, expenses, invoices)
      - Done/ folder (completed tasks this week)
      - Social media metrics (engagement)
      |
      v
  Generates: Briefings/YYYY-MM-DD_Monday_Briefing.md
      - Revenue summary
      - Bottlenecks
      - Proactive suggestions (cancel unused subscriptions, etc.)

  ---
  7. Error Recovery & Graceful Degradation

  What it means: When things break, the system doesn't die. It handles failures gracefully:

  - Retry with exponential backoff for transient errors (API timeouts)
  - Queue locally when external services are down
  - Never auto-retry payments (require fresh approval)
  - Watchdog process that monitors all watchers and restarts crashed ones
  - Quarantine corrupted files instead of crashing

  Architecture: Add a watchdog.py and retry_handler.py module, plus error states in your existing skills.

  ---
  8. Comprehensive Audit Logging

  What it means: Every single action the AI takes gets logged in structured JSON:

  {
    "timestamp": "2026-02-19T10:30:00Z",
    "action_type": "email_send",
    "actor": "claude_code",
    "target": "client@example.com",
    "parameters": {"subject": "Invoice #123"},
    "approval_status": "approved",
    "approved_by": "human",
    "result": "success"
  }

  Storage: AI_Employee_Vault/Logs/YYYY-MM-DD.json (retain 90+ days)

  You already have basic logging in Logs/ but Gold requires structured JSON for every action across all skills and MCP    
  servers.

  ---
  9. Ralph Wiggum Loop (Autonomous Multi-Step Task Completion)

  What it means: A Stop Hook pattern that keeps Claude Code running until a task is fully complete. Instead of Claude     
  doing one step and waiting for your input, it loops:

  1. Orchestrator creates a task state file with a prompt
  2. Claude works on the task
  3. Claude tries to exit
  4. Stop hook checks: Is the task file in /Done?
     - NO  -> Block exit, re-inject prompt (loop continues)
     - YES -> Allow exit (task complete)
  5. Max iterations safety valve (e.g., 10)

  Architecture: This is a .claude/hooks/ configuration (a stop hook):
  {
    "hooks": {
      "Stop": [{
        "matcher": "",
        "command": "python ralph_wiggum.py"
      }]
    }
  }

  ---
  10. Documentation of Architecture & Lessons Learned

  What it means: A proper README.md and architecture documentation. Include:
  - System architecture diagram
  - Setup instructions
  - How each component works
  - Security measures
  - Lessons learned during development

  ---
  11. All AI Functionality as Agent Skills

  What it means: Every new feature (Odoo, Facebook, Twitter, CEO Briefing, etc.) must be implemented as Agent Skills in   
  .claude/skills/, not just raw scripts.

  ---
  Complete Gold Tier Architecture Diagram

  ┌──────────────────────────────────────────────────────────────────────┐
  │                    GOLD TIER: AUTONOMOUS EMPLOYEE                    │
  └──────────────────────────────────────────────────────────────────────┘

    EXTERNAL SOURCES
    ┌────────┬──────────┬───────┬──────────┬───────────┬────────────────┐
    │ Gmail  │ WhatsApp │ Files │ Facebook │ Instagram │   Twitter/X    │
    └───┬────┴────┬─────┴──┬───┴────┬─────┴─────┬─────┴───────┬────────┘
        │         │        │        │           │             │
        ▼         ▼        ▼        ▼           ▼             ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │               PERCEPTION LAYER (Python Watchers)                 │
    │  Gmail Watcher │ WhatsApp Watcher │ File Watcher │ Social Watcher│
    └──────────────────────────┬───────────────────────────────────────┘
                               │ Creates .md files
                               ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    OBSIDIAN VAULT (Local)                        │
    │                                                                  │
    │  /Inbox/          - Raw incoming items                           │
    │  /Needs_Action/   - Items requiring processing                   │
    │  /Plans/          - Claude's action plans                        │
    │  /Pending_Approval/ - Awaiting human sign-off                    │
    │  /Approved/       - Human-approved actions                       │
    │  /Done/           - Completed items                              │
    │  /Logs/           - Structured JSON audit logs                   │
    │  /Briefings/      - CEO Monday briefings                         │
    │  /Social_Posts/   - LinkedIn, FB, Instagram, X drafts            │
    │                                                                  │
    │  Dashboard.md │ Business_Goals.md │ Company_Handbook.md          │
    └──────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    REASONING LAYER                               │
    │  ┌────────────────────────────────────────────────────────────┐  │
    │  │                    CLAUDE CODE                             │  │
    │  │  Read → Think → Plan → Write → Request Approval           │  │
    │  │                                                            │  │
    │  │  Ralph Wiggum Loop (Stop Hook)                             │  │
    │  │  ┌─────────────────────────────────────┐                   │  │
    │  │  │ Task not done? → Re-inject prompt   │                   │  │
    │  │  │ Task in /Done? → Allow exit         │                   │  │
    │  │  └─────────────────────────────────────┘                   │  │
    │  └────────────────────────────────────────────────────────────┘  │
    │                                                                  │
    │  Agent Skills (.claude/skills/)                                  │
    │  ├── vault-operations    ├── odoo-accounting                     │
    │  ├── email-monitoring    ├── facebook-posting                    │
    │  ├── email-sending       ├── instagram-posting                   │
    │  ├── whatsapp-monitoring ├── twitter-posting                     │
    │  ├── linkedin-posting    ├── ceo-briefing                        │
    │  ├── plan-generator      ├── audit-logger                        │
    │  ├── dashboard-updater   └── error-recovery                      │
    │  ├── human-approval                                              │
    │  └── inbox-manager                                               │
    └──────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    MCP SERVERS (Action Layer)                    │
    │                                                                  │
    │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
    │  │ Gmail MCP│  │ Odoo MCP │  │Social MCP │  │ Browser MCP   │  │
    │  │(existing)│  │(JSON-RPC)│  │(FB/IG/X)  │  │ (Playwright)  │  │
    │  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └──────┬────────┘  │
    └───────┼──────────────┼──────────────┼───────────────┼───────────┘
            │              │              │               │
            ▼              ▼              ▼               ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    EXTERNAL SERVICES                             │
    │  Gmail API │ Odoo 19 (localhost:8069) │ Meta Graph API           │
    │  Twitter API v2 │ Payment Portals (via browser)                  │
    └──────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                    ORCHESTRATION LAYER                           │
    │  ┌────────────────────────────────────────────────────────────┐  │
    │  │  Orchestrator.py - Master scheduler + folder watcher       │  │
    │  │  Watchdog.py     - Health monitor, auto-restart processes  │  │
    │  │  Retry Handler   - Exponential backoff for transient errors│  │
    │  │  Scheduled Tasks - Cron/Task Scheduler (CEO briefing, etc.)│  │
    │  └────────────────────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                    HUMAN-IN-THE-LOOP                             │
    │  Review /Pending_Approval/ → Move to /Approved/ or /Rejected/   │
    │  Required for: Payments, new contacts, social posts, large sends│
    └──────────────────────────────────────────────────────────────────┘

  ---
  Summary: What Gold Adds Over Silver

  ┌─────┬──────────────────────────────┬─────────────────┬───────────────────────────────────────────────┐
  │  #  │           Feature            │ Effort Estimate │                   Key Tech                    │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 1   │ Cross-domain integration     │ Medium          │ Orchestrator rewiring                         │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 2   │ Odoo ERP + MCP               │ High            │ Odoo 19, JSON-RPC, new MCP server             │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 3   │ Facebook + Instagram         │ Medium          │ Meta Graph API                                │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 4   │ Twitter/X                    │ Medium          │ Twitter API v2                                │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 5   │ Multiple MCP servers         │ Medium          │ Extend .claude/settings.local.json            │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 6   │ CEO Briefing                 │ Medium          │ Scheduled task + Odoo data                    │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 7   │ Error recovery               │ Medium          │ Retry handler, watchdog, graceful degradation │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 8   │ Audit logging                │ Low-Medium      │ Structured JSON logging in all skills         │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 9   │ Ralph Wiggum loop            │ Medium          │ Stop hook in .claude/hooks/                   │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 10  │ Documentation                │ Low             │ README.md, architecture docs                  │
  ├─────┼──────────────────────────────┼─────────────────┼───────────────────────────────────────────────┤
  │ 11  │ All features as Agent Skills │ Low             │ Wrap each feature in .claude/skills/          │
  └─────┴──────────────────────────────┴─────────────────┴───────────────────────────────────────────────┘

  The biggest lift is #2 (Odoo) - it requires installing and configuring a full ERP system, then building an MCP server to   bridge it with Claude Code. Everything else builds on patterns you already have from Bronze/Silver.



====================================================================================================

 Gold Tier Implementation Plan - Personal AI Employee

 Context

 You've completed Bronze + Silver tier with Gmail monitoring, WhatsApp integration, LinkedIn posting, Plan.md generation, 
  email sending via MCP, and human-in-the-loop approval. Gold Tier adds 11 new requirements: Odoo ERP, Facebook,
 Instagram, Twitter/X, multiple MCP servers, CEO briefing, error recovery, audit logging, Ralph Wiggum loop,
 documentation, and all as Agent Skills.

 Key Decision: Everything REAL - no mocks.

 ---
 PHASE 0: Get All API Keys & Accounts (You Do This First)

 Step 1: Install Odoo 19 Community Edition (Local)

 Option A: Docker (Recommended)
 1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
 2. After install, open terminal and run:
 docker run -d -p 8069:8069 -p 8072:8072 --name odoo -e HOST=localhost -t odoo:17.0
 2. (Note: Odoo 19 may not have an official Docker image yet - use latest available, likely 17.0 or 18.0)
 3. Open browser: http://localhost:8069
 4. Create your database:
   - Master Password: admin
   - Database Name: ai_employee
   - Email: your email
   - Password: choose one (e.g., admin)
   - Language: English
   - Country: Pakistan
 5. Install these modules from Odoo Apps:
   - Invoicing (account)
   - CRM (crm)
   - Contacts (contacts)
   - Sales (sale)
 6. JSON-RPC is enabled by default at http://localhost:8069/jsonrpc
 7. Credentials you'll have:
   - URL: http://localhost:8069
   - Database: ai_employee
   - Username: your email
   - Password: what you set
   - JSON-RPC endpoint: http://localhost:8069/jsonrpc

 Option B: Direct Install (No Docker)
 1. Download from https://www.odoo.com/page/download (Community Edition)
 2. Run the Windows installer
 3. It installs PostgreSQL automatically
 4. Access at http://localhost:8069
 5. Same database setup as above

 Python library: xmlrpc.client (built-in) or requests for JSON-RPC

 ---
 Step 2: Facebook Graph API (Page Posting)

 1. Create a Meta Developer Account:
   - Go to https://developers.facebook.com/
   - Click "Get Started" → Log in with your Facebook account
   - Accept Developer terms
 2. Create an App:
   - Go to https://developers.facebook.com/apps/
   - Click "Create App"
   - Select "Business" type
   - App name: AI Employee
   - Contact email: your email
   - Click "Create App"
 3. Add Facebook Login Product:
   - In your app dashboard, click "Add Product"
   - Add "Facebook Login" → Settings
   - Set Valid OAuth Redirect URIs: https://localhost/
 4. Get a Page Access Token:
   - Go to https://developers.facebook.com/tools/explorer/
   - Select your App from dropdown
   - Click "Get Token" → "Get Page Access Token"
   - Select your Facebook Page
   - Add permissions: pages_manage_posts, pages_read_engagement, pages_show_list
   - Click "Generate Access Token"
   - Copy this token - this is your FACEBOOK_PAGE_ACCESS_TOKEN
 5. Get your Page ID:
   - In Graph API Explorer, query: me/accounts
   - Find your page in the response → copy the id field
   - This is your FACEBOOK_PAGE_ID
 6. Extend Token to Long-Lived (60 days):
   - In Graph API Explorer, query:
   oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token= 
 YOUR_SHORT_TOKEN
   - Copy the new long-lived token

 Credentials you'll have:
 - FACEBOOK_APP_ID
 - FACEBOOK_APP_SECRET
 - FACEBOOK_PAGE_ACCESS_TOKEN (long-lived)
 - FACEBOOK_PAGE_ID

 Cost: Free

 Python library: requests (direct Graph API calls)

 ---
 Step 3: Instagram Graph API (Business Account Posting)

 Prerequisites: You need a Facebook Page linked to an Instagram Business/Creator account.

 1. Convert Instagram to Business Account:
   - Open Instagram app → Settings → Account → Switch to Professional Account → Business
   - Link it to your Facebook Page
 2. Get Instagram Business Account ID:
   - In Graph API Explorer (https://developers.facebook.com/tools/explorer/)
   - Query: me/accounts?fields=instagram_business_account
   - Or: {PAGE_ID}?fields=instagram_business_account
   - Copy the instagram_business_account.id → This is your INSTAGRAM_BUSINESS_ID
 3. Permissions needed (same app as Facebook):
   - instagram_basic
   - instagram_content_publish
   - pages_read_engagement
 4. Publishing flow:
   - Instagram Graph API requires a 2-step process:
       i. Create a media container (with image URL or video URL)
     ii. Publish the container
   - Important: Instagram API requires an image/video URL (publicly accessible) for posts. Text-only posts are NOT        
 supported via API.

 Credentials you'll have:
 - INSTAGRAM_BUSINESS_ID
 - Uses same FACEBOOK_PAGE_ACCESS_TOKEN from Step 2

 Cost: Free

 Python library: requests

 ---
 Step 4: Twitter/X API v2

 1. Apply for Developer Account:
   - Go to https://developer.x.com/en/portal/petition/essential/basic-info
   - Sign in with your X/Twitter account
   - Fill in:
       - What's your use case: "Building an AI assistant that posts business updates"
     - Country: Pakistan
 2. Create a Project & App:
   - Go to https://developer.x.com/en/portal/dashboard
   - Click "Create Project"
   - Project name: AI Employee
   - Use case: "Making a bot"
   - Project description: "AI employee that posts business updates"
   - Click "Create App" within the project
   - App name: AI Employee Bot
 3. Get API Keys:
   - After creating the app, you'll see:
       - API_KEY (Consumer Key)
     - API_KEY_SECRET (Consumer Secret)
     - BEARER_TOKEN
   - Save these immediately - they're shown only once
 4. Generate Access Tokens:
   - In your app settings → "Keys and Tokens" tab
   - Under "Authentication Tokens" → Click "Generate"
   - You'll get:
       - ACCESS_TOKEN
     - ACCESS_TOKEN_SECRET
 5. Set App Permissions:
   - In app settings → "User authentication settings" → "Set up"
   - App permissions: Read and write
   - Type: Web App, Automated App or Bot
   - Callback URL: https://localhost/
   - Website URL: your website or GitHub

 Credentials you'll have:
 - TWITTER_API_KEY
 - TWITTER_API_KEY_SECRET
 - TWITTER_BEARER_TOKEN
 - TWITTER_ACCESS_TOKEN
 - TWITTER_ACCESS_TOKEN_SECRET

 Cost: Free tier allows 1,500 tweets/month (posting). Read limits: 10,000 tweets/month.

 Python library: tweepy (recommended) or requests

 ---
 Step 5: LinkedIn API (You may already have this)

 1. Create LinkedIn App:
   - Go to https://www.linkedin.com/developers/apps
   - Click "Create App"
   - App name: AI Employee
   - LinkedIn Page: Select your company page (create one if needed)
   - Logo: Upload any image
   - Accept terms → Create
 2. Request Products:
   - In your app → "Products" tab
   - Request access to "Share on LinkedIn" (gives w_member_social permission)
   - This may take 1-2 days to approve
 3. Get Access Token:
   - Auth tab → Copy Client ID and Client Secret
   - Use OAuth 2.0 flow:
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://local 
 host/&scope=openid%20profile%20w_member_social
   - After redirect, extract code from URL
   - Exchange code for token via POST to https://www.linkedin.com/oauth/v2/accessToken
 4. Get your Person URN:
   - Call https://api.linkedin.com/v2/userinfo with your access token
   - Your URN is: urn:li:person:{sub}

 Credentials you'll have:
 - LINKEDIN_CLIENT_ID
 - LINKEDIN_CLIENT_SECRET
 - LINKEDIN_ACCESS_TOKEN
 - LINKEDIN_PERSON_URN

 Cost: Free

 Python library: requests

 ---
 PHASE 1: Build the Infrastructure (I Build This)

 After you have all the API keys, I will build:

 1. Odoo MCP Server (odoo_mcp_server.py)

 - Connect to your local Odoo via JSON-RPC (xmlrpc.client)
 - MCP tools: create_invoice, list_invoices, get_balance, list_customers, create_sale_order, log_transaction
 - Register in .claude/settings.local.json

 2. Social Media MCP Server (social_mcp_server.py)

 - Facebook posting via Graph API (post_to_facebook, get_facebook_insights)
 - Instagram posting via Graph API (post_to_instagram, get_instagram_insights)
 - Twitter/X posting via API v2 (post_tweet, get_tweet_metrics)
 - Register in .claude/settings.local.json

 3. Cross-Domain Orchestrator (orchestrator.py)

 - Unified event routing: WhatsApp → Odoo lookup → Email → Audit log
 - Domain detection: personal vs business classification
 - Event chaining across watchers and MCP servers

 4. CEO Weekly Briefing (ceo_briefing.py)

 - Scheduled task (Sunday night)
 - Reads: Business_Goals.md, Odoo data (revenue/invoices), Done/ folder, social metrics
 - Generates: Briefings/YYYY-MM-DD_Monday_Briefing.md

 5. Error Recovery & Watchdog (watchdog.py, retry_handler.py)

 - Exponential backoff retry for API calls
 - Watchdog monitors all processes, auto-restarts crashed ones
 - Queue locally when services are down
 - Never auto-retry payments

 6. Structured Audit Logging (audit_logger.py)

 - JSON-structured logging for every action
 - Stored in Logs/YYYY-MM-DD.json
 - 90+ day retention
 - Integrated into all skills and MCP servers

 7. Ralph Wiggum Stop Hook (ralph_wiggum.py)

 - .claude/hooks/ Stop hook configuration
 - Checks if current task file is in /Done
 - Re-injects prompt if not done, allows exit if done
 - Max 10 iteration safety valve

 8. New Vault Folders

 - /Briefings/ - CEO Monday briefings
 - Business_Goals.md - Revenue targets, KPIs
 - Company_Handbook.md - Rules of engagement

 9. New Agent Skills (.claude/skills/)

 - odoo-accounting/SKILL.md
 - facebook-posting/SKILL.md
 - instagram-posting/SKILL.md
 - twitter-posting/SKILL.md
 - ceo-briefing/SKILL.md
 - audit-logger/SKILL.md
 - error-recovery/SKILL.md

 10. Documentation

 - README.md - Full architecture, setup instructions, component explanations
 - Architecture diagram
 - Security measures documented
 - Lessons learned

 11. Updated Orchestrator (start_gold.py)

 - Launches all Gold Tier services
 - Includes watchdog health monitoring
 - Scheduled tasks for CEO briefing

 ---
 PHASE 2: Configuration

 .env file (you fill in your keys):

 # Odoo
 ODOO_URL=http://localhost:8069
 ODOO_DB=ai_employee
 ODOO_USER=your_email
 ODOO_PASSWORD=your_password

 # Facebook
 FACEBOOK_PAGE_ACCESS_TOKEN=your_token
 FACEBOOK_PAGE_ID=your_page_id

 # Instagram
 INSTAGRAM_BUSINESS_ID=your_ig_id

 # Twitter/X
 TWITTER_API_KEY=your_key
 TWITTER_API_KEY_SECRET=your_secret
 TWITTER_BEARER_TOKEN=your_bearer
 TWITTER_ACCESS_TOKEN=your_access_token
 TWITTER_ACCESS_TOKEN_SECRET=your_access_secret

 # LinkedIn
 LINKEDIN_ACCESS_TOKEN=your_token
 LINKEDIN_PERSON_URN=urn:li:person:your_id

 # Gemini (existing)
 GEMINI_API_KEY=your_key

 .claude/settings.local.json (I configure):

 {
   "mcpServers": {
     "gmail": { ... },
     "github": { ... },
     "odoo": { "command": "python", "args": ["odoo_mcp_server.py"] },
     "social": { "command": "python", "args": ["social_mcp_server.py"] }
   }
 }

 ---
 Verification Plan

 After implementation, we'll test each component:
 1. Odoo: Create an invoice via MCP → verify in Odoo web UI at localhost:8069
 2. Facebook: Post via MCP → verify on your Facebook Page
 3. Instagram: Post via MCP → verify on Instagram
 4. Twitter: Post via MCP → verify on Twitter/X
 5. CEO Briefing: Trigger manually → check Briefings/ folder
 6. Audit Logging: Run any action → check Logs/YYYY-MM-DD.json
 7. Ralph Wiggum: Create a multi-step task → verify loop continues until Done
 8. Error Recovery: Kill a watcher → verify watchdog restarts it
 9. Cross-Domain: Send a WhatsApp about "invoice" → verify Odoo lookup triggers
 10. Full Demo: End-to-end flow for LinkedIn video recording

 ---
 Summary: What You Need To Do First

 ┌─────┬──────────────────────────────────────────────┬───────────────┐
 │  #  │                    Action                    │ Time Estimate │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 1   │ Install Docker Desktop + run Odoo container  │ 30 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 2   │ Set up Odoo database + install modules       │ 15 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 3   │ Create Meta Developer account + Facebook App │ 20 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 4   │ Get Facebook Page Access Token               │ 10 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 5   │ Link Instagram Business Account              │ 10 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 6   │ Apply for Twitter/X Developer account        │ 15 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 7   │ Create Twitter app + get all tokens          │ 10 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 8   │ Set up LinkedIn Developer app (if not done)  │ 15 min        │
 ├─────┼──────────────────────────────────────────────┼───────────────┤
 │ 9   │ Create .env file with all credentials        │ 10 min        │
 └─────┴──────────────────────────────────────────────┴───────────────┘

 Total setup time: ~2 hours

 Once you have all credentials in the .env file, tell me and I'll build everything.