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

  function setupBriefingPresentation(root) {
    const deck = root.querySelector("[data-briefing-presentation='true']");
    if (!deck || deck.dataset.briefingReady === "true") {
      return;
    }
    deck.dataset.briefingReady = "true";
    const slides = Array.from(deck.querySelectorAll("[data-briefing-slide]"));
    const current = deck.querySelector("[data-briefing-current]");
    const dots = Array.from(deck.querySelectorAll("[data-briefing-target]"));
    const prev = deck.querySelector("[data-briefing-prev]");
    const next = deck.querySelector("[data-briefing-next]");
    let index = 0;

    function show(nextIndex) {
      if (!slides.length) {
        return;
      }
      index = Math.max(0, Math.min(nextIndex, slides.length - 1));
      slides.forEach(function (slide, slideIndex) {
        const active = slideIndex === index;
        slide.classList.toggle("is-active", active);
        slide.setAttribute("aria-hidden", active ? "false" : "true");
      });
      dots.forEach(function (dot, dotIndex) {
        const active = dotIndex === index;
        dot.classList.toggle("is-active", active);
        dot.setAttribute("aria-current", active ? "step" : "false");
      });
      if (current) {
        current.textContent = String(index + 1);
      }
      if (prev) {
        prev.disabled = index === 0;
      }
      if (next) {
        next.disabled = index === slides.length - 1;
      }
    }

    if (prev) {
      prev.addEventListener("click", function () {
        show(index - 1);
      });
    }
    if (next) {
      next.addEventListener("click", function () {
        show(index + 1);
      });
    }
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        show(Number(dot.dataset.briefingTarget || "0"));
      });
    });
    deck.addEventListener("keydown", function (event) {
      if (event.key === "ArrowRight") {
        event.preventDefault();
        show(index + 1);
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        show(index - 1);
      }
    });
    show(0);
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
      setupBriefingPresentation(resultPanel);
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
  setupBriefingPresentation(document);
  window.setTimeout(function () {
    rerunActiveTab();
  }, 0);
})();
