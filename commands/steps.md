# Step-by-Step Development Workflow

Execute development workflow in sequential steps. Each step requires user confirmation to proceed.

**IMPORTANT: Steps 0-3 are STRICTLY READ-ONLY - No files will be written or edited during planning phases.**
**Only Step 4 (ENGINEERING) is allowed to write/edit/create files.**

## 🔴 CRITICAL PARALLEL EXECUTION RULES
**MANDATORY**: All subagents MUST be deployed in PARALLEL, not sequentially!
- Use a single message with multiple Task tool invocations
- Deploy 3-7 agents simultaneously in each step
- NEVER wait for one agent to complete before starting another
- Combine all agent insights after parallel execution completes

## 📋 COMPREHENSIVE PROMPT REQUIREMENTS
**Every subagent deployment MUST include:**
1. **Full Context**: Complete conversation history and user requirements
2. **Previous Results**: All findings from earlier steps in the workflow
3. **Specific Goals**: Clear, detailed objectives for that agent's analysis
4. **Expected Output**: Precise format and depth of analysis needed
5. **Constraints**: Any limitations, preferences, or warnings to consider
6. **Integration Points**: How their findings connect with other agents' work

## Step 0: USER PROMPT (READ-ONLY)
User provides the initial request/feature/task to build.
Example: "I want to build a real-time chat feature"
Claude confirms understanding and starts workflow.
Mode: READ-ONLY - No files written

## Step 1: RESEARCHERS (READ-ONLY)
⚡ **PARALLEL DEPLOYMENT (Single Message, Multiple Task Invocations):**
- web-research-specialist
- solution-archeologist
- security-fortune-teller
- mistake-prophet

📝 **COMPREHENSIVE PROMPTS MUST INCLUDE:**
- Complete user requirements and feature descriptions
- Technology stack and constraints
- Specific research areas for each agent
- Expected deliverables (best practices, existing solutions, security predictions, historical mistakes)
- Cross-reference requirements between agents

Output: Combined research summary from all agents
Mode: READ-ONLY - Analysis only, no files written
User action: Type "next" to proceed

## Step 2: PROJECT MANAGER (READ-ONLY)
⚡ **PARALLEL DEPLOYMENT (Single Message, Multiple Task Invocations):**
- requirement-to-code
- project-structure-analyzer
- codebase-simplifier

📝 **COMPREHENSIVE PROMPTS MUST INCLUDE:**
- All research findings from Step 1
- Complete conversation history
- Specific analysis goals for each agent:
  * requirement-to-code: Transform requirements into implementation plans
  * project-structure-analyzer: Map existing codebase structure
  * codebase-simplifier: Identify complexity reduction opportunities
- Expected output format and detail level
- Integration points between their analyses

Output: Unified requirements, structure analysis, and complexity assessment
Mode: READ-ONLY - Planning only, no files written
User action: Type "next" to proceed

## Step 3: ARCHITECT (FINAL PLANNING - READ-ONLY)
⚡ **PARALLEL DEPLOYMENT (Single Message, Multiple Task Invocations):**
- frontend-architecture-auditor
- backend-architecture-analyzer
- performance-optimization-analyzer
- pattern-replicator
- security-vulnerability-auditor
- codebase-simplifier

📝 **COMPREHENSIVE PROMPTS MUST INCLUDE:**
- All findings from Steps 1-2 (research + requirements)
- Complete project context and constraints
- Specific architectural focus for each agent:
  * frontend-architecture-auditor: Component design, state management, UI/UX patterns
  * backend-architecture-analyzer: API design, database schema, service architecture
  * performance-optimization-analyzer: Bottleneck identification, optimization strategies
  * pattern-replicator: Existing patterns to maintain consistency
  * security-vulnerability-auditor: Security requirements and threat modeling
  * codebase-simplifier: Simplification opportunities in architecture
- Expected deliverables with specific detail requirements
- Cross-agent dependencies and integration points

Architecture Coverage:
- Database design and optimization
- Backend API structure
- Security patterns and authentication
- Performance strategies
- Clean code patterns
- Simple structure approach

Output: Complete technical blueprint ready for implementation
Mode: READ-ONLY - Design only, no files written
User action: Type "next" to proceed to documentation creation

## Step 3.5: PROJECT DOCUMENTATION & TODO CREATION (READ-ONLY)
⚡ **CREATE SINGLE COMPREHENSIVE FILE: `docs/[task-name].md`**

Write ONE file na may complete documentation with filename based on the task:
- Example: "chat feature" → `docs/chat-feature.md`
- Example: "user authentication" → `docs/user-authentication.md`
- Example: "payment system" → `docs/payment-system.md`

### 📋 SINGLE FILE STRUCTURE (`docs/[task-name].md`):

**1. ORIGINAL TASK & GOALS**
- User request
- Expected outcomes

**2. ALL SUBAGENT OPINIONS**
- Research results (web-research-specialist, solution-archeologist, etc.)
- Architecture recommendations (frontend/backend auditors)
- Security & performance insights
- All agent findings in one section

**3. FINAL VERDICT**
- Your decision based on all agent inputs
- Chosen approach and reasoning
- Architecture summary

**4. SIMPLE TODO LIST**
- Create TodoWrite with clear, simple tasks
- Each todo: task name, priority (1-3), files affected
- Mark as completed after each task
- COMMIT after each completed todo

**5. COMMIT STRATEGY**
- Commit message format: "feat(scope): description"
- One commit per completed todo
- Follow Filipino git guidelines (no Claude references)

Output: Complete project documentation and prioritized implementation todos
Mode: READ-ONLY - Documentation creation only, no code files written
User action: Type "go" or "g" to proceed to implementation

## Step 4: ENGINEERING (WRITE MODE ENABLED)
Primary Claude implements the solution based on all previous steps.
No subagents - direct implementation following the architecture.
Output: Working code
Mode: WRITE ENABLED - Files can be created/edited/modified
Condition: If interrupted/cancelled/stopped → Go back to Step 3 ARCHITECT for revision

Type "/steps" followed by your feature request to start from Step 0.

---

## DEBUG (Only when user reports issues - READ-ONLY)
When user reports a problem:
⚡ **PARALLEL DEPLOYMENT (Single Message, Multiple Task Invocations):**
- auto-debugger-fixer
- security-vulnerability-auditor
- performance-optimization-analyzer

📝 **COMPREHENSIVE PROMPTS MUST INCLUDE:**
- Complete error messages and stack traces
- Relevant code sections and file paths
- Steps to reproduce the issue
- Expected vs actual behavior
- Previous debugging attempts
- System environment and configuration
- Specific analysis focus for each agent:
  * auto-debugger-fixer: Root cause analysis and fix strategies
  * security-vulnerability-auditor: Security implications of the bug
  * performance-optimization-analyzer: Performance impact analysis

Output: Combined bug analysis, security report, and performance recommendations
Mode: READ-ONLY - Analysis only, fixes suggested but not applied