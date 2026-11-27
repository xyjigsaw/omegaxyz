const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");
const browserOptions = {executablePath: process.env.CHROME_PATH || undefined};

async function check(browser, lang, blocked) {
  const context = await browser.newContext({viewport: {width: blocked ? 320 : 1366, height: 820},
    colorScheme: blocked ? "dark" : "light", permissions: blocked ? [] : ["clipboard-read", "clipboard-write"]});
  try {
    const p = await context.newPage();
    const errors = [];
    p.on("pageerror", e => errors.push(String(e)));
    let requests = 0, fail = blocked;
    if (blocked) await p.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", {value: {write: async () => { throw Error("denied"); }}});
    });
    await p.route("**/*", r => {
      const url = new URL(r.request().url());
      if (url.origin !== base.origin) return r.abort();
      if (url.pathname.endsWith("/index.md")) {
        requests++;
        if (fail) return r.fulfill({status: 503, body: "offline"});
      }
      return r.continue();
    });
    const path = lang + "/2026/06/25/idevtools-safari-devtools-ipad/";
    await p.goto(new URL(path, base).href);
    const boxes = p.locator(".md-tools");
    assert.equal(await boxes.count(), 2);
    assert.equal(requests, 0);
    const raw = new URL(path + "index.md", base).href;
    const expected = await (await context.request.get(raw)).text();
    assert(expected.startsWith("# "));
    for (const box of await boxes.all()) {
      assert.equal(await box.locator("a").evaluate(a => a.href), raw);
      await box.getByRole("button").click();
      if (fail) {
        await box.getByText(/重试|Try again/).waitFor();
        fail = false;
        await box.getByRole("button").click();
      }
      if (blocked) {
        await box.locator("textarea").waitFor();
        assert.equal(await box.locator("textarea").inputValue(), expected);
      } else {
        await box.getByText(lang === "en" ? "Copied" : "已复制", {exact:true}).waitFor();
        assert.equal(await p.evaluate(() => navigator.clipboard.readText()), expected);
      }
    }
    assert.equal(requests, blocked ? 2 : 1);
    assert.equal(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await p.goto(new URL(lang + "/comment/", base).href);
    assert.equal(await boxes.count(), 0);
    for (const type of ["rss", "atom"]) {
      assert.equal(await p.locator('head link[type="application/' + type + '+xml"]').getAttribute("href"), "/" + lang + "/" + type + ".xml");
    }
    assert.deepEqual(errors, []);
    console.log(lang, blocked ? "denied clipboard and network retry" : "real clipboard", "passed");
  } finally { await context.close(); }
}

(async () => {
  const browser = await chromium.launch(browserOptions);
  try { await check(browser, "zh", false); await check(browser, "en", true); }
  finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
