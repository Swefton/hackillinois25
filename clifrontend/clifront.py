#!/usr/bin/env python3

import os
import click
import requests

from rich import print as rprint
from rich.panel import Panel
from rich import box

# For colored input
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

# Style so that typed text is blue
session_style = Style.from_dict({
    '': 'ansiblue'  # or use '#0000ff' if you prefer a hex color
})
session = PromptSession(style=session_style)

@click.group()
def cli():
    """
    Hackillinois CLI:
      - activate: Scrape files in a given directory.
      - chat: Launch a simple in-terminal chat interface.
    """
    pass

@cli.command()
def activate():
    """
    Prompts for a directory path and scrapes all files in that directory.
    """
    click.echo("Welcome! Please give path to project (ex: desktop/p1)")
    project_path = input(">> ").strip()

    if not os.path.isdir(project_path):
        click.echo(f"Error: '{project_path}' is not a valid directory.")
        return

    collected_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            collected_files.append(file_path)

    if collected_files:
        click.echo("Scraping complete. Files collected:")
        for f in collected_files:
            click.echo(f)
    else:
        click.echo("No files found in that directory.")

@cli.command()
def chat():
    """
    Launch a barebone chat interface.
    """
    rprint(Panel("Welcome to Hackillinois Chat",
                 title="Hackillinois Chat",
                 border_style="green",
                 box=box.ROUNDED))

    while True:
        try:
            # Prompt user for input in blue
            user_input = session.prompt("User: >> ")

            # Let user exit
            if user_input.lower() in ("exit", "quit"):
                rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
                break

            # Show user’s message in a blue panel
            rprint(Panel(f"[bold blue]User:[/bold blue] {user_input}",
                         border_style="blue",
                         box=box.ROUNDED))

            # Fetch a response (adjust as needed for your actual endpoint/model)
            response = fetch_ollama_response(user_input)

            # Show assistant response in a magenta panel
            rprint(Panel(f"[bold magenta]Assistant:[/bold magenta] {response}",
                         border_style="magenta",
                         box=box.ROUNDED))
        except KeyboardInterrupt:
            rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
            break

def fetch_ollama_response(user_message: str) -> str:
    """
    Example function to get a response from Ollama. 
    Adjust for your actual endpoint/model as needed.
    """
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": user_message, "stream": False}
        )
        if resp.status_code != 200:
            return f"Error: Received status code {resp.status_code}"
        data = resp.json()
        return data.get("response", "No response key found in JSON.")
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"

def main():
    cli()

if __name__ == "__main__":
    main()
