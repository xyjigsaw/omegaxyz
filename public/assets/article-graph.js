const root=document.querySelector("[data-graph]"), en=document.documentElement.lang==="en";
const $=s=>root.querySelector(s);
const label=(zh,eng)=>en?eng:zh;
function element(tag,text,cls){
  const e=document.createElement(tag);if(text!=null)e.textContent=text;if(cls)e.className=cls;return e;
}
function boot({terms,nodes}){
  const search=$("[data-graph-query]"),category=$("[data-graph-cat]"),results=$("[data-graph-results]");
  const detail=$("[data-graph-detail]"),more=$(".graph-more"),field=$(".graph-field");
  let selected=-1,visible=[],lookup=new Set(),limit=18,view;
  const catalogue=nodes.map(n=>[n.title,...n.terms.map(t=>terms[t].name+" "+terms[t].slug)].join(" ").toLowerCase());
  const keys=i=>nodes[i].terms;
  function reasons(i,j){
    const shared=keys(i).filter(t=>keys(j).includes(t)).slice(0,2);
    return shared.map(t=>terms[t].name).join(" · ");
  }
  function inspect(){
    detail.replaceChildren();
    if(selected<0){detail.append(element("p",label("没有匹配的文章","No matching articles")));return;}
    const n=nodes[selected],time=element("time",n.date), title=element("h2",n.title);
    time.dateTime=n.date;title.tabIndex=-1;
    const open=element("a",label("阅读文章 ↗","Read article ↗"),"graph-read");open.href=n.url;
    const context=element("div",null,"graph-selection");
    context.append(element("span",label("当前文章","Selected article")),time);
    detail.append(context,title,open,element("h3",label("关联文章","Connected articles")));
    const list=element("ol");
    for(const j of n.near){
      const row=element("li"),b=element("button",nodes[j].title);
      b.type="button";b.addEventListener("click",()=>navigate(j));
      row.append(b,element("small",reasons(selected,j)));list.append(row);
    }
    if(!n.near.length)list.append(element("li",label("还没有共享主题的文章。","No shared topics yet.")));
    detail.append(list);
  }
  function directory(){
    results.replaceChildren(...visible.slice(0,limit).map(i=>{
      const row=element("li"),b=element("button",nodes[i].title);
      b.type="button";b.setAttribute("aria-pressed",i===selected);
      b.addEventListener("click",()=>{navigate(i);detail.querySelector("h2")?.focus();});
      row.append(element("time",nodes[i].date.slice(0,4)),b);return row;
    }));
    more.hidden=limit>=visible.length;$("[data-graph-count]").textContent=visible.length;
  }
  function navigate(i){
    if(!lookup.has(i)){category.value="";search.value="";filter(i);return;}
    selected=i;inspect();directory();view?.select(i);
  }
  function filter(preferred){
    const query=search.value.trim().toLowerCase();
    visible=nodes.map((_,i)=>i).filter(i=>(category.value==="" || keys(i).includes(Number(category.value))) && catalogue[i].includes(query));
    lookup=new Set(visible);limit=18;
    selected=lookup.has(preferred)?preferred:(lookup.has(selected)?selected:visible[0]??-1);
    inspect();directory();view?.layout(visible,selected);
  }
  more.addEventListener("click",()=>{limit+=36;directory();});
  search.addEventListener("input",()=>filter());category.addEventListener("change",()=>filter());
  $(".graph-workbench").hidden=false;$(".graph-status").hidden=true;filter();
  if(!nodes.length || navigator.connection?.saveData)return;
  const orbitURL=new URL("./graph-orbit-v1.js",import.meta.url);
  orbitURL.search=new URL(import.meta.url).search;
  Promise.all([import("./vendor/three-r160.min.js"),import("./vendor/d3-hierarchy-3.1.2.min.js"),import(orbitURL.href)])
    .then(([T,,orbit])=>{
      view=orbit.createScene(T,globalThis.d3,nodes,terms,field,i=>{navigate(i);const link=$(".graph-picked");
        link.href=nodes[i].url;link.textContent=nodes[i].title+" ↗";link.hidden=false;});
      field.hidden=false;view.layout(visible,selected);
    }).catch(()=>{field.hidden=true;});
}


fetch(new URL(root.dataset.graph,document.baseURI)).then(r=>{
  if(!r.ok)throw Error("graph");return r.json();
}).then(boot).catch(()=>{$(".graph-status").hidden=false;});
