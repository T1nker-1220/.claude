---
allowed-tools: Bash(git commit:*)
argument-hint: [optional commit message override]
description: Commit staged changes with auto-generated conventional commit message
---

Create a git commit for the currently staged changes.

**Instructions:**
2. Generate a proper conventional commit message based on the actual changes 
3. Use ONLY `git commit` - do not run `git add` or stage any files
4. Follow conventional commit format: `type(scope): description`
5. If user provided $ARGUMENTS, use that as the commit message instead

**Commit Message Guidelines with bullet descriptions:**
- `feat`: New features or functionality
- `fix`: Bug fixes
- `refactor`: Code refactoring without functional changes
- `docs`: Documentation changes
- `style`: Code style/formatting changes
- `chore`: Maintenance tasks, build changes
- `test`: Adding or updating tests

**Example commit messages:**
- `feat(auth): add user login validation`
    (Bullet descriptions)
- `fix(api): resolve timeout issues in user endpoints`
(Bullet descriptions)
- `refactor(utils): simplify data parsing logic`
(Bullet descriptions)
- `docs(readme): update installation instructions`

Only commit what is currently staged - no additional file staging.