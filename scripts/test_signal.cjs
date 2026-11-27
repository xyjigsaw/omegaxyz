// Optional browser checks against a local build. Third-party region/widget states are fixtures.
const assert=require("node:assert/strict");
const {chromium}=require("playwright");
const base=new URL(process.env.SITE_PREVIEW||"http://127.0.0.1:4173/");
const discussion="https://github.com/xyjigsaw/omegaxyz/discussions/5";

async function exercise(browser,lang,width,js=true){
  const mobile=width<=700, url=(p)=>new URL(p,base).href;
  const c=await browser.newContext({viewport:{width,height:844},isMobile:mobile,hasTouch:mobile,
    javaScriptEnabled:js,reducedMotion:"reduce",colorScheme:mobile?"dark":"light"});
  try{
    const p=await c.newPage(),errors=[];p.on("pageerror",err=>errors.push(String(err)));
    let region="CN",fail=false,widgets=0;
    await p.route("**/*",r=>{
      const u=new URL(r.request().url());
      if(u.origin===base.origin)return r.continue();
      if(["ipapi.co","api.country.is"].includes(u.hostname))return region?r.fulfill({json:{country_code:region,ip:"2001:db8::1234"}}):r.abort();
      if(u.href==="https://giscus.app/client.js"){
        widgets++;return fail?r.abort():r.fulfill({contentType:"application/javascript",body:
          'const f=document.createElement("iframe");f.src="https://giscus.app/widget";f.className="giscus-frame";document.querySelector("[data-giscus-mount]").append(f);'});
      }
      if(u.href==="https://giscus.app/widget")return r.fulfill({contentType:"text/html",body:"Discussion fixture"});
      return r.abort();
    });
    const route=lang+"/comment/", go=(path=route)=>p.goto(url(path),{waitUntil:"domcontentloaded"});
    const visible=p.locator(".signal-topic:visible"), all=p.locator(".signal-topic"), main=p.locator(".signal-send");
    const support=p.locator(".signal-support"),note=p.locator("[data-mainland-comment-note]");
    async function aligned(id){
      await p.waitForFunction(id=>{
        const e=document.getElementById(id),r=e.getBoundingClientRect(),mast=document.querySelector(".site-header").getBoundingClientRect();
        return e.offsetHeight && r.top>=mast.bottom-1 && r.top<mast.bottom+60;
      },id,{timeout:5000});
    }
    await go();const n=await all.count();assert.ok(n>20);
    const deep=await all.nth(30).locator(".comment").last().getAttribute("id");
    const reply=await p.locator(".signal-topic:nth-last-of-type(-n+30) .reply").first().getAttribute("id");
    if(!js){
      assert.equal(await visible.count(),n);await go(route+"#"+reply);await aligned(reply);
      assert.equal(await main.getAttribute("href"),discussion);
      await go("comment/#"+reply);
      await p.waitForFunction(id=>{const r=document.getElementById(id).getBoundingClientRect();
        return r.height>0 && r.top>=0 && r.top<120;},reply);
      console.log(lang,width,"native links on canonical and legacy pages work without JavaScript");return;
    }
    await p.waitForFunction(()=>document.querySelector("[data-ip-status]").textContent.includes("2001:db8"));
    assert.equal(widgets,0);assert.ok(await note.isVisible());assert.equal(await main.getAttribute("href"),discussion);
    assert.equal(await visible.count(),10);assert.equal(await support.evaluate(d=>d.open),!mobile);
    if(mobile)await support.locator("summary").click();
    for(const a of await support.locator("figure a").all()){
      assert.equal(await a.getAttribute("href"),await a.locator("img").getAttribute("src"));
      assert.equal(await a.getAttribute("target"),"_blank");
    }
    if(mobile)await support.locator("summary").click();
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await p.locator(".signal-earlier").click();assert.equal(await visible.count(),20);
    assert.equal(await p.evaluate(()=>document.activeElement.id),await all.nth(10).locator(".comment").first().getAttribute("id"));
    await p.evaluate(id=>location.hash=id,deep);await aligned(deep);assert.equal(await visible.count(),40);
    await go(route+"index.html#"+reply);await aligned(reply);
    const anchor=p.locator("#"+reply);
    assert.ok(await anchor.evaluate(el=>[...el.closest(".signal-topic").children].every(e=>e.offsetHeight>0)));
    await p.locator(".nav-lang").click();await p.waitForURL(u=>u.hash==="#"+reply && !u.pathname.startsWith("/"+lang+"/"));
    await aligned(reply);
    await go("comment/#"+reply);await p.waitForURL(u=>u.pathname==="/zh/comment/index.html" && u.hash==="#"+reply);
    await aligned(reply);assert.equal(widgets,0);
    region=null;await go();await p.waitForFunction(()=>/unavailable|无法识别/.test(document.querySelector("[data-ip-status]").textContent));
    assert.equal(widgets,0);assert.equal(await main.getAttribute("href"),discussion);
    region="US";fail=true;await go();
    await p.waitForSelector('[data-giscus-state="failed"]');assert.ok(await note.isHidden());
    assert.equal(await main.getAttribute("href"),discussion);
    fail=false;await go(route+"index.html#"+reply);
    await p.waitForSelector("iframe.giscus-frame");await aligned(reply);
    await p.locator("iframe.giscus-frame").evaluate(f=>f.style.height="550px");
    await aligned(reply);
    const frame=p.frames().find(f=>f.url()==="https://giscus.app/widget");
    await frame.evaluate(()=>parent.postMessage({giscus:{resizeHeight:550}},"*"));
    await p.waitForSelector('[data-giscus-state="ready"]');assert.equal(await main.getAttribute("href"),"#signal-compose");
    await main.click();await aligned("signal-compose");assert.ok(await p.locator("[data-global-discussion-link]").isHidden());
    assert.deepEqual(errors,[]);
    console.log(lang,width,"region gate, QR disclosure, complete threads, legacy/reply anchors, composer and fallback passed");
  }finally{await c.close();}
}
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_PATH});
  try{await exercise(b,"en",1366);await exercise(b,"zh",390);await exercise(b,"en",320,false);}
  finally{await b.close();}
})().catch(err=>{console.error(err);process.exitCode=1;});
