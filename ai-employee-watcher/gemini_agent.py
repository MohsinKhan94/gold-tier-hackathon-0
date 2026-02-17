"""
Gemini-powered AI Agent for Obsidian Vault - Simple Version
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    with open(env_path, 'r') as f:
        api_key = f.read().strip().replace('GEMINI_API_KEY=', '')

# Vault path
VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'

def read_file(filepath):
    """Read a file from vault"""
    full_path = VAULT_PATH / filepath
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def write_file(filepath, content):
    """Write content to vault"""
    full_path = VAULT_PATH / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Written to: {filepath}")

def list_folder(folder_name):
    """List files in a vault folder"""
    folder_path = VAULT_PATH / folder_name
    if folder_path.exists():
        return [f.name for f in folder_path.iterdir() if f.is_file()]
    return []

def ask_agent(prompt, context=""):
    """Ask Gemini agent a question using REST API"""
    
    full_prompt = f"""You are a Personal AI Employee managing an Obsidian vault.

Vault Path: {VAULT_PATH}

Context:
{context}

Task: {prompt}

Respond concisely and actionably."""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "contents": [{
            "parts": [{
                "text": full_prompt
            }]
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

def update_dashboard(new_tasks=0, emails_processed=0):
    """Update dashboard with new stats"""
    dashboard = read_file("Dashboard.md")
    if dashboard:
        print("📊 Dashboard exists - ready for updates")
    else:
        print("⚠️ Dashboard not found")

if __name__ == "__main__":
    print("🤖 Gemini AI Agent Test\n")
    
    # Test 1: Read Dashboard
    dashboard = read_file("Dashboard.md")
    if dashboard:
        print("✅ Successfully read Dashboard.md")
        print(f"   Length: {len(dashboard)} characters\n")
    
    # Test 2: Read Handbook
    handbook = read_file("Company_Handbook.md")
    if handbook:
        print("✅ Successfully read Company_Handbook.md")
        print(f"   Length: {len(handbook)} characters\n")
    
    # Test 3: List inbox
    inbox_items = list_folder("Inbox")
    print(f"📥 Inbox items: {len(inbox_items)}")
    if inbox_items:
        for item in inbox_items:
            print(f"   - {item}")
    else:
        print("   (empty)\n")
    
    # Test 4: Ask Gemini a question
    print("🧠 Testing Gemini AI...")
    response = ask_agent("What is your role as a Personal AI Employee?")
    print(f"Response: {response}\n")
    
    print("✅ All tests complete!")
