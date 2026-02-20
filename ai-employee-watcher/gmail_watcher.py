"""
Gmail Watcher - Silver Tier
Monitors Gmail inbox and creates intelligent alerts using Gemini AI
"""

import os
import pickle
import time
from datetime import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import base64
from email.utils import parsedate_to_datetime

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']

# Paths
VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'
TOKEN_FILE = Path(__file__).parent / 'gmail_token.pickle'

# Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY'):
                    GEMINI_API_KEY = line.split('=')[1].strip()

def authenticate_gmail():
    """Authenticate with Gmail API"""
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ credentials.json not found!")
                print("   Download from Google Cloud Console")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_email_body(payload):
    """Extract email body from payload"""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    # Fallback to body data
    data = payload['body'].get('data', '')
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    return "No body content"

def analyze_email_with_gemini(sender, subject, body_preview):
    """Use Gemini to analyze email and categorize it"""
    
    prompt = f"""Analyze this email and provide:
1. Category (VIP, Action Required, Newsletter, Spam, Info)
2. Priority (High, Medium, Low)
3. One-sentence summary
4. Suggested action

Email:
From: {sender}
Subject: {subject}
Preview: {body_preview[:300]}

Respond in this exact format:
Category: [category]
Priority: [priority]
Summary: [one sentence]
Action: [what to do]"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            return parse_gemini_response(text)
        else:
            return default_analysis()
    except Exception as e:
        print(f"⚠️ Gemini analysis failed: {e}")
        return default_analysis()

def parse_gemini_response(text):
    """Parse Gemini's structured response"""
    lines = text.strip().split('\n')
    analysis = {
        'category': 'Info',
        'priority': 'Medium',
        'summary': 'New email received',
        'action': 'Review and respond if needed'
    }
    
    for line in lines:
        if line.startswith('Category:'):
            analysis['category'] = line.split(':', 1)[1].strip()
        elif line.startswith('Priority:'):
            analysis['priority'] = line.split(':', 1)[1].strip()
        elif line.startswith('Summary:'):
            analysis['summary'] = line.split(':', 1)[1].strip()
        elif line.startswith('Action:'):
            analysis['action'] = line.split(':', 1)[1].strip()
    
    return analysis

def default_analysis():
    """Default analysis if Gemini fails"""
    return {
        'category': 'Info',
        'priority': 'Medium',
        'summary': 'New email received',
        'action': 'Review email content'
    }

def create_email_alert(email_data, analysis):
    """Create intelligent email alert in Obsidian"""
    inbox_path = VAULT_PATH / "Inbox"
    inbox_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Email_{timestamp}_{email_data['id'][:8]}.md"
    
    # Priority emoji
    priority_emoji = {
        'High': '🔴',
        'Medium': '🟡',
        'Low': '🟢'
    }.get(analysis['priority'], '🟡')
    
    # Category emoji
    category_emoji = {
        'VIP': '⭐',
        'Action Required': '⚡',
        'Newsletter': '📰',
        'Spam': '🗑️',
        'Info': '📧'
    }.get(analysis['category'], '📧')
    
    content = f"""# {category_emoji} {analysis['category']} - {email_data['subject'][:50]}

{priority_emoji} **Priority:** {analysis['priority']}

## Email Details
**From:** {email_data['from']}
**Subject:** {email_data['subject']}
**Received:** {email_data['date']}
**Gmail ID:** {email_data['id']}

## AI Analysis
**Summary:** {analysis['summary']}

**Suggested Action:** {analysis['action']}

## Email Preview
{email_data['body_preview'][:500]}
{'...' if len(email_data['body_preview']) > 500 else ''}

## Actions
- [ ] {analysis['action']}
- [ ] Reply if needed
- [ ] Archive or Delete

## Links
[Open in Gmail](https://mail.google.com/mail/u/0/#inbox/{email_data['id']})

---
*AI-Analyzed by Gmail Watcher + Gemini • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    filepath = inbox_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filename}")
    print(f"   Category: {analysis['category']} | Priority: {analysis['priority']}")
    return filename

def get_recent_emails(service, max_results=10):
    """Fetch recent unread emails"""
    try:
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []

def get_email_details(service, msg_id):
    """Get full email details"""
    try:
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        # Get body
        body = get_email_body(message['payload'])
        
        # Parse date
        date_str = headers.get('Date', '')
        try:
            date_obj = parsedate_to_datetime(date_str)
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_date = date_str
        
        return {
            'id': msg_id,
            'from': headers.get('From', 'Unknown'),
            'subject': headers.get('Subject', 'No Subject'),
            'date': formatted_date,
            'body': body,
            'body_preview': body[:1000]
        }
    except Exception as e:
        print(f"❌ Error getting email details: {e}")
        return None

def main():
    """Main Gmail watcher loop"""
    print("="*60)
    print("📧 GMAIL WATCHER - Silver Tier")
    print("="*60)
    print(f"🔐 Authenticating with Gmail...")
    
    service = authenticate_gmail()
    if not service:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Gmail authenticated successfully")
    print(f"📁 Vault: {VAULT_PATH}")
    print(f"🤖 AI: Gemini API {'✅' if GEMINI_API_KEY else '❌'}")
    print("\n👁️ Monitoring Gmail (Press Ctrl+C to stop)...\n")
    
    processed_ids = set()
    check_interval = 60  # Check every 60 seconds
    
    while True:
        try:
            messages = get_recent_emails(service, max_results=5)
            
            new_count = 0
            for msg in messages:
                msg_id = msg['id']
                
                if msg_id not in processed_ids:
                    print(f"\n🔔 New email detected: {msg_id[:8]}...")
                    
                    # Get email details
                    email_data = get_email_details(service, msg_id)
                    if not email_data:
                        continue
                    
                    print(f"   From: {email_data['from'][:50]}")
                    print(f"   Subject: {email_data['subject'][:50]}")
                    
                    # Analyze with Gemini
                    print(f"   🤖 Analyzing with Gemini...")
                    analysis = analyze_email_with_gemini(
                        email_data['from'],
                        email_data['subject'],
                        email_data['body_preview']
                    )
                    
                    # Create alert
                    create_email_alert(email_data, analysis)
                    
                    processed_ids.add(msg_id)
                    new_count += 1
            
            if new_count > 0:
                print(f"\n📊 Processed {new_count} new email(s)")
            
            # Wait before next check
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Gmail Watcher stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(check_interval)

if __name__ == "__main__":
    main()