# Skill Structure and Technical Specifications

Complete technical reference for organizing Claude Code skills.

## Minimum Requirements

A valid skill requires only:

1. **A directory** with your skill name
2. **A SKILL.md file** with YAML frontmatter

That's it. Everything else is optional.

---

## Directory Structure Patterns

### Pattern 1: Simple Skill (Minimum)

```
skill-name/
└── SKILL.md
```

Use when:
- Instructions fit in one file
- No supplemental resources needed
- Straightforward use case

### Pattern 2: Skill with Reference Documentation

```
skill-name/
├── SKILL.md
└── REFERENCE.md
```

Use when:
- Core instructions are concise
- Additional context needed for specific scenarios
- Progressive disclosure saves tokens

### Pattern 3: Modular Skill (Recommended)

```
skill-name/
├── SKILL.md
├── core-concepts.md
├── advanced-usage.md
├── api-reference.md
└── examples.md
```

Use when:
- Large amount of documentation
- Multiple use cases
- Different expertise levels

### Pattern 4: Full-Featured Skill

```
skill-name/
├── SKILL.md
├── reference/
│   ├── api-docs.md
│   ├── troubleshooting.md
│   └── changelog.md
├── scripts/
│   ├── helper.py
│   ├── validator.js
│   └── README.md
├── templates/
│   ├── template.json
│   └── example.yaml
└── examples/
    ├── basic-usage.md
    └── advanced-patterns.md
```

Use when:
- Complex workflows
- Multiple programming languages
- Reusable scripts/templates needed
- Team collaboration

### Pattern 5: Document Processing Skill

```
pdf-processing/
├── SKILL.md
├── FORMS.md
├── REFERENCE.md
└── scripts/
    ├── fill_form.py
    └── validate.py
```

Official pattern from anthropics/skills for document manipulation.

---

## SKILL.md File Format

### Required Structure

```markdown
---
name: skill-name
description: What this skill does and when to use it
---

# Skill Title

[Your content here]
```

### YAML Frontmatter

**Required Fields:**

```yaml
---
name: skill-name          # lowercase, hyphens only, no spaces
description: Brief but complete description including when to use this skill
---
```

**Optional Fields:**

```yaml
---
name: skill-name
description: Complete description with use cases
version: 1.0.0           # semantic versioning
author: Your Name        # skill creator
tags: [typescript, testing, automation]  # for organization
---
```

### Field Specifications

**name:**
- Lowercase only
- Use hyphens for spaces
- No special characters
- Must be unique
- Examples: `git-helper`, `brand-guidelines`, `typescript-enforcer`

**description:**
- Most critical field for activation
- Include WHAT the skill does
- Include WHEN to use it
- Include keywords users might mention
- Length: 1-3 sentences recommended

**Good descriptions:**
```yaml
description: Generate conventional commit messages following type(scope): description format. Use when user asks to commit changes or needs help with git commit messages.
```

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad descriptions:**
```yaml
description: Helps with git
```

```yaml
description: PDF skill
```

---

## Content Organization

### Progressive Disclosure Architecture

At startup, Claude pre-loads only the **name** and **description** of every skill. Full content loads only when skill activates.

**Benefits:**
- Saves tokens
- Faster response times
- Efficient context management
- Scales to many skills

**Implementation:**

```
skill/
├── SKILL.md           # Core instructions (always loaded when active)
├── REFERENCE.md       # Detailed specs (loaded only when needed)
└── advanced.md        # Edge cases (loaded only when mentioned)
```

In SKILL.md, reference other files:

```markdown
# My Skill

## Core Usage
[Essential instructions here]

## Advanced Features
For advanced usage patterns, see `advanced.md`

## API Reference
For complete API documentation, see `REFERENCE.md`
```

Claude will load referenced files only when relevant.

---

## REFERENCE.md Usage

### Purpose

Use REFERENCE.md for:
- Detailed API documentation
- Comprehensive reference tables
- Edge cases and exceptions
- Technical specifications
- Rarely-used advanced features

### Structure

```markdown
# Reference Documentation

## API Reference
[Detailed API docs]

## Configuration Options
[All possible configurations]

## Error Codes
[Complete error reference]

## Advanced Patterns
[Complex usage patterns]
```

### When to Split Content

**Keep in SKILL.md:**
- Core instructions
- Common use cases
- Essential guidelines
- Frequently used examples

**Move to REFERENCE.md:**
- Complete API documentation
- All configuration options
- Error code tables
- Advanced edge cases
- Rarely-used features

**Threshold:** If SKILL.md exceeds ~500 lines, split it.

---

## Multi-File Organization

### Modular Documentation Pattern

```
skill/
├── SKILL.md              # Entry point and navigation
├── getting-started.md    # Beginner guide
├── core-features.md      # Main functionality
├── advanced.md           # Power user features
└── reference.md          # Complete reference
```

**SKILL.md as Navigation Hub:**

```markdown
---
name: comprehensive-skill
description: [Your description]
---

# Comprehensive Skill

## Quick Start
See `getting-started.md` for your first use.

## Core Features
Review `core-features.md` for main functionality.

## Advanced Usage
Check `advanced.md` for power user features.

## Complete Reference
See `reference.md` for full API documentation.
```

### Topic-Based Organization

```
skill/
├── SKILL.md
├── authentication.md
├── data-processing.md
├── api-integration.md
└── error-handling.md
```

Each file covers a distinct topic. Reference them contextually in SKILL.md.

---

## Scripts and Resources

### Scripts Directory

```
skill/
├── SKILL.md
└── scripts/
    ├── helper.py
    ├── validator.js
    ├── formatter.sh
    └── README.md
```

**Use for:**
- Reusable utility functions
- Data validation scripts
- File processing tools
- Automated workflows

**Guidelines:**
- Document each script in README.md
- Make scripts standalone when possible
- Include usage examples
- Handle errors gracefully

### Templates Directory

```
skill/
├── SKILL.md
└── templates/
    ├── config.json
    ├── markdown-template.md
    └── api-response.yaml
```

**Use for:**
- Configuration templates
- Document templates
- Response format examples
- Boilerplate code

---

## Examples Directory

```
skill/
├── SKILL.md
└── examples/
    ├── basic-example.md
    ├── advanced-example.md
    └── real-world-case.md
```

Show concrete, runnable examples for different use cases.

---

## File Naming Conventions

**Do:**
- ✅ `getting-started.md`
- ✅ `api-reference.md`
- ✅ `troubleshooting-guide.md`

**Don't:**
- ❌ `Getting Started.md` (no spaces)
- ❌ `API_Reference.md` (no underscores)
- ❌ `guide.MD` (lowercase extension)

**Consistency:**
- Use lowercase
- Use hyphens for spaces
- Use `.md` extension
- Be descriptive but concise

---

## Real-World Structure Examples

### Example 1: Brand Guidelines Skill

```
brand-guidelines/
├── SKILL.md
├── colors.md           # Hex codes, usage rules
├── typography.md       # Fonts, sizes, spacing
├── logo-usage.md       # Logo guidelines
└── templates/
    └── presentation.pptx
```

### Example 2: TypeScript Enforcer

```
typescript-enforcer/
├── SKILL.md
├── type-rules.md       # Type safety rules
├── naming-conventions.md
├── examples.md
└── scripts/
    └── lint-check.js
```

### Example 3: API Documentation Generator

```
api-doc-generator/
├── SKILL.md
├── openapi-spec.md
├── markdown-format.md
└── templates/
    ├── endpoint-template.md
    └── model-template.md
```

---

## Markdown Formatting Guidelines

### Headers

Use semantic heading levels:

```markdown
# Skill Title (H1 - once per file)

## Main Sections (H2)

### Subsections (H3)

#### Details (H4)
```

### Code Blocks

Always specify language for syntax highlighting:

````markdown
```javascript
const example = "code";
```

```python
def example():
    pass
```

```bash
echo "shell command"
```
````

### Lists

Use consistent formatting:

```markdown
Ordered:
1. First item
2. Second item
3. Third item

Unordered:
- Bullet point
- Another point
  - Nested point
  - Another nested
```

### Emphasis

```markdown
**Bold** for important terms
*Italic* for emphasis
`code` for inline code
```

---

## Token Optimization Through Structure

### Strategy 1: Separate Rarely-Used Content

```
skill/
├── SKILL.md          # Common cases (loaded often)
└── edge-cases.md     # Rare scenarios (loaded seldom)
```

Saves tokens by not loading edge cases unless needed.

### Strategy 2: Context-Specific Files

```
skill/
├── SKILL.md
├── windows-specific.md
├── macos-specific.md
└── linux-specific.md
```

Load only OS-relevant file.

### Strategy 3: Skill Variants

```
skill/
├── SKILL.md          # Beginner-friendly version
└── advanced.md       # Expert version with all options
```

Progressive complexity based on user expertise.

---

## Version Control Considerations

### Git-Friendly Structure

```
skill-name/
├── .gitignore
├── SKILL.md
├── CHANGELOG.md
└── version.txt
```

**Track changes:**
- Use CHANGELOG.md for version history
- Semantic versioning in frontmatter
- Clear commit messages

**Example CHANGELOG.md:**
```markdown
# Changelog

## [1.1.0] - 2025-10-21
### Added
- Advanced error handling
- New examples for edge cases

## [1.0.0] - 2025-10-15
### Initial Release
- Core functionality
- Basic examples
```

---

## Official Anthropic Patterns

From github.com/anthropics/skills:

**Document Skills Pattern:**
```
document-skills/
├── docx/SKILL.md
├── pdf/SKILL.md
├── pptx/SKILL.md
└── xlsx/SKILL.md
```

Each document type is a separate skill.

**Template Skill Pattern:**
```
template-skill/
├── SKILL.md           # Full documentation
└── README.md          # Developer notes
```

Minimal but complete.

---

## Skill Size Guidelines

**Small Skill:** < 200 lines in SKILL.md
- Single file sufficient
- Fast loading
- Easy maintenance

**Medium Skill:** 200-500 lines
- Consider REFERENCE.md
- Keep SKILL.md focused on core usage

**Large Skill:** > 500 lines
- Required: Split into multiple files
- Use modular structure
- Progressive disclosure essential

---

## Summary: Choosing Your Structure

**Start Simple:**
- Begin with single SKILL.md
- Add files only when needed
- Don't over-engineer early

**Expand Gradually:**
- Add REFERENCE.md when core file gets long
- Create examples/ when you have 3+ examples
- Add scripts/ when code becomes reusable

**Modularize Eventually:**
- Split by topic when file exceeds 500 lines
- Separate by use case for different user levels
- Organize by context for token efficiency

---

*The best structure is the simplest one that serves your needs. Start minimal and grow organically.*
