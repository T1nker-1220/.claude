# Best Practices for Claude Skills

Comprehensive guide for optimization, performance, security, and maintainability.

## Table of Contents

1. [Token Optimization](#token-optimization)
2. [Description Writing](#description-writing)
3. [Performance Optimization](#performance-optimization)
4. [Security Guidelines](#security-guidelines)
5. [Maintenance and Updates](#maintenance-and-updates)
6. [Team Collaboration](#team-collaboration)

---

## Token Optimization

### Why Token Efficiency Matters

- Reduces costs (tokens = money)
- Faster response times
- Better context management
- Scales to multiple skills

### Progressive Disclosure Architecture

**Concept:** Load only what's needed, when it's needed.

**Implementation:**

```
skill/
├── SKILL.md           # Core instructions (always loaded)
├── REFERENCE.md       # Detailed specs (loaded on demand)
└── advanced.md        # Rare cases (loaded when mentioned)
```

**SKILL.md (concise):**
```markdown
# My Skill

## Basic Usage
[Essential instructions - 200 lines]

## Advanced Features
For complex scenarios, see `advanced.md`

## Complete Reference
For full API docs, see `REFERENCE.md`
```

**Token Savings:**
- Without split: 1000 tokens loaded every time
- With split: 200 tokens normally, 1000 only when needed
- **Savings: 80% reduction** in typical use

### Size Guidelines

**Target Sizes:**
- SKILL.md: < 500 lines
- REFERENCE.md: Unlimited
- Supplemental files: As needed

**When to Split:**
```
< 200 lines    → Single file OK
200-500 lines  → Consider REFERENCE.md
> 500 lines    → Required: Split into modules
```

### Content Prioritization

**High Priority (in SKILL.md):**
- ✅ Common use cases (80% of usage)
- ✅ Quick reference
- ✅ Essential guidelines
- ✅ Frequently used examples

**Low Priority (in REFERENCE.md):**
- ⏬ Complete API documentation
- ⏬ Edge cases
- ⏬ Detailed technical specs
- ⏬ Rarely-used features

### Conditional Loading

**Context-Specific Files:**

```
skill/
├── SKILL.md
├── windows.md
├── macos.md
└── linux.md
```

Load only OS-relevant file → 66% token savings.

**Language-Specific:**

```
skill/
├── SKILL.md
├── typescript.md
├── python.md
└── rust.md
```

Load only relevant language → 75% token savings.

### Measuring Token Usage

**Rough Estimate:**
```
tokens ≈ characters / 4
```

**Example:**
- 2000 characters = ~500 tokens
- 10,000 characters = ~2500 tokens

**Check actual usage:**
```bash
/cost
```

Shows token consumption including skills.

### Optimization Checklist

- [ ] SKILL.md under 500 lines
- [ ] Supplemental content in separate files
- [ ] No duplicate information
- [ ] Examples are concise but complete
- [ ] Referenced files mentioned explicitly
- [ ] Tested token usage with /cost

---

## Description Writing

### Critical Importance

The `description` field determines:
- When skill activates
- Discoverability
- Relevance matching

**Impact:**
- Good description = automatic activation
- Poor description = skill never used

### Formula for Effective Descriptions

```
[What it does] + [When to use it] + [Keywords]
```

### Examples

**Excellent Description:**
```yaml
description: Generate conventional commit messages following type(scope): description format. Use when user asks to commit changes, needs help with git commit messages, or mentions git commits.
```

**Why it works:**
- ✅ Clear what it does (generate commit messages)
- ✅ Specific when to use (commit changes, git help)
- ✅ Keywords (git, commit, messages)

**Poor Description:**
```yaml
description: Helps with git
```

**Why it fails:**
- ❌ Too vague
- ❌ No activation triggers
- ❌ Missing keywords

### Description Template

```yaml
description: [Action verb] [specific output] [following pattern/standard]. Use when [user scenario 1], [user scenario 2], or when user mentions [keyword 1], [keyword 2], [keyword 3].
```

### More Examples

**PDF Processing:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Brand Guidelines:**
```yaml
description: Apply company brand guidelines including colors, fonts, logo usage, and spacing. Use when creating presentations, documents, or any branded materials.
```

**TypeScript Enforcer:**
```yaml
description: Enforce TypeScript best practices including strict type safety, no 'any' types, proper interfaces, and naming conventions. Use when writing or reviewing TypeScript code.
```

### Keywords to Include

**Trigger Words:**
- Actions: create, generate, validate, check, review, analyze
- Tools: git, PDF, Excel, TypeScript, API, database
- Objects: commit, document, spreadsheet, code, tests
- Scenarios: debugging, reviewing, creating, editing

### Testing Descriptions

**Method 1: Activation Test**

Ask Claude:
```
"I need to commit these changes"
```

Does your git skill activate? If not, improve description.

**Method 2: Keyword Test**

List keywords users might say:
- commit
- git message
- commit message
- git commit

Include all variations in description.

### Common Mistakes

**Too Generic:**
```yaml
❌ description: Helps with coding
✅ description: Enforce TypeScript type safety rules including no 'any' types, explicit return types, and proper interface definitions. Use when writing or reviewing TypeScript code.
```

**Missing Activation Triggers:**
```yaml
❌ description: Generates API documentation
✅ description: Generate API documentation from code comments, route definitions, and TypeScript interfaces. Use when documenting APIs, creating OpenAPI specs, or when user mentions API docs.
```

**No Keywords:**
```yaml
❌ description: A skill for documents
✅ description: Create and format Word documents with tables, images, and professional layouts. Use when creating reports, documentation, or DOCX files.
```

---

## Performance Optimization

### Startup Performance

**At Startup, Claude loads:**
- Only `name` and `description` fields
- Not full content

**Impact:**
- Can have dozens of skills
- No startup penalty
- Fast skill discovery

### Runtime Performance

**When Skill Activates:**
1. SKILL.md loads into context
2. Referenced files load if mentioned
3. Scripts execute if called

**Optimization:**
- Keep SKILL.md focused
- Lazy-load supplemental content
- Efficient scripts

### Script Performance

**Bad (Slow):**
```python
# Reads entire file into memory
with open('large_file.txt', 'r') as f:
    data = f.read()  # Could be GBs!
    process(data)
```

**Good (Fast):**
```python
# Streams data
with open('large_file.txt', 'r') as f:
    for line in f:  # Process incrementally
        process(line)
```

### Caching Strategies

**For Repeated Data:**

```python
# cache_helper.py
_cache = {}

def get_config():
    if 'config' not in _cache:
        _cache['config'] = load_config()
    return _cache['config']
```

Avoids repeated expensive operations.

### Batch Operations

**Bad (Multiple Calls):**
```python
for user in users:
    api.get_user(user.id)  # N API calls
```

**Good (Single Call):**
```python
api.get_users([u.id for u in users])  # 1 API call
```

---

## Security Guidelines

### Never Include Secrets

**Prohibited in Skills:**
- ❌ API keys
- ❌ Passwords
- ❌ OAuth tokens
- ❌ Private keys
- ❌ Database credentials
- ❌ Encryption keys

### Use Environment Variables

**Bad:**
```markdown
Use API key: sk-1234567890abcdef
```

**Good:**
```markdown
Use API key from environment variable `API_KEY`:

```python
import os
api_key = os.getenv('API_KEY')
```
```

### Validate Inputs

**Always validate user inputs:**

```python
def process_user_input(data):
    # Validate type
    if not isinstance(data, str):
        raise ValueError("Input must be string")

    # Validate length
    if len(data) > 1000:
        raise ValueError("Input too long")

    # Validate format
    if not data.isalnum():
        raise ValueError("Invalid characters")

    return data
```

### Sanitize Outputs

**Prevent injection attacks:**

```python
import html

def safe_output(user_data):
    # Escape HTML
    return html.escape(user_data)
```

### File Access Restrictions

**Restrict file operations:**

```python
import os
from pathlib import Path

def safe_read_file(filename):
    # Prevent directory traversal
    safe_path = Path(filename).resolve()
    allowed_dir = Path('/safe/directory').resolve()

    if not str(safe_path).startswith(str(allowed_dir)):
        raise ValueError("Access denied")

    return safe_path.read_text()
```

### Dependency Security

**Check dependencies:**

```bash
# Check for vulnerabilities
npm audit
pip check
```

**Update regularly:**

```bash
npm update
pip install --upgrade package-name
```

### Security Checklist

- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] Output sanitization applied
- [ ] File access restricted
- [ ] Dependencies up to date
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include secrets

---

## Maintenance and Updates

### Versioning Strategy

**Semantic Versioning:**

```
MAJOR.MINOR.PATCH
2.1.3
```

**When to increment:**

```
MAJOR (2.0.0) → Breaking changes
MINOR (1.1.0) → New features, backward compatible
PATCH (1.0.1) → Bug fixes
```

### Changelog Maintenance

**Keep detailed changelog:**

```markdown
# Changelog

## [2.0.0] - 2025-10-21
### Breaking Changes
- Changed API response format
- Removed deprecated `oldMethod()`

### Added
- New `advancedFeature()` method
- Support for async operations

### Fixed
- Memory leak in long-running processes

## [1.1.0] - 2025-10-15
### Added
- JSON export functionality
- Batch processing support

### Fixed
- Edge case in date parsing
```

### Update Frequency

**Regular updates:**
- Weekly: Check for issues
- Monthly: Review usage patterns
- Quarterly: Major improvements

**Trigger updates when:**
- Bug reports received
- New use cases emerge
- Dependencies updated
- Best practices change

### Deprecation Strategy

**When removing features:**

1. **Announce deprecation:**
```markdown
## Deprecated Features

`oldMethod()` is deprecated and will be removed in v2.0.0.
Use `newMethod()` instead.
```

2. **Provide migration path:**
```markdown
### Migration Guide

Replace:
```python
result = oldMethod(data)
```

With:
```python
result = newMethod(data)
```
```

3. **Set timeline:**
```
v1.9.0 - Feature deprecated
v1.10.0 - Warning added
v2.0.0 - Feature removed
```

### Testing Updates

**Before releasing updates:**

1. **Unit tests:**
```bash
npm test
pytest
```

2. **Integration tests:**
```bash
npm run test:integration
```

3. **Manual testing:**
- Test common scenarios
- Test edge cases
- Test with real data

### Rollback Plan

**Always have rollback capability:**

```bash
# Tag releases
git tag v1.2.0
git push origin v1.2.0

# Rollback if needed
git checkout v1.1.0
```

---

## Team Collaboration

### Code Review for Skills

**Review checklist:**
- [ ] Description is clear and complete
- [ ] Examples are accurate
- [ ] No hardcoded secrets
- [ ] Token usage is optimized
- [ ] Tests are included
- [ ] Documentation is updated

### Naming Conventions

**Consistent naming:**

```
team-style-guide      ✅ (lowercase, hyphens)
Team_Style_Guide      ❌ (uppercase, underscores)
teamStyleGuide        ❌ (camelCase)
```

### Documentation Standards

**Every skill should have:**

1. **Clear purpose statement**
2. **Usage examples**
3. **Configuration options**
4. **Troubleshooting guide**
5. **Changelog**

### Shared Skill Library

**Organize team skills:**

```
.claude/skills/
├── README.md                 # Skill index
├── authentication/
├── data-validation/
├── report-generation/
└── testing-utils/
```

**README.md:**
```markdown
# Team Skills

## Available Skills

### authentication
Handles user authentication and authorization.
Use when: Working with login, sessions, or permissions.

### data-validation
Validates input data against schemas.
Use when: Processing user input or API requests.

### report-generation
Generates PDF and Excel reports.
Use when: Creating business reports or exports.
```

### Communication

**When updating skills:**

1. **Notify team:**
   - Post in team chat
   - Update documentation
   - Mention in standup

2. **Provide migration guide:**
   - What changed
   - Why it changed
   - How to update code

3. **Set timeline:**
   - When changes deploy
   - Deprecation schedule
   - Support deadline

---

## Summary: Golden Rules

1. **Token Efficiency**
   - Keep SKILL.md < 500 lines
   - Use progressive disclosure
   - Split large content

2. **Great Descriptions**
   - What + When + Keywords
   - Test activation
   - Include trigger words

3. **Security First**
   - No secrets in skills
   - Validate inputs
   - Sanitize outputs

4. **Maintain Quality**
   - Regular updates
   - Detailed changelog
   - Comprehensive tests

5. **Team Collaboration**
   - Code reviews
   - Clear documentation
   - Communication

6. **Performance**
   - Optimize scripts
   - Cache when appropriate
   - Lazy-load content

---

## Monitoring and Metrics

### Track Usage

**Key metrics:**
- Activation frequency
- Token consumption
- Error rates
- User satisfaction

### Continuous Improvement

**Regular reviews:**
- Which skills are used most?
- Which skills never activate?
- Where are users struggling?
- What new needs have emerged?

**Act on data:**
- Optimize high-use skills
- Improve or remove low-use skills
- Create skills for common requests
- Update based on feedback

---

*Following these best practices ensures your skills are efficient, secure, maintainable, and valuable to your team.*
