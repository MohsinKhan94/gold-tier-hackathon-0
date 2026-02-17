
### File 4: Create `Skills/README.md`

```markdown
# AI Agent Skills Library

This folder contains all documented skills (capabilities) of your Personal AI Employee.

## Active Skills (Bronze Tier)

### 🟢 Vault Operations
Core read/write operations for Obsidian vault
- **File:** [vault_operations.md](vault_operations.md)
- **Script:** `gemini_agent.py`

### 🟢 File System Monitoring
Watch folders for new files and create alerts
- **File:** [file_monitoring.md](file_monitoring.md)
- **Script:** `file_watcher.py`

### 🟡 Email Monitoring (Planned)
Monitor Gmail and process emails
- **File:** [email_monitoring.md](email_monitoring.md)
- **Script:** `gmail_watcher.py` (future)

## How Skills Work

Each skill is:
1. **Documented** in a `.md` file (this folder)
2. **Implemented** as Python code (`ai-employee-watcher/`)
3. **Callable** by Claude Code or other scripts

## Adding New Skills

To add a new skill:
1. Create `SkillName.md` in this folder
2. Implement the Python code
3. Test it works
4. Document usage examples
5. Update this README

## Skill Status Indicators
- 🟢 Active & Working
- 🟡 Planned / In Progress
- 🔴 Broken / Needs Fix
- ⚪ Deprecated