
### File 3: Create `Skills/vault_operations.md`

```markdown
# Agent Skill: Vault Operations

## Status
🟢 Active & Working

## Description
Core operations for reading and writing to the Obsidian vault

## Capabilities
- Read any file from vault
- Write/update files in vault
- List contents of folders
- Create structured notes

## Implementation
**File:** `ai-employee-watcher/gemini_agent.py`

**Core Functions:**
```python
def read_file(filepath) -> str
    """Read a file from vault"""
    
def write_file(filepath, content) -> None
    """Write content to vault"""
    
def list_folder(folder_name) -> list
    """List files in a vault folder"""
    
def ask_agent(prompt, context="") -> str
    """Query Gemini AI with vault context"""