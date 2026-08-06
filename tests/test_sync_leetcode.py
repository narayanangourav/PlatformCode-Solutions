"""Tests for LeetCode sync helpers that do not require credentials."""

import tempfile
import unittest
from pathlib import Path

from scripts.sync_leetcode import Submission, get_solution_path, parse_submission, write_solution


class SyncLeetCodeTests(unittest.TestCase):
    def test_parse_submission_rejects_non_accepted_submissions(self) -> None:
        submission = parse_submission(
            {"id": "1", "lang": "python3", "statusDisplay": "Wrong Answer", "titleSlug": "two-sum"}
        )

        self.assertIsNone(submission)

    def test_solution_path_uses_slug_and_language_extension(self) -> None:
        path = get_solution_path(Submission(1, "python3", "two-sum"))

        self.assertEqual(path, Path("leetcode-solutions/two-sum/solution.py"))

    def test_write_solution_only_updates_changed_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "solution.py"

            self.assertTrue(write_solution(path, "print('first')"))
            self.assertFalse(write_solution(path, "print('first')\n"))
            self.assertTrue(write_solution(path, "print('second')"))
