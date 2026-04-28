(function () {
  const key = "codexray.recentPaths.v1";
  const themeKey = "codexray.theme.v1";
  const form = document.getElementById("analysis-form");
  const input = document.getElementById("path-input");
  const select = document.getElementById("recent-paths");
  const resultPanel = document.getElementById("result-panel");
  const statusText = document.getElementById("status-text");
  const themeToggle = document.getElementById("theme-toggle");
  const tabs = Array.from(document.querySelectorAll(".tab-button"));
  let activeTab = tabs.find((tab) => tab.classList.contains("is-active")) || tabs[0];

  function preferredTheme() {
    const stored = localStorage.getItem(themeKey);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    themeToggle.textContent = theme === "dark" ? "Light" : "Dark";
    themeToggle.setAttribute("aria-label", "Switch to " + (theme === "dark" ? "light" : "dark") + " mode");
  }

  function readPaths() {
    try {
      const parsed = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : [];
    } catch (_error) {
      return [];
    }
  }

  function writePaths(paths) {
    localStorage.setItem(key, JSON.stringify(paths.slice(0, 5)));
  }

  function renderOptions() {
    const paths = readPaths();
    select.innerHTML = '<option value="">Recent</option>';
    for (const path of paths) {
      const option = document.createElement("option");
      option.value = path;
      option.textContent = path;
      select.appendChild(option);
    }
  }

  function rememberPath() {
    const path = input.value.trim();
    if (!path) {
      return;
    }
    const next = [path].concat(readPaths().filter((item) => item !== path));
    writePaths(next);
    renderOptions();
  }

  function setStatus(text) {
    statusText.textContent = text;
  }

  function setActiveTab(tab) {
    if (!tab || !tab.classList.contains("tab-button")) {
      return;
    }
    activeTab = tab;
    for (const item of tabs) {
      const isActive = item === tab;
      item.classList.toggle("is-active", isActive);
      item.setAttribute("aria-current", isActive ? "page" : "false");
    }
  }

  function rerunActiveTab() {
    if (activeTab) {
      activeTab.click();
    }
  }

  select.addEventListener("change", function () {
    if (select.value) {
      input.value = select.value;
      rerunActiveTab();
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    rememberPath();
    const tab = event.detail.elt.closest(".tab-button");
    if (tab) {
      setActiveTab(tab);
      setStatus("Running " + tab.dataset.tab + "...");
    } else if (event.detail.elt.matches(".review-run-form")) {
      const button = event.detail.elt.querySelector(".primary-action");
      if (button) {
        button.disabled = true;
        button.textContent = "Starting review...";
      }
      setStatus("Starting AI review...");
    } else {
      setStatus("Refreshing...");
    }
    resultPanel.classList.add("is-loading");
  });

  document.body.addEventListener("htmx:afterRequest", function (event) {
    resultPanel.classList.remove("is-loading");
    if (event.detail.successful) {
      setStatus("Ready");
    } else {
      setStatus("Request failed");
    }
  });

  document.body.addEventListener("htmx:responseError", function () {
    resultPanel.classList.remove("is-loading");
    setStatus("Request failed");
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    rerunActiveTab();
  });

  themeToggle.addEventListener("click", function () {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(themeKey, next);
    applyTheme(next);
  });

  applyTheme(preferredTheme());
  renderOptions();
  setActiveTab(activeTab);
  window.setTimeout(function () {
    rerunActiveTab();
  }, 0);
})();
