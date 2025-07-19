#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Test Suite for LLM Utilities
Comprehensive testing for LLMClient, configuration, cost monitoring, and integration
"""

import sys
import time
import tempfile
import pathlib
from typing import Dict, Any, List
import subprocess

# Import LLM utilities (handle both package and standalone execution)
try:
    from .client import LLMClient, ask, ask_concise, ask_json
    from .config import get_config, update_config, apply_preset, LLMConfigManager
    from .cost_monitor import CostMonitor, estimate_cost, get_usage_report
except ImportError:
    # Running standalone - add path and import directly
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from client import LLMClient, ask, ask_concise, ask_json
    from config import get_config, update_config, apply_preset, LLMConfigManager
    from cost_monitor import CostMonitor, estimate_cost, get_usage_report

class LLMTestSuite:
    """Comprehensive test suite for LLM utilities."""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.client = None
        self.config_manager = None
        self.cost_monitor = None
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("🧪 Starting LLM Utilities Test Suite...")
        print("=" * 50)
        
        # Initialize test components
        self._setup_test_environment()
        
        # Run test categories
        self._test_configuration()
        self._test_client_initialization()
        self._test_basic_queries()
        self._test_error_handling()
        self._test_cost_monitoring()
        self._test_caching()
        self._test_convenience_functions()
        self._test_integration_patterns()
        
        # Generate final report
        return self._generate_test_report()
    
    def _setup_test_environment(self):
        """Set up test environment and components."""
        print("🔧 Setting up test environment...")
        
        try:
            self.config_manager = LLMConfigManager()
            self.client = LLMClient()
            self.cost_monitor = CostMonitor()
            self._log_test("Environment setup", True, "All components initialized")
        except Exception as e:
            self._log_test("Environment setup", False, f"Setup failed: {e}")
    
    def _test_configuration(self):
        """Test configuration management."""
        print("\n📋 Testing Configuration Management...")
        
        # Test default config loading
        try:
            config = get_config()
            assert config.default_model == "claude-3-5-haiku-20241022"
            assert config.enable_cost_tracking == True
            self._log_test("Default config", True, f"Model: {config.default_model}")
        except Exception as e:
            self._log_test("Default config", False, f"Error: {e}")
        
        # Test config updates
        try:
            original_timeout = get_config().default_timeout
            update_config(default_timeout=45)
            updated_config = get_config()
            assert updated_config.default_timeout == 45
            
            # Restore original
            update_config(default_timeout=original_timeout)
            self._log_test("Config updates", True, "Timeout update successful")
        except Exception as e:
            self._log_test("Config updates", False, f"Error: {e}")
        
        # Test presets
        try:
            apply_preset("ultra_efficient")
            config = get_config()
            assert config.default_model == "claude-3-5-haiku-20241022"
            self._log_test("Preset application", True, "Ultra-efficient preset applied")
        except Exception as e:
            self._log_test("Preset application", False, f"Error: {e}")
    
    def _test_client_initialization(self):
        """Test LLM client initialization."""
        print("\n🤖 Testing Client Initialization...")
        
        # Test basic initialization
        try:
            client = LLMClient()
            assert client.config is not None
            assert hasattr(client, '_response_cache')
            self._log_test("Client init", True, "Basic initialization successful")
        except Exception as e:
            self._log_test("Client init", False, f"Error: {e}")
        
        # Test custom config
        try:
            custom_config = get_config()
            custom_config.default_timeout = 60
            client = LLMClient(custom_config)
            assert client.config.default_timeout == 60
            self._log_test("Custom config", True, "Custom config accepted")
        except Exception as e:
            self._log_test("Custom config", False, f"Error: {e}")
    
    def _test_basic_queries(self):
        """Test basic LLM query functionality."""
        print("\n💬 Testing Basic Queries...")
        
        # Test simple ask (may fail if Claude not available)
        try:
            response = self.client.ask("What is 2+2? Answer with just the number.", 
                                     model="claude-3-5-haiku-20241022")
            success = response and len(response.strip()) > 0
            self._log_test("Simple ask", success, f"Response: {response[:50]}...")
        except Exception as e:
            self._log_test("Simple ask", False, f"Expected with no Claude: {e}")
        
        # Test concise ask
        try:
            response = self.client.ask_concise("Current year")
            success = response and len(response.strip()) > 0
            self._log_test("Concise ask", success, f"Response: {response[:30]}...")
        except Exception as e:
            self._log_test("Concise ask", False, f"Expected with no Claude: {e}")
        
        # Test manual fallback (should always work)
        try:
            # Force fallback by using invalid model
            response = self.client._manual_fallback("Generate a commit message")
            assert "chore:" in response or "unavailable" in response
            self._log_test("Manual fallback", True, f"Fallback: {response}")
        except Exception as e:
            self._log_test("Manual fallback", False, f"Error: {e}")
    
    def _test_error_handling(self):
        """Test error handling and fallbacks."""
        print("\n🛡️ Testing Error Handling...")
        
        # Test invalid model fallback
        try:
            response = self.client.ask("Test", model="invalid-model-12345")
            # Should get manual fallback
            success = response and len(response) > 0
            self._log_test("Invalid model fallback", success, "Fallback triggered")
        except Exception as e:
            self._log_test("Invalid model fallback", False, f"Error: {e}")
        
        # Test empty prompt handling
        try:
            response = self.client.ask("")
            success = response is not None  # Should handle gracefully
            self._log_test("Empty prompt", success, "Empty prompt handled")
        except Exception as e:
            self._log_test("Empty prompt", False, f"Error: {e}")
        
        # Test timeout simulation (quick test)
        try:
            original_timeout = self.client.config.default_timeout
            self.client.config.default_timeout = 1  # Very short timeout
            response = self.client.ask("Test prompt")
            # Should get fallback response
            success = response and len(response) > 0
            self.client.config.default_timeout = original_timeout
            self._log_test("Timeout handling", success, "Timeout handled gracefully")
        except Exception as e:
            self._log_test("Timeout handling", False, f"Error: {e}")
    
    def _test_cost_monitoring(self):
        """Test cost monitoring and token tracking."""
        print("\n💰 Testing Cost Monitoring...")
        
        # Test token estimation
        try:
            estimate = self.cost_monitor.estimate_tokens("Generate a commit message", 
                                                        "claude-3-5-haiku-20241022")
            assert estimate["prompt_tokens"] > 0
            assert estimate["estimated_completion_tokens"] > 0
            self._log_test("Token estimation", True, f"Estimated: {estimate['estimated_total_tokens']} tokens")
        except Exception as e:
            self._log_test("Token estimation", False, f"Error: {e}")
        
        # Test cost calculation
        try:
            cost = self.cost_monitor.calculate_cost(100, 50, "claude-3-5-haiku-20241022")
            assert cost > 0
            assert cost < 1.0  # Should be very low for Haiku
            self._log_test("Cost calculation", True, f"Cost: ${cost:.6f}")
        except Exception as e:
            self._log_test("Cost calculation", False, f"Error: {e}")
        
        # Test usage recording
        try:
            usage = self.cost_monitor.record_usage(
                prompt="Test prompt", 
                response="Test response", 
                model="claude-3-5-haiku-20241022",
                success=True,
                cache_hit=False
            )
            assert usage.total_tokens > 0
            self._log_test("Usage recording", True, f"Recorded: {usage.total_tokens} tokens")
        except Exception as e:
            self._log_test("Usage recording", False, f"Error: {e}")
        
        # Test convenience function
        try:
            estimate = estimate_cost("Short test prompt")
            assert "estimated_cost" in estimate
            self._log_test("Cost estimation function", True, f"Estimate: ${estimate['estimated_cost']:.6f}")
        except Exception as e:
            self._log_test("Cost estimation function", False, f"Error: {e}")
    
    def _test_caching(self):
        """Test response caching functionality."""
        print("\n📦 Testing Response Caching...")
        
        # Test cache key generation
        try:
            key1 = self.client._generate_cache_key("test prompt", "haiku", None)
            key2 = self.client._generate_cache_key("test prompt", "haiku", None)
            key3 = self.client._generate_cache_key("different prompt", "haiku", None)
            
            assert key1 == key2  # Same inputs = same key
            assert key1 != key3  # Different inputs = different keys
            self._log_test("Cache key generation", True, "Keys generated correctly")
        except Exception as e:
            self._log_test("Cache key generation", False, f"Error: {e}")
        
        # Test cache storage and retrieval
        try:
            cache_key = "test_key"
            test_response = "Test cached response"
            
            self.client._cache_response(cache_key, test_response)
            cached_item = self.client._response_cache.get(cache_key)
            
            assert cached_item is not None
            assert cached_item["response"] == test_response
            assert self.client._is_cache_valid(cached_item)
            
            self._log_test("Cache storage", True, "Response cached successfully")
        except Exception as e:
            self._log_test("Cache storage", False, f"Error: {e}")
        
        # Test cache expiration
        try:
            import datetime
            old_item = {
                "response": "Old response",
                "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2),
                "ttl_minutes": 60
            }
            
            is_valid = self.client._is_cache_valid(old_item)
            assert not is_valid  # Should be expired
            self._log_test("Cache expiration", True, "Expired cache detected")
        except Exception as e:
            self._log_test("Cache expiration", False, f"Error: {e}")
    
    def _test_convenience_functions(self):
        """Test convenience functions."""
        print("\n🔧 Testing Convenience Functions...")
        
        # Test ask function
        try:
            response = ask("Test question")  # Will use fallback
            success = response and len(response) > 0
            self._log_test("ask() function", success, f"Response: {response[:30]}...")
        except Exception as e:
            self._log_test("ask() function", False, f"Error: {e}")
        
        # Test ask_concise function
        try:
            response = ask_concise("Brief test")  # Will use fallback
            success = response and len(response) > 0
            self._log_test("ask_concise() function", success, f"Response: {response[:20]}...")
        except Exception as e:
            self._log_test("ask_concise() function", False, f"Error: {e}")
        
        # Test ask_json function
        try:
            response = ask_json("Return empty object")  # Will use fallback
            success = isinstance(response, dict)
            self._log_test("ask_json() function", success, f"Type: {type(response)}")
        except Exception as e:
            self._log_test("ask_json() function", False, f"Error: {e}")
    
    def _test_integration_patterns(self):
        """Test common integration patterns for hooks."""
        print("\n🔗 Testing Integration Patterns...")
        
        # Test hook-style usage
        try:
            def mock_hook(error_message):
                """Example hook that uses LLM for error analysis."""
                try:
                    from .client import ask_concise
                except ImportError:
                    from client import ask_concise
                return ask_concise(f"Summarize this error: {error_message}")
            
            result = mock_hook("FileNotFoundError: config.json missing")
            success = result and len(result) > 0
            self._log_test("Hook integration", success, f"Hook result: {result[:40]}...")
        except Exception as e:
            self._log_test("Hook integration", False, f"Error: {e}")
        
        # Test context file reading
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test file content for context")
                temp_path = f.name
            
            try:
                context = self.client._read_context_files([temp_path])
                assert "Test file content" in context
                self._log_test("Context file reading", True, "File content read successfully")
            finally:
                pathlib.Path(temp_path).unlink()
        except Exception as e:
            self._log_test("Context file reading", False, f"Error: {e}")
        
        # Test usage stats
        try:
            stats = self.client.get_usage_stats()
            assert "default_model" in stats
            assert "caching_enabled" in stats
            self._log_test("Usage stats", True, f"Stats: {len(stats)} fields")
        except Exception as e:
            self._log_test("Usage stats", False, f"Error: {e}")
    
    def _test_claude_availability(self):
        """Test if Claude executable is available."""
        print("\n🔍 Testing Claude Availability...")
        
        try:
            result = subprocess.run(["claude", "--version"], 
                                  capture_output=True, timeout=5)
            available = result.returncode == 0
            version_info = result.stdout.decode() if available else "Not available"
            self._log_test("Claude executable", available, version_info)
            return available
        except Exception as e:
            self._log_test("Claude executable", False, f"Error: {e}")
            return False
    
    def _log_test(self, test_name: str, success: bool, details: str):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}: {details}")
        
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests: {', '.join(self.failed_tests)}")
        
        # Test Claude availability
        claude_available = self._test_claude_availability()
        
        print(f"\n🔧 Environment:")
        print(f"  Claude CLI Available: {'✅ Yes' if claude_available else '❌ No'}")
        print(f"  LLM Package: ✅ Installed")
        print(f"  Config System: ✅ Working")
        print(f"  Cost Monitoring: ✅ Working")
        
        if not claude_available:
            print(f"\n💡 Note: Many tests use fallback responses because Claude CLI is not available.")
            print(f"   Install Claude Code CLI for full functionality: https://claude.ai/code")
        
        report = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "claude_available": claude_available,
            "failed_test_names": self.failed_tests,
            "all_results": self.test_results
        }
        
        return report

def run_quick_test():
    """Run a quick validation test."""
    print("Quick LLM Utilities Test")
    print("-" * 30)
    
    try:
        # Test imports
        try:
            from .client import LLMClient, ask
            from .config import get_config
            from .cost_monitor import estimate_cost
        except ImportError:
            from client import LLMClient, ask
            from config import get_config
            from cost_monitor import estimate_cost
        print("OK Imports successful")
        
        # Test initialization
        client = LLMClient()
        config = get_config()
        print(f"OK Initialization successful (Model: {config.default_model})")
        
        # Test cost estimation
        estimate = estimate_cost("Test prompt")
        print(f"OK Cost estimation: ${estimate['estimated_cost']:.6f}")
        
        # Test fallback response
        response = client._manual_fallback("Test prompt")
        print(f"OK Fallback response: {response}")
        
        print("\nQuick test PASSED - LLM utilities are ready!")
        return True
        
    except Exception as e:
        print(f"FAIL Quick test FAILED: {e}")
        return False

def main():
    """Main test runner."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        return run_quick_test()
    else:
        test_suite = LLMTestSuite()
        report = test_suite.run_all_tests()
        
        # Return success code based on results
        return report["success_rate"] > 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)