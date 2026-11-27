// Arrange a single record per post on dated annuli, within its most specific category.
// Keep coordinates fixed when filtering so a reader can follow the same point.
function ephemeris(d3,nodes,terms){
  const TAU=2*Math.PI, groups=new Map(), counts=new Map(), positions=[], rows=[];
  const years=nodes.map(n=>Number(n.date.slice(0,4))), start=Math.min(...years),end=Math.max(...years);
  nodes.forEach((n,i)=>{
    const cat=n.terms.find(t=>terms[t].cat)??-1;
    if(!groups.has(cat))groups.set(cat,{cat,ids:[]});
    groups.get(cat).ids.push(i);counts.set(years[i],(counts.get(years[i])||0)+1);
  });
  // Give sparse years a readable band without crushing the hundreds of early notes.
  let weight=0;
  for(let y=start;y<=end;y++){const w=2+Math.sqrt(counts.get(y)||0);rows.push({year:y,w});weight+=w;}
  let cursor=.16;
  for(const b of rows){
    b.lo=cursor;cursor+=.84*b.w/weight;b.hi=cursor;b.r=(b.lo+b.hi)/2;
    b.z=.22*(b.year-start)/Math.max(1,end-start)-.11;
  }
  const root=d3.hierarchy({children:[...groups.values()]}).sum(d=>d.ids?.length||0)
    .sort((a,b)=>b.value-a.value || a.data.cat-b.data.cat);
  d3.partition().size([TAU,1])(root);
  const at=(angle,r,z)=>[Math.cos(angle)*r,Math.sin(angle)*r,z];
  const sectors=[];
  for(const child of root.children){
    const {cat,ids}=child.data,from=child.x0+.26,to=child.x1+.26;
    sectors.push({cat,from,to,mid:(from+to)/2,size:ids.length});
    const parts=new Map();
    for(const i of ids){if(!parts.has(years[i]))parts.set(years[i],[]);parts.get(years[i]).push(i);}
    for(const [y,batch] of parts){
      const band=rows[y-start];
      batch.forEach((id,k)=>{
        // A low-discrepancy sequence fills each band without stacking same-day posts.
        const f=(k*.61803398875+.5)%1, angle=from+(to-from)*(.045+.91*(k+.5)/batch.length);
        const r=band.lo+(band.hi-band.lo)*(.12+.76*f);
        positions[id]={p:at(angle,r,band.z),cat};
      });
    }
  }
  return {positions,sectors,rows,at};
}

export function createScene(T,d3,nodes,terms,field,onPick){
  const stage=field.querySelector(".graph-stage"), map=ephemeris(d3,nodes,terms);
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:"low-power"});
  const dpr=Math.min(devicePixelRatio,1.8);renderer.setPixelRatio(dpr);renderer.setClearColor(0,0);
  const canvas=renderer.domElement;canvas.setAttribute("aria-hidden","true");stage.append(canvas);
  const scene=new T.Scene(),camera=new T.OrthographicCamera(-1,1,1,-1,.1,32), group=new T.Group();
  camera.position.z=6;scene.add(group);
  const TAU=2*Math.PI,polar=map.at;
  const sectorIndex=new Map(map.sectors.map((s,i)=>[s.cat,i]));
  const themedLines=new Map();
  let pigments=[],selectedInk,relatedInk,pulseInk;
  const def={yaw:-.18,pitch:-.82,roll:-.19};
  const reduced=matchMedia("(prefers-reduced-motion: reduce)");
  let yaw=def.yaw,pitch=def.pitch,zoom=1,frame=0,dead=false,w0=0,h0=0,press=null;
  let ids=[],sel=-1,screen=[],active=new Set();
  const v=new T.Vector3(),vector=p=>new T.Vector3(...p);
  function schedule(){if(!dead&&!frame)frame=requestAnimationFrame(draw);}
  function geom(object,coords){
    object.geometry.dispose();object.geometry=new T.BufferGeometry();
    object.geometry.setAttribute("position",new T.Float32BufferAttribute(coords,3));
  }
  function wires(role,opacity,order){
    const material=new T.LineBasicMaterial({opacity,transparent:true,depthWrite:false});
    themedLines.set(role,material);
    const obj=new T.LineSegments(new T.BufferGeometry(),material);
    obj.renderOrder=order;group.add(obj);return obj;
  }
  function arc(arr,r,z,a,b,n){
    for(let j=0;j<n;j++)arr.push(...polar(a+(b-a)*j/n,r,z),...polar(a+(b-a)*(j+1)/n,r,z));
  }
  const rings=[],rulers=[],rims=[],accents=[],axis=.92;
  arc(rulers,.039,-.11,0,TAU,40);
  rulers.push(-.065,0,-.11,.065,0,-.11,0,-.065,-.11,0,.065,-.11);
  for(const b of map.rows){
    arc(rings,b.r,b.z,0,TAU,180);
    rulers.push(...polar(axis,b.r-.009,b.z),...polar(axis,b.r+.01,b.z));
  }
  arc(rims,1.048,.12,0,TAU,224);
  for(let k=0;k<180;k++)rulers.push(...polar(k*TAU/180,1.057,.12),...polar(k*TAU/180,k%15===0?1.086:k%5===0?1.076:1.064,.12));
  for(const s of map.sectors.filter(s=>s.size>=nodes.length*.025)){
    arc(accents,1.033,.12,s.from+.014,s.to-.014,36);
    rulers.push(...polar(s.from,.20,-.11),...polar(s.from,1.04,.12));
  }
  geom(wires("rings",.39,0),rings);geom(wires("rulers",.36,0),rulers);
  geom(wires("rims",.56,0),rims);geom(wires("accents",.75,1),accents);
  const focus=wires("focus",.93,3),traces=wires("traces",.21,1);
  const dotMat=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{dpr:{value:dpr},night:{value:0},smallScale:{value:1}},
    vertexShader:"attribute float radius;attribute vec3 tint;varying vec3 ink;uniform float dpr,smallScale;void main(){ink=tint;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);gl_PointSize=radius*dpr*mix(smallScale,1.,smoothstep(8.,15.,radius));}",
    fragmentShader:"varying vec3 ink;uniform float night;void main(){float r=length(gl_PointCoord-.5)*2.;if(r>1.)discard;float core=1.-smoothstep(.2,.51,r);float glow=exp(-4.*r*r);float day=1.-smoothstep(.44,.78,r);gl_FragColor=vec4(mix(ink,vec3(.92,1.,1.),night*core*.38),mix(day,max(core,glow*.67),night));\n#include <colorspace_fragment>\n}"});
  const dots=new T.Points(new T.BufferGeometry(),dotMat);dots.renderOrder=4;group.add(dots);
  const pulse=new T.Points(new T.BufferGeometry(),dotMat);
  pulse.renderOrder=6;pulse.frustumCulled=false;group.add(pulse);
  let curves=[],phaseStart=0;
  // A hollow reticle marks the selected article even when the graph is dense.
  const reticle=new T.LineLoop(new T.BufferGeometry().setFromPoints(Array.from({length:54},(_,k)=>
    new T.Vector3(.028*Math.cos(TAU*k/54),.028*Math.sin(TAU*k/54),0))),
  new T.LineBasicMaterial({depthTest:false,transparent:true,opacity:.93}));reticle.renderOrder=5;group.add(reticle);
  const annotations=[];
  function annotate(text,p,kind){
    const el=document.createElement("span");el.className="orbit-label "+kind;el.textContent=text;stage.append(el);
    annotations.push({el,p,kind});
  }
  // These are physical annotations: they project with their ring or sector.
  for(const s of map.sectors.slice(0,4)){
    annotate(terms[s.cat]?.name||(document.documentElement.lang==="zh"?"未分类":"Uncategorized"),polar(s.mid,1.137,.12),"sector");
  }
  const labeled=new Set([0,Math.floor((map.rows.length-1)*.5),map.rows.length-1]);
  for(const i of labeled){
    const b=map.rows[i];annotate(String(b.year),polar(axis,b.r,b.z),"year");
  }
  function connect(arr,a,b,lift){
    const start=vector(map.positions[a].p),end=vector(map.positions[b].p);
    const mid=start.clone().lerp(end,.5);mid.z+=lift;
    const curve=new T.QuadraticBezierCurve3(start,mid,end), steps=curve.getPoints(lift>.1?32:8);
    for(let k=1;k<steps.length;k++)arr.push(...steps[k-1].toArray(),...steps[k].toArray());
    return curve;
  }
  function paintPoints(){
    const neighbors=new Set(nodes[sel]?.near||[]), c=[];
    for(const id of ids){
      const ink=id===sel?selectedInk:neighbors.has(id)?relatedInk:pigments[sectorIndex.get(map.positions[id].cat)%pigments.length];
      c.push(ink.r,ink.g,ink.b);
    }
    dots.geometry.setAttribute("tint",new T.Float32BufferAttribute(c,3));
    pulse.geometry.setAttribute("tint",new T.Float32BufferAttribute(curves.flatMap(()=>pulseInk.toArray()),3));
  }
  // Repaint the existing buffers; a theme change must not replay a selection or reset the camera.
  function syncTheme(){
    const style=getComputedStyle(field),read=role=>style.getPropertyValue("--orbit-"+role).trim();
    for(const [role,material] of themedLines)material.color.set(read(role));
    pigments=read("pigments").split(/\s+/).map(s=>new T.Color(s));
    selectedInk=new T.Color(read("selected"));relatedInk=new T.Color(read("related"));pulseInk=new T.Color(read("pulse"));
    reticle.material.color.set(read("focus"));
    dotMat.uniforms.night.value=document.documentElement.dataset.theme==="dark"?1:0;
    paintPoints();schedule();
  }
  function select(i){
    sel=i;curves=[];
    const neighbors=new Set(nodes[i]?.near||[]),sizes=[],links=[];
    for(const id of ids){
      const related=neighbors.has(id);
      sizes.push(id===i?21:related?15:ids.length<75?12:8);
      if(related && active.has(i))curves.push(connect(links,i,id,.16+.2*vector(map.positions[i].p).distanceTo(vector(map.positions[id].p))));
    }
    dots.geometry.setAttribute("radius",new T.Float32BufferAttribute(sizes,1));
    reticle.visible=active.has(sel);if(reticle.visible)reticle.position.fromArray(map.positions[i].p);
    geom(focus,links);field.querySelector(".graph-picked").hidden=true;
    geom(pulse,new Float32Array(curves.length*3));
    pulse.geometry.setAttribute("radius",new T.Float32BufferAttribute(curves.map(()=>14),1));
    paintPoints();
    phaseStart=performance.now();schedule();
  }
  function layout(list,i){
    ids=list;active=new Set(ids);const coords=[],links=[],seen=new Set();
    for(const id of ids){
      const p=map.positions[id];coords.push(...p.p);
      // Keep global context quiet; only a short, genuine local tie per article.
      const j=nodes[id].near.find(j=>active.has(j)&&map.positions[j].cat===p.cat);
      if(j==null)continue;
      const key=Math.min(j,id)+":"+Math.max(j,id);
      if(seen.has(key)||vector(p.p).distanceTo(vector(map.positions[j].p))>.23)continue;
      seen.add(key);connect(links,id,j,.025);
    }
    geom(dots,coords);geom(traces,links);select(i);
  }
  function draw(now){
    frame=0;const w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;
    if(w!==w0||h!==h0){renderer.setSize(w,h,false);w0=w;h0=h;}
    const aspect=w/h,extent=Math.max(1.21,aspect*.87)/zoom;
    dotMat.uniforms.smallScale.value=dotMat.uniforms.night.value ? 1 : Math.min(1,Math.max(.6,w/600));
    camera.left=-extent;camera.right=extent;camera.top=extent/aspect;camera.bottom=-camera.top;camera.updateProjectionMatrix();
    group.rotation.set(pitch,yaw,def.roll,"YXZ");group.updateMatrixWorld(true);camera.updateMatrixWorld();
    reticle.quaternion.copy(group.quaternion).invert();
    const progress=(now-phaseStart)/1100;
    pulse.visible=curves.length>0 && progress>=0 && progress<1 && !reduced.matches && !document.hidden;
    if(pulse.visible){
      const pos=pulse.geometry.attributes.position;
      curves.forEach((curve,k)=>{curve.getPoint(progress,v);pos.setXYZ(k,v.x,v.y,v.z);});
      pos.needsUpdate=true;schedule();
    }
    renderer.render(scene,camera);
    function project(p){v.fromArray(p).applyMatrix4(group.matrixWorld).project(camera);return {x:(1+v.x)*w/2,y:(1-v.y)*h/2};}
    screen=ids.map(i=>({...project(map.positions[i].p),i}));
    const taken=[];
    for(const l of annotations){
      const p=project(l.p),lw=l.el.offsetWidth,lh=l.el.offsetHeight,x=p.x-lw/2,y=p.y-lh/2;
      const fits=x>=2&&x+lw<w-2&&y>=4&&y+lh<h-4&&!taken.some(r=>x<r.x+r.w+5&&x+lw+5>r.x&&y<r.y+r.h+3&&y+lh+3>r.y);
      l.el.style.visibility=fits?"visible":"hidden";
      if(fits){l.el.style.transform="translate("+x+"px,"+y+"px)";taken.push({x,y,w:lw,h:lh});}
    }
    stage.dataset.ready="true";
  }
  function pick(e){
    const b=canvas.getBoundingClientRect(), x=e.clientX-b.left,y=e.clientY-b.top;
    let best=null,dist=e.pointerType==="touch"?17:9;
    for(const p of screen){const d=Math.hypot(p.x-x,p.y-y);if(d<dist){dist=d;best=p.i;}}
    return best;
  }
  canvas.addEventListener("pointerdown",e=>{
    if(!e.isPrimary||e.button!==0)return;
    press={id:e.pointerId,x:e.clientX,y:e.clientY,ox:yaw,oy:pitch,drag:false};canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove",e=>{
    if(!press){canvas.style.cursor=pick(e)!==null?"pointer":"grab";return;}
    if(press.id!==e.pointerId)return;
    const dx=e.clientX-press.x,dy=e.clientY-press.y;
    if(!press.drag && Math.hypot(dx,dy)<(e.pointerType==="touch"?9:4))return;
    press.drag=true;canvas.style.cursor="grabbing";yaw=press.ox+dx*.009;pitch=press.oy+dy*.008;schedule();
  });
  canvas.addEventListener("pointerup",e=>{
    if(press?.id!==e.pointerId)return;
    if(!press.drag){const id=pick(e);if(id!==null)onPick(id);}
    press=null;canvas.style.cursor="grab";
  });
  for(const type of ["pointercancel","lostpointercapture"])canvas.addEventListener(type,()=>{press=null;});
  const zoomBy=n=>{zoom=Math.max(.65,Math.min(4,zoom*n));schedule();};
  const reset=()=>{zoom=1;pitch=def.pitch;yaw=def.yaw;schedule();};
  stage.addEventListener("keydown",e=>{
    if(!["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","+","-"].includes(e.key))return;
    e.preventDefault();
    if(e.key==="Home")reset();else if(e.key==="+")zoomBy(1.25);else if(e.key==="-")zoomBy(.8);
    else{yaw+=({ArrowLeft:-.16,ArrowRight:.16}[e.key]||0);pitch+=({ArrowUp:-.16,ArrowDown:.16}[e.key]||0);schedule();}
  });
  field.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>{
    if(b.dataset.view==="reset")reset();else zoomBy(b.dataset.view==="in"?1.25:.8);
  }));
  const size=new ResizeObserver(schedule);size.observe(stage);
  const theme=new MutationObserver(syncTheme);
  theme.observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});syncTheme();
  canvas.addEventListener("webglcontextlost",()=>{dead=true;cancelAnimationFrame(frame);size.disconnect();theme.disconnect();field.hidden=true;},{once:true});
  return {layout,select};
}
