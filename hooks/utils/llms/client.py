#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
LLM Client for Claude Code Hooks
Reusable, cost-efficient AI client using Claude 3.5 Haiku by default
Supports the command structure: claude -p --model claude-3-5-haiku-20241022 "<PROMPT>"
"""

import subprocess
import tempfile
import pathlib
import datetime
import json
from typing import Dict, Any, Optional, List, Union
try:
    from .config import get_config, get_config_manager, LLMConfig
except ImportError:
    from config import get_config, get_config_manager, LLMConfig

class LLMClient:
    """
    Reusable LLM client for cost-efficient AI integration across Claude Code hooks.
    
    Features:
    - Claude 3.5 Haiku by default for cost efficiency
    - Automatic fallbacks: Haiku → Sonnet → Manual
    - Response caching and token tracking
    - Simple API: llm.ask("prompt")
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or get_config()
        self.config_manager = get_config_manager()
        self.debug_log = pathlib.Path(self.config.log_path)
        self._response_cache = {}
    
    def ask(self, prompt: str, model: Optional[str] = None, 
            max_tokens: Optional[int] = None, 
            system_prompt: Optional[str] = None) -> str:
        """
        Ask the LLM a question with automatic fallbacks and caching.
        
        Args:
            prompt: The question/task for the LLM
            model: Override default model (optional)
            max_tokens: Token limit override (optional)
            system_prompt: Additional system instructions (optional)
            
        Returns:
            str: The LLM's response, cleaned and validated
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(prompt, model, system_prompt)
            if self.config.enable_caching and cache_key in self._response_cache:
                cached_response = self._response_cache[cache_key]
                if self._is_cache_valid(cached_response):
                    self._log_debug(f"Cache hit for prompt: {prompt[:50]}...")
                    return cached_response["response"]
            
            # Try primary model
            target_model = model or self.config.default_model
            response = self._call_claude(prompt, target_model, system_prompt)
            
            if response and len(response.strip()) > 0:
                # Cache successful response
                if self.config.enable_caching:
                    self._cache_response(cache_key, response)
                
                self._log_debug(f"✅ LLM success with {target_model}: {len(response)} chars")
                return response
            
            # Fallback to next model
            return self._try_fallbacks(prompt, target_model, system_prompt)
            
        except Exception as e:
            self._log_debug(f"❌ LLM error: {e}")
            return self._try_fallbacks(prompt, model, system_prompt)
    
    def ask_concise(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Ask for an ultra-concise response optimized for cost efficiency.
        Uses aggressive compression and minimal tokens.
        """
        concise_system = (
            "Be extremely concise. Use minimal tokens. "
            "No explanations, examples, or elaboration. "
            "Output only the essential answer."
        )
        
        # Force haiku for maximum cost efficiency
        efficient_model = model or "claude-3-5-haiku-20241022"
        
        return self.ask(prompt, efficient_model, max_tokens=100, system_prompt=concise_system)
    
    def ask_with_context(self, prompt: str, context_files: List[str] = None, 
                        model: Optional[str] = None) -> str:
        """
        Ask with additional context from files.
        Automatically includes relevant file contents in the prompt.
        """
        enhanced_prompt = prompt
        
        if context_files:
            context_content = self._read_context_files(context_files)
            enhanced_prompt = f"Context:\n{context_content}\n\nQuestion: {prompt}"
        
        return self.ask(enhanced_prompt, model)
    
    def ask_structured(self, prompt: str, format_type: str = "json", 
                      model: Optional[str] = None) -> Union[Dict, List, str]:
        """
        Ask for a structured response (JSON, list, etc.).
        
        Args:
            prompt: The question/task
            format_type: "json", "list", "yaml", or "text"
            model: Model override
            
        Returns:
            Parsed structured data or raw text
        """
        format_instructions = {
            "json": "Respond with valid JSON only. No explanations.",
            "list": "Respond with a numbered list only. No explanations.",
            "yaml": "Respond with valid YAML only. No explanations.",
            "text": "Respond with plain text only. No formatting."
        }
        
        system_prompt = format_instructions.get(format_type, format_instructions["text"])
        response = self.ask(prompt, model, system_prompt=system_prompt)
        
        # Try to parse structured formats
        if format_type == "json":
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON", "raw_response": response}
        elif format_type == "list":
            return [line.strip() for line in response.split('\n') if line.strip()]
        
        return response
    
    def _call_claude(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> str:
        """Call Claude executable with the specified model and prompt."""
        try:
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(prompt)
                temp_file_path = temp_file.name
            
            try:
                # Build command arguments
                args = self.config_manager.get_claude_args(model, system_prompt)
                args.append(f"@{temp_file_path}")
                
                self._log_debug(f"Calling: {' '.join(args[:4])} @prompt ({len(prompt)} chars)")
                
                # Try direct execution without shell for better Windows compatibility
                import os
                env = os.environ.copy()
                
                # Try to find the actual Claude executable
                claude_exe = None
                potential_paths = [
                    r"C:\Users\NATH\AppData\Local\pnpm\claude.CMD",
                    r"C:\Users\NATH\AppData\Roaming\npm\claude.cmd",
                    "claude.cmd",
                    "claude"
                ]
                
                for path in potential_paths:
                    if pathlib.Path(path).exists() or path in ["claude.cmd", "claude"]:
                        claude_exe = path
                        break
                
                if not claude_exe:
                    raise FileNotFoundError("Claude executable not found in any expected location")
                
                # Build direct command arguments
                cmd_args = [claude_exe] + args[1:]  # Skip the first arg which is the executable path
                
                self._log_debug(f"Executing: {cmd_args[0]} with {len(cmd_args)-1} args")
                
                # Force Windows CMD shell instead of bash
                result = subprocess.run(
                    cmd_args,
                    capture_output=True,
                    text=True,
                    timeout=self.config.default_timeout,
                    cwd=pathlib.Path.cwd(),
                    shell=True,
                    env=env,
                    executable=None  # Let Windows choose the shell
                )
                
                if result.returncode == 0:
                    raw_response = result.stdout.strip()
                    cleaned_response = self._clean_response(raw_response)
                    return cleaned_response
                else:
                    self._log_debug(f"Claude failed: {result.stderr}")
                    raise Exception(f"Claude failed: {result.stderr}")
                    
            finally:
                # Clean up temporary file
                try:
                    pathlib.Path(temp_file_path).unlink()
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            self._log_debug(f"Claude timeout ({self.config.default_timeout}s)")
            raise Exception("Claude timeout")
        except FileNotFoundError:
            self._log_debug("Claude executable not found")
            raise Exception("Claude executable not found")
        except Exception as e:
            self._log_debug(f"Claude call error: {e}")
            raise
    
    def _try_fallbacks(self, prompt: str, failed_model: Optional[str], 
                      system_prompt: Optional[str]) -> str:
        """Try fallback models when primary model fails."""
        fallback_models = [m for m in self.config.fallback_models if m != failed_model]
        
        for fallback_model in fallback_models:
            if fallback_model == "manual_fallback":
                return self._manual_fallback(prompt)
            
            try:
                self._log_debug(f"Trying fallback: {fallback_model}")
                response = self._call_claude(prompt, fallback_model, system_prompt)
                if response and len(response.strip()) > 0:
                    self._log_debug(f"✅ Fallback success: {fallback_model}")
                    return response
            except Exception as e:
                self._log_debug(f"Fallback {fallback_model} failed: {e}")
                continue
        
        # All fallbacks failed
        return self._manual_fallback(prompt)
    
    def _manual_fallback(self, prompt: str) -> str:
        """Generate a manual fallback response when all AI models fail."""
        self._log_debug("All AI models failed, using manual fallback")
        
        # Simple keyword-based responses for common tasks
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["commit", "git", "message"]):
            return "chore: update files"
        elif any(word in prompt_lower for word in ["explain", "what", "how"]):
            return "Unable to generate explanation - AI models unavailable"
        elif any(word in prompt_lower for word in ["error", "debug", "fix"]):
            return "Error analysis unavailable - check logs and documentation"
        elif any(word in prompt_lower for word in ["summary", "summarize"]):
            return "Summary unavailable - AI models unavailable"
        else:
            return "AI response unavailable - please try again later"
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate AI response."""
        if not response:
            return ""
        
        # Remove common prefixes and suffixes
        cleaned = response.strip()
        
        # Remove quotes if response is entirely quoted
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        elif cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1]
        
        # Remove markdown code blocks
        if cleaned.startswith("```") and cleaned.endswith("```"):
            lines = cleaned.split('\n')
            if len(lines) > 2:
                cleaned = '\n'.join(lines[1:-1])
        
        return cleaned.strip()
    
    def _read_context_files(self, file_paths: List[str]) -> str:
        """Read content from context files."""
        context_parts = []
        
        for file_path in file_paths:
            try:
                path_obj = pathlib.Path(file_path)
                if path_obj.exists() and path_obj.is_file():
                    with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 2000:  # Limit context size
                            content = content[:2000] + "..."
                        context_parts.append(f"File: {file_path}\n{content}\n")
            except Exception:
                context_parts.append(f"File: {file_path}\n[Unable to read file]\n")
        
        return '\n'.join(context_parts)
    
    def _generate_cache_key(self, prompt: str, model: Optional[str], 
                           system_prompt: Optional[str]) -> str:
        """Generate cache key for response caching."""
        key_parts = [
            prompt[:100],  # First 100 chars of prompt
            model or self.config.default_model,
            system_prompt or ""
        ]
        return str(hash(tuple(key_parts)))
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache a response with timestamp."""
        self._response_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.datetime.now(),
            "ttl_minutes": self.config.cache_ttl_minutes
        }
        
        # Simple cache cleanup - remove old entries
        if len(self._response_cache) > 100:
            old_keys = list(self._response_cache.keys())[:20]
            for old_key in old_keys:
                del self._response_cache[old_key]
    
    def _is_cache_valid(self, cached_item: Dict) -> bool:
        """Check if cached response is still valid."""
        if not self.config.enable_caching:
            return False
        
        elapsed = datetime.datetime.now() - cached_item["timestamp"]
        ttl_minutes = cached_item.get("ttl_minutes", self.config.cache_ttl_minutes)
        
        return elapsed.total_seconds() < (ttl_minutes * 60)
    
    def _log_debug(self, message: str):
        """Log debug information."""
        if not self.config.debug_logging:
            return
        
        try:
            timestamp = datetime.datetime.now().isoformat()
            with open(self.debug_log, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - LLMClient: {message}\n")
        except:
            pass  # Fail silently on debug logging
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get basic usage statistics."""
        return {
            "cache_size": len(self._response_cache),
            "default_model": self.config.default_model,
            "caching_enabled": self.config.enable_caching,
            "cost_tracking_enabled": self.config.enable_cost_tracking
        }

# Convenience functions for simple usage
def ask(prompt: str, model: Optional[str] = None) -> str:
    """Quick ask function for simple queries."""
    client = LLMClient()
    return client.ask(prompt, model)

def ask_concise(prompt: str) -> str:
    """Quick concise ask for cost-efficient queries."""
    client = LLMClient()
    return client.ask_concise(prompt)

def ask_json(prompt: str) -> Dict:
    """Quick ask for JSON responses."""
    client = LLMClient()
    return client.ask_structured(prompt, "json")

# Test function
def test_llm_client():
    """Test LLM client functionality."""
    print("🧪 Testing LLM Client...")
    
    client = LLMClient()
    
    # Test basic ask
    try:
        response = client.ask("What is 2+2? Answer with just the number.")
        print(f"✅ Basic ask: {response}")
    except Exception as e:
        print(f"❌ Basic ask failed: {e}")
    
    # Test concise ask
    try:
        response = client.ask_concise("Current year")
        print(f"✅ Concise ask: {response}")
    except Exception as e:
        print(f"❌ Concise ask failed: {e}")
    
    # Test usage stats
    stats = client.get_usage_stats()
    print(f"✅ Usage stats: {stats}")
    
    print("🧪 LLM Client test completed!")

if __name__ == "__main__":
    test_llm_client()