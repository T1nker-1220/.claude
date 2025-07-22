# Requirements Management Workflow

## Overview
This document defines the standardized workflow for creating and managing project requirements using Claude Code's `/task` slash command, inspired by kiro.dev's spec-driven development approach.

## Workflow Process

### 1. Task Initiation
- User triggers `/task` command in any project directory
- Claude initiates interactive requirements gathering session
- System automatically detects current project context

### 2. Requirements Gathering (Interactive)
Claude will prompt for the following information step-by-step:

#### a. Task Description
- Clear, concise description of the main task or feature
- Context about why this task is needed
- High-level goals and objectives

#### b. User Stories & Requirements (EARS Format)
- Requirements written in EARS notation: "WHEN [condition/event] THE SYSTEM SHALL [expected behavior]"
- Benefits: clarity, testability, traceability, completeness
- Multiple user stories to cover different scenarios

#### c. Acceptance Criteria
- Specific, measurable criteria for task completion
- Clear pass/fail conditions
- Edge cases and error handling requirements

#### d. Technical Approach
- Preferred technologies, frameworks, or patterns
- Architecture decisions and reasoning
- Integration points with existing systems

#### e. Dependencies & Constraints
- External dependencies (APIs, libraries, services)
- Technical constraints (performance, security, compatibility)
- Resource limitations (time, budget, team capacity)

### 3. Requirements Document Generation
Claude creates `requirements.md` in the project's `.claude/` directory with structure:

```markdown
# Project Requirements: [Task Name]

## Project Overview
[High-level description and context]

## User Stories (EARS Format)
- WHEN [condition] THE SYSTEM SHALL [behavior]
- WHEN [condition] THE SYSTEM SHALL [behavior]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Approach
### Architecture
[System design decisions]

### Data Flow
[How data moves through the system]

### Interfaces
[API endpoints, UI components]

### Error Handling
[Error scenarios and responses]

## Dependencies & Constraints
### External Dependencies
- Dependency 1: [description]
- Dependency 2: [description]

### Technical Constraints
- Constraint 1: [description]
- Constraint 2: [description]

## Success Metrics
[How success will be measured]

## Timeline Considerations
[Estimated effort and milestones]
```

### 4. User Approval Process
- Claude presents complete requirements document for review
- User can request modifications or approve as-is
- Requirements are not finalized until explicit user approval

### 5. Todo Generation (Post-Approval)
- After requirements approval, Claude automatically uses TodoWrite
- Creates structured, actionable todos based on requirements
- Todos follow implementation phases: Design ’ Development ’ Testing ’ Deployment
- Each todo references specific requirements sections

### 6. File Management
- Requirements stored in `{project}/.claude/requirements.md`
- Todos managed through Claude Code's built-in TodoWrite system
- Version control recommended for requirements tracking

## Key Principles

### Spec-Driven Development
- Define requirements before implementation
- Document reasoning and decisions
- Break down complex tasks into manageable pieces
- Maintain traceability throughout development

### Interactive Collaboration
- User-driven requirement definition
- Iterative refinement process
- Explicit approval gates
- Context-aware assistance

### Tool Integration
- Leverage Claude Code's built-in TodoWrite functionality
- Integrate with existing project memory (CLAUDE.md)
- Support for various project types and structures
- Cross-platform compatibility

## Usage Examples

### Basic Usage
```
/task
```
Initiates interactive requirements gathering session.

### Expected Flow
1. User runs `/task` in project directory
2. Claude asks for task description
3. Claude guides through EARS requirements gathering
4. Claude generates requirements document
5. User reviews and approves
6. Claude creates structured todos
7. Development begins with clear requirements

## Benefits

### For Developers
- Clear understanding of requirements before coding
- Structured approach to complex tasks
- Built-in progress tracking
- Consistent documentation format

### For Projects
- Improved requirement traceability
- Better communication between team members
- Reduced scope creep and misunderstandings
- Historical record of decisions and rationale

### for Teams
- Standardized requirements format across projects
- Scalable process for projects of any size
- Integration with existing Claude Code workflows
- Support for both individual and collaborative development

## Integration Points

### With Claude Code Features
- **Memory System**: Integrates with existing CLAUDE.md files
- **TodoWrite**: Automatic todo generation post-approval
- **Slash Commands**: Accessible via `/task` globally
- **Project Context**: Automatic detection of project structure

### With Development Workflow
- **Version Control**: Requirements files are git-trackable
- **IDE Integration**: Works with Claude Code IDE integrations
- **CI/CD**: Can trigger automated processes post-requirements
- **Documentation**: Generated requirements serve as living documentation

## File Locations
- **Global Command**: `~/.claude/.claude/commands/task.md`
- **Project Requirements**: `{project}/.claude/requirements.md`
- **Guidelines**: `~/.claude/REQUIREMENTS-GUIDELINES.md` (this file)

---

*This workflow ensures consistent, thorough requirements gathering while leveraging Claude Code's built-in capabilities for maximum efficiency and integration.*