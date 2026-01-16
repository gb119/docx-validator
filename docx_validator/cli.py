"""
Command-line interface for docx-validator.
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

import click

from . import __version__
from .validator import DocxValidator, ValidationSpec


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    docx-validator - Validate Microsoft Word .docx files using LLM analysis.

    This tool uses GitHub models and pydantic-ai to check if .docx files
    conform to specification requirements.
    """
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--spec-file",
    "-s",
    type=click.Path(exists=True),
    help="JSON file containing validation specifications",
)
@click.option(
    "--spec",
    "-r",
    multiple=True,
    help="Inline specification in format 'name:description'",
)
@click.option(
    "--model",
    "-m",
    default="gpt-4o-mini",
    help="Model name to use (default: gpt-4o-mini)",
)
@click.option(
    "--api-key",
    "-k",
    envvar="GITHUB_TOKEN",
    help="API key for the model (uses GITHUB_TOKEN env var by default)",
)
@click.option(
    "--base-url",
    "-u",
    default="https://models.inference.ai.azure.com",
    help="Base URL for the API endpoint",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for results (JSON format)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed validation results",
)
def validate(
    file_path: str,
    spec_file: Optional[str],
    spec: tuple,
    model: str,
    api_key: Optional[str],
    base_url: str,
    output: Optional[str],
    verbose: bool,
):
    """
    Validate a .docx file against specifications.

    FILE_PATH: Path to the .docx file to validate

    Example:
        docx-validator validate document.docx -s specs.json
        docx-validator validate document.docx -r "Has Title:Document must have a title"
    """
    # Load specifications
    specifications = _load_specifications(spec_file, spec)

    if not specifications:
        click.echo(
            "Error: No specifications provided. Use --spec-file or --spec option.",
            err=True,
        )
        sys.exit(1)

    click.echo(f"Validating: {file_path}")
    click.echo(f"Using model: {model}")
    click.echo(f"Specifications: {len(specifications)}")
    click.echo()

    # Initialize validator
    try:
        validator = DocxValidator(
            model_name=model,
            api_key=api_key,
            base_url=base_url,
        )
    except Exception as e:
        click.echo(f"Error initializing validator: {e}", err=True)
        sys.exit(1)

    # Run validation
    try:
        report = validator.validate(file_path, specifications)
    except Exception as e:
        click.echo(f"Error during validation: {e}", err=True)
        sys.exit(1)

    # Display results
    _display_results(report, verbose)

    # Save to file if requested
    if output:
        _save_results(report, output)
        click.echo(f"\nResults saved to: {output}")

    # Exit with appropriate code
    sys.exit(0 if report.failed_count == 0 else 1)


@cli.command()
@click.argument("output_file", type=click.Path())
def init_spec(output_file: str):
    """
    Create a sample specification file.

    OUTPUT_FILE: Path where the specification file will be created

    Example:
        docx-validator init-spec specifications.json
    """
    sample_specs = [
        {
            "name": "Has Title",
            "description": "Document must contain a title in the metadata",
            "category": "metadata",
        },
        {
            "name": "Has Author",
            "description": "Document must have an author specified in metadata",
            "category": "metadata",
        },
        {
            "name": "Has Headings",
            "description": "Document must use heading styles (Heading 1, Heading 2, etc.)",
            "category": "structure",
        },
        {
            "name": "Has Table of Contents",
            "description": "Document should include a table of contents",
            "category": "structure",
        },
    ]

    try:
        with open(output_file, "w") as f:
            json.dump(sample_specs, f, indent=2)
        click.echo(f"Sample specification file created: {output_file}")
    except Exception as e:
        click.echo(f"Error creating specification file: {e}", err=True)
        sys.exit(1)


def _load_specifications(
    spec_file: Optional[str], inline_specs: tuple
) -> List[ValidationSpec]:
    """Load specifications from file and/or inline arguments."""
    specifications = []

    # Load from file
    if spec_file:
        try:
            with open(spec_file, "r") as f:
                spec_data = json.load(f)
                for spec in spec_data:
                    specifications.append(ValidationSpec(**spec))
        except Exception as e:
            click.echo(f"Error loading specification file: {e}", err=True)
            sys.exit(1)

    # Load inline specs
    for spec_str in inline_specs:
        if ":" in spec_str:
            name, description = spec_str.split(":", 1)
            specifications.append(
                ValidationSpec(name=name.strip(), description=description.strip())
            )
        else:
            click.echo(f"Warning: Invalid spec format: {spec_str}", err=True)

    return specifications


def _display_results(report, verbose: bool):
    """Display validation results to console."""
    click.echo("=" * 70)
    click.echo("VALIDATION RESULTS")
    click.echo("=" * 70)
    click.echo()

    # Summary
    click.echo(f"File: {report.file_path}")
    click.echo(f"Total Specifications: {report.total_specs}")
    click.echo(f"Passed: {report.passed_count}")
    click.echo(f"Failed: {report.failed_count}")
    click.echo(f"Score: {report.score:.2%}")
    click.echo()

    # Individual results
    for result in report.results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        color = "green" if result.passed else "red"
        click.echo(click.style(f"{status}: {result.spec_name}", fg=color, bold=True))

        if verbose and result.reasoning:
            click.echo(f"  Confidence: {result.confidence:.2f}")
            click.echo(f"  Reasoning: {result.reasoning}")
        click.echo()


def _save_results(report, output_file: str):
    """Save validation results to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(report.model_dump(), f, indent=2)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
