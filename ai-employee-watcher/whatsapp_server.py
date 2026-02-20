"""
Real WhatsApp Watcher - Silver Tier
Receives real WhatsApp messages via Twilio Webhook.

SETUP:
1. Create a Twilio Account (Free Trial).
2. Activate WhatsApp Sandbox.
3. Install Flask: pip install flask
4. Run this script: python whatsapp_server.py
5. Expose port 5000: ngrok http 5000
6. Add the ngrok URL to Twilio Sandbox Config: https://.../whatsapp
"""

import os
from flask import Flask, request
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
INBOX_PATH = VAULT_PATH / 'Inbox'

@app.route('/whatsapp', methods=['POST'])
def incoming_whatsapp():
    """Handle incoming WhatsApp messages from Twilio"""
    
    # Get message details
    sender = request.values.get('From', '')
    body = request.values.get('Body', '')
    
    print(f"\n\u2690 REAL WhatsApp Message received from {sender}")
    print(f"   Content: {body}")
    
    # Create Obsidian Note
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"WH_REAL_{timestamp}.md"
    
    content = f"""# \ud83d\udcac WhatsApp Message (REAL)

**From:** {sender}
**Received:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Message Content
{body}

---
*Received via Twilio Webhook*
"""
    
    INBOX_PATH.mkdir(exist_ok=True)
    filepath = INBOX_PATH / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\u2705 Created Obsidian alert: {filename}")
    
    return str("Message Received")

if __name__ == "__main__":
    print("\U0001f680 WhatsApp Server Running on Port 5000...")
    print("   Waiting for messages...")
    app.run(port=5000)
