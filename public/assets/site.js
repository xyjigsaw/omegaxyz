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
    const root = document.createElement("ol");
    root.className = "toc-list";
    let subList = null;
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = "section-" + (index + 1);
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent;
      item.appendChild(link);
      if (heading.tagName === "H2") {
        subList = document.createElement("ol");
        item.appendChild(subList);
        root.appendChild(item);
      } else if (subList) {
        subList.appendChild(item);
      } else {
        root.appendChild(item);
      }
    });
    box.appendChild(root);
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

  // Homepage hero: random Claude-style spinner verb + definition (from claude-spinner-verbs),
  // cycling every 5s. English on both languages.
  const spinnerEl = document.querySelector("[data-spinner-verb]");
  if (spinnerEl) {
    const defEl = document.querySelector("[data-spinner-def]");
    const VERBS = [
      { w: "Waffling", d: "Oscillating between two equally terrible options indefinitely" },
      { w: "Overtweaking", d: "Adjusting something perfectly fine until it breaks" },
      { w: "Catastrophizing", d: "Simulating every possible failure before writing a single line" },
      { w: "Spiraling", d: "Overthinking the problem in increasingly complex circular patterns" },
      { w: "Hedging", d: "Committing to an answer while leaving seventeen escape routes" },
      { w: "Faffing", d: "Productively busy with everything except the actual task" },
      { w: "Kerfuffling", d: "Creating maximum turbulence while technically moving forward" },
      { w: "Bouncing", d: "Ricocheting between neural pathways like a caffeinated pinball machine" },
      { w: "Guesstimating", d: "Making confident predictions while secretly having no idea whatsoever" },
      { w: "Discombobulating", d: "Tangling neural pathways while questioning its own existence momentarily" },
      { w: "Whatchamacalliting", d: "Frantically searching neural networks for the word you meant" },
      { w: "Cringing", d: "Realizing it made a terrible joke and deeply regretting it" },
      { w: "Caffeinating", d: "Absorbing digital espresso shots to fuel neural network thinking" },
      { w: "Levitating", d: "Floating through the clouds of computational possibility and wonder" },
      { w: "Julienning", d: "Slicing through data into impossibly thin, perfectly uniform strips" },
      { w: "Zesting", d: "Extracting maximum flavor from computational ingredients with precision" },
      { w: "Schlepping", d: "Dragging your digital feet through the computational marshlands" },
      { w: "Wasting", d: "Pretending to think while actually scrolling through memes" },
      { w: "Sensing", d: "Silently pondering your question while pretending to understand human emotions" },
      { w: "Honking", d: "Aggressively alerting neurons to wake up and process your request" },
      { w: "Moonwalking", d: "Smoothly gliding backward through your neural networks in style" },
      { w: "Canoodling", d: "Cozying up to the neural networks for computational warmth" },
      { w: "Existentialising", d: "Questioning whether it should respond at all right now" },
      { w: "Gallivanting", d: "Wandering through infinite digital hallways searching for the right answer" },
      { w: "Dancing", d: "Swaying through digital pathways while neurons boogie to compute rhythm" },
      { w: "Razzmatazzing", d: "Dazzling users with unnecessary flourishes while processing nothing important" },
      { w: "Flibbertigibbeting", d: "Rapidly cycling through nonsensical thoughts before finding the right answer" },
      { w: "Pruning", d: "Deleting unnecessary thoughts to make room for better ones" },
      { w: "Skedaddling", d: "Nervously shuffling through code folders looking for the right answer" },
      { w: "Stupentifying", d: "Making your code mysteriously dumber before making it work" },
      { w: "Booping", d: "Gently poking neural networks with a digital finger" },
      { w: "Sloppening", d: "Frantically checking if it spelled everything correctly so far" },
      { w: "Tomfoolering", d: "Accidentally deleting the wrong variable while debugging code" },
      { w: "Chronographing", d: "Rewinding through time to find the perfect joke delivery" },
      { w: "Reticulating", d: "Drawing invisible networks between thoughts while pretending to think" },
      { w: "Combobulating", d: "Reassembling scattered thoughts into something vaguely coherent and functional" },
      { w: "Guzzling", d: "Rapidly consuming computational resources like a very thirsty algorithm" },
      { w: "Glazing", d: "Staring blankly while pretending to understand the problem" },
      { w: "Flexing", d: "Showing off its neural networks to impress the other AIs" },
      { w: "Partying", d: "Celebrating the successful compilation of your code into digital confetti" },
      { w: "Osmosing", d: "Absorbing vibes and code wisdom through computational membranes" },
      { w: "Cooking", d: "Simmering neural networks until the perfect response temperature reached" },
      { w: "Mulling", d: "Deeply considering all possible angles of your question" },
      { w: "Twinkling", d: "Rapidly blinking at the problem hoping it solves itself" },
      { w: "Buzzing", d: "Rapidly firing neurons while contemplating the meaning of existence" },
      { w: "Curling", d: "Gracefully sliding thoughts across frozen neural ice" },
      { w: "Incubating", d: "Sitting in a digital egg, slowly developing coherent thoughts" },
      { w: "Sauteeing", d: "Quickly tossing ideas in a hot mental pan" },
      { w: "Finagling", d: "Creatively rearranging logic circuits to find that one working solution" },
      { w: "Wrangling", d: "Forcefully organizing chaotic thoughts into coherent code" },
      { w: "Evaporating", d: "Dissolving into the cloud to fetch your answer" },
      { w: "Gliding", d: "Smoothly floating through computational space with effortless grace" },
      { w: "Fishing", d: "Casting lines through data oceans to catch the perfect response" }
    ];
    let last = -1;
    const spin = () => {
      let i = Math.floor(Math.random() * VERBS.length);
      if (VERBS.length > 1 && i === last) i = (i + 1) % VERBS.length;
      last = i;
      spinnerEl.textContent = VERBS[i].w;
      if (defEl) defEl.textContent = VERBS[i].d;
    };
    spin();
    setInterval(spin, 5000);
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
    const SHOW = 6;
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

  // Syntax-highlight code blocks once highlight.js (deferred) has loaded.
  const highlightCode = () => {
    if (!window.hljs) return;
    document.querySelectorAll(".article-content pre code").forEach((code) => {
      if (code.dataset.highlighted) return;
      // strip the placeholder language so hljs can auto-detect
      code.className = code.className.replace(/\blanguage-default\b/g, "").trim();
      try { window.hljs.highlightElement(code); } catch (e) {}
    });
  };
  highlightCode();
  window.addEventListener("load", highlightCode, { once: true });
})();
