// Optional browser regression: serve docs/ and set SITE_PREVIEW and CHROME_PATH as needed.
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");
const url = (path) => new URL(path, base).href;

async function exercise(browser, lang) {
  const en = lang === "en";
  const context = await browser.newContext({locale: en ? "en-US" : "zh-CN",
    viewport: en ? {width: 1440, height: 900} : {width: 390, height: 844}});
  try {
    const p = await context.newPage();
    const errors = [];
    p.on("pageerror", err => errors.push(String(err)));
    let region = "CN", widget = "blocked", widgetRequests = 0, failSearch = false;
    const notFound = await (await context.request.get(url("404.html"))).text();
    await p.route("**/*", r => {
      const u = new URL(r.request().url());
      if (u.origin === base.origin) {
        if (u.pathname.endsWith("/missing-for-test")) return r.fulfill({status:404, contentType:"text/html", body:notFound});
        if (u.pathname.endsWith("/search-index.json") && failSearch) return r.fulfill({status:503, body:""});
        return r.continue();
      }
      if (["ipapi.co", "api.country.is"].includes(u.hostname)) {
        return region ? r.fulfill({json:{country_code:region}}) : r.abort();
      }
      if (u.href === "https://giscus.app/client.js") {
        widgetRequests++;
        if (widget === "blocked") return r.abort();
        return r.fulfill({contentType:"application/javascript", body:
          'const f=document.createElement("iframe");f.className="giscus-frame";f.src="https://giscus.app/widget";document.querySelector(".giscus").append(f);'});
      }
      if (u.href === "https://giscus.app/widget") return r.fulfill({contentType:"text/html", body:"<p>Widget fixture</p>"});
      return r.abort();
    });
    const go = path => p.goto(url(path), {waitUntil:"domcontentloaded"});
    const other = en ? "zh" : "en";
    await go(other + "/search/");
    assert.equal((await go(lang + "/missing-for-test")).status(), 404);
    const locale = () => p.evaluate(() => [document.documentElement.lang, localStorage.getItem("lang")]);
    assert.deepEqual(await locale(), [lang,other]);
    assert.equal(await p.locator("h1").innerText(), en ? "Page not found" : "页面走丢了");
    assert.ok(await p.locator("header a,.hero-actions a,.notfound-latest a").evaluateAll((as, lang) =>
      as.every(a => a.pathname.startsWith("/" + lang + "/")), lang));
    let box = p.locator(".search-box input");
    await box.fill("C");
    await p.locator("[data-search-results] a").first().waitFor();
    assert.ok((await p.locator("[data-search-results] a").first().getAttribute("href")).startsWith("/"+lang+"/"));
    await go("missing-for-test");
    assert.deepEqual(await locale(), [other,other]);

    await go(lang + "/search/");
    const recent = p.locator("[data-search-recent]");
    assert.equal(await recent.locator("a").count(),5);
    assert.ok(await recent.isVisible());
    failSearch = true;
    await box.fill("C");
    await p.getByRole("button", {name:en?"Retry":"重试"}).waitFor();
    assert.ok(await recent.isHidden());
    failSearch = false;
    await p.getByRole("button", {name:en?"Retry":"重试"}).click();
    const links = p.locator("[data-search-results] a");
    await links.first().waitFor();
    for (const q of ["C++", en?"Machine":"学"]) {
      await box.fill(q);
      assert.ok(await links.count() > 0, q);
    }
    assert.equal(await links.count(),12);
    await p.locator(".search-more").click();
    assert.equal(await links.count(),24);
    assert.ok((await p.locator(".search-feedback").innerText()).includes("24"));
    await box.fill("Omega-no-such-note-000");
    assert.match(await p.locator(".search-feedback").innerText(), /No results|没有找到/);
    await box.fill("");
    assert.equal(await p.locator("[data-search-results]").innerText(), "");
    assert.ok(await recent.isVisible());

    for (const path of [lang + "/archive/", lang + "/category/tech/"]) {
      await go(path);
      const query = p.locator("[data-archive-query]"), sort = p.locator("[data-archive-sort]");
      const ios = p.locator('[data-archive-kind="tag"][data-archive-term="ios"]');
      const items = p.locator("[data-archive-item]:visible");
      const all = await items.count();
      await ios.click();
      const tagged = await items.count();
      assert.ok(tagged > 0 && tagged < all);
      await sort.selectOption("oldest");
      await query.fill("iOS");
      await p.waitForURL(u => u.searchParams.get("q") === "iOS");
      const shared = p.url();
      assert.deepEqual(Object.fromEntries(new URL(shared).searchParams), {q:"iOS",tag:"ios",sort:"oldest"});
      await p.reload();
      assert.equal(await ios.getAttribute("aria-pressed"),"true");
      assert.equal(await sort.inputValue(),"oldest"); assert.equal(await query.inputValue(),"iOS");
      assert.equal(await items.count(), tagged);
      await ios.click();
      await p.waitForURL(u => !u.searchParams.has("tag"));
      await p.goBack();
      assert.equal(await ios.getAttribute("aria-pressed"),"true");
      await p.goForward();
      assert.equal(await ios.getAttribute("aria-pressed"),"false");
      await go(path+"?sort=invalid&tag=no-such-tag");
      assert.equal(await items.count(),all);
      assert.equal(await sort.inputValue(),"featured");
      await p.goto(shared);
      await p.locator(".nav-lang").click();
      await p.locator('[data-archive-term="ios"][aria-pressed="true"]').waitFor();
      assert.ok(new URL(p.url()).pathname.startsWith("/"+other+"/"));
      assert.equal(new URL(p.url()).search,new URL(shared).search);
      assert.equal(await items.count(),tagged);
    }
    await go(lang+"/archive/?category=tech");
    assert.equal(await p.locator('[data-archive-kind="category"][data-archive-term="tech"]').getAttribute("aria-pressed"),"true");

    const article = lang + "/2026/11/26/scaling-low-ai-risk-roundup/";
    const block = p.locator("[data-giscus-comments]");
    const mainland = block.locator("[data-mainland-comment-note]");
    const fallback = block.locator("[data-global-discussion-link]");
    const archive = block.locator("[data-giscus-mount]");
    for (region of ["CN", null]) {
      await go(article);
      await p.waitForFunction(() => /中国|China|unavailable|无法识别/.test(document.querySelector("[data-ip-status]").textContent));
      assert.ok(await mainland.isVisible()); assert.ok(await fallback.isHidden());
      assert.ok(await archive.isHidden()); assert.equal(widgetRequests,0);
    }
    region="US";
    await go(article);
    await block.locator('[data-global-discussion-link]:visible').waitFor();
    await p.waitForFunction(()=>document.querySelector("[data-giscus-comments]").dataset.giscusState==="failed");
    assert.ok(await mainland.isHidden());
    assert.equal(await fallback.getAttribute("href"),await mainland.locator("a").getAttribute("href"));
    widget="ok";
    await go(article);
    await p.frameLocator(".giscus-frame").getByText("Widget fixture").waitFor();
    assert.ok(await fallback.isVisible(), "iframe load alone must not remove fallback");
    const frame = p.frames().find(f=>f.url()==="https://giscus.app/widget");
    await frame.evaluate(()=>parent.postMessage({giscus:{resizeHeight:320}},"*"));
    await fallback.waitFor({state:"hidden"});
    await frame.evaluate(()=>parent.postMessage({giscus:{error:"API unavailable"}},"*"));
    await fallback.waitFor();
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);
    console.log(lang+": 404, search, shared archive and regional comments passed");
  } finally { await context.close(); }
}

(async()=>{
  const browser = await chromium.launch({executablePath:process.env.CHROME_PATH});
  try { await exercise(browser,"en"); await exercise(browser,"zh"); }
  finally { await browser.close(); }
})().catch(e=>{ console.error(e); process.exitCode=1; });
