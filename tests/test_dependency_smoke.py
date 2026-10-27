"""Offline regression checks for dependency upgrades."""

import json
import unittest
from unittest.mock import patch

from typer.core import TyperGroup
from typer.main import get_command
from typer.testing import CliRunner

from linear import __version__
from linear.cli import app
from linear.models import Issue
from linear.query_parser import QueryParseError, Tokenizer


def _issue() -> Issue:
    return Issue.model_validate(
        {
            "id": "issue-uuid",
            "identifier": "ENG-123",
            "title": "Dependency smoke test",
            "priorityLabel": "Normal",
            "url": "https://linear.app/example/issue/ENG-123",
            "createdAt": "2026-10-27T00:00:00Z",
            "updatedAt": "2026-10-27T00:00:00Z",
            "state": {"id": "state-uuid", "name": "Todo", "type": "unstarted"},
            "team": {"id": "team-uuid", "name": "Engineering", "key": "ENG"},
            "labels": {"nodes": []},
        }
    )


class DependencySmokeTests(unittest.TestCase):
    """Exercise Typer, Rich, Pydantic, and filter parsing without API calls."""

    def setUp(self) -> None:
        """Prevent accidental network access and create a CLI runner."""
        network = patch(
            "httpx.Client.send", side_effect=AssertionError("Unexpected HTTP request")
        )
        network.start()
        self.addCleanup(network.stop)
        self.runner = CliRunner()

    def test_all_command_help(self) -> None:
        """Render help for every command, including aliases and nested groups."""
        root_path: list[str] = []
        pending = [(root_path, get_command(app))]
        while pending:
            path, command = pending.pop()
            with self.subTest(command=" ".join(path) or "linear"):
                result = self.runner.invoke(app, [*path, "--help"])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("Usage:", result.output)
            if isinstance(command, TyperGroup):
                pending.extend(
                    ([*path, name], child) for name, child in command.commands.items()
                )

    def test_version(self) -> None:
        """Keep both eager version flags usable without credentials."""
        for flag in ("--version", "-V"):
            with self.subTest(flag=flag):
                result = self.runner.invoke(app, [flag])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn(__version__, result.output)

    def test_documentation(self) -> None:
        """Keep the Typer Markdown documentation generator working."""
        result = self.runner.invoke(app, ["docs"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("# Linear CLI Documentation", result.output)
        self.assertIn("linear issues update", result.output)
        self.assertIn("--yes", result.output)

    def test_list_option_parsing_and_output(self) -> None:
        """Check repeatable options, booleans, JSON, and Rich tables."""
        for output_format in ("json", "table"):
            with (
                self.subTest(format=output_format),
                patch(
                    "linear.commands.issues.LinearClient", autospec=True
                ) as client_class,
            ):
                client = client_class.return_value
                client.list_issues.return_value = ([_issue()], {"hasNextPage": False})
                result = self.runner.invoke(
                    app,
                    [
                        "--verbose",
                        "issues",
                        "list",
                        "--all-assignees",
                        "--label",
                        "bug",
                        "--label",
                        "urgent",
                        "--per-page",
                        "10",
                        "--format",
                        output_format,
                    ],
                )
                self.assertEqual(result.exit_code, 0, result.output)
                kwargs = client.list_issues.call_args.kwargs
                self.assertEqual(kwargs["labels"], ["bug", "urgent"])
                self.assertEqual(kwargs["limit"], 10)
                self.assertIsNone(kwargs["assignee"])
                client.get_viewer.assert_not_called()
                if output_format == "json":
                    self.assertEqual(
                        json.loads(result.stdout)["issues"][0]["identifier"], "ENG-123"
                    )
                else:
                    self.assertIn("ENG-123", result.output)
                    self.assertIn("Dependency smoke test", result.output)

    def test_delete_confirmation(self) -> None:
        """Keep deletion opt-in and allow both confirmation bypass flags."""
        for flags, answer, deleted in (
            ([], "n\n", False),
            ([], "y\n", True),
            (["--yes"], "", True),
            (["-y"], "", True),
        ):
            with (
                self.subTest(flags=flags, answer=answer),
                patch(
                    "linear.commands.issues.LinearClient", autospec=True
                ) as client_class,
            ):
                client = client_class.return_value
                client.get_issue.return_value = _issue()
                result = self.runner.invoke(
                    app, ["issues", "delete", "ENG-123", *flags], input=answer
                )
                self.assertEqual(result.exit_code, 0, result.output)
                if deleted:
                    client.delete_issue.assert_called_once_with(issue_id="issue-uuid")
                else:
                    client.delete_issue.assert_not_called()
                if flags:
                    self.assertNotIn("Are you sure", result.output)

    def test_model_aliases_and_serialization(self) -> None:
        """Preserve GraphQL aliases, connection nodes, dates, and URL serialization."""
        issue = _issue()
        self.assertEqual(issue.priority_label, "Normal")
        self.assertEqual(issue.labels, [])
        self.assertEqual(issue.created_at.year, 2026)
        payload = issue.model_dump(mode="json", by_alias=True)
        self.assertEqual(payload["priorityLabel"], "Normal")
        self.assertEqual(payload["url"], "https://linear.app/example/issue/ENG-123")
        self.assertEqual(Issue.model_validate(payload), issue)
        self.assertEqual(Issue.model_validate(issue.model_dump(mode="json")), issue)

    def test_tokenizer_strings(self) -> None:
        """Preserve quoted, escaped, and unquoted filter values."""
        for query, expected in (
            ('status:"in progress"', ["status", ":", "in progress"]),
            ('title:"say \\"hi\\""', ["title", ":", 'say "hi"']),
            ("team:ENG", ["team", ":", "ENG"]),
            ("assignee:me@example.com", ["assignee", ":", "me@example.com"]),
        ):
            with self.subTest(query=query):
                self.assertEqual(
                    [token.value for token in Tokenizer(query).tokenize()], expected
                )
        with self.assertRaises(QueryParseError):
            Tokenizer('status:"unterminated').tokenize()
