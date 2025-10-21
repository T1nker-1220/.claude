# API Usage and Team Integration

Complete guide for using Skills programmatically, sharing with teams, and enterprise deployment.

## Overview

Claude Skills can be accessed through:
- **Messages API** - Include skills in API requests
- **/v1/skills endpoint** - Programmatic skill management
- **Claude Console** - Web-based management
- **Version Control** - Git-based team sharing

---

## Messages API Integration

### Basic Usage

Include skills in your API requests using the `skills` parameter:

```javascript
const response = await anthropic.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: "Process this PDF file"
  }],
  skills: [
    {
      type: "agent_skill",
      skill_id: "pdf-processing",
      version: "1.0.0"  // optional
    }
  ]
});
```

### Multiple Skills

You can include up to **8 skills** per request:

```javascript
skills: [
  { type: "agent_skill", skill_id: "pdf-processing" },
  { type: "agent_skill", skill_id: "brand-guidelines" },
  { type: "agent_skill", skill_id: "typescript-enforcer" },
  // ... up to 8 total
]
```

### Skill Parameters

**Required:**
- `type` - Must be `"agent_skill"`
- `skill_id` - Unique skill identifier (matches `name` in frontmatter)

**Optional:**
- `version` - Specific version to use (defaults to latest)

### Python Example

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Review this TypeScript code"
    }],
    skills=[
        {
            "type": "agent_skill",
            "skill_id": "typescript-enforcer",
            "version": "2.1.0"
        }
    ]
)

print(message.content)
```

### Node.js Example

```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: "Generate API documentation"
  }],
  skills: [{
    type: "agent_skill",
    skill_id: "api-doc-generator"
  }]
});

console.log(message.content);
```

---

## /v1/skills Endpoint

### Overview

The Skills API endpoint provides programmatic control over skill versioning and management.

**Base URL:**
```
https://api.anthropic.com/v1/skills
```

### Create Skill

```http
POST /v1/skills
Content-Type: application/json
x-api-key: your-api-key

{
  "name": "custom-skill",
  "description": "Your skill description",
  "content": "---\nname: custom-skill\n...",
  "version": "1.0.0"
}
```

### List Skills

```http
GET /v1/skills
x-api-key: your-api-key
```

Response:
```json
{
  "skills": [
    {
      "skill_id": "custom-skill",
      "name": "custom-skill",
      "version": "1.0.0",
      "created_at": "2025-10-21T10:00:00Z"
    }
  ]
}
```

### Get Skill Details

```http
GET /v1/skills/{skill_id}
x-api-key: your-api-key
```

### Update Skill

```http
PATCH /v1/skills/{skill_id}
Content-Type: application/json
x-api-key: your-api-key

{
  "version": "1.1.0",
  "content": "updated content..."
}
```

### Delete Skill

```http
DELETE /v1/skills/{skill_id}
x-api-key: your-api-key
```

---

## Team Sharing Strategies

### Strategy 1: Git-Based Sharing (Recommended)

**Project Skills in Version Control:**

```bash
your-project/
├── .claude/
│   └── skills/
│       ├── team-style-guide/
│       │   └── SKILL.md
│       ├── api-patterns/
│       │   └── SKILL.md
│       └── testing-standards/
│           └── SKILL.md
├── src/
└── README.md
```

**Setup:**

1. Create skills in `.claude/skills/`
2. Commit to git:
```bash
git add .claude/skills/
git commit -m "feat(skills): add team coding standards"
git push
```

3. Team members clone/pull:
```bash
git pull origin main
```

4. Skills activate automatically in project

**Benefits:**
- ✅ Version controlled
- ✅ Automatic distribution
- ✅ Code review process applies
- ✅ Git history tracking
- ✅ Branch-specific skills

### Strategy 2: Manual Distribution

**For claude.ai users:**

1. Package skill as ZIP:
```bash
cd ~/.claude/skills/
zip -r my-skill.zip my-skill/
```

2. Share ZIP file with team (email, Slack, etc.)

3. Team members:
   - Download ZIP
   - Upload at claude.ai: Settings > Capabilities > Skills

**Limitations:**
- ❌ Manual updates required
- ❌ No version sync
- ❌ Each user uploads separately

### Strategy 3: API-Based Distribution

**For organizations with API access:**

```javascript
// Deploy skill to all team members
async function deploySkillToTeam(skillContent, teamApiKeys) {
  for (const apiKey of teamApiKeys) {
    const client = new Anthropic({ apiKey });

    await client.skills.create({
      name: "team-skill",
      version: "1.0.0",
      content: skillContent
    });
  }
}
```

**Benefits:**
- ✅ Programmatic deployment
- ✅ Centralized updates
- ✅ Version control

**Use cases:**
- Enterprise deployments
- CI/CD integration
- Automated updates

### Strategy 4: Claude Console (Enterprise)

**For Team/Enterprise plans:**

1. Admin uploads skill to Console
2. Enables for organization
3. All members get access automatically

**Access:** https://console.anthropic.com

---

## Version Management

### Semantic Versioning

Use semver for skill versions:

```
MAJOR.MINOR.PATCH
1.0.0
```

**Examples:**
- `1.0.0` - Initial release
- `1.1.0` - New features, backward compatible
- `1.0.1` - Bug fixes
- `2.0.0` - Breaking changes

### Version in Frontmatter

```yaml
---
name: my-skill
description: Skill description
version: 1.2.3
---
```

### Specifying Versions in API

```javascript
skills: [
  {
    type: "agent_skill",
    skill_id: "my-skill",
    version: "1.2.3"  // specific version
  }
]
```

Omit `version` to use latest:

```javascript
skills: [
  {
    type: "agent_skill",
    skill_id: "my-skill"  // uses latest version
  }
]
```

### Version Changelog

Track changes in `CHANGELOG.md`:

```markdown
# Changelog

## [2.0.0] - 2025-10-21
### Breaking Changes
- Changed response format
- Removed deprecated API

### Added
- New validation rules
- Better error messages

## [1.1.0] - 2025-10-15
### Added
- Support for JSON output
- New examples

### Fixed
- Edge case in date parsing
```

---

## Enterprise Deployment

### Deployment Workflow

**Phase 1: Development**
```
developer-workspace/
└── .claude/skills/new-skill/
    └── SKILL.md
```

Developer creates and tests skill locally.

**Phase 2: Review**
```bash
git checkout -b feature/new-skill
git add .claude/skills/new-skill/
git commit -m "feat(skills): add new skill"
git push origin feature/new-skill
# Create PR for review
```

**Phase 3: Approval & Merge**
```bash
# After PR approval
git checkout main
git merge feature/new-skill
git push origin main
```

**Phase 4: Distribution**
All team members pull changes:
```bash
git pull origin main
# Skills auto-activate in Claude Code
```

### CI/CD Integration

**GitHub Actions Example:**

```yaml
name: Deploy Skills

on:
  push:
    branches: [main]
    paths:
      - '.claude/skills/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate Skills
        run: |
          # Check YAML frontmatter
          python scripts/validate-skills.py

      - name: Deploy to API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Upload to Skills API
          node scripts/deploy-skills.js
```

### Validation Script Example

```python
# scripts/validate-skills.py
import yaml
import os
from pathlib import Path

def validate_skill(skill_path):
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        raise ValueError(f"Missing SKILL.md in {skill_path}")

    content = skill_md.read_text()

    # Extract YAML frontmatter
    if not content.startswith("---"):
        raise ValueError(f"Missing frontmatter in {skill_md}")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {skill_md}")

    metadata = yaml.safe_load(parts[1])

    # Validate required fields
    if "name" not in metadata:
        raise ValueError(f"Missing 'name' in {skill_md}")
    if "description" not in metadata:
        raise ValueError(f"Missing 'description' in {skill_md}")

    print(f"✓ Valid: {skill_path.name}")

skills_dir = Path(".claude/skills")
for skill_path in skills_dir.iterdir():
    if skill_path.is_dir():
        validate_skill(skill_path)
```

---

## Organization-Wide Settings

### For Team/Enterprise Plans

**Admin Requirements:**
1. Admin must enable Skills organization-wide
2. Access: Claude Console > Organization Settings
3. Enable "Skills" capability
4. Set permissions (who can create/modify)

**Permissions Levels:**
- **Admin** - Create, modify, delete all skills
- **Member** - Use approved skills only
- **Custom** - Define specific permissions

### Skill Approval Workflow

```
Developer creates → Review by lead → Admin approves → Deploy to org
```

**Example Policy:**
- All skills must be code-reviewed
- Minimum 2 approvals required
- Security review for sensitive operations
- Version testing before production

---

## Environment-Specific Skills

### Development vs Production

```
.claude/skills/
├── common/              # Used in all environments
│   └── code-style/
├── development/         # Dev-only skills
│   ├── debug-helper/
│   └── mock-data/
└── production/          # Prod-only skills
    ├── monitoring/
    └── alerting/
```

**Load based on environment:**

```javascript
const environment = process.env.NODE_ENV;
const skillsPath = `.claude/skills/${environment}/`;
```

---

## Monitoring and Analytics

### Track Skill Usage

```javascript
// Log skill activations
await anthropic.messages.create({
  // ... message config
  skills: [{ type: "agent_skill", skill_id: "my-skill" }],
  metadata: {
    user_id: "user123",
    session_id: "session456",
    timestamp: new Date().toISOString()
  }
});
```

### Usage Analytics

Track:
- Which skills are used most
- Token consumption per skill
- Error rates
- Response quality

Use for:
- Optimizing frequently-used skills
- Identifying unused skills for removal
- Improving skill descriptions

---

## Cost Management

### Token Costs

Skills consume tokens:
- Frontmatter loading: minimal
- Full content loading: varies by skill size
- Referenced files: only when accessed

**Optimization:**
- Keep SKILL.md under 500 lines
- Use REFERENCE.md for detailed docs
- Split large skills into modules

### Estimation

```javascript
// Rough token estimate
const skillTokens = skillContent.length / 4; // ~4 chars per token
```

**Monitor costs:**
```bash
/cost
```

Shows token usage including skills.

---

## Security Considerations

### Sensitive Information

**Never include in skills:**
- ❌ API keys
- ❌ Passwords
- ❌ Private credentials
- ❌ Secret tokens

**Use environment variables instead:**

```markdown
# In SKILL.md
To authenticate, use the API key from environment variable `API_KEY`.

```javascript
const apiKey = process.env.API_KEY;
```
```

### Access Control

**Project skills:**
- Controlled by git access
- Same permissions as code repository

**Personal skills:**
- Only accessible to individual user
- No sharing mechanism

**API skills:**
- Controlled by API key permissions
- Organization-level access control

---

## Best Practices Summary

**Development:**
- ✅ Use semantic versioning
- ✅ Track changes in CHANGELOG.md
- ✅ Test before deploying
- ✅ Code review skills like code

**Distribution:**
- ✅ Prefer git-based sharing for teams
- ✅ Use API for enterprise deployment
- ✅ Validate before publishing
- ✅ Document dependencies

**Maintenance:**
- ✅ Monitor usage analytics
- ✅ Update regularly
- ✅ Remove unused skills
- ✅ Optimize token usage

---

## Resources

**Official API Docs:**
- Skills Guide: https://docs.claude.com/en/api/skills-guide
- Messages API: https://docs.claude.com/en/api/messages

**GitHub:**
- Official Skills: https://github.com/anthropics/skills
- Cookbooks: https://github.com/anthropics/claude-cookbooks/tree/main/skills

**Console:**
- Claude Console: https://console.anthropic.com

---

*Skills API is available to Pro, Team, and Enterprise users. API access requires valid API key with skills permissions enabled.*
