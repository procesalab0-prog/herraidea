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
renderer.toneMappingExposure = 1.3;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(32, 1, 0.05, 40);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.07;
controls.minDistance = 0.5; controls.maxDistance = 7.5; controls.maxPolarAngle = Math.PI * 0.53;
controls.autoRotate = true; controls.autoRotateSpeed = 0.9;

const key = new THREE.DirectionalLight(0xffffff, 2.6);
key.position.set(-2.4, 3.6, 2.6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 5; key.shadow.bias = -0.0004;
Object.assign(key.shadow.camera, { left: -1.9, right: 1.9, top: 1.9, bottom: -1.9, near: 0.5, far: 10 });
scene.add(key);
scene.add(new THREE.HemisphereLight(0xdfe6f0, 0x9aa1aa, 1.0));

const suelo = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.2 }));
suelo.rotation.x = -Math.PI / 2; suelo.position.y = 0; suelo.receiveShadow = true; scene.add(suelo);

// ---- despiece: misma lógica que los visores del sitio (clip «Despiece», 0 = armado, 1 = desarmado)
let mixer = null, accion = null, duracion = 1, cantidad = 0, tween = 0;
const baseTarget = new THREE.Vector3();
const rango = $('#rango'), salida = $('#rango-valor');
const menosMovimiento = matchMedia('(prefers-reduced-motion: reduce)');
function marcar(sel) { document.querySelectorAll('[data-d]').forEach((b) => b.classList.toggle('on', b.matches(sel))); }
function fijar(v) {
  if (!accion) return;
  const t = Math.max(0, Math.min(1, v));
  const k = (1 + t * 0.55) / (1 + cantidad * 0.55);          // la cámara se aleja al separar las piezas
  const off = camera.position.clone().sub(controls.target).multiplyScalar(k);
  controls.target.copy(baseTarget); controls.target.y += 0.16 * t;
  camera.position.copy(controls.target).add(off);
  suelo.position.y = -0.22 * t;
  cantidad = t; accion.time = t * duracion; mixer.update(0); controls.update();
  rango.value = Math.round(t * 100); salida.textContent = `${Math.round(t * 100)} %`;
}
function animarA(dest) {
  cancelAnimationFrame(tween);
  if (menosMovimiento.matches) return fijar(dest);
  const t0 = performance.now(), desde = cantidad, ms = 2600 * Math.max(0.35, Math.abs(dest - desde));
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

const bytes = Uint8Array.from(atob(window.__GLB__), (c) => c.charCodeAt(0)).buffer;
new GLTFLoader().parse(bytes, '', (gltf) => {
  let piezas = 0;
  gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    piezas++; o.castShadow = true; o.receiveShadow = true;
    if (o.material) o.material.envMapIntensity = 1.7;
  });
  scene.add(gltf.scene);
  const c = new THREE.Box3().setFromObject(gltf.scene).getCenter(new THREE.Vector3());
  c.y -= 0.06; baseTarget.copy(c); controls.target.copy(c); vista('tres');
  mixer = new THREE.AnimationMixer(gltf.scene);
  const clip = gltf.animations.find((a) => a.name === 'Despiece') || gltf.animations[0];
  if (clip) { duracion = clip.duration; accion = mixer.clipAction(clip); accion.play(); accion.paused = true; }
  document.querySelectorAll('[data-d]').forEach((b) => { b.disabled = !accion; });
  rango.disabled = !accion; fijar(0);
  $('#carga').remove();
  $('#stats').textContent = `${piezas} piezas`;
  window.__LISTO__ = true;
}, (e) => { $('#carga').textContent = 'No se pudo abrir el modelo: ' + e.message; });

// y = arriba; z del visor = −Y del modelo (glTF convierte Z-arriba a Y-arriba)
const VISTAS = {
  tres:    [1.55, 0.78, 2.65], trasera: [-4.4, 0.12, 0.0], lateral: [0.0, 0.12, 4.4],
  planta:  [0.001, 4.6, 0.0], detalle: [-0.35, 0.62, 1.25],
};
function vista(n) {
  const t = controls.target, p = VISTAS[n].map((q) => q * (1 + cantidad * 0.55)), s = innerWidth / innerHeight < 0.9 ? 2.1 : 1;
  camera.position.set(t.x + p[0] * s, t.y + p[1] * s, t.z + p[2] * s);
  controls.autoRotate = false; $('#rot').classList.remove('on'); controls.update();
}
function fit() {
  const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.fov = w / h < 0.9 ? 46 : 32; camera.updateProjectionMatrix();
}
addEventListener('resize', fit); fit();

document.querySelectorAll('[data-v]').forEach((b) => b.addEventListener('click', () => vista(b.dataset.v)));
$('#rot').addEventListener('click', (e) => { controls.autoRotate = !controls.autoRotate; e.currentTarget.classList.toggle('on', controls.autoRotate); });
canvas.addEventListener('pointerdown', () => { controls.autoRotate = false; $('#rot').classList.remove('on'); });
$('#foto').addEventListener('click', () => {
  renderer.render(scene, camera);
  const a = document.createElement('a'); a.download = 'riverack-vista.png'; a.href = canvas.toDataURL('image/png'); a.click();
});
(function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
