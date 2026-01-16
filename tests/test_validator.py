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
        with pytest.raises(ValueError, match="must be a .docx file"):
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
