#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyttsx3>=2.99",
#   "pywin32>=306",
# ]
# ///

import json
import sys
import pathlib
import datetime

# Add utils directory to Python path for importing smart_voice_notify
utils_path = pathlib.Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from smart_voice_notify import process_compact_notification
except ImportError as e:
    # Fallback if import fails - use simplified approach
    def fallback_speak(text: str):
        """Simplified fallback TTS"""
        pass
    
    def process_compact_notification(payload: dict):
        # Simple fallback implementation  
        fallback_speak("Compacting the conversation")

def main():
    """
    PreCompact hook entry point.
    Called when Claude is about to compact the conversation.
    """
    try:
        # Read the payload from stdin
        payload_json = sys.stdin.read().strip()
        
        if not payload_json:
            # No payload, default to automatic
            payload = {"compact_type": "automatic"}
        else:
            payload = json.loads(payload_json)
        
        # Log to logs directory
        log_to_logs_directory(payload)
        
        # Process the compact notification using the smart voice notify system
        process_compact_notification(payload)
        
    except json.JSONDecodeError:
        # Fallback for invalid JSON
        process_compact_notification({"compact_type": "automatic"})
    except Exception as e:
        # Ultimate fallback - use centralized voice if possible
        try:
            from smart_voice_notify import speak
            speak("Compacting the conversation")
        except:
            # If all else fails, just exit silently
            pass

def log_to_logs_directory(payload) -> None:
    """
    Log PreCompact event to logs directory.
    
    Args:
        payload: Hook payload containing compact information
    """
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "pre_compact.json"
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "PreCompact",
            "session_id": payload.get("session_id", "unknown"),
            "trigger": payload.get("trigger", "unknown"),
            "custom_instructions": payload.get("custom_instructions", ""),
            "compact_type": payload.get("compact_type", "unknown"),
            "cwd": payload.get("cwd", "unknown"),
            "transcript_path": payload.get("transcript_path", "unknown"),
            "hook_event_name": payload.get("hook_event_name", "PreCompact")
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"Failed to log to logs directory: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()