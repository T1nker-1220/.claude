#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyttsx3>=2.99",
# ]
# ///

import json
import sys
import pathlib
import datetime
from utils.smart_voice_notify import process_subagent_notification

def main() -> None:
    """
    Handle SubagentStop events - runs when Task tool subagents complete.
    """
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        payload = {"error": f"JSON decode error: {e}", "hook_event_name": "SubagentStop"}
    except Exception as e:
        payload = {"error": f"Input error: {e}", "hook_event_name": "SubagentStop"}
    
    # Log the event
    log_subagent_stop(payload)
    
    # Use the smart voice notification system
    process_subagent_notification(payload)

def log_subagent_stop(payload) -> None:
    """Log SubagentStop event to logs directory."""
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "subagent_stop.json"
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "SubagentStop",
            "session_id": payload.get("session_id", "unknown"),
            "task_description": payload.get("task_description", ""),
            "tools_used": payload.get("tools_used", []),
            "duration": payload.get("duration", ""),
            "hook_event_name": payload.get("hook_event_name", "SubagentStop"),
            "error": payload.get("error")
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        print(f"Failed to log subagent stop: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()