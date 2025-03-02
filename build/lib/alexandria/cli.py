#!/usr/bin/env python3

import os
import json
import click
import requests
from rich import print as rprint
from rich.panel import Panel
from rich import box
from libfetch.combined_libs import parse_workspace_for_libraries  # Library detection
from scraping.scrape import scrape_full_documentation  # Scraping function
from scraping.test_model_query import get_ai_response  # AI response function

# For colored input
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

# Style so that typed text is blue
session_style = Style.from_dict({'': 'ansiblue'})
session = PromptSession(style=session_style)


@click.group()
def cli():
    """Alexandria CLI: Scan, Scrape, and Chat"""
    pass


@cli.command()
@click.argument("directory", required=False)
def init(directory=None):
    """Initialize Alexandria by creating a .alexandria folder for caching data."""
    
    target_dir = os.path.abspath(directory) if directory else os.getcwd()
    alexandria_path = os.path.join(target_dir, ".alexandria")

    try:
        os.makedirs(alexandria_path, exist_ok=True)
        click.echo(f"✅ Alexandria initialized at: {alexandria_path}")
    except Exception as e:
        click.echo(f"❌ Error initializing Alexandria: {e}")


@cli.command()
@click.argument("directory", required=False)
def scan(directory=None):
    """Scans the given workspace directory for libraries and scrapes their documentation."""
    
    target_dir = os.path.abspath(directory) if directory else os.getcwd()
    alexandria_path = os.path.join(target_dir, ".alexandria")

    if not os.path.exists(alexandria_path):
        click.echo(f"❌ Error: The .alexandria directory is missing in {target_dir}. Run 'alexandria init' first.")
        return

    # Detect libraries
    click.echo(f"🔍 Scanning workspace at {target_dir} for libraries...")
    parse_workspace_for_libraries(alexandria_path, target_dir)
    click.echo("✅ Library scan complete!")

    # Load libraries from combined_libraries.json
    combined_libraries_path = os.path.join(alexandria_path, "combined_libraries.json")
    if not os.path.exists(combined_libraries_path):
        click.echo(f"❌ Error: No libraries found in {combined_libraries_path}.")
        return

    with open(combined_libraries_path, "r", encoding="utf-8") as file:
        combined_libraries = json.load(file)

    # Extract libraries with valid documentation URLs
    libraries_to_scrape = []
    for lang, libraries in combined_libraries.items():
        for lib in libraries:
            if lib["doc_link"] and "Documentation not found" not in lib["doc_link"]:
                libraries_to_scrape.append((lib["library"], lib["doc_link"]))

    if not libraries_to_scrape:
        click.echo("⚠️ No valid documentation links found. Skipping scraping.")
        return

    # Scrape documentation for each detected library
    click.echo("🌐 Starting documentation scraping...")
    for name, link in libraries_to_scrape:
        click.echo(f"📖 Scraping docs for {name} at {link}")
        scrape_full_documentation(link, name, target_dir)

    click.echo("✅ All detected libraries have been scraped!")


@cli.command()
@click.argument("directory", required=False, type=click.Path(exists=False))
def chat(directory=None):
    """Launch the Alexandria chat interface with contextual knowledge from a given directory."""
    
    target_dir = os.path.abspath(directory) if directory else os.getcwd()
    alexandria_path = os.path.join(target_dir, ".alexandria")

    # Ensure the .alexandria directory exists
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
            # Prompt user for input
            user_input = session.prompt(">> ")

            if user_input.lower() in ("exit", "quit"):
                rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
                break

            # Display user input
            rprint(Panel(f"[bold blue]User:[/bold blue] {user_input}", border_style="blue", box=box.ROUNDED))

            # Fetch AI response with context
            response = fetch_ollama_response(user_input, alexandria_path)
            rprint(Panel(f"[bold magenta]Assistant:[/bold magenta] {response}", border_style="magenta", box=box.ROUNDED))

        except KeyboardInterrupt:
            rprint(Panel("Exiting chat...", border_style="red", box=box.ROUNDED))
            break


def fetch_ollama_response(user_message: str, directory: str) -> str:
    """
    Uses Alexandria's LLM response function to generate a reply based on stored documentation.
    """
    try:
        response = get_ai_response(user_message, directory)  # ✅ Passes directory correctly
        return response
    except Exception as e:
        return f"Error calling Alexandria LLM: {str(e)}"


def main():
    cli()


if __name__ == "__main__":
    main()
