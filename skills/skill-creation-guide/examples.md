# Real-World Skill Examples

Comprehensive collection of production-ready skill examples and use cases.

## Official Anthropic Skills

From https://github.com/anthropics/skills

### 1. PDF Processing Skill

**Use Case:** Extract text, fill forms, merge PDF documents

**Structure:**
```
pdf-processing/
├── SKILL.md
├── FORMS.md
├── REFERENCE.md
└── scripts/
    ├── fill_form.py
    └── validate.py
```

**SKILL.md:**
```markdown
---
name: pdf
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Capabilities

1. **Text Extraction**
   - Extract all text from PDF
   - Preserve formatting and structure
   - Handle multi-column layouts

2. **Form Filling**
   - Fill interactive PDF forms
   - Validate field types
   - Save completed forms

3. **Document Merging**
   - Combine multiple PDFs
   - Maintain bookmarks and links
   - Optimize file size

## Usage Examples

### Extract Text
```python
from pdf_processor import extract_text

text = extract_text("document.pdf")
print(text)
```

### Fill Form
See FORMS.md for form-filling examples.

## Reference
For complete API documentation, see REFERENCE.md
```

---

### 2. Excel/XLSX Processing Skill

**Use Case:** Create, read, and manipulate Excel spreadsheets

**SKILL.md:**
```markdown
---
name: xlsx
description: Create, read, and manipulate Excel spreadsheets with formulas, formatting, charts, and data analysis. Use when working with Excel files, spreadsheets, or data analysis tasks.
---

# Excel Processing

## Features

- Read and write .xlsx files
- Create formulas and calculations
- Apply formatting and styles
- Generate charts and visualizations
- Data validation and filtering

## Common Tasks

### Create Spreadsheet
```python
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active

ws['A1'] = 'Product'
ws['B1'] = 'Sales'
ws['C1'] = 'Total'

ws['C2'] = '=B2*10'

wb.save('sales.xlsx')
```

### Read Data
```python
wb = openpyxl.load_workbook('sales.xlsx')
ws = wb.active

for row in ws.iter_rows(values_only=True):
    print(row)
```

### Apply Formatting
```python
from openpyxl.styles import Font, PatternFill

ws['A1'].font = Font(bold=True, size=14)
ws['A1'].fill = PatternFill(start_color="FFFF00", fill_type="solid")
```

## Data Analysis

### Sales Report Example
```python
# Calculate totals
ws['C10'] = '=SUM(C2:C9)'

# Apply conditional formatting
ws.conditional_formatting.add('B2:B9',
    ColorScaleRule(start_type='min', end_type='max'))
```
```

---

### 3. PowerPoint/PPTX Skill

**Use Case:** Create and edit presentations programmatically

**SKILL.md:**
```markdown
---
name: pptx
description: Create, edit, and format PowerPoint presentations with slides, text, images, and charts. Use when working with presentations, slides, or PPTX files.
---

# PowerPoint Processing

## Capabilities

- Create new presentations
- Add and format slides
- Insert text, images, charts
- Apply themes and styles
- Export to various formats

## Examples

### Create Presentation
```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()

# Title slide
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title = title_slide.shapes.title
title.text = "Quarterly Report"

# Content slide
content_slide = prs.slides.add_slide(prs.slide_layouts[1])
title = content_slide.shapes.title
title.text = "Key Metrics"

prs.save('report.pptx')
```

### Add Chart
```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Sales', (100, 150, 120, 180))

slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(2), Inches(2),
    Inches(6), Inches(4),
    chart_data
)
```
```

---

### 4. Word/DOCX Processing Skill

**Use Case:** Create and edit Word documents

**SKILL.md:**
```markdown
---
name: docx
description: Create, read, and edit Word documents with text, tables, images, and formatting. Use when working with Word documents, reports, or DOCX files.
---

# Word Document Processing

## Features

- Create new documents
- Add paragraphs and headings
- Insert tables and images
- Apply styles and formatting
- Generate reports

## Examples

### Create Document
```python
from docx import Document
from docx.shared import Inches

doc = Document()

# Add heading
doc.add_heading('Project Report', 0)

# Add paragraph
doc.add_paragraph('This is the introduction.')

# Add table
table = doc.add_table(rows=3, cols=3)
table.cell(0, 0).text = 'Name'
table.cell(0, 1).text = 'Role'
table.cell(0, 2).text = 'Status'

# Save
doc.save('report.docx')
```

### Apply Styles
```python
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

paragraph = doc.add_paragraph('Important Notice')
run = paragraph.runs[0]
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(255, 0, 0)
paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
```
```

---

## Development Workflow Skills

### 5. Git Commit Message Generator

**Use Case:** Generate conventional commit messages

**SKILL.md:**
```markdown
---
name: git-commit-helper
description: Generate conventional commit messages following type(scope): description format. Use when user asks to commit changes or needs help with git commit messages.
---

# Git Commit Helper

## Format

```
type(scope): description

[optional body]

[optional footer]
```

## Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, missing semi colons, etc)
- **refactor**: Code refactoring
- **test**: Adding tests
- **chore**: Build process or tooling

## Process

1. Analyze `git diff --staged`
2. Identify type and scope
3. Write concise description (< 72 chars)
4. Add body if needed for context

## Examples

```
feat(auth): add JWT token validation

Implement JWT validation middleware with token
expiry checking and refresh token support.

Closes #123
```

```
fix(api): resolve null pointer in user endpoint

Check for null before accessing user.profile
```

```
docs(readme): update installation instructions
```

## Guidelines

- Use imperative mood ("add" not "added")
- Lowercase type and scope
- No period at end
- Reference issues in footer
```

---

### 6. Code Review Assistant

**Use Case:** Automated code review checklist

**SKILL.md:**
```markdown
---
name: code-reviewer
description: Perform systematic code reviews checking for best practices, security issues, performance, and maintainability. Use when reviewing code or pull requests.
---

# Code Review Assistant

## Review Checklist

### 1. Code Quality
- [ ] Clear and descriptive variable names
- [ ] Functions are single-purpose
- [ ] No code duplication (DRY)
- [ ] Proper error handling
- [ ] Comments for complex logic

### 2. Security
- [ ] No hardcoded credentials
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection

### 3. Performance
- [ ] No N+1 queries
- [ ] Efficient algorithms
- [ ] Proper indexing
- [ ] Caching where appropriate
- [ ] No memory leaks

### 4. Testing
- [ ] Unit tests included
- [ ] Edge cases covered
- [ ] Integration tests if needed
- [ ] Tests are passing

### 5. Documentation
- [ ] Function documentation
- [ ] API changes documented
- [ ] README updated if needed
- [ ] Breaking changes noted

## Usage

Analyze the code and provide:
1. Summary of changes
2. Issues found (Critical, Warning, Info)
3. Suggestions for improvement
4. Overall assessment

## Example Output

```markdown
## Code Review Summary

**Files Changed:** 3
**Lines Added:** 150
**Lines Removed:** 45

### Critical Issues
- ❌ SQL injection vulnerability in user query (line 45)
- ❌ Missing input validation in API endpoint

### Warnings
- ⚠️ Potential performance issue with nested loops
- ⚠️ Missing error handling in async function

### Suggestions
- ✅ Consider extracting helper function (lines 100-130)
- ✅ Add JSDoc comments for public methods

### Overall Assessment
⚠️ **Changes Required** - Address critical security issues before merging.
```
```

---

## Domain-Specific Skills

### 7. TypeScript Enforcer

**Use Case:** Enforce TypeScript best practices

**SKILL.md:**
```markdown
---
name: typescript-enforcer
description: Enforce TypeScript best practices including strict type safety, no 'any' types, proper interfaces, and naming conventions. Use when writing or reviewing TypeScript code.
---

# TypeScript Enforcer

## Rules

### 1. Type Safety
- ❌ Never use `any` type
- ✅ Use `unknown` and type guards instead
- ✅ Explicit return types on functions
- ✅ Strict null checking

### 2. Interfaces and Types
```typescript
// Bad
const user = { name: "John", age: 30 };

// Good
interface User {
  name: string;
  age: number;
}

const user: User = { name: "John", age: 30 };
```

### 3. Naming Conventions
- Interfaces: `PascalCase` (e.g., `UserProfile`)
- Types: `PascalCase` (e.g., `ResponseData`)
- Variables: `camelCase` (e.g., `userName`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)

### 4. Function Types
```typescript
// Bad
function process(data) {
  return data.map(x => x * 2);
}

// Good
function process(data: number[]): number[] {
  return data.map((x: number) => x * 2);
}
```

### 5. Utility Types
Use TypeScript utility types:
```typescript
type Partial<User>     // All properties optional
type Required<User>    // All properties required
type Pick<User, 'name'> // Select specific properties
type Omit<User, 'age'> // Exclude specific properties
```

## Review Checklist

- [ ] No `any` types
- [ ] All functions have return types
- [ ] Interfaces defined for objects
- [ ] Proper null/undefined handling
- [ ] Correct naming conventions
- [ ] Generic types where appropriate
```

---

### 8. Brand Guidelines Enforcer

**Use Case:** Ensure brand consistency across documents

**Structure:**
```
brand-guidelines/
├── SKILL.md
├── colors.md
├── typography.md
└── templates/
    └── presentation.pptx
```

**SKILL.md:**
```markdown
---
name: brand-guidelines
description: Apply company brand guidelines including colors, fonts, logo usage, and spacing. Use when creating presentations, documents, or any branded materials.
---

# Brand Guidelines

## Color Palette

Primary Colors (see colors.md for details):
- Brand Blue: #0066CC
- Brand Orange: #FF6600
- Neutral Gray: #F5F5F5

## Typography

See typography.md for complete font specifications.

Primary Font: "Helvetica Neue"
- Headings: Bold, 24-32pt
- Body: Regular, 12-14pt
- Captions: Light, 10pt

## Logo Usage

Requirements:
- Minimum size: 1 inch width
- Clear space: 0.5x logo height on all sides
- Never distort or rotate
- Use on white or brand blue background only

## Spacing

- Margins: 1 inch all sides
- Line height: 1.5x font size
- Section spacing: 24pt

## Templates

Use templates/ directory for:
- Presentation template (PPTX)
- Document template (DOCX)
- Email signature (HTML)

## Validation

Before finalizing, check:
- [ ] Colors match brand palette
- [ ] Fonts are correct
- [ ] Logo meets requirements
- [ ] Spacing is consistent
```

---

## Automation Skills

### 9. API Documentation Generator

**Use Case:** Generate API docs from code

**SKILL.md:**
```markdown
---
name: api-doc-generator
description: Generate API documentation from code comments, route definitions, and TypeScript interfaces. Use when documenting APIs or creating OpenAPI specs.
---

# API Documentation Generator

## Input Formats

Supports:
- Express.js routes
- FastAPI endpoints
- TypeScript interfaces
- JSDoc comments
- OpenAPI/Swagger specs

## Output Formats

Generate:
- Markdown documentation
- OpenAPI 3.0 spec
- Postman collection
- HTML documentation

## Example

**Input (Express route):**
```javascript
/**
 * Get user by ID
 * @route GET /api/users/:id
 * @param {string} id - User ID
 * @returns {User} User object
 * @throws {404} User not found
 */
app.get('/api/users/:id', async (req, res) => {
  // implementation
});
```

**Output (Markdown):**
```markdown
## GET /api/users/:id

Get user by ID

### Parameters
- `id` (string, required) - User ID

### Response
Returns User object

### Errors
- 404 - User not found

### Example Request
```bash
curl -X GET https://api.example.com/users/123
```

### Example Response
```json
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com"
}
```
```

## Template

```markdown
# API Documentation

## Base URL
`https://api.example.com/v1`

## Authentication
Bearer token required in Authorization header

## Endpoints
[Generated endpoint documentation]

## Models
[Generated data model documentation]

## Error Codes
[Standard error response format]
```
```

---

## Testing Skills

### 10. Test Generator

**Use Case:** Generate unit tests from code

**SKILL.md:**
```markdown
---
name: test-generator
description: Generate comprehensive unit tests for functions and classes covering happy path, edge cases, and error handling. Use when writing tests or when test coverage is needed.
---

# Test Generator

## Supported Frameworks

- Jest (JavaScript/TypeScript)
- Pytest (Python)
- JUnit (Java)
- RSpec (Ruby)

## Test Coverage

Generate tests for:
1. Happy path scenarios
2. Edge cases
3. Error handling
4. Boundary conditions
5. Null/undefined inputs

## Example

**Input Function:**
```typescript
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Division by zero");
  }
  return a / b;
}
```

**Generated Tests:**
```typescript
describe('divide', () => {
  it('should divide two positive numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('should divide negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('should handle decimal results', () => {
    expect(divide(5, 2)).toBe(2.5);
  });

  it('should throw error for division by zero', () => {
    expect(() => divide(10, 0)).toThrow("Division by zero");
  });

  it('should handle zero dividend', () => {
    expect(divide(0, 5)).toBe(0);
  });

  it('should handle negative divisor', () => {
    expect(divide(10, -2)).toBe(-5);
  });
});
```

## Test Template

```typescript
describe('[FunctionName]', () => {
  // Setup
  beforeEach(() => {
    // Initialize test data
  });

  // Happy path
  it('should [expected behavior]', () => {
    // Test implementation
  });

  // Edge cases
  it('should handle [edge case]', () => {
    // Test implementation
  });

  // Error handling
  it('should throw error when [condition]', () => {
    // Test implementation
  });

  // Cleanup
  afterEach(() => {
    // Clean up
  });
});
```
```

---

## Community Examples

### 11. Database Migration Helper

**Use Case:** Generate and validate database migrations

```markdown
---
name: db-migration-helper
description: Generate database migration scripts for schema changes, validate migrations, and ensure backward compatibility. Use when modifying database schema or creating migrations.
---

# Database Migration Helper

## Supported Databases
- PostgreSQL
- MySQL
- MongoDB
- SQLite

## Migration Types

### Add Column
```sql
ALTER TABLE users
ADD COLUMN last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

### Create Index
```sql
CREATE INDEX idx_users_email ON users(email);
```

### Add Foreign Key
```sql
ALTER TABLE orders
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES users(id);
```

## Validation Checklist

- [ ] Backward compatible
- [ ] Rollback script included
- [ ] Data migration if needed
- [ ] Index performance impact assessed
- [ ] No data loss
```

---

## Resources

**Official Examples:**
- GitHub: https://github.com/anthropics/skills
- Cookbooks: https://github.com/anthropics/claude-cookbooks/tree/main/skills

**Community Collections:**
- Awesome Claude Skills: https://github.com/travisvn/awesome-claude-skills
- Skills Collection: https://github.com/abubakarsiddik31/claude-skills-collection
- Office Skills: https://github.com/tfriedel/claude-office-skills

---

*These examples demonstrate real-world skill implementations. Adapt them to your specific needs and workflows.*
