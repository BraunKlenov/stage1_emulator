"""Tests for the variant 17 stage 1 shell prototype."""

import os
import unittest
from unittest.mock import patch

from src.main import CommandError
from src.main import execute_command
from src.main import expand_variables
from src.main import parse_command
from src.main import ShellApp


class ShellParserTests(unittest.TestCase):
    """Verify command parsing and environment expansion."""

    def test_environment_variable_expands(self) -> None:
        """Verify the corresponding behavior."""
        with patch.dict(os.environ, {"HOME": "/tmp/test-home"}):
            self.assertEqual(
                parse_command('cd "$HOME"'),
                ["cd", "/tmp/test-home"],
            )

    def test_expand_variables_uses_real_environment(self) -> None:
        """Verify the corresponding behavior."""
        with patch.dict(os.environ, {"V17_TEST": "value"}):
            self.assertEqual(expand_variables("$V17_TEST"), "value")

    def test_quoted_argument_is_preserved(self) -> None:
        """Verify the corresponding behavior."""
        self.assertEqual(
            parse_command('ls "two words"'),
            ["ls", "two words"],
        )


class CommandTests(unittest.TestCase):
    """Verify commands required by stage 1."""

    def test_ls_stub_outputs_name_and_arguments(self) -> None:
        """Verify the corresponding behavior."""
        result = execute_command(["ls", "-la"])
        self.assertEqual(result.text, "ls -la")

    def test_cd_stub_outputs_name_and_arguments(self) -> None:
        """Verify the corresponding behavior."""
        result = execute_command(["cd", "/tmp"])
        self.assertEqual(result.text, "cd /tmp")

    def test_exit_stops_application(self) -> None:
        """Verify the corresponding behavior."""
        result = execute_command(["exit"])
        self.assertTrue(result.should_exit)

    def test_unknown_command_is_error(self) -> None:
        """Verify the corresponding behavior."""
        with self.assertRaisesRegex(CommandError, "Неизвестная команда"):
            execute_command(["unknown"])

    def test_exit_arguments_are_error(self) -> None:
        """Verify the corresponding behavior."""
        with self.assertRaisesRegex(CommandError, "не принимает аргументы"):
            execute_command(["exit", "now"])

    def test_unclosed_quote_is_error(self) -> None:
        """Verify the corresponding behavior."""
        with self.assertRaisesRegex(CommandError, "Ошибка разбора"):
            parse_command('ls "broken')


class GuiTests(unittest.TestCase):
    """Verify GUI-independent window configuration."""

    def test_window_title_contains_vfs_name(self) -> None:
        """Verify the corresponding behavior."""
        app = object.__new__(ShellApp)
        app.vfs_name = "VFS-17"
        self.assertIn("VFS-17", app.window_title())


if __name__ == "__main__":
    unittest.main()
