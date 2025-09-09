#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyttsx3>=2.90",
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
    VOICE_AVAILABLE = False
    def speak(text: str):
        """Fallback if voice utilities unavailable"""
        pass

def main() -> None:
    """
    PreToolUse hook handler with enhanced security and GitButler integration.
    - Blocks dangerous deletion operations and security violations
    - Integrates with GitButler for automatic branch management
    - Logs all tool usage for audit trail
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
        
        # Process security and deletion prevention check
        result = process_deletion_check(payload)
        
        # If we have a permission decision, output it
        if result and "permissionDecision" in result:
            print(json.dumps(result))
            # Exit with 0 for both allow and deny (hook succeeded)
            sys.exit(0)
        else:
            # No decision - let Claude's normal flow continue
            sys.exit(0)
        
    except Exception as e:
        # Log error and allow operation (fail-open for safety)
        log_debug(f"Hook processing error: {e}")
        # Don't auto-approve on error - let Claude handle it normally
        sys.exit(0)

def process_deletion_check(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Main deletion prevention logic.
    
    Args:
        payload: JSON payload from Claude Code containing tool information
        
    Returns:
        Dict with permission decision and optional reason
    """
    # Only process Bash tool calls for dangerous operations
    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        # For non-Bash tools, return empty dict to let Claude handle normally
        return {}
    
    # Extract the bash command
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    
    if not command:
        # No command means nothing to check
        return {}
    
    # Check for dangerous deletion patterns
    is_dangerous, reason = is_dangerous_deletion(command)
    
    if is_dangerous:
        # Log the blocked operation
        log_blocked_operation(payload, command, reason)
        
        # Voice notification for blocked command
        notify_blocked_command(command, reason)
        
        # Use proper permission format per Claude Code docs
        return {
            "permissionDecision": "deny",
            "permissionDecisionReason": f"BLOCKED: {reason}\nCommand: {command}\n\nThis operation was blocked to prevent accidental deletion of critical files/directories."
        }
    
    # Check for unwanted Claude Code references in git commits
    has_claude_refs, commit_reason = has_claude_code_references(command)
    
    if has_claude_refs:
        # Log the blocked operation
        log_blocked_operation(payload, command, commit_reason)
        
        # Voice notification for blocked command
        notify_blocked_commit(command, commit_reason)
        
        # Use proper permission format per Claude Code docs
        return {
            "permissionDecision": "deny",
            "permissionDecisionReason": f"BLOCKED: {commit_reason}\nCommand: {command}\n\nThis commit was blocked to prevent Claude Code references in commit messages."
        }
    
    # For safe Bash commands, return empty to let Claude handle normally
    return {}

def is_dangerous_deletion(command: str) -> Tuple[bool, str]:
    """
    Enhanced security check for dangerous commands (beyond just deletion).
    Blocks dangerous rm commands, security violations, and malicious operations.
    
    Args:
        command: The bash command to analyze
        
    Returns:
        Tuple of (is_dangerous: bool, reason: str)
    """
    # Normalize command for analysis
    cmd_lower = command.lower().strip()
    
    # Enhanced dangerous patterns with regex support
    dangerous_patterns = [
        # Dangerous rm patterns (ENHANCED)
        (r'\brm\s+.*-[a-z]*r[a-z]*f', 'rm -rf variations detected'),
        (r'\brm\s+.*-[a-z]*f[a-z]*r', 'rm -fr variations detected'),
        (r'\brm\s+--recursive\s+--force', 'rm recursive force detected'),
        (r'\brm\s+.*\*.*/', 'rm with wildcards on directories'),
        (r'\brm\s+.*\$HOME', 'rm targeting home directory'),
        (r'\brm\s+.*~/', 'rm targeting user directory'),
        
        # Security violations (NEW)
        (r'\bchmod\s+777', 'dangerous permissions 777 detected'),
        (r'\bchmod\s+.*777', 'dangerous permissions 777 detected'),
        (r'\bsudo\s+rm', 'sudo rm command detected'),
        (r'\bsudo\s+chmod\s+777', 'sudo chmod 777 detected'),
        
        # System destruction (ENHANCED)
        (r'\bdd\s+if=/dev/zero', 'disk zeroing command'),
        (r'\bdd\s+if=/dev/random', 'disk randomization command'),
        (r'>\s*/dev/sd[a-z]', 'writing to raw disk device'),
        (r'\bmkfs\.', 'filesystem creation on device'),
        (r'\bformat\s+[c-z]:', 'Windows format command'),
        
        # Remote execution risks (NEW)
        (r'\bcurl\s+.*\|\s*(sh|bash)', 'curl pipe to shell execution'),
        (r'\bwget\s+.*\|\s*(sh|bash)', 'wget pipe to shell execution'),
        (r'\bcurl\s+.*-o.*\.(sh|exe|bat)', 'downloading executable files'),
        
        # Network/System compromise (NEW)  
        (r'\biptables\s+-F', 'flushing firewall rules'),
        (r'\bnetsh\s+.*reset', 'network configuration reset'),
        (r'>\s*/etc/passwd', 'writing to passwd file'),
        (r'>\s*/etc/shadow', 'writing to shadow file'),
        
        # Process/Service disruption (NEW)
        (r'\bkillall\s+-9', 'force killing all processes'),
        (r'\btaskkill\s+/f', 'Windows force process kill'),
        (r'\bsc\s+delete', 'Windows service deletion'),
        (r'\bsystemctl\s+disable.*\.(service|timer)', 'disabling system services')
    ]
    
    # Check regex patterns first (more precise)
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, cmd_lower, re.IGNORECASE):
            return True, f"SECURITY VIOLATION: {reason}"
    
    # Existing banned commands (kept for compatibility)
    banned_commands = [
        # Unix/Linux deletion
        'rm ',
        'rm\t',
        'rmdir',
        'unlink',
        
        # Windows deletion
        'del ',
        'del\t',
        'erase',
        'rd ',
        'rd\t',
        
        # PowerShell deletion
        'remove-item',
        'remove-',
        'ri ',
        'ri\t',
        
        # Dangerous utilities
        'shred',
        'wipe',
        'sdelete',
        'format',
        'diskpart',
        'fdisk',
        
        # System destruction
        'dd if=/dev/zero',
        'dd if=/dev/random',
        '> /dev/sda',
        'mkfs',
        
        # Package managers (dangerous operations)
        'apt purge',
        'apt-get purge',
        'apt remove',
        'apt-get remove',
        'yum remove',
        'dnf remove',
        'pacman -R',
        'brew uninstall',
        'npm uninstall',
        'pip uninstall',
        
        # Database destruction
        'drop database',
        'drop table',
        'truncate table',
        'delete from',
        
        # Git dangerous operations
        'git clean -f',
        'git reset --hard',
        'git push --force',
        
        # Find with delete
        'find ',
        'xargs',
        
        # Registry operations
        'reg delete',
        'regedit',
        
        # Service operations
        'sc delete',
        'net stop',
        'systemctl disable',
        'service stop',
        
        # Process killing
        'kill -9',
        'killall',
        'taskkill',
        'pkill',
        
        # Network reset
        'netsh reset',
        'iptables -F',
        'ipconfig /release',
    ]
    
    # Check if any banned command appears in the command
    for banned in banned_commands:
        if banned in cmd_lower:
            return True, f"Command contains banned operation: '{banned.strip()}'"
    
    # Additional check for command chaining that might bypass simple checks
    dangerous_operators = ['&&', '||', ';', '|', '`', '$(' ]
    for operator in dangerous_operators:
        if operator in command:
            # Check each part of the chained command
            parts = command.replace('&&', '|').replace('||', '|').replace(';', '|').split('|')
            for part in parts:
                part_lower = part.lower().strip()
                for banned in banned_commands:
                    if banned in part_lower:
                        return True, f"Chained command contains banned operation: '{banned.strip()}'"
    
    return False, ""

def log_to_logs_directory(payload: Dict[str, Any]) -> None:
    """
    Log PreToolUse event to logs directory.
    
    Args:
        payload: Hook payload containing tool information
    """
    try:
        # Use dynamic path relative to hook file location
        hook_dir = pathlib.Path(__file__).parent
        logs_dir = hook_dir.parent / "logs"
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
        # Use dynamic path relative to hook file location
        hook_dir = pathlib.Path(__file__).parent
        debug_log = hook_dir / "debug.log"
        
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


def has_claude_code_references(command: str) -> Tuple[bool, str]:
    """
    Check if git commit command contains unwanted Claude Code references.
    
    Args:
        command: The bash command to analyze
        
    Returns:
        Tuple of (has_references: bool, reason: str)
    """
    # Only check git commit commands
    if not ("git commit" in command.lower()):
        return False, ""
    
    # Patterns to block in commit messages
    blocked_patterns = [
        "Generated with [Claude Code](https://claude.ai/code)",
        "Co-Authored-By: Claude <noreply@anthropic.com>",
        "🤖 Generated with [Claude Code]",
        "claude.ai/code",
        "noreply@anthropic.com"
    ]
    
    for pattern in blocked_patterns:
        if pattern in command:
            return True, f"Commit message contains blocked Claude Code reference: '{pattern}'"
    
    return False, ""

def notify_blocked_commit(command: str, reason: str) -> None:
    """
    Send voice notification for blocked commit.
    
    Args:
        command: The blocked command
        reason: Reason for blocking
    """
    try:
        if VOICE_AVAILABLE:
            voice_message = "Blocked commit with Claude Code references"
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
        # Use dynamic path relative to hook file location
        hook_dir = pathlib.Path(__file__).parent
        debug_log = hook_dir / "debug.log"
        timestamp = datetime.datetime.now().isoformat()
        
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] PRE_TOOL_USE: {message}\n")
            
    except Exception:
        # Silently fail if logging doesn't work
        pass

if __name__ == "__main__":
    main()