"""GUI prototype of a UNIX-like shell emulator for practical work 1."""

from __future__ import annotations

import os
import shlex
import socket
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from typing import Callable


VFS_NAME = "VFS-17"
COMMANDS = {"ls", "cd", "exit"}


class CommandError(Exception):
    """Raised when a shell command cannot be executed."""


@dataclass(frozen=True)
class CommandResult:
    """Result of executing one parsed command."""

    text: str
    should_exit: bool = False


def expand_variables(text: str) -> str:
    """Expand environment variables in a command line."""
    return os.path.expandvars(text)


def parse_command(line: str) -> list[str]:
    """Expand environment variables and split a command using shell syntax."""
    expanded = expand_variables(line)
    try:
        return shlex.split(expanded, posix=True)
    except ValueError as error:
        raise CommandError(f"Ошибка разбора: {error}") from error


def execute_command(args: list[str]) -> CommandResult:
    """Execute a stage-1 command and return its textual result."""
    if not args:
        return CommandResult("")

    command, *arguments = args
    if command not in COMMANDS:
        raise CommandError(f"Неизвестная команда: {command}")

    if command == "exit":
        if arguments:
            raise CommandError("Команда exit не принимает аргументы")
        return CommandResult("Выход из эмулятора.", should_exit=True)

    if command in {"ls", "cd"}:
        rendered = " ".join(arguments)
        suffix = f" {rendered}" if rendered else ""
        return CommandResult(f"{command}{suffix}")

    raise CommandError(f"Неизвестная команда: {command}")


class ShellApp:
    """Tkinter application implementing the variant 17 REPL prototype."""

    def __init__(self, root: tk.Tk, vfs_name: str = VFS_NAME) -> None:
        """Initialize the GUI and display the initial prompt."""
        self.root = root
        self.vfs_name = vfs_name
        self.root.title(self.window_title())
        self.root.geometry("760x520")
        self.root.minsize(620, 420)
        self._build_ui()
        self._write_output(self.prompt())
        self._write_output(
            "Введите команду: ls, cd или exit. "
            "Переменные ОС раскрываются автоматически."
        )
        self._set_input_focus()

    def window_title(self) -> str:
        """Return the window title containing the VFS name."""
        return f"Эмулятор оболочки — {self.vfs_name}"

    def prompt(self) -> str:
        """Build a prompt from the current OS user and host."""
        username = (
            os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"
        )
        hostname = socket.gethostname() or "localhost"
        return f"{username}@{hostname}:{self.vfs_name}$ "

    def _build_ui(self) -> None:
        """Build the output area and command input controls."""
        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        self.output = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output.pack(fill=tk.BOTH, expand=True)

        controls = tk.Frame(frame, pady=10)
        controls.pack(fill=tk.X)
        self.entry = tk.Entry(controls)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)

        run_button = tk.Button(
            controls, text="Выполнить", command=self._run_input
        )
        run_button.pack(side=tk.LEFT, padx=(8, 0))

    def _set_input_focus(self) -> None:
        """Focus the command entry widget."""
        self.entry.focus_set()

    def _write_output(self, text: str) -> None:
        """Append one line to the read-only output area."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _on_enter(self, _event: tk.Event) -> str:
        """Execute the current input when Enter is pressed."""
        self._run_input()
        return "break"

    def _run_input(self) -> None:
        """Parse, execute, and display the current command line."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self._write_output(f"{self.prompt()}{line}")
        if not line.strip():
            self._write_output(self.prompt())
            return
        try:
            result = execute_command(parse_command(line))
        except CommandError as error:
            self._show_error(str(error))
            self._write_output(f"Ошибка: {error}")
            self._write_output(self.prompt())
            return
        if result.text:
            self._write_output(result.text)
        if result.should_exit:
            self.root.destroy()
            return
        self._write_output(self.prompt())

    def _show_error(self, message: str) -> None:
        """Display an execution error in a GUI dialog."""
        messagebox.showerror("Ошибка команды", message, parent=self.root)


def create_app(vfs_name: str = VFS_NAME) -> tuple[tk.Tk, ShellApp]:
    """Create the GUI application without starting its event loop."""
    root = tk.Tk()
    return root, ShellApp(root, vfs_name)


def main() -> None:
    """Start the graphical shell emulator."""
    root, _app = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
