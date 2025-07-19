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

if __name__ == "__main__":
    main()