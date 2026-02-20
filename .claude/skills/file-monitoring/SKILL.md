---
name: file-monitoring
description: Monitor the Watch_This_Folder directory for new files and create alerts in the vault Inbox. Use this when you need to process newly dropped files or check the watch folder status.
user-invocable: true
allowed-tools: Read, Write, Glob, Bash(python *), Bash(ls *)
---

# File System Monitoring Skill

Monitor `Watch_This_Folder/` for new files and create structured alerts in `AI_Employee_Vault/Inbox/`.

## How It Works
1. The `file_watcher.py` script runs continuously using Python watchdog
2. When a new file is detected, it creates a markdown alert in `AI_Employee_Vault/Inbox/`
3. The alert includes file metadata (name, size, location, timestamp)

## To Start the File Watcher
```bash
cd ai-employee-watcher && python file_watcher.py
```

## To Process a File Alert
1. Read the alert from `AI_Employee_Vault/Inbox/File_Alert_*.md`
2. Determine the appropriate action based on file type
3. Move the alert to `AI_Employee_Vault/Done/` when processed

## Alert Format
```markdown
# New File Detected
**File:** filename.ext
**Location:** /path/to/file
**Size:** X bytes
**Detected:** YYYY-MM-DD HH:MM:SS

## Action Required
- [ ] Review this file
- [ ] Organize into appropriate folder
- [ ] Update relevant notes
```

## File Type Routing Rules
- PDFs: Flag for document review
- Images: Flag for media processing
- CSV/Excel: Flag for data analysis
- Other: General review
