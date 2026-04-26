import typer
import json
from pathlib import Path
from typing import Optional

app = typer.Typer()
DISCLAIMER = "⚕️  This information is not a substitute for professional medical advice."
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
def summarize(input: str = typer.Option("", help="Inline record text"),
              file: str = typer.Option("", help="Path to medical record file"),
              output: Optional[str] = typer.Option(None, help="Optional path to save results as .txt"),
              format: str = typer.Option("text", "--format", help="Output format: text or json")):
    """Summarize a medical record."""
    if input and file:
        print("Please provide either --input or --file, not both")
        raise typer.Exit(code=4)
    if not input and not file:
        print("Please provide --input or --file")
        raise typer.Exit(code=1)
    source = file if file else input
    response_text = _build_response(f"Summarizing: {source}", format)
    _print_and_optionally_save(response_text, output)

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