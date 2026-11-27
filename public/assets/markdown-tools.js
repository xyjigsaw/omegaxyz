(() => {
  const en = document.documentElement.lang === "en";
  let pending;
  function read(url) {
    if (!pending) pending = fetch(url).then(response => {
      if (!response.ok || (response.headers.get("content-type") || "").includes("text/html"))
        throw new Error("Markdown unavailable");
      return response.text();
    }).catch(err => { pending = null; throw err; });
    return pending;
  }
  for (const box of document.querySelectorAll(".md-tools")) {
    const button = box.querySelector("[data-md-copy]"), status = box.querySelector("[role=status]");
    button.hidden = false;
    button.addEventListener("click", async () => {
      if (button.getAttribute("aria-busy") === "true") return;
      button.setAttribute("aria-busy", "true");
      status.textContent = "";
      box.querySelector("textarea")?.remove();
      const content = read(box.querySelector("a").href);
      try {
        if (window.ClipboardItem && navigator.clipboard?.write) {
          // Safari requires the clipboard request in the original user gesture.
          const blob = content.then(text => new Blob([text], {type: "text/plain"}));
          blob.catch(() => {});
          await navigator.clipboard.write([new ClipboardItem({"text/plain": blob})]);
        } else {
          await navigator.clipboard.writeText(await content);
        }
        status.textContent = en ? "Copied" : "已复制";
      } catch {
        try {
          const text = await content;
          const area = document.createElement("textarea");
          area.readOnly = true;
          area.value = text;
          area.setAttribute("aria-label", en ? "Markdown to copy" : "待复制的 Markdown");
          box.append(area);
          area.focus(); area.select(); area.setSelectionRange(0, text.length);
          status.textContent = en ? "Select and copy the text below." : "请复制下方已选中的正文。";
        } catch {
          status.textContent = en ? "Could not load. Try again." : "正文加载失败，请重试。";
        }
      } finally { button.removeAttribute("aria-busy"); }
    });
  }
})();
