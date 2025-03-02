#!/usr/bin/env python3

import os
import click
import requests
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Log, Input, Button
from textual.reactive import var

from scraping.test_model_query import get_ai_response

@click.group()
def cli():
    """
    Hackillinois CLI:
      - activate: Scrape files in a given directory.
      - chat: Launch an in-terminal Textual-based chat UI.
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
    Launch the in-terminal chat interface using Ollama for responses.
    """
    ChatApp().run()

class ChatApp(App):
    """
    A Textual TUI app that sends user messages to Ollama and displays the response.
    """

    CSS = """
    /* ------------------------------------------------------------------------
       Color variables
       ------------------------------------------------------------------------ */
    $bg: #1E1E2E;            /* Main background */
    $text: #D9E0EE;          /* Default text color */
    $panel: #2A2B40;         /* Header/footer panel color */
    $log-bg: #252637;        /* Background for the chat log */
    $button-send: #FF79C6;   /* "Send" button color (pink) */
    $button-exit: #FF5555;   /* "Exit" button color (red) */

    /* ------------------------------------------------------------------------
       Global Styles
       ------------------------------------------------------------------------ */
    Screen {
        background: $bg;
        color: $text;
    }

    /* ------------------------------------------------------------------------
       Header (top)
       ------------------------------------------------------------------------ */
    Header {
        background: $panel;
        text-style: bold;
        height: 2;
        content-align: center middle;
        color: $text;
        border: none;
    }

    /* ------------------------------------------------------------------------
       Footer (bottom)
       ------------------------------------------------------------------------ */
    Footer {
        background: $panel;
        height: 1;
        color: $text;
        border: none;
    }

    /* ------------------------------------------------------------------------
       Main container for the chat
       ------------------------------------------------------------------------ */
    #chat-container {
        background: $bg;
        width: 90%;
        height: 1fr;
        margin: 1 5;
        padding: 0;
        border: none;
    }

    /* ------------------------------------------------------------------------
       Scrollable area for messages
       ------------------------------------------------------------------------ */
    Log {
        background: $log-bg;
        width: 100%;
        height: 1fr;
        padding: 1;
        border: none;
    }

    /* ------------------------------------------------------------------------
       Input row (bottom of chat container)
       ------------------------------------------------------------------------ */
    #input-container {
        width: 100%;
        height: auto;
        background: $bg;
        border: none;
        padding: 1;
    }

    Input {
        width: 1fr;
        margin-right: 1;
        background: $log-bg;
        color: $text;
        border: none;
        padding: 1 2;
    }

    /* ------------------------------------------------------------------------
       Buttons
       ------------------------------------------------------------------------ */
    Button {
        width: auto;
        padding: 0 2;
        color: black;
        text-style: bold;
        margin-left: 1;
        border: none;
    }

    Button#send_button {
        background: $button-send;
    }

    Button#exit_button {
        background: $button-exit;
    }
    """

    user_message_count = var(0)

    def compose(self) -> ComposeResult:
        yield Header(name="HackIllinois name", show_clock=False)
        with Vertical(id="chat-container"):
            # Enable bracket markup by setting highlight=True
            self.chat_log = Log(highlight=True)
            yield self.chat_log
            with Horizontal(id="input-container"):
                self.input_box = Input(placeholder="Type your message here...")
                yield self.input_box
                yield Button("Send", id="send_button")
                yield Button("Exit", id="exit_button")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_button":
            self.send_user_message()
        elif event.button.id == "exit_button":
            self.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.send_user_message()

    def send_user_message(self) -> None:
        """
        Displays the user's message in the chat log, then fetches a response from Ollama.
        """
        message = self.input_box.value.strip()
        if not message:
            return

        # Bracket markup for bold label
        self.chat_log.write(f"User: {message}\n")  
        self.input_box.value = ""

        # Get the response from Ollama
        response = self.fetch_ollama_response(message)
        self.chat_log.write(f"Assistant: {response}\n")  


    def fetch_ollama_response(self, user_message: str) -> str:
        return get_ai_response(user_message)
        try:
            print(f"Sending request to Ollama: {user_message}")  # Debugging

            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2", "prompt": user_message, "stream": False}
            )

            print(f"Response status code: {resp.status_code}")  # Debugging
            print(f"Response text: {resp.text}")  # Debugging

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