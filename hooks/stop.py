#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-generativeai>=0.5.0",
#   "pyttsx3>=2.99",
#   "pywin32>=306",
# ]
# ///

import json
import sys
import pathlib
import datetime
from utils.smart_voice_notify import process_stop_notification

def main() -> None:
    """
    Simple Stop hook handler that delegates to smart voice utilities.
    """
    try:
        # Read JSON payload from stdin
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        # If JSON parsing fails, create basic payload
        payload = {"error": f"JSON decode error: {e}", "hook_event_name": "Stop"}
    except Exception as e:
        # Handle any other input errors  
        payload = {"error": f"Input error: {e}", "hook_event_name": "Stop"}
    
    # Log to logs directory
    log_to_logs_directory(payload)
    
    
    # Process using utility functions
    process_stop_notification(payload)


def log_to_logs_directory(payload) -> None:
    """
    Log Stop event to logs directory.
    
    Args:
        payload: Hook payload containing session information
    """
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "stop.json"
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "Stop",
            "session_id": payload.get("session_id", "unknown"),
            "stop_hook_active": payload.get("stop_hook_active", False),
            "cwd": payload.get("cwd", "unknown"),
            "transcript_path": payload.get("transcript_path", "unknown"),
            "hook_event_name": payload.get("hook_event_name", "Stop"),
            "error": payload.get("error")  # Include any errors that occurred
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"Failed to log to logs directory: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()