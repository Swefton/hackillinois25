#!/usr/bin/env python3

import os
import click
import requests
from rich import print as rprint
from rich.panel import Panel
from rich import box
from scraping.test_model_query import get_ai_response 

# For colored input
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

# Style so that typed text is blue
session_style = Style.from_dict({
    '': 'ansiblue'
})
session = PromptSession(style=session_style)

@click.group()
def cli():
    """
    Alexandria CLI:
      - activate: Scrape files in a given directory.
      - chat: Launch a simple in-terminal chat interface.
    """
    pass

@cli.command()
@click.argument("directory", required=False)
def activate(directory=None):
    """
    Prompts for a directory path and scrapes all files in that directory.
    """
    target_dir = os.path.abspath(directory) if directory else os.getcwd()
    
    if not os.path.isdir(target_dir):
        click.echo(f"❌ Error: '{target_dir}' is not a valid directory.")
        return

    collected_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            collected_files.append(file_path)

    if collected_files:
        click.echo("✅ Scraping complete. Files collected:")
        for f in collected_files:
            click.echo(f)
    else:
        click.echo("⚠️ No files found in that directory.")

@cli.command()
@click.argument("directory", required=False)
def chat(directory=None):
    """
    Launch the Alexandria chat interface with contextual knowledge from a given directory.
    """
    print(directory)
    target_dir = os.path.abspath(directory) if directory else os.getcwd()
    alexandria_path = os.path.join(target_dir, ".alexandria")

    # Ensure the .alexandria directory exists before proceeding
    if not os.path.exists(alexandria_path):
        rprint(Panel(f"❌ Error: No .alexandria directory found in {target_dir}. Run 'alexandria init' first.", border_style="red", box=box.ROUNDED))
        return

    rprint(
        Panel(
            f"Welcome to Alexandria Chat\n[green]Using knowledge from: {alexandria_path}[/green]",
            title="Alexandria",
            border_style="green",
            box=box.ROUNDED
        )
    )

    while True:
        try:
            # Prompt user for input in blue
            user_input = session.prompt(">> ")

            # Allow user to exit
            if user_input.lower() in ("exit", "quit"):
                rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
                break

            # Move cursor up one line and clear it, removing ">> hi"
            print("\033[A\033[K", end='')

            # Now print the user’s message in a blue panel
            rprint(
                Panel(
                    f"[bold blue]User:[/bold blue] {user_input}",
                    border_style="blue",
                    box=box.ROUNDED
                )
            )

            # Fetch assistant response with context
            response = fetch_ollama_response(user_input, alexandria_path)
            rprint(
                Panel(
                    f"[bold magenta]Assistant:[/bold magenta] {response}",
                    border_style="magenta",
                    box=box.ROUNDED
                )
            )

        except KeyboardInterrupt:
            rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
            break

def fetch_ollama_response(user_message: str, directory: str) -> str:
    """
    Uses Alexandria's LLM response function to generate a reply based on stored documentation.
    """
    try:
        response = get_ai_response(user_message, directory)  # Uses the correct function
        return response
    except Exception as e:
        return f"Error calling Alexandria LLM: {str(e)}"

def main():
    cli()

if __name__ == "__main__":
    main()
