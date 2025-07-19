# Claude Code Hooks Documentation

This directory contains custom hooks for Claude Code that extend functionality and provide safety features.

## =� Pre-Tool-Use Hook (Deletion Prevention System)

### Overview
The `pre_tool_use.py` hook provides comprehensive protection against destructive deletion commands across multiple platforms and shells.

### Features
- **Universal Command Blocking**: Blocks ALL deletion/removal commands regardless of target
- **Multi-Platform Support**: Windows CMD, PowerShell, Bash, and Unix/Linux commands
- **Voice Notifications**: Audible alerts when dangerous commands are blocked
- **Comprehensive Logging**: Full audit trail of blocked operations
- **Zero False Negatives**: Aggressive blocking to prevent any accidental deletions

### Blocked Commands

#### Basic Deletion Commands (ALL VARIATIONS BLOCKED)
- `rm` - All rm commands (with or without flags)
- `del` - All Windows del commands 
- `erase` - All Windows erase commands
- `rmdir` - All directory removal commands
- `remove-item` - All PowerShell removal commands
- `ri` - PowerShell Remove-Item alias

#### Advanced Destructive Patterns
- **Recursive/Force Flags**: `-rf`, `-fr`, `-r`, `-f`, `/s`, `/q`, `/f`, `-Recurse`, `-Force`
- **Glob Patterns**: `*`, `?`, `[...]`, `{...}`, `.*` wildcards
- **Pipeline Operations**: `get-childitem | remove-item`, `ls | rm`, etc.
- **System Utilities**: `format`, `diskpart`, `cipher /w`, `sdelete`, `shred`
- **Registry Operations**: `reg delete`, `regedit -s`
- **Service Management**: `sc delete`, `net stop`, `taskkill /f`
- **Network/Boot**: `netsh reset`, `bcdedit delete`, `bootrec /fixmbr`

### Protected Directory Examples
While ALL deletion commands are blocked, the system originally protected:
- `apps/`, `src/`, `.git/`, `node_modules/`
- `build/`, `dist/`, `public/`, `components/`
- `docs/`, `tests/`, `config/`, `utils/`
- IDE dirs: `.vscode/`, `.idea/`, `__pycache__/`

### Voice Notifications
When a dangerous command is blocked, you'll hear:
- "Blocked dangerous rm rf command" - for `rm -rf` variations
- "Blocked dangerous deletion command" - for `del`/`erase` commands  
- "Blocked disk format command" - for `format` commands
- "Blocked PowerShell removal command" - for PowerShell operations
- "Blocked dangerous command" - for other destructive operations

### Configuration
The hook is configured in `settings.json`:
```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      {
        "type": "command",
        "command": "uv run C:/Users/NATH/.claude/hooks/pre_tool_use.py",
        "timeout": 30
      }
    ]
  }
]
```

### Logging
All blocked operations are logged to `debug.log` with:
- Timestamp
- Session ID
- Blocked command
- Reason for blocking
- Working directory

### Testing Examples

####  Safe Commands (Allowed)
```bash
echo "hello"
ls -la
cat file.txt
mkdir new_folder
touch file.txt
```

#### L Blocked Commands (All Variations)
```bash
rm file.txt                    # Blocked: rm command detected
rm -rf apps/                   # Blocked: rm -rf detected  
del /f /q *.txt               # Blocked: del /f detected
rmdir /s folder               # Blocked: rmdir /s detected
Remove-Item -Recurse folder   # Blocked: PowerShell Remove-Item -Recurse detected
format c:                     # Blocked: Format drive command detected
```

### Dependencies
- `pyttsx3>=2.99` - Text-to-speech for voice notifications
- `pywin32>=306` - Windows system integration

### Safety Philosophy
This hook follows a "fail-safe" approach:
- **Block First, Ask Later**: All deletion patterns are blocked immediately
- **Zero Tolerance**: No exceptions for "safe" deletion operations
- **Comprehensive Coverage**: Covers all known destructive command patterns
- **Multi-Platform**: Works across Windows, Linux, and macOS environments
- **Auditable**: Full logging for security compliance

---

## 📝 Other Hooks

### Post-Tool-Use Hook (`post_tool_use.py`)
**Purpose**: Automatic git checkpoint system triggered after file modifications

**Features**:
- Monitors Write/Edit/MultiEdit operations via settings matcher
- Creates intelligent git commits with AI-generated messages
- Integrates with Smart Git Checkpoints utility system
- Processes tool context and session information

**Configuration**:
```json
"PostToolUse": [
  {
    "matcher": "Write|Edit|MultiEdit", 
    "hooks": [
      {
        "type": "command",
        "command": "uv run C:/Users/NATH/.claude/hooks/post_tool_use.py",
        "timeout": 60
      }
    ]
  }
]
```

**Dependencies**: `requests>=2.31.0`

### General Notifications Hook (`notifications.py`)
**Purpose**: Centralized voice notification system for Claude Code events

**Features**:
- Text-to-speech notifications using pyttsx3
- Smart voice selection with gender preference detection
- Fallback error handling for voice system failures
- Integration with smart voice utility for complex notifications

**Voice Selection Logic**:
- Prefers female voices (Zira, Hazel, Helen)
- Automatic fallback to alternative voices
- Configurable speech rate (185 WPM)

**Dependencies**: `pyttsx3>=2.99`, `pywin32>=306`

### Pre-Compact Hook (`pre_compact.py`)
**Purpose**: Voice notification before conversation compacting operations

**Features**:
- Detects manual vs automatic compacting modes
- Announces compacting operations via voice
- Graceful fallback if smart voice utilities fail
- Comprehensive error handling with voice backup

**Voice Messages**:
- "Automatic compacting the conversation" (auto mode)
- "Manual compacting the conversation" (manual mode)
- "Compacting the conversation" (fallback)

**Dependencies**: `pyttsx3>=2.99`, `pywin32>=306`

### Stop Hook (`stop.py`)
**Purpose**: Voice notification when Claude Code session terminates

**Features**:
- Session end notifications
- Integration with smart voice notification system
- Handles both normal and error termination scenarios
- Provides session summary context

**Dependencies**: `google-generativeai>=0.5.0`, `pyttsx3>=2.99`, `pywin32>=306`

### Placeholder Hooks
**Note**: The following hook files exist but appear to be placeholder/minimal implementations:
- `subagent_stop.py` - Subagent termination handling (1 line)
- `user_prompt_submit.py` - User prompt processing (1 line)

---

## 🔧 Utilities

### Smart Voice Notify (`utils/smart_voice_notify.py`)
**Purpose**: Advanced voice notification engine with intelligent context processing

**Core Functions**:
- `speak(text, voice_index)` - Core TTS with voice selection
- `get_simple_notification(context, tool)` - Generate context-aware messages
- `process_notification(payload)` - Main notification processor
- `process_stop_notification(payload)` - Session termination handling
- `process_compact_notification(payload)` - Compacting announcements

**Advanced Features**:
- **Intelligent Voice Selection**: Automatic detection of female/preferred voices
- **Context-Aware Messaging**: Different notification styles based on operation type
- **Permission Request Handling**: Smart prompts for tool permissions
- **Error Recovery**: Multiple fallback mechanisms for voice failures
- **Conversation Analysis**: Natural language processing for notification content

**Voice Selection Priority**:
1. Female voices (Zira, Hazel, Helen) - preferred
2. Alternative system voices - fallback
3. Default system voice - last resort

**Notification Categories**:
- Permission requests (tool usage confirmations)
- Completion notifications (task finished)
- Error notifications (failure alerts)
- Status updates (progress information)
- Session management (start/stop/compact)

**Dependencies**: `pyttsx3>=2.99`, `pywin32>=306`

### Smart Git Checkpoints (`utils/smart_git_checkpoints.py`)
**Purpose**: AI-powered automatic git commit system with intelligent message generation

**Core Architecture**:
- `SmartGitCheckpoints` class - Main checkpoint processor
- `process_checkpoint(payload)` - Primary entry point
- `process_tool_checkpoint(payload)` - Public interface function

**Advanced Features**:
- **Tool Context Analysis**: Extracts meaningful context from Claude Code operations
- **Session Context Processing**: Analyzes conversation transcripts for commit context
- **Git Change Analysis**: Intelligent detection of file modifications and additions
- **AI Commit Generation**: Uses Google Generative AI for descriptive commit messages
- **Change Classification**: Categorizes changes (new features, bug fixes, improvements)

**Commit Message Intelligence**:
- Analyzes file changes and tool operations
- Generates semantic commit messages following conventional formats
- Includes context from Claude Code session transcripts
- Handles multiple file changes with unified descriptions
- Fallback to descriptive manual messages when AI unavailable

**Error Handling**:
- Git repository validation
- Change detection and staging
- AI API quota management (noted: current quota exceeded issues)
- Graceful degradation when external services fail

**Dependencies**: No external dependencies (uses subprocess for git operations)

**Current Issues Detected**:
- Google Generative AI quota exhaustion (multiple 429 errors in debug.log)
- Need for fallback commit message generation when AI unavailable

---

## 🚨 Security Analysis & Recommendations

### Current Security Posture

#### ✅ Strengths
1. **Comprehensive Deletion Prevention**: Blocks all major destructive command patterns
2. **Fail-Safe Design**: Hooks fail open to prevent system lockout
3. **Audit Logging**: Full trail of blocked operations and system events
4. **Multi-Platform Coverage**: Windows, Linux, macOS command protection
5. **Voice Alerts**: Immediate notification of security events

#### ⚠️ Areas for Improvement

**High Priority Issues**:
1. **API Key Exposure Risk**: Google Generative AI integration may expose API credentials
2. **Log File Security**: Debug logs stored in plain text without access controls
3. **Dependency Vulnerabilities**: Multiple external dependencies need security auditing

**Medium Priority Issues**:
1. **Error Handling**: Some hooks may expose system information in error messages
2. **Path Traversal**: File operations should validate paths more strictly
3. **Code Injection**: Git commit message generation needs input sanitization

**Low Priority Issues**:
1. **Voice System Privacy**: TTS system may cache spoken content
2. **Session Data**: Transcript processing could expose sensitive information

### Security Recommendations

#### Immediate Actions (High Priority)
1. **Secure API Credentials**:
   - Move Google AI API keys to environment variables
   - Implement credential rotation mechanism
   - Add API key validation and sanitization

2. **Enhance Logging Security**:
   - Implement log rotation and retention policies
   - Add log file access controls (600 permissions)
   - Sanitize sensitive data from log entries

3. **Dependency Audit**:
   - Regular security scanning of all dependencies
   - Pin dependency versions for reproducible builds
   - Monitor for CVE notifications

#### Short-term Improvements (Medium Priority)
1. **Input Validation**:
   - Sanitize all user inputs before processing
   - Validate file paths to prevent traversal attacks
   - Escape shell commands and git commit messages

2. **Error Handling Enhancement**:
   - Implement secure error reporting
   - Avoid exposing system paths and internals
   - Add structured error codes

3. **Access Controls**:
   - Implement hook execution permissions
   - Add user authentication for sensitive operations
   - Create hook bypass mechanisms for administrators

#### Long-term Enhancements (Low Priority)
1. **Encrypted Storage**:
   - Encrypt sensitive configuration data
   - Secure storage for session transcripts
   - Protected backup mechanisms

2. **Advanced Monitoring**:
   - Real-time security event monitoring
   - Anomaly detection for unusual patterns
   - Integration with security information systems

### Compliance Considerations

**Data Protection**:
- Session transcripts may contain sensitive information
- Voice recordings could be cached by TTS systems
- Log files contain operational and security data

**Recommended Policies**:
- Regular purging of old session data
- Access controls for debugging information
- Documentation of data retention practices

### Emergency Procedures

**If Security Incident Detected**:
1. Review debug.log for suspicious activity
2. Check for unauthorized file modifications
3. Validate hook integrity and configuration
4. Rotate any potentially compromised credentials

**Hook Bypass for Emergencies**:
```json
// Temporarily disable all hooks
"hooks": {}
```

**Recovery Procedures**:
- Restore from known-good configuration
- Re-enable hooks incrementally
- Validate system functionality

### Testing & Validation

**Security Testing Checklist**:
- [ ] Deletion prevention blocks all dangerous patterns
- [ ] Voice notifications work without exposing data
- [ ] Git checkpoints don't commit sensitive information
- [ ] Error handling doesn't leak system information
- [ ] Dependencies are up-to-date and secure

**Regular Maintenance**:
- Monthly dependency updates
- Quarterly security reviews
- Annual penetration testing
- Continuous monitoring of debug logs

---

## 🛡️ Final Security Notice

The deletion prevention hook is designed to be **extremely aggressive** in blocking potentially destructive operations. This is intentional to prevent accidental data loss. 

**For Legitimate Deletion Operations**:
1. Use file explorer/finder for single file deletions
2. Temporarily disable the hook by modifying `settings.json`
3. Use alternative tools outside of Claude Code's Bash integration
4. Contact system administrator for bypass procedures

**Security Philosophy**: *"It's better to be overly cautious with deletions than to lose important data or compromise system security."*

**Emergency Contact**: Review system logs and configuration if unexpected behavior occurs.