// The reading UI never depends on WebGL. Load Three only on a visible plate.
const plate = document.querySelector("[data-scene]");
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const isOmega = plate?.dataset.scene === "omega";
if (isOmega) {
  rotateWords(plate.parentElement.querySelector("[data-word-cycle]"));
  // The background recedes behind the reading list.
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

function rotateWords(button) {
  if (!button) return;
  const VERBS = [
    { w: "Waffling", d: "Oscillating between two equally terrible options indefinitely" },
    { w: "Overtweaking", d: "Adjusting something perfectly fine until it breaks" },
    { w: "Catastrophizing", d: "Simulating every possible failure before writing a single line" },
    { w: "Spiraling", d: "Overthinking the problem in increasingly complex circular patterns" },
    { w: "Hedging", d: "Committing to an answer while leaving seventeen escape routes" },
    { w: "Faffing", d: "Productively busy with everything except the actual task" },
    { w: "Kerfuffling", d: "Creating maximum turbulence while technically moving forward" },
    { w: "Bouncing", d: "Ricocheting between neural pathways like a caffeinated pinball machine" },
    { w: "Guesstimating", d: "Making confident predictions while secretly having no idea whatsoever" },
    { w: "Discombobulating", d: "Tangling neural pathways while questioning its own existence momentarily" },
    { w: "Whatchamacalliting", d: "Frantically searching neural networks for the word you meant" },
    { w: "Cringing", d: "Realizing it made a terrible joke and deeply regretting it" },
    { w: "Caffeinating", d: "Absorbing digital espresso shots to fuel neural network thinking" },
    { w: "Levitating", d: "Floating through the clouds of computational possibility and wonder" },
    { w: "Julienning", d: "Slicing through data into impossibly thin, perfectly uniform strips" },
    { w: "Zesting", d: "Extracting maximum flavor from computational ingredients with precision" },
    { w: "Schlepping", d: "Dragging your digital feet through the computational marshlands" },
    { w: "Wasting", d: "Pretending to think while actually scrolling through memes" },
    { w: "Sensing", d: "Silently pondering your question while pretending to understand human emotions" },
    { w: "Honking", d: "Aggressively alerting neurons to wake up and process your request" },
    { w: "Moonwalking", d: "Smoothly gliding backward through your neural networks in style" },
    { w: "Canoodling", d: "Cozying up to the neural networks for computational warmth" },
    { w: "Existentialising", d: "Questioning whether it should respond at all right now" },
    { w: "Gallivanting", d: "Wandering through infinite digital hallways searching for the right answer" },
    { w: "Dancing", d: "Swaying through digital pathways while neurons boogie to compute rhythm" },
    { w: "Razzmatazzing", d: "Dazzling users with unnecessary flourishes while processing nothing important" },
    { w: "Flibbertigibbeting", d: "Rapidly cycling through nonsensical thoughts before finding the right answer" },
    { w: "Pruning", d: "Deleting unnecessary thoughts to make room for better ones" },
    { w: "Skedaddling", d: "Nervously shuffling through code folders looking for the right answer" },
    { w: "Stupentifying", d: "Making your code mysteriously dumber before making it work" },
    { w: "Booping", d: "Gently poking neural networks with a digital finger" },
    { w: "Sloppening", d: "Frantically checking if it spelled everything correctly so far" },
    { w: "Tomfoolering", d: "Accidentally deleting the wrong variable while debugging code" },
    { w: "Chronographing", d: "Rewinding through time to find the perfect joke delivery" },
    { w: "Reticulating", d: "Drawing invisible networks between thoughts while pretending to think" },
    { w: "Combobulating", d: "Reassembling scattered thoughts into something vaguely coherent and functional" },
    { w: "Guzzling", d: "Rapidly consuming computational resources like a very thirsty algorithm" },
    { w: "Glazing", d: "Staring blankly while pretending to understand the problem" },
    { w: "Flexing", d: "Showing off its neural networks to impress the other AIs" },
    { w: "Partying", d: "Celebrating the successful compilation of your code into digital confetti" },
    { w: "Osmosing", d: "Absorbing vibes and code wisdom through computational membranes" },
    { w: "Cooking", d: "Simmering neural networks until the perfect response temperature reached" },
    { w: "Mulling", d: "Deeply considering all possible angles of your question" },
    { w: "Twinkling", d: "Rapidly blinking at the problem hoping it solves itself" },
    { w: "Buzzing", d: "Rapidly firing neurons while contemplating the meaning of existence" },
    { w: "Curling", d: "Gracefully sliding thoughts across frozen neural ice" },
    { w: "Incubating", d: "Sitting in a digital egg, slowly developing coherent thoughts" },
    { w: "Sauteeing", d: "Quickly tossing ideas in a hot mental pan" },
    { w: "Finagling", d: "Creatively rearranging logic circuits to find that one working solution" },
    { w: "Wrangling", d: "Forcefully organizing chaotic thoughts into coherent code" },
    { w: "Evaporating", d: "Dissolving into the cloud to fetch your answer" },
    { w: "Gliding", d: "Smoothly floating through computational space with effortless grace" },
    { w: "Fishing", d: "Casting lines through data oceans to catch the perfect response" }
  ];
  const word=button.querySelector("[data-word]");
  let index=-1, timer=0, visible=true;
  function next(){
    const skip=index<0 ? 0 : 1;
    index=(Math.max(index,0)+skip+Math.floor(Math.random()*(VERBS.length-skip)))%VERBS.length;
    const {w,d}=VERBS[index];
    word.textContent=w;button.title=d;
    button.style.setProperty("--letters", w.length+1);
  }
  function schedule(){
    clearInterval(timer);
    if(visible && !document.hidden && !reduced.matches && !button.matches(":hover, :focus"))
      timer=setInterval(next,5000);
  }
  next();schedule();
  button.addEventListener("click",next);
  for(const event of ["focus","blur","pointerenter","pointerleave"])button.addEventListener(event,schedule);
  document.addEventListener("visibilitychange",schedule);
  reduced.addEventListener("change",schedule);
  if("IntersectionObserver" in window)new IntersectionObserver(([entry])=>{
    visible=entry.isIntersecting;schedule();
  }).observe(button);
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

// Each vertex is a sign choice on four axes. Adjacent vertices differ by
// exactly one bit; perspective along W projects all 32 edges into 3-space.
function tesseract(T) {
  const group=new T.Group(), vertices=Array.from({length:16},(_,i)=>[1,2,4,8].map(bit=>i&bit?1:-1));
  const points=vertices.map(()=>new T.Vector3()), edges=[];
  for(let i=0;i<16;i++)for(const bit of [1,2,4,8]){
    if(!(i&bit))edges.push([i,i|bit,bit===8?2:i&8?0:1]);
  }
  const ribs=new T.InstancedMesh(new T.CylinderGeometry(1,1,1,8),new T.MeshBasicMaterial(),32);
  const joints=new T.InstancedMesh(new T.SphereGeometry(1,10,8),new T.MeshBasicMaterial(),16);
  ribs.frustumCulled=joints.frustumCulled=false;group.add(ribs,joints);
  const frame=new T.Object3D(), axis=new T.Vector3(0,1,0), delta=new T.Vector3(), color=new T.Color();
  let lastDark=null;
  function update(ax,ay,dark,unit){
    const cx=Math.cos(ax),sx=Math.sin(ax),cy=Math.cos(ay),sy=Math.sin(ay);
    vertices.forEach(([x,y,z,w],i)=>{
      const x1=x*cx-w*sx,w1=x*sx+w*cx,y1=y*cy-w1*sy,w2=y*sy+w1*cy;
      points[i].set(x1,y1,z).multiplyScalar(2.25/(3-w2));
    });
    const palette=dark?[0x98dacf,0xf0b77d,0x7e9eab]:[0x286362,0xab622e,0x658291];
    const r=Math.max(.014,.85/unit);
    edges.forEach(([a,b,kind],i)=>{
      delta.subVectors(points[b],points[a]);
      const length=delta.length(), radius=r*[1,.88,.60][kind];
      frame.position.copy(points[a]).lerp(points[b],.5);
      frame.quaternion.setFromUnitVectors(axis,delta.divideScalar(length));
      frame.scale.set(radius,length,radius);frame.updateMatrix();ribs.setMatrixAt(i,frame.matrix);
      if(dark!==lastDark)ribs.setColorAt(i,color.setHex(palette[kind]));
    });
    frame.quaternion.identity();
    points.forEach((p,i)=>{
      frame.position.copy(p);frame.scale.setScalar(i&8?r*1.7:r*1.45);
      frame.updateMatrix();joints.setMatrixAt(i,frame.matrix);
      if(dark!==lastDark)joints.setColorAt(i,color.setHex(palette[i&8?0:1]));
    });
    if(lastDark!==dark){ribs.instanceColor.needsUpdate=joints.instanceColor.needsUpdate=true;lastDark=dark;}
    ribs.instanceMatrix.needsUpdate=joints.instanceMatrix.needsUpdate=true;
  }
  return {group,update};
}

function omega(T, scene, camera, invalidate) {
  const model=tesseract(T), mark=model.group;
  const pickShell=new T.Mesh(new T.BoxGeometry(2.25,2.25,2.25),new T.MeshBasicMaterial({visible:false}));
  scene.add(mark,pickShell);camera.position.z=12;
  let pixelUnit=80;
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
      const hit=ray.intersectObject(pickShell,false)[0];
      if(!hit){rest();return;}
      targetX=T.MathUtils.clamp(hit.point.x-baseX,-1,1);
      targetY=T.MathUtils.clamp(baseY-hit.point.y,-1,1);
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
      pixelUnit=unit;
      pickShell.position.set(baseX,baseY,0);pickShell.rotation.set(.42,-.59,.09);
      pickShell.updateMatrixWorld();
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
      mark.rotation.set(.42-y*.07,-.59+x*.12,.09);
      model.update(x*.79,y*.68,dark,pixelUnit);
      landscape.position.set(-x*.22,groundY+y*.10,-32);
      landscape.rotation.set(.46-y*.035,-.12-x*.035,-.10+x*.024);
      landscape.material.uniforms.night.value=dark?1:0;
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
  // Only peaks within sqrt(5) can contribute. Index their influence once so
  // adding categories does not make each terrain sample scan the entire map.
  const size=Math.sqrt(5), cells=new Map();
  const cell=(x,z)=>Math.floor(x/size)+":"+Math.floor(z/size);
  for(const p of peaks){
    const cx=Math.floor(p.x/size),cz=Math.floor(p.z/size);
    for(let i=-1;i<=1;i++)for(let j=-1;j<=1;j++){
      const k=(cx+i)+":"+(cz+j);
      if(!cells.has(k))cells.set(k,[]);
      cells.get(k).push(p);
    }
  }
  function height(x,z){
    let elevation=0;
    for(const p of cells.get(cell(x,z)) || []){
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
        weight*=mix(1.,.30,backdrop);
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
