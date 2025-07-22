#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyautogui", "psutil", "pillow"]
# ///

import json
import sys
import pathlib
import subprocess
import datetime
import time
import pyautogui
import psutil

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
        
        # Auto-stage the modified file with git
        stage_file_with_git(file_path)
        
        # Try to trigger VS Code Copilot commit message generation
        trigger_vscode_copilot_commit(file_path)
        
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

def trigger_vscode_copilot_commit(file_path: pathlib.Path) -> None:
    """
    Attempts to trigger VS Code Copilot commit message generation.
    This will only work if VS Code is running and has the source control panel open.
    """
    try:
        # Check if we're in a git repository
        git_root = find_git_root(file_path.parent)
        if not git_root:
            log_debug("Not in a git repository, skipping VS Code Copilot trigger")
            return
            
        # Check if there are staged changes
        if not has_staged_changes(git_root):
            log_debug("No staged changes found, skipping VS Code Copilot trigger")
            return
            
        # Check if VS Code is running
        if not is_vscode_running():
            log_debug("VS Code is not running, skipping Copilot trigger")
            return
            
        log_debug("Attempting to trigger VS Code Copilot commit message generation")
        
        # Try to focus VS Code window first
        focus_vscode_window()
        time.sleep(0.5)
        
        # Open source control panel if not already open
        open_source_control_panel()
        time.sleep(1)
        
        # Click the Copilot sparkle icon (coordinates from screenshot)
        # Note: These coordinates may need adjustment based on screen resolution/scaling
        click_copilot_sparkle_icon()
        
        log_debug("Successfully triggered VS Code Copilot commit generation")
        
    except Exception as e:
        log_debug(f"Error triggering VS Code Copilot: {e}")

def has_staged_changes(git_root: pathlib.Path) -> bool:
    """Check if there are any staged changes in the git repository."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=git_root,
            capture_output=True,
            timeout=5
        )
        # git diff --cached --quiet returns 1 if there are staged changes, 0 if none
        return result.returncode != 0
    except Exception:
        return False

def is_vscode_running() -> bool:
    """Check if VS Code is currently running."""
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'code' in proc.info['name'].lower():
                return True
        return False
    except Exception:
        return False

def focus_vscode_window() -> None:
    """Attempt to bring VS Code window to focus."""
    try:
        # Use Alt+Tab approach to find VS Code window
        # This is a simple approach that may need refinement
        windows = pyautogui.getWindowsWithTitle('Visual Studio Code')
        if windows:
            windows[0].activate()
    except Exception as e:
        log_debug(f"Could not focus VS Code window: {e}")

def open_source_control_panel() -> None:
    """Open the source control panel in VS Code using keyboard shortcut."""
    try:
        # Ctrl+Shift+G opens source control panel
        pyautogui.hotkey('ctrl', 'shift', 'g')
        log_debug("Sent Ctrl+Shift+G to open source control panel")
    except Exception as e:
        log_debug(f"Error opening source control panel: {e}")

def click_copilot_sparkle_icon() -> None:
    """Click the Copilot sparkle icon in the commit message input area."""
    try:
        # Coordinates based on the screenshot provided (may need adjustment)
        # The sparkle icon appears to be around coordinates (228, 124)
        # These coordinates are approximate and may need fine-tuning
        
        # First, try to click in the commit message input area to focus it
        pyautogui.click(175, 124)  # Click in commit message input
        time.sleep(0.3)
        
        # Then click the sparkle icon (slightly to the right)
        pyautogui.click(228, 124)  # Click sparkle icon
        log_debug("Clicked Copilot sparkle icon at coordinates (228, 124)")
        
    except Exception as e:
        log_debug(f"Error clicking Copilot sparkle icon: {e}")

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] POST_TOOL_USE_COPILOT: {message}\n")
    except Exception:
        # Silently fail if logging doesn't work
        pass

if __name__ == "__main__":
    main()