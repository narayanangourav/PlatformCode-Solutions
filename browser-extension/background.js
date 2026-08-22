const extensionApi = globalThis.browser ?? globalThis.chrome;
const LEETCODE_COOKIE_URL = "https://leetcode.com/";
const COOKIE_NAMES = Object.freeze({
  session: "LEETCODE_SESSION",
  csrf: "csrftoken",
});
const GITHUB_API_URL = "https://api.github.com";
const GITHUB_API_VERSION = "2022-11-28";
const REPOSITORY_PATTERN = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const WORKFLOW_PATTERN = /^[A-Za-z0-9_.-]+$/;

function callExtensionApi(apiFunction, args) {
  if (globalThis.browser) {
    return apiFunction(...args);
  }
  return new Promise((resolve, reject) => {
    apiFunction(...args, (result) => {
      const runtimeError = extensionApi.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }
      resolve(result);
    });
  });
}

function asErrorMessage(error) {
  return error instanceof Error ? error.message : "The requested operation failed.";
}

async function getCookie(name) {
  const cookie = await callExtensionApi(extensionApi.cookies.get.bind(extensionApi.cookies), [
    { name, url: LEETCODE_COOKIE_URL },
  ]);
  return cookie?.value?.trim() ? cookie : null;
}

async function getSessionStatus() {
  const [session, csrf] = await Promise.all([
    getCookie(COOKIE_NAMES.session),
    getCookie(COOKIE_NAMES.csrf),
  ]);

  return {
    hasSessionCookie: session !== null,
    hasCsrfCookie: csrf !== null,
    ready: session !== null && csrf !== null,
  };
}

function validateDispatchSettings(settings) {
  if (!settings || !REPOSITORY_PATTERN.test(settings.repository ?? "")) {
    throw new Error("Enter a repository in owner/repository format.");
  }
  if (!WORKFLOW_PATTERN.test(settings.workflow ?? "")) {
    throw new Error("Enter a workflow filename such as sync-leetcode.yml.");
  }
  if (!/^[A-Za-z0-9_.\/-]+$/.test(settings.ref ?? "")) {
    throw new Error("Enter a valid branch or tag name.");
  }
  if (typeof settings.token !== "string" || !settings.token.trim()) {
    throw new Error("Enter a GitHub token with Actions: write permission.");
  }
}

async function dispatchWorkflow(settings) {
  validateDispatchSettings(settings);
  const [owner, repository] = settings.repository.split("/");
  const workflow = encodeURIComponent(settings.workflow);
  const response = await fetch(
    `${GITHUB_API_URL}/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repository)}/actions/workflows/${workflow}/dispatches`,
    {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${settings.token.trim()}`,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: settings.ref }),
    },
  );

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error("GitHub rejected the token. Use a token with Actions: write permission for this repository.");
    }
    if (response.status === 404) {
      throw new Error("GitHub could not find the repository or workflow file.");
    }
    throw new Error(`GitHub returned HTTP ${response.status} while starting the workflow.`);
  }

  return { dispatched: true };
}

async function handleMessage(message) {
  if (message?.type === "checkLeetCodeSession") {
    return getSessionStatus();
  }
  if (message?.type === "dispatchSync") {
    return dispatchWorkflow(message.settings);
  }
  throw new Error("Unsupported extension message.");
}

extensionApi.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  handleMessage(message)
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({ ok: false, error: asErrorMessage(error) }));
  return true;
});
