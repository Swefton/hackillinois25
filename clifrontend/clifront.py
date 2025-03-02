#!/usr/bin/env python3

import os
import click
import requests
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Log, Input, Button, Static
from textual.reactive import var

@click.group()
def cli():
    """
    Hackillinois CLI:
      - activate: Scrape files in a given directory.
      - chat: Launch Alexandria – Your CLI Companion (Textual-based).
    """
    pass

@cli.command()
def activate():
    """Scrape files in a given directory."""
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
    """Launch Alexandria – Your CLI Companion."""
    Alexandria().run()

# ─────────────────────────────────────────────────────────────────────────────
# A simple spinning circle widget
# ─────────────────────────────────────────────────────────────────────────────

class SpinningCircle(Static):
    """
    A simple spinner that cycles through frames in a timer.
    Visible = True => spinner is shown; Visible = False => hidden.
    """

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_index: var[int] = var(0)

    def on_mount(self) -> None:
        # We'll animate the spinner ~10 FPS
        self.set_interval(0.1, self.update_spinner)
        # Hide by default
        self.visible = False

    def update_spinner(self) -> None:
        # If visible, cycle frames
        if self.visible:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.update(self.frames[self.frame_index])
        else:
            # If hidden, show nothing
            self.update("")

# ─────────────────────────────────────────────────────────────────────────────
# Main Chat Screen
# ─────────────────────────────────────────────────────────────────────────────

class MainChatScreen(Screen):
    """
    Main chat UI. We'll embed the spinner in the same screen,
    toggling visibility when we start or finish the Ollama request.
    """

    CSS = """
    /* Color Variables */
    $bg:         #16161e;
    $text:       #c6c8d1;
    $panel:      #24273a;
    $log-bg:     #1a1b26;
    $button-send:#FF79C6;
    $button-exit:#FF5555;

    Screen {
        background: $bg;
        color: $text;
    }

    Header {
        background: $panel;
        text-style: bold;
        height: 3;
        content-align: center middle;
        border: none;
        color: $text;
    }

    Footer {
        background: $panel;
        height: 1;
        border: none;
        color: $text;
    }

    #chat-container {
        background: $bg;
        width: 90%;
        height: 1fr;
        margin: 1 5;
        padding: 1;
        border: none;
    }

    Log {
        background: $log-bg;
        width: 100%;
        height: 70%;
        padding: 1;
        border: none;
        text-style: bold;
    }

    #input-container {
        background: $bg;
        padding: 1;
    }

    Input {
        width: 1fr;
        margin-right: 1;
        background: $log-bg;
        color: $text;
        padding: 1 3;
        border: none;
    }

    Button {
        width: auto;
        padding: 1 4;
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

    /* Position the spinner next to the Send/Exit buttons or somewhere else if desired */
    #spinner-container {
        width: auto;
        margin-left: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(name="📖 Alexandria – Your CLI Companion", show_clock=False)
        with Vertical(id="chat-container"):
            self.chat_log = Log(highlight=True)
            yield self.chat_log

            # Input row
            with Horizontal(id="input-container"):
                self.input_box = Input(placeholder="Write your query...")
                yield self.input_box
                yield Button("Send", id="send_button")
                yield Button("Exit", id="exit_button")
                # Spinner container
                with Horizontal(id="spinner-container"):
                    self.spinner = SpinningCircle()
                    yield self.spinner

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_button":
            self.send_user_message()
        elif event.button.id == "exit_button":
            self.app.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.send_user_message()

    def send_user_message(self) -> None:
        # Show the spinner
        self.spinner.visible = True
        message = self.input_box.value.strip()
        if not message:
            # No message, hide spinner again
            self.spinner.visible = False
            return
        self.chat_log.write(f"User: {message}\n")
        self.input_box.value = ""

        # Fetch the assistant response
        response = self.fetch_ollama_response(message)

        # Hide spinner once we have the response
        self.spinner.visible = False

        self.chat_log.write(f"Assistant:{response}\n")

    def fetch_ollama_response(self, user_message: str) -> str:
        try:
            payload = {
                "model": "llama2",  # Adjust to your installed model
                "prompt": user_message,
                "stream": False
            }
            r = requests.post("http://127.0.0.1:11434/api/generate", json=payload)
            data = r.json()
            return data.get("response", "No response from Ollama.")
        except Exception as e:
            return f"Error calling Ollama: {e}"

# ─────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────

class Alexandria(App):
    """
    Main Textual App that only shows the main chat UI,
    but includes a spinner for requests.
    """
    def on_mount(self) -> None:
        # Instead of a loading screen, we directly push the chat UI
        self.push_screen(MainChatScreen())

    def compose(self) -> ComposeResult:
        # Fallback compose if no screen is active
        yield Header(name="📖 Alexandria – Your CLI Companion", show_clock=False)
        # We won't define the spinner here; it's in the MainChatScreen
        yield Footer()

def main():
    cli()

if __name__ == "__main__":
    main()
