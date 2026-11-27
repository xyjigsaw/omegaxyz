(function () {
  const root = document.documentElement;
  const toggle = document.querySelector("[data-theme-toggle]");
  root.dataset.enhanced = "true";
  if (root.hasAttribute("data-not-found")) {
    const routeLang = location.pathname.split("/")[1];
    let preference;
    try { preference = localStorage.getItem("lang"); } catch (error) {}
    root.lang = [routeLang, preference].find((lang) => lang === "en" || lang === "zh")
      || (/^en/i.test(navigator.language) ? "en" : "zh");
    if (root.lang === "en") {
      document.querySelectorAll("[data-en-text]").forEach((el) => { el.textContent = el.dataset.enText; });
      document.querySelectorAll("[data-en-href]").forEach((el) => { el.href = el.dataset.enHref; });
    }
  } else {
    try { localStorage.setItem("lang", root.lang === "en" ? "en" : "zh"); } catch (error) {}
  }
  let saved = "";
  try {
    saved = localStorage.getItem("theme");
  } catch (error) {
    saved = "";
  }
  const themeQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  const themeModes = ["system", "light", "dark"];
  const themeIcons = {
    system: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="11" rx="2"></rect><path d="M9 20h6M12 16v4"></path></svg>',
    light: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path></svg>',
    dark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 13.1A8 8 0 1 1 10.9 3a6.2 6.2 0 0 0 10.1 10.1z"></path></svg>'
  };
  const themeLabels = {
    system: root.lang === "en" ? "System theme" : "跟随系统",
    light: root.lang === "en" ? "Light theme" : "白天模式",
    dark: root.lang === "en" ? "Dark theme" : "夜间模式"
  };
  const giscusTheme = () => root.dataset.theme === "dark" ? "dark" : "light";
  const syncGiscusTheme = () => {
    const frame = document.querySelector("iframe.giscus-frame");
    if (!frame || !frame.contentWindow) return;
    frame.contentWindow.postMessage({
      giscus: {
        setConfig: {
          theme: giscusTheme()
        }
      }
    }, "https://giscus.app");
  };
  const normalizeThemeMode = (value) => themeModes.includes(value) ? value : "system";
  const applyThemeMode = (mode, persist) => {
    const next = normalizeThemeMode(mode);
    const prefersDark = themeQuery ? themeQuery.matches : false;
    const resolved = next === "dark" || (next === "system" && prefersDark) ? "dark" : "light";
    root.dataset.theme = resolved;
    root.dataset.themeMode = next;
    if (toggle) {
      toggle.innerHTML = themeIcons[next];
      toggle.setAttribute("aria-label", themeLabels[next]);
      toggle.setAttribute("title", themeLabels[next]);
    }
    syncGiscusTheme();
    if (persist) {
      try {
        localStorage.setItem("theme", next);
      } catch (error) {}
    }
  };
  applyThemeMode(saved, false);

  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = normalizeThemeMode(root.dataset.themeMode);
      const next = themeModes[(themeModes.indexOf(current) + 1) % themeModes.length];
      applyThemeMode(next, true);
    });
  }
  if (themeQuery) {
    const syncSystemTheme = () => {
      if (normalizeThemeMode(root.dataset.themeMode) === "system") applyThemeMode("system", false);
    };
    if (themeQuery.addEventListener) {
      themeQuery.addEventListener("change", syncSystemTheme);
    } else if (themeQuery.addListener) {
      themeQuery.addListener(syncSystemTheme);
    }
  }

  document.querySelectorAll("[data-site-uptime]").forEach((node) => {
    const startValue = node.getAttribute("data-site-start") || "2017-04-18";
    const start = new Date(`${startValue}T00:00:00+08:00`);
    if (Number.isNaN(start.getTime())) return;
    const days = Math.max(0, Math.floor((Date.now() - start.getTime()) / 86400000));
    node.textContent = String(days);
  });

  const giscusBlocks = Array.from(document.querySelectorAll("[data-giscus-comments]"));
  const loadGiscusBlock = (block) => {
    if (!block || block.dataset.giscusState) return;
    const mount = block.querySelector("[data-giscus-mount]");
    if (!mount) return;
    block.dataset.giscusState = "loading";
    block.dataset.commentRegion = "global";
    const note = block.querySelector("[data-mainland-comment-note]");
    if (note) note.hidden = true;
    const fallback = block.querySelector("[data-global-discussion-link]");
    fallback.hidden = false;
    // An iframe load event also fires for some blocked pages. Wait for the widget itself.
    window.addEventListener("message", (event) => {
      const frame = mount.querySelector("iframe.giscus-frame");
      if (event.origin !== "https://giscus.app" || !frame || event.source !== frame.contentWindow) return;
      const payload = event.data && event.data.giscus;
      if (!payload) return;
      if (payload.error && !String(payload.error).includes("Discussion not found")) {
        block.dataset.giscusState = "failed";
        fallback.hidden = false;
      } else if (payload.discussion || (block.dataset.giscusState !== "failed" && Number(payload.resizeHeight) > 0)) {
        block.dataset.giscusState = "ready";
        fallback.hidden = true;
      }
    });
    mount.hidden = false;
    const script = document.createElement("script");
    const attrs = {
      src: "https://giscus.app/client.js",
      "data-repo": "xyjigsaw/omegaxyz",
      "data-repo-id": "R_kgDOSpZVLg",
      "data-category": "Comments",
      "data-category-id": "DIC_kwDOSpZVLs4C-SeJ",
      "data-mapping": "specific",
      "data-term": block.dataset.giscusTerm || "",
      "data-strict": "0",
      "data-reactions-enabled": "1",
      "data-emit-metadata": "1",
      "data-input-position": "top",
      "data-default-comment-order": "newest",
      "data-theme": giscusTheme(),
      "data-lang": block.dataset.giscusLang || (root.lang === "en" ? "en" : "zh-CN"),
      crossorigin: "anonymous"
    };
    Object.entries(attrs).forEach(([name, value]) => script.setAttribute(name, value));
    script.async = true;
    script.addEventListener("error", () => { block.dataset.giscusState = "failed"; });
    mount.appendChild(script);
  };
  const ipCards = Array.from(document.querySelectorAll("[data-ip-card]"));
  if (ipCards.length || giscusBlocks.length) {
    const lookup = async (url) => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4500);
      try {
        const response = await fetch(url, { cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error("Region lookup failed");
        const data = await response.json();
        const code = String(data.country_code || data.country || "").toUpperCase();
        if (data.error || !/^[A-Z]{2}$/.test(code) || ["ZZ", "XX", "T1"].includes(code)) throw new Error("Unknown region");
        const name = new Intl.DisplayNames([root.lang || "zh"], { type: "region", fallback: "none" }).of(code);
        if (!name) throw new Error("Unknown region");
        return { ip: data.ip || data.query, country: data.country_name || name, code };
      } finally {
        clearTimeout(timeout);
      }
    };
    const renderIpInfo = (data) => {
      const text = [data.ip, data.country].filter(Boolean).join(" · ");
      if (data.code !== "CN") giscusBlocks.forEach(loadGiscusBlock);
      ipCards.forEach((card) => {
        const status = card.querySelector("[data-ip-status]");
        if (status) status.textContent = text || (root.lang === "en" ? "IP unavailable." : "暂时无法识别 IP。");
      });
    };
    const renderIpError = () => {
      ipCards.forEach((card) => {
        const status = card.querySelector("[data-ip-status]");
        if (status) status.textContent = root.lang === "en"
          ? "IP and country/region are temporarily unavailable."
          : "暂时无法识别 IP 与国家/地区。";
      });
    };
    lookup("https://ipapi.co/json/")
      .catch(() => lookup("https://api.country.is/"))
      .then(renderIpInfo)
      .catch(renderIpError);
  }

  document.querySelectorAll("[data-archive]").forEach((archive) => {
    const query = archive.querySelector("[data-archive-query]");
    const sort = archive.querySelector("[data-archive-sort]");
    const list = archive.querySelector(".archive-index");
    const count = archive.querySelector("[data-archive-count]");
    const empty = archive.querySelector("[data-archive-empty]");
    const chips = archive.querySelectorAll("[data-archive-term]");
    const items = Array.from(list.children, (node) => ({
      node, search: node.dataset.search, date: node.dataset.date, title: node.dataset.title,
      category: node.dataset.categories.split(/\s+/), tag: node.dataset.tags.split(/\s+/),
      pinned: node.dataset.pinned === "true", priority: Number(node.dataset.pinOrder || 0)
    }));
    let kind = "", term = "", order = "featured", activeMonth = "";
    const chartYear = archive.querySelector("[data-chart-year]");
    if (chartYear) chartYear.disabled = false;
    const yearLabel = (year, n) => root.lang === "en" ? year + " (" + n + ")" : year + "（" + n + "）";
    // Match the build's UTC+8 calendar even for a cached page opened after New Year.
    const siteYear = () => String(new Date(Date.now() + 8 * 3600000).getUTCFullYear());
    let defaultYear = chartYear?.value;
    const syncChartYears = () => {
      const current = siteYear();
      for (let y = Number(chartYear.options[0].value) + 1; y <= Number(current); y++) {
        chartYear.add(new Option(yearLabel(y, 0), String(y)), 0);
      }
      if (Array.from(chartYear.options).some(o => o.value === current)) defaultYear = current;
    };
    const monthBars = archive.querySelectorAll("[data-month]");
    monthBars.forEach((bar) => { bar.disabled = false; });
    const filter = () => {
      const text = query.value.trim().toLowerCase();
      let visible = 0;
      const months = Array(12).fill(0);
      const annual = new Map();
      items.forEach((item) => {
        const matchesTerms = (!text || item.search.includes(text)) && (!term || item[kind].includes(term));
        // Count before applying the month so the other bars remain useful as filters.
        if (matchesTerms && chartYear) {
          const year = item.date.slice(0, 4);
          annual.set(year, (annual.get(year) || 0) + 1);
          if (year === chartYear.value) months[Number(item.date.slice(5, 7)) - 1]++;
        }
        const show = matchesTerms && (!activeMonth || item.date.startsWith(activeMonth + "-"));
        if (item.node.hidden === show) item.node.hidden = !show;
        if (show) visible++;
      });
      if (chartYear) {
        for (const option of chartYear.options) {
          const label = yearLabel(option.value, annual.get(option.value) || 0);
          if (option.text !== label) option.text = label;
        }
      }
      const peak = Math.max(1, ...months);
      monthBars.forEach((bar, i) => {
        const n = months[i];
        const month = chartYear.value + "-" + bar.dataset.month;
        bar.dataset.count = n;
        bar.setAttribute("aria-pressed", String(activeMonth === month));
        bar.style.setProperty("--level", n / peak);
        bar.querySelector("b").textContent = n;
        bar.title = month + (root.lang === "en" ? ": " + n + (n === 1 ? " post" : " posts") : "：" + n + " 篇");
        bar.setAttribute("aria-label", bar.title);
      });
      count.textContent = visible;
      empty.hidden = visible !== 0;
    };
    const reorder = () => {
      if (sort.value === order) return;
      order = sort.value;
      const sorted = items.slice().sort((a, b) => {
        if (order === "featured") {
          if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
          if (a.pinned && a.priority !== b.priority) return a.priority - b.priority;
        }
        if (order === "oldest") return a.date.localeCompare(b.date);
        if (order === "title") return a.title.localeCompare(b.title, root.lang);
        return b.date.localeCompare(a.date);
      });
      const fragment = document.createDocumentFragment();
      sorted.forEach(({ node }) => fragment.appendChild(node));
      list.appendChild(fragment);
    };
    const languageLink = document.querySelector(".nav-lang");
    const setParams = (url) => {
      ["q", "tag", "category", "sort"].forEach((key) => url.searchParams.delete(key));
      if (query.value.trim()) url.searchParams.set("q", query.value.trim());
      if (term) url.searchParams.set(kind, term);
      if (chartYear) {
        url.searchParams.delete("month");
        url.searchParams.delete("year");
        if (activeMonth) url.searchParams.set("month", activeMonth);
        else if (chartYear.value !== defaultYear) url.searchParams.set("year", chartYear.value);
      }
      if (sort.value !== "featured") url.searchParams.set("sort", sort.value);
      return url.href;
    };
    const syncLanguageLink = () => {
      if (languageLink) languageLink.href = setParams(new URL(languageLink.href));
    };
    const save = (push) => {
      const next = setParams(new URL(location.href));
      if (next !== location.href) history[push ? "pushState" : "replaceState"](null, "", next);
      syncLanguageLink();
    };
    const markChips = () => {
      chips.forEach((button) => {
        const active = button.dataset.archiveKind === kind && button.dataset.archiveTerm === term && (term !== "" || !activeMonth);
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
    };
    const restore = () => {
      const params = new URLSearchParams(location.search);
      query.value = params.get("q") || "";
      const selected = Array.from(chips).find(({ dataset }) =>
        dataset.archiveTerm && params.get(dataset.archiveKind) === dataset.archiveTerm);
      kind = selected ? selected.dataset.archiveKind : "";
      term = selected ? selected.dataset.archiveTerm : "";
      const requested = params.get("sort");
      sort.value = Array.from(sort.options).some((o) => o.value === requested) ? requested : "featured";
      if (chartYear) {
        syncChartYears();
        const month = params.get("month") || "";
        const years = Array.from(chartYear.options, (o) => o.value);
        activeMonth = /^\d{4}-(0[1-9]|1[0-2])$/.test(month) && years.includes(month.slice(0, 4)) ? month : "";
        chartYear.value = activeMonth ? activeMonth.slice(0, 4) : years.includes(params.get("year")) ? params.get("year") : defaultYear;
      }
      markChips();
      reorder();
      filter();
      syncLanguageLink();
    };
    archive.addEventListener("click", (event) => {
      const bar = event.target.closest("button[data-month]");
      if (bar) {
        const month = chartYear.value + "-" + bar.dataset.month;
        activeMonth = activeMonth === month ? "" : month;
        markChips();
        filter();
        save(true);
        return;
      }
      const chip = event.target.closest("[data-archive-term]");
      if (!chip) return;
      const same = chip.dataset.archiveKind === kind && chip.dataset.archiveTerm === term;
      kind = same ? "" : chip.dataset.archiveKind;
      term = same ? "" : chip.dataset.archiveTerm;
      if (!chip.dataset.archiveKind) activeMonth = "";
      markChips();
      filter();
      save(true);
    });
    query.addEventListener("input", () => { filter(); save(false); });
    chartYear?.addEventListener("change", () => {
      activeMonth = "";
      markChips();
      filter();
      save(true);
    });
    sort.addEventListener("change", () => { reorder(); save(true); });
    window.addEventListener("popstate", restore);
    if (chartYear) document.addEventListener("visibilitychange", () => {
      if (!document.hidden && siteYear() !== defaultYear) restore();
    });
    restore();
  });

  const classifyArticleImages = () => {
    document.querySelectorAll(".article-content img").forEach((img) => {
      const apply = () => {
        const w = Number(img.getAttribute("width")) || img.naturalWidth || 0;
        const h = Number(img.getAttribute("height")) || img.naturalHeight || 0;
        if (!w || !h) return;
        const ratio = w / h;
        img.classList.toggle("image-portrait", ratio < 0.78);
        img.classList.toggle("image-wide", ratio > 1.45);
        img.classList.toggle("image-small", w <= 420);
      };
      apply();
      if (!img.complete) img.addEventListener("load", apply, { once: true });
    });
  };
  classifyArticleImages();

  document.querySelectorAll("[data-toc]").forEach((box) => {
    const content = document.querySelector(".article-content");
    if (!content) return;
    const allHeadings = Array.from(content.querySelectorAll("h2, h3"));
    // Assign IDs before filtering so existing subsection links remain stable.
    allHeadings.forEach((heading, index) => {
      if (!heading.id) heading.id = "section-" + (index + 1);
    });
    const headings = allHeadings;
    if (!headings.length) {
      const sidebar = box.closest(".sidebar");
      const layoutEl = box.closest(".layout");
      const tocBox = box.closest(".side-box") || box;
      tocBox.remove();
      if (sidebar && !sidebar.children.length) sidebar.remove();
      if (layoutEl && (!sidebar || !sidebar.children.length)) layoutEl.classList.add("layout-solo");
      return;
    }
    const root = document.createElement("ol");
    root.className = "toc-list";
    let subList = null;
    let parentItem = null;
    headings.forEach((heading) => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent;
      item.appendChild(link);
      if (heading.tagName === "H2") {
        parentItem = item;
        subList = null;
        root.appendChild(item);
      } else if (parentItem) {
        if (!subList) {
          const details = document.createElement("details");
          const summary = document.createElement("summary");
          const parentLink = parentItem.children[0];
          const sectionTitle = parentLink.textContent;
          const zh = document.documentElement.lang === "zh";
          summary.textContent = sectionTitle;
          summary.setAttribute("aria-label", zh
            ? "展开或收起“" + sectionTitle + "”的下级章节"
            : "Toggle headings under “" + sectionTitle + "”");
          details.appendChild(summary);
          subList = document.createElement("ol");
          details.appendChild(subList);
          parentLink.remove();
          parentItem.classList.add("toc-parent");
          parentItem.appendChild(details);
          // Keep navigation outside summary so it never also toggles details.
          parentLink.textContent = "";
          const jumpIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
          jumpIcon.setAttribute("viewBox", "0 0 16 16");
          jumpIcon.setAttribute("width", "14");
          jumpIcon.setAttribute("height", "14");
          jumpIcon.setAttribute("aria-hidden", "true");
          jumpIcon.setAttribute("focusable", "false");
          const jumpPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
          jumpPath.setAttribute("d", "M4 12 12 4M5 4h7v7");
          jumpPath.setAttribute("fill", "none");
          jumpPath.setAttribute("stroke", "currentColor");
          jumpPath.setAttribute("stroke-width", "1.5");
          jumpPath.setAttribute("stroke-linecap", "round");
          jumpPath.setAttribute("stroke-linejoin", "round");
          jumpIcon.appendChild(jumpPath);
          parentLink.appendChild(jumpIcon);
          parentLink.classList.add("toc-section-link");
          const jumpLabel = (zh ? "跳转正文：" : "Go to section: ") + sectionTitle;
          parentLink.setAttribute("aria-label", jumpLabel);
          parentLink.setAttribute("title", jumpLabel);
          parentItem.appendChild(parentLink);
        }
        subList.appendChild(item);
      } else {
        root.appendChild(item);
      }
    });
    box.appendChild(root);
    // Scrollspy: highlight the TOC entry for the section currently near the top.
    if ("IntersectionObserver" in window) {
      const tocLinks = {};
      root.querySelectorAll("a").forEach((a) => { tocLinks[a.getAttribute("href").slice(1)] = a; });
      const obs = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          const a = tocLinks[e.target.id];
          if (!a) return;
          root.querySelectorAll("a.is-active, summary.is-active").forEach((x) => x.classList.remove("is-active"));
          a.classList.add("is-active");
          if (a.classList.contains("toc-section-link")) {
            const summary = a.closest(".toc-parent").querySelector("summary");
            if (summary) summary.classList.add("is-active");
          }
        });
      }, { rootMargin: "0px 0px -78% 0px" });
      headings.forEach((h) => obs.observe(h));
    }
  });

  // Local, reversible reading controls; no cross-page preference is persisted.
  document.querySelectorAll(".layout > .article").forEach((article) => {
    const content = article.querySelector(".article-content");
    if (!content || article.querySelector(".article-reading-controls")) return;
    const layout = article.closest(".layout");
    const tocPanels = [...new Set(Array.from(layout.querySelectorAll("[data-toc]"))
      .filter((toc) => toc.children.length)
      .map((toc) => toc.closest(".side-box") || toc))];
    const zh = document.documentElement.lang === "zh";
    const controls = document.createElement("div");
    controls.className = "article-reading-controls";
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", zh ? "阅读设置" : "Reading options");
    if (tocPanels.length) {
      tocPanels.forEach((panel, index) => {
        if (!panel.id) panel.id = "article-toc-panel-" + (index + 1);
      });
      let contentsVisible = true;
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.setAttribute("aria-controls", tocPanels.map((panel) => panel.id).join(" "));
      toggle.setAttribute("aria-expanded", "true");
      toggle.textContent = zh ? "隐藏目录" : "Hide contents";
      toggle.addEventListener("click", () => {
        contentsVisible = !contentsVisible;
        tocPanels.forEach((panel) => { panel.hidden = !contentsVisible; });
        toggle.setAttribute("aria-expanded", String(contentsVisible));
        toggle.textContent = !contentsVisible
          ? (zh ? "显示目录" : "Show contents")
          : (zh ? "隐藏目录" : "Hide contents");
      });
      controls.appendChild(toggle);
    }
    const wide = document.createElement("button");
    wide.type = "button";
    wide.setAttribute("aria-pressed", "false");
    wide.textContent = zh ? "宽屏阅读" : "Wide view";
    wide.addEventListener("click", () => {
      const expanded = layout.classList.toggle("article-wide");
      wide.setAttribute("aria-pressed", String(expanded));
      wide.textContent = expanded
        ? (zh ? "标准宽度" : "Standard width")
        : (zh ? "宽屏阅读" : "Wide view");
    });
    controls.appendChild(wide);
    article.insertBefore(controls, content);
  });

  const search = document.querySelector(".search-box[data-search]");
  if (search) {
    const input = search.querySelector("input");
    const results = search.querySelector("[data-search-results]");
    const recent = document.querySelector("[data-search-recent]");
    const en = root.lang === "en";
    const indexPath = (en && search.dataset.searchEn) || search.dataset.search;
    if (en && search.dataset.searchEn) {
      search.action = search.dataset.enAction;
      input.placeholder = "Search articles, pages and tags…";
      input.setAttribute("aria-label", "Search");
    }
    const status = document.createElement("p");
    status.className = "search-feedback";
    status.setAttribute("role", "status");
    const more = document.createElement("button");
    more.type = "button";
    more.className = "search-more";
    let index = [], matches = [], shown = 0, state = "idle";
    let pattern;
    const appendMatches = (moveFocus) => {
      more.remove();
      const batch = matches.slice(shown, shown + 12);
      const fragment = document.createDocumentFragment();
      let first;
      batch.forEach((item) => {
        const link = document.createElement("a");
        link.href = item.url;
        ["title", "excerpt"].forEach((field) => {
          const node = document.createElement(field === "title" ? "strong" : "span");
          let last = 0;
          const value = item[field] || "";
          for (const hit of value.matchAll(pattern)) {
            const mark = document.createElement("mark");
            mark.textContent = hit[0];
            node.append(value.slice(last, hit.index), mark);
            last = hit.index + hit[0].length;
          }
          node.append(value.slice(last));
          link.append(node);
        });
        fragment.append(link);
        if (!first) first = link;
      });
      results.append(fragment);
      shown += batch.length;
      status.textContent = matches.length ? (en ? "Showing " + shown + " of " + matches.length + " results" : "共 " + matches.length + " 条结果，已显示 " + shown + " 条")
        : (en ? "No results. Try a different keyword." : "没有找到结果，换个关键词试试。");
      if (shown < matches.length) {
        more.textContent = en ? "Show more results" : "显示更多结果";
        results.append(more);
      }
      if (moveFocus && first) first.focus();
    };
    const render = () => {
      const q = input.value.trim();
      if (recent) recent.hidden = Boolean(q);
      results.replaceChildren();
      if (!q) return;
      results.append(status);
      if (state !== "ready") {
        status.textContent = state === "error"
          ? (en ? "Search could not load." : "搜索暂时无法加载。")
          : (en ? "Loading search…" : "正在加载搜索…");
        if (state === "error") {
          more.textContent = en ? "Retry" : "重试";
          results.append(more);
        }
        return;
      }
      const literal = q.replace(/[.*+?^{}$()|[\]\\]/g, "\\$&");
      // Treat single-letter language names such as C and R as words, not arbitrary substrings.
      const term = /^[a-z]$/i.test(q) ? "\\b" + literal + "\\b" : literal;
      const matcher = new RegExp(term, "i");
      pattern = new RegExp(term, "gi");
      const inTitle = [], inOther = [];
      index.forEach((item) => {
        if (matcher.test(item.title)) inTitle.push(item);
        else if (matcher.test(item.tags) || matcher.test(item.excerpt)) inOther.push(item);
      });
      matches = inTitle.concat(inOther);
      shown = 0;
      appendMatches(false);
    };
    const loadIndex = async () => {
      if (state === "loading" || state === "ready") return;
      state = "loading";
      render();
      try {
        const response = await fetch(indexPath);
        if (!response.ok) throw new Error("Search index unavailable");
        index = await response.json();
        if (!Array.isArray(index)) throw new Error("Invalid search index");
        state = "ready";
      } catch (error) {
        state = "error";
      }
      render();
    };
    if (search.classList.contains("home-search")) {
      const outside = (event) => {
        if (!search.contains(event.target)) results.hidden = true;
      };
      document.addEventListener("pointerdown", outside);
      document.addEventListener("focusin", outside);
      const open = () => { results.hidden = false; };
      search.addEventListener("focusin", open);
      search.addEventListener("pointerdown", open);
      input.addEventListener("input", open);
      search.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        event.preventDefault();
        input.focus();
        results.hidden = true;
      });
    }
    more.addEventListener("click", () => state === "error" ? loadIndex() : appendMatches(true));
    input.addEventListener("focus", loadIndex, { once: true });
    input.addEventListener("input", () => state === "idle" ? loadIndex() : render());
    if (search.hasAttribute("data-search-page")) {
      input.value = (new URLSearchParams(location.search).get("q") || "").trim();
      const switcher = document.querySelector(".nav-lang");
      if (switcher) {
        const alternate = new URL(switcher.href);
        const syncLanguageLink = () => {
          const q = input.value.trim();
          if (q) alternate.searchParams.set("q", q);
          else alternate.searchParams.delete("q");
          switcher.href = alternate.href;
        };
        syncLanguageLink();
        input.addEventListener("input", syncLanguageLink);
      }
      if (input.value) loadIndex();
    }
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
    let loading = null;
    const buttons = latestSection.querySelectorAll("[data-home-mode]");
    const setActive = (mode) => buttons.forEach((b) => b.classList.toggle("is-active", b.dataset.homeMode === mode));
    const showRandom = (rows) => {
      const idx = pickIndices(rows.length, SHOW, true);
      list.innerHTML = Array.from(idx).map((i) => rows[i]).join("");
    };
    const loadPool = () => {
      if (pool) return Promise.resolve(pool);
      if (!dataUrl) return Promise.reject();
      if (!loading) loading = fetch(dataUrl).then((r) => r.json()).then((rows) => { pool = rows; return rows; });
      return loading;
    };
    // Warm the shuffle data in the background so the first "随机" click is instant.
    const prefetch = () => { loadPool().catch(() => {}); };
    if ("requestIdleCallback" in window) requestIdleCallback(prefetch, { timeout: 3000 });
    else window.addEventListener("load", () => setTimeout(prefetch, 1000), { once: true });
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.homeMode;
        setActive(mode);
        if (mode !== "random") { list.innerHTML = baked; return; }
        if (pool) { showRandom(pool); return; }
        loadPool().then(showRandom).catch(() => {});
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

  // Floating back-to-top button (appears after scrolling down).
  const toTop = document.createElement("button");
  toTop.type = "button";
  toTop.className = "to-top";
  toTop.setAttribute("aria-label", "Back to top");
  toTop.textContent = "↑";
  document.body.appendChild(toTop);
  toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  const toggleToTop = () => toTop.classList.toggle("is-visible", window.scrollY > 600);
  window.addEventListener("scroll", toggleToTop, { passive: true });
  toggleToTop();

  // Wrap article code blocks with a toolbar (copy + collapse). Default expanded.
  const enhanceCodeBlocks = () => {
    const lang = (document.documentElement.lang || "en").slice(0, 2);
    const L = lang === "zh"
      ? { copy: "复制", copied: "已复制", collapse: "折叠", expand: "展开" }
      : { copy: "Copy", copied: "Copied", collapse: "Collapse", expand: "Expand" };
    document.querySelectorAll(".article-content pre").forEach((pre) => {
      if (pre.parentElement && pre.parentElement.classList.contains("code-block")) return;
      const wrap = document.createElement("div");
      wrap.className = "code-block";
      const bar = document.createElement("div");
      bar.className = "code-toolbar";
      const collapseBtn = document.createElement("button");
      collapseBtn.type = "button";
      collapseBtn.className = "code-btn";
      collapseBtn.textContent = L.collapse;
      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "code-btn";
      copyBtn.textContent = L.copy;
      bar.appendChild(collapseBtn);
      bar.appendChild(copyBtn);
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(bar);
      wrap.appendChild(pre);
      collapseBtn.addEventListener("click", () => {
        const collapsed = wrap.classList.toggle("is-collapsed");
        collapseBtn.textContent = collapsed ? L.expand : L.collapse;
      });
      copyBtn.addEventListener("click", () => {
        const text = (pre.querySelector("code") || pre).innerText;
        const done = () => {
          copyBtn.textContent = L.copied;
          setTimeout(() => { copyBtn.textContent = L.copy; }, 1500);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(() => {});
        } else {
          const ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand("copy"); done(); } catch (e) {}
          document.body.removeChild(ta);
        }
      });
    });
  };
  enhanceCodeBlocks();

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
