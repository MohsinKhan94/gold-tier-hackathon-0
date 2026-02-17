
### File 2: Create `Skills/file_monitoring.md`

```markdown
# Agent Skill: File System Monitoring

## Status
🟢 Active & Working

## Description
Monitor a designated folder for new files and create alerts in Obsidian Inbox

## Capabilities
- Watch `Watch_This_Folder` directory
- Detect new file creation events
- Extract file metadata (name, size, location)
- Generate structured Inbox notes automatically

## Implementation
**File:** `ai-employee-watcher/file_watcher.py`

**Core Functions:**
- `FolderWatcherHandler.on_created()` - Detects file events
- `process_new_file()` - Processes and logs new files

## Trigger
Continuous monitoring (event-driven)

## Input
Any file dropped into `Watch_This_Folder/`

## Output
Markdown note in `/Inbox/File_Alert_[timestamp].md`

## Dependencies
- Python `watchdog` library
- File system access

## Usage
```bash
# Start the watcher
cd ai-employee-watcher
uv run file_watcher.py