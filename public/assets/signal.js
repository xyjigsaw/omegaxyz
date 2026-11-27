const page=document.querySelector(".signal-page");
const support=page.querySelector(".signal-support");
const compact=matchMedia("(max-width:700px)");
function sizeSupport(){support.open=!compact.matches;}
sizeSupport();compact.addEventListener("change",sizeSupport);

// The shared site script alone decides whether Giscus is allowed to load.
// Mirror that decision in the primary link without issuing another region lookup.
const block=page.querySelector("[data-giscus-comments]");
const mount=block?.querySelector("[data-giscus-mount]");
if(mount){
  const send=page.querySelector(".signal-send"),fallback=block.querySelector("[data-global-discussion-link]");
  const remote={href:send.href,label:send.textContent};
  const compose=document.createElement("div");
  compose.id="signal-compose";compose.tabIndex=-1;
  fallback.before(compose);compose.append(fallback,mount);
  function syncSend(){
    const inline=block.dataset.commentRegion==="global" && block.dataset.giscusState!=="failed";
    send.href=inline?"#signal-compose":remote.href;
    send.textContent=inline?send.dataset.sendLabel:remote.label;
    if(inline)send.removeAttribute("target");else send.target="_blank";
  }
  const observe=new MutationObserver(syncSend);
  observe.observe(block,{attributes:true,attributeFilter:["data-comment-region","data-giscus-state"]});
  syncSend();
}

const topics=Array.from(page.querySelectorAll(".signal-topic"));
const earlier=page.querySelector(".signal-earlier"), alternate=document.querySelector(".nav-lang");
const batch=10;
let shown=0, anchor=null;
function showUntil(n){
  shown=Math.min(n,topics.length);
  topics.forEach((topic,i)=>{topic.hidden=i>=shown;});
  if(earlier)earlier.hidden=shown===topics.length;
}
function alignAnchor(){
  if(anchor && Math.abs(anchor.getBoundingClientRect().top-parseFloat(getComputedStyle(anchor).scrollMarginTop))>2)
    anchor.scrollIntoView({block:"start",behavior:"instant"});
}
function restoreHash(){
  anchor=null;
  const id=location.hash.slice(1);
  const comment=/^comment-\d+$/.test(id)?document.getElementById(id):null;
  const index=topics.indexOf(comment?.closest(".signal-topic"));
  if(alternate)alternate.hash=index>=0?id:"";
  if(index>=0){
    showUntil(Math.max(shown,Math.ceil((index+1)/batch)*batch));
    anchor=comment;alignAnchor();
  }else if(!shown)showUntil(batch);
}
restoreHash();
window.addEventListener("hashchange",restoreHash);
// A late-loading discussion iframe or QR image above the archive can shift a deep link.
// Keep it aligned only until the reader starts interacting.
const resize=new ResizeObserver(alignAnchor);
for(const el of [page.querySelector(".signal-hero"),block])if(el)resize.observe(el);
for(const event of ["wheel","touchstart","pointerdown","keydown"])
  window.addEventListener(event,()=>{anchor=null;},{passive:true});
earlier?.addEventListener("click",()=>{
  const first=topics[shown]?.querySelector(".comment");
  showUntil(shown+batch);
  if(first){first.tabIndex=-1;first.focus({preventScroll:true});first.scrollIntoView({block:"nearest",behavior:"instant"});}
});
