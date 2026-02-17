"""
File System Watcher - Monitors folders for changes
"""

import time
import os
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT_PATH = Path(__file__).parent.parent / 'AI_Employee_Vault'
WATCH_FOLDER = Path(__file__).parent.parent / 'Watch_This_Folder'

class FolderWatcherHandler(FileSystemEventHandler):
    """Handles file system events"""
    
    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return
        
        print(f"\n🔔 New file detected: {event.src_path}")
        self.process_new_file(event.src_path)
    
    def process_new_file(self, filepath):
        """Process newly created file"""
        filepath = Path(filepath)
        
        # Create note in Inbox
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        note_filename = f"File_Alert_{timestamp}.md"
        note_path = VAULT_PATH / "Inbox" / note_filename
        
        content = f"""# 📁 New File Detected

**File:** {filepath.name}
**Location:** {filepath.parent}
**Size:** {filepath.stat().st_size} bytes
**Detected:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Action Required
- [ ] Review this file
- [ ] Organize into appropriate folder
- [ ] Update relevant notes

---
*Detected by File Watcher*
"""
        
        note_path.parent.mkdir(exist_ok=True)
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created inbox note: {note_filename}")

def main():
    """Main watcher loop"""
    # Create watch folder if it doesn't exist
    WATCH_FOLDER.mkdir(exist_ok=True)
    
    print("👁️ File System Watcher Starting...")
    print(f"📁 Watching: {WATCH_FOLDER}")
    print(f"📝 Writing to: {VAULT_PATH / 'Inbox'}")
    print("\nDrop files into 'Watch_This_Folder' to test!")
    print("Press Ctrl+C to stop...\n")
    
    event_handler = FolderWatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Watcher stopped")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()