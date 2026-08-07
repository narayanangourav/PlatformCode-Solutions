"""Download accepted LeetCode submissions into this repository."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LEETCODE_GRAPHQL_URL: Final = "https://leetcode.com/graphql/"
DESTINATION_DIRECTORY: Final = Path("leetcode-solutions")
REQUEST_TIMEOUT_SECONDS: Final = 30
PAGE_SIZE: Final = 20
USER_AGENT: Final = "LeetCode-Solutions-GitHub-Action/1.0"

LANGUAGE_EXTENSIONS: Final[dict[str, str]] = {
    "bash": "sh",
    "c": "c",
    "cpp": "cpp",
    "csharp": "cs",
    "dart": "dart",
    "elixir": "ex",
    "erlang": "erl",
    "golang": "go",
    "java": "java",
    "javascript": "js",
    "kotlin": "kt",
    "mssql": "sql",
    "mysql": "sql",
    "oraclesql": "sql",
    "php": "php",
    "python": "py",
    "python3": "py",
    "pythondata": "py",
    "postgresql": "sql",
    "racket": "rkt",
    "ruby": "rb",
    "rust": "rs",
    "scala": "scala",
    "swift": "swift",
    "typescript": "ts",
}

SUBMISSIONS_QUERY: Final = """
query submissions($offset: Int!, $limit: Int!, $slug: String) {
  submissionList(offset: $offset, limit: $limit, questionSlug: $slug) {
    hasNext
    submissions {
      id
      lang
      statusDisplay
      title
      titleSlug
    }
  }
}
"""

SUBMISSION_DETAILS_QUERY: Final = """
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    code
  }
}
"""


@dataclass(frozen=True)
class Submission:
    """The accepted-submission fields required for saving its source code."""

    submission_id: int
    language: str
    title: str
    title_slug: str


class LeetCodeSyncError(RuntimeError):
    """Raised when LeetCode data cannot be safely retrieved or validated."""


def get_required_environment_value(name: str) -> str:
    """Return a non-empty required environment variable without exposing its value."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise LeetCodeSyncError(f"Missing required environment variable: {name}")
    return value


def create_headers(session: str, csrf_token: str) -> dict[str, str]:
    """Create the authenticated headers required by LeetCode's GraphQL endpoint."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "Origin": "https://leetcode.com",
        "Referer": "https://leetcode.com/",
        "Cookie": f"csrftoken={csrf_token}; LEETCODE_SESSION={session};",
        "X-CSRFToken": csrf_token,
    }


def request_graphql(
    query: str, variables: dict[str, int | str | None], session: str, csrf_token: str
) -> dict[str, object]:
    """Run a GraphQL request and reject malformed or error responses."""
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = Request(LEETCODE_GRAPHQL_URL, body, create_headers(session, csrf_token))

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise LeetCodeSyncError(
            f"LeetCode request failed with HTTP status {error.code}. Verify both GitHub secrets use fresh cookie values and retry."
        ) from error
    except URLError as error:
        raise LeetCodeSyncError("Could not connect to LeetCode. Retry the workflow later.") from error
    except json.JSONDecodeError as error:
        raise LeetCodeSyncError("LeetCode returned an invalid response.") from error

    if not isinstance(payload, dict):
        raise LeetCodeSyncError("LeetCode returned an unexpected response format.")
    errors = payload.get("errors")
    if errors:
        raise LeetCodeSyncError("LeetCode rejected the request. Refresh the GitHub secrets and retry.")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise LeetCodeSyncError("LeetCode response did not contain data.")
    return data


def parse_submission(value: object) -> Submission | None:
    """Return a valid accepted submission, or ignore unusable API data."""
    if not isinstance(value, dict) or value.get("statusDisplay") != "Accepted":
        return None
    submission_id = value.get("id")
    language = value.get("lang")
    title = value.get("title")
    title_slug = value.get("titleSlug")
    if not isinstance(submission_id, str) or not submission_id.isdigit():
        return None
    if not isinstance(language, str) or not isinstance(title, str) or not isinstance(title_slug, str):
        return None
    if not title_slug or language not in LANGUAGE_EXTENSIONS:
        return None
    return Submission(int(submission_id), language, title, title_slug)


def get_accepted_submissions(session: str, csrf_token: str) -> list[Submission]:
    """Get the latest accepted submission for every problem and language."""
    accepted: dict[tuple[str, str], Submission] = {}
    offset = 0

    while True:
        data = request_graphql(
            SUBMISSIONS_QUERY,
            {"offset": offset, "limit": PAGE_SIZE, "slug": None},
            session,
            csrf_token,
        )
        submission_list = data.get("submissionList")
        if not isinstance(submission_list, dict):
            raise LeetCodeSyncError("LeetCode response did not contain a submission list.")
        submissions = submission_list.get("submissions")
        if not isinstance(submissions, list):
            raise LeetCodeSyncError("LeetCode response contained invalid submissions.")

        for item in submissions:
            submission = parse_submission(item)
            if submission is not None:
                accepted.setdefault((submission.title_slug, submission.language), submission)

        has_next = submission_list.get("hasNext")
        if not isinstance(has_next, bool):
            raise LeetCodeSyncError("LeetCode response did not contain pagination information.")
        if not has_next:
            break
        offset += PAGE_SIZE

    return list(accepted.values())


def extract_submission_code(data: dict[str, object]) -> str | None:
    """Return source code when LeetCode makes it available for a submission."""
    details = data.get("submissionDetails")
    if not isinstance(details, dict):
        return None
    code = details.get("code")
    if not isinstance(code, str) or not code.strip():
        return None
    return code


def get_submission_code(submission: Submission, session: str, csrf_token: str) -> str | None:
    """Get source code for one accepted submission, when it is accessible."""
    data = request_graphql(
        SUBMISSION_DETAILS_QUERY,
        {"submissionId": submission.submission_id},
        session,
        csrf_token,
    )
    return extract_submission_code(data)


def get_solution_path(submission: Submission) -> Path:
    """Create a safe, deterministic output path below the destination directory."""
    safe_slug = re.sub(r"[^a-z0-9-]", "", submission.title_slug.lower())
    if not safe_slug:
        raise LeetCodeSyncError("LeetCode returned an unsafe problem slug.")
    extension = LANGUAGE_EXTENSIONS[submission.language]
    return DESTINATION_DIRECTORY / safe_slug / f"solution.{extension}"


def get_metadata_path(submission: Submission) -> Path:
    """Return the metadata path for a synced problem."""
    return get_solution_path(submission).parent / "metadata.json"


def get_readme_path(submission: Submission) -> Path:
    """Return the generated README path for a synced problem."""
    return get_solution_path(submission).parent / "README.md"


def load_synced_submission_id(path: Path, language: str) -> int | None:
    """Read the synced submission ID for one language, if valid metadata exists."""
    if not path.is_file():
        return None
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(metadata, dict):
        return None
    submissions = metadata.get("submissions")
    if not isinstance(submissions, dict):
        return None
    submission_id = submissions.get(language)
    return submission_id if isinstance(submission_id, int) else None


def write_problem_metadata(submission: Submission) -> bool:
    """Record source-only problem metadata without copying LeetCode content."""
    metadata_path = get_metadata_path(submission)
    existing_submissions: dict[str, int] = {}
    if metadata_path.is_file():
        try:
            existing_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if isinstance(existing_metadata, dict) and isinstance(existing_metadata.get("submissions"), dict):
                existing_submissions = {
                    language: submission_id
                    for language, submission_id in existing_metadata["submissions"].items()
                    if isinstance(language, str) and isinstance(submission_id, int)
                }
        except json.JSONDecodeError:
            pass
    existing_submissions[submission.language] = submission.submission_id
    content = json.dumps(
        {"title": submission.title, "titleSlug": submission.title_slug, "submissions": existing_submissions},
        indent=2,
        sort_keys=True,
    ) + "\n"
    if metadata_path.is_file() and metadata_path.read_text(encoding="utf-8") == content:
        return False
    metadata_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def write_problem_readme(submission: Submission) -> bool:
    """Create a local index for the synced source without reproducing problem content."""
    readme_path = get_readme_path(submission)
    content = f"# {submission.title}\n\nLeetCode problem: https://leetcode.com/problems/{submission.title_slug}/\n"
    if readme_path.is_file():
        return False
    readme_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def write_solution(path: Path, code: str) -> bool:
    """Write source only when it changes and return whether a file was updated."""
    normalized_code = code.rstrip() + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == normalized_code:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized_code, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    """Synchronize accepted submissions and return a process exit code."""
    try:
        session = get_required_environment_value("LEETCODE_SESSION")
        csrf_token = get_required_environment_value("LEETCODE_CSRF_TOKEN")
        submissions = get_accepted_submissions(session, csrf_token)
        updated_count = 0
        for submission in submissions:
            solution_path = get_solution_path(submission)
            metadata_path = get_metadata_path(submission)
            if load_synced_submission_id(metadata_path, submission.language) == submission.submission_id:
                continue
            code = get_submission_code(submission, session, csrf_token)
            if code is None:
                print(
                    f"Skipped unavailable source for {submission.title_slug} "
                    f"({submission.language}, submission {submission.submission_id})."
                )
                continue
            updated_count += write_solution(solution_path, code)
            updated_count += write_problem_metadata(submission)
            updated_count += write_problem_readme(submission)
        print(f"Synchronized {updated_count} solution file(s).")
        return 0
    except LeetCodeSyncError as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
