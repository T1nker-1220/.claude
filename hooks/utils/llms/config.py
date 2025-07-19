#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
LLM Configuration Management for Claude Code Hooks
Centralized configuration for cost-efficient AI integration using Claude 3.5 Haiku
"""

import os
import json
import pathlib
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class LLMConfig:
    """Configuration for LLM client with cost-efficiency defaults."""
    
    # Model Configuration
    default_model: str = "claude-3-5-haiku-20241022"
    fallback_models: list = None
    
    # Cost & Performance
    default_timeout: int = 30
    max_tokens: Optional[int] = None
    temperature: float = 0.1
    
    # Claude Executable Settings
    claude_executable: str = "C:\\Users\\NATH\\AppData\\Local\\pnpm\\claude.CMD"  # Full path for reliability
    output_format: str = "text"
    print_mode: bool = True
    
    # Cost Monitoring
    enable_cost_tracking: bool = True
    daily_token_budget: Optional[int] = None
    warn_at_percentage: float = 0.8
    
    # Caching
    enable_caching: bool = True
    cache_ttl_minutes: int = 60
    
    # Logging
    debug_logging: bool = True
    log_path: str = "C:/Users/NATH/.claude/hooks/debug.log"
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.fallback_models is None:
            self.fallback_models = [
                "claude-3-5-haiku-20241022",
                "claude-3-5-sonnet-20241022", 
                "manual_fallback"
            ]

class LLMConfigManager:
    """Manages LLM configuration with file persistence and environment overrides."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = pathlib.Path(config_path or "C:/Users/NATH/.claude/hooks/utils/llms/llm_config.json")
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = None
    
    def load_config(self) -> LLMConfig:
        """Load configuration from file, environment, and defaults."""
        if self._config is not None:
            return self._config
            
        # Start with defaults
        config_dict = asdict(LLMConfig())
        
        # Override with file config if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config_dict.update(file_config)
            except Exception:
                pass  # Use defaults if file read fails
        
        # Override with environment variables
        env_overrides = self._get_env_overrides()
        config_dict.update(env_overrides)
        
        # Create config object
        self._config = LLMConfig(**config_dict)
        return self._config
    
    def save_config(self, config: LLMConfig) -> bool:
        """Save configuration to file."""
        try:
            config_dict = asdict(config)
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            self._config = config
            return True
        except Exception:
            return False
    
    def _get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables."""
        overrides = {}
        
        # Model settings
        if os.getenv("CLAUDE_LLM_MODEL"):
            overrides["default_model"] = os.getenv("CLAUDE_LLM_MODEL")
        
        if os.getenv("CLAUDE_LLM_TIMEOUT"):
            try:
                overrides["default_timeout"] = int(os.getenv("CLAUDE_LLM_TIMEOUT"))
            except ValueError:
                pass
        
        # Cost monitoring
        if os.getenv("CLAUDE_LLM_BUDGET"):
            try:
                overrides["daily_token_budget"] = int(os.getenv("CLAUDE_LLM_BUDGET"))
            except ValueError:
                pass
        
        # Executable path
        if os.getenv("CLAUDE_EXECUTABLE"):
            overrides["claude_executable"] = os.getenv("CLAUDE_EXECUTABLE")
        
        # Debug mode
        if os.getenv("CLAUDE_LLM_DEBUG"):
            overrides["debug_logging"] = os.getenv("CLAUDE_LLM_DEBUG").lower() in ("true", "1", "yes")
        
        return overrides
    
    def get_model_config(self, model_override: Optional[str] = None) -> Dict[str, str]:
        """Get model configuration for claude command."""
        config = self.load_config()
        model = model_override or config.default_model
        
        return {
            "model": model,
            "timeout": str(config.default_timeout),
            "executable": config.claude_executable,
            "output_format": config.output_format
        }
    
    def get_claude_args(self, model_override: Optional[str] = None, 
                       custom_system_prompt: Optional[str] = None) -> list:
        """Generate claude command arguments."""
        config = self.load_config()
        model = model_override or config.default_model
        
        args = [
            config.claude_executable,
            "--model", model,
            "--output-format", config.output_format
        ]
        
        if config.print_mode:
            args.append("--print")
        
        if custom_system_prompt:
            args.extend(["--append-system-prompt", custom_system_prompt])
        
        # Add temperature if not default
        if config.temperature != 0.1:
            args.extend(["--temperature", str(config.temperature)])
        
        return args

# Global configuration instance
_config_manager = None

def get_config_manager() -> LLMConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = LLMConfigManager()
    return _config_manager

def get_config() -> LLMConfig:
    """Get current LLM configuration."""
    return get_config_manager().load_config()

def update_config(**kwargs) -> bool:
    """Update configuration with new values."""
    manager = get_config_manager()
    config = manager.load_config()
    
    # Update only provided fields
    config_dict = asdict(config)
    config_dict.update(kwargs)
    
    new_config = LLMConfig(**config_dict)
    return manager.save_config(new_config)

# Cost-efficient presets
COST_PRESETS = {
    "ultra_efficient": {
        "default_model": "claude-3-5-haiku-20241022",
        "temperature": 0.0,
        "default_timeout": 15,
        "enable_caching": True
    },
    "balanced": {
        "default_model": "claude-3-5-haiku-20241022", 
        "temperature": 0.1,
        "default_timeout": 30,
        "enable_caching": True
    },
    "quality_focused": {
        "default_model": "claude-3-5-sonnet-20241022",
        "temperature": 0.2,
        "default_timeout": 45,
        "enable_caching": False
    }
}

def apply_preset(preset_name: str) -> bool:
    """Apply a cost/quality preset configuration."""
    if preset_name not in COST_PRESETS:
        return False
    
    preset_config = COST_PRESETS[preset_name]
    return update_config(**preset_config)

if __name__ == "__main__":
    # Test configuration system
    print("🔧 Testing LLM Configuration System...")
    
    manager = get_config_manager()
    config = manager.load_config()
    
    print(f"✅ Default Model: {config.default_model}")
    print(f"✅ Fallback Models: {config.fallback_models}")
    print(f"✅ Cost Tracking: {config.enable_cost_tracking}")
    print(f"✅ Claude Args: {manager.get_claude_args()}")
    
    print("🔧 Configuration system ready!")