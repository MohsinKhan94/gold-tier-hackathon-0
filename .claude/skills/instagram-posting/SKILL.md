---
name: instagram-posting
description: Post images and carousels to Instagram, view media with engagement metrics, and get post insights. Use this for Instagram content creation and performance tracking.
user-invocable: true
allowed-tools:
  - mcp: social
  - Read
  - Write
  - Glob
---

# Instagram Posting Skill (MCP)

Post images/carousels and get engagement data from your Instagram Business account via the Meta Graph API.

## Available MCP Tools

### `post_to_instagram`
Post a single image to Instagram.
- **image_url** (required): Publicly accessible URL of the image
- **caption** (optional): Caption text for the post

**Important:** Instagram Graph API does NOT support text-only posts. You MUST provide an image URL.

### `post_carousel_to_instagram`
Post a carousel (2-10 images) to Instagram.
- **image_urls** (required): Comma-separated publicly accessible image URLs
- **caption** (optional): Caption text

### `get_instagram_profile`
Get profile info (username, followers, media count, bio). No parameters.

### `get_instagram_media`
Get recent posts with engagement (likes, comments).
- **limit** (optional): Number of posts, default 10, max 25

### `get_instagram_insights`
Get insights for a specific post (impressions, reach, engagement, saved).
- **media_id** (required): Instagram media ID

### `get_social_engagement_summary`
Get combined engagement summary across all platforms.

## Workflow

1. Prepare image content (image must be publicly accessible via URL)
2. Write caption (use hashtags, call-to-action)
3. Use human-approval for business posts
4. Use `post_to_instagram` to publish
5. Check performance with `get_instagram_media` and `get_instagram_insights`

## Image Requirements

- Must be a publicly accessible URL (not a local file)
- Supported formats: JPEG, PNG
- Minimum 320x320 pixels
- Maximum aspect ratio: 1.91:1 (landscape) to 4:5 (portrait)
- For carousels: 2-10 images, all same aspect ratio recommended

## When to Use

- User asks to post on Instagram
- User asks about Instagram performance
- User asks to create visual content
- Scheduled social media posting workflow

## Safety Rules

- Always use human-approval for business posts
- Verify image URLs are accessible before posting
- Never post without a caption for business accounts
