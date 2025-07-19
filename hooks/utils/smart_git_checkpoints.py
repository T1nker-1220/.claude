#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import subprocess
import pathlib
import datetime
import tempfile
from typing import Dict, Any, Tuple, Optional

CLAUDE_EXECUTABLE = "claude" 

class SmartGitCheckpoints:
    """AI-powered git checkpointing system for Claude Code sessions."""
    
    def __init__(self):
        self.claude_executable = CLAUDE_EXECUTABLE
        self.debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
        self.logs_dir = pathlib.Path("C:/Users/NATH/.claude/logs")
    
    def process_checkpoint(self, payload: Dict[str, Any]) -> bool:
        """Main checkpoint processing function called by post_tool_use.py"""
        
        try:
            # Extract tool context
            tool_context = self._extract_tool_context(payload)
            
            # Only checkpoint file-changing tools
            if not self._should_checkpoint(tool_context):
                self._log_debug(f"Skipping checkpoint for tool: {tool_context.get('tool_name')}")
                return True
            
            # Extract session context from transcript
            session_context = self._extract_session_context(payload)
            # Add session_id to context for comprehensive logging
            session_context["session_id"] = payload.get("session_id")
            
            # Load tool usage history from logs
            tool_history = self._load_tool_usage_history(payload.get("session_id"))
            
            # Analyze git changes
            git_context = self._analyze_git_changes()
            
            # Skip if no actual changes
            if git_context.get("status") == "no_changes":
                self._log_debug("No git changes detected, skipping checkpoint")
                return True
            
            # Generate intelligent commit message with tool history
            commit_message = self._generate_smart_commit(tool_context, session_context, git_context, tool_history)
            
            # Create the checkpoint commit
            return self._create_commit(commit_message)
            
        except Exception as e:
            self._log_debug(f"Checkpoint processing error: {e}")
            return False
    
    def _extract_tool_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tool usage context from hook payload."""
        tool_response = payload.get("tool_response", {})
        
        # Check for explicit success field first (Claude Code format)
        if isinstance(tool_response, dict) and "success" in tool_response:
            success = tool_response.get("success", False)
        elif isinstance(tool_response, dict) and "filePath" in tool_response:
            # Edit/Write tools return {'filePath': '...'} on success
            success = True
        else:
            # Fallback: check for error indicators
            tool_response_str = str(tool_response).lower()
            has_errors = any(err in tool_response_str for err in ["error", "failed", "exception", "denied"])
            success = not has_errors
        
        context = {
            "tool_name": payload.get("tool_name", "unknown"),
            "tool_input": payload.get("tool_input", {}),
            "tool_response": tool_response,
            "success": success
        }
        
        # Debug logging
        self._log_debug(f"Tool context: {context['tool_name']}, success: {success}, response: {str(tool_response)[:100]}...")
        
        return context
    
    def _should_checkpoint(self, tool_context: Dict[str, Any]) -> bool:
        """Determine if this tool usage should trigger a checkpoint."""
        file_changing_tools = ["Write", "Edit", "MultiEdit"]
        tool_name = tool_context.get("tool_name", "")
        success = tool_context.get("success", False)
        
        should_checkpoint = tool_name in file_changing_tools and success
        
        self._log_debug(f"Checkpoint decision: tool={tool_name}, success={success}, should_checkpoint={should_checkpoint}")
        
        return should_checkpoint
    
    def _extract_session_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user intent directly from Claude Code transcript - YouTuber's approach."""
        transcript_path = pathlib.Path(payload.get("transcript_path", ""))
        
        if not transcript_path.exists():
            self._log_debug(f"Transcript not found: {transcript_path}")
            return {"user_intent": ["transcript not found"], "recent_activity": []}
        
        try:
            user_messages = []
            
            # Read transcript file directly (JSONL format like YouTuber)
            with transcript_path.open("r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            
            self._log_debug(f"Reading transcript with {len(lines)} lines...")
            
            # Parse recent entries (last 20 lines for performance)
            for i, line in enumerate(reversed(lines[-20:])):
                try:
                    record = json.loads(line.strip())
                    
                    # Look for user messages in Claude Code format
                    record_type = record.get("type", "")
                    if record_type == "user":
                        content = record.get("content", "")
                        if isinstance(content, str) and len(content.strip()) > 15:
                            clean_content = content.strip()
                            user_messages.append(clean_content)
                            self._log_debug(f"Found user message: {clean_content[:80]}...")
                            if len(user_messages) >= 2:  # Get last 2 user messages
                                break
                                
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if user_messages:
                # Return most recent message or combine recent ones
                if len(user_messages) == 1:
                    intent = user_messages[0]
                else:
                    intent = " | ".join(reversed(user_messages[-2:]))  # Last 2 messages
                
                self._log_debug(f"Extracted user intent: {intent[:100]}...")
                return {
                    "user_intent": [intent],
                    "recent_activity": [],
                    "has_context": True
                }
            else:
                self._log_debug("No user messages found in transcript")
                # Instead of generic message, try to infer from tool history
                return {
                    "user_intent": ["file modification requested"],
                    "recent_activity": [],
                    "has_context": False
                }
            
        except Exception as e:
            self._log_debug(f"Transcript reading error: {e}")
            return {"user_intent": [f"error reading transcript: {e}"], "recent_activity": []}
    
    def _load_tool_usage_history(self, session_id: str) -> Dict[str, Any]:
        """Load recent tool usage history from logs directory."""
        try:
            tool_history = {
                "pre_tool_use": [],
                "post_tool_use": [],
                "recent_tools": [],
                "file_operations": [],
                "session_summary": ""
            }
            
            # Read recent tool usage logs (last 10 entries per log file)
            log_files = [
                "pre_tool_use.json",
                "post_tool_use.json"
            ]
            
            current_session_tools = []
            all_recent_tools = []
            
            for log_file in log_files:
                log_path = self.logs_dir / log_file
                if log_path.exists():
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        # Get last 10 entries
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        
                        for line in recent_lines:
                            try:
                                entry = json.loads(line.strip())
                                all_recent_tools.append(entry)
                                
                                # Filter current session if session_id available
                                if session_id and entry.get("session_id") == session_id:
                                    current_session_tools.append(entry)
                                    
                                # Track file operations specifically
                                if entry.get("tool_name") in ["Write", "Edit", "MultiEdit"]:
                                    tool_input = entry.get("tool_input", {})
                                    file_path = tool_input.get("file_path", "")
                                    if file_path:
                                        tool_history["file_operations"].append({
                                            "tool": entry.get("tool_name"),
                                            "file": pathlib.Path(file_path).name,
                                            "timestamp": entry.get("timestamp"),
                                            "operation": self._classify_file_operation(tool_input)
                                        })
                                        
                            except json.JSONDecodeError:
                                continue
                                
                    except Exception as e:
                        self._log_debug(f"Error reading {log_file}: {e}")
                        continue
            
            # Use current session tools if available, otherwise recent tools
            relevant_tools = current_session_tools if current_session_tools else all_recent_tools[-5:]
            
            # Analyze tool patterns
            tool_summary = self._analyze_tool_patterns(relevant_tools)
            
            tool_history.update({
                "recent_tools": relevant_tools,
                "session_summary": tool_summary,
                "total_operations": len(relevant_tools),
                "file_count": len(tool_history["file_operations"])
            })
            
            self._log_debug(f"Loaded tool history: {len(relevant_tools)} operations, {len(tool_history['file_operations'])} file ops")
            
            return tool_history
            
        except Exception as e:
            self._log_debug(f"Tool history loading error: {e}")
            return {
                "recent_tools": [],
                "file_operations": [],
                "session_summary": "tool history unavailable",
                "total_operations": 0,
                "file_count": 0
            }
    
    def _classify_file_operation(self, tool_input: Dict[str, Any]) -> str:
        """Classify the type of file operation based on tool input."""
        if "new_string" in tool_input and "old_string" in tool_input:
            old_str = tool_input.get("old_string", "")
            new_str = tool_input.get("new_string", "")
            
            if not old_str:
                return "create"
            elif not new_str:
                return "delete"
            else:
                # Analyze the nature of the change
                if len(new_str) > len(old_str) * 2:
                    return "expand"
                elif len(new_str) < len(old_str) * 0.5:
                    return "shrink"
                else:
                    return "modify"
        elif "content" in tool_input:
            return "write"
        else:
            return "edit"
    
    def _analyze_tool_patterns(self, tools: list) -> str:
        """Analyze patterns in tool usage to understand the session intent."""
        if not tools:
            return "no recent activity"
            
        # Count tool types
        tool_counts = {}
        file_operations = []
        
        for tool in tools:
            tool_name = tool.get("tool_name", "unknown")
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            # Track file operations
            if tool_name in ["Write", "Edit", "MultiEdit"]:
                tool_input = tool.get("tool_input", {})
                file_path = tool_input.get("file_path", "")
                if file_path:
                    file_operations.append(pathlib.Path(file_path).name)
        
        # Determine primary activity
        if tool_counts.get("Write", 0) >= 2:
            activity = "creating files"
        elif tool_counts.get("Edit", 0) >= 2:
            activity = "editing files"
        elif tool_counts.get("MultiEdit", 0) >= 1:
            activity = "multi-file editing"
        elif tool_counts.get("Read", 0) >= 3:
            activity = "reading/analyzing code"
        elif tool_counts.get("Bash", 0) >= 2:
            activity = "executing commands"
        else:
            activity = "mixed operations"
            
        # Add file context if available
        unique_files = list(set(file_operations))
        if unique_files:
            if len(unique_files) == 1:
                activity += f" on {unique_files[0]}"
            elif len(unique_files) <= 3:
                activity += f" on {', '.join(unique_files)}"
            else:
                activity += f" on {len(unique_files)} files"
                
        return activity
    
    def _extract_file_info(self, tool_input: Dict[str, Any]) -> Dict[str, str]:
        """Extract filename and path info from tool input."""
        file_path = tool_input.get("file_path", "")
        if file_path:
            path_obj = pathlib.Path(file_path)
            return {
                "filename": path_obj.name,
                "directory": path_obj.parent.name,
                "extension": path_obj.suffix
            }
        return {"filename": "unknown", "directory": "", "extension": ""}
    
    def _analyze_git_changes(self) -> Dict[str, Any]:
        """Analyze current git repository changes."""
        try:
            # Try to find git repository from working directory
            working_dir = pathlib.Path.cwd()
            
            # Check if we're in a git repository
            git_check = subprocess.run(
                ["git", "rev-parse", "--git-dir"], 
                capture_output=True, text=True, timeout=5, cwd=working_dir
            )
            
            # If not in git repo, try to find one by looking in common project locations
            if git_check.returncode != 0:
                # Try common project locations
                potential_dirs = [
                    working_dir,
                    working_dir.parent,
                    pathlib.Path.home() / "Documents",
                    pathlib.Path.home() / "Projects",
                ]
                
                git_dir = None
                for check_dir in potential_dirs:
                    if check_dir.exists():
                        git_check = subprocess.run(
                            ["git", "rev-parse", "--git-dir"], 
                            capture_output=True, text=True, timeout=5, cwd=check_dir
                        )
                        if git_check.returncode == 0:
                            git_dir = check_dir
                            working_dir = git_dir
                            break
                
                if not git_dir:
                    self._log_debug(f"No git repository found. Checked: {[str(d) for d in potential_dirs]}")
                    return {"status": "no_git", "files": []}
            
            # Get git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, timeout=10
            )
            
            if status_result.returncode != 0:
                return {"status": "git_error", "files": []}
            
            # Parse changed files
            changed_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line.strip():
                    status_code = line[:2].strip()
                    filename = line[3:].strip()
                    changed_files.append({
                        "file": pathlib.Path(filename).name,
                        "path": filename,
                        "status": self._interpret_git_status(status_code),
                        "extension": pathlib.Path(filename).suffix
                    })
            
            return {
                "status": "changes_detected" if changed_files else "no_changes",
                "files": changed_files,
                "file_count": len(changed_files),
                "primary_file": changed_files[0] if changed_files else None
            }
            
        except Exception as e:
            self._log_debug(f"Git analysis error: {e}")
            return {"status": f"error: {e}", "files": []}
    
    def _interpret_git_status(self, status_code: str) -> str:
        """Convert git status codes to readable actions."""
        status_map = {
            "A": "added",
            "M": "modified",
            "D": "deleted", 
            "R": "renamed",
            "C": "copied",
            "??": "untracked",
            "AM": "added+modified",
            "MM": "modified"
        }
        return status_map.get(status_code, "changed")
    
    def _generate_smart_commit(self, tool_context: Dict[str, Any], 
                              session_context: Dict[str, Any], 
                              git_context: Dict[str, Any],
                              tool_history: Dict[str, Any]) -> str:
        """Generate intelligent commit message using AI analysis."""
        
        prompt = self._build_ai_prompt(tool_context, session_context, git_context, tool_history)
        
        # Debug: Log the actual prompt being sent
        self._log_debug(f"Generated prompt for LLM (first 300 chars): {prompt[:300]}...")
        
        try:
            # Call Claude Code Task tool for intelligent commit generation
            response = self._call_claude_task(prompt)
            commit_message = response.strip()
            
            # Clean and validate AI response
            if commit_message and len(commit_message) > 5:
                cleaned_message = self._clean_commit_message(commit_message)
                return cleaned_message
            else:
                return self._create_fallback_commit(tool_context, git_context)
                
        except Exception as e:
            self._log_debug(f"AI commit generation failed: {e}")
            return self._create_fallback_commit(tool_context, git_context)
    
    def _build_ai_prompt(self, tool_context: Dict[str, Any], 
                        session_context: Dict[str, Any], 
                        git_context: Dict[str, Any],
                        tool_history: Dict[str, Any]) -> str:
        """Build AI prompt for intelligent commit message generation."""
        
        # Extract detailed context
        user_intent = " | ".join(session_context.get("user_intent", ["unknown"]))[:200]
        tool_name = tool_context.get("tool_name", "unknown")
        files_changed = [f["file"] for f in git_context.get("files", [])]
        primary_file = git_context.get("primary_file", {})
        
        # Get file content context from tool_input
        tool_input = tool_context.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        old_string = tool_input.get("old_string", "")[:100]
        new_string = tool_input.get("new_string", "")[:100]
        
        # Extract specific changes
        change_description = ""
        if old_string and new_string:
            change_description = f"Changed: '{old_string}' → '{new_string}'"
        
        # Extract tool history context
        session_activity = tool_history.get("session_summary", "unknown activity")
        total_ops = tool_history.get("total_operations", 0)
        file_ops = tool_history.get("file_operations", [])
        
        # Build tool history summary
        tool_context_summary = ""
        if file_ops:
            recent_file_ops = file_ops[-3:]  # Last 3 file operations
            ops_summary = []
            for op in recent_file_ops:
                ops_summary.append(f"{op.get('operation', 'edit')} {op.get('file', 'file')}")
            tool_context_summary = f"Recent: {', '.join(ops_summary)}"
        
        prompt = f"""Generate a git commit message using conventional commit format.

Context:
- User request: {user_intent}
- File: {primary_file.get('file', 'unknown')}
- Operation: {tool_name}
- Session activity: {session_activity}
- Change: {change_description}

Rules:
- Format: type(scope): description
- Under 50 characters
- Present tense
- Types: feat, fix, refactor, docs, style, test, chore

Examples:
- feat(auth): add login validation
- fix(parser): handle null values
- refactor(ui): extract components

Generate ONLY the commit message:"""
        
        return prompt
    
    def _clean_commit_message(self, message: str) -> str:
        """Clean and validate AI-generated commit message."""
        # Remove quotes and extra whitespace
        message = message.strip().strip('"').strip("'").strip()
        
        # Take only the first line
        first_line = message.split('\n')[0]
        
        # Ensure reasonable length
        if len(first_line) > 72:
            first_line = first_line[:69] + "..."
        
        # Basic validation - ensure it looks like a commit message
        if ':' not in first_line or len(first_line) < 10:
            return self._create_fallback_commit({}, {})
        
        return first_line
    
    def _create_fallback_commit(self, tool_context: Dict[str, Any], 
                               git_context: Dict[str, Any]) -> str:
        """Create fallback commit when AI generation fails."""
        tool_name = tool_context.get("tool_name", "edit")
        files = git_context.get("files", [])
        
        if len(files) == 1:
            file_info = files[0]
            filename = file_info.get("file", "file")
            status = file_info.get("status", "modified")
            return f"chore: {status} {filename}"
        elif len(files) > 1:
            primary = files[0].get("file", "files") if files else "files"
            return f"chore: update {primary} +{len(files)-1} more"
        else:
            return f"chore: {tool_name.lower()} operation"
    
    def _create_commit(self, commit_message: str) -> bool:
        """Create git commit with the generated message."""
        try:
            # Stage all changes
            add_result = subprocess.run(
                ["git", "add", "."], 
                capture_output=True, text=True, timeout=30
            )
            
            if add_result.returncode != 0:
                self._log_debug(f"Git add failed: {add_result.stderr}")
                return False
            
            # Create commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message], 
                capture_output=True, text=True, timeout=30
            )
            
            if commit_result.returncode == 0:
                self._log_debug(f" Smart commit created: {commit_message}")
                return True
            else:
                self._log_debug(f"L Git commit failed: {commit_result.stderr}")
                return False
                
        except Exception as e:
            self._log_debug(f"Commit creation error: {e}")
            return False
    
    def _call_claude_task(self, prompt: str) -> str:
        """Call Claude Code Task tool to generate intelligent commit message."""
        try:
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                # Ultra-compact prompt for minimal token usage
                # Extract key info from the original detailed prompt
                task_prompt = f"""Generate git commit message from this context:

{prompt[:200]}

Format: type(scope): description
Max 50 chars. Examples:
feat(auth): add login
fix(api): handle errors
chore: update config

Output only the commit message:"""
                
                temp_file.write(task_prompt)
                temp_file_path = temp_file.name
            
            try:
                # Call Claude Code with the Task tool
                # Use shell=True on Windows to handle .cmd files properly
                # Use new LLM utility for cost-efficient queries (Claude 3.5 Haiku)
                try:
                    from .llms import ask_concise
                    # Debug: Log what we're sending to LLM utility
                    self._log_debug(f"Sending to LLM utility (first 200 chars): {task_prompt[:200]}...")
                    response = ask_concise(task_prompt)
                    self._log_debug(f"✅ LLM utility success: {response}")
                    
                    # Check if this is the hardcoded fallback
                    if response == "chore: update files":
                        self._log_debug("LLM returned hardcoded fallback, trying direct claude command")
                    elif response and response != "AI response unavailable" and len(response) > 10:
                        self._log_debug(f"LLM gave meaningful response: {response}")
                        return response
                    else:
                        self._log_debug("LLM response appears to be fallback, trying original method")
                        
                except ImportError:
                    self._log_debug("LLM utilities not available, using fallback")
                except Exception as e:
                    self._log_debug(f"LLM utility error: {e}")
                
                # Fallback to original claude command with Haiku for cost efficiency
                
                result = subprocess.run([
                    self.claude_executable, 
                    "--print",  # Print response and exit (non-interactive)
                    "--model", "claude-3-5-haiku-20241022",  # Use Haiku for cost efficiency
                    "--output-format", "text",  # Plain text output only
                    "--append-system-prompt", "Be extremely concise. Output only the requested git commit message with no explanations, analysis, or additional text.",
                    f"@{temp_file_path}"  # Read prompt from file
                ], 
                capture_output=True, 
                text=True, 
                timeout=30,  # Reduced timeout for simple task
                cwd=pathlib.Path.cwd(),
                shell=True)  # Required for .cmd files on Windows
                
                if result.returncode == 0:
                    raw_response = result.stdout.strip()
                    self._log_debug(f"Claude Task raw response: {raw_response[:50]}...")
                    
                    # Aggressive cleaning for minimal token usage
                    cleaned_response = self._extract_commit_message_only(raw_response)
                    self._log_debug(f"Claude Task cleaned: {cleaned_response}")
                    return cleaned_response
                else:
                    self._log_debug(f"Claude Task failed: {result.stderr}")
                    raise Exception(f"Claude Task failed: {result.stderr}")
                    
            finally:
                # Clean up temporary file
                try:
                    pathlib.Path(temp_file_path).unlink()
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            self._log_debug("Claude Task timed out")
            raise Exception("Claude Task timeout")
        except FileNotFoundError:
            self._log_debug("Claude executable not found - is Claude Code installed?")
            raise Exception("Claude executable not found")
        except Exception as e:
            self._log_debug(f"Claude Task error: {e}")
            raise
    
    def _clean_commit_response(self, response: str) -> str:
        """Extract clean commit message from Claude response."""
        if not response:
            return ""
        
        # Remove common prefixes and thinking patterns
        response = response.strip()
        
        # Look for lines that match commit message pattern
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip().strip('"').strip("'").strip('`')
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip explanatory lines
            if any(skip in line.lower() for skip in [
                'here is', 'the commit', 'message is', 'based on', 'according to',
                'looking at', 'i think', 'this appears', 'let me', 'your commit'
            ]):
                continue
            
            # Look for proper commit format: type(scope): description
            if ':' in line and len(line) > 5 and len(line) < 72:
                # Check for conventional commit types
                if any(commit_type in line.lower() for commit_type in 
                       ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'build', 'ci']):
                    return line.strip()
                    
                # Or any line with reasonable commit-like structure
                elif line.count(':') == 1 and '(' in line and ')' in line:
                    return line.strip()
        
        # If no proper format found, look for any reasonable short line
        for line in lines:
            line = line.strip().strip('"').strip("'").strip('`')
            if line and len(line) > 10 and len(line) < 72 and ':' in line:
                return line
        
        # Ultimate fallback - return first meaningful line
        for line in lines:
            line = line.strip().strip('"').strip("'").strip('`')
            if line and len(line) > 5:
                return line[:50]
        
        return "chore: update files"  # Hard fallback
    
    def _extract_commit_message_only(self, response: str) -> str:
        """Ultra-aggressive extraction - get ONLY the commit message, nothing else."""
        if not response:
            return "chore: update files"
            
        # Remove any common prefixes/suffixes
        response = response.strip()
        
        # Split by lines and find the shortest valid commit message
        lines = [line.strip().strip('"').strip("'").strip('`').strip('*').strip('-') 
                for line in response.split('\n') if line.strip()]
        
        commit_candidates = []
        
        for line in lines:
            # Skip obviously non-commit lines
            if len(line) < 8 or len(line) > 60:
                continue
                
            # Skip lines with explanatory words
            if any(word in line.lower() for word in [
                'message', 'commit', 'here', 'based', 'according', 'would', 'should',
                'this', 'that', 'for', 'with', 'using', 'example', 'like'
            ]):
                continue
                
            # Must have colon and parentheses for conventional format
            if ':' in line and '(' in line and ')' in line:
                # Check for conventional commit types
                if any(ctype in line.lower() for ctype in [
                    'feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'build', 'ci'
                ]):
                    commit_candidates.append(line)
        
        # Return the shortest valid candidate (most likely to be clean)
        if commit_candidates:
            return min(commit_candidates, key=len)
            
        # Fallback: look for any line with colon
        for line in lines:
            if ':' in line and len(line) > 5 and len(line) < 60:
                return line
                
        # Ultimate fallback
        return "chore: update files"
    
    def _log_debug(self, message: str):
        """Log debug information for troubleshooting."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            with open(self.debug_log, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - SmartCheckpoint: {message}\n")
        except:
            pass  # Fail silently on debug logging

# Public API functions for external usage
def process_tool_checkpoint(payload: Dict[str, Any]) -> bool:
    """
    Main entry point for processing tool-based checkpoints.
    Called by post_tool_use.py hook.
    
    Args:
        payload: Hook payload containing tool_name, tool_input, tool_response, transcript_path
        
    Returns:
        bool: True if checkpoint was successful or skipped, False if error occurred
    """
    checkpoint_manager = SmartGitCheckpoints()
    return checkpoint_manager.process_checkpoint(payload)

def test_checkpoint_system():
    """Test function for manual verification of checkpoint system."""
    print("🧪 Testing Smart Git Checkpoints...")
    
    # Create test payload
    test_payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "test.js"},
        "tool_response": {"success": True},
        "transcript_path": "test_transcript.jsonl"
    }
    
    checkpoint_manager = SmartGitCheckpoints()
    
    # Test context extraction
    tool_context = checkpoint_manager._extract_tool_context(test_payload)
    print(f"=� Tool Context: {tool_context}")
    
    # Test git analysis
    git_context = checkpoint_manager._analyze_git_changes()
    print(f"=� Git Context: {git_context}")
    
    # Test fallback commit message
    fallback_msg = checkpoint_manager._create_fallback_commit(tool_context, git_context)
    print(f"=� Fallback Message: {fallback_msg}")
    
    print(" Test completed!")

if __name__ == "__main__":
    test_checkpoint_system()