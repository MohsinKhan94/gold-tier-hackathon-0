---
name: vault-operations
description: Read, write, list, and manage files in the AI_Employee_Vault Obsidian vault. Use this skill when you need to interact with the vault filesystem - reading dashboard, creating notes, listing folders, or moving files between Inbox/Needs_Action/Done.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls *), Bash(mkdir *)
---

# Vault Operations Skill

You manage an Obsidian vault at `AI_Employee_Vault/` in the project root.

## Vault Structure
```
AI_Employee_Vault/
  Dashboard.md          # Real-time status overview
  Company_Handbook.md   # Rules of engagement
  SKILLS.md             # Skill documentation
  Plan.md               # Current action plan
  Inbox/                # New items awaiting processing
  Needs_Action/         # Items requiring action
  Done/                 # Completed items
  Social_Posts/         # LinkedIn post workflow
    Drafts/             # Draft posts
    Approved/           # Posts approved for publishing
    Posted/             # Published posts
  Pending_Approval/     # Items awaiting human approval
  Approved/             # Human-approved sensitive actions
  skills/               # Skill documentation files
```

## Operations

### Read a vault file
Read any `.md` file from the vault using the Read tool with path relative to `AI_Employee_Vault/`.

### Write a vault file
Write or update any file in the vault. Always preserve existing frontmatter. Use Write or Edit tools.

### List folder contents
Use Glob tool with pattern `AI_Employee_Vault/<folder>/*.md` to list files.

### Move files between folders
Read the source file, write it to the destination, then delete the source. Log the move in Dashboard.md.

## Rules
- Always use UTF-8 encoding
- Include timestamps in ISO format on created files
- Use YAML frontmatter for metadata on new files
- Never delete files without logging the action
