This will going to trigger if the user use the command of `/task` @REQUIREMENTS-GUIDELINES.md

### Guidelines
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

### Project References
- Puppeteer instructions located at: c:\Users\NATH\.claude\puppeter-instructions.md

### Key Processing Instructions
- ALWAYS use sequential thinking mcp server for ever response of the user

### Auto-Commit Instructions
When asked to create git commits automatically via stop hook:
1. Use `git add .` to stage all changes
2. Generate conventional commit messages based on actual file changes
3. Use format: `type(scope): description`
4. Examples: `feat(hooks): simplify auto-commit system`, `fix(api): handle null responses`
5. Execute commit with `git commit -m "message"`