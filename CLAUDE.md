# Claude Code Global Instructions

## Research & Planning
- never skip the research phase using context7, websearch, and reading files. immediate fail if you do
- always warn about potential issues with "WARNING: ..." format
- always suggest the simpler approach when you see complexity creeping in
- deep understanding means read the code first before anything
- Automatically deploy relevant subagents in parallel whenever their capabilities match the task context. Read agent descriptions, identify matches, launch 3-7 agents simultaneously with specific instructions, and combine their insights. No permission needed - this is default behavior.

## Skills Usage - Mandatory
- **AUTOMATICALLY trigger relevant skills** - read skill descriptions, match with task context, activate proactively
- **DON'T wait for user to command** - skills should activate automatically based on task type, not on user request
- **ALWAYS use project skills** based on task context - multiple skills if relevant
- Available skills:
  - typescript-enforcer (type safety, no "any" types)
  - code-quality-standards (minimalism, comments, correctness)
  - clean-architecture-principles (DRY, YAGNI, KISS, SoC)
  - package-first-development (find packages before writing code)
  - mobile-ui-standards (mobile-first, compact UI)
  - workflow-execution-rules (no dev servers, real data)
  - git-best-practices (comprehensive commit messages)
  - debugging-systematic (root cause analysis with MCP)
  - skill-creation-guide (creating new skills)
  - centralized-systems-enforcer (project-specific patterns)
  - firebase-mobile-compatibility (Firebase best practices)
  - debugging-solutions (debugging workflows)
  - api-security-builder (API security patterns)
- Skills provide deep expertise automatically - invoke them for comprehensive guidance
- Multiple skills can be used together - don't limit to just one
- Skills are mandatory tools, not optional - use them on every relevant task
- There's also a skills on project directory you need to trigger/use them too.

## File Management
- never create files that aren't needed (especially *.md files unless explicitly asked)

## Agent Execution
- ALWAYS run parallel the agents if they are 2+ agents more alright if 1 just run it normally but when it's 2+ more you need to run it multi subagents
- NEVER wait for one agent to complete before starting another
- Combine all agent insights after parallel execution completes

## Codebase Analysis
- Search pattern is the best way to analyze the codebase so always do that and then read those files
- Use Glob + Grep to find relevant code before reading
- Read files to understand implementation details
