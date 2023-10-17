import typer
import os
import subprocess
import argparse  # Import argparse for processing command-line arguments

app = typer.Typer()

@app.command()
def model(question):
    print(f"here is the question: {question}")

@app.command()
def help():
    print("help")

@app.command()
def upload(json_path: str): 
    os.chdir("/Users/adititripathi/Desktop/ollama")
    ollama_command = "ollama serve"
    ollama_process = subprocess.Popen(ollama_command, shell=True)

    print("Ollama is running")
    training_script_path = "/Users/adititripathi/privadoRepos/privado-buddy-CLI/training.py"
    command = ["python3", training_script_path, "--json_path", json_path]
    print(command)
    subprocess.run(command)
    ollama_process.terminate()
    print("Ollama has been stopped")

if __name__ == "__main__":
    app()
