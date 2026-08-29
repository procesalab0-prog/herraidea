(function () {
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const smooth = t => t * t * (3 - 2 * t);
  const seg = (p, a, b) => clamp((p - a) / (b - a), 0, 1);
  const lerp = (a, b, t) => a + (b - a) * t;

  class HrdScroll3D extends HTMLElement {
    connectedCallback() {
      if (this._booted) return;
      this._booted = true;
      this.style.display = 'block';
      this.style.width = '100%';
      this.style.height = '100%';
      this.canvas = document.createElement('canvas');
      this.canvas.style.cssText = 'display:block;width:100%;height:100%';
      this.appendChild(this.canvas);
      this._waitForThree();
    }

    _waitForThree() {
      if (window.THREE) return this._init();
      let tries = 0;
      const id = setInterval(() => {
        if (window.THREE) { clearInterval(id); this._init(); }
        else if (++tries > 200) clearInterval(id);
      }, 50);
    }

    _init() {
      const T = window.THREE;
      const renderer = new T.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      if (T.sRGBEncoding) renderer.outputEncoding = T.sRGBEncoding;
      renderer.toneMapping = T.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      this.renderer = renderer;

      const scene = new T.Scene();
      scene.background = new T.Color(0xf1f3f4);
      this.scene = scene;

      const camera = new T.PerspectiveCamera(36, 1, 0.5, 8000);
      this.camera = camera;
      this.cam = { dist: 200, theta: 0.85, phi: 1.18, tx: 0, ty: 40, tz: 0 };

      scene.add(new T.HemisphereLight(0xf7f8fa, 0xbfc5ca, 0.72));
      const key = new T.DirectionalLight(0xffffff, 1.0);
      key.position.set(260, 400, 220);
      scene.add(key);
      const fill = new T.DirectionalLight(0xe6ecf5, 0.5);
      fill.position.set(-320, 160, 200); scene.add(fill);
      const rimA = new T.DirectionalLight(0xffffff, 0.5);
      rimA.position.set(-120, 260, -340); scene.add(rimA);
      const rimB = new T.DirectionalLight(0xdde3ea, 0.34);
      rimB.position.set(300, 60, -260); scene.add(rimB);

      const floor = new T.Mesh(
        new T.CircleGeometry(1400, 64),
        new T.MeshStandardMaterial({ color: 0xe7e9eb, roughness: 0.95, metalness: 0 })
      );
      floor.rotation.x = -Math.PI / 2;
      floor.position.y = -1;
      scene.add(floor);

      this.mats = [];
      this.pipeta = this._buildPipeta(T);
      this.conector = this._buildConector(T);
      this.poste = this._buildPoste(T);
      scene.add(this.pipeta, this.conector, this.poste);

      this.track = this.closest('[data-3d-track]') || this.parentElement;
      this.onScroll = () => { if (!this.raf) this.raf = requestAnimationFrame(this.tickFn); };
      this.tickFn = () => { this.raf = 0; this._frame(); };
      window.addEventListener('scroll', this.onScroll, { passive: true, capture: true });
      window.addEventListener('resize', this.onScroll, { passive: true });
      this._loop = () => { this._rafLoop = requestAnimationFrame(this._loop); this._frame(); };
      this._loop();
    }

    _steel(T, tint) {
      const m = new T.MeshStandardMaterial({
        color: tint || 0xc4c9ce, metalness: 0.95, roughness: tint ? 0.38 : 0.26,
        transparent: true, opacity: 1
      });
      this.mats.push(m);
      return m;
    }

    _mat(T, opts) {
      const m = new T.MeshStandardMaterial(Object.assign({ transparent: true, opacity: 1 }, opts));
      this.mats.push(m);
      return m;
    }

    _glass(T) {
      const m = new T.MeshPhysicalMaterial({
        color: 0x9fd0de, transparent: true, opacity: 0.24, roughness: 0.05,
        metalness: 0, side: T.DoubleSide
      });
      this.mats.push(m);
      return m;
    }

    _buildPipeta(T) {
      const g = new T.Group();
      const M = this._steel(T), MD = this._steel(T, 0xa9aeb4);
      const socket = this._mat(T, { color: 0x53585e, metalness: 0.7, roughness: 0.5 });
      const nylon = this._mat(T, { color: 0xdfe0dc, metalness: 0, roughness: 0.7 });
      const glass = this._glass(T);

      const cylY = (r1, r2, len, mat, x, y, z) => {
        const m = new T.Mesh(new T.CylinderGeometry(r1, r2, len, 48), mat);
        m.position.set(x, y, z); g.add(m); return m;
      };
      const cylX = (r1, r2, len, mat, x, y, z) => {
        const m = new T.Mesh(new T.CylinderGeometry(r1, r2, len, 48), mat);
        m.rotation.z = Math.PI / 2; m.position.set(x, y, z); g.add(m); return m;
      };

      const bodyR = 12.5, bodyH = 53, flangeR = 16;
      cylY(flangeR, flangeR, 4, M, 0, 2, 0);
      cylY(flangeR - 1, bodyR, 3, M, 0, 5.5, 0);
      cylY(bodyR, bodyR, bodyH - 7, M, 0, 7 + (bodyH - 7) / 2, 0);
      cylY(bodyR, bodyR, 1.5, MD, 0, bodyH - 0.5, 0);

      const set = new T.Mesh(new T.CylinderGeometry(3.2, 3.2, bodyR * 2 + 1, 6), socket);
      set.rotation.z = Math.PI / 2; set.position.set(0, 15, 0); g.add(set);

      const armY = 40;
      let x = bodyR - 1;
      cylX(7.5, 7.5, 9, M, x + 4.5, armY, 0); x += 9;
      cylX(10.5, 10.5, 5, MD, x + 2.5, armY, 0); x += 5;
      cylX(8, 8, 3.5, nylon, x + 1.75, armY, 0); x += 3.5;
      const pane = new T.Mesh(new T.BoxGeometry(10, 60, 60), glass);
      pane.position.set(x + 5, armY, 0); g.add(pane); x += 10;
      cylX(13, 13, 8, M, x + 4, armY, 0);
      const head = cylX(13, 13, 2.2, MD, x + 8.3, armY, 0);
      const hex = new T.Mesh(new T.CylinderGeometry(5.5, 5.5, 2.6, 6), socket);
      hex.rotation.z = Math.PI / 2; hex.position.set(x + 8.7, armY, 0); g.add(hex);
      void head;
      return g;
    }

    _buildConector(T) {
      const g = new T.Group();
      const M = this._steel(T), MD = this._steel(T, 0xa9aeb4);
      const socket = this._mat(T, { color: 0x53585e, metalness: 0.7, roughness: 0.5 });
      const gasket = this._mat(T, { color: 0x0f1012, metalness: 0.02, roughness: 0.9 });
      const glass = this._glass(T);
      const cylX = (r1, r2, len, mat, x, y, z) => {
        const m = new T.Mesh(new T.CylinderGeometry(r1, r2, len, 48), mat);
        m.rotation.z = Math.PI / 2; m.position.set(x, y, z); g.add(m); return m;
      };

      const R = 22, y = 44;
      let x = -43;
      cylX(R - 1.2, R, 1.5, M, x + 0.75, y, 0);
      cylX(R, R, 37, M, x + 19.5, y, 0);
      cylX(R, R - 0.8, 1.5, MD, x + 38.75, y, 0);
      x += 40;

      const pane = new T.Mesh(new T.BoxGeometry(10, 84, 84), glass);
      pane.position.set(x + 5, y, 0); g.add(pane);
      x += 10;

      cylX(R - 0.5, R - 0.5, 3, gasket, x + 1.5, y, 0);
      x += 3;

      cylX(R, R, 4, M, x + 2, y, 0);
      cylX(R, R - 3.5, 3, M, x + 5.5, y, 0);
      cylX(R - 3.5, R - 3.5, 0.8, MD, x + 7.4, y, 0);
      cylX(6.5, 6.5, 1.2, MD, x + 7.9, y, 0);
      const hex = new T.Mesh(new T.CylinderGeometry(3.6, 3.6, 4, 6), socket);
      hex.rotation.z = Math.PI / 2; hex.position.set(x + 7.2, y, 0); g.add(hex);
      return g;
    }

    _buildPoste(T) {
      const g = new T.Group();
      const M = this._steel(T), MD = this._steel(T, 0x9ba0a6);
      const socket = this._mat(T, { color: 0x53585e, metalness: 0.7, roughness: 0.5 });
      const glass = this._glass(T);
      const box = (w, h, d, mat, x, y, z) => {
        const m = new T.Mesh(new T.BoxGeometry(w, h, d), mat);
        m.position.set(x, y, z); g.add(m); return m;
      };

      const W = 25, D = 50, H = 450, faceTop = 380, slotLen = 300, slotBase = 50;
      const slotT = 12, sideD = (D - slotT) / 2, plate = 100, plateT = 8;

      box(plate, plateT, plate, M, 0, plateT / 2, 0);
      [[36, 36], [-36, 36], [36, -36], [-36, -36]].forEach(([hx, hz]) => {
        const h = new T.Mesh(new T.CylinderGeometry(4, 4, plateT + 1.2, 24), socket);
        h.position.set(hx, plateT / 2, hz); g.add(h);
      });

      box(W, slotBase, D, M, 0, plateT + slotBase / 2, 0);
      const solidTop = plateT + slotBase;
      const frontH = faceTop - solidTop, backH = H - solidTop;
      box(W, frontH, sideD, M, 0, solidTop + frontH / 2, (slotT + sideD) / 2);
      box(W, backH, sideD, M, 0, solidTop + backH / 2, -(slotT + sideD) / 2);
      box(W - 1, slotLen, slotT, MD, 0, solidTop + slotLen / 2, 0);

      const pane = new T.Mesh(new T.BoxGeometry(260, 470, 10), glass);
      pane.position.set(0, solidTop + 200, 0); g.add(pane);

      [110, 300].forEach(sy => {
        const s = new T.Mesh(new T.CylinderGeometry(5, 5, 2.5, 24), MD);
        s.rotation.x = Math.PI / 2; s.position.set(0, sy, D / 2 + 0.5); g.add(s);
        const hex = new T.Mesh(new T.CylinderGeometry(2, 2, 3, 6), socket);
        hex.rotation.x = Math.PI / 2; hex.position.set(0, sy, D / 2 + 0.9); g.add(hex);
      });
      return g;
    }

    _setOpacity(group, o) {
      group.visible = o > 0.01;
      group.traverse(n => {
        if (n.material) {
          const base = n.material.userData._base != null
            ? n.material.userData._base
            : (n.material.userData._base = n.material.opacity);
          n.material.opacity = base * o;
        }
      });
    }

    _frame() {
      const T = window.THREE;
      const track = this.track;
      if (!track) return;
      const r = track.getBoundingClientRect();
      const span = r.height - window.innerHeight;
      const p = span > 0 ? clamp(-r.top / span, 0, 1) : 0;

      const a = smooth(seg(p, 0, 0.28));
      const t1 = smooth(seg(p, 0.26, 0.40));
      const m = smooth(seg(p, 0.38, 0.62));
      const t2 = smooth(seg(p, 0.60, 0.74));
      const b = smooth(seg(p, 0.72, 1));

      this._setOpacity(this.pipeta, 1 - t1);
      this._setOpacity(this.conector, t1 * (1 - t2));
      this._setOpacity(this.poste, t2);

      this.pipeta.rotation.y = lerp(-0.75, 1.05, a);
      this.pipeta.position.y = lerp(0, 16, t1);
      this.conector.rotation.y = lerp(-0.9, 0.85, m);
      this.conector.position.y = lerp(-16, 0, t1) + lerp(0, 16, t2);
      this.poste.rotation.y = lerp(-0.55, 0.95, b);
      this.poste.position.y = lerp(-70, 0, t2);

      const cvw = this.canvas.clientWidth || 1, cvh = this.canvas.clientHeight || 1;
      const ar = cvw / cvh;
      const zoomOut = ar < 1 ? lerp(1.85, 1.15, clamp((ar - 0.45) / 0.55, 0, 1)) : 1;
      const lift = ar < 1 ? lerp(0.24, 0.06, clamp((ar - 0.45) / 0.55, 0, 1)) : 0;
      const mix3 = (v1, v2, v3) => lerp(lerp(v1, v2, t1), v3, t2);
      const dist = mix3(lerp(232, 178, a), lerp(268, 214, m), lerp(830, 650, b)) * zoomOut;
      // The full-screen mobile composition reserves its upper area for the
      // technical heading. Aim the camera higher so the part sits visually
      // in the remaining center, instead of crowding the title.
      const mobileCentering = window.innerWidth <= 900 ? dist * 0.18 : 0;
      const ty = mix3(34, 44, 232) - dist * lift + mobileCentering;
      const tx = mix3(14, -8, 0);
      const phi = mix3(lerp(1.28, 1.12, a), lerp(1.34, 1.18, m), lerp(1.36, 1.18, b));
      const theta = 0.72 + p * 0.55;

      const c = this.camera;
      c.position.set(
        tx + dist * Math.sin(phi) * Math.sin(theta),
        ty + dist * Math.cos(phi),
        dist * Math.sin(phi) * Math.cos(theta)
      );
      c.lookAt(new T.Vector3(tx, ty, 0));

      const cv = this.canvas;
      const w = cv.clientWidth, h = cv.clientHeight;
      if (w && h && (cv.width !== Math.round(w * Math.min(window.devicePixelRatio, 2)) || this._lw !== w || this._lh !== h)) {
        this.renderer.setSize(w, h, false);
        c.aspect = w / h;
        c.updateProjectionMatrix();
        this._lw = w; this._lh = h;
      }
      this.renderer.render(this.scene, c);
    }

    disconnectedCallback() {
      window.removeEventListener('scroll', this.onScroll, { capture: true });
      window.removeEventListener('resize', this.onScroll);
      if (this._rafLoop) cancelAnimationFrame(this._rafLoop);
      if (this.renderer) this.renderer.dispose();
    }
  }

  if (!window.customElements.get('hrd-scroll-3d')) {
    window.customElements.define('hrd-scroll-3d', HrdScroll3D);
  }
})();
