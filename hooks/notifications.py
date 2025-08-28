#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyttsx3>=2.90",
# ]
# ///

import json
import sys
import pathlib
import datetime
from utils.smart_voice_notify import process_notification

def main() -> None:
    """
    Simplified notification handler - just voice notifications.
    """
    try:
        # Read JSON payload from stdin
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        # If JSON parsing fails, create error payload
        payload = {"error": f"JSON decode error: {e}", "hook_event_name": "Notification"}
    except Exception as e:
        # Handle any other input errors
        payload = {"error": f"Input error: {e}", "hook_event_name": "Notification"}
    
    # Validate that this is a Notification hook event
    if payload.get("hook_event_name") != "Notification" and "transcript_path" not in payload:
        # If it's not a proper notification, try to process anyway
        payload["hook_event_name"] = "Notification"
    
    # Log to logs directory
    log_to_logs_directory(payload)
    
    try:
        # Process with voice notification system
        process_notification(payload)
        
    except Exception as e:
        # Fallback if processing fails - use centralized voice function
        try:
            from utils.smart_voice_notify import speak
            speak("Claude notification error")
        except:
            # If even centralized TTS fails, just exit silently
            pass

def log_to_logs_directory(payload) -> None:
    """
    Log Notification event to logs directory.
    
    Args:
        payload: Hook payload containing notification information
    """
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "notifications.json"
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "Notification",
            "session_id": payload.get("session_id", "unknown"),
            "message": payload.get("message", ""),
            "cwd": payload.get("cwd", "unknown"),
            "transcript_path": payload.get("transcript_path", "unknown"),
            "hook_event_name": payload.get("hook_event_name", "Notification"),
            "error": payload.get("error")  # Include any errors that occurred
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"Failed to log to logs directory: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()