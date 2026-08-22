# LeetCode Solutions Sync browser extension

This optional Manifest V3 extension checks whether the current browser has the LeetCode cookies and can manually dispatch the repository's `sync-leetcode.yml` workflow.

It does not upload or store `LEETCODE_SESSION` or `csrftoken`. The GitHub workflow continues to read `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` from repository secrets. Configure those secrets once in the fork before using the extension.

## Install locally

### Chromium browsers

1. Open `chrome://extensions` (or the equivalent page in Edge, Brave, or Opera).
2. Enable **Developer mode**.
3. Select **Load unpacked** and choose this `browser-extension/` folder.

### Firefox

1. Open `about:debugging#/runtime/this-firefox`.
2. Select **Load Temporary Add-on**.
3. Choose `browser-extension/manifest.json`.

## Use

1. Sign in to `https://leetcode.com`.
2. Open the extension and select **Check browser session**.
3. Enter the fork as `owner/repository`.
4. Create a fine-grained GitHub token with **Actions: Read and write** for that repository. The token is used only for the dispatch request and is not saved.
5. Select **Start sync**.

The repository's GitHub cron remains the automatic scheduler. The extension is an explicit browser-side trigger and session check; it cannot copy cookies into GitHub secrets.

## Security

The extension only checks the presence of the two LeetCode cookies. It never sends cookie values to GitHub, stores them in extension storage, or writes them to the repository. If the GitHub secrets expire, update them manually in the fork's Actions secrets settings.
