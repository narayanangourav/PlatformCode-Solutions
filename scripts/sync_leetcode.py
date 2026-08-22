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
PROBLEM_STATEMENT_MARKER: Final = "<!-- synced-problem-statement -->"

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
query submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
    lastKey
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

SOLVED_QUESTIONS_QUERY: Final = """
query userProgressQuestionList($filters: UserProgressQuestionListInput) {
  userProgressQuestionList(filters: $filters) {
    totalNum
    questions {
      title
      titleSlug
    }
  }
}
"""

QUESTION_SUBMISSIONS_QUERY: Final = """
query submissionList($offset: Int!, $limit: Int!, $questionSlug: String!) {
  questionSubmissionList(
    offset: $offset
    limit: $limit
    questionSlug: $questionSlug
  ) {
    submissions {
      id
      statusDisplay
      lang
    }
  }
}
"""

USER_STATUS_QUERY: Final = """
query currentUser {
  userStatus {
    isSignedIn
    username
  }
}
"""

RECENT_ACCEPTED_QUERY: Final = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
  }
}
"""

QUESTION_DETAILS_QUERY: Final = """
query questionDetails($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    content
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


@dataclass(frozen=True)
class SolvedProblem:
    """A solved problem used to query its authenticated submissions."""

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
    query: str, variables: dict[str, object], session: str, csrf_token: str
) -> dict[str, object]:
    """Run a GraphQL request and reject malformed or error responses."""
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = Request(LEETCODE_GRAPHQL_URL, body, create_headers(session, csrf_token))

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise LeetCodeSyncError(
            f"LeetCode request failed with HTTP status {error.code}. "
            "Verify both GitHub secrets use fresh cookie values and retry."
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
    if isinstance(submission_id, int) and submission_id > 0:
        normalized_submission_id = submission_id
    elif isinstance(submission_id, str) and submission_id.isdigit():
        normalized_submission_id = int(submission_id)
    else:
        return None
    if not isinstance(language, str) or not isinstance(title, str) or not isinstance(title_slug, str):
        return None
    normalized_language = language.lower()
    if not title_slug or normalized_language not in LANGUAGE_EXTENSIONS:
        return None
    return Submission(normalized_submission_id, normalized_language, title, title_slug)


def get_accepted_submissions(session: str, csrf_token: str) -> list[Submission]:
    """Get the latest accepted submission for every problem and language."""
    accepted: dict[tuple[str, str], Submission] = {}
    offset = 0
    last_key: str | None = None

    while True:
        try:
            data = request_graphql(
                SUBMISSIONS_QUERY,
                {"offset": offset, "limit": PAGE_SIZE, "lastKey": last_key, "questionSlug": None},
                session,
                csrf_token,
            )
        except LeetCodeSyncError:
            return get_accepted_submissions_by_problem(session, csrf_token)
        submission_list = data.get("submissionList")
        if not isinstance(submission_list, dict):
            return get_accepted_submissions_by_problem(session, csrf_token)
        submissions = submission_list.get("submissions")
        if not isinstance(submissions, list):
            return get_accepted_submissions_by_problem(session, csrf_token)

        for item in submissions:
            submission = parse_submission(item)
            if submission is not None:
                accepted.setdefault((submission.title_slug, submission.language), submission)

        has_next = submission_list.get("hasNext")
        if not isinstance(has_next, bool):
            return get_accepted_submissions_by_problem(session, csrf_token)
        if not has_next:
            break
        response_last_key = submission_list.get("lastKey")
        if response_last_key is not None and not isinstance(response_last_key, str):
            return get_accepted_submissions_by_problem(session, csrf_token)
        last_key = response_last_key
        offset += PAGE_SIZE

    return list(accepted.values())


def get_solved_problems(session: str, csrf_token: str) -> list[SolvedProblem]:
    """Get solved problems for the fallback per-problem submission query."""
    problems_by_slug: dict[str, SolvedProblem] = {}
    skip = 0
    page_limit = 100

    while True:
        data = request_graphql(
            SOLVED_QUESTIONS_QUERY,
            {
                "filters": {
                    "questionStatus": "SOLVED",
                    "skip": skip,
                    "limit": page_limit,
                }
            },
            session,
            csrf_token,
        )
        result = data.get("userProgressQuestionList")
        if not isinstance(result, dict):
            raise LeetCodeSyncError("LeetCode did not return the solved-problem list.")
        question_values = result.get("questions")
        if not isinstance(question_values, list):
            raise LeetCodeSyncError("LeetCode returned an invalid solved-problem list.")

        for value in question_values:
            if not isinstance(value, dict):
                continue
            title = value.get("title")
            title_slug = value.get("titleSlug")
            if isinstance(title, str) and isinstance(title_slug, str) and title and title_slug:
                problems_by_slug.setdefault(title_slug, SolvedProblem(title, title_slug))

        total = result.get("totalNum")
        if not question_values or len(question_values) < page_limit:
            break
        if isinstance(total, int) and skip + len(question_values) >= total:
            break
        skip += len(question_values)

    return list(problems_by_slug.values())


def get_problem_accepted_submissions(
    problem: SolvedProblem, session: str, csrf_token: str
) -> list[Submission]:
    """Get accepted submissions for one solved problem."""
    accepted: dict[str, Submission] = {}
    offset = 0

    while True:
        data = request_graphql(
            QUESTION_SUBMISSIONS_QUERY,
            {
                "offset": offset,
                "limit": PAGE_SIZE,
                "questionSlug": problem.title_slug,
            },
            session,
            csrf_token,
        )
        submission_list = data.get("questionSubmissionList")
        if not isinstance(submission_list, dict):
            break
        submissions = submission_list.get("submissions")
        if not isinstance(submissions, list):
            break
        for value in submissions:
            if not isinstance(value, dict) or value.get("statusDisplay") != "Accepted":
                continue
            submission_id = value.get("id")
            language = value.get("lang")
            if isinstance(submission_id, int) and submission_id > 0:
                normalized_submission_id = submission_id
            elif isinstance(submission_id, str) and submission_id.isdigit():
                normalized_submission_id = int(submission_id)
            else:
                continue
            if not isinstance(language, str):
                continue
            normalized_language = language.lower()
            if normalized_language in LANGUAGE_EXTENSIONS:
                accepted.setdefault(
                    normalized_language,
                    Submission(
                        normalized_submission_id,
                        normalized_language,
                        problem.title,
                        problem.title_slug,
                    ),
                )
        if len(submissions) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return list(accepted.values())


def get_current_username(session: str, csrf_token: str) -> str:
    """Return the authenticated username for the recent-submissions fallback."""
    data = request_graphql(USER_STATUS_QUERY, {}, session, csrf_token)
    user_status = data.get("userStatus")
    if not isinstance(user_status, dict) or user_status.get("isSignedIn") is not True:
        raise LeetCodeSyncError("LeetCode authentication is not active. Refresh both GitHub secrets and retry.")
    username = user_status.get("username")
    if not isinstance(username, str) or not username.strip():
        raise LeetCodeSyncError("LeetCode did not return the authenticated username.")
    return username


def get_recent_solved_problems(session: str, csrf_token: str) -> list[SolvedProblem]:
    """Get the recent accepted problems available to accounts without progress history."""
    username = get_current_username(session, csrf_token)
    data = request_graphql(
        RECENT_ACCEPTED_QUERY,
        {"username": username, "limit": PAGE_SIZE},
        session,
        csrf_token,
    )
    values = data.get("recentAcSubmissionList")
    if not isinstance(values, list):
        raise LeetCodeSyncError("LeetCode returned an invalid recent-submission list.")
    problems_by_slug: dict[str, SolvedProblem] = {}
    for value in values:
        if not isinstance(value, dict):
            continue
        title = value.get("title")
        title_slug = value.get("titleSlug")
        if isinstance(title, str) and isinstance(title_slug, str) and title and title_slug:
            problems_by_slug.setdefault(title_slug, SolvedProblem(title, title_slug))
    return list(problems_by_slug.values())


def get_accepted_submissions_by_problem(session: str, csrf_token: str) -> list[Submission]:
    """Recover accepted submissions when the global submission list is unavailable."""
    try:
        problems = get_solved_problems(session, csrf_token)
    except LeetCodeSyncError:
        problems = []
    if not problems:
        print("LeetCode history is unavailable; syncing the recent accepted submissions instead.")
        problems = get_recent_solved_problems(session, csrf_token)

    accepted: list[Submission] = []
    for problem in problems:
        accepted.extend(get_problem_accepted_submissions(problem, session, csrf_token))
    return accepted


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


def get_problem_statement(submission: Submission, session: str, csrf_token: str) -> str | None:
    """Return a problem statement when the authenticated account can access it."""
    data = request_graphql(
        QUESTION_DETAILS_QUERY,
        {"titleSlug": submission.title_slug},
        session,
        csrf_token,
    )
    question = data.get("question")
    if not isinstance(question, dict):
        return None
    content = question.get("content")
    return content if isinstance(content, str) and content.strip() else None


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


def write_problem_readme(submission: Submission, problem_statement: str | None) -> bool:
    """Create a local problem README with accessible statement content."""
    readme_path = get_readme_path(submission)
    source_link = f"https://leetcode.com/problems/{submission.title_slug}/"
    content = f"# {submission.title}\n\nLeetCode problem: {source_link}\n"
    if problem_statement is not None:
        content = (
            f"# {submission.title}\n\n{PROBLEM_STATEMENT_MARKER}\n\n"
            f"{problem_statement.rstrip()}\n\nSource: {source_link}\n"
        )
    if readme_path.is_file() and readme_path.read_text(encoding="utf-8") == content:
        return False
    readme_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def has_synced_problem_statement(path: Path) -> bool:
    """Return whether a problem README contains successfully downloaded content."""
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
        session = get_required_environment_value("LEETCODE_SESSION")
        csrf_token = get_required_environment_value("LEETCODE_CSRF_TOKEN")
        submissions = get_accepted_submissions(session, csrf_token)
        updated_count = 0
        for submission in submissions:
            solution_path = get_solution_path(submission)
            metadata_path = get_metadata_path(submission)
            is_existing_submission = (
                load_synced_submission_id(metadata_path, submission.language) == submission.submission_id
            )
            if is_existing_submission and has_synced_problem_statement(get_readme_path(submission)):
                continue
            if not is_existing_submission:
                code = get_submission_code(submission, session, csrf_token)
                if code is None:
                    print(
                        f"Skipped unavailable source for {submission.title_slug} "
                        f"({submission.language}, submission {submission.submission_id})."
                    )
                    continue
                updated_count += write_solution(solution_path, code)
                updated_count += write_problem_metadata(submission)
            problem_statement = get_problem_statement(submission, session, csrf_token)
            if problem_statement is None:
                print(f"Problem statement unavailable for {submission.title_slug}.")
            updated_count += write_problem_readme(submission, problem_statement)
        print(f"Synchronized {updated_count} solution file(s).")
        return 0
    except LeetCodeSyncError as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
