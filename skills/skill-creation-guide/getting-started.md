# Getting Started with Claude Skills

Complete beginner's guide to creating your first Claude Code skill.

## Prerequisites

**Required:**
- Claude Code installed and authenticated
- Claude Pro, Team, or Enterprise subscription
- Basic understanding of Markdown

**Optional:**
- Git for version control
- Text editor (VS Code, Cursor, etc.)

**Note:** For Team/Enterprise users, admins must enable Skills organization-wide first.

## Two Ways to Create Skills

### Method 1: Interactive Creation (Recommended for Beginners)

Use the built-in `skill-creator` skill for guided creation.

**Step 1: Invoke skill-creator**
```
In Claude Code or claude.ai, simply ask:
"Help me create a new skill using skill-creator"
```

**Step 2: Describe Your Workflow**
Claude will ask about your workflow. Provide detailed explanation:
- What task you want to automate
- When it should be used
- What steps are involved
- Any special requirements

**Example:**
```
"I want a skill that enforces our company's TypeScript
coding standards. It should check for:
- No 'any' types
- Proper interface definitions
- Consistent naming conventions
- JSDoc comments on public functions

Use this when reviewing or writing TypeScript code."
```

**Step 3: Review Generated Files**
Claude creates:
- SKILL.md with proper frontmatter
- Folder structure
- Any scripts or templates needed
- Documentation

**Step 4: Download and Install**
- Claude packages everything as a ZIP file
- Download the ZIP
- Extract to `~/.claude/skills/your-skill-name/`
- Or upload via Claude.ai: Settings > Capabilities > Skills

**Step 5: Activate**
```bash
/reload-skills
```

Skills activate automatically based on context.

---

### Method 2: Manual Creation

For more control or learning purposes.

**Step 1: Create Directory Structure**
```bash
mkdir -p ~/.claude/skills/my-first-skill
cd ~/.claude/skills/my-first-skill
```

**Windows:**
```cmd
mkdir C:\Users\NATH\.claude\skills\my-first-skill
cd C:\Users\NATH\.claude\skills\my-first-skill
```

**Step 2: Create SKILL.md File**

Create `SKILL.md` with this minimal structure:

```markdown
---
name: my-first-skill
description: Brief description of what this skill does and when to use it
---

# My First Skill

## Purpose
[Explain what this skill helps with]

## Instructions
[Step-by-step guidance for Claude]

1. First do this
2. Then do that
3. Finally do this

## Examples
[Show concrete examples]
```

**Step 3: Save and Reload**

Save the file, then reload skills:
```bash
/reload-skills
```

Or restart Claude Code.

---

## Your First Skill: Complete Example

Let's create a "git-commit-helper" skill:

**Directory:**
```
~/.claude/skills/git-commit-helper/
└── SKILL.md
```

**SKILL.md Content:**
```markdown
---
name: git-commit-helper
description: Generate conventional commit messages following best practices. Use when user asks to commit changes or needs help with commit messages.
---

# Git Commit Helper

## Purpose
Generate clear, conventional commit messages following the format:
type(scope): description

## Instructions

When user requests commit message generation:

1. Analyze the staged changes using git diff
2. Identify the change type:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - style: Code style changes
   - refactor: Code refactoring
   - test: Test additions/changes
   - chore: Build/tooling changes

3. Determine the scope (area of codebase affected)

4. Write concise description in imperative mood
   - Good: "add user authentication"
   - Bad: "added user authentication"

5. Format as: type(scope): description

## Examples

**Feature addition:**
```
feat(auth): add JWT token validation
```

**Bug fix:**
```
fix(api): resolve null pointer in user endpoint
```

**Documentation:**
```
docs(readme): update installation instructions
```

## Guidelines

- Keep description under 72 characters
- Use lowercase for type and scope
- No period at end of description
- Be specific but concise
```

---

## Testing Your Skill

**Test 1: Check Installation**
```bash
/reload-skills
```

Look for confirmation that skill was loaded.

**Test 2: Trigger Activation**

Ask Claude something that matches your skill's description:

For git-commit-helper:
```
"I need to commit these changes. Can you help me write a commit message?"
```

**Test 3: Verify Behavior**

Claude should:
1. Recognize the skill is relevant
2. Load the skill instructions
3. Follow the guidelines in SKILL.md

**Debugging Tips:**
- Skill not activating? Check the description field
- Make description specific about WHEN to use it
- Include keywords user might mention
- Be explicit about use cases

---

## Installation Locations

### Personal Skills (Your Use Only)
```
~/.claude/skills/
├── skill-one/
│   └── SKILL.md
└── skill-two/
    └── SKILL.md
```

Available across ALL your projects.

### Project Skills (Team Shared)
```
/your-project/.claude/skills/
├── project-skill-one/
│   └── SKILL.md
└── project-skill-two/
    └── SKILL.md
```

Shared via git commits with your team.

---

## Quick Commands

**Reload skills after changes:**
```bash
/reload-skills
```

**Check Claude Code version:**
```bash
claude --version
```

**View installed plugins:**
```bash
/plugins
```

---

## Next Steps After Your First Skill

1. ✅ **Created your first skill**
2. **Learn advanced structure:** See `structure.md`
3. **Add supplemental content:** Use REFERENCE.md for detailed info
4. **Optimize performance:** Read `best-practices.md`
5. **Share with team:** Check `api-usage.md`
6. **Browse examples:** Review `examples.md`

---

## Common First-Time Issues

**Skill not loading?**
- Check YAML frontmatter format (three dashes `---`)
- Ensure name has no spaces (use hyphens)
- Verify file is named exactly `SKILL.md` (all caps)

**Skill not activating?**
- Make description more specific
- Include keywords from user prompts
- Mention WHEN to use the skill in description

**Changes not applying?**
- Run `/reload-skills`
- Or restart Claude Code completely

**YAML parsing error?**
- Check for proper indentation (spaces, not tabs)
- Ensure closing `---` after frontmatter
- No special characters in name field

---

## Availability

**Skills are available to:**
- ✅ Claude Pro users
- ✅ Claude Team users
- ✅ Claude Enterprise users
- ❌ Free tier users

**Platforms:**
- ✅ Claude.ai web interface
- ✅ Claude Code CLI
- ✅ Claude API

---

## Resources

**Official:**
- GitHub Examples: https://github.com/anthropics/skills
- Official Docs: https://docs.claude.com/en/docs/claude-code/skills
- API Guide: https://docs.claude.com/en/api/skills-guide

**Community:**
- Awesome Claude Skills: https://github.com/travisvn/awesome-claude-skills
- Skills Collection: https://github.com/abubakarsiddik31/claude-skills-collection

---

*Pro Tip: Start simple! Your first skill doesn't need to be complex. A basic SKILL.md with clear instructions is often enough to see significant productivity gains.*
