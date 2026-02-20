"""
Gmail MCP Server - Silver Tier
Exposes Gmail actions (send, draft, search, list) as MCP tools for Claude Code.
Uses existing OAuth2 credentials from gmail_watcher.py.
"""

import pickle
import base64
import json
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

# Gmail API scopes (gmail.modify covers sending)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

# Paths
SCRIPT_DIR = Path(__file__).parent
VAULT_PATH = SCRIPT_DIR.parent / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "gmail_token.pickle"

# Ensure logs directory exists
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Initialize MCP server
mcp = FastMCP("gmail", instructions="Gmail MCP server for sending, drafting, and searching emails via Gmail API.")


def get_gmail_service():
    """Authenticate and return Gmail API service. Reuses existing token."""
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Download from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def log_action(action: str, details: dict):
    """Log email actions to the vault for audit trail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"email_actions_{date_str}.md"

    entry = f"\n## [{timestamp}] {action}\n"
    for key, value in details.items():
        entry += f"- **{key}:** {value}\n"
    entry += "---\n"

    if not log_file.exists():
        header = f"# Email Action Log - {date_str}\n\nAll email actions performed via Gmail MCP Server.\n\n---\n"
        log_file.write_text(header + entry, encoding="utf-8")
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)


@mcp.tool()
def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text)
        cc: CC recipients (comma-separated, optional)
        bcc: BCC recipients (comma-separated, optional)

    Returns:
        JSON string with message ID and status
    """
    service = get_gmail_service()

    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    sent = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    log_action("SEND_EMAIL", {
        "To": to,
        "Subject": subject,
        "CC": cc or "None",
        "Message ID": sent["id"],
        "Status": "Sent",
    })

    return json.dumps({
        "status": "sent",
        "message_id": sent["id"],
        "to": to,
        "subject": subject,
    })


@mcp.tool()
def draft_email(to: str, subject: str, body: str) -> str:
    """Create an email draft in Gmail (does not send).

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text)

    Returns:
        JSON string with draft ID and status
    """
    service = get_gmail_service()

    message = MIMEText(body, "plain")
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()

    log_action("DRAFT_EMAIL", {
        "To": to,
        "Subject": subject,
        "Draft ID": draft["id"],
        "Status": "Draft created",
    })

    return json.dumps({
        "status": "draft_created",
        "draft_id": draft["id"],
        "to": to,
        "subject": subject,
    })


@mcp.tool()
def search_emails(query: str, max_results: int = 5) -> str:
    """Search Gmail with a query string.

    Args:
        query: Gmail search query (e.g. 'from:boss@company.com is:unread', 'subject:invoice')
        max_results: Maximum number of results to return (default 5, max 20)

    Returns:
        JSON string with list of matching emails (id, from, subject, date, snippet)
    """
    service = get_gmail_service()
    max_results = min(max_results, 20)

    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}

        emails.append({
            "id": msg["id"],
            "from": headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No Subject"),
            "date": headers.get("Date", "Unknown"),
            "snippet": detail.get("snippet", ""),
        })

    log_action("SEARCH_EMAILS", {
        "Query": query,
        "Results found": str(len(emails)),
    })

    return json.dumps({"query": query, "count": len(emails), "emails": emails})


@mcp.tool()
def list_recent_emails(max_results: int = 10) -> str:
    """List recent unread emails from Gmail inbox.

    Args:
        max_results: Maximum number of emails to return (default 10, max 20)

    Returns:
        JSON string with list of recent unread emails
    """
    return search_emails(query="is:unread", max_results=max_results)


if __name__ == "__main__":
    mcp.run(transport="stdio")
