"""Tests for LeetCode sync helpers that do not require credentials."""

import tempfile
import unittest
from unittest import mock
from pathlib import Path

from scripts.sync_leetcode import (
    Submission,
    create_headers,
    extract_submission_code,
    get_solution_path,
    has_synced_problem_statement,
    load_synced_submission_id,
    parse_submission,
    write_problem_readme,
    write_solution,
)


class SyncLeetCodeTests(unittest.TestCase):
    def test_request_headers_include_csrf_and_user_agent(self) -> None:
        headers = create_headers("session-value", "csrf-value")

        self.assertEqual(headers["X-CSRFToken"], "csrf-value")
        self.assertIn("LEETCODE_SESSION=session-value", headers["Cookie"])
        self.assertTrue(headers["User-Agent"])

    def test_missing_submission_source_is_skipped(self) -> None:
        self.assertIsNone(extract_submission_code({"submissionDetails": {"code": None}}))

    def test_problem_readme_includes_the_accessible_statement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            readme_path = Path(directory) / "README.md"
            submission = Submission(1, "python3", "Two Sum", "two-sum")

            with mock.patch("scripts.sync_leetcode.get_readme_path", return_value=readme_path):
                self.assertTrue(write_problem_readme(submission, "<p>Find two values.</p>"))

            self.assertIn("<p>Find two values.</p>", readme_path.read_text(encoding="utf-8"))
            self.assertTrue(has_synced_problem_statement(readme_path))

    def test_parse_submission_rejects_non_accepted_submissions(self) -> None:
        submission = parse_submission(
            {"id": "1", "lang": "python3", "statusDisplay": "Wrong Answer", "titleSlug": "two-sum"}
        )

        self.assertIsNone(submission)

    def test_parse_submission_accepts_numeric_submission_ids(self) -> None:
        submission = parse_submission(
            {
                "id": 1,
                "lang": "python3",
                "statusDisplay": "Accepted",
                "title": "Two Sum",
                "titleSlug": "two-sum",
            }
        )

        self.assertIsNotNone(submission)
        self.assertEqual(submission.submission_id if submission else None, 1)

    def test_solution_path_uses_slug_and_language_extension(self) -> None:
        path = get_solution_path(Submission(1, "python3", "Two Sum", "two-sum"))

        self.assertEqual(path, Path("leetcode-solutions/two-sum/solution.py"))

    def test_write_solution_only_updates_changed_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "solution.py"

            self.assertTrue(write_solution(path, "print('first')"))
            self.assertFalse(write_solution(path, "print('first')\n"))
            self.assertTrue(write_solution(path, "print('second')"))

    def test_metadata_tracks_submission_per_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "metadata.json"
            metadata_path.write_text('{"submissions": {"python3": 1}}', encoding="utf-8")

            self.assertEqual(load_synced_submission_id(metadata_path, "python3"), 1)
