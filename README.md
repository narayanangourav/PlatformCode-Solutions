# LeetCode Solutions

A personal collection of Python solutions to LeetCode problems. Each solution follows LeetCode's expected `Solution` class format, so it can be copied directly into the online editor.

## Repository structure

```text
code/
  <problem-name>.py   # One solution per LeetCode problem
.github/workflows/
  sync-leetcode.yml   # Manually triggered sync workflow
scripts/
  sync_leetcode.py    # Authenticated LeetCode sync script
leetcode-solutions/
  <problem-slug>/     # README, metadata, and synced accepted source files
.env.example          # Optional local LeetCode session configuration
```

## Requirements

- Python 3.10 or later

The submitted solution files do not require third-party packages. LeetCode supplies the runtime types and invokes the appropriate method when a solution is submitted.

## Using a solution locally

1. Open a file in `code/` and review the `Solution` class and its method signature.
2. Copy the class into the matching LeetCode problem's editor, or create a small local test harness that calls the method.
3. Run your harness with Python:

   ```bash
   python path/to/your_test.py
   ```

## Optional LeetCode session configuration

The environment variables are only needed by local tooling that accesses an authenticated LeetCode session; the solution files themselves do not use them.

1. Copy `.env.example` to `.env`.
2. Set `csrftoken` and `LEETCODE_SESSION` to the corresponding cookie values from your own signed-in LeetCode browser session.
3. Keep `.env` private. It is excluded from Git because these values grant access to your account session.

Never commit or share real cookie values. If a value is exposed, sign out of LeetCode or revoke the affected session and create a new one.

`LEETCODE_SESSION` may expire. When it does, copy the new cookie values and update the two GitHub repository secrets; do not change the workflow file.

## Sync accepted submissions

The workflow at `.github/workflows/sync-leetcode.yml` runs manually from **Actions → Sync LeetCode Solutions → Run workflow**, after every push, and every Sunday at 12:00 AM India Standard Time (Saturday 6:30 PM UTC). Before the first run, add these repository secrets under **Settings → Secrets and variables → Actions**:

- `LEETCODE_CSRF_TOKEN`: the value of your browser's `csrftoken` cookie.
- `LEETCODE_SESSION`: the value of your browser's `LEETCODE_SESSION` cookie.

The workflow uses the `github.token` permission to commit changes. Set **Settings → Actions → General → Workflow permissions** to **Read and write permissions**.

To disable only the weekly cron run, create the repository variable `LEETCODE_SYNC_CRON_DISABLED` with the value `true` under **Settings → Secrets and variables → Actions → Variables**. Manual and push-triggered syncs remain enabled. Delete the variable or change its value to re-enable the schedule.

### Sync flow

1. The `test-sync-script` job checks out the repository, installs Python 3.13, and runs the sync-script unit tests.
2. Only after those tests pass does the `sync-leetcode` job start.
3. The sync job runs `scripts/sync_leetcode.py` with the two secrets available only as environment variables.
4. The script requests the authenticated submission history, keeps the latest accepted submission for each problem and language, and retrieves its source code.
5. Each problem accessible to your LeetCode account receives a `README.md` with its statement, a `metadata.json`, and its latest accepted source file for each language under `leetcode-solutions/<problem-slug>/`.
6. Git stages only `leetcode-solutions/`. If nothing changed, it ends successfully; otherwise, it creates and pushes a `Sync LeetCode solutions` commit.

On the first run, the script paginates through all accessible accepted submissions. Later runs use `metadata.json` to avoid downloading source code for submission IDs that are already synchronized. It stores statements only when they are accessible to your account; hidden test cases are not available for export. It uses Python's standard library, so `requirements.txt` has no external dependencies.

## Adding a solution

1. Add one Python file to `code/` using a descriptive problem name.
2. Keep the public method signature compatible with LeetCode.
3. Verify the solution against the problem's examples and edge cases before committing.
