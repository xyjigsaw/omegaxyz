// Optional browser regression: serve docs/ and run with Playwright installed.
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");

async function fingerprints(canvas) {
  return canvas.evaluate(el => {
    const sample = document.createElement("canvas");
    sample.width = 160; sample.height = 120;
    const g = sample.getContext("2d");
    g.drawImage(el, 0, 0, 160, 120);
    const pixels = g.getImageData(0, 0, 160, 120).data;
    let alpha = 0, color = 0, visible = 0;
    for (let i = 0; i < pixels.length; i += 4) {
      alpha = (alpha * 31 + pixels[i + 3]) >>> 0;
      color = (color * 31 + pixels[i] * 7 + pixels[i + 1] * 3 + pixels[i + 2]) >>> 0;
      if (pixels[i + 3] > 100) visible++;
    }
    return { alpha, color, visible };
  });
}

async function exercise(browser, mobile) {
  const lang = mobile ? "zh" : "en";
  const ctx = await browser.newContext({viewport: mobile ? {width:390,height:820} : {width:1366,height:840},
    isMobile:mobile, hasTouch:mobile, colorScheme:mobile ? "dark" : "light"});
  try {
    const p = await ctx.newPage(), home = new URL(lang + "/categories/", base).href;
    await p.route("**/*", r => new URL(r.request().url()).origin === base.origin ? r.continue() : r.abort());
    await p.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function(type, opts) {
        return original.call(this, type, type.startsWith("webgl") ? {...opts, preserveDrawingBuffer:true} : opts);
      };
    });
    await p.goto(home);
    const canvas = p.locator(".terrain-stage[data-ready] canvas"), label = p.locator("[data-peak-label]");
    await canvas.waitFor();
    const pause = p.locator("[data-terrain-pause]"), reset = p.locator("[data-terrain-reset]");
    const first = await fingerprints(canvas);
    assert.ok(first.visible > 1500, "non-blank terrain");
    await p.waitForTimeout(550);
    const second = await fingerprints(canvas);
    assert.equal(first.alpha, second.alpha, "palette must not move the terrain");
    assert.notEqual(first.color, second.color, "palette is changing");
    await pause.click(); await p.waitForTimeout(150);
    const still = await fingerprints(canvas);
    await p.waitForTimeout(200); assert.deepEqual(still, await fingerprints(canvas));

    const b = await canvas.boundingBox(), x = b.x + b.width * .43, y = b.y + b.height * .67;
    async function drag() {
      if (mobile) {
        const client = await ctx.newCDPSession(p);
        for (const [type, points] of [["touchStart", [{x,y}]], ["touchMove", [{x:x+78,y:y+4}]], ["touchEnd", []]]) {
          await client.send("Input.dispatchTouchEvent", {type,touchPoints:points});
        }
        await client.detach();
      } else {
        await p.mouse.move(x,y); await p.mouse.down();
        await p.mouse.move(x+120,y+48,{steps:5}); await p.mouse.up();
      }
      await p.waitForTimeout(140);
      assert.equal(p.url(), home, "drag release must not navigate");
      assert.notEqual((await fingerprints(canvas)).alpha, first.alpha, "drag actually rotated the view");
    }
    await drag(); await reset.click(); await p.waitForTimeout(120);
    assert.equal((await fingerprints(canvas)).alpha, first.alpha, "reset restores the initial camera");
    await drag();
    // Locate a real summit via its projected label, without importing scene internals.
    const peaks = p.locator(".category-cloud [data-peak]");
    await peaks.first().evaluate(a => a.focus({preventScroll:true}));
    await p.waitForTimeout(100);
    const target = await label.evaluate(a => {
      const r = a.getBoundingClientRect();
      return {href:a.href,x:r.left-3,y:r.bottom+2};
    });
    assert.equal(target.href, await peaks.first().evaluate(a=>a.href));
    assert.ok(await p.evaluate(({x,y}) => document.elementFromPoint(x,y)?.tagName === "CANVAS", target));
    await Promise.all([p.waitForURL(target.href), mobile ? p.touchscreen.tap(target.x,target.y) : p.mouse.click(target.x,target.y)]);
    await p.goto(home); await canvas.waitFor();
    const labelUrl = await label.evaluate(a=>a.href);
    await Promise.all([p.waitForURL(labelUrl), mobile ? label.tap() : label.click()]);
    if (mobile) {
      await p.emulateMedia({reducedMotion:"reduce"}); await p.goto(home); await canvas.waitFor();
      const a = await fingerprints(canvas); await p.waitForTimeout(250);
      assert.deepEqual(a, await fingerprints(canvas), "reduced motion freezes the palette");
      const client = await ctx.newCDPSession(p);
      await client.send("Input.dispatchTouchEvent",{type:"touchStart",touchPoints:[{x,y}]});
      for (const dy of [20,50,100])
        await client.send("Input.dispatchTouchEvent",{type:"touchMove",touchPoints:[{x,y:y-dy}]});
      await client.send("Input.dispatchTouchEvent",{type:"touchEnd",touchPoints:[]});
      await client.detach(); await p.waitForFunction(()=>scrollY>12);
      assert.equal(p.url(),home,"vertical touch scroll must not navigate");
    }
    console.log(lang + ": palette, fixed relief, drag, reset and summit navigation OK");
  } finally { await ctx.close(); }
}

(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROME_PATH,
    args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
  try { await exercise(browser,false); await exercise(browser,true); }
  finally { await browser.close(); }
})().catch(e=>{ console.error(e); process.exitCode=1; });
