#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import sys
import pathlib
import subprocess
import datetime

def main() -> None:
    """
    PostToolUse hook to provide a silent, automatic linter feedback loop for TypeScript files.
    """
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If there's no payload, we can't do anything. Approve to avoid blocking.
        print(json.dumps({"decision": "approve"}))
        return

    # Default decision is to let the workflow continue
    decision = {"decision": "approve"}
    quality_result = ""
    
    try:
        # This hook should only act on successful file modifications
        tool_name = payload.get("tool_name")
        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            log_to_structured_logs(payload, quality_result)
            print(json.dumps(decision))
            return

        tool_response = payload.get("tool_response", {})
        if not tool_response.get("success", False) and "filePath" not in tool_response:
            log_to_structured_logs(payload, "Tool operation failed")
            print(json.dumps(decision))
            return
             
        # Extract the file path that was modified
        file_path_str = get_file_path(payload)
        if not file_path_str:
            log_debug(f"Could not determine file path from payload for tool {tool_name}")
            log_to_structured_logs(payload, "Could not determine file path")
            print(json.dumps(decision))
            return

        file_path = pathlib.Path(file_path_str)
        
        # Auto-stage the modified file with git
        stage_file_with_git(file_path)
        
        # Enhanced TypeScript/JavaScript file processing
        if file_path.suffix not in [".ts", ".tsx", ".js", ".jsx"]:
            log_debug(f"File modified: {file_path}. Skipping TypeScript quality checks.")
            quality_result = "Skipped - not a TypeScript/JavaScript file"
            log_to_structured_logs(payload, quality_result)
            print(json.dumps(decision))
            return

        log_debug(f"Detected change in TypeScript/JS file: {file_path}. Running quality checks.")

        # Run comprehensive TypeScript quality checks
        quality_issues = run_typescript_quality_checks(file_path)
        quality_result = quality_issues if quality_issues else "No issues found"

        if quality_issues:
            log_debug(f"Quality issues found. Providing feedback.")
            decision = {
                "decision": "block",
                "reason": (
                    f"🔧 TypeScript Quality Check Results for `{file_path.name}`:\n\n"
                    f"{quality_issues}\n\n"
                    "Please address these issues for better code quality."
                )
            }

        # Log everything to structured logs
        log_to_structured_logs(payload, quality_result)

    except Exception as e:
        log_debug(f"Error in post_tool_use.py linter hook: {e}")
        quality_result = f"Error: {str(e)}"
        log_to_structured_logs(payload, quality_result)
        # In case of any error in the hook itself, always approve to not break the user's flow
        decision = {"decision": "approve"}

    # Output the final decision to Claude
    print(json.dumps(decision))


def get_file_path(payload: dict) -> str:
    """Extracts the file path from various possible locations in the payload."""
    tool_input = payload.get("tool_input", {})
    tool_response = payload.get("tool_response", {})
    
    # Path can be in tool_input or tool_response
    if "file_path" in tool_input:
        return tool_input["file_path"]
    if isinstance(tool_response, dict) and "filePath" in tool_response:
        return tool_response["filePath"] # Handle the camelCase key from Write/Edit tools
    return ""

def run_typescript_quality_checks(file_path: pathlib.Path) -> str:
    """
    Comprehensive TypeScript quality checks: ESLint auto-fix, Prettier, and tsc.
    
    Returns:
        String with quality issues found, empty if all good
    """
    project_root = find_project_root(file_path)
    if not project_root:
        log_debug(f"Could not find project root (package.json) for file {file_path}")
        return ""

    quality_report = []
    
    try:
        # 1. Run Prettier formatting first
        prettier_issues = run_prettier_format(file_path, project_root)
        if prettier_issues:
            quality_report.append(f"📝 **Prettier Formatting:**\n{prettier_issues}")
        
        # 2. Run ESLint with auto-fix
        eslint_issues = run_eslint_autofix(file_path, project_root)
        if eslint_issues:
            quality_report.append(f"🔍 **ESLint Issues:**\n{eslint_issues}")
        
        # TypeScript compilation check removed due to module resolution issues
        
        return "\n\n".join(quality_report)
        
    except Exception as e:
        log_debug(f"Error in TypeScript quality checks: {e}")
        return ""

def run_prettier_format(file_path: pathlib.Path, project_root: pathlib.Path) -> str:
    """Run Prettier formatting and return issues if any."""
    try:
        # First check if file needs formatting
        check_cmd = ["npx", "prettier", "--check", str(file_path)]
        check_result = subprocess.run(
            check_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=15,
            shell=True
        )
        
        if check_result.returncode == 0:
            log_debug("Prettier: File already formatted correctly")
            return ""
        
        # Auto-format the file
        format_cmd = ["npx", "prettier", "--write", str(file_path)]
        format_result = subprocess.run(
            format_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=15,
            shell=True
        )
        
        if format_result.returncode == 0:
            log_debug("Prettier: File formatted successfully")
            return "✅ File has been auto-formatted with Prettier"
        else:
            return f"❌ Prettier formatting failed: {format_result.stderr}"
            
    except Exception as e:
        log_debug(f"Prettier error: {e}")
        return f"❌ Prettier error: {str(e)}"

def run_eslint_autofix(file_path: pathlib.Path, project_root: pathlib.Path) -> str:
    """Run ESLint with auto-fix and return remaining issues."""
    try:
        # Run ESLint with auto-fix
        fix_cmd = ["npx", "eslint", "--fix", "--format", "json", str(file_path)]
        result = subprocess.run(
            fix_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True
        )
        
        if result.returncode == 0 and not result.stdout.strip():
            log_debug("ESLint: No issues found")
            return ""
        
        if result.stdout.strip():
            lint_output = json.loads(result.stdout)
            if lint_output and lint_output[0].get('messages'):
                error_report = format_error_report(lint_output)
                return error_report
        
        log_debug("ESLint: Auto-fixed successfully")
        return "✅ ESLint auto-fixes applied"
        
    except Exception as e:
        log_debug(f"ESLint error: {e}")
        return f"❌ ESLint error: {str(e)}"




def format_error_report(lint_output: list) -> str:
    """Formats the JSON output from ESLint into a human-readable string for Claude."""
    report_lines = []
    # We only process the first file in the output, as we only lint one at a time
    file_result = lint_output[0]
    
    for message in file_result.get('messages', []):
        line = message.get('line', 'N/A')
        column = message.get('column', 'N/A')
        rule = message.get('ruleId', 'general')
        text = message.get('message', 'No message')
        severity = "ERROR" if message.get('severity') == 2 else "WARNING"
        
        report_lines.append(f"- {severity} at L{line}:C{column} ({rule}): {text}")
        
    return "\n".join(report_lines)

def find_project_root(start_path: pathlib.Path) -> pathlib.Path | None:
    """Finds the project root by looking for a package.json file."""
    current = start_path.parent
    while current != current.parent: # Stop at the filesystem root
        if (current / "package.json").exists():
            return current
        current = current.parent
    return None

def stage_file_with_git(file_path: pathlib.Path) -> None:
    """
    Stages the specified file with git add.
    Fails silently if not in a git repository or if git command fails.
    """
    try:
        # Check if we're in a git repository by looking for .git directory
        current_dir = file_path.parent
        git_root = find_git_root(current_dir)
        
        if not git_root:
            log_debug(f"File {file_path} is not in a git repository. Skipping git staging.")
            return
            
        # Stage the file using git add
        command = ["git", "add", str(file_path)]
        result = subprocess.run(
            command,
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log_debug(f"Successfully staged file: {file_path}")
        else:
            log_debug(f"Git staging failed for {file_path}: {result.stderr.strip()}")
            
    except Exception as e:
        log_debug(f"Error during git staging for {file_path}: {e}")

def find_git_root(start_path: pathlib.Path) -> pathlib.Path | None:
    """Finds the git repository root by looking for a .git directory."""
    current = start_path
    while current != current.parent:  # Stop at the filesystem root
        if (current / ".git").exists():
            return current
        current = current.parent
    return None

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] POST_TOOL_USE: {message}\n")
    except Exception:
        # Silently fail if logging doesn't work
        pass

def log_to_structured_logs(payload: dict, quality_result: str = "") -> None:
    """
    Log PostToolUse event to structured logs directory.
    
    Args:
        payload: Hook payload containing tool information
        quality_result: TypeScript quality check results
    """
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "post_tool_use.json"
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "PostToolUse",
            "session_id": payload.get("session_id", "unknown"),
            "tool_name": payload.get("tool_name", "unknown"),
            "tool_input": payload.get("tool_input", {}),
            "tool_response": payload.get("tool_response", {}),
            "cwd": payload.get("cwd", "unknown"),
            "transcript_path": payload.get("transcript_path", "unknown"),
            "hook_event_name": payload.get("hook_event_name", "PostToolUse"),
            "quality_result": quality_result if quality_result else None
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        log_debug(f"Failed to log to structured logs: {e}")

if __name__ == "__main__":
    main()