// Run against a locally served build with SITE_PREVIEW and optional CHROME_PATH.
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");
const post = "2026/06/25/idevtools-safari-devtools-ipad/";

async function check(browser, lang, width, colorScheme) {
  const ctx = await browser.newContext({viewport: {width, height: 844}, isMobile: width <= 980,
    hasTouch: width <= 980, colorScheme, reducedMotion: "reduce"});
  try {
    const p = await ctx.newPage();
    const errors = [];
    p.on("pageerror", e => errors.push(e.message));
    await p.route("**/*", r => new URL(r.request().url()).origin === base.origin ? r.continue() : r.abort());
    const visit = path => p.goto(new URL(lang + "/" + path, base).href);
    await visit(post);
    const buttons = p.locator(".article-reading-controls button:visible");
    const wide = p.getByRole("button", {name: lang === "en" ? "Wide view" : "宽屏阅读", exact: true});
    const trigger = p.getByRole("button", {name: lang === "en" ? "Contents" : "目录", exact: true});
    if (width > 980) {
      await wide.click();
      assert(await p.locator(".layout.article-wide").count());
      assert(await p.locator("[data-toc]").isVisible());
      assert.equal(await trigger.count(), 0);
      return;
    }
    await trigger.waitFor();
    assert.equal(await buttons.count(), 1);
    assert.equal(await p.locator("[data-toc]").isVisible(), false);
    assert(await p.locator(".related-box").isVisible());
    const sheet = p.getByRole("dialog");
    await trigger.tap();
    await sheet.waitFor();
    assert.equal(await sheet.locator("a").count(), await p.locator(".article-content :is(h2,h3)[id]").count());
    const link = sheet.locator("li.subsection a").first();
    const hash = await link.getAttribute("href");
    await link.tap();
    await p.waitForFunction(h => {
      const target = document.getElementById(decodeURIComponent(h.slice(1)));
      const y = target.getBoundingClientRect().top;
      return location.hash === h && document.activeElement === target &&
        y >= document.querySelector(".site-header").getBoundingClientRect().bottom - 1 && y < 120;
    }, hash);
    assert.equal(await sheet.count(), 0);
    await p.goBack();
    assert.equal(new URL(p.url()).hash, "");
    await trigger.click();
    await p.keyboard.press("Escape");
    assert.equal(await sheet.count(), 0);
    assert(await trigger.evaluate(e => e === document.activeElement));
    await trigger.click();
    await p.mouse.click(5, 5);
    assert.equal(await sheet.count(), 0);
    await trigger.click();
    assert.equal(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await p.setViewportSize({width: 1280, height: 800});
    await wide.waitFor();
    await sheet.waitFor({state: "hidden"});
    assert(await p.locator("[data-toc]").isVisible());
    await p.setViewportSize({width, height: 844});
    await visit("2022/01/13/contrastive_learning_python/");
    await p.locator('[data-mobile-contents="empty"]').waitFor();
    assert.equal(await buttons.count(), 0);
    assert(await p.locator(".related-box").isVisible());
    await visit("archive/");
    assert.equal(await p.locator('script[src*="/article-contents.js"]').count(), 0);
    assert.deepEqual(errors, []);
  } finally { await ctx.close(); }
}

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || undefined});
  try {
    for (const [lang, width, theme] of [["zh",390,"light"],["en",320,"dark"],["en",768,"light"],["zh",1366,"dark"]]) {
      await check(browser, lang, width, theme);
      console.log(lang, width, theme, "article contents passed");
    }
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
