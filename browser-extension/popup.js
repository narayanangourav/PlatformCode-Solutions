const extensionApi = globalThis.browser ?? globalThis.chrome;
const DEFAULT_SETTINGS = Object.freeze({
  repository: "",
  workflow: "sync-leetcode.yml",
  ref: "main",
});

const elements = Object.freeze({
  repository: document.getElementById("repository"),
  workflow: document.getElementById("workflow"),
  ref: document.getElementById("ref"),
  token: document.getElementById("token"),
  checkSession: document.getElementById("check-session"),
  runSync: document.getElementById("run-sync"),
  sessionStatus: document.getElementById("session-status"),
  workflowStatus: document.getElementById("workflow-status"),
});

function sendExtensionMessage(message) {
  if (globalThis.browser) {
    return extensionApi.runtime.sendMessage(message);
  }
  return new Promise((resolve, reject) => {
    extensionApi.runtime.sendMessage(message, (response) => {
      const runtimeError = extensionApi.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }
      resolve(response);
    });
  });
}

function storageGet(defaults) {
  if (globalThis.browser) {
    return extensionApi.storage.local.get(defaults);
  }
  return new Promise((resolve, reject) => {
    extensionApi.storage.local.get(defaults, (result) => {
      const runtimeError = extensionApi.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }
      resolve(result);
    });
  });
}

function storageSet(values) {
  if (globalThis.browser) {
    return extensionApi.storage.local.set(values);
  }
  return new Promise((resolve, reject) => {
    extensionApi.storage.local.set(values, () => {
      const runtimeError = extensionApi.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }
      resolve();
    });
  });
}

function setStatus(element, message) {
  element.textContent = message;
}

function sendMessage(message) {
  return sendExtensionMessage(message).then((response) => {
    if (!response?.ok) {
      throw new Error(response?.error ?? "The extension request failed.");
    }
    return response.result;
  });
}

async function loadSettings() {
  const settings = await storageGet(DEFAULT_SETTINGS);
  elements.repository.value = settings.repository ?? DEFAULT_SETTINGS.repository;
  elements.workflow.value = settings.workflow ?? DEFAULT_SETTINGS.workflow;
  elements.ref.value = settings.ref ?? DEFAULT_SETTINGS.ref;
}

async function saveSettings() {
  await storageSet({
    repository: elements.repository.value.trim(),
    workflow: elements.workflow.value.trim(),
    ref: elements.ref.value.trim(),
  });
}

async function checkSession() {
  elements.checkSession.disabled = true;
  setStatus(elements.sessionStatus, "Checking browser cookies...");
  try {
    const status = await sendMessage({ type: "checkLeetCodeSession" });
    if (status.ready) {
      setStatus(elements.sessionStatus, "LeetCode cookies are present in this browser.");
    } else {
      setStatus(elements.sessionStatus, "Open leetcode.com and sign in before syncing.");
    }
  } catch (error) {
    setStatus(elements.sessionStatus, error.message);
  } finally {
    elements.checkSession.disabled = false;
  }
}

async function runSync() {
  elements.runSync.disabled = true;
  setStatus(elements.workflowStatus, "Starting GitHub Actions workflow...");
  try {
    await saveSettings();
    await sendMessage({
      type: "dispatchSync",
      settings: {
        repository: elements.repository.value.trim(),
        workflow: elements.workflow.value.trim(),
        ref: elements.ref.value.trim(),
        token: elements.token.value,
      },
    });
    elements.token.value = "";
    setStatus(elements.workflowStatus, "Workflow started. GitHub Actions will use the repository secrets.");
  } catch (error) {
    setStatus(elements.workflowStatus, error.message);
  } finally {
    elements.runSync.disabled = false;
  }
}

elements.checkSession.addEventListener("click", checkSession);
elements.runSync.addEventListener("click", runSync);
loadSettings().catch((error) => setStatus(elements.workflowStatus, error.message));
