#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "edge-tts>=6.1.0",
#   "pyttsx3>=2.99",
# ]
# ///

import json, os, pathlib, random
import asyncio
import tempfile
import subprocess

async def speak_edge(text: str, voice: str = "en-US-JennyNeural") -> None:
    """Use Edge TTS for high-quality natural voices"""
    import edge_tts
    
    # Create a temporary file for the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    # Generate speech using Edge TTS
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tmp_path)
    
    # Play the audio file
    subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{tmp_path}').PlaySync()"], 
                  capture_output=True, check=False)
    
    # Clean up
    try:
        os.unlink(tmp_path)
    except:
        pass

def speak_pyttsx3_fallback(text: str) -> None:
    """Simple pyttsx3 fallback when edge_tts not available"""
    try:
        import pyttsx3
        eng = pyttsx3.init()
        eng.setProperty("rate", 185)
        eng.say(text)
        eng.runAndWait()
    except:
        # Silent fallback if pyttsx3 also fails
        pass

def speak(text: str, voice: str = "en-GB-SoniaNeural") -> None:
    """Main speak function - uses Edge TTS with pyttsx3 fallback"""
    try:
        import edge_tts
        asyncio.run(speak_edge(text, voice))
    except (ImportError, ModuleNotFoundError):
        # Fallback to pyttsx3 if edge_tts not available
        speak_pyttsx3_fallback(text)
    except Exception:
        # Fallback to pyttsx3 on any other error
        speak_pyttsx3_fallback(text)

# Removed get_dynamic_notification - using random variations instead

def get_simple_notification(context: str, tool: str) -> str:
    """Generate varied voice notifications for each tool with random selection."""
    if context == "permission_request":
        # Multiple permission request variations
        permission_variations = {
            "Read": ["Permission for Read", "Claude wants to read a file", "Requesting read access", "Need permission to read"],
            "Write": ["Permission for Write", "Claude wants to write a file", "Requesting write access", "Need permission to write"],
            "Edit": ["Permission for Edit", "Claude wants to edit a file", "Requesting edit access", "Need permission to edit"],
            "MultiEdit": ["Permission for MultiEdit", "Claude wants to edit multiple files", "Requesting multi-edit access", "Need permission for batch editing"],
            "Bash": ["Permission for Bash", "Claude wants to run a command", "Requesting terminal access", "Need permission for command"],
            "LS": ["Permission for LS", "Claude wants to list files", "Requesting directory access", "Need permission to browse"],
            "Grep": ["Permission for Grep", "Claude wants to search files", "Requesting search access", "Need permission to search"],
            "Glob": ["Permission for Glob", "Claude wants to find files", "Requesting file search", "Need permission to locate files"],
            "Update": ["Permission for Update", "Claude wants to update", "Requesting update access", "Need permission to update"],
            "Task": ["Permission for Task", "Claude wants to delegate", "Requesting task access", "Need permission for sub-task"],
            "Plan": ["Permission for Plan", "Claude wants to plan", "Requesting planning access", "Need permission to plan"]
        }
        variations = permission_variations.get(tool, [f"Permission for {tool}", f"Claude needs {tool} access"])
        return random.choice(variations)
    
    elif context == "tool_completion":
        # Multiple completion message variations
        completion_variations = {
            "Read": ["Read complete", "File loaded", "Reading finished", "Got the file content"],
            "Write": ["Write complete", "File saved", "Writing finished", "File created successfully"],
            "Edit": ["Edit complete", "File updated", "Changes saved", "Editing finished"],
            "MultiEdit": ["MultiEdit complete", "Multiple files updated", "Batch editing done", "All changes saved"],
            "Bash": ["Command complete", "Terminal finished", "Command executed", "Shell operation done"],
            "LS": ["Directory listed", "Files enumerated", "Listing complete", "Directory scanned"],
            "Grep": ["Search complete", "Matches found", "Search finished", "Pattern search done"],
            "Glob": ["Files found", "Pattern matched", "File search complete", "Globbing finished"],
            "Update": ["Update complete", "Successfully updated", "Update finished", "Changes applied"],
            "Task": ["Task complete", "Sub-task finished", "Delegation done", "Task executed"]
        }
        variations = completion_variations.get(tool, [f"{tool} complete", f"{tool} finished", f"{tool} done"])
        return random.choice(variations)
    
    elif context == "session_end":
        session_variations = []
        if tool and any(keyword in tool.lower() for keyword in ["commit", "git", "file"]):
            session_variations = [
                "Session complete with changes",
                "Work finished, changes saved", 
                "Claude done, files updated",
                "Session ended, work committed"
            ]
        else:
            session_variations = [
                "Claude session complete",
                "Work finished successfully",
                "Claude session ended",
                "All done, session closed"
            ]
        return random.choice(session_variations)
    
    elif context == "error_notification":
        error_variations = [
            "Error occurred",
            "Something went wrong",
            "Claude encountered an issue",
            "Operation failed"
        ]
        return random.choice(error_variations)
    
    elif context == "waiting":
        waiting_variations = [
            "Claude ready",
            "Ready for input",
            "Claude standing by",
            "Waiting for instructions"
        ]
        return random.choice(waiting_variations)
    
    elif context == "compact_notification":
        if "automatic" in tool.lower():
            auto_variations = [
                "Automatically compacting conversation",
                "Auto-compacting the chat",
                "Conversation being compressed",
                "Auto-tidying the session"
            ]
            return random.choice(auto_variations)
        elif "manual" in tool.lower():
            manual_variations = [
                "Manually compacting conversation", 
                "Compacting on request",
                "User-triggered compression",
                "Manual conversation cleanup"
            ]
            return random.choice(manual_variations)
        else:
            general_variations = [
                "Compacting the conversation",
                "Tidying up the chat",
                "Conversation cleanup",
                "Compressing the session"
            ]
            return random.choice(general_variations)
    
    else:
        general_variations = [
            "Claude notification",
            "Claude update",
            "System message",
            "Claude alert"
        ]
        return random.choice(general_variations)



def detect_notification_context(payload: dict, transcript_path: pathlib.Path) -> tuple[str, str, str]:
    """
    Detect the context of a notification and extract tool/result information
    Returns: (context, tool, result)
    """
    message = payload.get("message", "")
    
    # Enhanced detection patterns for various notification types
    
    # 1. Permission/Confirmation requests - Multiple patterns
    if any(pattern in message.lower() for pattern in [
        "needs your permission to use",
        "needs permission to use", 
        "wants to use",
        "requesting permission",
        "confirm to proceed",
        "confirmation required",
        "needs your confirmation",
        "confirm this action",
        "proceed with",
        "allow claude to"
    ]):
        # Extract tool name from various message formats
        tool = "unknown tool"
        
        # Try different extraction patterns
        if "use " in message:
            parts = message.split("use ")
            if len(parts) > 1:
                tool = parts[-1].strip().rstrip("?").rstrip(".")
        elif "with " in message:
            parts = message.split("with ")
            if len(parts) > 1:
                tool = parts[-1].strip().rstrip("?").rstrip(".")
        elif "to " in message:
            parts = message.split("to ")
            if len(parts) > 1:
                extracted = parts[-1].strip().rstrip("?").rstrip(".")
                # Only use if it looks like a tool name (short, no spaces)
                if len(extracted.split()) <= 2:
                    tool = extracted
        
        return "permission_request", tool, f"Requesting permission for {tool}"
    
    # 2. Error/Warning notifications
    if any(pattern in message.lower() for pattern in [
        "error occurred",
        "failed to",
        "warning:",
        "could not",
        "unable to",
        "permission denied",
        "access denied",
        "file not found",
        "network error"
    ]):
        return "error_notification", "error", f"Error: {message[:50]}..."
    
    # 3. Task completion notifications  
    if any(pattern in message.lower() for pattern in [
        "task completed",
        "operation finished",
        "successfully completed",
        "done",
        "finished",
        "completed successfully"
    ]):
        return "completion_notification", "task", message
    
    # 4. User input required
    if any(pattern in message.lower() for pattern in [
        "waiting for input",
        "please respond",
        "your input needed",
        "waiting for your response",
        "please provide"
    ]):
        return "input_required", "user_input", "Waiting for your input"
    
    # 5. System status updates
    if any(pattern in message.lower() for pattern in [
        "ready for",
        "standing by",
        "available",
        "idle",
        "waiting"
    ]):
        return "status_update", "system", message
    
    # 6. If not a specific notification, check transcript for recent tool activity
    tool, result = last_post_tooluse(transcript_path)
    if tool:
        return "tool_completion", tool, result
    
    # 7. Default case - general notification
    if message and len(message.strip()) > 0:
        return "general_notification", "notification", message
    
    # 8. Final fallback
    return "waiting", "", "Claude is ready"

def last_post_tooluse(transcript: pathlib.Path) -> tuple[str, str]:
    """
    Scan the transcript bottom-up and return (tool_name, summary)
    Enhanced to provide more intelligent summaries
    """
    if not transcript.exists():
        return "", ""
        
    with transcript.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Look for the most recent PostToolUse event
    for line in reversed(lines):
        try:
            record = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
            
        if record.get("hook_event_name") == "PostToolUse":
            tool = record.get("tool_name", "")
            tool_response = record.get("tool_response", {})
            tool_input = record.get("tool_input", {})
            
            # Generate intelligent summary based on tool type
            summary = generate_tool_summary(tool, tool_input, tool_response)
                
            return tool, summary
            
    return "", ""

def generate_tool_summary(tool: str, tool_input: dict, tool_response: any) -> str:
    """
    Generate intelligent summaries based on tool type and response
    """
    if tool == "Write":
        if isinstance(tool_response, dict):
            file_path = tool_response.get("filePath", tool_input.get("file_path", ""))
            if file_path:
                return f"Created/updated file: {file_path.split('/')[-1]}"
        return "File operation completed"
    
    elif tool == "Edit" or tool == "MultiEdit":
        if isinstance(tool_input, dict):
            file_path = tool_input.get("file_path", "")
            if file_path:
                return f"Modified file: {file_path.split('/')[-1]}"
        return "File editing completed"
    
    elif tool == "Read":
        if isinstance(tool_input, dict):
            file_path = tool_input.get("file_path", "")
            if file_path:
                return f"Read file: {file_path.split('/')[-1]}"
        return "File reading completed"
    
    elif tool == "Bash":
        if isinstance(tool_response, dict):
            stdout = tool_response.get("stdout", "")
            stderr = tool_response.get("stderr", "")
            exit_code = tool_response.get("exit_code", 0)
            
            if exit_code != 0:
                return f"Command failed with exit code {exit_code}"
            elif stdout:
                return f"Command output: {stdout[:50]}..."
            else:
                return "Command executed successfully"
        return "Command completed"
    
    elif tool == "LS":
        if isinstance(tool_response, str):
            file_count = len(tool_response.strip().split('\n')) if tool_response.strip() else 0
            return f"Listed {file_count} items in directory"
        return "Directory listing completed"
    
    elif tool == "Grep":
        if isinstance(tool_response, str):
            match_count = len(tool_response.strip().split('\n')) if tool_response.strip() else 0
            return f"Found {match_count} matches"
        return "Search completed"
    
    else:
        # Generic summary for unknown tools
        if isinstance(tool_response, dict):
            if "error" in str(tool_response).lower():
                return f"{tool} encountered an error"
            else:
                return f"{tool} completed successfully"
        elif isinstance(tool_response, str):
            if tool_response and len(tool_response) > 0:
                return f"{tool} returned: {tool_response[:50]}..."
            else:
                return f"{tool} completed"
        else:
            return f"{tool} operation completed"



def process_notification(payload: dict) -> None:
    """
    Main notification processing function called by the hook handler.
    Takes a payload dict and handles the voice notification logic.
    """
    # Debug: Log detailed hook information
    import datetime
    debug_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": "hook_triggered",
        "payload": payload,
        "environment": {
            "cwd": str(pathlib.Path.cwd()),
            "hook_type": "unknown"
        }
    }
    
    # Determine hook type from payload
    if "hook_event_name" in payload:
        debug_info["environment"]["hook_type"] = payload["hook_event_name"]
    elif "transcript_path" in payload:
        debug_info["environment"]["hook_type"] = "Notification"
    else:
        debug_info["environment"]["hook_type"] = "Unknown/Direct"
    
    # Write debug log
    with open("C:/Users/NATH/.claude/hooks/debug.log", "a", encoding="utf-8") as f:
        f.write(f"{json.dumps(debug_info, indent=2)}\n")
        f.write("="*80 + "\n")
    
    # Handle pure Notification events only
    if "transcript_path" in payload:
        transcript_path = pathlib.Path(payload["transcript_path"])
        notification_message = payload.get("message", "")
        
        # Detect notification context
        context, tool, result_summary = detect_notification_context(payload, transcript_path)
        
        # If there's no specific tool context, use a simple ready message
        if not tool and not result_summary:
            speak("Claude is ready.")
            return
    else:
        # Unknown format - should not happen with pure Notification hooks
        speak("Claude notification received.")
        return

    # Generate notification with random variations
    final_text = get_simple_notification(context, tool)
    
    # Final fallback to ensure we always say something
    final_text = final_text or "Claude notification"
    speak(final_text)

def detect_stop_context(payload: dict) -> tuple[str, str]:
    """
    Analyze Stop hook payload to extract meaningful session context.
    Returns: (context_summary, detailed_info)
    """
    # Look for git activity or recent commits
    recent_commits = payload.get("recent_commits", [])
    files_changed = payload.get("files_changed", [])
    session_duration = payload.get("session_duration", "")
    tools_used = payload.get("tools_used", [])
    
    # Build smart context summary
    if recent_commits and len(recent_commits) > 0:
        commit_count = len(recent_commits)
        if commit_count == 1:
            return f"saved 1 commit", f"git activity with {commit_count} commit"
        else:
            return f"saved {commit_count} commits", f"git activity with {commit_count} commits"
    
    elif files_changed and len(files_changed) > 0:
        file_count = len(files_changed)
        if file_count == 1:
            return f"modified 1 file", f"file changes: {file_count} file"
        else:
            return f"modified {file_count} files", f"file changes: {file_count} files"
    
    elif tools_used and len(tools_used) > 0:
        if len(tools_used) == 1:
            return f"used {tools_used[0]}", f"tools: {tools_used[0]}"
        elif len(tools_used) <= 3:
            tool_list = ", ".join(tools_used)
            return f"used {tool_list}", f"tools: {tool_list}"
        else:
            return f"used {len(tools_used)} tools", f"tools: {len(tools_used)} different tools"
    
    elif session_duration:
        return f"worked for {session_duration}", f"duration: {session_duration}"
    
    else:
        return "completed work", "general session completion"

def process_stop_notification(payload: dict) -> None:
    """
    Process Stop hook events and provide smart voice feedback about session completion.
    Uses existing utilities for consistency.
    """
    # Debug: Log Stop hook information
    import datetime
    debug_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": "stop_hook_triggered",
        "payload": payload,
        "environment": {
            "cwd": str(pathlib.Path.cwd()),
            "hook_type": "Stop"
        }
    }
    
    # Write debug log
    with open("C:/Users/NATH/.claude/hooks/debug.log", "a", encoding="utf-8") as f:
        f.write(f"{json.dumps(debug_info, indent=2)}\n")
        f.write("="*80 + "\n")
    
    # Analyze session context for simple feedback
    context_summary, detailed_info = detect_stop_context(payload)
    
    # Generate simple session end notification
    text = get_simple_notification("session_end", context_summary)
    
    # Ensure we always have something to say
    final_text = text or "Claude session complete"
    speak(final_text)

def process_compact_notification(payload: dict) -> None:
    """
    Process PreCompact hook events and provide voice feedback about compacting.
    Uses existing utilities for consistency.
    """
    # Debug: Log PreCompact hook information
    import datetime
    debug_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": "pre_compact_hook_triggered",
        "payload": payload,
        "environment": {
            "cwd": str(pathlib.Path.cwd()),
            "hook_type": "PreCompact"
        }
    }
    
    # Write debug log
    with open("C:/Users/NATH/.claude/hooks/debug.log", "a", encoding="utf-8") as f:
        f.write(f"{json.dumps(debug_info, indent=2)}\n")
        f.write("="*80 + "\n")
    
    # Determine if it's automatic or manual compacting
    # Check payload for compact type indicators
    compact_type = "unknown"
    
    # Check various payload fields that might indicate automatic vs manual
    if "automatic" in str(payload).lower() or "auto" in str(payload).lower():
        compact_type = "automatic"
    elif "manual" in str(payload).lower() or "user" in str(payload).lower():
        compact_type = "manual"
    else:
        # Default to automatic if we can't determine
        compact_type = "automatic"
    
    # Generate compact notification
    text = get_simple_notification("compact_notification", compact_type)
    
    # Ensure we always have something to say
    final_text = text or "Compacting the conversation"
    speak(final_text)

if __name__ == "__main__":
    # Test the voice system
    speak("Hello! This is your Claude Code voice assistant.")