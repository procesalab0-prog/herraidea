import * as THREE from 'https://esm.sh/three@0.160.0';
import { GLTFLoader } from 'https://esm.sh/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'https://esm.sh/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const systems = {
  clips: {
    name: 'Postes con clips + vidrio', code: 'HRD 1525',
    src: '/assets/projects/clip-system/herraje-cristal.glb', sourceSpacing: .96,
    sourceGlassWidth: .838, clipInset: .0592,
    spanParts: new Set(['Cristal_central', 'Pasamanos_continuo'])
  },
  tubo: {
    name: 'Sistema de tubo de 1/2"', code: 'HRD 1518',
    src: '/assets/projects/hrd-1518/hrd-1518.glb', sourceSpacing: .84,
    cornerSrc: '/assets/projects/hrd-1518/hrd-1518-esquina.glb',
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
  const minSpaces = Math.max(1, Math.ceil(length / 1.4));
  const maxSpaces = Math.max(1, Math.floor(length / 1.2));
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

function cableSpan(source, spacing, omitStart = false, omitEnd = false) {
  const span = new THREE.Group();
  const config = systems.cable;
  source.children.forEach(part => {
    const isStart = part.name.startsWith('Esquina_') || /_A_Esquina_/.test(part.name);
    const isEnd = part.name.startsWith('Extremo_A_') || /_A_Extremo_/.test(part.name);
    const isContinuous = part.name.startsWith('Cable_A_') || part.name === 'Pasamanos_A';
    if ((!isStart && !isEnd && !isContinuous) || (omitStart && isStart) || (omitEnd && isEnd)) return;
    const copy = cloneMesh(part);
    if (isEnd) copy.position.x += spacing - config.sourceSpacing;
    if (isContinuous) {
      const bounds = new THREE.Box3().setFromObject(part);
      const sourceMin = bounds.min.x;
      const sourceMax = bounds.max.x;
      const desiredMin = part.name === 'Pasamanos_A' && omitStart ? 0 : sourceMin;
      const desiredMax = part.name === 'Pasamanos_A' && omitEnd
        ? spacing
        : sourceMax + spacing - config.sourceSpacing;
      const scale = (desiredMax - desiredMin) / (sourceMax - sourceMin);
      copy.scale.x *= scale;
      copy.position.x += desiredMin - sourceMin * scale;
    }
    span.add(copy);
  });
  span.children.forEach(part => { part.position.x -= spacing / 2; });
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
  if (system === 'clips') {
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
      const cornerSource = config.cornerSrc
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
          const span = system === 'clips'
            ? clipSpan(source, spacing, omitStart, omitEnd)
            : system === 'tubo'
              ? tubeSpan(source, spacing, omitStart, omitEnd)
              : cableSpan(source, spacing, omitStart, omitEnd);
          span.rotation.y = -angle;
          span.position.copy(startPoint).add(endPoint).multiplyScalar(.5);
          model.add(span);
        }
        cursor.copy(end);
        if (segmentIndex < segments.length - 1) {
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
      this.setAttribute('aria-label', `Modelo 3D real de ${config.name}, distribuido en ${segments.reduce((sum, segment) => sum + segment.spaces, 0)} espacios`);
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
  let lengths = [5.3];

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
    const totalPosts = totalSpaces + 1;
    const totalMeters = lengths.reduce((sum, length) => sum + length, 0);
    const corners = Math.max(0, lengths.length - 1);
    const warnings = distributions.filter(item => !item.exact).length;
    const system = systems[systemSelect.value] || systems.clips;
    postOutput.textContent = totalPosts;
    spacesOutput.textContent = totalSpaces;
    metersOutput.textContent = totalMeters.toFixed(2);
    postNote.textContent = corners ? `incluye ${corners} ${corners === 1 ? 'poste compartido en esquina' : 'postes compartidos en esquinas'}` : 'para 1 tramo recto';
    breakdown.innerHTML = distributions.map((item, index) => `<li><span>Tramo ${String(index + 1).padStart(2, '0')} · ${item.length.toFixed(2)} m</span><strong>${item.spaces} espacios de ${item.spacing.toFixed(2)} m</strong></li>`).join('');
    status.classList.toggle('warning', warnings > 0);
    status.textContent = warnings
      ? `${warnings === 1 ? 'Un tramo requiere' : `${warnings} tramos requieren`} revisión: se respetó el máximo de 1.40 m, pero la separación quedó por debajo de 1.20 m.`
      : 'Todos los tramos quedan dentro del rango de separación de 1.20 a 1.40 m.';
    modelLabel.textContent = `${system.code} · modelo 3D real`;
    model.setLayout(distributions, systemSelect.value);
    const lines = distributions.map((item, index) => `Tramo ${index + 1}: ${item.length.toFixed(2)} m, ${item.spaces} espacios de ${item.spacing.toFixed(2)} m.`).join('\n');
    const message = `Hola, quiero revisar esta estimación para ${system.name}:\n${lines}\nTotal: ${totalMeters.toFixed(2)} m, ${totalPosts} postes estimados${corners ? `, considerando ${corners} ${corners === 1 ? 'esquina compartida' : 'esquinas compartidas'}` : ''}.`;
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
    }
  });
  segmentsRoot.addEventListener('click', event => {
    const button = event.target.closest('[data-remove-segment]');
    if (!button) return;
    lengths.splice(Number(button.dataset.removeSegment), 1);
    renderInputs();
    update();
  });
  addButton.addEventListener('click', () => {
    if (lengths.length >= 8) return;
    lengths.push(3.9);
    renderInputs();
    update();
    segmentsRoot.querySelector('[data-segment-index]:last-of-type')?.focus();
  });
  systemSelect.addEventListener('change', update);
  form.addEventListener('submit', event => event.preventDefault());
  renderInputs();
  update();
}
