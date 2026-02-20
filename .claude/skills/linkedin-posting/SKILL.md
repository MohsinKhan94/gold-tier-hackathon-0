---
name: linkedin-posting
description: Create, draft, approve, and post content to LinkedIn for business promotion. Use this skill when creating social media content, managing the post approval workflow, or checking post status.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Bash(python *), Bash(ls *), Bash(cp *), Bash(mv *)
---

# LinkedIn Posting Skill

Manage the full LinkedIn posting workflow: Draft -> Approve -> Post.

## Workflow
1. **Draft**: Create post content in `AI_Employee_Vault/Social_Posts/Drafts/`
2. **Review**: Human reviews the draft
3. **Approve**: Move draft to `AI_Employee_Vault/Social_Posts/Approved/`
4. **Post**: `linkedin_poster.py` detects approved posts and publishes them
5. **Archive**: Posted content moves to `AI_Employee_Vault/Social_Posts/Posted/`

## To Create a Draft Post
Write a markdown file to `AI_Employee_Vault/Social_Posts/Drafts/` with:
```markdown
# Post Title

Post content here. Keep it professional and engaging.
Include relevant hashtags.

#AI #Business #Tech
```

## To Start the LinkedIn Poster
```bash
cd ai-employee-watcher && python linkedin_poster.py
```

## Human-in-the-Loop
Posts require explicit human approval:
1. Draft is created in `Drafts/`
2. Human reviews content
3. Human moves file to `Approved/` to authorize posting
4. System posts and moves to `Posted/`

**No post is ever published without human approval.**

## Post Guidelines
- Keep posts under 3000 characters
- Include 3-5 relevant hashtags
- Professional tone
- Include a call to action
- Avoid controversial topics

## For Real LinkedIn API
Configure `linkedin_real.py` with:
- `LINKEDIN_ACCESS_TOKEN` from LinkedIn Developer Portal
- `LINKEDIN_PERSON_URN` (your LinkedIn user ID)
