"""Download accepted HackerRank submissions into this repository."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeAlias
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HACKERRANK_BASE_URL: Final = "https://www.hackerrank.com"
SUBMISSIONS_PATH: Final = "/rest/contests/master/submissions/"
DESTINATION_DIRECTORY: Final = Path("hackerrank-solutions")
REQUEST_TIMEOUT_SECONDS: Final = 30
PAGE_SIZE: Final = 100
USER_AGENT: Final = "HackerRank-Solutions-GitHub-Action/1.0"
PROBLEM_STATEMENT_MARKER: Final = "<!-- synced-problem-statement -->"

LANGUAGE_EXTENSIONS: Final[dict[str, str]] = {
    "bash": "sh",
    "c": "c",
    "cpp": "cpp",
    "cpp14": "cpp",
    "cpp17": "cpp",
    "c++": "cpp",
    "c++14": "cpp",
    "c++17": "cpp",
    "csharp": "cs",
    "c#": "cs",
    "go": "go",
    "golang": "go",
    "java": "java",
    "java8": "java",
    "java15": "java",
    "javascript": "js",
    "js": "js",
    "kotlin": "kt",
    "php": "php",
    "python": "py",
    "python2": "py",
    "python3": "py",
    "python 3": "py",
    "ruby": "rb",
    "rust": "rs",
    "scala": "scala",
    "swift": "swift",
    "typescript": "ts",
    "sql": "sql",
    "haskell": "hs",
    "r": "r",
    "dart": "dart",
    "perl": "pl",
    "lua": "lua",
    "groovy": "groovy",
}

JsonValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | dict[str, "JsonValue"]
    | list["JsonValue"]
)


@dataclass(frozen=True)
class Submission:
    """The accepted-submission fields required for saving source code."""

    submission_id: int
    language: str
    title: str
    title_slug: str


class HackerRankSyncError(RuntimeError):
    """Raised when HackerRank data cannot be safely retrieved or validated."""


def get_required_environment_value(name: str) -> str:
    """Return a non-empty required environment variable without exposing its value."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise HackerRankSyncError(f"Missing required environment variable: {name}")
    return value


def create_headers(cookie: str) -> dict[str, str]:
    """Create headers for the authenticated HackerRank REST API."""
    return {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "Referer": f"{HACKERRANK_BASE_URL}/",
        "Cookie": cookie,
    }


def request_json(path: str, cookie: str, query: dict[str, int] | None = None) -> JsonValue:
    """Run an authenticated HackerRank request and validate its JSON envelope."""
    query_string = f"?{urlencode(query)}" if query else ""
    request = Request(
        f"{HACKERRANK_BASE_URL}{path}{query_string}",
        headers=create_headers(cookie),
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise HackerRankSyncError(
            f"HackerRank request failed with HTTP status {error.code}. "
            "Verify the HACKERRANK_COOKIE secret and retry."
        ) from error
    except URLError as error:
        raise HackerRankSyncError("Could not connect to HackerRank. Retry the workflow later.") from error
    except json.JSONDecodeError as error:
        raise HackerRankSyncError("HackerRank returned an invalid response.") from error

    if not isinstance(payload, (dict, list)):
        raise HackerRankSyncError("HackerRank returned an unexpected response format.")
    return payload


def parse_submission(value: object) -> Submission | None:
    """Return a valid accepted submission, or ignore unusable API data."""
    if not isinstance(value, dict) or value.get("status") != "Accepted":
        return None
    submission_id = value.get("id")
    if isinstance(submission_id, int) and submission_id > 0:
        normalized_submission_id = submission_id
    elif isinstance(submission_id, str) and submission_id.isdigit() and int(submission_id) > 0:
        normalized_submission_id = int(submission_id)
    else:
        return None

    challenge = value.get("challenge")
    if isinstance(challenge, dict):
        title = challenge.get("name")
        title_slug = challenge.get("slug")
    else:
        title = value.get("challenge_name")
        title_slug = value.get("challenge_slug")
    language = value.get("language") or value.get("lang")
    if not isinstance(title, str) or not isinstance(title_slug, str) or not isinstance(language, str):
        return None
    normalized_language = language.strip().lower()
    if not title.strip() or not title_slug.strip() or normalized_language not in LANGUAGE_EXTENSIONS:
        return None
    return Submission(normalized_submission_id, normalized_language, title.strip(), title_slug.strip())


def get_models(payload: JsonValue) -> list[dict[str, JsonValue]]:
    """Extract HackerRank's list-model response while rejecting malformed data."""
    if not isinstance(payload, dict):
        return []
    models = payload.get("models")
    if not isinstance(models, list):
        return []
    return [model for model in models if isinstance(model, dict)]


def get_accepted_submissions(cookie: str) -> list[Submission]:
    """Get the newest accepted submission for every challenge and language."""
    accepted: dict[tuple[str, str], Submission] = {}
    offset = 0
    while True:
        payload = request_json(SUBMISSIONS_PATH, cookie, {"offset": offset, "limit": PAGE_SIZE})
        models = get_models(payload)
        if not models:
            break
        for model in models:
            submission = parse_submission(model)
            if submission is None:
                continue
            key = (submission.title_slug, submission.language)
            existing = accepted.get(key)
            if existing is None or submission.submission_id > existing.submission_id:
                accepted[key] = submission
        if len(models) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return list(accepted.values())


def unwrap_model(payload: JsonValue) -> dict[str, JsonValue] | None:
    """Return the object containing challenge or submission fields."""
    if not isinstance(payload, dict):
        return None
    for key in ("model", "submission", "challenge", "data"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def extract_submission_code(payload: JsonValue) -> str | None:
    """Return source code from a submission-detail response."""
    model = unwrap_model(payload)
    if model is None:
        return None
    for key in ("code", "source_code", "source", "code_content"):
        code = model.get(key)
        if isinstance(code, str) and code.strip():
            return code
    return None


def get_submission_code(submission: Submission, cookie: str) -> str | None:
    """Get source code for one accepted submission, when it is accessible."""
    path = (
        f"/rest/contests/master/challenges/{submission.title_slug}/submissions/"
        f"{submission.submission_id}"
    )
    return extract_submission_code(request_json(path, cookie))


def extract_problem_statement(payload: JsonValue) -> str | None:
    """Return an accessible challenge statement from a challenge response."""
    model = unwrap_model(payload)
    if model is None:
        return None
    for key in ("body", "description", "problem_statement", "content"):
        statement = model.get(key)
        if isinstance(statement, str) and statement.strip():
            return statement
    return None


def get_problem_statement(submission: Submission, cookie: str) -> str | None:
    """Return a challenge statement when HackerRank exposes it."""
    path = f"/rest/contests/master/challenges/{submission.title_slug}"
    try:
        return extract_problem_statement(request_json(path, cookie))
    except HackerRankSyncError:
        return None


def get_solution_path(submission: Submission) -> Path:
    """Create a safe, deterministic output path below the destination directory."""
    safe_slug = re.sub(r"[^a-z0-9-]+", "-", submission.title_slug.lower()).strip("-")
    if not safe_slug:
        raise HackerRankSyncError("HackerRank returned an unsafe challenge slug.")
    return DESTINATION_DIRECTORY / safe_slug / f"solution.{LANGUAGE_EXTENSIONS[submission.language]}"


def get_metadata_path(submission: Submission) -> Path:
    """Return the metadata path for a synced challenge."""
    return get_solution_path(submission).parent / "metadata.json"


def get_readme_path(submission: Submission) -> Path:
    """Return the generated README path for a synced challenge."""
    return get_solution_path(submission).parent / "README.md"


def load_synced_submission_id(path: Path, language: str) -> int | None:
    """Read the synced submission ID for one language, if valid metadata exists."""
    if not path.is_file():
        return None
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(metadata, dict) or not isinstance(metadata.get("submissions"), dict):
        return None
    submission_id = metadata["submissions"].get(language)
    return submission_id if isinstance(submission_id, int) else None


def write_problem_metadata(submission: Submission) -> bool:
    """Record source metadata without copying HackerRank content."""
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
        {
            "platform": "HackerRank",
            "title": submission.title,
            "titleSlug": submission.title_slug,
            "submissions": existing_submissions,
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
    if metadata_path.is_file() and metadata_path.read_text(encoding="utf-8") == content:
        return False
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def write_problem_readme(submission: Submission, problem_statement: str | None) -> bool:
    """Create a local challenge README with accessible statement content."""
    readme_path = get_readme_path(submission)
    source_link = f"{HACKERRANK_BASE_URL}/challenges/{submission.title_slug}/problem"
    if problem_statement is None:
        content = f"# {submission.title}\n\nHackerRank problem: {source_link}\n"
    else:
        content = (
            f"# {submission.title}\n\n{PROBLEM_STATEMENT_MARKER}\n\n"
            f"{problem_statement.rstrip()}\n\nSource: {source_link}\n"
        )
    if readme_path.is_file() and readme_path.read_text(encoding="utf-8") == content:
        return False
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def has_synced_problem_statement(path: Path) -> bool:
    """Return whether a challenge README contains downloaded content."""
    return path.is_file() and PROBLEM_STATEMENT_MARKER in path.read_text(encoding="utf-8")


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
        cookie = get_required_environment_value("HACKERRANK_COOKIE")
        submissions = get_accepted_submissions(cookie)
        updated_count = 0
        for submission in submissions:
            solution_path = get_solution_path(submission)
            metadata_path = get_metadata_path(submission)
            is_existing_submission = (
                load_synced_submission_id(metadata_path, submission.language) == submission.submission_id
            )
            if (
                is_existing_submission
                and solution_path.is_file()
                and has_synced_problem_statement(get_readme_path(submission))
            ):
                continue
            if not is_existing_submission or not solution_path.is_file():
                code = get_submission_code(submission, cookie)
                if code is None:
                    print(
                        f"Skipped unavailable source for {submission.title_slug} "
                        f"({submission.language}, submission {submission.submission_id})."
                    )
                    continue
                updated_count += write_solution(solution_path, code)
                updated_count += write_problem_metadata(submission)
            problem_statement = get_problem_statement(submission, cookie)
            if problem_statement is None:
                print(f"Problem statement unavailable for {submission.title_slug}.")
            updated_count += write_problem_readme(submission, problem_statement)
        print(f"Synchronized {updated_count} HackerRank solution file(s).")
        return 0
    except HackerRankSyncError as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
