from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

class ChatbotConsole:
    def __init__(self):
        self.console = Console(theme=Theme({
            "user": "green bold",
            "ai_thought": "cyan",
            "ai_action": "yellow",
            "divider": "dim white",
            "error": "red bold",
            "warning": "yellow bold",
            "success": "green bold"
        }))

    def print_user_message(self, message):
        self.console.print(Panel(f"[user]User: {message}[/user]"), justify="right")

    def print_ai_response(self, message):
        self.console.print(Panel(
            f"[ai_thought]Agent:\n{message}[/ai_thought]"
        ), justify="left")

    def print_action_output(self, message):
        self.console.print(Panel(
            f"[ai_action]Action Output:\n{message}[/ai_action]"
        ), justify="left")

    def print_divider(self):
        self.console.print("[divider]" + "─" * 80 + "[/divider]\n")

    def print_error(self, message):
        self.console.print(f"[error]Error: {message}[/error]")

    def print_warning(self, message):
        self.console.print(f"[warning]Warning: {message}[/warning]")

    def print_success(self, message):
        self.console.print(f"[success]Success: {message}[/success]")