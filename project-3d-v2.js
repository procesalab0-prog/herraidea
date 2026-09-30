import * as THREE from '/assets/vendor/three/three.module.js';
import { GLTFLoader } from '/assets/vendor/three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from '/assets/vendor/three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from '/assets/vendor/three/addons/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const profiles = {
  domo: { target: [.4, 1.6, 0], camera: [-5.6, 2.6, 13], min: 2, max: 65, far: 160, detailTarget: [0, .5, -.1], detailCamera: [.2, 9.4, 7.6] },
  riverack: { target: [0, .3, 0], camera: [1.9, 1.25, 3.2], min: .5, detailTarget: [-.735, .63, .75], detailCamera: [-.25, .95, 1.55] },
  hrd1206: { target: [0, .55, 0], camera: [1.5, 1.1, 3.8], min: .12, detailTarget: [0, 1.055, .007], detailCamera: [.18, 1.15, .3] },
  hrd153x: { target: [0, .52, 0], camera: [1.2, 1.1, 2.1], min: .15, detailTarget: [0, .88, 0], detailCamera: [.19, 1.13, .29] },
  hrd1220: { target: [0, .095, 0], camera: [.31, .23, .45], min: .06, detailTarget: [0, .09, .018], detailCamera: [.10, .14, .20] },
  hrd1221: { target: [0, .53, .03], camera: [1.45, 1.08, 2.15], min: .25, detailTarget: [0, .78, .03], detailCamera: [.28, .89, .48] },
  hrd1223: { target: [0, .53, .03], camera: [1.45, 1.08, 2.15], min: .25, detailTarget: [.08, .78, .07], detailCamera: [.37, .9, .46] },
  clips: { target: [0, .48, 0], camera: [1.3, 1, 2.1], min: .7, detailTarget: [-.413, .695, 0], detailCamera: [-.163, .845, .48] },
  hrd1518: { target: [0, .48, 0], camera: [1.3, 1, 2.1], min: .3, detailTarget: [0, .78, .05], detailCamera: [.23, .89, .39] },
  hrd1616: { target: [.57, .52, .57], camera: [2.2, 1.55, 2.35], min: .45, detailTarget: [0, .53, 0], detailCamera: [.48, .82, .5] },
  futbolito: { target: [0, .5, 0], camera: [2.1, 1.65, 2.15], min: 1.3, detailTarget: [0, .5, .406], detailCamera: [.85, 1.1, 2.6] }
};

const projects = {
  domo: {
    src: '/assets/projects/domo-geodesico/domo-geodesico.glb?v=1-60-0', profile: 'domo',
    title: 'Domo geodésico', number: 'Proyecto de glamping · Herraidea',
    description: 'Un espacio para conectar con el exterior.',
    content: '467 piezas y elementos de contexto', detail: 'Ver interior',
    aria: 'Modelo interactivo de domo geodésico con terraza e interior amueblado',
    caveat: 'Modelo ilustrativo basado en referencias. Medidas, uniones, mobiliario y terraza sujetos a definición del proyecto.'
  },
  riverack: {
    src: '/assets/projects/riverack/riverack.glb?v=1-59-0', profile: 'riverack',
    title: 'Riverack', number: 'Rack de caja · RAM 700',
    description: 'Diseñado para la aventura. Probado en RAM 700.',
    content: '100 piezas · 56 tornillos', detail: 'Ver unión',
    aria: 'Modelo interactivo del rack Riverack para caja de pickup',
    caveat: 'Modelo ilustrativo. Consulta las medidas y la adaptación a tu vehículo con Herraidea.'
  },
  hrd1206: {
    src: '/assets/projects/postes-cortos/postes-cortos.glb?v=1-54-0', profile: 'hrd1206', kicker: 'Conector cuadrado vidrio-vidrio',
    title: 'HRD 1301-A / 1302-B / 1301-C', number: 'Uniones de vidrio · Acero satinado',
    heading: 'Cristal libre. Uniones discretas.',
    description: 'HRD 1301-A: vidrio a muro. HRD 1302-B: alineador rectangular. HRD 1301-C: esquina vidrio-vidrio. Con postes HRD 1206 de 45 cm en acero satinado.',
    content: '72 piezas y elementos de contexto', detail: 'Ver unión superior',
    aria: 'Modelo de apoyos cortos en acero y unión rectangular superior entre cristales',
    caveat: 'Estudio según fotografías. Postes HRD 1206 de 45 cm. Dimensiones de los conectores, vidrio y anclajes pendientes de confirmar.'
  },
  hrd153x: {
    src: '/assets/projects/hrd-153x/hrd-153x.glb?v=1-51-0', profile: 'hrd153x', kicker: 'Estudio interactivo · HRD 1533 / 1534 / 1535',
    title: 'HRD 1533 / 1534 / 1535 · Vidrio en canal', number: 'Postes con canales · Acero satinado',
    heading: 'El cristal se integra en el poste.',
    description: 'Incluye vinil de empaque para vidrio de 10 mm de espesor. Explora el perfil acanalado, la base de cuatro agujeros y el soporte articulado del pasamanos.',
    content: '17 piezas y elementos de contexto', detail: 'Ver canal y soporte',
    aria: 'Estudio de poste acanalado en acero satinado con vidrio y pasamanos',
    caveat: 'Reconstrucción visual a partir de fotografías. Medidas del perfil y configuración de cada código pendientes de confirmar.'
  },
  hrd1220: {
    src: '/assets/projects/hrd-1220/hrd-1220-piloto.glb?v=1-57-0', profile: 'hrd1220', kicker: 'Estudio interactivo · HRD 1220',
    title: 'HRD 1220 · Despiece por etapas', number: 'HRD 1220 · Pinza baja',
    heading: 'Cada pieza, en su lugar.',
    description: 'Explora el HRD 1220 en acero satinado. Controla su despiece por etapas o vuelve a armarlo: la tapa decorativa baja al final.',
    content: '9 componentes · Armado por etapas', detail: 'Ver pinza',
    aria: 'Pinza HRD 1220 en acero satinado con despiece por etapas',
    caveat: 'Pinza reconstruida según CAD: 185 mm de altura, base de 101.6 × 101.6 mm y vidrio de 10–12 mm. Espesores internos y tornillería aproximados; animación ilustrativa.'
  },
  hrd1221: {
    src: '/assets/projects/hrd-1221/hrd-1221.glb?v=1-46-0', profile: 'hrd1221', kicker: 'Estudio interactivo · HRD 1221',
    title: 'HRD 1221 · Soleras y tubo', number: 'HRD 1221 · Soleras planas',
    heading: 'Una solera continua. Dos puntos de sujeción.',
    description: 'Explora el poste circular, las dos soleras horizontales y su fijación central. Acércate a los discos del vidrio o separa cada componente.',
    content: '33 piezas y elementos de contexto', detail: 'Ver solera',
    aria: 'HRD 1221 de cuerpo circular con dos soleras horizontales continuas y vidrio',
    caveat: 'Reconstrucción visual según CAD. Espesores, anclaje y detalles internos por confirmar; vidrio y pasamanos como contexto de instalación.'
  },
  hrd1223: {
    src: '/assets/projects/hrd-1223/hrd-1223-tubo.glb?v=1-45-2', profile: 'hrd1223', kicker: 'Estudio interactivo · HRD 1223',
    title: 'HRD 1223 · Tubo y vidrio', number: 'HRD 1223 · Cuerpo tubular',
    heading: 'Cada brazo, cada punto de sujeción.',
    description: 'Explora el cuerpo tubular, los brazos ajustables y los discos que sujetan el vidrio. Acércate a la articulación o separa los componentes.',
    content: '45 piezas y elementos de contexto', detail: 'Ver brazo',
    aria: 'Reconstrucción visual del HRD 1223 de tubo circular con brazos ajustables y vidrio',
    caveat: 'Estudio reconstruido a partir de fotografías. Medidas, anclaje y detalles internos por confirmar; el vidrio y el pasamanos son contexto de instalación.'
  },
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
    content: '20 componentes y conjuntos', detail: 'Ver unión',
    aria: 'Modelo tridimensional interactivo del poste HRD 1518 con pasamanos y tres barras',
    caveat: 'Las barras y el pasamanos muestran el sistema instalado y no indican por sí solos el contenido comercial del kit.'
  },
  hrd1616: {
    src: '/assets/projects/hrd-1616/hrd-1616-esquina-7-cables.glb?v=1-63-0', profile: 'hrd1616', kicker: 'Solución interactiva 03',
    title: 'HRD 1616 · Poste cuadrado + cable', number: '03 / HRD 1616 · Cable de acero',
    heading: 'Una esquina completa, unión por unión.',
    description: 'Recorre los dos tramos, acércate al poste compartido y controla el despiece del sistema completo.',
    content: '93 piezas y conjuntos', detail: 'Ver esquina',
    aria: 'Modelo tridimensional interactivo del sistema HRD 1616 con postes cuadrados y cable de acero', caveat: ''
  },
  futbolito: {
    src: '/assets/projects/futbolito/futbolito-herraidea.glb', profile: 'futbolito', kicker: 'Proyecto interactivo 09',
    title: 'Futbolito Herraidea', number: 'Proyecto especial · Fabricación Herraidea',
    heading: 'Observa cómo cada parte forma el proyecto.',
    description: 'Cristal y acero. El juego visto desde otra perspectiva.',
    content: '190 piezas y conjuntos', detail: 'Ver costado',
    aria: 'Modelo tridimensional interactivo del Futbolito Herraidea',
    caveat: 'Modelo conceptual reconstruido a partir de fotografías. Las medidas y la secuencia de fabricación están por confirmar.'
  }
};

const prepareModel = (gltf, profileName) => {
  if (profileName === 'domo') gltf.scene.traverse(object => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    materials.forEach(material => {
      material.envMapIntensity = 1.2;
      if (material.transparent) { material.depthWrite = false; object.renderOrder = 2; }
    });
  });
  if (profileName === 'hrd1616') {
    let steel;
    gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      steel ||= materials.find(material => material?.name === 'Acero inoxidable');
    });
    if (steel) {
      const satin = steel.clone();
      satin.name = 'Acero inoxidable satinado';
      satin.color.setHex(0xd1d5d8);
      satin.metalness = .82;
      satin.roughness = .26;
      satin.envMapIntensity = 1.55;
      gltf.scene.traverse(object => {
        if (!object.isMesh) return;
        const replace = material => ['Negro', 'Acero inoxidable'].includes(material?.name) ? satin.clone() : material;
        object.material = Array.isArray(object.material) ? object.material.map(replace) : replace(object.material);
      });
    }
  }
  if (profileName === 'clips') {
    const glass = gltf.scene.getObjectByName('Cristal_central');
    if (glass) glass.scale.x *= (.96 - .0592) / .838;
  }

  if (profileName !== 'hrd1518') return gltf.animations;
  gltf.scene.updateMatrixWorld(true);
  [1, 2, 3].forEach((index) => {
    const pin = gltf.scene.getObjectByName(`Pin_intermedio_${index}`);
    const head = gltf.scene.getObjectByName(`Cabeza_pin_${index}`);
    if (pin && head) pin.attach(head);
  });
  return gltf.animations.map((clip) => new THREE.AnimationClip(
    clip.name,
    clip.duration,
    clip.tracks.filter((track) => !/^Cabeza_pin_[1-3]\./.test(track.name))
  ));
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
      if (entry.isIntersecting && (this.preview || this.hasAttribute('autostart'))) this.start();
    }, { rootMargin: '180px' });
    this.observer.observe(this);
  }

  disconnectedCallback() {
    this.observer?.disconnect();
    this.resizeObserver?.disconnect();
    cancelAnimationFrame(this.animationFrame);
    cancelAnimationFrame(this.tweenFrame);
    this.disposed = true;
    this.controls?.dispose();
    this.mixer?.stopAllAction();
    if (this.model) this.mixer?.uncacheRoot(this.model);
    this.disposeModel(this.model);
    this.scene?.environment?.dispose();
    this.renderer?.dispose();
  }

  disposeModel(model) {
    model?.traverse(object => {
      if (!object.isMesh) return;
      object.geometry.dispose();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach(material => material.dispose());
    });
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
      this.camera = new THREE.PerspectiveCamera(32, 1, .01, this.profile.far || 30);
      this.camera.position.fromArray(this.profile.camera);
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
      this.controls.target.fromArray(this.profile.target);
      this.controls.minDistance = this.profile.min;
      this.controls.maxDistance = this.profile.max || 9;
      this.controls.maxPolarAngle = Math.PI * .55;
      this.controls.enablePan = false;
      this.controls.enableDamping = true;
      this.controls.dampingFactor = .06;
      this.controls.autoRotate = this.preview && !reduceMotion.matches;
      this.controls.autoRotateSpeed = .55;

      const pmrem = new THREE.PMREMGenerator(this.renderer);
      const environment = new RoomEnvironment();
      this.scene.environment = pmrem.fromScene(environment, .04).texture;
      environment.dispose();
      pmrem.dispose();
      this.scene.add(new THREE.HemisphereLight(0xffffff, 0x6c7075, 1.15));
      const key = new THREE.DirectionalLight(0xffffff, 2.7);
      key.position.set(3, 5, 2);
      this.scene.add(key);
      const rim = new THREE.DirectionalLight(0xc9e7ff, 1.25);
      rim.position.set(-3, 2, -3);
      this.scene.add(rim);
      if (this.id === 'special-project-viewer') {
        this.renderer.toneMappingExposure = 1.18;
        const fill = new THREE.DirectionalLight(0xe4edff, 2);
        fill.position.set(0, 3, 6);
        this.scene.add(fill);
      }

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
      if (this.disposed) { this.disposeModel(gltf.scene); return; }
      this.model = gltf.scene;
      const animations = prepareModel(gltf, this.getAttribute('profile'));
      this.scene.add(this.model);
      this.mixer = new THREE.AnimationMixer(this.model);
      const clip = animations.find((item) => item.name === 'Despiece') || animations[0];
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
    if (this.disposed) return;
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
    const offset = this.baseCamera.clone().sub(this.baseTarget).multiplyScalar(aspect * preview * (this.getAttribute('profile') === 'domo' ? 1.42 : 1));
    this.controls.target.copy(this.baseTarget);
    this.camera.position.copy(this.baseTarget).add(offset);
    this.controls.minDistance = this.profile.min;
    this.controls.maxDistance = this.profile.max || 9;
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
    raisedTarget.y += (this.getAttribute('profile') === 'hrd1220' ? .06 : .3) * target;
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

  setDomeLayer(name, visible) {
    if (!this.ready || this.getAttribute('profile') !== 'domo') return;
    const prefixes = name === 'lona' ? ['lona_', 'ventanal_', 'ojo_de_buey', 'respiradero', 'chimenea_sombrero', 'chimenea_tapajuntas'] : ['terraza'];
    this.model.traverse(object => {
      if (object.isMesh && prefixes.some(prefix => object.name.startsWith(prefix))) object.visible = visible;
    });
    this.dispatchEvent(new CustomEvent('projectlayer', { bubbles: true, detail: { name, visible } }));
  }

  showDomeView(name) {
    if (!this.ready || this.getAttribute('profile') !== 'domo') return;
    const views = {
      exterior: { camera: [-5.6, 2.6, 13], target: [.4, 1.6, 0], layers: true },
      interior: { camera: [.2, 9.4, 7.6], target: [0, .5, -.1], layers: false },
      frente: { camera: [0, 2.2, 15.5], target: [0, 1.8, 0] },
      planta: { camera: [.01, 17, .6], target: [0, 0, 0] }
    };
    const view = views[name];
    if (!view) return;
    cancelAnimationFrame(this.tweenFrame);
    this.setAmount(0);
    this.corner = true;
    this.controls.target.fromArray(view.target);
    const offset = new THREE.Vector3().fromArray(view.camera).sub(this.controls.target);
    this.camera.position.copy(this.controls.target).add(offset.multiplyScalar(Math.max(1, 1.55 / this.camera.aspect) * (name === 'exterior' || name === 'frente' ? 1.42 : 1)));
    if (view.layers !== undefined) ['lona', 'terraza'].forEach(layer => this.setDomeLayer(layer, view.layers));
    this.controls.update();
  }

  showCorner() {
    if (!this.ready) return;
    if (this.getAttribute('profile') === 'domo') return this.showDomeView('interior');
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

const setActiveControl = (active) => {
  dialog?.querySelectorAll('.project-actions button').forEach((button) => {
    const pressed = Boolean(active) && button.matches(active);
    button.classList.toggle('active', pressed);
    button.setAttribute('aria-pressed', String(pressed));
  });
};

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
  setActiveControl('[data-project-assemble]');
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
dialog?.querySelector('[data-project-explode]')?.addEventListener('click', () => {
  setActiveControl('[data-project-explode]');
  viewer.animateTo(1);
});
dialog?.querySelector('[data-project-assemble]')?.addEventListener('click', () => {
  setActiveControl('[data-project-assemble]');
  viewer.animateTo(0);
});
dialog?.querySelector('[data-project-corner]')?.addEventListener('click', () => {
  setActiveControl('[data-project-corner]');
  viewer.showCorner();
});
range?.addEventListener('input', () => {
  cancelAnimationFrame(viewer.tweenFrame);
  setActiveControl(range.value === '0' ? '[data-project-assemble]' : range.value === '100' ? '[data-project-explode]' : '');
  viewer.setAmount(Number(range.value) / 100);
});

bindViewer();

// The Projects section shares the model engine and existing Liquid Glass controls.
const specialSection = document.querySelector('#proyectos');
let specialViewer = document.querySelector('#special-project-viewer');
const specialRange = document.querySelector('#special-project-range');
const specialOutput = document.querySelector('#special-project-range-value');
const specialStatus = document.querySelector('#special-project-status');
const specialButtons = [...document.querySelectorAll('.special-project-controls button')];
const selectSpecialControl = (selector) => specialButtons.forEach(button => {
  const active = Boolean(selector) && button.matches(selector);
  button.classList.toggle('active', active);
  button.setAttribute('aria-pressed', String(active));
});
const bindSpecialViewer = () => {
  specialViewer.addEventListener('projectready', () => {
    specialRange.disabled = false;
    specialButtons.forEach(button => { button.disabled = false; });
    specialSection.querySelectorAll('[data-dome-view], [data-dome-layer]').forEach(button => { button.disabled = false; });
    specialStatus.textContent = 'Modelo listo · gira, acerca y explora sus piezas.';
  });
  specialViewer.addEventListener('projectlayer', event => {
    const button = specialSection.querySelector(`[data-dome-layer="${event.detail.name}"]`);
    button.classList.toggle('active', event.detail.visible);
    button.setAttribute('aria-pressed', String(event.detail.visible));
  });
  specialViewer.addEventListener('projecterror', event => { specialStatus.textContent = event.detail.message; });
  specialViewer.addEventListener('projectprogress', event => {
    const value = event.detail.value;
    specialRange.value = value;
    specialRange.style.setProperty('--project-range', `${value}%`);
    specialOutput.value = `${value} %`;
  });
};
const selectSpecialProject = key => {
  if (!specialSection || !['riverack', 'futbolito', 'domo'].includes(key)) return;
  const project = projects[key];
  specialSection.querySelector('.dome-options').hidden = key !== 'domo';
  specialSection.querySelector('.dome-options').open = false;
  specialSection.querySelectorAll('[data-dome-layer]').forEach(button => {
    button.disabled = true;
    button.classList.add('active');
    button.setAttribute('aria-pressed', 'true');
  });
  specialSection.querySelectorAll('[data-dome-view]').forEach(button => { button.disabled = true; });
  specialSection.querySelectorAll('[data-special]').forEach(element => { element.textContent = project[element.dataset.special]; });
  specialSection.querySelectorAll('[data-special-project]').forEach(button => {
    const active = button.dataset.specialProject === key;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  specialRange.value = 0;
  specialRange.disabled = true;
  specialRange.style.setProperty('--project-range', '0%');
  specialOutput.value = '0 %';
  specialStatus.textContent = 'Preparando modelo 3D…';
  specialButtons.forEach(button => { button.disabled = true; });
  selectSpecialControl('[data-project-assemble]');
  const replacement = document.createElement('hrd-project-3d');
  replacement.id = 'special-project-viewer';
  replacement.setAttribute('autostart', '');
  replacement.setAttribute('src', project.src);
  replacement.setAttribute('profile', project.profile);
  replacement.setAttribute('role', 'img');
  replacement.setAttribute('aria-label', project.aria);
  specialViewer.replaceWith(replacement);
  specialViewer = replacement;
  bindSpecialViewer();
};
if (specialViewer) {
  bindSpecialViewer();
  specialSection.querySelectorAll('[data-special-project]').forEach(button => button.addEventListener('click', () => {
    if (button.getAttribute('aria-pressed') !== 'true') selectSpecialProject(button.dataset.specialProject);
  }));
  specialButtons.forEach(button => button.addEventListener('click', () => {
    const selector = button.hasAttribute('data-project-explode') ? '[data-project-explode]' : button.hasAttribute('data-project-assemble') ? '[data-project-assemble]' : '[data-project-corner]';
    selectSpecialControl(selector);
    if (button.hasAttribute('data-project-corner')) specialViewer.showCorner();
    else specialViewer.animateTo(button.hasAttribute('data-project-explode') ? 1 : 0);
  }));
  specialSection.querySelectorAll('[data-dome-view]').forEach(button => button.addEventListener('click', () => {
    specialViewer.showDomeView(button.dataset.domeView);
    selectSpecialControl('[data-project-assemble]');
  }));
  specialSection.querySelectorAll('[data-dome-layer]').forEach(button => button.addEventListener('click', () => {
    specialViewer.setDomeLayer(button.dataset.domeLayer, button.getAttribute('aria-pressed') !== 'true');
  }));
  specialRange.addEventListener('input' , () => {
    cancelAnimationFrame(specialViewer.tweenFrame);
    selectSpecialControl(specialRange.value === '0' ? '[data-project-assemble]' : specialRange.value === '100' ? '[data-project-explode]' : '');
    specialViewer.setAmount(Number(specialRange.value) / 100);
  });
}

const requestedProject = new URLSearchParams(location.search).get('proyecto');
if (requestedProject && projects[requestedProject]) {
  const requestedIndex = cards.findIndex(card => card.dataset.project === requestedProject);
  if (requestedIndex >= 0) setSlide(requestedIndex, 'auto');
  requestAnimationFrame(() => {
    if (['riverack', 'futbolito', 'domo'].includes(requestedProject)) {
      selectSpecialProject(requestedProject);
      specialSection.scrollIntoView({ behavior: 'instant' });
    } else openProject(requestedProject);
    const cleanUrl = new URL(location.href);
    cleanUrl.searchParams.delete('proyecto');
    history.replaceState({}, '', cleanUrl);
  });
}
