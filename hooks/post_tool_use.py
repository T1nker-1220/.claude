#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31.0",
# ]
# ///

import json
import sys
import pathlib
import datetime
import re

def check_task_chaining(payload) -> dict:
    """
    Check if we should prompt Claude to chain to the next logical task.
    Returns dict with should_prompt and reason.
    """
    try:
        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input", {})
        
        # Only check for successful Write/Edit operations
        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            return {"should_prompt": False}
            
        # Check if the tool output indicates success
        tool_response = payload.get("tool_response", {})
        success = tool_response.get("success", False)
        if isinstance(tool_response, dict) and "filePath" in tool_response:
            success = True

        if not success:
            return {"should_prompt": False}

        # Get the content that was written or added
        content_added = ""
        if "content" in tool_input:  # From Write tool
            content_added = tool_input["content"]
        elif "new_string" in tool_input:  # From Edit tool
            content_added = tool_input["new_string"]

        if not content_added:
            return {"should_prompt": False}

        # Check if the added content looks like a new function or class
        # This is a simple but effective check for Python and JavaScript/TypeScript
        if re.search(r'^\s*(def|class|function|const|let|var)\s+\w+', content_added, re.MULTILINE):
            log_debug(f"Detected new function/class in {tool_name} operation. Prompting for tests.")
            return {
                "should_prompt": True,
                "reason": "You have successfully added a new function or class. As the next logical step, please write a comprehensive unit test for the code you just added."
            }
            
        return {"should_prompt": False}
        
    except Exception as e:
        log_debug(f"Error in check_task_chaining: {e}")
        return {"should_prompt": False}

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] POST_TOOL_USE_TASK_CHAIN: {message}\n")
    except Exception:
        pass  # Silently fail if logging doesn't work

def main() -> None:
    """
    Simplified PostToolUse hook handler.
    Now just logs tool usage - smart commits moved to Stop hook to avoid timing issues.
    """
    try:
        # Read JSON payload from stdin
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Just log tool usage to logs directory
        # Smart git commits now happen in Stop hook (no timing constraints)
        log_to_logs_directory(payload)
        
        # Check for automated task chaining opportunities
        task_chain_decision = check_task_chaining(payload)
        if task_chain_decision.get("should_prompt", False):
            # Return early to interrupt Claude and prompt for next task
            print(json.dumps({"decision": "block", "reason": task_chain_decision["reason"]}))
            sys.exit(0)
        
        # Exit with success
        sys.exit(0)
        
    except Exception as e:
        print(f"Hook processing error: {e}", file=sys.stderr)
        sys.exit(1)

def log_to_logs_directory(payload) -> None:
    """
    Log PostToolUse event to logs directory.
    
    Args:
        payload: Hook payload containing tool information
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
            "hook_event_name": payload.get("hook_event_name", "PostToolUse")
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"Failed to log to logs directory: {e}", file=sys.stderr)

def check_task_chaining(payload) -> dict:
    """
    Check if we should prompt Claude to chain to the next logical task.
    Returns dict with should_prompt and reason.
    """
    try:
        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input", {})
        
        # Only check for successful Write/Edit operations
        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            return {"should_prompt": False}
            
        # Check if the tool output indicates success
        tool_response = payload.get("tool_response", {})
        success = tool_response.get("success", False)
        if isinstance(tool_response, dict) and "filePath" in tool_response:
            success = True

        if not success:
            return {"should_prompt": False}

        # Get the content that was written or added
        content_added = ""
        if "content" in tool_input:  # From Write tool
            content_added = tool_input["content"]
        elif "new_string" in tool_input:  # From Edit tool
            content_added = tool_input["new_string"]

        if not content_added:
            return {"should_prompt": False}

        # Check if the added content looks like a new function or class
        # This is a simple but effective check for Python and JavaScript/TypeScript
        if re.search(r'^\s*(def|class|function|const|let|var)\s+\w+', content_added, re.MULTILINE):
            log_debug(f"Detected new function/class in {tool_name} operation. Prompting for tests.")
            return {
                "should_prompt": True,
                "reason": "You have successfully added a new function or class. As the next logical step, please write a comprehensive unit test for the code you just added."
            }
            
        return {"should_prompt": False}
        
    except Exception as e:
        log_debug(f"Error in check_task_chaining: {e}")
        return {"should_prompt": False}

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] POST_TOOL_USE_TASK_CHAIN: {message}\n")
    except Exception:
        pass  # Silently fail if logging doesn't work

if __name__ == "__main__":
    main()