"""
Core validation module using pydantic-ai with pluggable AI backends.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .backends import get_backend
from .parser import DocxParser
from .parsers import detect_parser, get_parser

# Set up module logger
logger = logging.getLogger(__name__)


class ValidationSpec(BaseModel):
    """Specification for document validation requirements.

    Attributes:
        name (str):
            Name of the validation requirement.
        description (str):
            Detailed description of what to check.
        category (str):
            Category of the requirement.
        score (float):
            Score weight for this test (default 1.0).
    """

    name: str = Field(description="Name of the validation requirement")
    description: str = Field(description="Detailed description of what to check")
    category: Optional[str] = Field(default=None, description="Category of the requirement")
    score: float = Field(default=1.0, description="Score weight for this test (default 1.0)")


class ValidationResult(BaseModel):
    """Result of a single validation check.

    Attributes:
        spec_name (str):
            Name of the validation specification.
        passed (bool):
            Whether the validation passed.
        confidence (float):
            Confidence score between 0.0 and 1.0.
        reasoning (str):
            Explanation of the result.
    """

    spec_name: str = Field(description="Name of the validation specification")
    passed: bool = Field(description="Whether the validation passed")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(default=None, description="Explanation of the result")


class ValidationReport(BaseModel):
    """Complete validation report for a document.

    Attributes:
        file_path (str):
            Path to the validated document.
        results (List[ValidationResult]):
            List of validation results.
        total_specs (int):
            Total number of specifications checked.
        passed_count (int):
            Number of specifications that passed.
        failed_count (int):
            Number of specifications that failed.
        score (float):
            Normalized score (achieved/total_available).
        total_score_available (float):
            Total score available from all tests.
        achieved_score (float):
            Actual score achieved from passed tests.
    """

    file_path: str = Field(description="Path to the validated document")
    results: List[ValidationResult] = Field(description="List of validation results")
    total_specs: int = Field(description="Total number of specifications checked")
    passed_count: int = Field(description="Number of specifications that passed")
    failed_count: int = Field(description="Number of specifications that failed")
    score: float = Field(description="Normalized score (achieved/total_available)")
    total_score_available: float = Field(description="Total score available from all tests")
    achieved_score: float = Field(description="Actual score achieved from passed tests")


class DocxValidator:
    """Validator for documents using LLM-based analysis.

    Supports multiple AI backends including OpenAI, GitHub Models, and NebulaOne.
    Supports multiple document formats including DOCX, HTML, and LaTeX.

    Keyword Parameters:
        backend (str):
            Name of the backend to use ('openai', 'github', 'nebulaone').
        model_name (str):
            Name of the model to use.
        api_key (str):
            API key for authentication. If not provided, will try environment variables:
            For OpenAI/GitHub: GITHUB_TOKEN or OPENAI_API_KEY.
            For NebulaOne: NEBULAONE_API_KEY or OPENAI_API_KEY.
        base_url (str):
            Base URL for the API endpoint. If not provided, will try environment variables:
            For OpenAI/GitHub: OPENAI_BASE_URL.
            For NebulaOne: NEBULAONE_BASE_URL.
        parser (str):
            Name of the parser to use ('docx', 'html', 'latex').
            If not provided, parser will be auto-detected from file extension.
        **backend_kwargs:
            Additional backend-specific configuration options.

    Examples:
        # Use OpenAI (default) with auto-detected parser
        validator = DocxValidator()

        # Use GitHub Models with explicit HTML parser
        validator = DocxValidator(backend='github', parser='html', api_key='ghp_xxx')

        # Use NebulaOne with LaTeX parser
        validator = DocxValidator(
            backend='nebulaone', model_name='nebula-1',
            parser='latex', api_key='your-key', base_url='https://api.nebulaone.example'
        )
    """

    def __init__(
        self,
        backend: str = "openai",
        model_name: str = "gpt-5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        parser: Optional[str] = None,
        **backend_kwargs,
    ):
        # Store parser preference for auto-detection
        self._parser_name = parser
        # For backward compatibility, maintain a parser instance (will be docx by default)
        self.parser = DocxParser() if parser is None else get_parser(parser)

        # Create the backend
        self.backend = get_backend(
            backend, model_name=model_name, api_key=api_key, base_url=base_url, **backend_kwargs
        )

        # Create the validation agent
        self.agent = self.backend.get_agent(
            system_prompt=(
                "You are a document validation expert. Analyze document structures "
                "and determine if they meet specific requirements. Provide clear, "
                "factual assessments based on the document structure data provided."
            )
        )

    def validate(self, file_path: str, specifications: List[ValidationSpec]) -> ValidationReport:
        """Validate a document file against a list of specifications.

        This method optimizes LLM API calls by setting up the document context once,
        then validating each specification against that context using message history.
        This reduces token usage significantly compared to repeating the document
        structure in each validation request.

        Supports multiple document formats including DOCX, HTML, and LaTeX.
        The parser is auto-detected from file extension if not explicitly specified.

        Args:
            file_path (str):
                Path to the document file to validate.
            specifications (List[ValidationSpec]):
                List of validation specifications to check.

        Returns:
            (ValidationReport):
                ValidationReport containing all validation results and scores.

        Examples:
            >>> validator = DocxValidator()
            >>> specs = [ValidationSpec(name="Has Title", description="Must have a title")]
            >>> report = validator.validate("document.docx", specs)
            >>> print(f"Score: {report.score:.2%}")
        """
        # Detect or use the appropriate parser
        if self._parser_name:
            parser = get_parser(self._parser_name)
        else:
            parser = detect_parser(file_path)

        # Parse the document structure
        doc_structure = parser.parse(file_path)

        # Set up the document context once for all validations
        message_history = self._setup_document_context(doc_structure)

        # Check if context setup succeeded
        use_context_method = bool(message_history)
        if use_context_method:
            logger.info("Using context-based validation (efficient, shares document context)")
        else:
            logger.info("Using legacy validation method (includes document in each request)")

        # Validate against each specification
        results: List[ValidationResult] = []
        for spec in specifications:
            if use_context_method:
                result, message_history = self._validate_spec_with_context(
                    spec, message_history, doc_structure
                )
            else:
                # Fall back to legacy method that includes document in each request
                result = self._validate_spec(doc_structure, spec)
            results.append(result)

        # Calculate scores
        passed_count = sum(1 for r in results if r.passed)
        total_specs = len(specifications)

        # Calculate weighted scores
        # Create a mapping of spec_name to result for robust matching
        result_map = {result.spec_name: result for result in results}
        total_score_available = sum(spec.score for spec in specifications)
        achieved_score = sum(spec.score for spec in specifications if result_map[spec.name].passed)
        # Handle edge cases with zero or negative total scores
        # When total is <= 0, score calculation is undefined, so default to 0.0
        if total_score_available > 0:
            score = achieved_score / total_score_available
        else:
            score = 0.0

        return ValidationReport(
            file_path=file_path,
            results=results,
            total_specs=total_specs,
            passed_count=passed_count,
            failed_count=total_specs - passed_count,
            score=score,
            total_score_available=total_score_available,
            achieved_score=achieved_score,
        )

    def _setup_document_context(self, doc_structure: Dict[str, Any]) -> List[Any]:
        """Set up the document context for validation.

        Sends the document structure once to the LLM. This establishes context
        that can be reused for multiple validation checks without repeating
        the document structure.

        Args:
            doc_structure (Dict[str, Any]):
                Parsed document structure.

        Returns:
            (List[Any]):
                Message history list that can be passed to subsequent validation calls.
        """
        # Prepare the context setup prompt
        context_prompt = f"""
I will provide you with a document structure to analyze. After I provide the document, \
I will ask you a series of validation questions about it. Please analyze and remember \
this document structure.

Document Structure:
{json.dumps(doc_structure, indent=2, default=str)}

Please confirm you have received and understood the document structure by responding \
with: "Document structure received and ready for validation."
"""

        try:
            # Log the prompt at debug level
            logger.debug("=" * 80)
            logger.debug("LLM REQUEST - Document Context Setup")
            logger.debug("=" * 80)
            logger.debug("Prompt:\n%s", context_prompt)
            logger.debug("-" * 80)
            
            # Run the agent to establish context
            response = self.backend.run_sync(self.agent, context_prompt)
            
            # Log the response at debug level
            logger.debug("Response received")
            logger.debug("Response data: %s", str(response.data))
            if hasattr(response, 'usage') and response.usage():
                logger.debug("Token usage: %s", response.usage())
            if hasattr(response, 'metadata') and response.metadata:
                logger.debug("Response metadata: %s", response.metadata)
            logger.debug("=" * 80)
            
            # Return the message history from this interaction
            return response.all_messages()
        except Exception as e:
            # If context setup fails, log the error and return empty history
            # This will trigger fallback to the legacy validation method
            # Note: We log the exception type but not the full message to avoid
            # potentially exposing sensitive information in logs
            logger.warning(
                f"Context setup failed with {type(e).__name__}. "
                "Falling back to legacy validation method (includes document in each request)."
            )
            return []

    def _validate_spec_with_context(
        self, spec: ValidationSpec, message_history: List[Any], doc_structure: Dict[str, Any]
    ) -> Tuple[ValidationResult, List[Any]]:
        """Validate a specification against the document using established context.

        Args:
            spec (ValidationSpec):
                Validation specification to check.
            message_history (List[Any]):
                Message history containing the document context.
            doc_structure (Dict[str, Any]):
                Parsed document structure (used as fallback if context is lost).

        Returns:
            (Tuple[ValidationResult, List[Any]]):
                A tuple containing the ValidationResult for this specification
                and the updated message history.
        """
        # Safety check: if message_history is empty, fall back to legacy method
        if not message_history:
            logger.warning(
                f"Message history empty for spec '{spec.name}'. "
                "Falling back to legacy validation method for this spec."
            )
            return self._validate_spec(doc_structure, spec), message_history

        # Prepare the validation prompt (without repeating the document)
        prompt = f"""
Now validate this requirement:

Requirement Name: {spec.name}
Description: {spec.description}
{f"Category: {spec.category}" if spec.category else ""}

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
            # Log the prompt at debug level
            logger.debug("=" * 80)
            logger.debug("LLM REQUEST - Validation (with context)")
            logger.debug("=" * 80)
            logger.debug("Specification: %s", spec.name)
            logger.debug("Prompt:\n%s", prompt)
            logger.debug("-" * 80)
            
            # Run the agent with message history for context
            response = self.backend.run_sync(self.agent, prompt, message_history=message_history)
            response_text = str(response.data)
            
            # Log the response at debug level
            logger.debug("Response received")
            logger.debug("Response data: %s", response_text)
            if hasattr(response, 'usage') and response.usage():
                logger.debug("Token usage: %s", response.usage())
            if hasattr(response, 'metadata') and response.metadata:
                logger.debug("Response metadata: %s", response.metadata)
            logger.debug("=" * 80)

            # Parse the response
            passed = (
                "PASS" in response_text.upper()
                and "FAIL" not in response_text.split("Result:")[1].split("\n")[0].upper()
            )

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

            result = ValidationResult(
                spec_name=spec.name,
                passed=passed,
                confidence=confidence,
                reasoning=reasoning or response_text,
            )
            # Return both result and updated message history for context continuity
            return result, response.all_messages()

        except Exception as e:
            # If validation fails, return a failed result with error
            result = ValidationResult(
                spec_name=spec.name,
                passed=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
            )
            # Preserve message history even on error
            return result, message_history

    def _validate_spec(
        self, doc_structure: Dict[str, Any], spec: ValidationSpec
    ) -> ValidationResult:
        """Validate document structure against a single specification using LLM.

        This is the legacy method that includes the full document in each request.
        It's kept for backward compatibility but is not used by the default validate() method.

        Args:
            doc_structure (Dict[str, Any]):
                Parsed document structure.
            spec (ValidationSpec):
                Validation specification to check.

        Returns:
            (ValidationResult):
                ValidationResult for this specification.
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
            # Log the prompt at debug level
            logger.debug("=" * 80)
            logger.debug("LLM REQUEST - Validation (legacy method)")
            logger.debug("=" * 80)
            logger.debug("Specification: %s", spec.name)
            logger.debug("Prompt:\n%s", prompt)
            logger.debug("-" * 80)
            
            # Run the agent synchronously using the backend
            response = self.backend.run_sync(self.agent, prompt)
            response_text = str(response.data)
            
            # Log the response at debug level
            logger.debug("Response received")
            logger.debug("Response data: %s", response_text)
            if hasattr(response, 'usage') and response.usage():
                logger.debug("Token usage: %s", response.usage())
            if hasattr(response, 'metadata') and response.metadata:
                logger.debug("Response metadata: %s", response.metadata)
            logger.debug("=" * 80)

            # Parse the response
            passed = (
                "PASS" in response_text.upper()
                and "FAIL" not in response_text.split("Result:")[1].split("\n")[0].upper()
            )

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
