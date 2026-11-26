// The reading UI never depends on WebGL. Load Three only on a visible plate.
const plate = document.querySelector("[data-scene]");
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const isOmega = plate?.dataset.scene === "omega";
if (isOmega) {
  // The plate recedes behind the reading list, including in static-poster mode.
  const fade = () => {
    const amount=Math.min(1, Math.max(0, scrollY / Math.max(280,innerHeight*.50)));
    plate.style.opacity=String(1-.94*amount);
  };
  window.addEventListener("scroll",fade,{passive:true}); fade();
}
if (plate && !navigator.connection?.saveData && !(isOmega && reduced.matches)) {
  const mount = async () => {
    try {
      const T = await import("./vendor/three-r160.min.js");
      drawPlate(T);
    } catch {
      fallback();
    }
  };
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { observer.disconnect(); mount(); }
    });
    observer.observe(plate.parentElement);
  } else { mount(); }
}

function fallback() {
  delete plate.dataset.ready;
  plate.querySelector("canvas")?.remove();
  if (!isOmega) plate.hidden = true;
}

function drawPlate(T) {
  const renderer = new T.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
  renderer.setClearColor(0, 0);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.65));
  const canvas = renderer.domElement;
  canvas.className = "plate-canvas";
  canvas.setAttribute("aria-hidden", "true");
  plate.hidden = false;
  plate.prepend(canvas);
  const scene = new T.Scene();
  const camera = new T.OrthographicCamera(-2, 2, 2, -2, 0.1, 100);
  let frame = 0, visible = true, width = 0, height = 0;
  const invalidate = () => {
    if (!frame && visible && !document.hidden && !renderer.getContext().isContextLost()) frame = requestAnimationFrame(render);
  };
  const study = isOmega ? omega(T, scene, camera, invalidate) : terrain(T, scene, camera, invalidate);
  function render() {
    frame = 0;
    if (!visible || document.hidden) return;
    const w = plate.clientWidth, h = plate.clientHeight;
    if (!w || !h) return;
    if (width !== w || height !== h) {
      width = w; height = h;
      renderer.setSize(w, h, false);
      study.resize(w, h);
    }
    const moving = study.update(document.documentElement.dataset.theme === "dark");
    renderer.render(scene, camera);
    plate.dataset.ready = "true";
    if (moving) invalidate();
  }
  const size = new ResizeObserver(invalidate);
  size.observe(plate);
  const theme = new MutationObserver(invalidate);
  theme.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  const visibility = new IntersectionObserver(([e]) => { visible = e.isIntersecting; invalidate(); });
  visibility.observe(plate);
  document.addEventListener("visibilitychange", invalidate);
  canvas.addEventListener("webglcontextlost", () => {
    cancelAnimationFrame(frame); visible = false;
    size.disconnect(); theme.disconnect(); visibility.disconnect();
    document.removeEventListener("visibilitychange", invalidate);
    fallback();
  }, { once: true });
  render();
}

function omega(T, scene, camera, invalidate) {
  // A single four-letter drawing, with matched cap heights, strokes and cuts.
  const arch = new T.Shape();
  arch.moveTo(-1.12,-.88); arch.lineTo(-.39,-.88); arch.lineTo(-.39,-.65);
  arch.bezierCurveTo(-.65,-.41,-.76,-.13,-.76,.15);
  arch.bezierCurveTo(-.76,.58,-.47,.87,0,.87);
  arch.bezierCurveTo(.47,.87,.76,.58,.76,.15);
  arch.bezierCurveTo(.76,-.13,.65,-.41,.39,-.65);
  arch.lineTo(.39,-.88); arch.lineTo(1.12,-.88); arch.lineTo(1.12,-.61);
  arch.lineTo(.78,-.61); arch.bezierCurveTo(1.02,-.38,1.1,-.12,1.1,.16);
  arch.bezierCurveTo(1.1,.78,.66,1.16,0,1.16);
  arch.bezierCurveTo(-.66,1.16,-1.1,.78,-1.1,.16);
  arch.bezierCurveTo(-1.1,-.12,-1.02,-.38,-.78,-.61);
  arch.lineTo(-1.12,-.61); arch.closePath();
  const polygon = points => new T.Shape(points.map(([x,y]) => new T.Vector2(x,y)));
  const letters = [
    [arch,-2.80],
    [polygon([[-.84,1.12],[-.43,1.12],[0,.40],[.46,1.12],[.86,1.12],[.20,.16],[.91,-.88],[.48,-.88],[0,-.12],[-.49,-.88],[-.90,-.88],[-.21,.15]]),-.68],
    [polygon([[-.92,1.12],[-.53,1.12],[0,.26],[.53,1.12],[.92,1.12],[.18,-.04],[.18,-.88],[-.18,-.88],[-.18,-.04]]),1.30],
    [polygon([[-.79,1.12],[.82,1.12],[.82,.86],[-.39,-.56],[.85,-.56],[.85,-.88],[-.85,-.88],[-.85,-.62],[.35,.80],[-.79,.80]]),3.21]
  ];
  const film = new T.ShaderMaterial({
    uniforms:{ night:{value:0} },
    vertexShader:`varying vec3 n; varying vec3 place;
      void main(){ vec4 p=modelMatrix*vec4(position,1.);place=p.xyz;n=normalize(normalMatrix*normal);
        gl_Position=projectionMatrix*viewMatrix*p; }`,
    fragmentShader:`uniform float night; varying vec3 n,place;
      void main(){
        vec3 N=normalize(n); float face=smoothstep(.63,.94,N.z);
        float a=place.x*.74+place.y*.54;
        float silk=.55+.45*cos(a*1.3-.4);
        float glint=exp(-4.*abs(a-.85))+.45*exp(-5.*abs(a+2.9));
        vec3 ink=mix(vec3(.058,.16,.18),vec3(.37,.59,.60),night);
        vec3 sheen=mix(vec3(.39,.58,.57),vec3(.89,.97,.94),night);
        vec3 top=mix(ink,sheen,.12+.53*silk+.28*glint);
        vec3 rim=mix(vec3(.048,.27,.29),vec3(.57,.83,.78),smoothstep(-.6,.85,N.y-N.x*.46));
        vec3 paper=mix(vec3(.98,.985,.985),vec3(.055,.075,.083),night);
        gl_FragColor=vec4(mix(mix(rim,top,face),paper,mix(.29,.24,night)),1.);
      }`
  });
  const mark = new T.Group();
  const edge = new T.MeshBasicMaterial({color:0x469d95});
  for (const [i,[shape,origin]] of letters.entries()) {
    const offset=origin+(i-1.5)*.17;
    const g=new T.ExtrudeGeometry(shape,{depth:.22,bevelEnabled:true,bevelSize:.033,bevelThickness:.035,bevelSegments:3,curveSegments:24});
    // A slight forward rake ties the four glyphs together like one engraved signature.
    g.applyMatrix4(new T.Matrix4().makeShear(0,0,.105,0,0,0));
    const glyph=new T.Mesh(g,film);glyph.position.x=offset;mark.add(glyph);
    const inlay=new T.Mesh(g,edge);inlay.position.set(offset,0,-.11);inlay.scale.z=.45;mark.add(inlay);
  }
  scene.add(mark);camera.position.z=12;
  const peaks=(plate.dataset.peaks||"").split(",").map(Number).filter(n=>n>0).map(count=>({count}));
  const landscape=new T.Mesh(makeRelief(T,peaks,Math.max(1,Math.ceil(Math.sqrt(peaks.length*2)))), reliefMaterial(T,true));
  landscape.renderOrder=-1;scene.add(landscape);
  let targetX=0,targetY=0,x=0,y=0, baseX=0,baseY=0,groundY=0;
  const ray=new T.Raycaster(), mouse=new T.Vector2();
  let pickFrame=0;
  const rest=()=>{
    cancelAnimationFrame(pickFrame);pickFrame=0;
    if(targetX||targetY){targetX=targetY=0;invalidate();}
  };
  const hero=plate.parentElement.querySelector(".omega-hero");
  // Pick through the decorative canvas, never through a foreground control.
  window.addEventListener("pointermove",e=>{
    if(e.pointerType==="touch" || reduced.matches || e.target!==hero || scrollY>innerHeight){rest();return;}
    const rect=plate.getBoundingClientRect();
    mouse.set((e.clientX-rect.left)/rect.width*2-1,1-(e.clientY-rect.top)/rect.height*2);
    if(!pickFrame)pickFrame=requestAnimationFrame(()=>{
      pickFrame=0;ray.setFromCamera(mouse,camera);
      const hit=ray.intersectObjects(mark.children,false)[0];
      if(!hit){rest();return;}
      const local=mark.worldToLocal(hit.point);
      targetX=T.MathUtils.clamp(local.x/4,-1,1);targetY=T.MathUtils.clamp(-local.y,-1,1);
      invalidate();
    });
  },{passive:true});
  document.documentElement.addEventListener("pointerleave",rest);
  window.addEventListener("scroll",rest,{passive:true});
  window.addEventListener("blur",rest);
  return {
    resize(w,h){
      const compact=w<=640, unit=compact?w/10.1:Math.min(w*.064,103), half=h/(2*unit);
      camera.top=half;camera.bottom=-half;camera.right=half*w/h;camera.left=-camera.right;camera.updateProjectionMatrix();
      const nav=document.querySelector(".site-header");
      const navHeight=nav?.offsetHeight || 0;
      baseX=compact?0:(w*.19)/unit;
      baseY=half-(navHeight+hero.offsetHeight*(compact ? .32 : .45))/unit;
      groundY=half-(navHeight+hero.offsetHeight*.76)/unit;
      const span=landscape.geometry.parameters.width;
      const scale=(camera.right-camera.left)*1.27/span;
      landscape.scale.set(scale,Math.min(1.1,scale)*.88,scale);
      landscape.position.set(0,groundY,-32);
    },
    update(dark){
      x+=(targetX-x)*.11;y+=(targetY-y)*.11;
      if(Math.abs(targetX-x)+Math.abs(targetY-y)<=.002){x=targetX;y=targetY;}
      mark.position.set(baseX+x*.17,baseY-y*.085,0);
      mark.rotation.set(.13-y*.14,-.14+x*.23,-.014+x*.012);
      landscape.position.set(-x*.22,groundY+y*.10,-32);
      landscape.rotation.set(.46-y*.035,-.12-x*.035,-.10+x*.024);
      film.uniforms.night.value=landscape.material.uniforms.night.value=dark?1:0;
      return Math.abs(targetX-x)+Math.abs(targetY-y)>.002;
    }
  };
}

function makeRelief(T, peaks, cols) {
  const rows=Math.max(1,Math.ceil(peaks.length/cols));
  const mapWidth=cols*1.35+1.5, mapDepth=rows*1.35+1.5;
  const slots=Array.from({length:cols*rows},(_,i)=>{
    const col=i%cols,row=Math.floor(i/cols);
    const x=(col-(cols-1)/2)*1.35+0.13*Math.sin(i*2.41);
    const z=(row-(rows-1)/2)*1.35+0.13*Math.cos(i*1.73);
    return {x,z,rank:Math.hypot(x/mapWidth,z/mapDepth)+.25*Math.sin(i*7.23)};
  }).sort((a,b)=>a.rank-b.rank);
  peaks.forEach((p,i)=>Object.assign(p,slots[i],{
    h:.14+1.64*Math.log1p(p.count)/Math.log1p(peaks[0].count),
    cos:Math.cos(i*2.4),sin:Math.sin(i*2.4),phase:i*.93
  }));
  function height(x,z){
    let elevation=0;
    for(const p of peaks){
      const dx=x-p.x,dz=z-p.z, r=dx*dx+dz*dz;
      if(r>5)continue;
      const along=dx*p.cos+dz*p.sin, across=dz*p.cos-dx*p.sin+.18*Math.sin(along*3.1);
      const ridge=1.65*along*along+4.8*across*across;
      const spur=1+.25*Math.sin(4*x+2*z+p.phase)+.14*Math.sin(6*z-3*x);
      elevation+=p.h*Math.exp(-ridge*spur);
    }
    return elevation;
  }
  const g=new T.PlaneGeometry(mapWidth,mapDepth,cols*18,rows*18);
  g.rotateX(-Math.PI/2);
  const pos=g.attributes.position;
  for(let i=0;i<pos.count;i++)pos.setY(i,height(pos.getX(i),pos.getZ(i)));
  g.computeVertexNormals();
  peaks.forEach(p=>p.y=height(p.x,p.z));
  return g;
}

function reliefMaterial(T, background) {
  return new T.ShaderMaterial({
    transparent:true, depthWrite:!background,
    uniforms:{ night:{value:0}, backdrop:{value:background?1:0} }, extensions:{derivatives:true},
    vertexShader:`varying float elevation; varying vec3 norm; varying vec2 field;
      void main(){field=uv;elevation=position.y;norm=normal;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`varying float elevation; varying vec3 norm; varying vec2 field; uniform float night,backdrop;
      void main(){
        float h=clamp(elevation/1.8,0.,1.);
        vec2 ends=min(field,1.-field); float edge=smoothstep(0.,.13,min(ends.x,ends.y));
        float shade=max(0.,dot(normalize(norm),normalize(vec3(-.6,1.,.5))));
        vec3 paper=mix(vec3(.976,.985,.983),vec3(.055,.075,.083),night);
        vec3 teal=mix(vec3(.20,.49,.47),vec3(.44,.72,.67),night);
        vec3 tint=mix(teal,vec3(.81,.66,.47),smoothstep(.36,.94,h));
        float k=elevation*14.,d=abs(fract(k+.5)-.5);
        float line=(1.-smoothstep(0.,max(.025,fwidth(k)*.95),d))*smoothstep(.012,.08,elevation);
        float weight=(.13+.65*h)*(.77+.23*shade)+line*.28;
        weight*=mix(1.,.48,backdrop);
        float opacity=edge*smoothstep(.004,.11,elevation);
        if(opacity<.008)discard;
        gl_FragColor=vec4(mix(paper,tint,clamp(weight,0.,1.)),opacity);
      }`
  });
}

function terrain(T, scene, camera, invalidate) {
  const links = Array.from(document.querySelectorAll(".category-cloud [data-peak]"));
  const peaks = links.map(link => ({ link, name:link.querySelector("span").textContent,
    count:Number(link.dataset.count), x:0,z:0,y:0 })).sort((a,b)=>b.count-a.count || a.link.dataset.peak.localeCompare(b.link.dataset.peak));
  if (!peaks.length) throw new Error("Empty terrain");
  const label=plate.querySelector("[data-peak-label]");
  let mesh, selected=peaks[0], columns=0;
  let tx=0,ty=0,rx=0,ry=0;
  const ray=new T.Raycaster(), mouse=new T.Vector2();
  const material=reliefMaterial(T,false);
  function build(cols) {
    if(mesh){scene.remove(mesh);mesh.geometry.dispose();}
    columns=cols;
    mesh=new T.Mesh(makeRelief(T,peaks,cols),material);
    scene.add(mesh);
  }
  function choose(p) {
    selected.link.classList.remove("is-peak");
    selected=p; p.link.classList.add("is-peak");
    label.textContent=p.name+" · "+p.count+" ↗";label.href=p.link.href;label.hidden=false;
    invalidate();
  }
  for(const p of peaks){
    p.link.addEventListener("focus",()=>choose(p));
    p.link.addEventListener("pointerenter",()=>choose(p));
  }
  function picked(event){
    const b=plate.getBoundingClientRect();
    mouse.set((event.clientX-b.left)/b.width*2-1,1-(event.clientY-b.top)/b.height*2);
    ray.setFromCamera(mouse,camera);
    const hit=ray.intersectObject(mesh)[0];
    if(!hit)return null;
    mesh.worldToLocal(hit.point);
    if(hit.point.y<.025 || Math.min(hit.uv.x,hit.uv.y,1-hit.uv.x,1-hit.uv.y)<.015)return null;
    return peaks.reduce((a,p)=>Math.hypot(p.x-hit.point.x,p.z-hit.point.z)<Math.hypot(a.x-hit.point.x,a.z-hit.point.z)?p:a);
  }
  const canvas=plate.querySelector("canvas");
  let pointer=null, pickFrame=0;
  canvas.addEventListener("pointermove",e=>{
    if(e.pointerType==="touch")return;
    pointer=e;
    if(!pickFrame)pickFrame=requestAnimationFrame(()=>{
      pickFrame=0;
      const hovered=picked(pointer); canvas.style.cursor=hovered?"pointer":"";
      tx=hovered&&!reduced.matches?mouse.x:0;ty=hovered&&!reduced.matches?-mouse.y:0;
      invalidate();
      if(hovered && hovered!==selected)choose(hovered);
    });
  });
  canvas.addEventListener("pointerleave",()=>{
    cancelAnimationFrame(pickFrame);pickFrame=0;tx=ty=0;invalidate();
  });
  plate.addEventListener("click",e=>{
    if(e.target!==canvas)return;
    const p=picked(e); if(!p)return;
    if(matchMedia("(hover: hover)").matches)location.assign(p.link.href);
    else choose(p);
  });
  choose(selected);
  return {
    resize(w,h) {
      const cols=Math.min(peaks.length,Math.max(1,Math.ceil(Math.sqrt(peaks.length*(w <= 580 ? .72 : 1.85)))));
      if(cols!==columns)build(cols);
      camera.position.set(w<=580?2.3:3.6,w<=580?11:7.8,11);
      camera.lookAt(0,0,0);camera.updateMatrixWorld();
      const bounds=new T.Box3(),v=new T.Vector3(),a=mesh.geometry.attributes.position;
      for(let i=0;i<a.count;i++)bounds.expandByPoint(v.fromBufferAttribute(a,i).applyMatrix4(camera.matrixWorldInverse));
      const mid=bounds.getCenter(v), half=Math.max((bounds.max.y-bounds.min.y)*.54,(bounds.max.x-bounds.min.x)*h/w*.52);
      camera.left=mid.x-half*w/h;camera.right=mid.x+half*w/h;
      camera.top=mid.y+half;camera.bottom=mid.y-half;camera.updateProjectionMatrix();
    },
    update(dark) {
      material.uniforms.night.value=dark?1:0;
      rx+=(tx-rx)*.15;ry+=(ty-ry)*.15;
      if(Math.abs(tx-rx)+Math.abs(ty-ry)<=.002){rx=tx;ry=ty;}
      mesh.rotation.set(ry*.018,rx*.035,0);mesh.updateMatrixWorld();
      const v=mesh.localToWorld(new T.Vector3(selected.x,selected.y,selected.z)).project(camera);
      const x=Math.min(plate.clientWidth-label.offsetWidth,Math.max(0,(v.x+1)*.5*plate.clientWidth+3));
      const y=Math.max(0,(1-v.y)*.5*plate.clientHeight-label.offsetHeight-2);
      label.style.transform="translate("+Math.round(x)+"px,"+Math.round(y)+"px)";
      return Math.abs(tx-rx)+Math.abs(ty-ry)>.002;
    }
  };
}
