#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "elevenlabs>=1.0.0",
#   "requests>=2.31.0",
# ]
# ///

import json
import pathlib
import random
import tempfile
import requests
import subprocess

# Hardcoded ElevenLabs API key
ELEVENLABS_API_KEY = "sk_4c5b5d139cf16ee957812a0de9692839572dbbfb0a20770c"
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

def speak(text: str, voice_id: str = "cgSgspJ2msm6clMCkdW9") -> None:
    """Main speak function using ElevenLabs API"""
    try:
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            # Play audio silently
            subprocess.run([
                "powershell", "-WindowStyle", "Hidden", "-Command", 
                f"Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object system.windows.media.mediaplayer; $mediaPlayer.open('{tmp_file_path.replace(chr(92), chr(92)+chr(92))}'); $mediaPlayer.Play(); Start-Sleep -Seconds 5"
            ], check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            
    except Exception:
        pass  # Silent fail

def get_notification_text(context: str, tool: str = "") -> str:
    """Generate notification text based on context"""
    notifications = {
        "permission_request": [
            f"Permission for {tool}" if tool else "Permission needed",
            f"Claude wants to use {tool}" if tool else "Claude needs permission"
        ],
        "tool_completion": [
            f"{tool} complete" if tool else "Task complete",
            f"{tool} finished" if tool else "Operation finished"
        ],
        "session_end": [
            "Claude session complete",
            "Work finished successfully",
            "Session ended"
        ],
        "error_notification": [
            "Error occurred",
            "Something went wrong"
        ],
        "waiting": [
            "Claude ready",
            "Ready for input"
        ],
        "compact_notification": [
            "Compacting conversation" if "auto" not in tool else "Auto-compacting chat",
            "Tidying up the session"
        ],
        "subagent_start": [
            "Subagent starting",
            "Delegating to helper"
        ],
        "subagent_stop": [
            "Subagent finished",
            "Helper task complete"
        ],
        "subagent_activity": [
            "Subagent working",
            "Helper in progress"
        ]
    }
    
    variations = notifications.get(context, ["Claude notification"])
    return random.choice(variations)

def detect_context(payload: dict, transcript_path: pathlib.Path = None) -> tuple[str, str]:
    """Detect notification context from payload"""
    message = payload.get("message", "").lower()
    
    # Subagent patterns
    if any(word in message for word in ["subagent", "delegation", "helper"]):
        if any(word in message for word in ["starting", "assigned", "delegating"]):
            return "subagent_start", "subagent"
        elif any(word in message for word in ["finished", "complete", "done"]):
            return "subagent_stop", "subagent"
        else:
            return "subagent_activity", "subagent"
    
    # Permission requests
    if any(phrase in message for phrase in ["permission", "confirm", "allow"]):
        tool = "unknown"
        if "use " in message:
            parts = message.split("use ")
            if len(parts) > 1:
                tool = parts[-1].strip().rstrip("?").rstrip(".")
        return "permission_request", tool
    
    # Error patterns
    if any(word in message for word in ["error", "failed", "warning", "denied"]):
        return "error_notification", "error"
    
    # Check recent tool use from transcript
    if transcript_path and transcript_path.exists():
        try:
            with transcript_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in reversed(lines[-10:]):  # Check last 10 lines only
                try:
                    record = json.loads(line.strip())
                    if record.get("hook_event_name") == "PostToolUse":
                        tool = record.get("tool_name", "")
                        if tool:
                            return "tool_completion", tool
                        break
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
    
    return "waiting", ""

def process_notification(payload: dict) -> None:
    """Main notification processing function"""
    if "transcript_path" in payload:
        transcript_path = pathlib.Path(payload["transcript_path"])
        context, tool = detect_context(payload, transcript_path)
        
        if not tool and not context:
            speak("Claude is ready")
            return
    else:
        context, tool = "waiting", ""
    
    text = get_notification_text(context, tool)
    speak(text)

def process_stop_notification(payload: dict) -> None:
    """Process Stop hook events"""
    recent_commits = payload.get("recent_commits", [])
    files_changed = payload.get("files_changed", [])
    tools_used = payload.get("tools_used", [])
    
    if recent_commits:
        context_info = f"saved {len(recent_commits)} commit{'s' if len(recent_commits) > 1 else ''}"
    elif files_changed:
        context_info = f"modified {len(files_changed)} file{'s' if len(files_changed) > 1 else ''}"
    elif tools_used:
        context_info = f"used {len(tools_used)} tool{'s' if len(tools_used) > 1 else ''}"
    else:
        context_info = "completed work"
    
    text = get_notification_text("session_end", context_info)
    speak(text)

def process_subagent_notification(payload: dict) -> None:
    """Process SubagentStop hook events"""
    context = "subagent_stop"
    
    message = payload.get("message", "").lower()
    if any(word in message for word in ["starting", "delegating", "assigned"]):
        context = "subagent_start"
    elif any(word in message for word in ["working", "processing", "executing"]):
        context = "subagent_activity"
    
    text = get_notification_text(context, "subagent")
    speak(text)

def process_compact_notification(payload: dict) -> None:
    """Process PreCompact hook events"""
    compact_type = "manual"
    if "automatic" in str(payload).lower() or "auto" in str(payload).lower():
        compact_type = "automatic"
    
    text = get_notification_text("compact_notification", compact_type)
    speak(text)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "subagent":
            payload = {"message": "Subagent finished task", "transcript_path": ""}
            process_subagent_notification(payload)
        elif sys.argv[1] == "test":
            speak("Hello! This is your Claude Code voice assistant.")
        else:
            speak("Hello! This is your Claude Code voice assistant.")
    else:
        speak("Hello! This is your Claude Code voice assistant.")