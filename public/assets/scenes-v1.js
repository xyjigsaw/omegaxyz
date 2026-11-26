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
// The category canvas starts hidden; its fallback region has a real layout box.
const sceneRegion=isOmega ? plate.parentElement.querySelector(".omega-hero") : plate?.parentElement;
if (plate && !navigator.connection?.saveData) {
  let started=false, inView=false;
  const mount = async () => {
    if(started || !inView || (isOmega && reduced.matches))return;
    started=true; reduced.removeEventListener("change",mount);
    try {
      const T = await import("./vendor/three-r160.min.js");
      drawPlate(T);
    } catch {
      fallback();
    }
  };
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(([entry]) => {
      inView=entry.isIntersecting;
      if(inView){ mount(); if(started)observer.disconnect(); }
    });
    observer.observe(sceneRegion);
  } else { inView=true; mount(); }
  if(isOmega && !started)reduced.addEventListener("change",mount);
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
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, isOmega ? 1.35 : 1.65));
  const canvas = renderer.domElement;
  canvas.className = "plate-canvas";
  canvas.setAttribute("aria-hidden", "true");
  plate.hidden = false;
  plate.prepend(canvas);
  const scene = new T.Scene();
  const camera = new T.OrthographicCamera(-2, 2, 2, -2, 0.1, 100);
  let frame = 0, visible = true, width = 0, height = 0, lastTick=null;
  const invalidate = () => {
    if (!frame && visible && !document.hidden && !renderer.getContext().isContextLost()) frame = requestAnimationFrame(render);
  };
  const study = isOmega ? omega(T, scene, camera, invalidate) : terrain(T, scene, camera, invalidate);
  function render(now=performance.now()) {
    frame = 0;
    if (!visible || document.hidden) return;
    // Bound GPU work for the continuously animated homepage, not the on-demand map.
    if(isOmega && lastTick!==null && now-lastTick<1000/30-1){invalidate();return;}
    const dt=lastTick===null?0:Math.min(.10,(now-lastTick)/1000);
    lastTick=now;
    const w = plate.clientWidth, h = plate.clientHeight;
    if (!w || !h) return;
    if (width !== w || height !== h) {
      width = w; height = h;
      renderer.setSize(w, h, false);
      study.resize(w, h);
    }
    const moving = study.update(document.documentElement.dataset.theme === "dark",dt);
    renderer.render(scene, camera);
    plate.dataset.ready = "true";
    if (moving) invalidate();
  }
  const size = new ResizeObserver(invalidate);
  size.observe(plate);
  const theme = new MutationObserver(invalidate);
  theme.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  function syncVisibility(){
    lastTick=null;
    if(!visible || document.hidden){cancelAnimationFrame(frame);frame=0;study.release?.();}
    else invalidate();
  }
  const visibility = new IntersectionObserver(([e]) => { visible=e.isIntersecting;syncVisibility(); });
  visibility.observe(sceneRegion);
  document.addEventListener("visibilitychange",syncVisibility);
  reduced.addEventListener("change",invalidate);
  canvas.addEventListener("webglcontextlost", () => {
    cancelAnimationFrame(frame); visible = false;
    size.disconnect(); theme.disconnect(); visibility.disconnect();
    document.removeEventListener("visibilitychange",syncVisibility);
    reduced.removeEventListener("change",invalidate);
    study.dispose?.();
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
  const glints=new T.InstancedMesh(ribs.geometry,new T.MeshBasicMaterial(),8);
  glints.frustumCulled=false;glints.renderOrder=3;glints.instanceMatrix.setUsage(T.DynamicDrawUsage);
  // The six axis pairs each generate four square faces, sharing the same 16 projected vertices.
  const panels=new T.BufferGeometry(), indices=[];
  for(const a of [1,2,4,8])for(const b of [1,2,4,8])if(a<b){
    for(let i=0;i<16;i++)if(!(i&(a|b)))indices.push(i,i|a,i|a|b, i,i|a|b,i|b);
  }
  const coords=new T.Float32BufferAttribute(new Float32Array(16*3),3).setUsage(T.DynamicDrawUsage);
  panels.setAttribute("position",coords);panels.setIndex(indices);
  const film=new T.ShaderMaterial({
    transparent:true,depthWrite:false,side:T.DoubleSide,forceSinglePass:true,extensions:{derivatives:true},
    uniforms:{phase:{value:0},night:{value:0}},
    vertexShader:`varying vec3 viewPos;
      void main(){vec4 v=modelViewMatrix*vec4(position,1.);viewPos=v.xyz;gl_Position=projectionMatrix*v;}`,
    fragmentShader:`varying vec3 viewPos; uniform float phase,night;
      void main(){
        vec3 normal=normalize(cross(dFdx(viewPos),dFdy(viewPos)));
        float rim=pow(1.-abs(normal.z),1.7);
        float sweep=.5+.5*cos(viewPos.x*1.8-viewPos.y*2.4+phase*.48);
        float tint=.5+.5*sin(phase*.22+normal.x*2.6+normal.y);
        vec3 aqua=mix(vec3(.15,.69,.71),vec3(.18,.88,.89),night);
        vec3 iris=mix(vec3(.44,.48,.88),vec3(.65,.53,.96),night);
        vec3 film=mix(aqua,iris,tint);
        film=mix(film,vec3(.91,.98,1.),pow(sweep,9.)*.44);
        gl_FragColor=vec4(film,.035+.105*rim+.065*pow(sweep,5.));
      }`
  });
  const skin=new T.Mesh(panels,film);
  skin.renderOrder=1;ribs.renderOrder=joints.renderOrder=2;
  skin.frustumCulled=ribs.frustumCulled=joints.frustumCulled=false;
  ribs.instanceMatrix.setUsage(T.DynamicDrawUsage);joints.instanceMatrix.setUsage(T.DynamicDrawUsage);
  group.add(skin,ribs,joints,glints);
  const frame=new T.Object3D(), axis=new T.Vector3(0,1,0), delta=new T.Vector3();
  const spectra=[[0x226a73,0x965478,0x507d91,0x405aa8,0xae6b31,0x438b86],
    [0x6ce8d8,0xf9bc8e,0x8eb5d1,0xa1baff,0xf6a5db,0x78d1c4]].map(row=>row.map(hex=>new T.Color(hex)));
  const inks=[new T.Color(),new T.Color(),new T.Color()], radii=[1,.88,.6];
  function update(ax,ay,dark,unit,time){
    const cx=Math.cos(ax),sx=Math.sin(ax),cy=Math.cos(ay),sy=Math.sin(ay);
    vertices.forEach(([x,y,z,w],i)=>{
      const x1=x*cx-w*sx,w1=x*sx+w*cx,y1=y*cy-w1*sy,w2=y*sy+w1*cy;
      const p=points[i].set(x1,y1,z).multiplyScalar(2.25/(3-w2));
      coords.setXYZ(i,p.x,p.y,p.z);
    });
    coords.needsUpdate=true;film.uniforms.phase.value=time;film.uniforms.night.value=dark?1:0;
    const palette=spectra[dark?1:0],blend=.5-.5*Math.cos(time*.24);
    inks.forEach((ink,i)=>ink.lerpColors(palette[i],palette[i+3],blend));
    const r=Math.max(.014,.85/unit);
    glints.material.color.setHex(dark?0xbafff4:0x219b9b);
    edges.forEach(([a,b,kind],i)=>{
      delta.subVectors(points[b],points[a]);
      const length=delta.length(), radius=r*radii[kind];
      frame.position.copy(points[a]).lerp(points[b],.5);
      frame.quaternion.setFromUnitVectors(axis,delta.divideScalar(length));
      frame.scale.set(radius,length,radius);frame.updateMatrix();ribs.setMatrixAt(i,frame.matrix);
      ribs.setColorAt(i,inks[kind]);
      if(kind===2){
        const at=.5-.41*Math.cos(time*.77+a*Math.PI/4);
        frame.position.copy(points[a]).lerp(points[b],at);
        frame.scale.set(r*1.12,length*.14,r*1.12);frame.updateMatrix();glints.setMatrixAt(a,frame.matrix);
      }
    });
    frame.quaternion.identity();
    points.forEach((p,i)=>{
      frame.position.copy(p);frame.scale.setScalar(i&8?r*1.7:r*1.45);
      frame.updateMatrix();joints.setMatrixAt(i,frame.matrix);
      joints.setColorAt(i,inks[i&8?0:1]);
    });
    ribs.instanceColor.needsUpdate=joints.instanceColor.needsUpdate=true;
    ribs.instanceMatrix.needsUpdate=joints.instanceMatrix.needsUpdate=glints.instanceMatrix.needsUpdate=true;
  }
  return {group,update};
}

function omega(T, scene, camera, invalidate) {
  const model=tesseract(T), mark=model.group;
  scene.add(mark);camera.position.z=12;
  const peaks=(plate.dataset.peaks||"").split(",").map(Number).filter(n=>n>0).map(count=>({count}));
  const landscape=new T.Mesh(makeRelief(T,peaks,Math.max(1,Math.ceil(Math.sqrt(peaks.length*2)))), reliefMaterial(T,true));
  landscape.renderOrder=-1;scene.add(landscape);
  const hero=sceneRegion, handle=hero.querySelector("[data-orbit]"), toggle=hero.querySelector("[data-motion]");
  const cleanup=new AbortController(), options={signal:cleanup.signal};
  let drag=null,yaw=0,pitch=0,turn=0,time=0,pixelUnit=80,paused=false;
  const pauseLabel=toggle.getAttribute("aria-label");
  function setPaused(value){
    paused=value;toggle.toggleAttribute("data-paused",value);
    const label=value?toggle.dataset.resume:pauseLabel;
    toggle.title=label;toggle.setAttribute("aria-label",label);invalidate();
  }
  toggle.title=pauseLabel;
  toggle.addEventListener("click",()=>setPaused(!paused),options);
  function orbit(dx,dy){
    yaw+=dx;pitch-=dy;invalidate();
  }
  function release(){
    if(!drag)return;
    const {id}=drag;drag=null;delete handle.dataset.dragging;
    if(handle.hasPointerCapture(id))handle.releasePointerCapture(id);
    invalidate();
  }
  handle.addEventListener("pointerdown",e=>{
    if(drag || !e.isPrimary || e.button!==0)return;
    drag={id:e.pointerId,x:e.clientX,y:e.clientY};
    handle.dataset.dragging="";handle.setPointerCapture(e.pointerId);
  },options);
  handle.addEventListener("pointermove",e=>{
    if(!drag || e.pointerId!==drag.id)return;
    orbit((e.clientX-drag.x)/pixelUnit*.78,(e.clientY-drag.y)/pixelUnit*.78);
    drag.x=e.clientX;drag.y=e.clientY;
  },options);
  for(const event of ["pointerup","pointercancel","lostpointercapture"])
    handle.addEventListener(event,e=>{if(e.pointerId===drag?.id)release();},options);
  window.addEventListener("blur",release,options);
  handle.addEventListener("keydown",e=>{
    const step={ArrowLeft:[-.15,0],ArrowRight:[.15,0],ArrowUp:[0,-.15],ArrowDown:[0,.15]}[e.key];
    if(step){e.preventDefault();orbit(...step);}
  },options);
  return {
    release,dispose(){cleanup.abort();release();},
    resize(w,h){
      const compact=w<=640,hh=hero.offsetHeight;
      pixelUnit=Math.min(compact?w/10.1:w*.064,hh*(compact?.112:.215),103);
      const half=h/(2*pixelUnit);
      camera.top=half;camera.bottom=-half;camera.right=half*w/h;camera.left=-camera.right;camera.updateProjectionMatrix();
      mark.position.set(compact?0:w*.19/pixelUnit,half-hh*(compact?.32:.45)/pixelUnit,0);
      handle.style.setProperty("--orbit-size",(4.08*pixelUnit)+"px");
      const scale=(camera.right-camera.left)*1.27/landscape.geometry.parameters.width;
      landscape.scale.set(scale,Math.min(1.1,scale)*.88,scale);
      landscape.position.set(0,half-hh*.76/pixelUnit,-32);landscape.rotation.set(.46,-.12,-.10);
    },
    update(dark,dt){
      const playing=!paused && !reduced.matches;
      if(playing){time+=dt;if(!drag)turn+=dt;}
      mark.rotation.set(.42+pitch+.08*Math.sin(turn*.24),-.59+yaw+turn*.085,.09);
      model.update(turn*.21,.38*Math.sin(turn*.25),dark,pixelUnit,time);
      landscape.material.uniforms.night.value=dark?1:0;
      landscape.material.uniforms.phase.value=time;
      return playing;
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
    defines:background?{HOME_WAVES:1}:{},
    uniforms:{ night:{value:0}, phase:{value:0} }, extensions:{derivatives:true},
    vertexShader:`varying float elevation; varying vec3 norm; varying vec2 field; uniform float phase;
      void main(){
        vec3 p=position;field=uv;norm=normal;
        #ifdef HOME_WAVES
          float wave=sin(.91*p.x+.64*p.z-phase*.73);
          float swell=cos(.68*p.z-.43*p.x+phase*.49);
          p.y*=1.+.24*wave+.16*swell;
          p.x+=.10*swell*smoothstep(.02,.8,p.y);
        #endif
        elevation=p.y;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);
      }`,
    fragmentShader:`varying float elevation; varying vec3 norm; varying vec2 field; uniform float night,phase;
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
        #ifdef HOME_WAVES
          float drift=.5+.5*sin(phase*.25+field.x*4.-field.y*1.7);
          vec3 low=mix(vec3(.11,.59,.54),vec3(.35,.50,.84),drift);
          vec3 high=mix(vec3(.88,.66,.42),vec3(.64,.53,.85),drift);
          tint=mix(low,high,smoothstep(.22,.96,h))+night*.07;
          weight=weight*.45+line*.055;
        #endif
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
