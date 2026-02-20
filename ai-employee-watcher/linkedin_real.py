"""
Real LinkedIn Poster - Silver Tier
Posts content to your actual LinkedIn profile using the Official API.

SETUP:
1. Get an Access Token from https://www.linkedin.com/developers/tools/oauth
   (Select 'w_member_social' scope)
2. Get your Person URN (User ID). You can find this by decoding the token or making a GET /me request.
"""

import os
import time
import requests
import json
from pathlib import Path

# ==============================================================================
# 🔑 CONFIGURATION (PASTE YOUR KEYS HERE)
# ==============================================================================
LINKEDIN_ACCESS_TOKEN = "YOUR_LONG_ACCESS_TOKEN_HERE"
LINKEDIN_PERSON_URN = "urn:li:person:YOUR_ID_HERE"  # e.g., urn:li:person:123456789
# ==============================================================================

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
APPROVED_PATH = VAULT_PATH / 'Social_Posts' / 'Approved'
POSTED_PATH = VAULT_PATH / 'Social_Posts' / 'Posted'

def post_to_linkedin(text_content):
    """
    Posts text to LinkedIn Profile.
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    headers = {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    post_data = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            print("✅ Successfully posted to LinkedIn!")
            print(f"   Post ID: {response.json().get('id')}")
            return True
        else:
            print(f"❌ Failed to post: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def monitor_loop():
    print(f"🔗 Monitoring {APPROVED_PATH} for REAL LinkedIn posts...")
    
    # Ensure folders exist
    APPROVED_PATH.mkdir(parents=True, exist_ok=True)
    POSTED_PATH.mkdir(parents=True, exist_ok=True)
    
    while True:
        # Check for files
        files = [f for f in APPROVED_PATH.iterdir() if f.is_file()]
        
        for file in files:
            print(f"\n🔔 Found approved post: {file.name}")
            
            # Read content
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Attempt Post
            success = post_to_linkedin(content)
            
            if success:
                # Move to Posted
                dest = POSTED_PATH / f"REAL_{file.name}"
                file.rename(dest)
                print(f"📦 Moved to {dest.name}")
        
        time.sleep(10)

if __name__ == "__main__":
    if "YOUR_LONG" in LINKEDIN_ACCESS_TOKEN:
        print("⚠️  PLEASE UPDATE THE CONFIGURATION SECTION WITH YOUR REAL KEYS ⚠️")
    else:
        monitor_loop()
