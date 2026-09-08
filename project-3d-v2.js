import * as THREE from 'https://esm.sh/three@0.160.0';
import { GLTFLoader } from 'https://esm.sh/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'https://esm.sh/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const profiles = {
  clips: { target: [0, .48, 0], camera: [1.3, 1, 2.1], min: .7, detailTarget: [-.413, .695, 0], detailCamera: [-.163, .845, .48] },
  hrd1518: { target: [0, .48, 0], camera: [1.3, 1, 2.1], min: .3, detailTarget: [0, .78, .05], detailCamera: [.23, .89, .39] },
  futbolito: { target: [0, .5, 0], camera: [2.1, 1.65, 2.15], min: 1.3, detailTarget: [0, .5, .406], detailCamera: [.85, 1.1, 2.6] }
};

const projects = {
  clips: {
    src: '/assets/projects/clip-system/herraje-cristal.glb', profile: 'clips', kicker: 'Solución interactiva 01',
    title: 'Postes con clips + vidrio', number: '01 / HRD 1525 · Barandal con clips',
    heading: 'Mira cómo cada herraje sostiene la solución.',
    description: 'Recorre el sistema completo y acércate a la unión entre poste, pinza y cristal.',
    content: '46 piezas y conjuntos', detail: 'Ver pinza',
    aria: 'Modelo tridimensional interactivo de postes con clips y vidrio', caveat: ''
  },
  hrd1518: {
    src: '/assets/projects/hrd-1518/hrd-1518.glb', profile: 'hrd1518', kicker: 'Pieza interactiva 02',
    title: 'Poste HRD 1518', number: '02 / HRD 1518',
    heading: 'Del poste completo a cada unión.',
    description: 'Gira el sistema, acércate a sus soportes y controla la separación de cada componente.',
    content: '23 componentes y conjuntos', detail: 'Ver unión',
    aria: 'Modelo tridimensional interactivo del poste HRD 1518 con pasamanos y tres barras',
    caveat: 'Las barras y el pasamanos muestran el sistema instalado y no indican por sí solos el contenido comercial del kit.'
  },
  futbolito: {
    src: '/assets/projects/futbolito/futbolito-herraidea.glb', profile: 'futbolito', kicker: 'Proyecto interactivo 03',
    title: 'Futbolito Herraidea', number: '03 / Proyecto especial',
    heading: 'Observa cómo cada parte forma el proyecto.',
    description: 'Gira el modelo, acércate a sus uniones y controla la separación de todos sus componentes.',
    content: '190 piezas y conjuntos', detail: 'Ver costado',
    aria: 'Modelo tridimensional interactivo del Futbolito Herraidea',
    caveat: 'Modelo conceptual reconstruido a partir de fotografías. Las medidas y la secuencia de fabricación están por confirmar.'
  }
};

class HerraideaProject3D extends HTMLElement {
  constructor() {
    super();
    this.amount = 0;
    this.ready = false;
    this.started = false;
    this.visible = false;
    this.corner = false;
    this.animationFrame = 0;
    this.tweenFrame = 0;
  }

  connectedCallback() {
    this.preview = this.hasAttribute('preview');
    this.profile = profiles[this.getAttribute('profile')] || profiles.futbolito;
    this.innerHTML = '<span class="project-model-loading">Preparando modelo 3D…</span>';
    this.observer = new IntersectionObserver(([entry]) => {
      this.visible = entry.isIntersecting;
      if (entry.isIntersecting && this.preview) this.start();
    }, { rootMargin: '180px' });
    this.observer.observe(this);
  }

  disconnectedCallback() {
    this.observer?.disconnect();
    this.resizeObserver?.disconnect();
    cancelAnimationFrame(this.animationFrame);
    cancelAnimationFrame(this.tweenFrame);
    this.renderer?.dispose();
  }

  start() {
    if (this.started) {
      this.visible = true;
      this.resize();
      return;
    }
    this.started = true;
    this.visible = true;
    try {
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, this.preview ? 1.25 : 1.7));
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1.08;
      this.renderer.outputColorSpace = THREE.SRGBColorSpace;
      this.renderer.setClearColor(0x000000, 0);
      Object.assign(this.renderer.domElement.style, { width: '100%', height: '100%', display: 'block' });
      this.replaceChildren(this.renderer.domElement);

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(32, 1, .01, 30);
      this.camera.position.fromArray(this.profile.camera);
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
      this.controls.target.fromArray(this.profile.target);
      this.controls.minDistance = this.profile.min;
      this.controls.maxDistance = 9;
      this.controls.maxPolarAngle = Math.PI * .55;
      this.controls.enablePan = false;
      this.controls.enableDamping = true;
      this.controls.dampingFactor = .06;
      this.controls.autoRotate = this.preview && !reduceMotion.matches;
      this.controls.autoRotateSpeed = .55;

      const pmrem = new THREE.PMREMGenerator(this.renderer);
      this.scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
      this.scene.add(new THREE.HemisphereLight(0xffffff, 0x6c7075, 1.15));
      const key = new THREE.DirectionalLight(0xffffff, 2.7);
      key.position.set(3, 5, 2);
      this.scene.add(key);
      const rim = new THREE.DirectionalLight(0xc9e7ff, 1.25);
      rim.position.set(-3, 2, -3);
      this.scene.add(rim);

      this.resizeObserver = new ResizeObserver(() => this.resize());
      this.resizeObserver.observe(this);
      this.resize();
      this.loadModel();
      this.loop();
    } catch (error) {
      this.fail('Este dispositivo no pudo iniciar el visor 3D.', error);
    }
  }

  loadModel() {
    new GLTFLoader().load(this.getAttribute('src'), (gltf) => {
      this.model = gltf.scene;
      this.scene.add(this.model);
      this.mixer = new THREE.AnimationMixer(this.model);
      const clip = gltf.animations.find((item) => item.name === 'Despiece') || gltf.animations[0];
      if (clip) {
        this.duration = clip.duration;
        this.action = this.mixer.clipAction(clip);
        this.action.play();
        this.action.paused = true;
      }
      this.baseTarget = new THREE.Vector3().fromArray(this.profile.target);
      this.baseCamera = new THREE.Vector3().fromArray(this.profile.camera);
      this.fitModel();
      this.ready = true;
      this.setAmount(0, false);
      this.dispatchEvent(new CustomEvent('projectready', { bubbles: true }));
    }, undefined, (error) => this.fail('No se pudo cargar el modelo en este dispositivo.', error));
  }

  fail(message, error) {
    console.error(error);
    this.innerHTML = `<span class="project-model-error">${message}</span>`;
    this.dispatchEvent(new CustomEvent('projecterror', { bubbles: true, detail: { message } }));
  }

  resize() {
    if (!this.renderer || !this.clientWidth || !this.clientHeight) return;
    this.renderer.setSize(this.clientWidth, this.clientHeight, false);
    this.camera.aspect = this.clientWidth / this.clientHeight;
    this.camera.updateProjectionMatrix();
    if (this.ready && !this.corner && this.amount === 0) this.fitModel();
  }

  fitModel() {
    if (!this.baseTarget || !this.camera || !this.controls) return;
    const aspect = Math.max(1, 1.55 / this.camera.aspect);
    const preview = this.preview ? 1.08 : 1;
    const offset = this.baseCamera.clone().sub(this.baseTarget).multiplyScalar(aspect * preview);
    this.controls.target.copy(this.baseTarget);
    this.camera.position.copy(this.baseTarget).add(offset);
    this.controls.minDistance = this.profile.min;
    this.controls.maxDistance = 9;
    this.fittedCamera = this.camera.position.clone();
    this.controls.update();
  }

  loop() {
    this.animationFrame = requestAnimationFrame(() => this.loop());
    if (!this.visible || !this.renderer) return;
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  setAmount(value, notify = true) {
    if (!this.ready || !this.action) return;
    const target = Math.max(0, Math.min(1, value));
    if (this.corner) this.resetView();
    const oldScale = 1 + this.amount * .7;
    const newScale = 1 + target * .7;
    const offset = this.camera.position.clone().sub(this.controls.target).multiplyScalar(newScale / oldScale);
    const raisedTarget = this.baseTarget.clone();
    raisedTarget.y += .3 * target;
    this.controls.target.copy(raisedTarget);
    this.camera.position.copy(this.controls.target).add(offset);
    this.amount = target;
    this.action.time = target * (this.duration || 3);
    this.mixer.update(0);
    this.controls.update();
    if (notify) this.dispatchEvent(new CustomEvent('projectprogress', { bubbles: true, detail: { value: Math.round(target * 100) } }));
  }

  animateTo(target) {
    if (!this.ready) return;
    cancelAnimationFrame(this.tweenFrame);
    if (reduceMotion.matches) return this.setAmount(target);
    const start = performance.now();
    const from = this.amount;
    const tick = (now) => {
      const elapsed = Math.min(1, (now - start) / 2200);
      const eased = elapsed * elapsed * (3 - 2 * elapsed);
      this.setAmount(from + (target - from) * eased);
      if (elapsed < 1) this.tweenFrame = requestAnimationFrame(tick);
    };
    this.tweenFrame = requestAnimationFrame(tick);
  }

  resetView() {
    this.corner = false;
    this.controls.target.copy(this.baseTarget);
    this.camera.position.copy(this.fittedCamera || this.baseCamera);
    this.controls.minDistance = this.profile.min;
    this.controls.update();
  }

  showCorner() {
    if (!this.ready) return;
    cancelAnimationFrame(this.tweenFrame);
    this.setAmount(0);
    this.corner = true;
    this.controls.minDistance = .12;
    this.controls.target.fromArray(this.profile.detailTarget);
    this.camera.position.fromArray(this.profile.detailCamera);
    this.controls.update();
  }
}

customElements.define('hrd-project-3d', HerraideaProject3D);

const dialog = document.querySelector('#project-dialog');
const rail = document.querySelector('#projects-rail');
const cards = [...document.querySelectorAll('.project-card[data-project]')];
const dots = [...document.querySelectorAll('[data-project-slide]')];
const next = document.querySelector('.projects-next');
const range = document.querySelector('#project-range');
const rangeValue = document.querySelector('#project-range-value');
const status = document.querySelector('#project-status');
let viewer = document.querySelector('#project-viewer');
let activeSlide = 0;

const setSlide = (index, behavior = 'smooth') => {
  if (!rail || !cards.length) return;
  activeSlide = (index + cards.length) % cards.length;
  const card = cards[activeSlide];
  rail.scrollTo({ left: card.offsetLeft - rail.offsetLeft, behavior });
  dots.forEach((dot, dotIndex) => dot.classList.toggle('active', dotIndex === activeSlide));
};

let slideFrame = 0;
rail?.addEventListener('scroll', () => {
  cancelAnimationFrame(slideFrame);
  slideFrame = requestAnimationFrame(() => {
    const center = rail.scrollLeft + rail.clientWidth / 2;
    activeSlide = cards.reduce((best, card, index) => {
      const cardCenter = card.offsetLeft - rail.offsetLeft + card.offsetWidth / 2;
      const distance = Math.abs(cardCenter - center);
      return distance < best.distance ? { index, distance } : best;
    }, { index: 0, distance: Infinity }).index;
    dots.forEach((dot, index) => dot.classList.toggle('active', index === activeSlide));
  });
}, { passive: true });
dots.forEach((dot, index) => dot.addEventListener('click', () => setSlide(index)));
next?.addEventListener('click', () => setSlide(activeSlide + 1));

const bindViewer = () => {
  viewer.addEventListener('projectready', () => {
    range.disabled = false;
    dialog.querySelectorAll('.project-actions button').forEach((button) => { button.disabled = false; });
    status.textContent = 'Modelo listo · arrastra para girar y usa la rueda o pellizco para acercar.';
  });
  viewer.addEventListener('projecterror', (event) => { status.textContent = event.detail.message; });
  viewer.addEventListener('projectprogress', (event) => {
    range.value = event.detail.value;
    range.style.setProperty('--project-range', `${event.detail.value}%`);
    rangeValue.textContent = `${event.detail.value} %`;
  });
};

const openProject = (key) => {
  const project = projects[key];
  if (!dialog || !project || dialog.open) return;
  document.querySelector('#project-dialog-kicker').textContent = project.kicker;
  document.querySelector('#project-dialog-title').textContent = project.title;
  document.querySelector('#project-number').textContent = project.number;
  document.querySelector('#project-heading').textContent = project.heading;
  document.querySelector('#project-description').textContent = project.description;
  document.querySelector('#project-content').textContent = project.content;
  document.querySelector('#project-detail-label').textContent = project.detail;
  const caveat = document.querySelector('#project-caveat');
  caveat.textContent = project.caveat;
  caveat.hidden = !project.caveat;
  range.value = 0;
  range.disabled = true;
  range.style.setProperty('--project-range', '0%');
  rangeValue.textContent = '0 %';
  status.textContent = 'Preparando el modelo 3D…';
  dialog.querySelectorAll('.project-actions button').forEach((button) => { button.disabled = true; });

  const replacement = document.createElement('hrd-project-3d');
  replacement.id = 'project-viewer';
  replacement.setAttribute('src', project.src);
  replacement.setAttribute('profile', project.profile);
  replacement.setAttribute('role', 'img');
  replacement.setAttribute('aria-label', project.aria);
  viewer.replaceWith(replacement);
  viewer = replacement;
  bindViewer();

  dialog.showModal();
  document.body.classList.add('project-open');
  viewer.start();
  requestAnimationFrame(() => viewer.resize());
};

cards.forEach((card) => {
  card.addEventListener('click', (event) => {
    if (event.target.closest('[data-open-project]')) return;
    openProject(card.dataset.project);
  });
});
document.querySelectorAll('[data-open-project]').forEach((button) => button.addEventListener('click', () => openProject(button.dataset.openProject)));

const closeProject = () => { if (dialog?.open) dialog.close(); };
dialog?.querySelector('.project-close')?.addEventListener('click', closeProject);
dialog?.addEventListener('click', (event) => { if (event.target === dialog) closeProject(); });
dialog?.addEventListener('close', () => {
  document.body.classList.remove('project-open');
  viewer.visible = false;
});
dialog?.querySelector('[data-project-explode]')?.addEventListener('click', () => viewer.animateTo(1));
dialog?.querySelector('[data-project-assemble]')?.addEventListener('click', () => viewer.animateTo(0));
dialog?.querySelector('[data-project-corner]')?.addEventListener('click', () => viewer.showCorner());
range?.addEventListener('input', () => {
  cancelAnimationFrame(viewer.tweenFrame);
  viewer.setAmount(Number(range.value) / 100);
});

bindViewer();
