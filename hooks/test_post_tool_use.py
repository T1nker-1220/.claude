#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pytest>=7.0.0",
# ]
# ///

import pytest
import json
from unittest.mock import patch, mock_open
from post_tool_use import check_task_chaining, log_debug


class TestTaskChaining:
    """Comprehensive unit tests for the check_task_chaining function."""
    
    def test_ignores_non_file_tools(self):
        """Should not prompt for tools other than Write/Edit/MultiEdit."""
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "test.py"},
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    def test_ignores_failed_operations(self):
        """Should not prompt when tool operation failed."""
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "def test_function():\n    pass"},
            "tool_response": {"success": False}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    def test_detects_python_function_in_write_tool(self):
        """Should detect Python function definition in Write tool content."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": "def calculate_sum(a, b):\n    return a + b\n"
            },
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is True
        assert "unit test" in result["reason"]
    
    def test_detects_python_class_in_edit_tool(self):
        """Should detect Python class definition in Edit tool new_string."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "old_string": "# placeholder",
                "new_string": "class Calculator:\n    def add(self, a, b):\n        return a + b"
            },
            "tool_response": {"filePath": "calculator.py"}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is True
        assert "unit test" in result["reason"]
    
    def test_detects_javascript_function(self):
        """Should detect JavaScript function definition."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": "function calculateTotal(items) {\n    return items.reduce((sum, item) => sum + item.price, 0);\n}"
            },
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is True
    
    def test_detects_const_arrow_function(self):
        """Should detect const arrow function definition."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "old_string": "// TODO",
                "new_string": "const processData = (data) => {\n    return data.map(item => item.value);\n};"
            },
            "tool_response": {"filePath": "utils.js"}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is True
    
    def test_ignores_variable_assignments(self):
        """Should not trigger for simple variable assignments."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": "const config = {\n    api_url: 'https://api.example.com',\n    timeout: 5000\n};"
            },
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    def test_ignores_comments_and_strings(self):
        """Should not trigger for function names in comments or strings."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": "# This explains the def keyword\nprint('def is used to define functions')"
            },
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    def test_handles_multiline_function_definition(self):
        """Should detect function definitions spanning multiple lines."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": """
def complex_calculation(
    param1: int,
    param2: str,
    param3: bool = False
) -> dict:
    # Complex logic here
    return {"result": param1 * 2}
"""
            },
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is True
    
    def test_handles_missing_content(self):
        """Should handle gracefully when content is missing."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {},
            "tool_response": {"success": True}
        }
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    def test_handles_malformed_payload(self):
        """Should handle gracefully when payload is malformed."""
        payload = {}
        
        result = check_task_chaining(payload)
        assert result["should_prompt"] is False
    
    @patch('post_tool_use.log_debug')
    def test_logs_detection(self, mock_log_debug):
        """Should log when function/class is detected."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "content": "def my_function():\n    pass"
            },
            "tool_response": {"success": True}
        }
        
        check_task_chaining(payload)
        mock_log_debug.assert_called_once()
        assert "Detected new function/class" in mock_log_debug.call_args[0][0]


class TestLogDebug:
    """Tests for the log_debug function."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_logs_message_with_timestamp(self, mock_exists, mock_file):
        """Should log message with timestamp to debug log."""
        test_message = "Test log message"
        
        log_debug(test_message)
        
        mock_file.assert_called_once()
        written_content = mock_file().write.call_args[0][0]
        assert "POST_TOOL_USE_TASK_CHAIN" in written_content
        assert test_message in written_content
        assert "T" in written_content  # ISO timestamp contains T
    
    def test_handles_file_write_error_gracefully(self):
        """Should not raise exception if file write fails."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            # Should not raise an exception
            log_debug("This should not crash")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])