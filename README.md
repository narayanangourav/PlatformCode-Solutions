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
browser-extension/    # Optional cross-browser workflow trigger
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
2. Set `LEETCODE_CSRF_TOKEN` to the value of the `csrftoken` cookie and `LEETCODE_SESSION` to the value of the matching `LEETCODE_SESSION` cookie from your own signed-in browser session.
3. Keep `.env` private. It is excluded from Git because these values grant access to your account session.

Never commit or share real cookie values. If a value is exposed, sign out of LeetCode or revoke the affected session and create a new one.

`LEETCODE_SESSION` may expire. When it does, copy the new cookie values and update the two GitHub repository secrets; do not change the workflow file.

## Run the sync locally with Podman

1. Copy `.env.example` to `.env` and provide the two cookie values.
2. Build and run the sync:

   ```bash
   podman compose run --rm leetcode-sync
   ```

The container has no network ports and runs as an unprivileged user. Only `leetcode-solutions/` is mounted read-write, so synced files remain in your working tree. `.env` is excluded from both Git and the container build context.

## Releases

Create a `v*` release tag, such as `v1.0.0`, to run the release workflow. You can either publish a release from **Releases → Draft a new release** in the GitHub web UI, or push a tag from your terminal:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow uses four dependent jobs: installs dependencies, runs tests, builds and publishes the release image, then creates or updates the matching GitHub Release with a source bundle containing the sync tooling. Existing solutions and local credentials are not included in the bundle.

### Public container images

The workflows publish two GitHub Container Registry images:

- `ghcr.io/<owner>/leetcode-solutions-sync:autosync-latest` is rebuilt after successful sync-workflow tests. Each build also receives an immutable `autosync-sha-<commit>` tag.
- `ghcr.io/<owner>/leetcode-solutions-release:release-<tag>` is published for each release tag, with a `release-latest` tag as well.

Replace `<owner>` with the GitHub account or organization that owns this repository. Public GHCR images can be pulled without authentication.

GitHub publishes a newly created container package as private by default. After each image name is published for the first time, open the package from your GitHub profile or organization **Packages** page and set **Package settings → Change visibility → Public**. That visibility setting persists for later image tags.

## Sync accepted submissions

The workflow at `.github/workflows/sync-leetcode.yml` runs manually from **Actions → Sync LeetCode Solutions → Run workflow**, after every push, and at 12:00 AM India Standard Time on the 1st, 10th, 20th, and 30th of each month (6:30 PM UTC on the preceding day). Before the first run, add these repository secrets under **Settings → Secrets and variables → Actions**:

- `LEETCODE_CSRF_TOKEN`: the value of your browser's `csrftoken` cookie.
- `LEETCODE_SESSION`: the value of your browser's `LEETCODE_SESSION` cookie.

The workflow uses the `github.token` permission to commit changes. Set **Settings → Actions → General → Workflow permissions** to **Read and write permissions**.

To disable only the weekly cron run, create the repository variable `LEETCODE_SYNC_CRON_DISABLED` with the value `true` under **Settings → Secrets and variables → Actions → Variables**. Manual and push-triggered syncs remain enabled. Delete the variable or change its value to re-enable the schedule.

### Optional browser extension

The `browser-extension/` folder contains an optional Manifest V3 extension for Chromium browsers and Firefox. It checks whether the current browser has the LeetCode cookies and can manually trigger `sync-leetcode.yml` in a fork. It never copies cookies to GitHub, stores them, or changes repository secrets. The GitHub schedule remains the automatic sync mechanism.

Each fork owner must still enable Actions, add their own `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` repository secrets, and create a fine-grained GitHub token with **Actions: Read and write** if they want to use the extension's manual trigger. Installation and browser-specific instructions are in [browser-extension/README.md](browser-extension/README.md).

### Sync flow

1. The `install-dependencies` job checks out the repository, installs Python 3.13, and installs the requirements.
2. The `test-sync-script` job runs the sync-script unit tests after dependencies install successfully.
3. The `build-container` job builds and publishes the public sync container after tests pass.
4. The `sync-leetcode` job runs `scripts/sync_leetcode.py` with the two secrets available only as environment variables.
5. The script requests the authenticated submission history, keeps the latest accepted submission for each problem and language, and retrieves its source code.
6. Each problem accessible to your LeetCode account receives a `README.md` with its statement, a `metadata.json`, and its latest accepted source file for each language under `leetcode-solutions/<problem-slug>/`.
7. Git stages only `leetcode-solutions/`. If nothing changed, it ends successfully; otherwise, it creates and pushes a `Sync LeetCode solutions` commit.

On the first run, the script paginates through all accessible accepted submissions. Later runs use `metadata.json` to avoid downloading source code for submission IDs that are already synchronized. If LeetCode does not expose the full progress history for an account, the script falls back to the recent accepted-submission list instead of failing on the older global submission response. It stores statements only when they are accessible to your account; hidden test cases are not available for export. It uses Python's standard library, so `requirements.txt` has no external dependencies.

## Adding a solution

1. Add one Python file to `code/` using a descriptive problem name.
2. Keep the public method signature compatible with LeetCode.
3. Verify the solution against the problem's examples and edge cases before committing.
