import * as THREE from '../../assets/vendor/three/three.module.js';
import { GLTFLoader } from '../../assets/vendor/three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from '../../assets/vendor/three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from '../../assets/vendor/three/addons/environments/RoomEnvironment.js';

const $ = (s) => document.querySelector(s);
const canvas = $('#c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 120);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.07;
controls.minDistance = 1.2; controls.maxDistance = 40; controls.maxPolarAngle = Math.PI * 0.5;
controls.autoRotateSpeed = 0.7;

const sol = new THREE.DirectionalLight(0xfff1dc, 2.4);
sol.position.set(-7, 11, 8); sol.castShadow = true;
sol.shadow.mapSize.set(4096, 4096); sol.shadow.radius = 4; sol.shadow.bias = -0.0005; sol.shadow.normalBias = 0.02;
Object.assign(sol.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 });
scene.add(sol);
scene.add(new THREE.HemisphereLight(0xe4ebf4, 0x9a8f86, 0.9));
const calida = new THREE.PointLight(0xffd6a8, 6, 7, 1.6); calida.position.set(0, 2.6, 0.5); scene.add(calida);

const suelo = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShadowMaterial({ opacity: 0.2 }));
suelo.rotation.x = -Math.PI / 2; suelo.receiveShadow = true; scene.add(suelo);

// ---- capas que se pueden ocultar
const CAPAS = {
  lona: ['lona_', 'ventanal_', 'ojo_de_buey', 'respiradero', 'chimenea_sombrero', 'chimenea_tapajuntas'],
  terraza: ['terraza'],
};
const grupos = { lona: [], terraza: [] };
const estado = { lona: true, terraza: true };
function capa(nombre, visible) {
  estado[nombre] = visible;
  grupos[nombre].forEach((o) => { o.visible = visible; });
  $(`#capa-${nombre}`).classList.toggle('on', visible);
  $(`#capa-${nombre}`).setAttribute('aria-pressed', String(visible));
  suelo.position.y = estado.terraza ? -0.66 : -0.002;
}

// ---- despiece: misma lógica que los visores del sitio (clip «Despiece», 0 = armado, 1 = desarmado)
let mixer = null, accion = null, duracion = 1, cantidad = 0, tween = 0;
const rango = $('#rango'), salida = $('#rango-valor');
const menosMovimiento = matchMedia('(prefers-reduced-motion: reduce)');
function marcar(sel) { document.querySelectorAll('[data-d]').forEach((b) => b.classList.toggle('on', b.matches(sel))); }
function fijar(v) {
  if (!accion) return;
  const t = Math.max(0, Math.min(1, v));
  const k = (1 + t * 0.4) / (1 + cantidad * 0.4);           // la cámara se aleja al separar las piezas
  const off = camera.position.clone().sub(controls.target).multiplyScalar(k);
  camera.position.copy(controls.target).add(off);
  cantidad = t; accion.time = t * duracion; mixer.update(0); controls.update();
  rango.value = Math.round(t * 100); salida.textContent = `${Math.round(t * 100)} %`;
}
function animarA(dest) {
  cancelAnimationFrame(tween);
  if (menosMovimiento.matches) return fijar(dest);
  const t0 = performance.now(), desde = cantidad, ms = 3200 * Math.max(0.35, Math.abs(dest - desde));
  const paso = (now) => {
    const e = Math.min(1, (now - t0) / ms), s = e * e * (3 - 2 * e);
    fijar(desde + (dest - desde) * s);
    if (e < 1) tween = requestAnimationFrame(paso);
  };
  tween = requestAnimationFrame(paso);
}
$('#desarmar').addEventListener('click', () => { marcar('#desarmar'); animarA(1); });
$('#armar').addEventListener('click', () => { marcar('#armar'); animarA(0); });
rango.addEventListener('input', () => {
  cancelAnimationFrame(tween);
  marcar(rango.value === '0' ? '#armar' : rango.value === '100' ? '#desarmar' : 'x');
  fijar(Number(rango.value) / 100);
});
window.__despiece = (v) => fijar(v);

// ---- vistas (y = arriba; z del visor = −Y del modelo)
const VISTAS = {
  exterior: { cam: [-5.6, 2.6, 13.0], tgt: [0.4, 1.6, 0], lona: true, terraza: true },
  interior: { cam: [0.2, 9.4, 7.6], tgt: [0, 0.5, -0.1], lona: false, terraza: false },
  frente:   { cam: [0, 2.2, 15.5], tgt: [0, 1.8, 0] },
  planta:   { cam: [0.01, 17, 0.6], tgt: [0, 0, 0] },
};
function vista(n) {
  const v = VISTAS[n], s = (innerWidth / innerHeight < 0.9 ? 1.55 : 1) * (1 + cantidad * 0.4);
  if (v.lona !== undefined) { capa('lona', v.lona); capa('terraza', v.terraza); }
  controls.target.set(...v.tgt);
  camera.position.set(...v.cam.map((q, i) => v.tgt[i] + (q - v.tgt[i]) * s));
  detenerGiro(); controls.update();
}
function detenerGiro() { controls.autoRotate = false; $('#rot').classList.remove('on'); }

const bytes = Uint8Array.from(atob(window.__GLB__), (c) => c.charCodeAt(0)).buffer;
new GLTFLoader().parse(bytes, '', (gltf) => {
  let piezas = 0;
  gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    piezas++; o.castShadow = true; o.receiveShadow = true;
    const m = o.material;
    if (m) {
      m.envMapIntensity = 1.2;
      if (m.transparent) { m.depthWrite = false; o.castShadow = false; o.renderOrder = 2; }
    }
    for (const [nombre, prefijos] of Object.entries(CAPAS)) if (prefijos.some((p) => o.name.startsWith(p))) grupos[nombre].push(o);
  });
  scene.add(gltf.scene);
  mixer = new THREE.AnimationMixer(gltf.scene);
  const clip = gltf.animations.find((a) => a.name === 'Despiece') || gltf.animations[0];
  if (clip) { duracion = clip.duration; accion = mixer.clipAction(clip); accion.play(); accion.paused = true; }
  document.querySelectorAll('[data-d]').forEach((b) => { b.disabled = !accion; });
  rango.disabled = !accion;
  vista('exterior'); fijar(0);
  $('#carga').remove();
  $('#stats').textContent = `${piezas} piezas`;
  window.__LISTO__ = true;
}, (e) => { $('#carga').textContent = 'No se pudo abrir el modelo: ' + e.message; });

function fit() {
  const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.fov = w / h < 0.9 ? 48 : 34; camera.updateProjectionMatrix();
}
addEventListener('resize', fit); fit();

document.querySelectorAll('[data-v]').forEach((b) => b.addEventListener('click', () => vista(b.dataset.v)));
['lona', 'terraza'].forEach((n) => $(`#capa-${n}`).addEventListener('click', () => capa(n, !estado[n])));
$('#rot').addEventListener('click', (e) => { controls.autoRotate = !controls.autoRotate; e.currentTarget.classList.toggle('on', controls.autoRotate); });
canvas.addEventListener('pointerdown', detenerGiro);
$('#foto').addEventListener('click', () => {
  renderer.render(scene, camera);
  const a = document.createElement('a'); a.download = 'domo-geodesico-vista.png'; a.href = canvas.toDataURL('image/png'); a.click();
});
(function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
