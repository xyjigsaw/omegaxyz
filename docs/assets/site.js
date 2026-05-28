(function () {
  const root = document.documentElement;
  const toggle = document.querySelector("[data-theme-toggle]");
  root.dataset.enhanced = "true";
  let saved = "";
  try {
    saved = localStorage.getItem("theme");
  } catch (error) {
    saved = "";
  }
  if (saved) root.dataset.theme = saved;

  if (toggle) {
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try {
        localStorage.setItem("theme", next);
      } catch (error) {}
    });
  }

  const applyArchiveFilters = (archive) => {
    if (!archive) return;
    const queryInput = archive.querySelector("[data-archive-query]");
    const sortSelect = archive.querySelector("[data-archive-sort]");
    const list = archive.querySelector(".archive-index");
    const count = archive.querySelector("[data-archive-count]");
    const empty = archive.querySelector("[data-archive-empty]");
    const items = Array.from(archive.querySelectorAll("[data-archive-item]"));
    const query = (queryInput && queryInput.value ? queryInput.value : "").trim().toLowerCase();
    const sort = sortSelect ? sortSelect.value : "newest";
    const activeTag = archive.dataset.activeTag || "";
    let visible = items.filter((item) => {
      const itemSearch = item.dataset.search || "";
      const itemTags = (item.dataset.tags || "").split(/\s+/);
      const matchesQuery = !query || itemSearch.includes(query);
      const matchesTag = !activeTag || itemTags.includes(activeTag);
      return matchesQuery && matchesTag;
    });

    visible.sort((a, b) => {
      if (sort === "oldest") return a.dataset.date.localeCompare(b.dataset.date);
      if (sort === "title") return a.dataset.title.localeCompare(b.dataset.title);
      return b.dataset.date.localeCompare(a.dataset.date);
    });

    items.forEach((item) => {
      item.hidden = true;
    });
    visible.forEach((item) => {
      item.hidden = false;
      if (list) list.appendChild(item);
    });
    if (count) count.textContent = visible.length;
    if (empty) empty.hidden = visible.length !== 0;
  };

  window.omegaArchiveApply = (control) => {
    const archive = control && control.closest ? control.closest("[data-archive]") : null;
    applyArchiveFilters(archive);
  };
  window.omegaArchiveTag = (chip) => {
    const archive = chip && chip.closest ? chip.closest("[data-archive]") : null;
    if (!archive) return;
    const nextTag = chip.dataset.archiveTag || "";
    archive.dataset.activeTag = archive.dataset.activeTag === nextTag ? "" : nextTag;
    archive.querySelectorAll("[data-archive-tag]").forEach((item) => {
      item.classList.toggle("is-active", (item.dataset.archiveTag || "") === archive.dataset.activeTag);
    });
    applyArchiveFilters(archive);
  };

  document.querySelectorAll("[data-archive]").forEach((archive) => {
    const queryInput = archive.querySelector("[data-archive-query]");
    const sortSelect = archive.querySelector("[data-archive-sort]");
    archive.dataset.activeTag = archive.dataset.activeTag || "";
    if (queryInput) queryInput.addEventListener("input", () => applyArchiveFilters(archive));
    if (sortSelect) sortSelect.addEventListener("change", () => applyArchiveFilters(archive));
    applyArchiveFilters(archive);
  });

  document.querySelectorAll("[data-toc]").forEach((box) => {
    const content = document.querySelector(".article-content");
    if (!content) return;
    const headings = Array.from(content.querySelectorAll("h2, h3")).slice(0, 24);
    if (!headings.length) {
      (box.closest(".side-box") || box).remove();
      return;
    }
    const list = document.createElement("ol");
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = "section-" + (index + 1);
      const item = document.createElement("li");
      item.className = heading.tagName === "H3" ? "toc-child" : "";
      const link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent;
      item.appendChild(link);
      list.appendChild(item);
    });
    box.appendChild(list);
  });

  const search = document.querySelector(".search-box[data-search]");
  if (search) {
    const input = search.querySelector("input");
    const results = search.querySelector("[data-search-results]");
    const indexPath = search.dataset.search;
    let index = [];
    fetch(indexPath)
      .then((r) => r.json())
      .then((data) => {
        index = data;
      })
      .catch(() => {});

    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      results.innerHTML = "";
      if (q.length < 2) return;
      const matches = index
        .filter((item) => (item.title + " " + item.excerpt + " " + item.tags).toLowerCase().includes(q))
        .slice(0, 12);
      matches.forEach((item) => {
        const a = document.createElement("a");
        a.href = item.url;
        a.innerHTML = "<strong></strong><span></span>";
        a.querySelector("strong").textContent = item.title;
        a.querySelector("span").textContent = item.excerpt;
        results.appendChild(a);
      });
    });
  }

  const renderMath = () => {
    if (!window.renderMathInElement) return;
    window.renderMathInElement(document.body, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false
    });
  };
  renderMath();
  window.addEventListener("load", renderMath, { once: true });
})();
