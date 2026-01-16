"""
Core validation module using pydantic-ai and GitHub models.
"""

import json
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .parser import DocxParser


class ValidationSpec(BaseModel):
    """Specification for document validation requirements."""

    name: str = Field(description="Name of the validation requirement")
    description: str = Field(description="Detailed description of what to check")
    category: Optional[str] = Field(default=None, description="Category of the requirement")


class ValidationResult(BaseModel):
    """Result of a single validation check."""

    spec_name: str = Field(description="Name of the validation specification")
    passed: bool = Field(description="Whether the validation passed")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(default=None, description="Explanation of the result")


class ValidationReport(BaseModel):
    """Complete validation report for a document."""

    file_path: str = Field(description="Path to the validated document")
    results: List[ValidationResult] = Field(description="List of validation results")
    total_specs: int = Field(description="Total number of specifications checked")
    passed_count: int = Field(description="Number of specifications that passed")
    failed_count: int = Field(description="Number of specifications that failed")
    score: float = Field(description="Numerical score (passed/total)")


class DocxValidator:
    """
    Validator for .docx files using LLM-based analysis.

    Uses GitHub models through pydantic-ai to validate document structure
    against specification requirements.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the DocxValidator.

        Args:
            model_name: Name of the OpenAI-compatible model to use
            api_key: API key for the model (uses GITHUB_TOKEN or OPENAI_API_KEY env var if not provided)
            
        Note:
            To use a custom endpoint (like GitHub Models), set the OPENAI_BASE_URL environment variable.
            For GitHub Models, use: OPENAI_BASE_URL="https://models.inference.ai.azure.com"
        """
        self.model_name = model_name
        self.parser = DocxParser()

        # Set default API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")

        # Create the OpenAI-compatible model
        # pydantic-ai will automatically use OPENAI_API_KEY and OPENAI_BASE_URL environment variables
        self.model = OpenAIChatModel(model_name)

        # Create the validation agent
        self.agent = Agent(
            model=self.model,
            system_prompt=(
                "You are a document validation expert. Analyze document structures "
                "and determine if they meet specific requirements. Provide clear, "
                "factual assessments based on the document structure data provided."
            ),
        )

    def validate(
        self, file_path: str, specifications: List[ValidationSpec]
    ) -> ValidationReport:
        """
        Validate a .docx file against a list of specifications.

        Args:
            file_path: Path to the .docx file to validate
            specifications: List of validation specifications to check

        Returns:
            ValidationReport containing all validation results and scores
        """
        # Parse the document structure
        doc_structure = self.parser.parse_docx(file_path)

        # Validate against each specification
        results: List[ValidationResult] = []
        for spec in specifications:
            result = self._validate_spec(doc_structure, spec)
            results.append(result)

        # Calculate scores
        passed_count = sum(1 for r in results if r.passed)
        total_specs = len(specifications)
        score = passed_count / total_specs if total_specs > 0 else 0.0

        return ValidationReport(
            file_path=file_path,
            results=results,
            total_specs=total_specs,
            passed_count=passed_count,
            failed_count=total_specs - passed_count,
            score=score,
        )

    def _validate_spec(
        self, doc_structure: Dict[str, Any], spec: ValidationSpec
    ) -> ValidationResult:
        """
        Validate document structure against a single specification using LLM.

        Args:
            doc_structure: Parsed document structure
            spec: Validation specification to check

        Returns:
            ValidationResult for this specification
        """
        # Prepare the validation prompt
        prompt = f"""
Analyze the following document structure and determine if it meets this requirement:

Requirement Name: {spec.name}
Description: {spec.description}

Document Structure:
{json.dumps(doc_structure, indent=2, default=str)}

Does the document meet this requirement? Respond with:
1. "PASS" or "FAIL"
2. A confidence score between 0.0 and 1.0
3. A brief explanation of your reasoning

Format your response as:
Result: PASS/FAIL
Confidence: 0.0-1.0
Reasoning: Your explanation here
"""

        try:
            # Run the agent synchronously
            response = self.agent.run_sync(prompt)
            response_text = str(response.data)

            # Parse the response
            passed = "PASS" in response_text.upper() and "FAIL" not in response_text.split("Result:")[1].split("\n")[0].upper()
            
            # Extract confidence
            confidence = 0.8  # Default confidence
            if "Confidence:" in response_text:
                try:
                    conf_str = response_text.split("Confidence:")[1].split("\n")[0].strip()
                    confidence = float(conf_str)
                except (ValueError, IndexError):
                    pass

            # Extract reasoning
            reasoning = None
            if "Reasoning:" in response_text:
                try:
                    reasoning = response_text.split("Reasoning:")[1].strip()
                except IndexError:
                    reasoning = response_text

            return ValidationResult(
                spec_name=spec.name,
                passed=passed,
                confidence=confidence,
                reasoning=reasoning or response_text,
            )

        except Exception as e:
            # If validation fails, return a failed result with error
            return ValidationResult(
                spec_name=spec.name,
                passed=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
            )
