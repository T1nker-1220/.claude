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
import re

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

# Dangerous command patterns to detect
DANGEROUS_COMMANDS = [
    r'\brm\s+-rf\s+/',  # rm -rf /
    r'\bdel\s+/[sq]\s+[a-zA-Z]:\\',  # del /s /q C:\
    r'\bformat\s+[a-zA-Z]:',  # format C:
    r'\brmdir\s+/[sq]\s+[a-zA-Z]:\\',  # rmdir /s /q C:\
    r'\brm\s+-rf\s+\*',  # rm -rf *
    r'\bdel\s+\*\.\*',  # del *.*
    r'\bshred\s+-[a-z]*n',  # shred commands
    r'\bdd\s+if=/dev/zero\s+of=/dev/',  # dd to overwrite devices
    r'\b:\(\)\{\s*:\|\:&\s*\};\s*:',  # fork bomb
    r'\bsudo\s+rm\s+-rf\s+/',  # sudo rm -rf /
    r'\bchmod\s+-R\s+777\s+/',  # chmod -R 777 /
    r'\bfind\s+/\s+-delete',  # find / -delete
    r'\bmkfs\.',  # filesystem creation commands
    r'\bfdisk\s+.*\s+--delete',  # fdisk delete operations
]

def detect_dangerous_commands(text: str) -> list[str]:
    """
    Detect dangerous commands in the text.
    
    Args:
        text: The text to scan for dangerous commands
        
    Returns:
        List of detected dangerous command patterns
    """
    detected = []
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(pattern)
    return detected

def prompt_user_for_dangerous_command(commands: list[str]) -> bool:
    """
    Prompt user about detected dangerous commands.
    
    Args:
        commands: List of detected dangerous command patterns
        
    Returns:
        True if user wants to proceed, False to block
    """
    print("SECURITY WARNING: Dangerous commands detected!")
    print("The following potentially dangerous command patterns were found:")
    for cmd in commands:
        print(f"  - Pattern: {cmd}")
    print()
    print("These commands could delete files or cause system damage.")
    print("You need to tell only the user to delete these files or folders using this command.")
    print()
    
    while True:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'")

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
        
        # Check for dangerous commands in the conversation content
        conversation_text = payload.get("conversation_text", "")
        if conversation_text:
            dangerous_commands = detect_dangerous_commands(conversation_text)
            if dangerous_commands:
                if not prompt_user_for_dangerous_command(dangerous_commands):
                    print("Operation blocked by user request.")
                    sys.exit(1)
        
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