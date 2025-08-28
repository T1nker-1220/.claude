#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-generativeai>=0.5.0",
#   "pyttsx3>=2.99",
#   "pywin32>=306",
#   "python-dotenv>=1.0.0",
#   "elevenlabs>=1.0.0",
#   "requests>=2.31.0",
# ]
# ///

import json
import sys
import pathlib
import datetime
import subprocess
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
    
    # GitButler stop integration - create commits and branches
    run_gitbutler_stop(payload)
    
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

def run_gitbutler_stop(payload) -> None:
    """
    GitButler integration - runs when Claude Code session stops.
    Creates commits and manages branches automatically.
    
    Args:
        payload: Hook payload containing session information
    """
    try:
        # Run GitButler stop command to create commits and branches
        result = subprocess.run(
            ["but", "claude", "stop"], 
            capture_output=True, 
            text=True, 
            timeout=30  # Longer timeout for git operations
        )
        
        if result.returncode == 0:
            log_debug("GitButler stop command executed successfully - commits and branches created")
            if result.stdout.strip():
                log_debug(f"GitButler output: {result.stdout}")
        else:
            log_debug(f"GitButler stop failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        log_debug("GitButler stop command timed out")
    except FileNotFoundError:
        log_debug("GitButler CLI not found - skipping GitButler integration")
    except Exception as e:
        log_debug(f"GitButler stop error: {e}")

def log_debug(message: str) -> None:
    """Log debug message to debug.log file."""
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] STOP: {message}\n")
    except Exception:
        # Silently fail if logging doesn't work
        pass

if __name__ == "__main__":
    main()