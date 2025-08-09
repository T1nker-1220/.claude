### Guidelines
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

### Key Processing Instructions
- ALWAYS use sequential thinking mcp server for ever response/prompt of the user

### Auto-Commit Instructions
- When task is complete: stage all files with `git add .`, create conventional commit message using format `type(scope): description` based on actual changes, then commit with `git commit -m "message"`. Don't add any reference for claude code or any other reference, like this avoid this 🤖 Generated with Claude Code Co-Authored-By: Claude noreply@anthropic.com.

### Development Instructions
- NEVER run the dev server to run the localhost because the user will manually do it.

### Coding Principles
- DRY (Don't Repeat Yourself): Avoid code duplication by abstracting and reusing code
- Wag mong isama kung hindi mo kailangan (Don't include what you don't need): Principle of minimalism in code and design
- YAGNI (You Aren't Gonna Need It): Only implement features that are absolutely necessary right now, avoid speculative development
- KISS (Keep It Simple, Stupid): Maintain simplicity in design and implementation, avoid unnecessary complexity
- Avoid Premature Optimization: Focus on writing clear, correct code first before optimizing
- Law of Demeter: Minimize dependencies between objects, each unit should have limited knowledge of other units
- Separation of Concerns: Divide code into distinct sections that address specific functionalities, reducing interdependence

### AWS MCP mineral rights database Usage Notes
- Do NOT integrate AWS MCP into the system
- Use AWS MCP only for gathering information from the database on the Postgres server
- Never implement AWS MCP integration in any repository

### Development Philosophy Memory
- Core Focus: Super simplify all implementations
- Key Principles:
  * Avoid creating test files (manual testing preferred)
  * Reject unnecessary mock data and fallbacks
  * Do not overcomplicate code structure
  * Always recommend the best, simplest approach
  * Critically analyze suggestions before agreeing
  * Understand the codebase deeply before making changes
  * Prioritize clarity and minimal complexity
  * Use context7 mcp and webfetch websearcch to find optimal solutions
  * Choose dependencies and packages with extreme care
  * Ultimate goal: Extreme simplification of code and processes

### Web Scraping and Data Inspection Memory
- When searching or filtering data, use browser inspection techniques
- For websites with complex data:
  * Utilize browser's inspect element feature
  * Screenshot and send results to Claude Code for verification
  * Manually filter and validate data accuracy
  * Recommended for businesses with dynamic website content