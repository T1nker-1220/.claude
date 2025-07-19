#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import sys
import pathlib
import re
import datetime

def main() -> None:
    """
    SubagentStop hook to automatically chain tasks.
    If a new function is written, it prompts Claude to write a unit test.
    """
    # Always log that we were called
    log_debug("SubagentStop hook triggered")
    
    try:
        payload = json.load(sys.stdin)
        log_debug(f"Received payload: {json.dumps(payload, indent=2)}")
    except json.JSONDecodeError as e:
        log_debug(f"Failed to parse JSON payload: {e}")
        # If there's no payload, there's nothing to do.
        print(json.dumps({"decision": "approve"}))
        sys.exit(0)

    decision = {"decision": "approve"}
    
    try:
        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input", {})
        
        # We only care about successful Write/Edit operations
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            # Check if the tool output indicates success
            tool_response = payload.get("tool_response", {})
            success = tool_response.get("success", False)
            if isinstance(tool_response, dict) and "filePath" in tool_response:
                success = True

            if success:
                # Get the content that was written or added
                content_added = ""
                if "content" in tool_input: # From Write tool
                    content_added = tool_input["content"]
                elif "new_string" in tool_input: # From Edit tool
                    content_added = tool_input["new_string"]

                # Check if the added content looks like a new function or class
                # This is a simple but effective check for Python and JavaScript/TypeScript
                if re.search(r'^\s*(def|class|function|const|let|var)\s+\w+', content_added, re.MULTILINE):
                    log_debug(f"Detected new function/class in {tool_name} operation. Prompting for tests.")
                    decision = {
                        "decision": "block",
                        "reason": "You have successfully added a new function or class. As the next logical step, please write a comprehensive unit test for the code you just added."
                    }
    except Exception as e:
        log_debug(f"Error in subagent_stop.py: {e}")
        # Fail open to not interrupt the user's workflow
        decision = {"decision": "approve"}

    # Log the decision and output it to Claude
    log_debug(f"SubagentStop decision: {decision['decision']}")
    print(json.dumps(decision))
    sys.exit(0)

def log_debug(message: str) -> None:
    """Logs a debug message to the central debug log."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] SUBAGENT_STOP: {message}\n")
    except Exception:
        pass # Silently fail if logging doesn't work

if __name__ == "__main__":
    main()