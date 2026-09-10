import * as THREE from 'https://esm.sh/three@0.160.0';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'https://esm.sh/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const systemNames = {
  clips: 'Postes con clips + vidrio',
  tubo: 'Sistema de tubo de 1/2"',
  cable: 'Sistema de cable de acero',
  presion: 'Sistema de vidrio a presión',
  solera: 'Postes de solera'
};

function bestDistribution(length) {
  const minSpaces = Math.max(1, Math.ceil(length / 1.4));
  const maxSpaces = Math.max(1, Math.floor(length / 1.2));
  const exact = minSpaces <= maxSpaces;
  const candidates = exact
    ? Array.from({ length: maxSpaces - minSpaces + 1 }, (_, index) => minSpaces + index)
    : [minSpaces];
  const spaces = candidates.reduce((best, candidate) =>
    Math.abs(length / candidate - 1.3) < Math.abs(length / best - 1.3) ? candidate : best
  , candidates[0]);
  return { spaces, spacing: length / spaces, exact };
}

function cylinderBetween(start, end, radius, material) {
  const direction = new THREE.Vector3().subVectors(end, start);
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, direction.length(), 18), material);
  mesh.position.copy(start).add(end).multiplyScalar(.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());
  return mesh;
}

class PostCalculator3D extends HTMLElement {
  connectedCallback() {
    this.innerHTML = '<span class="calculator-loading">Preparando vista 3D…</span>';
    this.pending = { segments: [{ length: 5.3, spaces: 4 }], system: 'clips' };
    this.observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        this.start();
        this.observer.disconnect();
      }
    }, { rootMargin: '180px' });
    this.observer.observe(this);
  }

  setLayout(segments, system) {
    this.pending = { segments, system };
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

    this.floor = new THREE.Mesh(
      new THREE.CircleGeometry(5.8, 64),
      new THREE.MeshStandardMaterial({ color: 0xe9edef, roughness: .86, metalness: .04 })
    );
    this.floor.rotation.x = -Math.PI / 2;
    this.floor.position.y = -.015;
    this.floor.receiveShadow = true;
    this.scene.add(this.floor);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.enablePan = false;
    this.controls.minDistance = 3.2;
    this.controls.maxDistance = 9;
    this.controls.maxPolarAngle = Math.PI * .49;
    this.controls.target.set(0, .55, 0);
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(this);
    this.rebuild();
    this.resize();
    this.animate();
  }

  rebuild() {
    if (this.model) {
      this.scene.remove(this.model);
      this.model.traverse(object => {
        object.geometry?.dispose();
        if (Array.isArray(object.material)) object.material.forEach(material => material.dispose());
        else object.material?.dispose();
      });
    }

    const { segments, system } = this.pending;
    const model = new THREE.Group();
    this.model = model;
    this.scene.add(model);
    const steel = new THREE.MeshStandardMaterial({ color: 0xbec4c8, metalness: .92, roughness: .23 });
    const darkSteel = new THREE.MeshStandardMaterial({ color: 0x586067, metalness: .82, roughness: .3 });
    const glass = new THREE.MeshPhysicalMaterial({ color: 0xaedcec, transmission: .84, transparent: true, opacity: .34, roughness: .08, metalness: 0, side: THREE.DoubleSide, depthWrite: false });
    const cable = new THREE.MeshStandardMaterial({ color: 0x242a2e, metalness: .86, roughness: .28 });
    const accent = new THREE.MeshStandardMaterial({ color: 0xe3212c, metalness: .12, roughness: .48 });
    const directions = [[1, 0], [0, -1], [-1, 0], [0, 1]];
    const totalLength = segments.reduce((sum, segment) => sum + segment.length, 0);
    const scale = Math.min(1, 5.25 / Math.max(4, totalLength));
    let cursor = new THREE.Vector3(0, 0, 0);
    let sequence = 0;

    const addAnimated = object => {
      object.userData.delay = sequence++ * 20;
      object.userData.targetScale = object.scale.clone();
      if (!reduceMotion.matches) object.scale.multiplyScalar(.001);
      model.add(object);
    };
    const addPost = (point, corner = false) => {
      const geometry = system === 'solera' ? new THREE.BoxGeometry(.1, 1.02, .05) : new THREE.CylinderGeometry(.055, .055, 1.02, 22);
      const post = new THREE.Mesh(geometry, steel);
      post.position.set(point.x, .51, point.z);
      post.castShadow = true;
      addAnimated(post);
      const base = new THREE.Mesh(new THREE.CylinderGeometry(.09, .1, .035, 24), steel);
      base.position.set(point.x, .018, point.z);
      base.castShadow = true;
      addAnimated(base);
      if (corner) {
        const ring = new THREE.Mesh(new THREE.TorusGeometry(.13, .014, 10, 32), accent);
        ring.rotation.x = Math.PI / 2;
        ring.position.set(point.x, .04, point.z);
        addAnimated(ring);
      }
    };

    segments.forEach((segment, segmentIndex) => {
      const direction = directions[segmentIndex % directions.length];
      const start = cursor.clone();
      const end = new THREE.Vector3(start.x + segment.length * scale * direction[0], 0, start.z + segment.length * scale * direction[1]);
      const points = Array.from({ length: segment.spaces + 1 }, (_, index) => start.clone().lerp(end, index / segment.spaces));
      points.forEach((point, index) => {
        if (segmentIndex === 0 || index > 0) addPost(point, segmentIndex > 0 && index === 0);
      });
      if (segmentIndex > 0) {
        const ring = new THREE.Mesh(new THREE.TorusGeometry(.13, .014, 10, 32), accent);
        ring.rotation.x = Math.PI / 2;
        ring.position.set(start.x, .04, start.z);
        addAnimated(ring);
      }

      points.slice(0, -1).forEach((point, index) => {
        const next = points[index + 1];
        const angle = Math.atan2(next.z - point.z, next.x - point.x);
        const length = point.distanceTo(next);
        const midpoint = point.clone().add(next).multiplyScalar(.5);
        const topRail = cylinderBetween(new THREE.Vector3(point.x, 1.08, point.z), new THREE.Vector3(next.x, 1.08, next.z), .045, steel);
        topRail.castShadow = true;
        addAnimated(topRail);

        if (system === 'clips' || system === 'presion') {
          const panel = new THREE.Mesh(new THREE.BoxGeometry(length - .09, .72, .018), glass);
          panel.rotation.y = -angle;
          panel.position.set(midpoint.x, .64, midpoint.z);
          addAnimated(panel);
          if (system === 'clips') {
            [point, next].forEach(anchor => [.42, .78].forEach(height => {
              const clip = new THREE.Mesh(new THREE.BoxGeometry(.075, .075, .075), darkSteel);
              clip.position.set(anchor.x, height, anchor.z);
              addAnimated(clip);
            }));
          }
        } else {
          const levels = system === 'tubo' ? [.35, .59, .83] : system === 'cable' ? [.28, .47, .66, .85] : [.33, .61, .87];
          levels.forEach(height => {
            const rail = cylinderBetween(new THREE.Vector3(point.x, height, point.z), new THREE.Vector3(next.x, height, next.z), system === 'cable' ? .009 : .018, system === 'cable' ? cable : steel);
            rail.castShadow = system !== 'cable';
            addAnimated(rail);
          });
        }
      });
      cursor.copy(end);
    });

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    model.position.x = -center.x;
    model.position.z = -center.z;
    this.enterStart = performance.now();
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
    if (this.model && !reduceMotion.matches) {
      const elapsed = time - this.enterStart;
      this.model.children.forEach(object => {
        if (!object.userData.targetScale) return;
        const progress = Math.min(1, Math.max(0, (elapsed - object.userData.delay) / 430));
        const eased = 1 - Math.pow(1 - progress, 3);
        object.scale.copy(object.userData.targetScale).multiplyScalar(Math.max(.001, eased));
      });
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
    postOutput.textContent = totalPosts;
    spacesOutput.textContent = totalSpaces;
    metersOutput.textContent = totalMeters.toFixed(2);
    postNote.textContent = corners ? `incluye ${corners} ${corners === 1 ? 'poste compartido en esquina' : 'postes compartidos en esquinas'}` : 'para 1 tramo recto';
    breakdown.innerHTML = distributions.map((item, index) => `<li><span>Tramo ${String(index + 1).padStart(2, '0')} · ${item.length.toFixed(2)} m</span><strong>${item.spaces} espacios de ${item.spacing.toFixed(2)} m</strong></li>`).join('');
    status.classList.toggle('warning', warnings > 0);
    status.textContent = warnings
      ? `${warnings === 1 ? 'Un tramo requiere' : `${warnings} tramos requieren`} revisión: se respetó el máximo de 1.40 m, pero la separación quedó por debajo de 1.20 m.`
      : `Todos los tramos quedan dentro del rango de separación de 1.20 a 1.40 m.`;
    modelLabel.textContent = systemNames[systemSelect.value];
    model.setLayout(distributions, systemSelect.value);
    const lines = distributions.map((item, index) => `Tramo ${index + 1}: ${item.length.toFixed(2)} m, ${item.spaces} espacios de ${item.spacing.toFixed(2)} m.`).join('\n');
    const message = `Hola, quiero revisar esta estimación para ${systemNames[systemSelect.value]}:\n${lines}\nTotal: ${totalMeters.toFixed(2)} m, ${totalPosts} postes estimados${corners ? `, considerando ${corners} ${corners === 1 ? 'esquina compartida' : 'esquinas compartidas'}` : ''}.`;
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
