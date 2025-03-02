import click
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Log, Input, Button
from textual.reactive import var
from scraping.test_model_query import get_ai_response


@click.group()
def cli():
    """Hackillinois CLI"""
    pass


@cli.command()
def chat():
    """Launches the in-terminal chat interface"""
    Alexandria().run()


class Alexandria(App):
    """Textual-based TUI chat application"""

    CSS = """
    /* Styling omitted for brevity, but keep it the same */
    """

    user_message_count = var(0)

    def compose(self) -> ComposeResult:
        yield Header(name="HackIllinois Chat", show_clock=False)
        with Vertical(id="chat-container"):
            self.chat_log = Log(highlight=True)
            yield self.chat_log
            with Horizontal(id="input-container"):
                self.input_box = Input(placeholder="Type your message here...")
                yield self.input_box
                yield Button("Enter", id="enter_button")
                yield Button("Exit", id="exit_button")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "enter_button":
            self.send_user_message()
        elif event.button.id == "exit_button":
            self.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.send_user_message()

    def send_user_message(self) -> None:
        """Sends user input to the AI and displays the response."""
        message = self.input_box.value.strip()
        if not message:
            return

        self.chat_log.write(f"User: {message}\n")
        self.input_box.value = ""

        response = self.fetch_ollama_response(message)
        self.chat_log.write(f"Assistant: {response}\n")

    def fetch_ollama_response(self, user_message: str) -> str:
        """Uses test_model_query to get an AI-generated response"""
        return get_ai_response(user_message)


def main():
    cli()


if __name__ == "__main__":
    main()
