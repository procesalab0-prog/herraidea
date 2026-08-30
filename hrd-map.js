(() => {
  const RED = '#fa1418', GRAY = '#c6c9cd';
  const outline = [[-117,32.5],[-114.7,32.7],[-111,31.3],[-108.2,31.3],[-105,30.6],[-103.3,29],[-101.4,29.7],[-99.1,26.4],[-97.2,26],[-97.8,22.9],[-96.4,19.9],[-94.5,18.2],[-92,18.6],[-90.4,21],[-87.4,21.6],[-86.8,20.4],[-88.3,18.5],[-89.2,17.3],[-91.4,16.1],[-92.2,14.6],[-94.8,16.2],[-97.8,15.9],[-100.8,17.2],[-104.3,19.1],[-105.7,20.5],[-105.9,22.3],[-108.9,25.6],[-109.9,27.3],[-112.2,29.5],[-114.5,31.8],[-114.7,31],[-113.5,29.3],[-112.3,27],[-110.7,25],[-109.4,23.1],[-111.6,24.4],[-113.5,26.8],[-114,28.4],[-115.7,30],[-116.7,31.7]];
  const cities = [['Tijuana',-117,32.5],['Hermosillo',-111,29.1],['Chihuahua',-106.1,28.6],['Monterrey',-100.3,25.7],['Durango',-104.7,24],['Mazatlán',-106.4,23.3],['San Luis Potosí',-101,22.2],['Guadalajara',-103.4,20.7],['Querétaro',-100.4,20.6],['CDMX',-99.1,19.4],['Puebla',-98.2,19],['Veracruz',-96.1,19.2],['Acapulco',-99.9,16.9],['Oaxaca',-96.7,17.1],['Villahermosa',-92.9,18],['Mérida',-89.6,21],['Cancún',-86.9,21.2],['Tuxtla Gutiérrez',-93.1,16.8]];
  const origin = [-101.68,21.12], cycle = 8200;
  class HrdMap extends HTMLElement {
    connectedCallback() {
      if (this.canvas) return;
      this.canvas = document.createElement('canvas'); this.append(this.canvas); this.ctx = this.canvas.getContext('2d');
      this.canvas.style.cssText = 'display:block;width:100%;height:auto'; this.start = performance.now(); this.fired = new Set();
      this.resize = () => this.layout(); addEventListener('resize', this.resize, {passive:true}); this.layout();
      this.loop = now => { this.frame = requestAnimationFrame(this.loop); this.draw(now); }; this.frame = requestAnimationFrame(this.loop);
    }
    disconnectedCallback(){ removeEventListener('resize',this.resize); cancelAnimationFrame(this.frame); }
    point(lon,lat){ return [this.ox+(lon+117.5)*this.sx,this.oy+(33-lat)*this.sy]; }
    layout(){
      this.w=this.clientWidth||900; this.h=Math.max(270,Math.min(580,this.w*.48)); const d=Math.min(devicePixelRatio||1,2);
      this.canvas.width=this.w*d; this.canvas.height=this.h*d; this.canvas.style.height=`${this.h}px`; this.ctx.setTransform(d,0,0,d,0,0);
      this.ox=this.w*.055; this.oy=this.h*.07; this.sx=(this.w*.89)/31.2; this.sy=(this.h*.86)/18.8;
      const poly=outline.map(p=>this.point(...p)); this.dots=[]; const step=this.w<620?7:9;
      const inside=(x,y)=>{let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++)if((poly[i][1]>y)!=(poly[j][1]>y)&&x<(poly[j][0]-poly[i][0])*(y-poly[i][1])/(poly[j][1]-poly[i][1])+poly[i][0])hit=!hit;return hit};
      for(let y=this.oy;y<this.h-this.oy;y+=step)for(let x=this.ox;x<this.w-this.ox;x+=step)if(inside(x,y))this.dots.push([x,y]);
      this.o=this.point(...origin); this.targets=cities.map(c=>{const p=this.point(c[1],c[2]);return{name:c[0],x:p[0],y:p[1],d:Math.hypot(p[0]-this.o[0],p[1]-this.o[1])}}); this.max=Math.max(...this.targets.map(t=>t.d));
    }
    draw(now){
      const c=this.ctx;if(!c)return;let t=((now-this.start)%cycle)/cycle;if(t<.02)this.fired.clear();const reach=Math.min(t/.63,1)*this.max*1.08,fade=t>.84?1-(t-.84)/.16:1;
      c.clearRect(0,0,this.w,this.h); for(const p of this.dots){const d=Math.hypot(p[0]-this.o[0],p[1]-this.o[1]),on=Math.max(0,Math.min(1,(reach-d)/38))*fade;c.fillStyle=on?`rgba(250,20,24,${.3+on*.65})`:GRAY;c.beginPath();c.arc(p[0],p[1],1.5+on*.7,0,Math.PI*2);c.fill()}
      for(const target of this.targets){const on=reach>=target.d;if(on&&!this.fired.has(target.name)){this.fired.add(target.name);this.dispatchEvent(new CustomEvent('hrd-city',{detail:target.name,bubbles:true}))}c.fillStyle=on?RED:'#9ea2a7';c.beginPath();c.arc(target.x,target.y,on?3:2.2,0,Math.PI*2);c.fill()}
      const pulse=(now/1700)%1;c.strokeStyle=`rgba(250,20,24,${(1-pulse)*.35})`;c.beginPath();c.arc(this.o[0],this.o[1],7+pulse*28,0,Math.PI*2);c.stroke();c.fillStyle=RED;c.beginPath();c.arc(this.o[0],this.o[1],5,0,Math.PI*2);c.fill();c.fillStyle='#0b0d10';c.font="700 11px 'Archivo Narrow',sans-serif";c.fillText('LEÓN, GTO.',this.o[0]+12,this.o[1]+4);
    }
  }
  if(!customElements.get('hrd-map'))customElements.define('hrd-map',HrdMap);
})();
