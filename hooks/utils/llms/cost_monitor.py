#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Cost Monitoring and Token Tracking for LLM Utilities
Tracks usage, estimates costs, and provides budget management for Claude 3.5 Haiku
"""

import json
import datetime
import pathlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class TokenUsage:
    """Token usage tracking for a single LLM call."""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    prompt_hash: str
    success: bool

@dataclass
class UsageStats:
    """Daily usage statistics."""
    date: str
    total_calls: int
    successful_calls: int
    total_tokens: int
    total_cost: float
    models_used: Dict[str, int]
    cache_hits: int
    cache_misses: int

class CostMonitor:
    """
    Token usage tracking and cost monitoring for LLM operations.
    
    Features:
    - Token estimation and actual usage tracking
    - Cost calculation based on model pricing
    - Daily/weekly/monthly usage summaries
    - Budget alerts and warnings
    - Cache hit/miss tracking for optimization
    """
    
    # Model pricing (tokens per $1, approximate)
    MODEL_PRICING = {
        "claude-3-5-haiku-20241022": {
            "input_tokens_per_dollar": 4000,  # Very cost-efficient
            "output_tokens_per_dollar": 2000,
            "cost_tier": "ultra_low"
        },
        "claude-3-5-sonnet-20241022": {
            "input_tokens_per_dollar": 400,   # Higher cost
            "output_tokens_per_dollar": 200,
            "cost_tier": "medium"
        }
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = pathlib.Path(data_dir or "C:/Users/NATH/.claude/hooks/utils/llms/usage_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.usage_file = self.data_dir / "token_usage.jsonl"
        self.stats_file = self.data_dir / "daily_stats.json"
        self.config_file = self.data_dir / "monitor_config.json"
        
        self._load_config()
    
    def _load_config(self):
        """Load monitoring configuration."""
        default_config = {
            "daily_budget_tokens": None,
            "daily_budget_cost": None,
            "warning_threshold": 0.8,
            "alert_threshold": 0.95,
            "track_cache_performance": True,
            "detailed_logging": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
            except:
                pass
        
        self.config = default_config
    
    def estimate_tokens(self, prompt: str, model: str = "claude-3-5-haiku-20241022") -> Dict[str, int]:
        """
        Estimate token usage for a prompt before making the API call.
        Uses simple heuristics for cost planning.
        """
        # Simple token estimation (rough approximation)
        # Real tokenization would require Claude's specific tokenizer
        
        # Estimate input tokens (prompt)
        # Average: ~4 characters per token for English text
        prompt_tokens = max(1, len(prompt) // 4)
        
        # Estimate completion tokens based on prompt type and model
        completion_multiplier = self._get_completion_multiplier(prompt, model)
        estimated_completion = int(prompt_tokens * completion_multiplier)
        
        total_tokens = prompt_tokens + estimated_completion
        
        return {
            "prompt_tokens": prompt_tokens,
            "estimated_completion_tokens": estimated_completion,
            "estimated_total_tokens": total_tokens,
            "model": model
        }
    
    def _get_completion_multiplier(self, prompt: str, model: str) -> float:
        """Estimate completion length based on prompt characteristics."""
        prompt_lower = prompt.lower()
        
        # Different types of prompts have different completion ratios
        if any(word in prompt_lower for word in ["summarize", "brief", "concise", "short"]):
            return 0.3  # Short responses
        elif any(word in prompt_lower for word in ["explain", "describe", "analyze"]):
            return 0.8  # Medium responses
        elif any(word in prompt_lower for word in ["generate", "create", "write", "code"]):
            return 1.2  # Longer responses
        elif "json" in prompt_lower or "list" in prompt_lower:
            return 0.5  # Structured responses
        else:
            return 0.6  # Default ratio
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Calculate estimated cost for token usage."""
        pricing = self.MODEL_PRICING.get(model)
        if not pricing:
            # Fallback to sonnet pricing (conservative estimate)
            pricing = self.MODEL_PRICING["claude-3-5-sonnet-20241022"]
        
        input_cost = prompt_tokens / pricing["input_tokens_per_dollar"]
        output_cost = completion_tokens / pricing["output_tokens_per_dollar"]
        
        return input_cost + output_cost
    
    def record_usage(self, prompt: str, response: str, model: str, 
                    success: bool, cache_hit: bool = False) -> TokenUsage:
        """Record actual token usage after an LLM call."""
        
        # Estimate actual token usage
        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = max(1, len(response) // 4) if response else 0
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        estimated_cost = self.calculate_cost(prompt_tokens, completion_tokens, model)
        
        # Create usage record
        usage = TokenUsage(
            timestamp=datetime.datetime.now().isoformat(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            prompt_hash=str(hash(prompt[:100])),
            success=success
        )
        
        # Save to file
        self._save_usage_record(usage, cache_hit)
        
        # Update daily stats
        self._update_daily_stats(usage, cache_hit)
        
        # Check budget warnings
        self._check_budget_warnings()
        
        return usage
    
    def _save_usage_record(self, usage: TokenUsage, cache_hit: bool):
        """Save usage record to JSONL file."""
        if not self.config.get("detailed_logging", True):
            return
        
        try:
            record = asdict(usage)
            record["cache_hit"] = cache_hit
            
            with open(self.usage_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except:
            pass  # Fail silently on logging errors
    
    def _update_daily_stats(self, usage: TokenUsage, cache_hit: bool):
        """Update daily statistics."""
        today = datetime.date.today().isoformat()
        
        # Load existing stats
        daily_stats = {}
        if self.stats_file.exists():
            try:
                with open(self.stats_file) as f:
                    daily_stats = json.load(f)
            except:
                pass
        
        # Initialize today's stats if needed
        if today not in daily_stats:
            daily_stats[today] = {
                "date": today,
                "total_calls": 0,
                "successful_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "models_used": {},
                "cache_hits": 0,
                "cache_misses": 0
            }
        
        stats = daily_stats[today]
        
        # Update stats
        stats["total_calls"] += 1
        if usage.success:
            stats["successful_calls"] += 1
            stats["total_tokens"] += usage.total_tokens
            stats["total_cost"] += usage.estimated_cost
        
        # Track model usage
        if usage.model not in stats["models_used"]:
            stats["models_used"][usage.model] = 0
        stats["models_used"][usage.model] += 1
        
        # Track cache performance
        if cache_hit:
            stats["cache_hits"] += 1
        else:
            stats["cache_misses"] += 1
        
        # Save updated stats
        try:
            with open(self.stats_file, "w") as f:
                json.dump(daily_stats, f, indent=2)
        except:
            pass
    
    def _check_budget_warnings(self):
        """Check if usage is approaching budget limits."""
        if not (self.config.get("daily_budget_tokens") or self.config.get("daily_budget_cost")):
            return
        
        today_stats = self.get_daily_stats()
        if not today_stats:
            return
        
        # Check token budget
        if self.config.get("daily_budget_tokens"):
            token_usage_ratio = today_stats.total_tokens / self.config["daily_budget_tokens"]
            if token_usage_ratio >= self.config.get("alert_threshold", 0.95):
                self._log_warning(f"🚨 Daily token budget 95% exceeded: {today_stats.total_tokens}/{self.config['daily_budget_tokens']}")
            elif token_usage_ratio >= self.config.get("warning_threshold", 0.8):
                self._log_warning(f"⚠️ Daily token budget 80% used: {today_stats.total_tokens}/{self.config['daily_budget_tokens']}")
        
        # Check cost budget
        if self.config.get("daily_budget_cost"):
            cost_usage_ratio = today_stats.total_cost / self.config["daily_budget_cost"]
            if cost_usage_ratio >= self.config.get("alert_threshold", 0.95):
                self._log_warning(f"🚨 Daily cost budget 95% exceeded: ${today_stats.total_cost:.4f}/${self.config['daily_budget_cost']}")
            elif cost_usage_ratio >= self.config.get("warning_threshold", 0.8):
                self._log_warning(f"⚠️ Daily cost budget 80% used: ${today_stats.total_cost:.4f}/${self.config['daily_budget_cost']}")
    
    def get_daily_stats(self, date: Optional[str] = None) -> Optional[UsageStats]:
        """Get usage statistics for a specific date."""
        target_date = date or datetime.date.today().isoformat()
        
        if not self.stats_file.exists():
            return None
        
        try:
            with open(self.stats_file) as f:
                daily_stats = json.load(f)
            
            if target_date in daily_stats:
                stats_data = daily_stats[target_date]
                return UsageStats(**stats_data)
        except:
            pass
        
        return None
    
    def get_usage_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get usage summary for the last N days."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        total_calls = 0
        total_tokens = 0
        total_cost = 0.0
        model_usage = {}
        daily_breakdown = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            daily_stats = self.get_daily_stats(date_str)
            
            if daily_stats:
                total_calls += daily_stats.total_calls
                total_tokens += daily_stats.total_tokens
                total_cost += daily_stats.total_cost
                
                for model, count in daily_stats.models_used.items():
                    model_usage[model] = model_usage.get(model, 0) + count
                
                daily_breakdown.append({
                    "date": date_str,
                    "calls": daily_stats.total_calls,
                    "tokens": daily_stats.total_tokens,
                    "cost": daily_stats.total_cost
                })
            else:
                daily_breakdown.append({
                    "date": date_str,
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                })
            
            current_date += datetime.timedelta(days=1)
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_daily_calls": total_calls / days,
            "avg_daily_tokens": total_tokens / days,
            "avg_daily_cost": total_cost / days,
            "model_usage": model_usage,
            "daily_breakdown": daily_breakdown
        }
    
    def set_budget(self, daily_tokens: Optional[int] = None, 
                  daily_cost: Optional[float] = None):
        """Set daily budget limits."""
        if daily_tokens:
            self.config["daily_budget_tokens"] = daily_tokens
        if daily_cost:
            self.config["daily_budget_cost"] = daily_cost
        
        # Save config
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def _log_warning(self, message: str):
        """Log budget warning."""
        try:
            debug_log = pathlib.Path("C:/Users/NATH/.claude/hooks/debug.log")
            timestamp = datetime.datetime.now().isoformat()
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - CostMonitor: {message}\n")
        except:
            pass

# Global cost monitor instance
_cost_monitor = None

def get_cost_monitor() -> CostMonitor:
    """Get global cost monitor instance."""
    global _cost_monitor
    if _cost_monitor is None:
        _cost_monitor = CostMonitor()
    return _cost_monitor

def estimate_cost(prompt: str, model: str = "claude-3-5-haiku-20241022") -> Dict[str, Any]:
    """Quick function to estimate cost for a prompt."""
    monitor = get_cost_monitor()
    token_estimate = monitor.estimate_tokens(prompt, model)
    cost_estimate = monitor.calculate_cost(
        token_estimate["prompt_tokens"],
        token_estimate["estimated_completion_tokens"],
        model
    )
    
    return {
        **token_estimate,
        "estimated_cost": cost_estimate,
        "cost_breakdown": {
            "input_cost": monitor.calculate_cost(token_estimate["prompt_tokens"], 0, model),
            "output_cost": monitor.calculate_cost(0, token_estimate["estimated_completion_tokens"], model)
        }
    }

def get_usage_report(days: int = 7) -> Dict[str, Any]:
    """Get a formatted usage report."""
    monitor = get_cost_monitor()
    return monitor.get_usage_summary(days)

if __name__ == "__main__":
    # Test cost monitoring
    print("💰 Testing Cost Monitor...")
    
    monitor = CostMonitor()
    
    # Test estimation
    estimate = monitor.estimate_tokens("Generate a commit message for auth.js", "claude-3-5-haiku-20241022")
    print(f"✅ Token estimate: {estimate}")
    
    # Test cost calculation
    cost = monitor.calculate_cost(100, 50, "claude-3-5-haiku-20241022")
    print(f"✅ Cost estimate: ${cost:.6f}")
    
    # Test usage summary
    summary = monitor.get_usage_summary(7)
    print(f"✅ Usage summary: {summary}")
    
    print("💰 Cost monitoring ready!")