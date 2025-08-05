### Serena Usage and Meta-Cognition ALWAYS USE THIS MCP SERVER.
#### Code Exploration Tools
- find_symbol: Find functions, classes, variables by name across your codebase
- get_symbols_overview: Get high-level view of what's defined in files/directories
- find_referencing_symbols: See where symbols are used throughout your code
- search_for_pattern: Search for text patterns with regex support

#### Intelligent Code Editing
- replace_symbol_body: Replace entire function/class definitions precisely
- insert_after_symbol / insert_before_symbol: Add code relative to existing symbols
- create_text_file: Create new files
- replace_lines: Line-based editing when needed

#### Project Management
- activate_project: Switch between different codebases
- write_memory / read_memory: Store and retrieve project knowledge
- onboarding: Let Serena learn about your project structure

#### Execution & Testing
- execute_shell_command: Run tests, builds, linting, any shell commands
- restart_language_server: Refresh language server if needed

#### Workflow Intelligence
- think_about_collected_information: Assist in planning
- summarize_changes: Document what was accomplished
- switch_modes: Change behavior (planning → editing → testing)

#### Usage Patterns
##### Analysis Workflow
- Activate project: "Activate the project /path/to/my_code"
- Explore structure: Use get_symbols_overview to understand codebase organization
- Find relevant code: Use find_symbol to locate specific functionality
- Trace dependencies: Use find_referencing_symbols to see how code is connected

##### Development Workflow
- Plan first: Switch to planning mode, analyze requirements
- Implement: Use symbol-level editing tools to make precise changes
- Test: Use execute_shell_command to run tests and verify changes
- Iterate: Serena can debug by reading test output and making corrections

#### Context & Modes System
- Contexts: desktop-app, agent, ide-assistant - define the environment
- Modes: planning, editing, interactive, one-shot - define the task type
- Switch modes dynamically: "Switch to planning and one-shot modes"