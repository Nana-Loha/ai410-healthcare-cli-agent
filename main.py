import typer

app = typer.Typer()

@app.command()
def symptoms(input: str):
    print(f"Checking symptoms: {input}")
    print("Disclaimer: Not a substitute for professional medical advice.")

@app.command()
def summarize(file: str):
    print(f"Summarizing file: {file}")

@app.command()
def interactions(drugs: str):
    print(f"Checking interactions: {drugs}")

if __name__ == "__main__":
    app()