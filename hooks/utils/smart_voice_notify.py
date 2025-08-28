#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pyttsx3>=2.90",
# ]
# ///

"""Simplified voice notifications using Windows SAPI
Replaces 222-line ElevenLabs implementation with ultra-simple local solution.
Maintains full hook compatibility while eliminating external dependencies.
"""

import json
import pathlib
import threading
from typing import Tuple

# Global TTS engine - initialize once, reuse for performance
_tts_engine = None
_engine_lock = threading.Lock()

def _get_tts_engine():
    """Get or initialize Windows SAPI TTS engine"""
    global _tts_engine
    
    if _tts_engine is None:
        with _engine_lock:
            if _tts_engine is None:
                try:
                    import pyttsx3
                    _tts_engine = pyttsx3.init('sapi5')  # Windows SAPI
                    
                    # Configure for fast, clear speech
                    voices = _tts_engine.getProperty('voices')
                    if voices:
                        # Use first available voice (usually default system voice)
                        _tts_engine.setProperty('voice', voices[0].id)
                    
                    # Set speech rate (words per minute) - faster for notifications
                    _tts_engine.setProperty('rate', 180)
                    
                    # Set volume (0.0 to 1.0)
                    _tts_engine.setProperty('volume', 0.8)
                    
                except Exception:
                    _tts_engine = None
    
    return _tts_engine

def speak(text: str, voice_id: str = None) -> None:
    """Main speak function - ultra-simplified Windows SAPI"""
    try:
        engine = _get_tts_engine()
        if engine:
            # Run TTS in separate thread to avoid blocking
            def _speak_async():
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass
            
            thread = threading.Thread(target=_speak_async, daemon=True)
            thread.start()
    except Exception:
        pass  # Silent fail maintains compatibility

def detect_context(payload: dict) -> Tuple[str, str]:
    """Simplified context detection"""
    message = payload.get("message", "").lower()
    
    if "subagent" in message:
        return "subagent", "helper"
    elif "permission" in message:
        return "permission", "tool"
    elif any(word in message for word in ["error", "failed", "warning"]):
        return "error", ""
    elif "compact" in message:
        return "compact", ""
    else:
        return "ready", ""

def get_notification_text(context: str, tool: str = "") -> str:
    """Generate notification text"""
    messages = {
        "permission": f"Permission for {tool}" if tool else "Permission needed",
        "ready": "Claude ready",
        "error": "Error occurred", 
        "subagent": "Helper task complete",
        "compact": "Compacting chat",
        "tool_completion": f"{tool} complete" if tool else "Task complete"
    }
    return messages.get(context, "Claude notification")

# Hook compatibility functions - maintain exact signatures
def process_notification(payload: dict) -> None:
    """Main notification processing - maintains compatibility"""
    context, tool = detect_context(payload)
    
    # Check for recent tool completion from transcript
    if context == "ready" and "transcript_path" in payload:
        transcript_path = pathlib.Path(payload["transcript_path"])
        if transcript_path.exists():
            try:
                with transcript_path.open("r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # Check last few lines for tool completion
                for line in reversed(lines[-5:]):
                    try:
                        record = json.loads(line.strip())
                        if record.get("hook_event_name") == "PostToolUse":
                            tool_name = record.get("tool_name", "").replace("mcp__", "").replace("__", " ")
                            context = "tool_completion"
                            tool = tool_name
                            break
                    except json.JSONDecodeError:
                        continue
            except Exception:
                pass
    
    text = get_notification_text(context, tool)
    speak(text)

def process_stop_notification(payload: dict) -> None:
    """Session end notification"""
    speak("Session complete")

def process_subagent_notification(payload: dict) -> None:
    """Subagent notification"""  
    speak("Helper finished")

def process_compact_notification(payload: dict) -> None:
    """Compact notification"""
    speak("Compacting chat")

# Test and diagnostic functionality
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "test":
            speak("Hello! This is your simplified Claude Code voice assistant.")
            
        elif test_type == "engines":
            try:
                engine = _get_tts_engine()
                if engine:
                    speak("Windows speech engine working")
                    print("SUCCESS: Windows SAPI TTS available")
                else:
                    print("ERROR: TTS engine initialization failed")
            except Exception as e:
                print(f"ERROR: TTS engine failed: {e}")
                
        else:
            speak("Hello! This is your simplified Claude Code voice assistant.")
    else:
        speak("Hello! This is your simplified Claude Code voice assistant.")