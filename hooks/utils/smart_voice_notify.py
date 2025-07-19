#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyttsx3>=2.99",
#   "pywin32>=306",
# ]
# ///

import json, os, sys, pyttsx3, pathlib, itertools
from utils.llms import ask_concise

def speak(text: str, voice_index: int = None) -> None:
    eng = pyttsx3.init()        # Windows SAPI-5 voice
    voices = eng.getProperty('voices')
    
    # Manual voice selection override
    if voice_index is not None and voices and 0 <= voice_index < len(voices):
        eng.setProperty('voice', voices[voice_index].id)
    elif voices:
        # Automatic voice selection - try to find a female voice or different one
        preferred_voices = []
        for voice in voices:
            voice_name = voice.name.lower()
            # Look for female voices or specific good voices
            if any(keyword in voice_name for keyword in ['zira', 'hazel', 'helen', 'female', 'woman']):
                preferred_voices.append(voice)
        
        # If we found preferred voices, use the first one
        if preferred_voices:
            eng.setProperty('voice', preferred_voices[0].id)
        # Otherwise, use the second voice if available (usually different from default)
        elif len(voices) > 1:
            eng.setProperty('voice', voices[1].id)
    
    eng.setProperty("rate", 185)
    eng.say(text)
    eng.runAndWait()

def get_dynamic_notification(tool: str, summary: str) -> str:
    """Generate a friendly, dynamic voice notification using an LLM."""
    if not summary:
        return "" # Can't generate a notification without a summary

    try:
        # We use a very specific prompt to get a short, conversational response.
        prompt = (
            f"You are a voice assistant for a programmer. Create a very short, friendly notification "
            f"(under 12 words) for the following completed action. Be conversational. "
            f"Do not say 'task completed'.\n\n"
            f"Tool Used: '{tool}'\n"
            f"Action Summary: '{summary}'\n\n"
            f"Example: If the summary is 'Modified file: auth.py', a good response would be "
            f"'Okay, I've just updated the auth file for you.'\n\n"
            f"Your notification:"
        )
        
        # Use the cost-efficient LLM utility
        notification_text = ask_concise(prompt)
        
        if notification_text and "unavailable" not in notification_text:
            return notification_text
        return ""
    except Exception:
        # If the LLM call fails for any reason, return an empty string
        # The system will then fall back to the simple notification
        return ""

def get_simple_notification(context: str, tool: str) -> str:
    """Generate simple, direct voice notifications for each tool."""
    if context == "permission_request":
        # Simple permission requests
        tool_messages = {
            "Read": "Permission for Read",
            "Write": "Permission for Write", 
            "Edit": "Permission for Edit",
            "MultiEdit": "Permission for MultiEdit",
            "Bash": "Permission for Bash",
            "LS": "Permission for LS",
            "Grep": "Permission for Grep",
            "Glob": "Permission for Glob",
            "Update": "Permission for Update",
            "Task": "Permission for Task",
            "Plan": "Permission for Plan"
        }
        return tool_messages.get(tool, f"Permission for {tool}")
    
    elif context == "tool_completion":
        # Simple completion messages
        tool_messages = {
            "Read": "Read complete",
            "Write": "Write complete",
            "Edit": "Edit complete", 
            "MultiEdit": "MultiEdit complete",
            "Bash": "Command complete",
            "LS": "Directory listed",
            "Grep": "Search complete",
            "Glob": "Files found",
            "Update": "Update complete",
            "Task": "Task complete"
        }
        return tool_messages.get(tool, f"{tool} complete")
    
    elif context == "session_end":
        if tool and any(keyword in tool.lower() for keyword in ["commit", "git", "file"]):
            return "Session complete with changes"
        return "Claude session complete"
    
    elif context == "error_notification":
        return "Error occurred"
    
    elif context == "waiting":
        return "Claude ready"
    
    elif context == "compact_notification":
        # Extract compact type from tool parameter
        if "automatic" in tool.lower():
            return "Automatic compacting the conversation"
        elif "manual" in tool.lower():
            return "Manual compacting the conversation"
        else:
            return "Compacting the conversation"
    
    else:
        return "Claude notification"

def get_fallback_response(context: str, tool: str) -> str:
    """
    Provide fallback responses when Gemini fails or returns empty
    """
    if context == "permission_request":
        return f"Claude needs your confirmation for {tool}"
    elif context == "tool_completion":
        if tool:
            return f"{tool} completed successfully"
        else:
            return "Tool operation completed"
    elif context == "error_notification":
        return "Claude encountered an error"
    elif context == "completion_notification":
        return "Task completed successfully"
    elif context == "input_required":
        return "Claude needs your input"
    elif context == "status_update":
        return "Claude status update"
    elif context == "general_notification":
        return "Claude notification received"
    elif context == "waiting":
        return "Claude is ready"
    elif context == "session_end":
        if tool:  # tool parameter contains session info for Stop context
            return f"Claude session finished, {tool}"
        else:
            return "Claude session completed successfully"
    elif context == "compact_notification":
        if "automatic" in tool.lower():
            return "Automatic compacting conversation"
        elif "manual" in tool.lower():
            return "Manual compacting conversation"
        else:
            return "Compacting conversation"
    else:
        return "Claude notification received"

def generate_context_prompt(context: str, tool: str, result: str) -> str:
    """
    Generate simple, clear prompts that speak TO the user ABOUT Claude
    """
    if context == "permission_request":
        return (
            f"Say in 6 words or less that Claude needs your confirmation for {tool}. "
            f"Speak to the user, not to Claude. Example: 'Claude needs your confirmation for {tool}' or 'Confirm {tool} permission'"
        )
    elif context == "tool_completion":
        # Check if result indicates error or success
        if any(error_word in result.lower() for error_word in ["error", "failed", "exception", "denied"]):
            return (
                f"Tell the user in 5 words that {tool} failed. "
                f"Example: '{tool} failed' or 'Error in {tool}'"
            )
        else:
            return (
                f"Tell the user in 5 words that {tool} completed successfully. "
                f"Example: '{tool} finished' or '{tool} completed successfully'"
            )
    elif context == "error_notification":
        return (
            f"Tell the user in 4 words that Claude encountered an error: {result[:30]}. "
            f"Example: 'Claude encountered error' or 'Error occurred'"
        )
    elif context == "completion_notification":
        return (
            f"Tell the user in 4 words that a task completed: {result[:30]}. "
            f"Example: 'Task completed successfully' or 'Operation finished'"
        )
    elif context == "input_required":
        return (
            f"Tell the user in 5 words that Claude needs their input. "
            f"Example: 'Claude needs your input' or 'Your input required'"
        )
    elif context == "status_update":
        return (
            f"Tell the user in 4 words about Claude's status: {result[:30]}. "
            f"Example: 'Claude status update' or 'Claude ready'"
        )
    elif context == "general_notification":
        return (
            f"Tell the user in 5 words about this notification: {result[:40]}. "
            f"Example: 'Claude notification received' or brief summary of notification"
        )
    elif context == "waiting":
        return (
            f"Tell the user in 3 words that Claude is ready. "
            f"Example: 'Claude ready' or 'Ready for input'"
        )
    elif context == "session_end":
        if tool and result:
            return (
                f"Tell the user Claude session ended with comprehensive context: {tool}. "
                f"Be smart and meaningful, under 8 words. "
                f"Example: 'Claude finished, {tool}' or 'Session complete, {result}'"
            )
        elif tool:
            return (
                f"Tell the user Claude session ended with: {tool}. "
                f"Be comprehensive but under 6 words. "
                f"Example: 'Claude finished working with {tool}' or 'Session complete, used {tool}'"
            )
        else:
            return (
                f"Tell the user Claude session ended successfully. "
                f"Be professional and brief, under 5 words. "
                f"Example: 'Claude session completed' or 'Work finished successfully'"
            )
    elif context == "compact_notification":
        return (
            f"Tell the user that Claude is compacting the conversation. "
            f"Type is: {tool}. Be concise, under 6 words. "
            f"Example: 'Automatic compacting the conversation' or 'Manual compacting the conversation'"
        )
    else:
        return (
            f"Say 'Claude notification' in 2 words or less."
        )

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

def list_available_voices() -> None:
    """List all available voices on the system for user selection."""
    print("🎤 Available voices on your system:")
    eng = pyttsx3.init()
    voices = eng.getProperty('voices')
    
    if voices:
        for i, voice in enumerate(voices):
            print(f"{i}: {voice.name} - {voice.id}")
            print(f"   Languages: {getattr(voice, 'languages', 'Unknown')}")
            print(f"   Gender: {getattr(voice, 'gender', 'Unknown')}")
            print()
    else:
        print("No voices found!")
    
    # Test the current voice selection
    print("🔊 Testing current voice selection...")
    speak("Hello! This is your Claude Code voice assistant.")

def test_voice_notification() -> None:
    """Manual test mode - simulate different notification scenarios"""
    print("Testing voice notification system...")
    
    # First, show available voices
    list_available_voices()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Permission Request",
            "context": "permission_request",
            "tool": "Bash",
            "result": "Requesting permission to use Bash"
        },
        {
            "name": "Successful Tool Completion",
            "context": "tool_completion", 
            "tool": "Read",
            "result": "File contents loaded successfully"
        },
        {
            "name": "Tool Error",
            "context": "tool_completion",
            "tool": "Write", 
            "result": "Error: Permission denied"
        },
        {
            "name": "Waiting/Ready",
            "context": "waiting",
            "tool": "",
            "result": "Claude is ready"
        },
        {
            "name": "Automatic Compact",
            "context": "compact_notification",
            "tool": "automatic",
            "result": "Starting automatic compacting"
        },
        {
            "name": "Manual Compact",
            "context": "compact_notification",
            "tool": "manual",
            "result": "Starting manual compacting"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Test {i}: {scenario['name']} ---")
        print(f"Context: {scenario['context']}")
        print(f"Tool: {scenario['tool']}")
        print(f"Result: {scenario['result']}")
        
        text = get_simple_notification(scenario['context'], scenario['tool'])
        
        print(f"Simple notification: {text}")
        print("Speaking...")
        speak(text or "Notification received.")
        print("Done.")
    
    print("\nAll tests complete!")

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

    # --- NEW DYNAMIC LOGIC ---
    final_text = ""
    # 1. Try to generate a dynamic notification first
    if context == "tool_completion":
        dynamic_text = get_dynamic_notification(tool, result_summary)
        if dynamic_text:
            final_text = dynamic_text
            
    # 2. If dynamic generation failed or isn't applicable, use the simple one
    if not final_text:
        final_text = get_simple_notification(context, tool)
    
    # 3. Final fallback to ensure we always say something
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
    # If run directly, enter test mode
    test_voice_notification()