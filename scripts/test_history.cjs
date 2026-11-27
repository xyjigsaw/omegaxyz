// Run against the local build with SITE_PREVIEW and CHROME_PATH, like test_reader_paths.cjs.
const assert = require("node:assert/strict");
const {chromium} = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");

async function exercise(browser, lang, width, js=true){
  const mobile=width<700;
  const context=await browser.newContext({viewport:{width,height:820},isMobile:mobile,hasTouch:mobile,
    colorScheme:mobile?"dark":"light",reducedMotion:mobile?"reduce":"no-preference",javaScriptEnabled:js});
  try {
    const p=await context.newPage(), errors=[];
    p.on("pageerror",err=>errors.push(String(err)));
    await p.route("**/*",r=>new URL(r.request().url()).origin===base.origin?r.continue():r.abort());
    const path=s=>new URL(lang+"/"+s,base).href;
    await p.goto(path("archive/"));
    const heading=p.locator(".archive-heading"), graph=heading.getByRole("link",{name:lang==="en"?"Article Graph":"文章关联图谱"});
    const [h,g,num]=await Promise.all([heading.locator("h1").boundingBox(),graph.boundingBox(),p.locator(".archive-count").boundingBox()]);
    assert.ok(h.x+h.width<=g.x+1 && g.y<h.y+h.height && g.x+g.width<=num.x+1 && num.x+num.width<=width);
    assert.ok(g.height>=44);await graph.click();
    await p.waitForURL(path("article-graph/"));

    await p.goto(path("webhistory/index.html"));
    const log=p.locator(".history-log"), nav=p.locator(".history-scale");
    const dates=await log.locator("time").evaluateAll(els=>els.map(e=>e.dateTime));
    assert.ok(dates.length>1);assert.deepEqual(dates,dates.slice().sort().reverse());
    const years=[...new Set(dates.map(d=>d.slice(0,4)))];
    assert.deepEqual(await nav.locator("a").allTextContents(),years);
    assert.equal(await log.locator(".history-year").count(),years.length);
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    const year=years.find(y=>dates.filter(d=>d.startsWith(y)).length>1);
    const target="#year-"+year, link=nav.locator('a[href="'+target+'"]');
    await link.click();await p.waitForURL(u=>u.hash===target);
    if(js){
      await p.waitForFunction(id=>document.querySelector(".history-year[data-active]")?.id===id,target.slice(1));
      assert.equal(await link.getAttribute("aria-current"),"location");
      assert.ok((await p.locator(".nav-lang").getAttribute("href")).endsWith(target));
      const local=p.locator(target+" .history-event").nth(1);
      // Manual reading within a year advances the node as well as the long spine.
      await local.evaluate(el=>{const nav=document.querySelector(".history-nav");
        const offset=document.querySelector(".site-header").offsetHeight+nav.offsetHeight+40;
        const pin=el.querySelector(".history-pin").getBoundingClientRect();
        scrollBy({top:pin.top-offset,behavior:"instant"});});
      await p.waitForFunction(id=>document.querySelector(id+" .history-event:nth-child(2)")?.hasAttribute("data-current"),target);
      const progress=await log.evaluate(el=>Number(el.style.getPropertyValue("--progress")));
      assert.ok(progress>0 && progress<1);
      assert.equal(await p.locator("[data-current] .history-pin").evaluate(el=>getComputedStyle(el).animationName),
        mobile?"none":"signal-arrival");
      const sticky=await p.locator(".history-nav").boundingBox(), mast=await p.locator(".site-header").boundingBox();
      assert.ok(Math.abs(sticky.y-mast.height)<2);
      await p.locator(".nav-lang").click();
      await p.waitForURL(u=>u.pathname.startsWith(lang==="en"?"/zh/":"/en/")&&u.hash===target);
      await p.waitForSelector(target+"[data-active]");
    }else{
      assert.ok(await p.locator(target+" time").first().isVisible());
      const r=await p.locator(target).boundingBox();assert.ok(r.y>0 && r.y<220);
    }
    assert.deepEqual(errors,[]);
    console.log(lang,width,js?"archive link, history navigation, progress and language switch OK":"native year links without JavaScript OK");
  }finally{await context.close();}
}
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.CHROME_PATH});
  try{await exercise(browser,"en",1366);await exercise(browser,"zh",390);await exercise(browser,"en",320,false);}
  finally{await browser.close();}
})().catch(err=>{console.error(err);process.exitCode=1;});
