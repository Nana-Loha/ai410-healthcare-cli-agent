import typer
from pathlib import Path

app = typer.Typer()


def _print_and_optionally_save(response_text: str, output: str) -> None:
    """Print response text and optionally persist the exact same content."""
    print(response_text)

    if not output:
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

@app.command()
def symptoms(
    input: str = typer.Option(..., help="Free-form symptom description"),
    output: str = typer.Option("", help="Optional path to save results as .txt"),
):
    """Check symptoms and get possible conditions."""
    response_text = (
        f"Checking symptoms: {input}\n"
        "⚕️  This information is not a substitute for professional medical advice."
    )
    _print_and_optionally_save(response_text, output)

@app.command()
def summarize(input: str = typer.Option("", help="Inline record text"),
              file: str = typer.Option("", help="Path to medical record file"),
              output: str = typer.Option("", help="Optional path to save results as .txt")):
    """Summarize a medical record."""
    if not input and not file:
        print("Please provide --input or --file")
        raise typer.Exit(code=1)
    source = file if file else input
    response_text = (
        f"Summarizing: {source}\n"
        "⚕️  This information is not a substitute for professional medical advice."
    )
    _print_and_optionally_save(response_text, output)

@app.command()
def interactions(
    drugs: str = typer.Option("", help="Comma-separated drug names"),
    output: str = typer.Option("", help="Optional path to save results as .txt"),
):
    """Check drug interactions."""
    if not drugs:
        print("Please provide --drugs")
        raise typer.Exit(code=1)
    response_text = (
        f"Checking interactions for: {drugs}\n"
        "⚕️  This information is not a substitute for professional medical advice."
    )
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