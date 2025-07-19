"""
LLM Utilities Package for Claude Code Hooks
Cost-efficient AI integration using Claude 3.5 Haiku by default

Simple Usage:
    from utils.llms import LLMClient, ask, ask_concise
    
    # Full client with all features
    llm = LLMClient()
    response = llm.ask("Generate a commit message for auth.js")
    
    # Quick convenience functions
    answer = ask("What is this error?")
    summary = ask_concise("Summarize this code")
"""

# Import production-ready functions by default
try:
    from .production_client import ask as prod_ask, ask_concise as prod_ask_concise
    # Use production client for better reliability
    ask = prod_ask
    ask_concise = prod_ask_concise
except ImportError:
    # Fallback to full client
    from .client import ask, ask_concise

from .client import LLMClient, ask_json
from .config import get_config, update_config, apply_preset, COST_PRESETS

# Version info
__version__ = "1.0.0"
__author__ = "Claude Code Hooks"

# Default exports for easy importing
__all__ = [
    # Main client
    "LLMClient",
    
    # Convenience functions
    "ask",
    "ask_concise", 
    "ask_json",
    
    # Configuration
    "get_config",
    "update_config",
    "apply_preset",
    "COST_PRESETS"
]

# Package-level configuration
DEFAULT_MODEL = "claude-3-5-haiku-20241022"
PACKAGE_INFO = {
    "name": "llms",
    "version": __version__,
    "description": "Cost-efficient LLM utilities for Claude Code hooks",
    "default_model": DEFAULT_MODEL,
    "features": [
        "Claude 3.5 Haiku by default (cost-efficient)",
        "Automatic model fallbacks (Haiku → Sonnet → Manual)",
        "Response caching with TTL",
        "Token usage tracking",
        "Simple API: ask(), ask_concise(), ask_json()",
        "Context-aware prompting with file support",
        "Comprehensive error handling and logging"
    ]
}

def get_package_info():
    """Get package information and capabilities."""
    return PACKAGE_INFO

def quick_start_guide():
    """Print quick start guide for new users."""
    guide = """
🚀 LLM Utilities Quick Start Guide

1. Basic Usage:
   from utils.llms import ask
   response = ask("Your question here")

2. Cost-Efficient Queries:
   from utils.llms import ask_concise
   answer = ask_concise("Brief answer needed")

3. Structured Responses:
   from utils.llms import ask_json
   data = ask_json("Return user info as JSON")

4. Full Client Features:
   from utils.llms import LLMClient
   llm = LLMClient()
   response = llm.ask_with_context("Question", ["file1.py", "file2.js"])

5. Configuration:
   from utils.llms import update_config, apply_preset
   update_config(default_model="claude-3-5-sonnet-20241022")
   apply_preset("ultra_efficient")

Cost Optimization:
- Default: Claude 3.5 Haiku (most cost-efficient)
- Fallbacks: Haiku → Sonnet → Manual responses
- Caching: Automatic response caching (60min TTL)
- Monitoring: Optional token usage tracking

Example Integration in Hooks:
```python
from utils.llms import ask_concise

def your_hook(payload):
    error_summary = ask_concise(f"Summarize this error: {error_msg}")
    return f"Error: {error_summary}"
```
"""
    print(guide)

# Auto-import check
def _check_claude_availability():
    """Check if Claude executable is available."""
    try:
        import subprocess
        result = subprocess.run(["claude", "--version"], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

# Package initialization
if __name__ == "__main__":
    quick_start_guide()
else:
    # Silent availability check on import
    _claude_available = _check_claude_availability()
    if not _claude_available:
        import warnings
        warnings.warn(
            "Claude executable not found. LLM features may not work. "
            "Install Claude Code CLI: https://claude.ai/code",
            ImportWarning
        )