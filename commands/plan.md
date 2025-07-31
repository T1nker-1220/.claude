# Team Planning Command
This command triggers a comprehensive team planning workflow where all specialist agents work together simultaneously, followed by user approval and implementation phases.

## Command Usage
- `/plan` - Primary agent asks for task
- `/plan "<specific task>"` - Primary agent validates the provided task

## Pre-Phase: Task Validation (Primary Agent Only)
**ALWAYS TRIGGERED** - regardless of how `/plan` is used:

**When `/plan` is used without arguments:**
1. **Primary Agent** asks user: "What specific task do you want to plan and implement?"
2. User provides task details
3. **Primary Agent** analyzes and confirms (go to step 4)

**When `/plan "<specific task>"` is used:**
1. **Primary Agent** receives the explicit task
2. **Primary Agent** analyzes and confirms (go to step 4)

**Step 4 - Iterative Clarification Loop:**
**Primary Agent** enters clarification loop until ALL scopes are clear:

1. **Analyze & Summarize**: "Based on your request, I understand you want to: [DETAILED SUMMARIZATION]"

2. **Identify Unclear Areas**: If any scope is unclear or missing:
   - "I need clarification on these areas: [LIST SPECIFIC UNCLEAR POINTS]"
   - "Can you provide more details about [SPECIFIC AREA]?"
   - Wait for user response

3. **Loop Back**: After user provides more info, return to step 1 with updated understanding

4. **Continue Loop**: Repeat steps 1-3 until ALL scopes are clarified

5. **Final Confirmation**: When everything is clear:
   - **Primary Agent**: "FINAL SUMMARY: Here's my complete understanding of your task: [COMPREHENSIVE SUMMARY]"
   - "All scopes are now clear. Do you confirm this is exactly what you want me to plan and implement?"
   - **User must explicitly confirm**: "Yes, proceed" or similar
   - If user says anything other than clear approval, return to clarification loop

**Only proceed to Phase 1 when:**
- ALL scopes are clarified
- User gives explicit final confirmation
- No ambiguity remains

When final confirmation is received, the workflow proceeds as follows:

## Phase 1: Complete Multi-Agent Analysis (All Simultaneous)
All 8 agents execute together sabay-sabay:
- **[PM1]** `pm1-project-scanner` - Comprehensive repository scan, coding conventions extraction, and initial task list
- **[PM2]** `pm2-roadmap-prioritizer` - Independent analysis with conflict detection and prioritized roadmap
- **[VALIDATION]** `plan-validation-analyst` - Quality assurance and validation of all outputs
- **[WEB]** `web-research-specialist` - Latest technology research and best practices gathering
- **[ARCH]** `arch-planner` - Merge all outputs, facilitate trade-off decisions, create architecture plan
- **[BACKEND]** `senior-backend-architect` - Expert backend guidance and architectural review
- **[FRONTEND]** `senior-frontend-architect` - Expert frontend guidance and architectural review
- **[UIUX]** `uiux-auditor` - Style guide compliance, accessibility, responsive design audit (conditional on UI changes)

## Phase 2: User Approval Gate
**Primary Agent** presents brief summary to user:
- Overview of what happened in Phase 1
- Key findings and recommendations
- Proposed implementation plan
- **ASK USER**: "Do you approve this plan for implementation?"

### If User Approves:
- Primary agent proceeds to **Phase 3: Implementation**
- Execute the approved plan
- No subagents involved in implementation

### If User Disagrees:
- Primary agent asks: "What specific changes do you want?"
- Based on user feedback, re-trigger specific subagents assigned to those areas
- Return to Phase 1 with focused revisions
- Present updated plan for approval again

## Phase 3: Implementation (Primary Agent Only)
- Primary agent implements the approved plan
- Follow all coding principles and user guidelines
- Complete all required tasks
- No subagent involvement in actual implementation

## Workflow Rules
1. **Phase 1**: All 8 agents work simultaneously (sabay-sabay)
2. **Phase 2**: Primary agent summarizes and seeks user approval
3. **Phase 3**: Primary agent implements if approved, or revises if not
4. **Authority**: Only primary agent implements and edits code
5. **Iteration**: Process repeats until user approves the plan