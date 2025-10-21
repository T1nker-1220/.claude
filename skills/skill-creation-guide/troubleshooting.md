# Troubleshooting Claude Skills

Complete guide for diagnosing and resolving common skill issues.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Activation Problems](#activation-problems)
3. [Loading Errors](#loading-errors)
4. [Performance Issues](#performance-issues)
5. [Integration Problems](#integration-problems)
6. [Debugging Techniques](#debugging-techniques)

---

## Installation Issues

### Skill Not Found After Installation

**Symptom:** Skill directory exists but Claude doesn't recognize it.

**Diagnosis:**
```bash
# Check directory location
ls -la ~/.claude/skills/

# Windows
dir C:\Users\[USERNAME]\.claude\skills\
```

**Solution 1: Verify File Name**
- File must be named exactly `SKILL.md` (all caps)
- Not `skill.md`, `Skill.md`, or `SKILL.MD`

**Solution 2: Reload Skills**
```bash
/reload-skills
```

Or restart Claude Code:
```bash
# Exit and restart
exit
claude
```

**Solution 3: Check Permissions**
```bash
# Ensure read permissions
chmod +r ~/.claude/skills/my-skill/SKILL.md

# Windows: Right-click > Properties > Security
```

---

### YAML Parsing Error

**Symptom:**
```
Error: Failed to parse SKILL.md frontmatter
```

**Common Causes:**

**Cause 1: Missing Dashes**
```yaml
❌ Incorrect:
name: my-skill
description: My description
---

✅ Correct:
---
name: my-skill
description: My description
---
```

**Cause 2: Tabs Instead of Spaces**
```yaml
❌ Incorrect (tabs):
---
name:	my-skill
description:	Description
---

✅ Correct (spaces):
---
name: my-skill
description: Description
---
```

**Cause 3: Special Characters**
```yaml
❌ Incorrect:
name: my-skill's-name
description: Using "quotes" incorrectly

✅ Correct:
name: my-skill-name
description: Using quotes correctly or avoiding them
```

**Solution:**
1. Use a YAML validator: https://www.yamllint.com/
2. Check indentation (use spaces, not tabs)
3. Escape special characters
4. Ensure three dashes `---` top and bottom

---

### Permission Denied Errors

**Symptom:**
```
Error: EACCES: permission denied
```

**Solution for macOS/Linux:**
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/.claude/skills/

# Fix permissions
chmod -R u+rw ~/.claude/skills/
```

**Solution for Windows:**
1. Right-click skill folder
2. Properties > Security
3. Edit > Add your user account
4. Grant "Read" and "Write" permissions

---

## Activation Problems

### Skill Never Activates

**Symptom:** Skill installed correctly but Claude never uses it.

**Diagnosis Checklist:**

1. **Check description field:**
   - Is it specific enough?
   - Does it include trigger keywords?
   - Does it mention when to use?

2. **Test description:**
```yaml
❌ Poor:
description: Helps with coding

✅ Better:
description: Enforce TypeScript type safety rules. Use when writing or reviewing TypeScript code.
```

**Solution 1: Improve Description**

Add explicit triggers:
```yaml
description: [What it does]. Use when [scenario 1], [scenario 2], or when user mentions [keyword 1], [keyword 2].
```

**Solution 2: Test Activation**

Ask Claude questions that should trigger the skill:

For a git-commit skill:
```
"Help me write a commit message"
"I need to commit changes"
"Generate git commit"
```

If skill still doesn't activate, description needs improvement.

**Solution 3: Reduce Competition**

Too many similar skills? Claude might choose another.

Check:
```bash
ls ~/.claude/skills/
```

Disable conflicting skills temporarily:
```bash
mv ~/.claude/skills/old-skill ~/.claude/skills/.old-skill
/reload-skills
```

Hidden skills (starting with `.`) are ignored.

---

### Wrong Skill Activates

**Symptom:** Claude uses different skill than intended.

**Cause:** Multiple skills have similar descriptions.

**Solution:**

Make descriptions more specific:

```yaml
❌ Too generic:
name: code-helper
description: Helps with code

name: typescript-helper
description: Helps with TypeScript

✅ Specific:
name: code-reviewer
description: Perform code reviews checking for security, performance, and best practices. Use when reviewing pull requests or code quality.

name: typescript-enforcer
description: Enforce TypeScript strict type safety and naming conventions. Use when writing new TypeScript code or refactoring existing code.
```

---

### Skill Activates Too Often

**Symptom:** Skill triggers when it shouldn't.

**Cause:** Description too broad or includes common keywords.

**Solution:**

Narrow the description:

```yaml
❌ Too broad:
description: Work with files and documents

✅ Specific:
description: Extract text from PDF files and fill PDF forms. Use specifically when working with PDF documents or when user explicitly mentions PDFs.
```

---

## Loading Errors

### "Failed to Load SKILL.md"

**Symptom:**
```
Error: Failed to load SKILL.md
```

**Diagnosis:**

1. **Check file encoding:**
```bash
file ~/.claude/skills/my-skill/SKILL.md
```

Should be: `UTF-8 Unicode text`

**Solution:**
Convert to UTF-8:
```bash
iconv -f ISO-8859-1 -t UTF-8 SKILL.md > SKILL_UTF8.md
mv SKILL_UTF8.md SKILL.md
```

2. **Check file size:**
```bash
du -h ~/.claude/skills/my-skill/SKILL.md
```

Very large files (>10MB) may cause issues.

**Solution:** Split into smaller files.

3. **Check for corrupted file:**
```bash
cat SKILL.md
```

If garbled output, file is corrupted.

**Solution:** Restore from backup or recreate.

---

### Referenced Files Not Loading

**Symptom:** SKILL.md loads but REFERENCE.md doesn't.

**Diagnosis:**

Check reference in SKILL.md:

```markdown
❌ Incorrect:
See reference.md for details

✅ Correct:
See `REFERENCE.md` for details
```

**Solution:**

1. Use exact filename in backticks
2. Ensure file exists:
```bash
ls -la ~/.claude/skills/my-skill/
```

3. Check file permissions:
```bash
chmod +r ~/.claude/skills/my-skill/REFERENCE.md
```

---

### Script Execution Errors

**Symptom:**
```
Error: Script failed to execute
```

**Diagnosis:**

1. **Check script permissions:**
```bash
ls -la ~/.claude/skills/my-skill/scripts/
```

**Solution:**
```bash
chmod +x ~/.claude/skills/my-skill/scripts/helper.py
```

2. **Check interpreter:**
```python
#!/usr/bin/env python3
```

**Solution:** Add shebang line at top of script.

3. **Check dependencies:**
```bash
python3 -c "import required_module"
```

**Solution:** Install missing dependencies:
```bash
pip install required_module
```

---

## Performance Issues

### Slow Skill Loading

**Symptom:** Long delay when skill activates.

**Diagnosis:**

Check skill size:
```bash
du -sh ~/.claude/skills/my-skill/
```

**Solution:**

1. **Split large SKILL.md:**
```
Before: SKILL.md (2000 lines)
After:  SKILL.md (300 lines)
        REFERENCE.md (1700 lines)
```

2. **Remove unnecessary content:**
- Delete redundant examples
- Move rarely-used info to REFERENCE.md
- Optimize images and assets

3. **Use progressive disclosure:**
```markdown
# Core instructions here (always loaded)

## Advanced Usage
For advanced patterns, see `advanced.md`
```

---

### High Token Usage

**Symptom:** Skills consuming too many tokens.

**Diagnosis:**
```bash
/cost
```

Check token usage statistics.

**Solution:**

1. **Reduce SKILL.md size:**
   - Target: < 500 lines
   - Move details to REFERENCE.md

2. **Remove verbose examples:**
```markdown
❌ Verbose:
Here is a very detailed example that explains every single
step in great detail with lots of explanation...

✅ Concise:
Example:
```python
result = process(data)
```
```

3. **Use context-specific files:**
```
skill/
├── SKILL.md       (core)
├── windows.md     (load only on Windows)
├── macos.md       (load only on macOS)
└── linux.md       (load only on Linux)
```

---

### Skill Conflicts

**Symptom:** Multiple skills trying to handle same request.

**Diagnosis:**

List all skills:
```bash
ls -la ~/.claude/skills/
```

Check descriptions for overlap.

**Solution:**

1. **Make descriptions distinct:**
```yaml
Skill A:
description: Generate unit tests for functions and classes

Skill B:
description: Generate integration tests for API endpoints

(Previously both said "generate tests")
```

2. **Disable conflicting skills:**
```bash
# Temporarily disable
mv ~/.claude/skills/conflict-skill ~/.claude/skills/.conflict-skill
/reload-skills
```

3. **Merge related skills:**

Combine two similar skills into one comprehensive skill.

---

## Integration Problems

### API Integration Failures

**Symptom:**
```
Error: Skill not found in API request
```

**Diagnosis:**

Check skill_id matches exactly:

```javascript
❌ Incorrect:
skills: [
  { type: "agent_skill", skill_id: "My-Skill" }
]

✅ Correct:
skills: [
  { type: "agent_skill", skill_id: "my-skill" }
]
```

**Solution:**

1. Use exact `name` from frontmatter
2. Lowercase, hyphens only
3. No spaces or special characters

---

### Version Mismatch

**Symptom:**
```
Error: Skill version 2.0.0 not found
```

**Diagnosis:**

Check available versions:
```bash
grep "version:" ~/.claude/skills/my-skill/SKILL.md
```

**Solution:**

1. **Update version in frontmatter:**
```yaml
---
name: my-skill
version: 2.0.0  # Must match API request
---
```

2. **Or remove version from API request:**
```javascript
skills: [
  { type: "agent_skill", skill_id: "my-skill" }
  // No version = use latest
]
```

---

### Git Sync Issues

**Symptom:** Team members don't have latest skill version.

**Diagnosis:**

Check git status:
```bash
git status .claude/skills/
```

**Solution:**

1. **Ensure skills are committed:**
```bash
git add .claude/skills/
git commit -m "feat(skills): update skill"
git push origin main
```

2. **Team pulls changes:**
```bash
git pull origin main
/reload-skills
```

3. **Check .gitignore:**
Ensure `.claude/skills/` is NOT ignored:
```bash
# .gitignore should NOT contain:
# .claude/skills/  ❌
```

---

## Debugging Techniques

### Enable Verbose Logging

**Claude Code:**
```bash
claude --verbose
```

Shows detailed information about skill loading.

**API:**
```javascript
const response = await anthropic.messages.create({
  // ... config
  debug: true
});
```

---

### Validate SKILL.md

**Manual Check:**

1. **YAML frontmatter valid?**
   - Three dashes top and bottom
   - name and description present
   - Proper spacing (not tabs)

2. **File encoding UTF-8?**
```bash
file SKILL.md
```

3. **Markdown syntax correct?**
   - Headers use #
   - Code blocks have closing ```
   - Lists properly formatted

**Automated Validation:**

```python
# validate_skill.py
import yaml
from pathlib import Path

def validate_skill(skill_path):
    skill_md = Path(skill_path) / "SKILL.md"

    # Check exists
    if not skill_md.exists():
        print(f"❌ Missing SKILL.md in {skill_path}")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter
    if not content.startswith("---"):
        print(f"❌ Missing frontmatter in {skill_md}")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"❌ Invalid frontmatter structure")
        return False

    # Parse YAML
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False

    # Check required fields
    if "name" not in metadata:
        print(f"❌ Missing 'name' field")
        return False

    if "description" not in metadata:
        print(f"❌ Missing 'description' field")
        return False

    # Check name format
    if " " in metadata["name"]:
        print(f"❌ Name contains spaces: {metadata['name']}")
        return False

    print(f"✅ Valid: {skill_path}")
    return True

# Run validation
validate_skill("~/.claude/skills/my-skill")
```

---

### Test Skill Activation

**Create test script:**

```javascript
// test_skill.js
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function testSkill(skillId, testPrompt) {
  console.log(`Testing skill: ${skillId}`);
  console.log(`Prompt: ${testPrompt}\n`);

  const response = await client.messages.create({
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 1024,
    messages: [{
      role: "user",
      content: testPrompt
    }],
    skills: [{
      type: "agent_skill",
      skill_id: skillId
    }]
  });

  console.log("Response:", response.content[0].text);
}

// Test
testSkill("git-commit-helper", "Help me write a commit message");
```

---

### Check Skill Discovery

**Verify Claude can see skill:**

Ask Claude:
```
"What skills do you have available?"
```

Claude should list your custom skills.

---

### Inspect Token Usage

**Monitor costs:**
```bash
/cost
```

Shows:
- Total tokens used
- Token breakdown
- Cost estimates

**Identify expensive skills:**

Test with and without skill:
```javascript
// Without skill
const response1 = await anthropic.messages.create({
  // ... no skills
});

// With skill
const response2 = await anthropic.messages.create({
  skills: [{ type: "agent_skill", skill_id: "my-skill" }]
});

console.log("Token difference:",
  response2.usage.total_tokens - response1.usage.total_tokens);
```

---

## Common Error Messages

### "Authentication Error"

**Cause:** Invalid or missing API key

**Solution:**
```bash
# Set API key
export ANTHROPIC_API_KEY=your-api-key

# Or in .env file
echo "ANTHROPIC_API_KEY=your-api-key" > .env
```

---

### "Skill Not Enabled"

**Cause:** Skills not enabled for organization (Team/Enterprise)

**Solution:**
Admin must enable in Claude Console:
1. Go to console.anthropic.com
2. Organization Settings
3. Enable "Skills" capability

---

### "Rate Limit Exceeded"

**Cause:** Too many API requests

**Solution:**
1. Implement rate limiting
2. Use exponential backoff
3. Reduce request frequency

```javascript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw error;
    }
  }
}
```

---

## Getting Help

### Official Resources

1. **Documentation:**
   - https://docs.claude.com/en/docs/claude-code/skills
   - https://docs.claude.com/en/api/skills-guide

2. **GitHub Issues:**
   - https://github.com/anthropics/skills/issues

3. **Community:**
   - Claude Discord
   - GitHub Discussions

### Reporting Bugs

**Include in bug report:**

1. **Skill configuration:**
```yaml
# SKILL.md frontmatter
---
name: my-skill
description: My description
version: 1.0.0
---
```

2. **Error message:**
```
Full error output here
```

3. **Steps to reproduce:**
```
1. Create skill with...
2. Try to activate by...
3. Observe error...
```

4. **Environment:**
```
OS: macOS 14.0
Claude Code version: 1.2.3
Node.js: 18.0.0
```

---

## Quick Troubleshooting Checklist

When something goes wrong:

- [ ] Run `/reload-skills`
- [ ] Check YAML frontmatter syntax
- [ ] Verify `name` and `description` fields present
- [ ] Ensure SKILL.md is UTF-8 encoded
- [ ] Test with simple description
- [ ] Check file permissions
- [ ] Restart Claude Code
- [ ] Review error logs
- [ ] Test skill in isolation
- [ ] Validate with script
- [ ] Check official documentation

---

*Most issues can be resolved by reloading skills, checking YAML syntax, or improving the description field.*
