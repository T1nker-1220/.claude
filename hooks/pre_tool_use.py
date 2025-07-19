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
import re
import pathlib
import datetime
from typing import Dict, Any, List, Tuple

# Add utils directory to Python path for importing smart_voice_notify
utils_path = pathlib.Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from smart_voice_notify import speak
    VOICE_AVAILABLE = True
except ImportError:
    try:
        import pyttsx3
        def speak(text: str):
            eng = pyttsx3.init()
            eng.setProperty("rate", 185)
            eng.say(text)
            eng.runAndWait()
        VOICE_AVAILABLE = True
    except ImportError:
        VOICE_AVAILABLE = False

def main() -> None:
    """
    PreToolUse hook handler - Deletion prevention system and tool logging.
    Blocks dangerous deletion operations targeting critical directories.
    Logs all tool usage for audit trail.
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
        # Log all tool usage to logs directory
        log_to_logs_directory(payload)
        
        # Process deletion prevention check
        result = process_deletion_check(payload)
        
        # Output the decision as JSON
        print(json.dumps(result))
        
        # Exit with appropriate code
        sys.exit(0 if result.get("decision") == "approve" else 1)
        
    except Exception as e:
        # Log error and allow operation (fail-open for safety)
        log_debug(f"Hook processing error: {e}")
        print(json.dumps({"decision": "approve"}))
        sys.exit(0)

def process_deletion_check(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Main deletion prevention logic.
    
    Args:
        payload: JSON payload from Claude Code containing tool information
        
    Returns:
        Dict with decision and optional reason
    """
    # Only process Bash tool calls
    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        return {"decision": "approve"}
    
    # Extract the bash command
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    
    if not command:
        return {"decision": "approve"}
    
    # Check for dangerous deletion patterns
    is_dangerous, reason = is_dangerous_deletion(command)
    
    if is_dangerous:
        # Log the blocked operation
        log_blocked_operation(payload, command, reason)
        
        # Voice notification for blocked command
        notify_blocked_command(command, reason)
        
        return {
            "decision": "block",
            "reason": f"BLOCKED: {reason}\nCommand: {command}\n\nThis operation was blocked to prevent accidental deletion of critical files/directories."
        }
    
    return {"decision": "approve"}

def is_dangerous_deletion(command: str) -> Tuple[bool, str]:
    """
    Check if a bash command contains dangerous deletion patterns.
    
    Args:
        command: The bash command to analyze
        
    Returns:
        Tuple of (is_dangerous: bool, reason: str)
    """
    # Normalize command for analysis
    cmd_lower = command.lower().strip()
    
    # Define dangerous deletion patterns
    dangerous_patterns = [
        # Unix/Linux rm patterns
        (r'\brm\s+.*-[rf]*r[rf]*\s+[./]', "Recursive rm command detected"),
        (r'\brm\s+.*-[rf]*f[rf]*\s+[./]', "Force rm command detected"),
        (r'\brm\s+-rf\b', "rm -rf detected"),
        (r'\brm\s+-fr\b', "rm -fr detected"),
        (r'\brm\s+--recursive\b', "rm --recursive detected"),
        (r'\brm\s+--force\b', "rm --force detected"),
        (r'\brm\s+-r\b', "rm -r detected"),
        (r'\brm\s+-f\b', "rm -f detected"),
        
        # Glob patterns for destructive commands
        (r'\brm\s+.*\*', "rm with glob pattern detected"),
        (r'\brm\s+.*\?', "rm with glob pattern detected"),
        (r'\brm\s+.*\[.*\]', "rm with glob pattern detected"),
        (r'\brm\s+.*\{.*\}', "rm with brace expansion detected"),
        (r'\bdel\s+.*\*', "del with glob pattern detected"),
        (r'\bdel\s+.*\?', "del with glob pattern detected"),
        (r'\bremove-item\s+.*\*', "Remove-Item with glob pattern detected"),
        (r'\bremove-item\s+.*\?', "Remove-Item with glob pattern detected"),
        (r'\brm\s+.*\.\*', "rm with dot glob pattern detected"),
        (r'\bdel\s+.*\.\*', "del with dot glob pattern detected"),
        (r'\bremove-item\s+.*\.\*', "Remove-Item with dot glob pattern detected"),
        
        # Windows CMD deletion patterns
        (r'\brmdir\s+/s\b', "rmdir /s detected"),
        (r'\brmdir\s+.*\s+/s\b', "rmdir with /s flag detected"),
        (r'\brmdir\s+/q\b', "rmdir /q detected"),
        (r'\brmdir\s+.*\s+/q\b', "rmdir with /q flag detected"),
        (r'\bdel\s+/s\b', "del /s detected"),
        (r'\bdel\s+.*\s+/s\b', "del with /s flag detected"),
        (r'\bdel\s+/q\b', "del /q detected"),
        (r'\bdel\s+.*\s+/q\b', "del with /q flag detected"),
        (r'\bdel\s+/f\b', "del /f detected"),
        (r'\bdel\s+.*\s+/f\b', "del with /f flag detected"),
        (r'\berase\s+/s\b', "erase /s detected"),
        (r'\berase\s+.*\s+/s\b', "erase with /s flag detected"),
        
        # PowerShell destructive patterns
        (r'\bremove-item\s+.*-recurse\b', "PowerShell Remove-Item -Recurse detected"),
        (r'\bremove-item\s+.*-force\b', "PowerShell Remove-Item -Force detected"),
        (r'\brm\s+.*-recurse\b', "PowerShell rm -Recurse detected"),
        (r'\brm\s+.*-force\b', "PowerShell rm -Force detected"),
        (r'\bri\s+.*-recurse\b', "PowerShell ri -Recurse detected"),
        (r'\bri\s+.*-force\b', "PowerShell ri -Force detected"),
        (r'\bget-childitem\s+.*\|\s*remove-item\b', "PowerShell pipeline deletion detected"),
        (r'\bgci\s+.*\|\s*remove-item\b', "PowerShell gci pipeline deletion detected"),
        (r'\bls\s+.*\|\s*remove-item\b', "PowerShell ls pipeline deletion detected"),
        
        # Format and destructive system commands
        (r'\bformat\s+[a-z]:\b', "Format drive command detected"),
        (r'\bdiskpart\b', "Diskpart utility detected"),
        (r'\bfsutil\s+.*delete\b', "Fsutil delete detected"),
        (r'\bcipher\s+/w\b', "Cipher wipe command detected"),
        (r'\bsdelete\b', "Secure delete utility detected"),
        (r'\bshred\b', "Shred command detected"),
        (r'\bwipe\b', "Wipe command detected"),
        
        # Mass deletion patterns
        (r'\bfind\s+.*-delete\b', "find with -delete detected"),
        (r'\bxargs\s+.*rm\b', "xargs rm combination detected"),
        (r'\bxargs\s+.*del\b', "xargs del combination detected"),
        (r'\.*\*.*rm\b', "Wildcard rm pattern detected"),
        (r'\.*\*.*del\b', "Wildcard del pattern detected"),
        (r'\.*\*.*remove-item\b', "Wildcard Remove-Item pattern detected"),
        
        # Registry destructive operations
        (r'\breg\s+delete\b', "Registry delete command detected"),
        (r'\bregedit\s+.*-s\b', "Silent registry edit detected"),
        
        # Service and process destruction
        (r'\btaskkill\s+/f\b', "Force task kill detected"),
        (r'\bsc\s+delete\b', "Service delete detected"),
        (r'\bnet\s+stop\b', "Service stop detected"),
        
        # Network destructive commands
        (r'\bnetsh\s+.*reset\b', "Network reset command detected"),
        (r'\bipconfig\s+/flushdns\b', "DNS flush detected"),
        
        # Boot and system destruction
        (r'\bbcdedit\s+.*delete\b', "Boot configuration delete detected"),
        (r'\battrib\s+.*-s\s+-h\b', "System file attribute removal detected"),
        (r'\bbootrec\s+/fixmbr\b', "Master boot record modification detected"),
    ]
    
    # Check against dangerous patterns - BLOCK ALL MATCHES
    for pattern, description in dangerous_patterns:
        if re.search(pattern, cmd_lower):
            return True, description
    
    # Additional broad blocking for any deletion commands
    broad_deletion_patterns = [
        (r'\brm\s+', "rm command detected"),
        (r'\bdel\s+', "del command detected"), 
        (r'\berase\s+', "erase command detected"),
        (r'\brmdir\s+', "rmdir command detected"),
        (r'\bremove-item\s+', "PowerShell Remove-Item detected"),
        (r'\bri\s+', "PowerShell ri (Remove-Item alias) detected"),
    ]
    
    # Block these broad patterns too
    for pattern, description in broad_deletion_patterns:
        if re.search(pattern, cmd_lower):
            return True, description
    
    return False, ""

def get_protected_directories() -> List[str]:
    """
    Get list of directories that should be protected from deletion.
    
    Returns:
        List of directory names/patterns to protect
    """
    return [
        "apps/",
        "app/",
        "src/",
        "source/",
        ".git/",
        ".github/",
        "node_modules/",
        "packages/",
        "lib/",
        "libs/",
        "components/",
        "pages/",
        "public/",
        "assets/",
        "static/",
        "build/",
        "dist/",
        "docs/",
        ".vscode/",
        ".idea/",
        "config/",
        "configs/",
        "database/",
        "migrations/",
        "models/",
        "views/",
        "controllers/",
        "services/",
        "utils/",
        "helpers/",
        "middleware/",
        "schemas/",
        "types/",
        "interfaces/",
        "prompts/"
    ]

def log_to_logs_directory(payload: Dict[str, Any]) -> None:
    """
    Log PreToolUse event to logs directory.
    
    Args:
        payload: Hook payload containing tool information
    """
    try:
        logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / "pre_tool_use.json"
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event": "PreToolUse",
            "session_id": payload.get("session_id", "unknown"),
            "tool_name": payload.get("tool_name", "unknown"),
            "tool_input": payload.get("tool_input", {}),
            "cwd": payload.get("cwd", "unknown"),
            "transcript_path": payload.get("transcript_path", "unknown"),
            "hook_event_name": payload.get("hook_event_name", "PreToolUse")
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        log_debug(f"Failed to log to logs directory: {e}")

def log_blocked_operation(payload: Dict[str, Any], command: str, reason: str) -> None:
    """
    Log blocked deletion operation for audit trail.
    
    Args:
        payload: Original hook payload
        command: The blocked command
        reason: Reason for blocking
    """
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        
        timestamp = datetime.datetime.now().isoformat()
        session_id = payload.get("session_id", "unknown")
        
        log_entry = {
            "timestamp": timestamp,
            "event": "DELETION_BLOCKED",
            "session_id": session_id,
            "command": command,
            "reason": reason,
            "tool_name": payload.get("tool_name"),
            "cwd": payload.get("cwd", "unknown")
        }
        
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"{json.dumps(log_entry)}\n")
            
    except Exception as e:
        # Don't fail the hook if logging fails
        log_debug(f"Failed to log blocked operation: {e}")

def notify_blocked_command(command: str, reason: str) -> None:
    """
    Send voice notification for blocked command.
    
    Args:
        command: The blocked command
        reason: Reason for blocking
    """
    try:
        if VOICE_AVAILABLE:
            # Create short, clear voice message
            if "rm -rf" in reason.lower():
                voice_message = "Blocked dangerous rm rf command"
            elif "del" in reason.lower() or "erase" in reason.lower():
                voice_message = "Blocked dangerous deletion command"
            elif "format" in reason.lower():
                voice_message = "Blocked disk format command"
            elif "remove-item" in reason.lower():
                voice_message = "Blocked PowerShell removal command"
            else:
                voice_message = "Blocked dangerous command"
            
            log_debug(f"Sending voice notification: {voice_message}")
            speak(voice_message)
            log_debug("Voice notification sent successfully")
        else:
            log_debug("Voice notification unavailable")
        
    except Exception as e:
        # Don't fail the hook if voice notification fails
        log_debug(f"Voice notification failed: {e}")

def log_debug(message: str) -> None:
    """
    Log debug message to debug.log file.
    
    Args:
        message: Debug message to log
    """
    try:
        debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        timestamp = datetime.datetime.now().isoformat()
        
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] PRE_TOOL_USE: {message}\n")
            
    except Exception:
        # Silently fail if logging doesn't work
        pass

if __name__ == "__main__":
    main()