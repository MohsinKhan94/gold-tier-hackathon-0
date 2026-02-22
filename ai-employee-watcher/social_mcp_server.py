"""
Social Media MCP Server - Gold Tier
Exposes Facebook, Instagram, and Twitter/X posting and engagement tools
as MCP tools for Claude Code.

APIs used:
- Facebook: Meta Graph API (v19.0)
- Instagram: Meta Graph API (v19.0) - requires linked Facebook Page
- Twitter/X: GetXAPI proxy (api.getxapi.com) for posting, official API v2 for reads
"""

import json
import os
import sys
import requests
import hashlib
import hmac
import time
import base64
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
SCRIPT_DIR = Path(__file__).parent
ENV_PATH = SCRIPT_DIR.parent / ".env"
load_dotenv(ENV_PATH)

# Vault paths for logging
VAULT_PATH = SCRIPT_DIR.parent / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
SOCIAL_POSTS_PATH = VAULT_PATH / "Social_Posts"
LOGS_PATH.mkdir(parents=True, exist_ok=True)
SOCIAL_POSTS_PATH.mkdir(parents=True, exist_ok=True)

# ─── Credentials ─────────────────────────────────────────────────────────────

# Facebook
FB_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")

# Instagram (uses same Facebook Page Access Token)
IG_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID", "")

# Twitter/X (GetXAPI proxy)
GETXAPI_KEY = os.getenv("GETXAPI", "")
TWITTER_AUTH_TOKEN = os.getenv("TWITTER_AUTH_TOKEN", "")

# Legacy Twitter keys (kept for bearer token reads)
TW_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Meta Graph API base URL
GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

# Twitter API base URLs
TWITTER_API_BASE = "https://api.twitter.com/2"
GETXAPI_BASE = "https://api.getxapi.com"

# Initialize MCP server
mcp = FastMCP(
    "social",
    instructions=(
        "Social Media MCP server for posting to Facebook, Instagram, and Twitter/X. "
        "Also retrieves engagement metrics and insights."
    ),
)

# ─── Audit Logger ────────────────────────────────────────────────────────────

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from audit_logger import log_audit
except ImportError:
    def log_audit(**kwargs):
        pass


def log_social_action(action: str, details: dict):
    """Log social media actions to vault markdown log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"social_actions_{date_str}.md"

    entry = f"\n## [{timestamp}] {action}\n"
    for key, value in details.items():
        entry += f"- **{key}:** {value}\n"
    entry += "---\n"

    if not log_file.exists():
        header = f"# Social Media Action Log - {date_str}\n\nAll social media actions via Social MCP Server.\n\n---\n"
        log_file.write_text(header + entry, encoding="utf-8")
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _check_facebook_credentials():
    if not FB_PAGE_ACCESS_TOKEN or not FB_PAGE_ID:
        raise ValueError(
            "Facebook credentials not configured. "
            "Set FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env"
        )


def _check_instagram_credentials():
    if not FB_PAGE_ACCESS_TOKEN or not IG_BUSINESS_ID:
        raise ValueError(
            "Instagram credentials not configured. "
            "Set FACEBOOK_PAGE_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ID in .env"
        )


def _check_twitter_credentials():
    if not GETXAPI_KEY or not TWITTER_AUTH_TOKEN:
        raise ValueError(
            "Twitter credentials not configured. "
            "Set GETXAPI and TWITTER_AUTH_TOKEN in .env"
        )


def _getxapi_headers() -> dict:
    """Return headers for GetXAPI requests."""
    return {
        "Authorization": f"Bearer {GETXAPI_KEY}",
        "Content-Type": "application/json",
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  FACEBOOK TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def post_to_facebook(message: str, link: str = "") -> str:
    """Post a text message (with optional link) to your Facebook Page.

    Args:
        message: The post text content (required)
        link: Optional URL to include in the post

    Returns:
        JSON string with post ID and status
    """
    try:
        _check_facebook_credentials()

        url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/feed"
        payload = {
            "message": message,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        if link:
            payload["link"] = link

        resp = requests.post(url, data=payload, timeout=30)
        data = resp.json()

        if "error" in data:
            error_msg = data["error"].get("message", str(data["error"]))
            log_social_action("FACEBOOK_POST_FAILED", {"Error": error_msg, "Message": message[:100]})
            log_audit(action_type="facebook_post", target="facebook_page", result="failure", error_message=error_msg)
            return json.dumps({"status": "error", "error": error_msg})

        post_id = data.get("id", "")
        log_social_action("FACEBOOK_POST", {"Post ID": post_id, "Message": message[:100], "Link": link or "None"})
        log_audit(
            action_type="facebook_post",
            target="facebook_page",
            parameters={"message_preview": message[:100], "link": link},
            result="success",
        )
        return json.dumps({"status": "success", "post_id": post_id, "message_preview": message[:100]})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_facebook_page_info() -> str:
    """Get information about your Facebook Page (name, followers, etc).

    Returns:
        JSON string with page info
    """
    try:
        _check_facebook_credentials()

        url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}"
        params = {
            "fields": "name,fan_count,followers_count,category,about,link",
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        log_social_action("FACEBOOK_PAGE_INFO", {"Page": data.get("name", ""), "Followers": data.get("followers_count", 0)})
        return json.dumps({"status": "success", "page": data})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_facebook_posts(limit: int = 10) -> str:
    """Get recent posts from your Facebook Page with engagement metrics.

    Args:
        limit: Number of posts to retrieve (default 10, max 25)

    Returns:
        JSON string with list of posts and their engagement
    """
    try:
        _check_facebook_credentials()
        limit = min(limit, 25)

        url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/posts"
        params = {
            "fields": "id,message,created_time,shares,likes.summary(true),comments.summary(true)",
            "limit": limit,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        posts = []
        for post in data.get("data", []):
            posts.append({
                "id": post.get("id", ""),
                "message": post.get("message", "")[:200],
                "created_time": post.get("created_time", ""),
                "likes": post.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                "shares": post.get("shares", {}).get("count", 0),
            })

        log_social_action("FACEBOOK_GET_POSTS", {"Count": len(posts)})
        return json.dumps({"status": "success", "count": len(posts), "posts": posts})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_facebook_insights(period: str = "day", metric: str = "page_impressions") -> str:
    """Get Facebook Page insights/analytics.

    Args:
        period: Time period - 'day', 'week', or 'days_28' (default 'day')
        metric: Metric name. Options: page_impressions, page_engaged_users,
                page_post_engagements, page_fan_adds, page_views_total

    Returns:
        JSON string with insight data
    """
    try:
        _check_facebook_credentials()

        url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/insights/{metric}"
        params = {
            "period": period,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        insights = data.get("data", [])
        log_social_action("FACEBOOK_INSIGHTS", {"Metric": metric, "Period": period})
        return json.dumps({"status": "success", "metric": metric, "period": period, "data": insights})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════════
#  INSTAGRAM TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def post_to_instagram(image_url: str, caption: str = "") -> str:
    """Post an image to Instagram (requires a publicly accessible image URL).

    Instagram API requires a 2-step process:
    1. Create a media container with the image URL
    2. Publish the container

    Note: Instagram Graph API does NOT support text-only posts.

    Args:
        image_url: Publicly accessible URL of the image to post (required)
        caption: Caption text for the post (optional)

    Returns:
        JSON string with media ID and status
    """
    try:
        _check_instagram_credentials()

        # Step 1: Create media container
        url = f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media"
        payload = {
            "image_url": image_url,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        if caption:
            payload["caption"] = caption

        resp = requests.post(url, data=payload, timeout=60)
        data = resp.json()

        if "error" in data:
            error_msg = data["error"].get("message", str(data["error"]))
            log_social_action("INSTAGRAM_POST_FAILED", {"Error": error_msg, "Step": "create_container"})
            return json.dumps({"status": "error", "error": error_msg, "step": "create_container"})

        container_id = data.get("id")
        if not container_id:
            return json.dumps({"status": "error", "error": "No container ID returned"})

        # Step 2: Publish the container
        publish_url = f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }

        # Wait for container to be ready (Instagram processes asynchronously)
        time.sleep(3)

        pub_resp = requests.post(publish_url, data=publish_payload, timeout=60)
        pub_data = pub_resp.json()

        if "error" in pub_data:
            error_msg = pub_data["error"].get("message", str(pub_data["error"]))
            log_social_action("INSTAGRAM_POST_FAILED", {"Error": error_msg, "Step": "publish"})
            return json.dumps({"status": "error", "error": error_msg, "step": "publish"})

        media_id = pub_data.get("id", "")
        log_social_action("INSTAGRAM_POST", {
            "Media ID": media_id,
            "Caption": caption[:100] if caption else "None",
            "Image URL": image_url[:100],
        })
        log_audit(
            action_type="instagram_post",
            target="instagram_business",
            parameters={"caption_preview": caption[:100] if caption else "", "image_url": image_url[:100]},
            result="success",
        )
        return json.dumps({"status": "success", "media_id": media_id, "caption_preview": caption[:100] if caption else ""})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def post_carousel_to_instagram(image_urls: str, caption: str = "") -> str:
    """Post a carousel (multiple images) to Instagram.

    Args:
        image_urls: Comma-separated publicly accessible image URLs (2-10 images)
        caption: Caption text for the carousel post

    Returns:
        JSON string with media ID and status
    """
    try:
        _check_instagram_credentials()

        urls = [u.strip() for u in image_urls.split(",") if u.strip()]
        if len(urls) < 2:
            return json.dumps({"status": "error", "error": "Carousel requires at least 2 images"})
        if len(urls) > 10:
            return json.dumps({"status": "error", "error": "Carousel supports maximum 10 images"})

        # Step 1: Create containers for each image
        container_ids = []
        for url in urls:
            resp = requests.post(
                f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media",
                data={
                    "image_url": url,
                    "is_carousel_item": "true",
                    "access_token": FB_PAGE_ACCESS_TOKEN,
                },
                timeout=60,
            )
            data = resp.json()
            if "error" in data:
                return json.dumps({"status": "error", "error": data["error"].get("message", ""), "step": "create_item"})
            container_ids.append(data.get("id"))

        # Step 2: Create carousel container
        resp = requests.post(
            f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(container_ids),
                "caption": caption,
                "access_token": FB_PAGE_ACCESS_TOKEN,
            },
            timeout=60,
        )
        data = resp.json()
        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", ""), "step": "create_carousel"})

        carousel_id = data.get("id")
        time.sleep(5)

        # Step 3: Publish
        pub_resp = requests.post(
            f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media_publish",
            data={"creation_id": carousel_id, "access_token": FB_PAGE_ACCESS_TOKEN},
            timeout=60,
        )
        pub_data = pub_resp.json()
        if "error" in pub_data:
            return json.dumps({"status": "error", "error": pub_data["error"].get("message", ""), "step": "publish"})

        media_id = pub_data.get("id", "")
        log_social_action("INSTAGRAM_CAROUSEL", {"Media ID": media_id, "Images": len(urls), "Caption": caption[:100]})
        log_audit(action_type="instagram_carousel", target="instagram_business", result="success")
        return json.dumps({"status": "success", "media_id": media_id, "images": len(urls)})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_instagram_profile() -> str:
    """Get Instagram Business account profile information.

    Returns:
        JSON string with profile data (followers, media count, bio)
    """
    try:
        _check_instagram_credentials()

        url = f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}"
        params = {
            "fields": "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website",
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        log_social_action("INSTAGRAM_PROFILE", {
            "Username": data.get("username", ""),
            "Followers": data.get("followers_count", 0),
        })
        return json.dumps({"status": "success", "profile": data})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_instagram_media(limit: int = 10) -> str:
    """Get recent Instagram posts with engagement metrics.

    Args:
        limit: Number of posts to retrieve (default 10, max 25)

    Returns:
        JSON string with list of posts and their engagement
    """
    try:
        _check_instagram_credentials()
        limit = min(limit, 25)

        url = f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count,permalink",
            "limit": limit,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        posts = []
        for post in data.get("data", []):
            posts.append({
                "id": post.get("id", ""),
                "caption": (post.get("caption", "") or "")[:200],
                "media_type": post.get("media_type", ""),
                "timestamp": post.get("timestamp", ""),
                "likes": post.get("like_count", 0),
                "comments": post.get("comments_count", 0),
                "permalink": post.get("permalink", ""),
            })

        log_social_action("INSTAGRAM_GET_MEDIA", {"Count": len(posts)})
        return json.dumps({"status": "success", "count": len(posts), "posts": posts})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_instagram_insights(media_id: str) -> str:
    """Get insights for a specific Instagram post.

    Args:
        media_id: The Instagram media ID to get insights for

    Returns:
        JSON string with engagement metrics (impressions, reach, engagement)
    """
    try:
        _check_instagram_credentials()

        url = f"{GRAPH_API_BASE}/{media_id}/insights"
        params = {
            "metric": "impressions,reach,engagement,saved",
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            return json.dumps({"status": "error", "error": data["error"].get("message", str(data["error"]))})

        metrics = {}
        for item in data.get("data", []):
            metrics[item["name"]] = item["values"][0]["value"] if item.get("values") else 0

        log_social_action("INSTAGRAM_INSIGHTS", {"Media ID": media_id, **metrics})
        return json.dumps({"status": "success", "media_id": media_id, "metrics": metrics})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════════
#  TWITTER/X TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def post_tweet(text: str) -> str:
    """Post a tweet to Twitter/X via GetXAPI.

    Args:
        text: Tweet text (max 280 characters)

    Returns:
        JSON string with tweet ID and status
    """
    try:
        _check_twitter_credentials()

        if len(text) > 280:
            return json.dumps({"status": "error", "error": f"Tweet too long ({len(text)}/280 characters)"})

        url = f"{GETXAPI_BASE}/twitter/tweet/create"
        payload = {
            "auth_token": TWITTER_AUTH_TOKEN,
            "text": text,
        }

        resp = requests.post(url, headers=_getxapi_headers(), json=payload, timeout=30)
        data = resp.json()

        if data.get("status") != "success" or resp.status_code not in (200, 201):
            error_msg = data.get("error", data.get("msg", f"HTTP {resp.status_code}"))
            log_social_action("TWEET_FAILED", {"Error": error_msg, "Text": text[:100]})
            log_audit(action_type="tweet_post", target="twitter", result="failure", error_message=error_msg)
            return json.dumps({"status": "error", "error": error_msg, "http_status": resp.status_code})

        tweet_data = data.get("data", {})
        tweet_id = tweet_data.get("id", "")

        log_social_action("TWEET_POST", {"Tweet ID": tweet_id, "Text": text[:100]})
        log_audit(
            action_type="tweet_post",
            target="twitter",
            parameters={"text_preview": text[:100]},
            result="success",
        )
        return json.dumps({"status": "success", "tweet_id": tweet_id, "text_preview": text[:100]})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def post_tweet_with_poll(text: str, options: str, duration_minutes: int = 1440) -> str:
    """Post a tweet with a poll on Twitter/X via GetXAPI.

    Note: GetXAPI may not support polls directly. Falls back to posting text with poll options listed.

    Args:
        text: Tweet text (max 280 characters)
        options: Comma-separated poll options (2-4 options, each max 25 chars)
        duration_minutes: Poll duration in minutes (default 1440 = 24 hours, max 10080 = 7 days)

    Returns:
        JSON string with tweet ID and status
    """
    try:
        _check_twitter_credentials()

        poll_options = [o.strip() for o in options.split(",") if o.strip()]
        if len(poll_options) < 2 or len(poll_options) > 4:
            return json.dumps({"status": "error", "error": "Poll requires 2-4 options"})
        for opt in poll_options:
            if len(opt) > 25:
                return json.dumps({"status": "error", "error": f"Poll option too long: '{opt}' ({len(opt)}/25 chars)"})

        # Post as a regular tweet with poll options in text
        poll_text = text + "\n\nPoll:\n" + "\n".join(f"- {opt}" for opt in poll_options)
        if len(poll_text) > 280:
            poll_text = text  # Fallback to just the text if too long

        url = f"{GETXAPI_BASE}/twitter/tweet/create"
        payload = {
            "auth_token": TWITTER_AUTH_TOKEN,
            "text": poll_text,
        }

        resp = requests.post(url, headers=_getxapi_headers(), json=payload, timeout=30)
        data = resp.json()

        if data.get("status") != "success" or resp.status_code not in (200, 201):
            error_msg = data.get("error", data.get("msg", f"HTTP {resp.status_code}"))
            return json.dumps({"status": "error", "error": error_msg})

        tweet_data = data.get("data", {})
        tweet_id = tweet_data.get("id", "")
        log_social_action("TWEET_POLL", {"Tweet ID": tweet_id, "Options": poll_options})
        log_audit(action_type="tweet_poll", target="twitter", result="success")
        return json.dumps({"status": "success", "tweet_id": tweet_id, "poll_options": poll_options})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def delete_tweet(tweet_id: str) -> str:
    """Delete a tweet from Twitter/X via GetXAPI.

    Args:
        tweet_id: The ID of the tweet to delete

    Returns:
        JSON string with deletion status
    """
    try:
        _check_twitter_credentials()

        url = f"{GETXAPI_BASE}/twitter/tweet/delete"
        payload = {
            "auth_token": TWITTER_AUTH_TOKEN,
            "tweet_id": tweet_id,
        }

        resp = requests.post(url, headers=_getxapi_headers(), json=payload, timeout=30)
        data = resp.json()

        if data.get("status") == "success":
            log_social_action("TWEET_DELETE", {"Tweet ID": tweet_id})
            log_audit(action_type="tweet_delete", target=tweet_id, result="success")
            return json.dumps({"status": "success", "tweet_id": tweet_id, "deleted": True})
        else:
            error_msg = data.get("error", data.get("msg", "Tweet not deleted"))
            return json.dumps({"status": "error", "error": error_msg})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_twitter_user_info() -> str:
    """Get your Twitter/X profile information via GetXAPI.

    Returns:
        JSON string with profile data (username, followers, tweet count)
    """
    try:
        _check_twitter_credentials()

        # First get user ID from auth token, then get info
        url = f"{GETXAPI_BASE}/twitter/user/info"
        # GetXAPI needs userName param - get it from auth_token first
        me_url = f"{GETXAPI_BASE}/twitter/user/me"
        me_resp = requests.get(me_url, headers=_getxapi_headers(), params={"auth_token": TWITTER_AUTH_TOKEN}, timeout=30)
        me_data = me_resp.json()

        # If /user/me doesn't exist, try /user/info with auth_token
        if me_resp.status_code == 404 or "error" in me_data:
            # Try alternative: pass auth_token to user/info
            resp = requests.get(url, headers=_getxapi_headers(), params={"auth_token": TWITTER_AUTH_TOKEN}, timeout=30)
            data = resp.json()
        else:
            data = me_data

        if "error" in data and data.get("status") != "success":
            return json.dumps({"status": "error", "error": data.get("error", "Unknown error")})

        user = data.get("data", data)
        log_social_action("TWITTER_PROFILE", {
            "Username": user.get("username", user.get("screen_name", "")),
            "Followers": user.get("followers_count", 0),
        })
        return json.dumps({"status": "success", "profile": user})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def get_tweet_metrics(tweet_id: str) -> str:
    """Get engagement metrics for a specific tweet via GetXAPI.

    Args:
        tweet_id: The tweet ID to get metrics for

    Returns:
        JSON string with engagement metrics (likes, retweets, replies)
    """
    try:
        _check_twitter_credentials()

        url = f"{GETXAPI_BASE}/twitter/tweet/info"
        params = {"auth_token": TWITTER_AUTH_TOKEN, "tweet_id": tweet_id}

        resp = requests.get(url, headers=_getxapi_headers(), params=params, timeout=30)
        data = resp.json()

        if data.get("status") != "success" and "error" in data:
            return json.dumps({"status": "error", "error": data.get("error", "Unknown error")})

        tweet = data.get("data", {})
        metrics = {
            "like_count": tweet.get("favorite_count", tweet.get("like_count", 0)),
            "retweet_count": tweet.get("retweet_count", 0),
            "reply_count": tweet.get("reply_count", 0),
        }
        log_social_action("TWEET_METRICS", {"Tweet ID": tweet_id, **metrics})
        return json.dumps({
            "status": "success",
            "tweet_id": tweet_id,
            "text_preview": tweet.get("text", tweet.get("full_text", ""))[:100],
            "metrics": metrics,
        })

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@mcp.tool()
def search_recent_tweets(query: str, limit: int = 10) -> str:
    """Search recent tweets on Twitter/X via GetXAPI.

    Args:
        query: Search query (Twitter search syntax)
        limit: Number of results (default 10, max 100)

    Returns:
        JSON string with matching tweets
    """
    try:
        _check_twitter_credentials()
        limit = min(max(limit, 10), 100)

        url = f"{GETXAPI_BASE}/twitter/search"
        params = {
            "auth_token": TWITTER_AUTH_TOKEN,
            "query": query,
            "count": limit,
        }

        resp = requests.get(url, headers=_getxapi_headers(), params=params, timeout=30)
        data = resp.json()

        if data.get("status") != "success" and "error" in data:
            return json.dumps({"status": "error", "error": data.get("error", "Unknown error")})

        tweets = []
        for tweet in data.get("data", []):
            tweets.append({
                "id": tweet.get("id", tweet.get("id_str", "")),
                "text": tweet.get("text", tweet.get("full_text", ""))[:200],
                "created_at": tweet.get("created_at", ""),
                "metrics": {
                    "like_count": tweet.get("favorite_count", 0),
                    "retweet_count": tweet.get("retweet_count", 0),
                },
            })

        log_social_action("TWITTER_SEARCH", {"Query": query, "Results": len(tweets)})
        return json.dumps({"status": "success", "query": query, "count": len(tweets), "tweets": tweets})

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════════
#  CROSS-PLATFORM ENGAGEMENT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_social_engagement_summary() -> str:
    """Get a combined engagement summary across all configured social platforms.

    Returns:
        JSON string with engagement summary for Facebook, Instagram, and Twitter
    """
    summary = {"platforms": {}}

    # Facebook
    if FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID:
        try:
            resp = requests.get(
                f"{GRAPH_API_BASE}/{FB_PAGE_ID}",
                params={"fields": "name,fan_count,followers_count", "access_token": FB_PAGE_ACCESS_TOKEN},
                timeout=15,
            )
            data = resp.json()
            if "error" not in data:
                summary["platforms"]["facebook"] = {
                    "status": "connected",
                    "page_name": data.get("name", ""),
                    "followers": data.get("followers_count", 0),
                    "fans": data.get("fan_count", 0),
                }
            else:
                summary["platforms"]["facebook"] = {"status": "error", "error": data["error"].get("message", "")}
        except Exception as e:
            summary["platforms"]["facebook"] = {"status": "error", "error": str(e)}
    else:
        summary["platforms"]["facebook"] = {"status": "not_configured"}

    # Instagram
    if FB_PAGE_ACCESS_TOKEN and IG_BUSINESS_ID:
        try:
            resp = requests.get(
                f"{GRAPH_API_BASE}/{IG_BUSINESS_ID}",
                params={"fields": "username,followers_count,media_count", "access_token": FB_PAGE_ACCESS_TOKEN},
                timeout=15,
            )
            data = resp.json()
            if "error" not in data:
                summary["platforms"]["instagram"] = {
                    "status": "connected",
                    "username": data.get("username", ""),
                    "followers": data.get("followers_count", 0),
                    "media_count": data.get("media_count", 0),
                }
            else:
                summary["platforms"]["instagram"] = {"status": "error", "error": data["error"].get("message", "")}
        except Exception as e:
            summary["platforms"]["instagram"] = {"status": "error", "error": str(e)}
    else:
        summary["platforms"]["instagram"] = {"status": "not_configured"}

    # Twitter (via GetXAPI)
    if GETXAPI_KEY and TWITTER_AUTH_TOKEN:
        try:
            resp = requests.get(
                f"{GETXAPI_BASE}/twitter/user/info",
                params={"auth_token": TWITTER_AUTH_TOKEN},
                headers=_getxapi_headers(),
                timeout=15,
            )
            data = resp.json()
            user = data.get("data", data)
            if user and "error" not in data:
                summary["platforms"]["twitter"] = {
                    "status": "connected",
                    "followers": user.get("followers_count", 0),
                    "following": user.get("friends_count", user.get("following_count", 0)),
                    "tweets": user.get("statuses_count", user.get("tweet_count", 0)),
                }
            else:
                summary["platforms"]["twitter"] = {"status": "error", "error": data.get("error", "Unknown")}
        except Exception as e:
            summary["platforms"]["twitter"] = {"status": "error", "error": str(e)}
    else:
        summary["platforms"]["twitter"] = {"status": "not_configured"}

    configured = sum(1 for p in summary["platforms"].values() if p.get("status") == "connected")
    summary["configured_platforms"] = configured

    log_social_action("ENGAGEMENT_SUMMARY", {"Configured": configured})
    return json.dumps({"status": "success", **summary})


# ─── Run Server ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
