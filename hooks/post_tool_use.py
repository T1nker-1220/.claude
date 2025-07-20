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
    
    try:
        # This hook should only act on successful file modifications
        tool_name = payload.get("tool_name")
        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            print(json.dumps(decision))
            return

        tool_response = payload.get("tool_response", {})
        if not tool_response.get("success", False) and "filePath" not in tool_response:
             print(json.dumps(decision))
             return
             
        # Extract the file path that was modified
        file_path_str = get_file_path(payload)
        if not file_path_str:
            log_debug(f"Could not determine file path from payload for tool {tool_name}")
            print(json.dumps(decision))
            return

        file_path = pathlib.Path(file_path_str)
        
        # Only lint TypeScript files
        if file_path.suffix not in [".ts", ".tsx"]:
            print(json.dumps(decision))
            return

        log_debug(f"Detected change in TypeScript file: {file_path}. Running linter.")

        # Run the linter and check for errors
        has_errors, error_report = run_linter(file_path)

        if has_errors:
            log_debug(f"Linter found errors. Blocking and injecting feedback.")
            # If errors are found, block and construct a new prompt for Claude
            decision = {
                "decision": "block",
                "reason": (
                    f"I just ran the linter on `{file_path.name}` after your changes, and it found the following issues. "
                    "Please fix them now.\n\n"
                    f"Linter Report:\n{error_report}"
                )
            }

    except Exception as e:
        log_debug(f"Error in post_tool_use.py linter hook: {e}")
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

def run_linter(file_path: pathlib.Path) -> tuple[bool, str]:
    """
    Runs ESLint on the specified file and returns a formatted report.
    
    Returns:
        A tuple: (has_errors: bool, report: str)
    """
    project_root = find_project_root(file_path)
    if not project_root:
        log_debug(f"Could not find project root (package.json) for file {file_path}")
        return False, ""

    # Use npx to ensure we're using the project's local ESLint install
    # --format json makes the output easily and reliably parsable
    command = ["npx", "eslint", "--format", "json", str(file_path)]

    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True # shell=True can be more reliable for npx on Windows
        )

        if result.returncode == 0 and not result.stdout.strip():
            log_debug("Linter ran successfully with no issues.")
            return False, ""
            
        # ESLint with --format json outputs to stdout even for errors
        lint_output = json.loads(result.stdout)
        
        # The output is an array of file results. We only linted one file.
        if not lint_output or not lint_output[0]['messages']:
            log_debug("Linter ran, no messages found.")
            return False, ""

        error_report = format_error_report(lint_output)
        return True, error_report

    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        log_debug(f"Linter execution failed: {e}")
        return False, ""
    except Exception as e:
        log_debug(f"An unexpected error occurred during linting: {e}")
        return False, ""


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

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] POST_TOOL_USE_LINTER: {message}\n")
    except Exception:
        # Silently fail if logging doesn't work
        pass

if __name__ == "__main__":
    main()