---
name: facebook-posting
description: Post content to Facebook Page, view posts with engagement metrics, and get page insights. Use this when creating Facebook content, checking post performance, or reviewing page analytics.
user-invocable: true
allowed-tools:
  - mcp: social
  - Read
  - Write
  - Glob
---

# Facebook Posting Skill (MCP)

Post content and get engagement data from your Facebook Page via the Meta Graph API.

## Available MCP Tools

### `post_to_facebook`
Post a text message (with optional link) to your Facebook Page.
- **message** (required): Post text content
- **link** (optional): URL to include in the post

### `get_facebook_page_info`
Get your page info (name, followers, category, etc). No parameters.

### `get_facebook_posts`
Get recent posts with engagement metrics.
- **limit** (optional): Number of posts, default 10, max 25

### `get_facebook_insights`
Get page analytics (impressions, engagements, fan growth).
- **period** (optional): 'day', 'week', or 'days_28'
- **metric** (optional): e.g. 'page_impressions', 'page_engaged_users', 'page_post_engagements'

### `get_social_engagement_summary`
Get combined engagement summary across all platforms. No parameters.

## Workflow

1. Draft post content (consider audience, tone, timing)
2. Use human-approval workflow for business posts - create approval file in `Pending_Approval/`
3. Once approved, use `post_to_facebook` to publish
4. Check engagement with `get_facebook_posts` after 24 hours
5. Review weekly performance with `get_facebook_insights`

## When to Use

- User asks to post on Facebook
- User asks about Facebook page performance
- User asks for social media engagement summary
- Scheduled social media posting workflow

## Safety Rules

- Always use human-approval for business-related posts
- Log all posts to `AI_Employee_Vault/Logs/social_actions_*.md`
- Never post personal/sensitive information without explicit approval
