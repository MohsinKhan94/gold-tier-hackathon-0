"""
LinkedIn Poster - Silver Tier
Monitors 'Social_Posts/Approved' folder and automatically posts content to LinkedIn (Simulated).
"""

import time
import os
import shutil
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
SOCIAL_PATH = VAULT_PATH / 'Social_Posts'
APPROVED_PATH = SOCIAL_PATH / 'Approved'
POSTED_PATH = SOCIAL_PATH / 'Posted'
DRAFTS_PATH = SOCIAL_PATH / 'Drafts'

def setup_folders():
    """Ensure social post folders exist"""
    APPROVED_PATH.mkdir(parents=True, exist_ok=True)
    POSTED_PATH.mkdir(parents=True, exist_ok=True)
    DRAFTS_PATH.mkdir(parents=True, exist_ok=True)

def post_to_linkedin(filepath):
    """Simulate posting to LinkedIn API"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simulate API call
        print(f"🚀 Posting to LinkedIn: {filepath.name}...")
        time.sleep(2) # Network delay simulation
        
        # In a real scenario, this would be:
        # response = requests.post('https://api.linkedin.com/v2/ugcPosts', json={...})
        
        print(f"✅ Successfully posted content length: {len(content)}")
        
        # Move to Posted folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"Posted_{timestamp}_{filepath.name}"
        shutil.move(filepath, POSTED_PATH / new_filename)
        
        # Log the action
        log_file = SOCIAL_PATH / "Posting_Log.md"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n- **{datetime.now()}**: Posted `{filepath.name}` to LinkedIn")

    except Exception as e:
        print(f"❌ Error posting {filepath.name}: {e}")

def create_sample_draft():
    """Create a sample draft for the user to approve"""
    draft_file = DRAFTS_PATH / "Sample_Launch_Post.md"
    if not draft_file.exists():
        content = """# 🚀 Launching Our New AI Service!

We are thrilled to announce the launch of our new AI-powered personal assistant. 
It helps you manage your emails, files, and tasks automatically!

#AI #Productivity #Tech #Launch #Startup
"""
        with open(draft_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 Created sample draft: {draft_file.name}")

def main():
    print("="*60)
    print("📢 LINKEDIN POSTER - Silver Tier")
    print("="*60)
    
    setup_folders()
    create_sample_draft()
    
    print(f"📂 Monitoring: {APPROVED_PATH}")
    print(f"✅ Move files from '{DRAFTS_PATH.name}' to '{APPROVED_PATH.name}' to post.")
    print("\nWaiting for approved posts... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            # Check for files in Approved folder
            files = [f for f in APPROVED_PATH.iterdir() if f.is_file()]
            
            for file in files:
                print(f"\n🔔 Found approved post: {file.name}")
                post_to_linkedin(file)
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Poster stopped")

if __name__ == "__main__":
    main()
