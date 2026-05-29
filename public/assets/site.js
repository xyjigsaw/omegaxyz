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
    const activeKind = archive.dataset.activeKind || "";
    const activeTerm = archive.dataset.activeTerm || "";
    let visible = items.filter((item) => {
      const itemSearch = item.dataset.search || "";
      const itemTerms = (activeKind === "category" ? item.dataset.categories || "" : item.dataset.tags || "").split(/\s+/);
      const matchesQuery = !query || itemSearch.includes(query);
      const matchesTerm = !activeTerm || itemTerms.includes(activeTerm);
      return matchesQuery && matchesTerm;
    });

    visible.sort((a, b) => {
      if (sort === "oldest") return a.dataset.date.localeCompare(b.dataset.date);
      if (sort === "title") return a.dataset.title.localeCompare(b.dataset.title);
      return b.dataset.date.localeCompare(a.dataset.date);
    });

    items.forEach((item) => {
      item.hidden = true;
      item.style.display = "none";
    });
    visible.forEach((item) => {
      item.hidden = false;
      item.style.removeProperty("display");
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
    const nextKind = chip.dataset.archiveKind || "";
    const nextTerm = chip.dataset.archiveTerm || "";
    const isSame = (archive.dataset.activeKind || "") === nextKind && (archive.dataset.activeTerm || "") === nextTerm;
    archive.dataset.activeKind = isSame ? "" : nextKind;
    archive.dataset.activeTerm = isSame ? "" : nextTerm;
    archive.querySelectorAll("[data-archive-term]").forEach((item) => {
      item.classList.toggle(
        "is-active",
        (item.dataset.archiveKind || "") === archive.dataset.activeKind &&
          (item.dataset.archiveTerm || "") === archive.dataset.activeTerm
      );
    });
    applyArchiveFilters(archive);
  };

  document.querySelectorAll("[data-archive]").forEach((archive) => {
    const queryInput = archive.querySelector("[data-archive-query]");
    const sortSelect = archive.querySelector("[data-archive-sort]");
    archive.dataset.activeKind = archive.dataset.activeKind || "";
    archive.dataset.activeTerm = archive.dataset.activeTerm || "";
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

  // Homepage hero: random Claude-style spinner verb (from claude-spinner-verbs).
  const spinnerEl = document.querySelector("[data-spinner-verb]");
  if (spinnerEl) {
    const VERBS = [
      "Waffling", "Overtweaking", "Catastrophizing", "Spiraling", "Hedging",
      "Faffing", "Kerfuffling", "Bouncing", "Guesstimating", "Discombobulating",
      "Whatchamacalliting", "Cringing", "Caffeinating", "Levitating", "Julienning",
      "Zesting", "Schlepping", "Sensing", "Honking", "Moonwalking", "Canoodling",
      "Existentialising", "Gallivanting", "Dancing", "Razzmatazzing", "Flibbertigibbeting",
      "Pruning", "Skedaddling", "Stupentifying", "Booping", "Sloppening", "Tomfoolering",
      "Chronographing", "Reticulating", "Combobulating", "Guzzling", "Glazing", "Flexing",
      "Partying", "Osmosing", "Cooking", "Mulling", "Twinkling", "Buzzing", "Curling",
      "Incubating", "Sauteeing", "Finagling", "Wrangling", "Evaporating", "Gliding", "Fishing"
    ];
    spinnerEl.textContent = VERBS[Math.floor(Math.random() * VERBS.length)];
  }

  const pickIndices = (count, show, random) => {
    const order = Array.from({ length: count }, (_, i) => i);
    if (random) {
      for (let i = order.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [order[i], order[j]] = [order[j], order[i]];
      }
    }
    return new Set(order.slice(0, show));
  };

  // Homepage "Latest / Shuffle" tabs — Shuffle draws a random 9 from ALL posts (lazy-loaded).
  const latestSection = document.querySelector("[data-home-latest]");
  if (latestSection) {
    const list = latestSection.querySelector("[data-home-list]");
    const baked = list ? list.innerHTML : "";
    const dataUrl = latestSection.dataset.homeData;
    const SHOW = 9;
    let pool = null;
    const buttons = latestSection.querySelectorAll("[data-home-mode]");
    const setActive = (mode) => buttons.forEach((b) => b.classList.toggle("is-active", b.dataset.homeMode === mode));
    const showRandom = (rows) => {
      const idx = pickIndices(rows.length, SHOW, true);
      list.innerHTML = Array.from(idx).map((i) => rows[i]).join("");
    };
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.homeMode;
        setActive(mode);
        if (mode !== "random") { list.innerHTML = baked; return; }
        if (pool) { showRandom(pool); return; }
        if (!dataUrl) return;
        fetch(dataUrl).then((r) => r.json()).then((rows) => { pool = rows; showRandom(rows); }).catch(() => {});
      });
    });
  }

  // Homepage topic rail: show top categories by default, shuffle to random on refresh.
  const topicSection = document.querySelector("[data-home-topics]");
  if (topicSection) {
    const rail = topicSection.querySelector("[data-topic-rail]");
    const items = rail ? Array.from(rail.children) : [];
    const SHOW = 8;
    const apply = (random) => {
      const keep = pickIndices(items.length, SHOW, random);
      items.forEach((item, i) => { item.style.display = keep.has(i) ? "" : "none"; });
    };
    const refresh = topicSection.querySelector("[data-topic-refresh]");
    if (refresh) refresh.addEventListener("click", () => apply(true));
    apply(false);
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
