const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
const ease=value=>value*value*(3-2*value);
const segment=(progress,start,end)=>clamp((progress-start)/(end-start),0,1);

const stage=document.querySelector('#heroStage');
const image=document.querySelector('#heroImage');
const light=document.querySelector('#lightScrim');
const dark=document.querySelector('#darkScrim');
const copy=document.querySelector('#heroCopy');
const panel=document.querySelector('#workshopPanel');
const hint=document.querySelector('#scrollHint');

let frame=0;
function updateHero(){
  frame=0;
  if(!stage||window.matchMedia('(max-width: 760px)').matches)return;
  const rect=stage.getBoundingClientRect();
  const span=rect.height-window.innerHeight;
  const progress=span>0?clamp(-rect.top/span,0,1):0;
  const exit=ease(segment(progress,0,.55));
  const enter=ease(segment(progress,.35,.85));
  image.style.transform=`scale(${1+.16*ease(progress)}) translateY(${-40*ease(progress)}px)`;
  light.style.opacity=String(1-exit);
  dark.style.opacity=String(.92*exit);
  copy.style.transform=`translateY(${-70*exit}px)`;
  copy.style.opacity=String(1-exit);
  hint.style.opacity=String(1-ease(segment(progress,0,.15)));
  panel.style.transform=`translateY(${54*(1-enter)}px)`;
  panel.style.opacity=String(enter);
}
function requestUpdate(){if(!frame)frame=requestAnimationFrame(updateHero)}
addEventListener('scroll',requestUpdate,{passive:true});
addEventListener('resize',requestUpdate,{passive:true});
updateHero();

const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('#navigation');
toggle?.addEventListener('click',()=>{
  const open=toggle.getAttribute('aria-expanded')==='true';
  toggle.setAttribute('aria-expanded',String(!open));
  nav.classList.toggle('open',!open);
});
nav?.addEventListener('click',()=>{nav.classList.remove('open');toggle?.setAttribute('aria-expanded','false')});
