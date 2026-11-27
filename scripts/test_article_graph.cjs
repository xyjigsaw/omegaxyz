// Run against a local build, with the same environment as test_terrain.cjs.
const assert = require("node:assert/strict");
const {chromium} = require("playwright");
const base = new URL(process.env.SITE_PREVIEW || "http://127.0.0.1:4173/");

async function inspectPixels(canvas) {
  return canvas.evaluate(el => {
    const box=el.getBoundingClientRect(), img=document.createElement("canvas");
    img.width=Math.round(box.width);img.height=Math.round(box.height);
    const ctx=img.getContext("2d");ctx.drawImage(el,0,0,img.width,img.height);
    const rgba=ctx.getImageData(0,0,img.width,img.height).data;
    let hash=0,opaque=0,hit=null;
    for(let i=0;i<rgba.length;i+=4){
      const a=rgba[i+3];hash=(Math.imul(hash,31)+a)>>>0;
      if(a<245)continue;opaque++;
      const x=(i/4)%img.width,y=Math.floor(i/4/img.width);
      if(!hit && x>20 && y>30 && document.elementFromPoint(box.left+x,box.top+y)===el)
        hit={x:box.left+x,y:box.top+y};
    }
    return {hash,opaque,hit};
  });
}

async function exercise(browser,lang,width,fallback=false){
  const mobile=width<800,ctx=await browser.newContext({viewport:{width,height:880},isMobile:mobile,
    hasTouch:mobile,colorScheme:mobile?"dark":"light",reducedMotion:"reduce"});
  try{
    const p=await ctx.newPage(),errors=[];p.on("pageerror",e=>errors.push(e.message));
    await p.route("**/*",r=>new URL(r.request().url()).origin===base.origin?r.continue():r.abort());
    await p.addInitScript(noGL=>{
      const orig=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(t,o){
        return noGL && t.includes("webgl")?null:orig.call(this,t,t.includes("webgl")?{...o,preserveDrawingBuffer:true}:o);
      };
    },fallback);
    await p.goto(new URL(lang+"/",base).href);
    assert.equal(await p.locator("header a[href*='article-graph']").count(),0);
    assert.equal(await p.locator(".page-strip a[href*='civ-globe-privacy']").count(),0);
    await p.locator(".page-strip a[href*='article-graph']").click();
    await p.locator(".graph-workbench").waitFor();const canvas=p.locator(".graph-stage canvas");
    const data=await p.locator("[data-graph]").evaluate(async root=>(await fetch(root.dataset.graph)).json());
    assert.equal(Number(await p.locator("[data-graph-count]").innerText()),data.nodes.length);
    const q=p.locator("[data-graph-query]"),cat=p.locator("[data-graph-cat]");
    if(!fallback){
      await p.locator(".graph-stage[data-ready]").waitFor();await canvas.scrollIntoViewIfNeeded();
      const first=await inspectPixels(canvas);assert.ok(first.opaque>500 && first.hit);
      const {x,y}=first.hit;
      if(mobile)await p.touchscreen.tap(x,y);else await p.mouse.click(x,y);
      await p.locator(".graph-picked:visible").waitFor();assert.equal(await p.locator(".graph-picked").getAttribute("href"),await p.locator(".graph-read").getAttribute("href"));
      await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      const before=(await inspectPixels(canvas)).hash;
      if(mobile){
        const c=await ctx.newCDPSession(p);
        for(const [type,touchPoints] of [["touchStart",[{x,y}]],["touchMove",[{x:x+65,y:y+2}]],["touchEnd",[]]])
          await c.send("Input.dispatchTouchEvent",{type,touchPoints});await c.detach();
      }else{await p.mouse.move(x,y);await p.mouse.down();await p.mouse.move(x+65,y+12,{steps:5});await p.mouse.up();}
      await p.waitForTimeout(90);
      assert.notEqual((await inspectPixels(canvas)).hash,before);
      await p.locator('[data-view="reset"]').click();await p.waitForTimeout(90);
      assert.equal((await inspectPixels(canvas)).hash,before);
      assert.ok(new URL(p.url()).pathname.includes("/article-graph/"));
    }else{assert.ok(await p.locator(".graph-field").isHidden());}
    const option=await cat.locator("option").nth(1).getAttribute("value");await cat.selectOption(option);
    assert.equal(Number(await p.locator("[data-graph-count]").innerText()),data.terms[Number(option)].count);
    await q.fill("!no-matching-article!");assert.equal(await p.locator("[data-graph-count]").innerText(),"0");
    await q.fill("");await cat.selectOption("");
    const before=await p.locator("[data-graph-results] li").count();await p.locator(".graph-more").click();
    assert.ok(await p.locator("[data-graph-results] li").count()>before);
    const indexButton=p.locator("[data-graph-results] button").nth(2), title=await indexButton.innerText();
    await indexButton.click();assert.equal(await p.locator(".graph-inspector h2").innerText(),title);
    await p.locator(".graph-inspector li button").first().click();
    assert.notEqual(await p.locator(".graph-inspector h2").innerText(),title);
    const href=await p.locator(".graph-read").getAttribute("href");assert.ok(href.startsWith("/"+lang+"/"));
    assert.ok((await ctx.request.get(new URL(href,base).href)).ok());
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);console.log(lang,width,fallback?"text-only graph OK":"pixels, picking, rotation, filters and links OK");
  }finally{await ctx.close();}
}
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME_PATH,args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
  try{await exercise(b,"zh",390);await exercise(b,"en",1366);await exercise(b,"en",669,true);}
  finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
