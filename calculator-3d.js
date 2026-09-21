import * as THREE from '/assets/vendor/three/three.module.js';
import { GLTFLoader } from '/assets/vendor/three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from '/assets/vendor/three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from '/assets/vendor/three/addons/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const systems = {
  hrd153x: {
    name: 'HRD 1533 / 1534 / 1535 · Poste con canales para vidrio', code: 'HRD 1533 / 1534 / 1535',
    src: '/assets/projects/hrd-153x/hrd-153x.glb?v=1-51-0',
    cornerSrc: '/assets/projects/hrd-153x/hrd-153x-esquina.glb?v=1-51-0', conceptual: true, channel: true
  },
  hrd1220: {
    name: 'HRD 1220 · Pinzas bajas y unión de cristales', code: 'HRD 1220',
    src: '/assets/projects/hrd-1220/hrd-1220.glb?v=1-47-0', conceptual: true, spigot: true
  },
  hrd1221: {
    name: 'HRD 1221 de tubo con soleras planas + vidrio', code: 'HRD 1221',
    src: '/assets/projects/hrd-1221/hrd-1221.glb?v=1-46-0', conceptual: true
  },
  hrd1223: {
    name: 'HRD 1223 de tubo + vidrio', code: 'HRD 1223',
    src: '/assets/projects/hrd-1223/hrd-1223-tubo.glb?v=1-45-2', conceptual: true
  },
  clips: {
    name: 'Postes con clips + vidrio', code: 'HRD 1525',
    src: '/assets/projects/clip-system/herraje-cristal.glb', sourceSpacing: .96,
    sourceGlassWidth: .838, clipInset: .0592,
    spanParts: new Set(['Cristal_central', 'Pasamanos_continuo'])
  },
  tubo: {
    name: 'Sistema de tubo de 1/2"', code: 'HRD 1518',
    src: '/assets/projects/hrd-1518/hrd-1518.glb', sourceSpacing: .84,
    cornerSrc: '/assets/projects/hrd-1518/hrd-1518-esquina-v1233.glb',
    spanParts: new Set(['Pasamanos_contexto', 'Barra_contexto_1', 'Barra_contexto_2', 'Barra_contexto_3'])
  },
  cable: {
    name: 'Poste cuadrado + cable de acero', code: 'HRD 1616',
    src: '/assets/projects/hrd-1616/hrd-1616-esquina.glb', sourceSpacing: 1.15,
    cornerSrc: '/assets/projects/hrd-1616/hrd-1616-esquina.glb', satin: true
  }
};
const loader = new GLTFLoader();
const sourceModels = new Map();

function bestDistribution(length) {
  const minSpaces = Math.max(1, Math.ceil(length / 1.4 - 1e-9));
  const maxSpaces = Math.max(1, Math.floor(length / 1.2 + 1e-9));
  const exact = minSpaces <= maxSpaces;
  const candidates = exact ? Array.from({ length: maxSpaces - minSpaces + 1 }, (_, index) => minSpaces + index) : [minSpaces];
  const spaces = candidates.reduce((best, candidate) =>
    Math.abs(length / candidate - 1.3) < Math.abs(length / best - 1.3) ? candidate : best
  , candidates[0]);
  return { spaces, spacing: length / spaces, exact };
}

function loadSource(config) {
  if (!sourceModels.has(config.src)) {
    sourceModels.set(config.src, new Promise((resolve, reject) => {
      loader.load(config.src, ({ scene }) => {
        if (config.satin) applySatinFinish(scene);
        resolve(scene);
      }, undefined, reject);
    }));
  }
  return sourceModels.get(config.src);
}

function applySatinFinish(scene) {
  let steel;
  scene.traverse(object => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    steel ||= materials.find(material => material?.name === 'Acero inoxidable');
  });
  const satin = steel?.clone() || new THREE.MeshStandardMaterial();
  satin.name = 'Acero inoxidable satinado';
  satin.color.setHex(0xd1d5d8);
  satin.metalness = .82;
  satin.roughness = .26;
  satin.envMapIntensity = 1.55;
  scene.traverse(object => {
    if (!object.isMesh) return;
    const replace = material => ['Negro', 'Acero inoxidable'].includes(material?.name) ? satin.clone() : material;
    object.material = Array.isArray(object.material) ? object.material.map(replace) : replace(object.material);
  });
}

function cloneMesh(source) {
  const copy = source.clone(true);
  copy.traverse(object => {
    if (!object.isMesh) return;
    object.castShadow = true;
    object.receiveShadow = true;
  });
  return copy;
}

function clipSpan(source, spacing, omitStart = false, omitEnd = false) {
  const span = new THREE.Group();
  const half = spacing / 2;
  source.children.forEach(part => {
    if ((omitStart && part.name.startsWith('izquierdo_')) || (omitEnd && part.name.startsWith('derecho_'))) return;
    const copy = cloneMesh(part);
    if (part.name.startsWith('izquierdo_')) copy.position.x += -half + .48;
    else if (part.name.startsWith('derecho_')) copy.position.x += half - .48;
    else if (part.name === 'Cristal_central') {
      copy.scale.x *= (spacing - systems.clips.clipInset) / systems.clips.sourceGlassWidth;
    } else if (part.name === 'Pasamanos_continuo') {
      const bounds = new THREE.Box3().setFromObject(part);
      const sourceMin = bounds.min.x;
      const sourceMax = bounds.max.x;
      const overhang = Math.max(0, (sourceMax - sourceMin - systems.clips.sourceSpacing) / 2);
      const desiredMin = -half - (omitStart ? 0 : overhang);
      const desiredMax = half + (omitEnd ? 0 : overhang);
      const fitted = new THREE.Group();
      copy.position.x -= sourceMin;
      fitted.add(copy);
      fitted.scale.x = (desiredMax - desiredMin) / (sourceMax - sourceMin);
      fitted.position.x = desiredMin;
      span.add(fitted);
      return;
    } else copy.scale.x *= spacing / systems.clips.sourceSpacing;
    span.add(copy);
  });
  return span;
}

function tubeSpan(source, spacing, omitStart = false, omitEnd = false) {
  const span = new THREE.Group();
  const config = systems.tubo;
  const postParts = source.children.filter(part => !config.spanParts.has(part.name));
  [-spacing / 2, spacing / 2].forEach((position, index) => {
    if ((index === 0 && omitStart) || (index === 1 && omitEnd)) return;
    postParts.forEach(part => {
      const copy = cloneMesh(part);
      copy.position.x += position;
      span.add(copy);
    });
  });
  source.children.filter(part => config.spanParts.has(part.name)).forEach(part => {
    const copy = cloneMesh(part);
    copy.scale.x *= spacing / config.sourceSpacing;
    span.add(copy);
  });
  return span;
}

function cableSpan(source, spacing, omitStart = false, omitEnd = false, side = 'A') {
  const span = new THREE.Group();
  const config = systems.cable;
  const axis = side === 'B' ? 'z' : 'x';
  source.children.forEach(part => {
    const isStart = part.name.startsWith('Esquina_') || part.name.includes(`_${side}_Esquina_`);
    const isEnd = part.name.startsWith(`Extremo_${side}_`) || part.name.includes(`_${side}_Extremo_`);
    const isContinuous = part.name.startsWith(`Cable_${side}_`) || part.name === `Pasamanos_${side}`;
    if ((!isStart && !isEnd && !isContinuous) || (omitStart && isStart) || (omitEnd && isEnd)) return;
    if (isContinuous) {
      const bounds = new THREE.Box3().setFromObject(part);
      const sourceMin = bounds.min[axis];
      const sourceMax = bounds.max[axis];
      const desiredMin = part.name === `Pasamanos_${side}` && omitStart ? 0 : sourceMin;
      const desiredMax = part.name === `Pasamanos_${side}` && omitEnd
        ? spacing
        : sourceMax + spacing - config.sourceSpacing;
      const fitted = new THREE.Group();
      const copy = cloneMesh(part);
      copy.position[axis] -= sourceMin;
      fitted.add(copy);
      fitted.scale[axis] = (desiredMax - desiredMin) / (sourceMax - sourceMin);
      fitted.position[axis] = desiredMin;
      span.add(fitted);
      return;
    }
    const copy = cloneMesh(part);
    if (isEnd) copy.position[axis] += spacing - config.sourceSpacing;
    span.add(copy);
  });
  span.children.forEach(part => { part.position[axis] -= spacing / 2; });
  return span;
}

// The source is one centered post. Keep hardware dimensions fixed; only fit glass/rail.
function glassPost(source, sides = ['left', 'right'], system = 'hrd1223', includeBody = true) {
  const post = new THREE.Group();
  source.children.forEach(part => {
    if (part.userData.role === 'crossbar' && sides.length) {
      const strip = cloneMesh(part);
      if (sides.length === 1) {
        strip.scale.x *= .5;
        strip.position.x += sides[0] === 'left' ? -.0575 : .0575;
      }
      post.add(strip);
    } else if ((includeBody && part.userData.role === 'post') ||
      (part.userData.role === 'barfix' && sides.length) ||
      (['arm', 'lining'].includes(part.userData.role) && sides.includes(part.userData.side))) {
      post.add(cloneMesh(part));
    }
  });
  post.name = includeBody ? `${system.toUpperCase()}_Poste` : `${system.toUpperCase()}_Brazos`;
  return post;
}

function glassSpan(source, spacing, makeStart, makeEnd, terminalStart, system) {
  const span = new THREE.Group();
  if (makeStart) {
    const post = glassPost(source, terminalStart ? ['right'] : ['left', 'right'], system);
    post.position.x = -spacing / 2;
    span.add(post);
  }
  if (makeEnd) {
    const post = glassPost(source, ['left'], system);
    post.position.x = spacing / 2;
    span.add(post);
  }
  const glass = cloneMesh(source.getObjectByName('Contexto_vidrio_right'));
  glass.position.x = 0;
  glass.scale.x *= Math.max(.01, spacing - (system === 'hrd153x' ? .034 : .05)) / .605;
  glass.name = `${system.toUpperCase()}_Vidrio`;
  span.add(glass);
  const rail = cloneMesh(source.getObjectByName('Contexto_pasamanos'));
  rail.scale.x *= spacing / 1.32;
  rail.name = `${system.toUpperCase()}_Pasamanos`;
  span.add(rail);
  return span;
}

// HRD 1220 uses two independent floor clamps per pane; no full-height post or rail.
function spigotSpan(source, spacing, joinPrevious) {
  const span = new THREE.Group();
  for (const x of [-spacing / 4, spacing / 4]) {
    const support = new THREE.Group();
    support.name = 'HRD1220_Pinza';
    source.children.filter(part => part.userData.role === 'support' && part.userData.side === '1').forEach(part => {
      const copy = cloneMesh(part);
      copy.position.x += .98;
      support.add(copy);
    });
    support.position.x = x;
    span.add(support);
  }
  const glass = cloneMesh(source.getObjectByName('Cristal_right'));
  glass.position.x = 0;
  glass.scale.x *= Math.max(.01, spacing - .01) / 1.30;
  glass.name = 'HRD1220_Cristal';
  span.add(glass);
  if (joinPrevious) {
    const connector = new THREE.Group();
    connector.name = 'HRD1220_Union_superior';
    source.children.filter(part => part.userData.role === 'connector').forEach(part => connector.add(cloneMesh(part)));
    connector.position.x = -spacing / 2;
    span.add(connector);
  }
  return span;
}

function centeredEndpoint(source, prefix, offset) {
  const group = new THREE.Group();
  source.children.filter(part => part.name.startsWith(prefix)).forEach(part => {
    const copy = cloneMesh(part);
    copy.position.x += offset;
    group.add(copy);
  });
  return group;
}

function sharedCorner(system, source, cornerSource, position, junctionIndex, incomingAngle, outgoingAngle) {
  const corner = new THREE.Group();
  if (system === 'hrd153x') {
    const body = glassPost(cornerSource, ['left', 'right'], system);
    body.rotation.y = -incomingAngle;
    corner.add(body);
  } else if (system === 'hrd1223' || system === 'hrd1221') {
    const body = glassPost(source, [], system);
    body.rotation.y = -incomingAngle;
    corner.add(body);
    [['left', incomingAngle], ['right', outgoingAngle]].forEach(([side, angle]) => {
      const arms = glassPost(source, [side], system, false);
      arms.rotation.y = -angle;
      corner.add(arms);
    });
  } else if (system === 'clips') {
    const incoming = centeredEndpoint(source, 'derecho_', -.48);
    incoming.rotation.y = -incomingAngle;
    const outgoing = centeredEndpoint(source, 'izquierdo_', .48);
    outgoing.rotation.y = -outgoingAngle;
    corner.add(incoming, outgoing);
  } else {
    const matchesCorner = part => system === 'tubo'
      ? part.name.startsWith('Esquina_') || part.name.startsWith('Union_90_')
      : part.name.startsWith('Esquina_') || part.name.includes('_Esquina_');
    cornerSource.children.filter(matchesCorner).forEach(part => corner.add(cloneMesh(part)));
    corner.rotation.y = Math.PI + junctionIndex * Math.PI / 2;
  }
  corner.position.copy(position);
  corner.name = `${systems[system].code}_Esquina_${junctionIndex + 1}`;
  return corner;
}

class PostCalculator3D extends HTMLElement {
  connectedCallback() {
    this.innerHTML = '<span class="calculator-loading">Preparando modelo 3D real…</span>';
    this.pending = { segments: [{ length: 5.3, spaces: 4 }], system: 'clips' };
    this.loadRequest = 0;
    this.observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        this.start();
        this.observer.disconnect();
      }
    }, { rootMargin: '180px' });
    this.observer.observe(this);
  }

  setLayout(segments, system) {
    this.pending = { segments, system: systems[system] ? system : 'clips' };
    if (this.started) this.rebuild();
  }

  start() {
    if (this.started) return;
    this.started = true;
    this.innerHTML = '';
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(34, 1, .1, 100);
    this.camera.position.set(4.8, 3.5, 5.5);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.8));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.append(this.renderer.domElement);

    const environment = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(environment, .04).texture;
    environment.dispose();
    pmrem.dispose();
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xb7bec4, 1.4));
    const key = new THREE.DirectionalLight(0xffffff, 3.6);
    key.position.set(4, 7, 5);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    this.scene.add(key);
    const red = new THREE.PointLight(0xe3212c, 7, 8);
    red.position.set(-3, 1.2, 2);
    this.scene.add(red);

    this.floor = new THREE.Mesh(new THREE.CircleGeometry(5.8, 64), new THREE.MeshStandardMaterial({ color: 0xe9edef, roughness: .86, metalness: .04 }));
    this.floor.rotation.x = -Math.PI / 2;
    this.floor.position.y = -.09;
    this.floor.receiveShadow = true;
    this.scene.add(this.floor);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.enablePan = false;
    this.controls.minDistance = 3.2;
    this.controls.maxDistance = 10;
    this.controls.maxPolarAngle = Math.PI * .49;
    this.controls.target.set(0, .5, 0);
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(this);
    this.rebuild();
    this.resize();
    this.animate();
  }

  async rebuild() {
    const request = ++this.loadRequest;
    const { segments, system } = this.pending;
    const config = systems[system];
    this.setAttribute('data-loading', 'true');
    try {
      const source = await loadSource(config);
      const cornerSource = config.cornerSrc && segments.length > 1
        ? await loadSource({ src: config.cornerSrc, satin: config.satin })
        : source;
      if (request !== this.loadRequest || !this.isConnected) return;
      if (this.model) this.scene.remove(this.model);

      const model = new THREE.Group();
      const directions = [[1, 0], [0, -1], [-1, 0], [0, 1]];
      let cursor = new THREE.Vector3();
      segments.forEach((segment, segmentIndex) => {
        const [dx, dz] = directions[segmentIndex % directions.length];
        const end = new THREE.Vector3(cursor.x + segment.length * dx, 0, cursor.z + segment.length * dz);
        const angle = Math.atan2(dz, dx);
        for (let index = 0; index < segment.spaces; index += 1) {
          const startPoint = cursor.clone().lerp(end, index / segment.spaces);
          const endPoint = cursor.clone().lerp(end, (index + 1) / segment.spaces);
          const spacing = startPoint.distanceTo(endPoint);
          const omitStart = segmentIndex > 0 && index === 0;
          const omitEnd = segmentIndex < segments.length - 1 && index === segment.spaces - 1;
          const cableSide = segmentIndex === 1 ? 'B' : 'A';
          const span = system === 'hrd1220'
            ? spigotSpan(source, spacing, index > 0)
            : (system === 'hrd1223' || system === 'hrd1221' || system === 'hrd153x')
            ? glassSpan(source, spacing, !omitStart,
                segmentIndex === segments.length - 1 && index === segment.spaces - 1,
                segmentIndex === 0 && index === 0, system)
            : system === 'clips'
            ? clipSpan(source, spacing, omitStart, omitEnd)
            : system === 'tubo'
              ? tubeSpan(source, spacing, omitStart, omitEnd)
              : cableSpan(source, spacing, omitStart, omitEnd, cableSide);
          span.rotation.y = system === 'cable' && cableSide === 'B' ? Math.PI / 2 - angle : -angle;
          span.position.copy(startPoint).add(endPoint).multiplyScalar(.5);
          model.add(span);
        }
        cursor.copy(end);
        if (segmentIndex < segments.length - 1 && system !== 'hrd1220') {
          const [nextDx, nextDz] = directions[(segmentIndex + 1) % directions.length];
          model.add(sharedCorner(
            system, source, cornerSource, cursor, segmentIndex,
            angle, Math.atan2(nextDz, nextDx)
          ));
        }
      });

      const totalLength = segments.reduce((sum, segment) => sum + segment.length, 0);
      const displayScale = Math.min(1, 5.15 / Math.max(4, totalLength));
      model.scale.setScalar(displayScale);
      const center = new THREE.Box3().setFromObject(model).getCenter(new THREE.Vector3());
      model.position.set(-center.x, 0, -center.z);
      this.model = model;
      this.scene.add(model);
      this.targetScale = displayScale;
      if (!reduceMotion.matches) model.scale.setScalar(.001);
      this.enterStart = performance.now();
      this.setAttribute('aria-label', `${config.conceptual ? 'Reconstrucción visual' : 'Modelo 3D real'} de ${config.name}, distribuido en ${segments.reduce((sum, segment) => sum + segment.spaces, 0)} espacios`);
      this.removeAttribute('data-loading');
      this.removeAttribute('data-error');
    } catch (error) {
      console.error(error);
      this.removeAttribute('data-loading');
      this.setAttribute('data-error', 'true');
    }
  }

  resize() {
    if (!this.renderer) return;
    const width = this.clientWidth || 1;
    const height = this.clientHeight || 1;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  animate = time => {
    if (!this.isConnected) return;
    this.frame = requestAnimationFrame(this.animate);
    if (this.model && !reduceMotion.matches && this.targetScale) {
      const progress = Math.min(1, Math.max(0, (time - this.enterStart) / 620));
      const eased = 1 - Math.pow(1 - progress, 3);
      this.model.scale.setScalar(Math.max(.001, this.targetScale * eased));
    }
    this.controls?.update();
    this.renderer?.render(this.scene, this.camera);
  };

  disconnectedCallback() {
    cancelAnimationFrame(this.frame);
    this.observer?.disconnect();
    this.resizeObserver?.disconnect();
    this.controls?.dispose();
    this.renderer?.dispose();
  }
}

customElements.define('herraidea-post-calculator-3d', PostCalculator3D);

const form = document.querySelector('#post-calculator');
if (form) {
  const segmentsRoot = document.querySelector('#calculator-segments');
  const addButton = document.querySelector('#calculator-add-segment');
  const systemSelect = document.querySelector('#calculator-system');
  const model = document.querySelector('#calculator-model');
  const stepCount = document.querySelector('#calculator-step-count');
  const postOutput = document.querySelector('#calculator-posts');
  const postNote = document.querySelector('#calculator-posts-note');
  const spacesOutput = document.querySelector('#calculator-spaces');
  const metersOutput = document.querySelector('#calculator-meters');
  const breakdown = document.querySelector('#calculator-breakdown');
  const status = document.querySelector('#calculator-status');
  const modelLabel = document.querySelector('#calculator-model-label');
  const whatsapp = document.querySelector('#calculator-whatsapp');
  const shareButton = document.querySelector('#calculator-share');
  let lengths = [5.3];
  const query = new URLSearchParams(location.search);
  const requestedSystem = query.get('sistema');
  const systemAliases = { hrd1525: 'clips', hrd1518: 'tubo', hrd1616: 'cable', soleras: 'hrd1223' };
  const initialSystem = systems[requestedSystem] ? requestedSystem : systemAliases[requestedSystem];
  const requestedLengths = String(query.get('tramos') || '').split(',').slice(0, 8)
    .map(value => Number(value)).filter(value => Number.isFinite(value) && value >= .2 && value <= 100);
  if (initialSystem) systemSelect.value = initialSystem;
  if (requestedLengths.length) lengths = requestedLengths;

  function configurationUrl() {
    const url = new URL(location.href);
    url.pathname = '/';
    url.search = `sistema=${encodeURIComponent(systemSelect.value)}&tramos=${lengths.map(length => length.toFixed(2)).join(',')}`;
    url.hash = 'calculadora';
    return url;
  }

  function syncConfigurationUrl() {
    const url = configurationUrl();
    history.replaceState(history.state, '', url);
    return url.href;
  }

  if (initialSystem || requestedLengths.length) syncConfigurationUrl();

  function renderInputs() {
    segmentsRoot.innerHTML = lengths.map((length, index) => `
      <div class="calculator-segment">
        <label for="calculator-length-${index}"><span>Tramo ${String(index + 1).padStart(2, '0')}</span><span class="calculator-input-wrap"><input id="calculator-length-${index}" data-segment-index="${index}" type="number" inputmode="decimal" min="0.20" max="100" step="0.01" value="${length.toFixed(2)}" aria-label="Metros del tramo ${index + 1}"><b>m</b></span></label>
        ${index ? `<button type="button" data-remove-segment="${index}" aria-label="Quitar tramo ${index + 1}">×</button>` : ''}
      </div>`).join('');
    addButton.disabled = lengths.length >= 8;
    stepCount.textContent = `${String(lengths.length).padStart(2, '0')} ${lengths.length === 1 ? 'tramo' : 'tramos'}`;
  }

  function update() {
    const distributions = lengths.map(length => ({ length, ...bestDistribution(length) }));
    const totalSpaces = distributions.reduce((sum, item) => sum + item.spaces, 0);
    const system = systems[systemSelect.value] || systems.clips;
    const totalPosts = system.spigot ? totalSpaces * 2 : totalSpaces + 1;
    const unions = totalSpaces - lengths.length;
    const totalMeters = lengths.reduce((sum, length) => sum + length, 0);
    const corners = Math.max(0, lengths.length - 1);
    const warnings = distributions.filter(item => !item.exact).length;
    document.querySelector('#calculator-heading-copy').textContent = system.spigot ? 'Agrega los tramos de tu proyecto. La vista propone cristales con dos pinzas al piso y una unión circular superior por junta recta; sus medidas y anclajes requieren validación.' : 'Agrega los tramos conectados de tu proyecto. La herramienta distribuye los postes entre 1.20 y 1.40 m y comparte el poste donde dos tramos forman una esquina.';
    postOutput.textContent = totalPosts;
    spacesOutput.textContent = totalSpaces;
    metersOutput.textContent = totalMeters.toFixed(2);
    document.querySelector('#calculator-count-label').textContent = system.spigot ? 'Pinzas estimadas' : 'Postes estimados';
    document.querySelector('#calculator-spaces-label').textContent = system.spigot ? 'Cristales' : 'Espacios';
    document.querySelector('#calculator-rule-text').textContent = system.spigot ? 'Dos pinzas por cristal en esta propuesta. Las esquinas mantienen apoyos independientes; su unión superior requiere otra pieza por confirmar.' : 'Cada tramo nuevo comparte con el anterior el poste de la esquina. Máximo 8 tramos en esta vista.';
    postNote.textContent = system.spigot ? `${unions} ${unions === 1 ? 'unión circular superior' : 'uniones circulares superiores'} en juntas rectas` : corners ? `incluye ${corners} ${corners === 1 ? 'poste compartido en esquina' : 'postes compartidos en esquinas'}` : 'para 1 tramo recto';
    breakdown.innerHTML = distributions.map((item, index) => `<li><span>Tramo ${String(index + 1).padStart(2, '0')} · ${item.length.toFixed(2)} m</span><strong>${item.spaces} ${system.spigot ? 'cristales' : 'espacios'} de ${(system.spigot ? item.spacing - .01 : item.spacing).toFixed(2)} m</strong></li>`).join('');
    status.classList.toggle('warning', warnings > 0);
    status.textContent = warnings
      ? `${warnings === 1 ? 'Un tramo requiere' : `${warnings} tramos requieren`} revisión: se respetó el máximo de 1.40 m, pero la separación quedó por debajo de 1.20 m.`
      : 'Todos los tramos quedan dentro del rango de separación de 1.20 a 1.40 m.';
    const modelNote = document.querySelector('#calculator-model-note');
    if (modelNote) {
      modelNote.textContent = system.conceptual
        ? `${system.code}: reconstrucción según CAD y fotografías. Medidas y solución de esquina por confirmar; el rango de separación es orientativo y requiere validación para este sistema.`
        : 'La vista utiliza las piezas 3D recibidas para esta solución.';
    }
    if (system.spigot) {
      status.classList.add('warning');
      status.textContent = 'Distribución visual: dos pinzas por cristal y una unión circular en cada junta recta. Anchos de cristal, anclajes y uniones de esquina por validar.';
      modelNote.textContent = 'Pinza de 185 mm, base 101.6 × 101.6 mm y vidrio de 10–12 mm según CAD. El conector circular superior es una reconstrucción visual.';
    }
    if (system.channel) modelNote.textContent = 'Incluye vinil de empaque para vidrio de 10 mm de espesor. Modelo visual de la familia HRD 1533 / 1534 / 1535; medidas del perfil y distribución por validar.';
    modelLabel.textContent = `${system.code} · ${system.spigot ? 'pinzas y unión superior' : system.channel ? 'vidrio de 10 mm + vinil' : system.conceptual ? 'estudio de tubo' : 'modelo 3D real'}`;
    model.setLayout(distributions, systemSelect.value);
    const lines = distributions.map((item, index) => `Tramo ${index + 1}: ${item.length.toFixed(2)} m, ${item.spaces} ${system.spigot ? 'cristales' : 'espacios'} de ${(system.spigot ? item.spacing - .01 : item.spacing).toFixed(2)} m.`).join('\n');
    const quantity = system.spigot ? `${totalPosts} pinzas estimadas y ${unions} uniones superiores en juntas rectas${corners ? ', esquinas pendientes de validar' : ''}` : `${totalPosts} postes estimados${corners ? `, considerando ${corners} ${corners === 1 ? 'esquina compartida' : 'esquinas compartidas'}` : ''}`;
    const message = `Hola, quiero revisar esta estimación para ${system.name}${system.conceptual ? ' (estudio visual, medidas y esquinas pendientes de validar)' : ''}:\n${lines}${system.channel ? '\nIncluye vinil de empaque para vidrio de 10 mm de espesor.' : ''}\nTotal: ${totalMeters.toFixed(2)} m, ${quantity}.\nConfiguración: ${configurationUrl().href}`;
    whatsapp.href = `https://wa.me/524772561695?text=${encodeURIComponent(message)}`;
  }

  segmentsRoot.addEventListener('input', event => {
    const input = event.target.closest('[data-segment-index]');
    if (!input) return;
    const index = Number(input.dataset.segmentIndex);
    const value = Number(input.value);
    if (Number.isFinite(value) && value >= .2) {
      lengths[index] = Math.min(100, value);
      update();
      syncConfigurationUrl();
    }
  });
  segmentsRoot.addEventListener('click', event => {
    const button = event.target.closest('[data-remove-segment]');
    if (!button) return;
    lengths.splice(Number(button.dataset.removeSegment), 1);
    renderInputs();
    update();
    syncConfigurationUrl();
  });
  addButton.addEventListener('click', () => {
    if (lengths.length >= 8) return;
    lengths.push(3.9);
    renderInputs();
    update();
    syncConfigurationUrl();
    // `:last-of-type` devolvía el primer tramo, no el recién agregado, y el foco
    // arrastraba la página hasta él. Ahora se enfoca el nuevo sin mover el scroll.
    const nuevoTramo = segmentsRoot.querySelector(`[data-segment-index="${lengths.length - 1}"]`);
    nuevoTramo?.focus({ preventScroll: true });
    nuevoTramo?.scrollIntoView({ block: 'nearest' });
  });
  systemSelect.addEventListener('change', () => {
    update();
    syncConfigurationUrl();
  });
  shareButton?.addEventListener('click', async () => {
    const url = syncConfigurationUrl();
    try {
      await navigator.clipboard.writeText(url);
    } catch {
      const field = document.createElement('textarea');
      field.value = url;
      field.setAttribute('readonly', '');
      field.style.position = 'fixed';
      field.style.opacity = '0';
      document.body.append(field);
      field.select();
      document.execCommand('copy');
      field.remove();
    }
    shareButton.classList.add('copied');
    shareButton.firstChild.textContent = 'Enlace copiado ';
    setTimeout(() => {
      shareButton.classList.remove('copied');
      shareButton.firstChild.textContent = 'Copiar enlace de esta configuración ';
    }, 2200);
  });
  form.addEventListener('submit', event => event.preventDefault());
  renderInputs();
  update();
}
