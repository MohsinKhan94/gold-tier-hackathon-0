"""
Mock Communication Watcher - Silver Tier
Simulates incoming messages from WhatsApp and LinkedIn to demonstrate multi-channel monitoring.
"""

import time
import random
import os
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'

MOCK_MESSAGES = [
    {
        "source": "WhatsApp",
        "sender": "John Doe (Client)",
        "content": "Hey, can we reschedule our meeting to tomorrow at 2 PM?",
        "priority": "high"
    },
    {
        "source": "LinkedIn",
        "sender": "Recruiter Alice",
        "content": "I saw your profile and I have a great opportunity for you.",
        "priority": "normal"
    },
    {
        "source": "WhatsApp",
        "sender": "Mom",
        "content": "Don't forget to buy milk on your way home.",
        "priority": "low"
    },
    {
        "source": "LinkedIn",
        "sender": "Tech Group",
        "content": "New discussion: AI in 2026. Join us!",
        "priority": "low"
    },
    {
        "source": "WhatsApp",
        "sender": "Project Team",
        "content": "The deployment failed. We need your help ASAP.",
        "priority": "high"
    }
]

def create_alert(message):
    """Create an alert in Obsidian Inbox"""
    inbox_path = VAULT_PATH / "Inbox"
    inbox_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_prefix = message['source'][:2].upper()
    filename = f"{source_prefix}_{timestamp}.md"
    
    priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(message['priority'], "🟡")
    source_emoji = {"WhatsApp": "💬", "LinkedIn": "💼"}.get(message['source'], "📱")
    
    content = f"""
# {source_emoji} {message['source']} Message

{priority_emoji} **Priority:** {message['priority']}

## Details
**From:** {message['sender']}
**Received:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Message
{message['content']}

## Actions
- [ ] Reply
- [ ] Ignore
- [ ] Archive

---
*Detected by Mock Watcher*
"""
    
    filepath = inbox_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created alert: {filename} from {message['source']}")

def main():
    print("="*60)
    print("📱 MOCK COMMUNICATION WATCHER - Silver Tier")
    print("="*60)
    print(f"📁 Vault: {VAULT_PATH}")
    print("\nSimulating incoming messages... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            # Simulate random interval between messages (10-30 seconds for demo purposes)
            sleep_time = random.randint(10, 30)
            time.sleep(sleep_time)
            
            # Pick a random message
            message = random.choice(MOCK_MESSAGES)
            
            print(f"\n🔔 New {message['source']} message detected!")
            create_alert(message)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Mock Watcher stopped")

if __name__ == "__main__":
    main()
