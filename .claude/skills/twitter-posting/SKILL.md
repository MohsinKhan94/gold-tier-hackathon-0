---
name: twitter-posting
description: Post tweets, create polls, search tweets, and get engagement metrics on Twitter/X. Use this for Twitter content creation, audience engagement, and performance tracking.
user-invocable: true
allowed-tools:
  - mcp: social
  - Read
  - Write
  - Glob
---

# Twitter/X Posting Skill (MCP)

Post tweets, create polls, and get engagement data from Twitter/X via the Twitter API v2.

## Available MCP Tools

### `post_tweet`
Post a tweet to Twitter/X.
- **text** (required): Tweet text (max 280 characters)

### `post_tweet_with_poll`
Post a tweet with an attached poll.
- **text** (required): Tweet text (max 280 characters)
- **options** (required): Comma-separated poll options (2-4, each max 25 chars)
- **duration_minutes** (optional): Poll duration, default 1440 (24h), max 10080 (7 days)

### `delete_tweet`
Delete a tweet.
- **tweet_id** (required): ID of the tweet to delete

### `get_twitter_user_info`
Get your Twitter profile (username, followers, tweet count). No parameters.

### `get_tweet_metrics`
Get engagement metrics for a specific tweet.
- **tweet_id** (required): Tweet ID

### `search_recent_tweets`
Search tweets from the last 7 days.
- **query** (required): Twitter search query
- **limit** (optional): Results count, default 10, max 100

### `get_social_engagement_summary`
Get combined engagement summary across all platforms.

## Workflow

1. Draft tweet (280 char limit - be concise!)
2. Use human-approval for business tweets
3. Use `post_tweet` to publish
4. Track engagement with `get_tweet_metrics`
5. Monitor mentions with `search_recent_tweets`

## Twitter API Limits (Free Tier)

- **Post:** 1,500 tweets/month
- **Read:** 10,000 tweets/month
- **Search:** Recent tweets only (last 7 days)

## When to Use

- User asks to post on Twitter/X
- User asks about Twitter engagement
- User asks to search tweets or monitor topics
- User wants to create a poll
- Scheduled social media posting workflow

## Safety Rules

- Always use human-approval for business tweets
- Check character count before posting (280 max)
- Never post personal/sensitive information without approval
- Be mindful of API rate limits (1,500 tweets/month on free tier)
