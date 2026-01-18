"""
Tests for logging functionality in the validator.
"""

import logging
import os
from unittest.mock import MagicMock, Mock

import pytest

from docx_tex_validator import DocxValidator, ValidationSpec


def test_debug_logging_captures_prompts_and_responses(caplog):
    """Test that debug logging captures full LLM transcript."""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        # Set logging level to DEBUG to capture debug messages
        caplog.set_level(logging.DEBUG)
        
        validator = DocxValidator(model_name="gpt-4o", api_key="test_key")
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.data = "Document structure received and ready for validation."
        mock_response.all_messages.return_value = [{"role": "user", "content": "test"}]
        mock_response.usage.return_value = {"prompt_tokens": 100, "completion_tokens": 50}
        mock_response.metadata = {"model": "gpt-4o"}
        
        # Mock the backend's run_sync to return our mock response
        validator.backend.run_sync = Mock(return_value=mock_response)
        
        # Test document structure
        doc_structure = {
            "metadata": {"title": "Test", "author": "Test Author"},
            "paragraphs": ["Test paragraph"],
        }
        
        # Call the method that should log
        message_history = validator._setup_document_context(doc_structure)
        
        # Verify debug logging occurred
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        
        # Should have multiple debug log entries
        assert len(debug_logs) > 0, "No debug logs were captured"
        
        # Check that we logged the prompt
        log_text = "\n".join([record.message for record in debug_logs])
        assert "LLM REQUEST" in log_text, "LLM REQUEST header not found in logs"
        assert "Prompt:" in log_text or "prompt" in log_text.lower(), "Prompt not logged"
        assert "Response" in log_text or "response" in log_text.lower(), "Response not logged"
        
        # Check that we logged response data
        assert "Document structure received" in log_text, "Response data not logged"
        
        print("\n=== Captured Debug Logs ===")
        for record in debug_logs:
            print(f"{record.levelname}: {record.message}")
        
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_validation_debug_logging(caplog):
    """Test that validation requests are logged at debug level."""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        # Set logging level to DEBUG
        caplog.set_level(logging.DEBUG)
        
        validator = DocxValidator(model_name="gpt-4o", api_key="test_key")
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.data = "Result: PASS\nConfidence: 0.95\nReasoning: Test passed"
        mock_response.all_messages.return_value = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"},
        ]
        mock_response.usage.return_value = {"prompt_tokens": 50, "completion_tokens": 20}
        mock_response.metadata = {"model": "gpt-4o"}
        
        # Mock the backend's run_sync
        validator.backend.run_sync = Mock(return_value=mock_response)
        
        # Test specification
        spec = ValidationSpec(
            name="Has Title", description="Document must have a title", category="metadata"
        )
        
        # Mock message history
        message_history = [{"role": "user", "content": "Document structure..."}]
        
        # Mock document structure
        doc_structure = {"metadata": {"title": "Test"}, "paragraphs": ["Content"]}
        
        # Call the validation method
        result, updated_history = validator._validate_spec_with_context(
            spec, message_history, doc_structure
        )
        
        # Verify debug logging occurred
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        
        assert len(debug_logs) > 0, "No debug logs were captured"
        
        # Check that we logged the specification name
        log_text = "\n".join([record.message for record in debug_logs])
        assert "Has Title" in log_text, "Specification name not logged"
        assert "Validation" in log_text, "Validation header not found"
        
        print("\n=== Captured Validation Debug Logs ===")
        for record in debug_logs:
            print(f"{record.levelname}: {record.message}")
        
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_backend_logging(caplog):
    """Test that backend logs model and metadata information."""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        # Set logging level to DEBUG
        caplog.set_level(logging.DEBUG, logger="docx_tex_validator.backends.openai")
        
        validator = DocxValidator(model_name="gpt-4o", api_key="test_key")
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.data = "Test response"
        mock_response.all_messages.return_value = []
        mock_response.metadata = {"model": "gpt-4o", "finish_reason": "stop"}
        
        # Create a mock agent
        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_response
        
        # Call run_sync directly
        result = validator.backend.run_sync(mock_agent, "test prompt")
        
        # Verify backend logging occurred
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        
        assert len(debug_logs) > 0, "No debug logs were captured from backend"
        
        log_text = "\n".join([record.message for record in debug_logs])
        assert "gpt-4o" in log_text, "Model name not logged by backend"
        
        print("\n=== Captured Backend Debug Logs ===")
        for record in debug_logs:
            print(f"{record.levelname}: {record.message}")
        
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_default_model_is_gpt4o():
    """Test that the default model is now gpt-4o."""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        # Create validator without specifying model
        validator = DocxValidator(api_key="test_key")
        
        # Check that the model name is gpt-4o
        assert validator.backend.model_name == "gpt-4o", (
            f"Expected default model to be 'gpt-4o', but got '{validator.backend.model_name}'"
        )
        
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
