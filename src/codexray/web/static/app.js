(function () {
  const key = "codexray.recentPaths.v1";
  const form = document.getElementById("analysis-form");
  const input = document.getElementById("path-input");
  const select = document.getElementById("recent-paths");

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

  select.addEventListener("change", function () {
    if (select.value) {
      input.value = select.value;
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function () {
    rememberPath();
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
  });

  renderOptions();
})();
