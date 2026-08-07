"""Tests for LeetCode sync helpers that do not require credentials."""

import tempfile
import unittest
from pathlib import Path

from scripts.sync_leetcode import (
    Submission,
    create_headers,
    get_solution_path,
    load_synced_submission_id,
    parse_submission,
    write_solution,
)


class SyncLeetCodeTests(unittest.TestCase):
    def test_request_headers_include_csrf_and_user_agent(self) -> None:
        headers = create_headers("session-value", "csrf-value")

        self.assertEqual(headers["X-CSRFToken"], "csrf-value")
        self.assertIn("LEETCODE_SESSION=session-value", headers["Cookie"])
        self.assertTrue(headers["User-Agent"])

    def test_parse_submission_rejects_non_accepted_submissions(self) -> None:
        submission = parse_submission(
            {"id": "1", "lang": "python3", "statusDisplay": "Wrong Answer", "titleSlug": "two-sum"}
        )

        self.assertIsNone(submission)

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
