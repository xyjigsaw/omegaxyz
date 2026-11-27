// The shared reader already assigns stable heading IDs for the desktop TOC.
const layout = document.querySelector("main.layout");
const controls = layout?.querySelector(".article-reading-controls");
const compact = matchMedia("(max-width: 980px)");
const en = document.documentElement.lang === "en";
const label = en ? "Contents" : "目录";
let sheet;

function adapt() {
  if (!compact.matches) {
    if (sheet?.open) sheet.close();
    return;
  }
  if (!controls || layout.hasAttribute("data-mobile-contents") || !window.HTMLDialogElement?.prototype.showModal) return;
  const headings = [...layout.querySelectorAll(".article-content :is(h2, h3)[id]")].filter(h => h.textContent.trim());
  const panel = layout.querySelector("[data-toc]")?.closest(".side-box");
  layout.dataset.mobileContents = headings.length && panel ? "ready" : "empty";
  if (panel) panel.classList.add("desktop-contents-panel");
  if (layout.dataset.mobileContents === "empty") return;

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "contents-trigger";
  trigger.innerHTML = '<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>';
  trigger.append(label);
  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-controls", "article-contents-sheet");
  controls.append(trigger);

  sheet = document.createElement("dialog");
  sheet.className = "article-contents-sheet";
  sheet.id = "article-contents-sheet";
  sheet.setAttribute("aria-labelledby", "article-contents-title");
  sheet.innerHTML = '<header><h2 id="article-contents-title"></h2><button type="button" autofocus><svg aria-hidden="true" viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="m18 6-12 12M6 6l12 12"/></svg></button></header><ol></ol>';
  sheet.querySelector("h2").textContent = label;
  const close = sheet.querySelector("button");
  close.setAttribute("aria-label", en ? "Close contents" : "关闭目录");
  close.addEventListener("click", () => sheet.close());
  const list = sheet.querySelector("ol");
  const links = headings.map(h => {
    const li = document.createElement("li");
    if (h.tagName === "H3") li.className = "subsection";
    const link = document.createElement("a");
    link.href = "#" + encodeURIComponent(h.id);
    link.textContent = h.textContent.trim();
    link.addEventListener("click", event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      sheet.close();
      if (!h.hasAttribute("tabindex")) h.tabIndex = -1;
      h.focus({preventScroll: true});
      // Let the native link update the fragment and browser back history.
    });
    li.append(link);
    list.append(li);
    return link;
  });
  document.body.append(sheet);
  trigger.addEventListener("click", () => {
    const top = document.querySelector(".site-header")?.getBoundingClientRect().bottom || 0;
    let current = 0;
    headings.forEach((h, i) => { if (h.getBoundingClientRect().top <= top + 24) current = i; });
    links.forEach((a, i) => {
      if (i === current) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    });
    sheet.showModal();
    links[current].scrollIntoView({block: "nearest", behavior: "instant"});
  });
  sheet.addEventListener("click", e => {
    if (e.target !== sheet) return;
    const rect = sheet.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) sheet.close();
  });
}

adapt();
compact.addEventListener("change", adapt);
