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
    for (const selector of [".notfound-title", ".notfound-search", ".notfound-latest"]) {
      assert.ok(await p.locator(selector).evaluate(el => Math.abs(el.getBoundingClientRect().left * 2 +
        el.getBoundingClientRect().width - document.documentElement.clientWidth) < 2));
    }
    assert.ok(await p.locator("header a,.hero-actions a,.notfound-latest a").evaluateAll((as, lang) =>
      as.every(a => a.pathname.startsWith("/" + lang + "/")), lang));
    let box = p.locator(".search-box input");
    await box.fill("C");
    await p.locator("[data-search-results] a").first().waitFor();
    assert.ok((await p.locator("[data-search-results] a").first().getAttribute("href")).startsWith("/"+lang+"/"));
    await go("missing-for-test");
    assert.deepEqual(await locale(), [other,other]);

    await p.emulateMedia({reducedMotion:"reduce"});
    await go(lang + "/");
    await box.fill("AI");
    const dropdown = p.locator(".home-search [data-search-results]");
    await dropdown.locator("a").first().waitFor();
    assert.equal(await p.locator("[data-search-kind]").count(), 0);
    assert.match(await dropdown.evaluate(el => getComputedStyle(el).backdropFilter), /blur/);
    await p.locator(".omega-hero").click({position:{x:4,y:4}});
    assert.ok(await dropdown.isHidden());
    await box.click();
    assert.equal(await box.inputValue(), "AI");
    await dropdown.locator("a").first().waitFor();
    await box.press("Escape");
    assert.ok(await dropdown.isHidden());
    assert.equal(await box.inputValue(), "AI");
    const topic = en ? "机器学习" : "Machine Learning";
    await box.fill(topic);
    await dropdown.locator("a.search-tag").first().waitFor();
    assert.ok(await dropdown.evaluate(el => {
      const rect = el.getBoundingClientRect();
      return el.contains(document.elementFromPoint(rect.left + 20, Math.min(innerHeight - 1, rect.bottom - 10)));
    }), "Home search results should be above the latest posts");
    await box.press("Enter");
    await p.waitForURL(u => u.pathname === "/"+lang+"/search/" && u.searchParams.get("q") === topic);
    for (const [kind, slug] of [["category","machine-learning"],["tag","机器学习"]]) {
      const hit = p.locator(".search-results a.search-"+kind).first();
      await hit.waitFor();
      assert.equal(await hit.getAttribute("href"), "/"+lang+"/"+kind+"/"+slug+"/");
      assert.match(await hit.locator(".search-term-names").innerText(), /机器学习/);
      assert.match(await hit.locator(".search-term-names").innerText(), /Machine Learning/);
      assert.match(await hit.locator("small").innerText(), /[1-9]\d* (?:post|篇文章)/);
      const alias = hit.locator(".search-term-names > [lang]");
      assert.equal(await alias.getAttribute("lang"), other);
      assert.ok(await alias.evaluate(el => {
        const primary = getComputedStyle(el.previousElementSibling), secondary = getComputedStyle(el);
        return parseFloat(secondary.fontSize) < parseFloat(primary.fontSize) && secondary.color !== primary.color;
      }));
    }

    const type = k => p.locator('[data-search-kind="' + k + '"]');
    const hitCounts = () => p.locator("[data-search-kind] [data-count]").allTextContents();
    assert.equal(await type("all").getAttribute("aria-pressed"), "true");
    await box.fill("Python");
    const index = await (await context.request.get(url(lang + "/search-index.json"))).json();
    const kinds = ["post","page","category","tag"];
    const expected = kinds.map(kind => index.filter(r => r.kind === kind &&
      [r.title,r.excerpt,r.tags,r.alternate,r.slug].some(s => s && s.toLowerCase().includes("python"))).length);
    const totals = [expected.reduce((a,b) => a+b, 0), ...expected].map(String);
    const searchLinks = p.locator("[data-search-results] a");
    for (const [i, k] of kinds.entries()) {
      await type(k).click();
      assert.deepEqual(await hitCounts(), totals);
      assert.equal(await searchLinks.count(), Math.min(expected[i],12));
      const label = (en ? ["Post","Page","Category","Tag"] : ["文章","页面","分类","标签"])[i];
      assert.ok((await searchLinks.locator(".search-kind").allTextContents()).every(t => t === label));
      if (expected[i] > 12) {
        await p.locator(".search-more").click();
        assert.equal(await searchLinks.count(), Math.min(expected[i],24));
        assert.deepEqual(await hitCounts(), totals);
      }
    }
    await type("page").click();
    const pages = index.filter(r => r.kind === "page");
    const onlyPostTitle = index.find(r => r.kind === "post" && r.title.length > 4 &&
      !pages.some(page => [page.title,page.excerpt,page.tags].some(s => s.toLowerCase().includes(r.title.toLowerCase())))).title;
    await box.fill(onlyPostTitle);
    assert.equal(await searchLinks.count(),0);
    assert.match(await p.locator(".search-feedback").innerText(), /this type|该类型/);
    await box.fill("Python");
    await Promise.all([p.waitForNavigation(), box.press("Enter")]);
    assert.equal(await type("page").getAttribute("aria-pressed"), "true");
    await p.locator(".nav-lang").click();
    assert.equal(await type("page").getAttribute("aria-pressed"), "true");
    assert.equal(await box.inputValue(), "Python");
    await type("all").click();
    assert.ok(!new URL(p.url()).searchParams.has("type"));

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
    assert.deepEqual(await p.locator(".archive-filters").evaluate(el => [
      el.clientHeight, el.closest(".archive-filter-frame").nextElementSibling.className, el.contains(document.querySelector(".month-chart"))
    ]), [en ? 230 : 156, "month-chart", false]);
    const year = p.locator("[data-chart-year]");
    async function checkMonths() {
      const counts = await p.locator("[data-archive-item]:visible").evaluateAll((els,y) => {
        const months = Array(12).fill(0);
        els.forEach(e => { if (e.dataset.date.startsWith(y+"-")) months[Number(e.dataset.date.slice(5,7))-1]++; });
        return months;
      }, await year.inputValue());
      assert.deepEqual((await p.locator("[data-month] b").allTextContents()).map(Number), counts);
      const n = counts.reduce((a,b) => a+b,0);
      const y = await year.inputValue();
      const label = await year.locator("option:checked").innerText();
      assert.equal(label, await p.locator("html").getAttribute("lang") === "en" ? y+" ("+n+")" : y+"（"+n+"）");
    }
    await checkMonths();
    const visible = p.locator("[data-archive-item]:visible");
    const month = (await visible.first().getAttribute("data-date")).slice(0,7);
    await year.selectOption(month.slice(0,4));
    const bar = p.locator('button[data-month="'+month.slice(5)+'"]');
    const total = await visible.count();
    const counts = await p.locator("[data-month] b").allTextContents();
    const annualLabel = await year.locator("option:checked").innerText();
    await bar.focus(); await bar.press("Enter");
    await p.waitForURL(u => u.searchParams.get("month") === month);
    assert.deepEqual(await p.locator("[data-month] b").allTextContents(), counts);
    assert.equal(await year.locator("option:checked").innerText(),annualLabel);
    assert.equal(await visible.count(), Number(await bar.getAttribute("data-count")));
    assert.ok(await visible.evaluateAll((rows,m) => rows.every(row => row.dataset.date.startsWith(m+"-")),month));
    assert.equal(Number(await p.locator("[data-archive-count]").innerText()),await visible.count());
    await p.reload();
    assert.equal(await bar.getAttribute("aria-pressed"),"true");
    await p.locator(".nav-lang").click();
    await p.locator('button[data-month][aria-pressed="true"]').waitFor();
    assert.equal(await year.inputValue(),month.slice(0,4));
    assert.equal(new URL(p.url()).searchParams.get("category"),"tech");
    await bar.click();
    await p.waitForURL(u => !u.searchParams.has("month"));
    assert.equal(await visible.count(),total);
    await p.goBack();
    assert.equal(await bar.getAttribute("aria-pressed"),"true");
    await year.selectOption({index: await year.evaluate(el => el.selectedIndex === 0 ? 1 : 0)});
    assert.equal(await bar.getAttribute("aria-pressed"),"false");
    await checkMonths();
    await p.locator("[data-archive-query]").fill("no-such-note-000"); await checkMonths();
    await p.locator("button[data-month]").first().click();
    assert.ok(await p.locator("[data-archive-empty]").isVisible());
    // Same build, two visits straddling midnight on January 1 in Shanghai.
    const newest = Number(await year.locator("option").first().getAttribute("value"));
    for (const [hour, expected] of [[15,newest+1],[16,newest+2]]) {
      await p.clock.setFixedTime(new Date(Date.UTC(newest+1,11,31,hour)));
      await go(lang+"/archive/");
      assert.equal(await year.inputValue(),String(expected));
      await checkMonths();
      assert.equal(await year.locator("option:checked").innerText(),en ? expected+" (0)" : expected+"（0）");
    }
    await go(lang + "/pages/");
    assert.equal(await p.locator(".pages-page .directory-mast").count(),0);
    assert.ok(await p.locator(".pages-page > .section-head").isVisible());

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
