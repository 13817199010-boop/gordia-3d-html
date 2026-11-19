import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import modelUrl from './models/gordia-mobile.glb?url';

const canvas = document.querySelector('canvas');
const status = document.querySelector('output');
async function start() {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, .1, 100);
  const controls = new OrbitControls(camera, canvas);
  controls.minDistance = 2.6;
  controls.maxDistance = 32;
  controls.enablePan = false;
  const draw = () => renderer.render(scene, camera);
  controls.addEventListener('change', draw);
  scene.add(new THREE.HemisphereLight(0xfff0e1, 0x9f9cb6, 2.1));
  for (const [x,y,z,intensity] of [[-4,8,6,2.8],[5,4,3,1.1],[2,7,-5,2.2]]) {
    const light = new THREE.DirectionalLight(0xfff4e9, intensity);
    light.position.set(x,y,z); scene.add(light);
  }
  const { scene: model } = await new GLTFLoader().loadAsync(modelUrl, event => {
    if (event.total) status.textContent = '加载 ' + Math.round(100 * event.loaded / event.total) + '%';
  });
  scene.add(model);
  const size = new THREE.Box3().setFromObject(model);
  const center = size.getCenter(new THREE.Vector3());
  const span = size.getSize(new THREE.Vector3());
  function preset(angle) {
    controls.target.copy(center);
    const radius = Math.max(span.y * 1.21, span.x * 1.16 / camera.aspect) / (2 * Math.tan(Math.PI / 12));
    const t = THREE.MathUtils.degToRad(angle);
    camera.position.copy(center).add(new THREE.Vector3(radius*Math.sin(t), radius*.065, radius*Math.cos(t)));
    controls.update(); draw();
  }
  function resize() {
    const {clientWidth:w,clientHeight:h} = canvas;
    renderer.setSize(w,h,false);
    camera.aspect = w/h; camera.updateProjectionMatrix(); draw();
  }
  resize(); preset(0);
  new ResizeObserver(resize).observe(canvas);
  for (const button of document.querySelectorAll('[data-angle]')) {
    button.onclick = () => preset(Number(button.dataset.angle));
  }
  const socket = model.getObjectByName('WeaponSocketR') || model.getObjectByName('WeaponSocket.R');
  if (!socket) throw new Error('武器挂点缺失');
  document.querySelector('#weapon').onclick = event => {
    socket.visible = !socket.visible;
    event.currentTarget.setAttribute('aria-pressed', String(socket.visible)); draw();
  };
  status.textContent = '';
  canvas.dataset.ready = 'true';
}
start().catch(error => { console.error(error); status.textContent = '预览加载失败，请检查模型文件与 WebGL 支持。'; });
