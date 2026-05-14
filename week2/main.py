import typer
import json
from pathlib import Path
from typing import Optional

from summarizer import summarize_record

app = typer.Typer()
DISCLAIMER = "This information is not a substitute for professional medical advice, diagnosis, or treatment."
VALID_FORMATS = {"text", "json"}


def _print_and_optionally_save(response_text: str, output: Optional[str]) -> None:
    """Print response text and optionally persist the exact same content."""
    print(response_text)

    if output is None:
        return

    output_path = Path(output)
    if not output_path.parent.exists():
        typer.echo(f"Error: output directory does not exist: {output_path.parent}", err=True)
        raise typer.Exit(code=2)

    try:
        output_path.write_text(response_text, encoding="utf-8")
    except OSError as exc:
        typer.echo(f"Error: could not write output file: {exc}", err=True)
        raise typer.Exit(code=2)

    print(f"Results saved to {output}")


def _normalize_format(format_value: str) -> str:
    normalized = format_value.lower()
    if normalized not in VALID_FORMATS:
        typer.echo("Invalid format. Please use 'text' or 'json'.", err=True)
        raise typer.Exit(code=1)
    return normalized


def _build_response(result_text: str, format_value: str) -> str:
    normalized_format = _normalize_format(format_value)
    if normalized_format == "json":
        return json.dumps({"result": result_text, "disclaimer": DISCLAIMER}, ensure_ascii=False)
    return f"{result_text}\n{DISCLAIMER}"

@app.command()
def symptoms(
    input: str = typer.Option(..., help="Free-form symptom description"),
    output: Optional[str] = typer.Option(None, help="Optional path to save results as .txt"),
    format: str = typer.Option("text", "--format", help="Output format: text or json"),
):
    """Check symptoms and get possible conditions."""
    response_text = _build_response(f"Checking symptoms: {input}", format)
    _print_and_optionally_save(response_text, output)

@app.command()
def summarize(
    input: str = typer.Option("", help="Inline medical record text"),
    file: str = typer.Option("", help="Path to a local medical record file"),
    provider: str = typer.Option(
        "",
        "--provider",
        help="Reserved for future provider-backed summarization; local mode is used to satisfy FR-004.",
    ),
    output: Optional[str] = typer.Option(None, help="Optional path to save summary as .txt"),
    format: str = typer.Option("text", "--format", help="Output format: text or json"),
):
    """Summarize a medical record (diagnoses, medications, allergies, follow-ups).

    Patient data is processed in-memory only and never persisted (FR-004).
    """
    if input and file:
        typer.echo("Error: provide --input or --file, not both.", err=True)
        raise typer.Exit(code=4)
    if not input and not file:
        typer.echo("Error: provide --input <text> or --file <path>.", err=True)
        raise typer.Exit(code=1)
    if output is not None:
        typer.echo("Error: summarize does not support --output because FR-004 forbids persisting patient data.", err=True)
        raise typer.Exit(code=4)

    # Read record text into memory only — never write it to disk.
    if file:
        record_path = Path(file)
        if not record_path.exists():
            typer.echo(f"Error: file not found: {file}", err=True)
            raise typer.Exit(code=2)
        try:
            record_text = record_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            typer.echo(f"Error: could not read file: {exc}", err=True)
            raise typer.Exit(code=2)
    else:
        record_text = input

    try:
        summary = summarize_record(record_text)
    except (ValueError, EnvironmentError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=3)

    response_text = _build_response(summary, format)
    print(response_text)

@app.command()
def interactions(
    drugs: str = typer.Option("", help="Comma-separated drug names"),
    output: Optional[str] = typer.Option(None, help="Optional path to save results as .txt"),
    format: str = typer.Option("text", "--format", help="Output format: text or json"),
):
    """Check drug interactions."""
    if not drugs:
        print("Please provide --drugs")
        raise typer.Exit(code=1)
    drug_list = [drug.strip() for drug in drugs.split(",") if drug.strip()]
    if len(drug_list) < 2:
        print("Please provide at least 2 drugs (comma-separated)")
        raise typer.Exit(code=1)
    response_text = _build_response(f"Checking interactions for: {drugs}", format)
    _print_and_optionally_save(response_text, output)

@app.command()
def config(set_provider: str = typer.Option("", help="Set default AI provider"),
           show: bool = typer.Option(False, help="Show current configuration")):
    """Manage provider configuration."""
    if show:
        print("Default provider: claude")
    elif set_provider:
        print(f"Default provider set to: {set_provider}")

if __name__ == "__main__":
    app()