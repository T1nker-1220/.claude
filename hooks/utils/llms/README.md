# LLM Utilities for Claude Code Hooks

Cost-efficient AI integration using Claude 3.5 Haiku by default. Supports the command structure: `claude -p --model claude-3-5-haiku-20241022 "<PROMPT>"`

## 🚀 Quick Start

### Simple Usage
```python
from utils.llms import ask, ask_concise

# Basic AI query
response = ask("Generate a commit message for auth.js")

# Cost-efficient query  
summary = ask_concise("Summarize this error")
```

### Full Client Features
```python
from utils.llms import LLMClient

llm = LLMClient()

# Ask with context files
response = llm.ask_with_context("Explain this bug", ["error.log", "config.py"])

# Structured responses
data = llm.ask_structured("Return user info as JSON", format_type="json")

# Usage statistics
stats = llm.get_usage_stats()
```

## 📦 Package Structure

```
hooks/utils/llms/
├── __init__.py          # Package exports and quick start
├── client.py            # Main LLMClient class  
├── config.py            # Configuration management
├── cost_monitor.py      # Token tracking and cost monitoring
├── test.py              # Comprehensive test suite
└── README.md            # This documentation
```

## ⚙️ Configuration

### Default Settings
- **Model**: Claude 3.5 Haiku (cost-efficient)
- **Fallbacks**: Haiku → Sonnet → Manual responses
- **Caching**: 60-minute TTL for repeated queries
- **Timeout**: 30 seconds per request

### Environment Overrides
```bash
export CLAUDE_LLM_MODEL="claude-3-5-sonnet-20241022"
export CLAUDE_LLM_TIMEOUT=45
export CLAUDE_LLM_BUDGET=10000  # Daily token budget
export CLAUDE_LLM_DEBUG=true
```

### Programmatic Configuration
```python
from utils.llms import update_config, apply_preset

# Update specific settings
update_config(default_model="claude-3-5-sonnet-20241022")

# Apply cost/quality presets
apply_preset("ultra_efficient")  # Max cost savings
apply_preset("balanced")         # Default settings
apply_preset("quality_focused")  # Higher quality responses
```

## 💰 Cost Monitoring

### Token Estimation
```python
from utils.llms import estimate_cost

estimate = estimate_cost("Your prompt here")
print(f"Estimated cost: ${estimate['estimated_cost']:.6f}")
print(f"Estimated tokens: {estimate['estimated_total_tokens']}")
```

### Usage Tracking
```python
from utils.llms import get_usage_report

# Get 7-day usage summary
report = get_usage_report(days=7)
print(f"Total cost: ${report['total_cost']:.4f}")
print(f"Total tokens: {report['total_tokens']}")
```

### Budget Management
```python
from utils.llms.cost_monitor import get_cost_monitor

monitor = get_cost_monitor()
monitor.set_budget(daily_tokens=5000, daily_cost=0.50)
```

## 🔧 Integration Examples

### Hook Integration
```python
# In any hook file
from utils.llms import ask_concise

def your_hook(payload):
    error_msg = payload.get("error", "")
    if error_msg:
        summary = ask_concise(f"Summarize this error: {error_msg}")
        return f"Error summary: {summary}"
```

### Smart Git Checkpoints (Already Integrated)
The `smart_git_checkpoints.py` has been updated to use the new LLM utilities automatically:
- Uses `ask_concise()` for commit message generation
- Falls back to original claude command if LLM utils unavailable
- Automatically uses Haiku model for cost efficiency

### Voice Notifications Enhancement
```python
# In notifications.py or similar
from utils.llms import ask_concise

def smart_notification(context):
    summary = ask_concise(f"Create notification text: {context}")
    speak(summary)
```

## 🧪 Testing

### Quick Test
```bash
cd C:\Users\NATH\.claude\hooks\utils\llms
uv run test.py --quick
```

### Full Test Suite
```bash
uv run test.py
```

### Test Results
- ✅ Configuration management
- ✅ Client initialization  
- ✅ Cost estimation and monitoring
- ✅ Error handling and fallbacks
- ✅ Response caching
- ✅ Integration patterns

## 🎯 Key Features

### Cost Efficiency
- **Claude 3.5 Haiku** by default (significantly cheaper than Sonnet)
- **Smart caching** prevents duplicate API calls
- **Token estimation** for cost planning
- **Budget monitoring** with alerts

### Reliability  
- **Automatic fallbacks**: Haiku → Sonnet → Manual responses
- **Comprehensive error handling** with logging
- **Timeout management** prevents hanging
- **Graceful degradation** when Claude CLI unavailable

### Developer Experience
- **Simple API**: Import and use in one line
- **Flexible configuration** via environment or code
- **Usage statistics** for optimization
- **Comprehensive test suite** for validation

## 📊 Performance

### Typical Response Times
- **Haiku**: 1-3 seconds for simple queries
- **Fallback**: Instant manual responses
- **Cache hits**: <100ms

### Cost Comparison
- **Haiku**: ~10x cheaper than Sonnet for similar quality
- **Caching**: Eliminates repeated costs
- **Monitoring**: Prevents budget overruns

## 🔍 Troubleshooting

### Common Issues

**ImportError when using in hooks:**
```python
# Use absolute imports in hook files
from utils.llms import ask, ask_concise
```

**Claude CLI not found:**
- Install Claude Code CLI: https://claude.ai/code
- Set `CLAUDE_EXECUTABLE` environment variable
- LLM utilities will use fallback responses

**High costs:**
- Use `ask_concise()` for simple queries
- Set daily budgets with `set_budget()`
- Apply "ultra_efficient" preset

**Slow responses:**
- Check internet connection
- Reduce timeout in configuration
- Enable caching for repeated queries

### Debug Logging
All operations are logged to `C:/Users/NATH/.claude/hooks/debug.log`:
```
2024-XX-XX - LLMClient: ✅ LLM success with claude-3-5-haiku-20241022: 45 chars
2024-XX-XX - CostMonitor: ⚠️ Daily token budget 80% used: 4000/5000
```

## 🔮 Future Enhancements

- [ ] Response streaming for long queries
- [ ] Multi-language support for international users  
- [ ] Advanced caching with semantic similarity
- [ ] Integration with more Claude Code features
- [ ] Custom model fine-tuning support

## 📄 License

Part of Claude Code Hooks system. Use according to your Claude Code license.

---

**Quick Command Reference:**
```python
from utils.llms import ask, ask_concise, ask_json, LLMClient
```

For questions or issues, check the debug log or run the test suite.