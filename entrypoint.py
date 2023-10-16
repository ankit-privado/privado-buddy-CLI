import typer

app = typer.Typer()

@app.command()
def model(question):
    print(f"here is the question: {question}")

@app.command()
def help():
    print("help")

@app.command()
def upload(json_path):
    print(f"uploading file to model: {json_path}")

if __name__ == "__main__":
    app()