"""Tests for HackerRank sync helpers that do not require credentials."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.sync_hackerrank import (
    Submission,
    extract_problem_statement,
    extract_submission_code,
    extract_submission_language,
    get_solution_path,
    load_synced_submission_id,
    parse_submission,
    write_problem_readme,
    write_solution,
    validate_cookie,
)


class SyncHackerRankTests(unittest.TestCase):
    def test_validate_cookie_rejects_a_bare_token(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "cookie pairs"):
            validate_cookie("session-token-only")

    def test_validate_cookie_accepts_named_cookie_pairs(self) -> None:
        validate_cookie("_hrank_session=session-token")

    def test_parse_submission_normalizes_versioned_python_language(self) -> None:
        submission = parse_submission(
            {
                "id": 9,
                "status": "Accepted",
                "language": {"name": "Python 3.11"},
                "challenge": {"name": "Two Strings", "slug": "two-strings"},
            }
        )

        self.assertEqual(submission.language if submission else None, "python3")

    def test_parse_submission_accepts_nested_challenge_data(self) -> None:
        submission = parse_submission(
            {
                "id": "9",
                "status": "Accepted",
                "language": "Python3",
                "challenge": {"name": "Two Strings", "slug": "two-strings"},
            }
        )

        self.assertIsNotNone(submission)
        self.assertEqual(submission.submission_id if submission else None, 9)
        self.assertEqual(submission.language if submission else None, "python3")

    def test_parse_submission_rejects_non_accepted_submissions(self) -> None:
        self.assertIsNone(
            parse_submission(
                {
                    "id": 9,
                    "status": "Wrong Answer",
                    "language": "Python3",
                    "challenge": {"name": "Two Strings", "slug": "two-strings"},
                }
            )
        )

    def test_parse_submission_allows_language_to_be_resolved_from_details(self) -> None:
        submission = parse_submission(
            {
                "id": 9,
                "status": "Accepted",
                "challenge": {"name": "Two Strings", "slug": "two-strings"},
            }
        )

        self.assertIsNotNone(submission)
        self.assertIsNone(submission.language if submission else None)

    def test_extract_submission_language_from_detail_response(self) -> None:
        self.assertEqual(
            extract_submission_language({"model": {"language": "Python3"}}),
            "python3",
        )

    def test_extract_submission_code_from_detail_response(self) -> None:
        self.assertEqual(
            extract_submission_code({"model": {"code": "print('ok')"}}),
            "print('ok')",
        )

    def test_extract_problem_statement_from_challenge_response(self) -> None:
        self.assertEqual(
            extract_problem_statement({"model": {"body": "<p>Find two strings.</p>"}}),
            "<p>Find two strings.</p>",
        )

    def test_solution_path_uses_slug_and_language_extension(self) -> None:
        path = get_solution_path(Submission(1, "python3", "Two Strings", "two-strings"))

        self.assertEqual(path, Path("hackerrank-solutions/two-strings/solution.py"))

    def test_write_solution_only_updates_changed_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "solution.py"

            self.assertTrue(write_solution(path, "print('first')"))
            self.assertFalse(write_solution(path, "print('first')\n"))
            self.assertTrue(write_solution(path, "print('second')"))

    def test_problem_readme_contains_source_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            readme_path = Path(directory) / "README.md"
            submission = Submission(1, "python3", "Two Strings", "two-strings")

            with mock.patch("scripts.sync_hackerrank.get_readme_path", return_value=readme_path):
                self.assertTrue(write_problem_readme(submission, "<p>Find two strings.</p>"))

            readme = readme_path.read_text(encoding="utf-8")
            self.assertIn("https://www.hackerrank.com/challenges/two-strings/problem", readme)

    def test_metadata_tracks_submission_per_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "metadata.json"
            metadata_path.write_text('{"submissions": {"python3": 1}}', encoding="utf-8")

            self.assertEqual(load_synced_submission_id(metadata_path, "python3"), 1)
