const page=document.querySelector(".timeline-page");
const mast=document.querySelector(".site-header"), nav=page.querySelector(".history-nav");
const scale=nav.querySelector(".history-scale"), log=page.querySelector(".history-log");
const links=new Map(Array.from(scale.querySelectorAll("a"),a=>[a.hash.slice(1),a]));
const events=Array.from(log.querySelectorAll(".history-event"),el=>({
  el, pin:el.querySelector(".history-pin"), group:el.closest(".history-year")
}));
const alternate=document.querySelector(".nav-lang");
let centers=[], guide=0, frame=0, dirty=true, current=-1;

function measure(){
  const top=mast.offsetHeight, height=nav.offsetHeight;
  page.style.setProperty("--mast",top+"px");
  page.style.setProperty("--scale-h",height+"px");
  const bounds=log.getBoundingClientRect();
  centers=events.map(({pin})=>{
    const b=pin.getBoundingClientRect();
    return scrollY+b.top+b.height/2;
  });
  const first=centers[0], last=centers.at(-1);
  log.style.setProperty("--rail-top",first-scrollY-bounds.top+"px");
  log.style.setProperty("--rail-bottom",scrollY+bounds.bottom-last+"px");
  guide=top+height+52;
  dirty=false;
}
function activate(next){
  const prev=events[current], item=events[next], group=item.group;
  prev?.el.removeAttribute("data-current");
  item.el.setAttribute("data-current","");
  if(prev?.group!==group){
    prev?.group.removeAttribute("data-active");
    if(prev)links.get(prev.group.id).removeAttribute("aria-current");
    const link=links.get(group.id);
    link.setAttribute("aria-current","location");
    group.setAttribute("data-active","");
    if(alternate)alternate.hash=group.id;
    // Reveal the year horizontally without pulling the reader back up to the nav.
    const r=link.getBoundingClientRect(), bounds=scale.getBoundingClientRect();
    if(r.left<bounds.left)scale.scrollLeft+=r.left-bounds.left;
    else if(r.right>bounds.right)scale.scrollLeft+=r.right-bounds.right;
  }
  current=next;
}
function draw(){
  frame=0;
  if(dirty)measure();
  const reading=scrollY+guide, first=centers[0], last=centers.at(-1);
  const progress=Math.min(1,Math.max(0,(reading-first)/Math.max(1,last-first)));
  log.style.setProperty("--progress",String(progress));
  let i=current<0?0:current;
  while(i+1<centers.length && centers[i+1]<=reading)i++;
  while(i>0 && centers[i]>reading)i--;
  if(i!==current)activate(i);
}
function schedule(){if(!frame)frame=requestAnimationFrame(draw);}
function resize(){dirty=true;schedule();}
if(events.length){
  draw();
  window.addEventListener("scroll",schedule,{passive:true});
  window.addEventListener("pageshow",resize);
  const size=new ResizeObserver(resize);
  for(const el of [mast,nav,log])size.observe(el);
  document.fonts?.ready.then(resize);
}
