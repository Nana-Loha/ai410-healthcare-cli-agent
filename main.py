import typer

app = typer.Typer()

@app.command()
def symptoms(input: str = typer.Option(..., help="Free-form symptom description")):
    """Check symptoms and get possible conditions."""
    print(f"Checking symptoms: {input}")
    print("⚕️  This information is not a substitute for professional medical advice.")

@app.command()
def summarize(input: str = typer.Option("", help="Inline record text"),
              file: str = typer.Option("", help="Path to medical record file")):
    """Summarize a medical record."""
    if not input and not file:
        print("Please provide --input or --file")
        raise typer.Exit(code=1)
    source = file if file else input
    print(f"Summarizing: {source}")
    print("⚕️  This information is not a substitute for professional medical advice.")

@app.command()
def interactions(drugs: str = typer.Option("", help="Comma-separated drug names")):
    """Check drug interactions."""
    if not drugs:
        print("Please provide --drugs")
        raise typer.Exit(code=1)
    print(f"Checking interactions for: {drugs}")
    print("⚕️  This information is not a substitute for professional medical advice.")

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