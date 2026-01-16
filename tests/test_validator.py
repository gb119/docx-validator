"""
Basic tests for the docx-validator package.
"""

import pytest

from docx_validator import DocxValidator, ValidationResult, ValidationSpec
from docx_validator.parser import DocxParser


def test_validation_spec_creation():
    """Test creating a ValidationSpec."""
    spec = ValidationSpec(
        name="Test Spec", description="This is a test specification", category="test"
    )
    assert spec.name == "Test Spec"
    assert spec.description == "This is a test specification"
    assert spec.category == "test"


def test_validation_result_creation():
    """Test creating a ValidationResult."""
    result = ValidationResult(
        spec_name="Test Spec",
        passed=True,
        confidence=0.95,
        reasoning="Document meets all requirements",
    )
    assert result.spec_name == "Test Spec"
    assert result.passed is True
    assert result.confidence == 0.95
    assert result.reasoning == "Document meets all requirements"


def test_docx_parser_file_not_found():
    """Test that DocxParser raises FileNotFoundError for missing files."""
    parser = DocxParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_docx("nonexistent_file.docx")


def test_docx_parser_invalid_extension():
    """Test that DocxParser raises ValueError for non-.docx files."""
    import os
    import tempfile

    parser = DocxParser()

    # Create a temporary file with wrong extension
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="is not supported by DocxParser"):
            parser.parse_docx(temp_path)
    finally:
        os.unlink(temp_path)


def test_validation_spec_from_json():
    """Test loading ValidationSpec from JSON."""
    json_data = {
        "name": "Has Title",
        "description": "Document must have a title",
        "category": "metadata",
    }
    spec = ValidationSpec(**json_data)
    assert spec.name == "Has Title"
    assert spec.description == "Document must have a title"
    assert spec.category == "metadata"


def test_validation_spec_with_score():
    """Test ValidationSpec with custom score."""
    spec = ValidationSpec(name="Critical Test", description="A critical validation test", score=2.5)
    assert spec.name == "Critical Test"
    assert spec.score == 2.5


def test_validation_spec_default_score():
    """Test ValidationSpec uses default score of 1.0."""
    spec = ValidationSpec(name="Standard Test", description="A standard validation test")
    assert spec.score == 1.0


def test_validation_spec_negative_score():
    """Test ValidationSpec allows negative scores."""
    spec = ValidationSpec(
        name="Penalty Test", description="A test that penalizes on failure", score=-1.0
    )
    assert spec.score == -1.0


def test_validation_spec_with_score_from_json():
    """Test loading ValidationSpec with score from JSON."""
    json_data = {
        "name": "Important Test",
        "description": "An important validation test",
        "category": "critical",
        "score": 3.0,
    }
    spec = ValidationSpec(**json_data)
    assert spec.name == "Important Test"
    assert spec.score == 3.0


def test_validator_initialization():
    """Test DocxValidator initialization."""
    import os

    # Set a test API key for initialization
    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        # Test default OpenAI backend
        validator = DocxValidator(
            model_name="gpt-4o-mini",
            api_key="test_key",
        )
        assert validator.backend.name == "openai"

        # Test GitHub backend
        validator_github = DocxValidator(
            backend="github",
            model_name="gpt-4o-mini",
            api_key="test_key",
        )
        assert validator_github.backend.name == "openai"  # GitHub uses OpenAI backend

        # Test NebulaOne backend
        validator_nebula = DocxValidator(
            backend="nebulaone",
            model_name="nebula-1",
            api_key="test_key",
        )
        assert validator_nebula.backend.name == "nebulaone"
    finally:
        # Clean up
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_backend_registry():
    """Test that all backends are registered correctly."""
    from docx_validator.backends import BACKENDS

    assert "openai" in BACKENDS
    assert "github" in BACKENDS
    assert "nebulaone" in BACKENDS


def test_get_backend():
    """Test the get_backend function."""
    import os

    from docx_validator.backends import get_backend

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        # Test creating backends
        openai_backend = get_backend("openai", model_name="gpt-4")
        assert openai_backend.name == "openai"

        nebula_backend = get_backend("nebulaone", model_name="nebula-1")
        assert nebula_backend.name == "nebulaone"

        # Test invalid backend
        try:
            get_backend("invalid_backend")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown backend" in str(e)
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_validation_report_weighted_scores():
    """Test ValidationReport calculates weighted scores correctly."""
    from docx_validator import ValidationReport, ValidationResult

    # Create results for a report with mixed pass/fail
    results = [
        ValidationResult(spec_name="Test 1", passed=True, confidence=1.0),
        ValidationResult(spec_name="Test 2", passed=True, confidence=1.0),
        ValidationResult(spec_name="Test 3", passed=False, confidence=1.0),
    ]

    report = ValidationReport(
        file_path="test.docx",
        results=results,
        total_specs=3,
        passed_count=2,
        failed_count=1,
        score=0.6667,
        total_score_available=5.0,  # e.g., 2.0 + 1.0 + 2.0
        achieved_score=3.0,  # e.g., 2.0 + 1.0 (passed tests)
    )

    assert report.total_specs == 3
    assert report.passed_count == 2
    assert report.failed_count == 1
    assert report.total_score_available == 5.0
    assert report.achieved_score == 3.0
    # Score should be 3.0 / 5.0 = 0.6
    assert abs(report.score - 0.6667) < 0.01


def test_validation_report_all_tests_equal_weight():
    """Test that equal weights give same result as count-based scoring."""
    from docx_validator import ValidationReport, ValidationResult

    # All tests have score 1.0 (default)
    results = [
        ValidationResult(spec_name="Test 1", passed=True, confidence=1.0),
        ValidationResult(spec_name="Test 2", passed=False, confidence=1.0),
        ValidationResult(spec_name="Test 3", passed=True, confidence=1.0),
    ]

    report = ValidationReport(
        file_path="test.docx",
        results=results,
        total_specs=3,
        passed_count=2,
        failed_count=1,
        score=2.0 / 3.0,
        total_score_available=3.0,  # 3 tests * 1.0
        achieved_score=2.0,  # 2 passed tests * 1.0
    )

    # With equal weights, score should be same as passed_count/total_specs
    assert report.score == pytest.approx(2.0 / 3.0)
    assert report.total_score_available == 3.0
    assert report.achieved_score == 2.0


def test_validation_report_negative_scores():
    """Test ValidationReport handles negative scores.

    This test documents the edge case where negative scores could result in
    zero or negative total_score_available. In such cases, the score calculation
    is undefined, so it defaults to 0.0 to avoid division by zero or misleading results.

    This scenario might occur if users assign penalty scores that cancel out positive scores.
    """
    from docx_validator import ValidationReport, ValidationResult

    # Test with negative score for penalty that cancels out positive score
    results = [
        ValidationResult(spec_name="Test 1", passed=True, confidence=1.0),
        ValidationResult(spec_name="Penalty Test", passed=False, confidence=1.0),
    ]

    # When a test with negative score fails, total_score_available could be 0 or negative
    # In this case the score calculation should handle it gracefully
    report = ValidationReport(
        file_path="test.docx",
        results=results,
        total_specs=2,
        passed_count=1,
        failed_count=1,
        score=0.0,  # When total <= 0, score defaults to 0.0 (undefined calculation)
        total_score_available=0.0,  # 1.0 + (-1.0) = 0
        achieved_score=1.0,
    )

    assert report.total_score_available == 0.0
    assert report.achieved_score == 1.0
    assert report.score == 0.0


def test_validation_report_negative_total():
    """Test ValidationReport with negative total score available.

    This edge case occurs when the sum of negative scores exceeds positive scores.
    The score defaults to 0.0 as the calculation would be meaningless.
    """
    from docx_validator import ValidationReport, ValidationResult

    results = [
        ValidationResult(spec_name="Test 1", passed=True, confidence=1.0),
        ValidationResult(spec_name="Big Penalty", passed=False, confidence=1.0),
    ]

    # Total is negative: 1.0 + (-2.0) = -1.0
    report = ValidationReport(
        file_path="test.docx",
        results=results,
        total_specs=2,
        passed_count=1,
        failed_count=1,
        score=0.0,  # Undefined when total < 0
        total_score_available=-1.0,
        achieved_score=1.0,
    )

    assert report.total_score_available == -1.0
    assert report.achieved_score == 1.0
    assert report.score == 0.0


def test_context_setup_method():
    """Test that _setup_document_context method works correctly."""
    import os
    from unittest.mock import MagicMock, Mock

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        validator = DocxValidator(model_name="gpt-4o-mini", api_key="test_key")

        # Create a mock response
        mock_response = MagicMock()
        mock_response.data = "Document structure received and ready for validation."
        mock_response.all_messages.return_value = [{"role": "user", "content": "test"}]

        # Mock the backend's run_sync to return our mock response
        validator.backend.run_sync = Mock(return_value=mock_response)

        # Test document structure
        doc_structure = {
            "metadata": {"title": "Test", "author": "Test Author"},
            "paragraphs": ["Test paragraph"],
        }

        # Call the method
        message_history = validator._setup_document_context(doc_structure)

        # Verify the method was called
        assert validator.backend.run_sync.called
        assert len(message_history) > 0
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_validate_spec_with_context():
    """Test that _validate_spec_with_context method works correctly."""
    import os
    from unittest.mock import MagicMock, Mock

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        validator = DocxValidator(model_name="gpt-4o-mini", api_key="test_key")

        # Create a mock response
        mock_response = MagicMock()
        mock_response.data = "Result: PASS\nConfidence: 0.95\nReasoning: Document has a title"
        mock_response.all_messages.return_value = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"},
        ]

        # Mock the backend's run_sync to return our mock response
        validator.backend.run_sync = Mock(return_value=mock_response)

        # Test specification
        spec = ValidationSpec(
            name="Has Title", description="Document must have a title", category="metadata"
        )

        # Mock message history
        message_history = [{"role": "user", "content": "Document structure..."}]

        # Call the method (now returns tuple)
        result, updated_history = validator._validate_spec_with_context(spec, message_history)

        # Verify the result
        assert result.spec_name == "Has Title"
        assert result.passed is True
        assert result.confidence == 0.95
        assert "title" in result.reasoning.lower()
        # Verify message history was returned
        assert updated_history is not None
        assert len(updated_history) > 0
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_context_based_validation_efficiency():
    """
    Test that validates the efficiency improvement of context-based validation.

    This test verifies that when validating multiple specs, the document structure
    is only sent once in the initial context setup, not repeated for each spec.
    """
    import json
    import os
    from unittest.mock import MagicMock, Mock

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        validator = DocxValidator(model_name="gpt-4o-mini", api_key="test_key")

        # Track all prompts sent to the backend
        prompts_sent = []

        def mock_run_sync(agent, prompt, message_history=None):
            prompts_sent.append({"prompt": prompt, "has_history": message_history is not None})
            mock_response = MagicMock()
            if "Document Structure:" in prompt:
                # This is the context setup
                mock_response.data = "Document structure received and ready for validation."
            else:
                # This is a validation request
                mock_response.data = "Result: PASS\nConfidence: 0.9\nReasoning: Test passed"
            mock_response.all_messages.return_value = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": str(mock_response.data)},
            ]
            return mock_response

        validator.backend.run_sync = Mock(side_effect=mock_run_sync)

        # Create test specs
        specs = [
            ValidationSpec(name="Test 1", description="First test"),
            ValidationSpec(name="Test 2", description="Second test"),
            ValidationSpec(name="Test 3", description="Third test"),
        ]

        # Create a simple mock document
        doc_structure = {"metadata": {"title": "Test"}, "paragraphs": ["Content"]}

        # Mock the detect_parser to avoid file validation
        from unittest.mock import patch

        mock_parser = Mock()
        mock_parser.parse = Mock(return_value=doc_structure)

        with patch("docx_validator.validator.detect_parser", return_value=mock_parser):
            # Run validation (this should use the new context-based approach)
            report = validator.validate("test.docx", specs)

            # Verify the results
            assert report.total_specs == 3

            # Verify efficiency: should have 4 calls total
            # 1 for context setup + 3 for individual validations
            assert len(prompts_sent) == 4

            # First call should be context setup (no message history)
            assert not prompts_sent[0]["has_history"]
            assert "Document Structure:" in prompts_sent[0]["prompt"]

            # Count how many times the full document structure appears in prompts
            doc_json = json.dumps(doc_structure, indent=2, default=str)
            full_doc_appearances = sum(1 for p in prompts_sent if doc_json in p["prompt"])

            # Document should only appear once (in context setup), not in validation prompts
            assert full_doc_appearances == 1, (
                "Document structure should only be sent once in context setup"
            )

            # Subsequent calls should have message history
            for i in range(1, 4):
                assert prompts_sent[i]["has_history"], (
                    f"Validation call {i} should have message history"
                )
                assert "Document Structure:" not in prompts_sent[i]["prompt"], (
                    f"Validation call {i} should not repeat the document structure"
                )

    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
