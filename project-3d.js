import * as THREE from 'https://esm.sh/three@0.160.0';
import { GLTFLoader } from 'https://esm.sh/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'https://esm.sh/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

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
      this.renderer.domElement.style.width = '100%';
      this.renderer.domElement.style.height = '100%';
      this.renderer.domElement.style.display = 'block';
      this.replaceChildren(this.renderer.domElement);

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(32, 1, 0.01, 30);
      this.camera.position.set(2.1, 1.65, 2.15);
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
      this.controls.target.set(0, 0.5, 0);
      this.controls.minDistance = 1.3;
      this.controls.maxDistance = 9;
      this.controls.maxPolarAngle = Math.PI * 0.52;
      this.controls.enablePan = false;
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.06;
      this.controls.autoRotate = this.preview && !reduceMotion.matches;
      this.controls.autoRotateSpeed = 0.55;

      const pmrem = new THREE.PMREMGenerator(this.renderer);
      const environment = pmrem.fromScene(new RoomEnvironment(), 0.04);
      this.scene.environment = environment.texture;
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
    const source = this.getAttribute('src');
    new GLTFLoader().load(source, (gltf) => {
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
      this.baseTarget = new THREE.Vector3(0, 0.5, 0);
      this.modelRadius = 1;
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
    const aspectCorrection = Math.max(1, 1.62 / this.camera.aspect);
    const previewCorrection = this.preview ? 1.08 : 1;
    const offset = new THREE.Vector3(2.1, 1.15, 2.15).multiplyScalar(aspectCorrection * previewCorrection);
    this.controls.target.copy(this.baseTarget);
    this.camera.position.copy(this.baseTarget).add(offset);
    this.controls.minDistance = 1.3;
    this.controls.maxDistance = 9;
    this.baseCamera = this.camera.position.clone();
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
    const oldScale = 1 + this.amount * 0.7;
    const newScale = 1 + target * 0.7;
    const offset = this.camera.position.clone().sub(this.controls.target).multiplyScalar(newScale / oldScale);
    const raisedTarget = this.baseTarget.clone();
    raisedTarget.y += 0.42 * target;
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
    if (reduceMotion.matches) {
      this.setAmount(target);
      return;
    }
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
    this.camera.position.copy(this.baseCamera);
    this.controls.minDistance = 1.3;
    this.controls.update();
  }

  showCorner() {
    if (!this.ready) return;
    cancelAnimationFrame(this.tweenFrame);
    this.setAmount(0);
    this.corner = true;
    this.controls.minDistance = 0.16;
    this.controls.target.set(0, 0.5, 0.406);
    this.camera.position.set(0.85, 1.1, 2.6);
    this.controls.update();
  }
}

customElements.define('hrd-project-3d', HerraideaProject3D);

const dialog = document.querySelector('#project-dialog');
const viewer = document.querySelector('#futbolito-viewer');
const range = document.querySelector('#project-range');
const rangeValue = document.querySelector('#project-range-value');
const status = document.querySelector('#project-status');

const closeProject = () => {
  if (dialog?.open) dialog.close();
};

const openProject = () => {
  if (dialog.open) return;
  dialog.showModal();
  document.body.classList.add('project-open');
  viewer.start();
  requestAnimationFrame(() => viewer.resize());
};

document.querySelector('[data-open-project]')?.addEventListener('click', openProject);
document.querySelector('.project-card')?.addEventListener('click', (event) => {
  if (event.target.closest('[data-open-project]')) return;
  openProject();
});

dialog?.querySelector('.project-close')?.addEventListener('click', closeProject);
dialog?.addEventListener('click', (event) => {
  if (event.target === dialog) closeProject();
});
dialog?.addEventListener('close', () => {
  document.body.classList.remove('project-open');
  viewer.visible = false;
});
dialog?.querySelector('[data-project-explode]')?.addEventListener('click', () => viewer.animateTo(1));
dialog?.querySelector('[data-project-assemble]')?.addEventListener('click', () => viewer.animateTo(0));
dialog?.querySelector('[data-project-corner]')?.addEventListener('click', () => viewer.showCorner());

viewer?.addEventListener('projectready', () => {
  range.disabled = false;
  dialog.querySelectorAll('.project-actions button').forEach((button) => { button.disabled = false; });
  status.textContent = 'Modelo listo · arrastra para girar y usa la rueda o pellizco para acercar.';
});
viewer?.addEventListener('projecterror', (event) => {
  status.textContent = event.detail.message;
});
viewer?.addEventListener('projectprogress', (event) => {
  range.value = event.detail.value;
  range.style.setProperty('--project-range', `${event.detail.value}%`);
  rangeValue.textContent = `${event.detail.value} %`;
});
range?.addEventListener('input', () => {
  cancelAnimationFrame(viewer.tweenFrame);
  viewer.setAmount(Number(range.value) / 100);
});
