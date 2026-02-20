# AI Agent Skills Library

This folder contains documentation for the Personal AI Employee's capabilities.

## Claude Code Agent Skills (.claude/skills/)

All AI functionality is implemented as proper Claude Code Agent Skills:

| Skill | Status | Script |
|-------|--------|--------|
| vault-operations | Active | `skills.py` |
| file-monitoring | Active | `file_watcher.py` |
| email-monitoring | Active | `gmail_watcher.py` |
| whatsapp-monitoring | Active | `mock_watcher.py`, `whatsapp_server.py` |
| linkedin-posting | Active | `linkedin_poster.py` |
| plan-generator | Active | `skills.py` |
| dashboard-updater | Active | `skills.py` |
| human-approval | Active | `skills.py` |
| inbox-manager | Active | `skills.py` |

## Legacy Skill Docs (This Folder)

- [vault_operations.md](vault_operations.md) - Core vault read/write operations
- [file_monitoring.md](file_monitoring.md) - File system watcher documentation
- [email_monitoring.md](email_monitoring.md) - Gmail monitoring documentation

## How Skills Work

Each Claude Code Agent Skill is:
1. **Defined** in `.claude/skills/<name>/SKILL.md` (YAML frontmatter + instructions)
2. **Backed by** Python functions in `ai-employee-watcher/skills.py`
3. **Auto-discovered** by Claude Code at startup
4. **Invocable** via `/skill-name` or automatically when context matches

## Adding New Skills

1. Create `.claude/skills/<skill-name>/SKILL.md`
2. Add YAML frontmatter (name, description)
3. Write instructions in markdown body
4. Implement Python backing functions if needed
5. Update SKILLS.md in vault root
