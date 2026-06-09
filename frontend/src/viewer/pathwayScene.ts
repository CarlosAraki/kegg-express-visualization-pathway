import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import type { AreaData, VisualizationPayload } from "../types";
import { exportIsometricPng, exportPathwaySvg, formatTooltip } from "./exports";
import { createPvalueFilter } from "./pvalueFilter";

export function initPathwayViewer(
  payload: VisualizationPayload,
  host: HTMLElement,
  ui: {
    title: HTMLElement;
    intro: HTMLElement;
    summary: HTMLElement;
    legendPos: HTMLElement;
    legendNeg: HTMLElement;
    tooltip: HTMLElement;
    exportPng: HTMLButtonElement;
    exportSvg: HTMLButtonElement;
    pvalueMin: HTMLInputElement;
    pvalueMax: HTMLInputElement;
    pvalueMinLabel: HTMLElement;
    pvalueMaxLabel: HTMLElement;
    pvalueCount: HTMLElement;
    pvalueReset: HTMLButtonElement;
  },
) {
  const {
    mapId,
    mapW,
    mapH,
    areas,
    absMax,
    log2Min,
    log2Max,
    pvalueMin,
    pvalueMax,
    imageBase64,
  } = payload;

  ui.title.textContent = `${mapId} — 3D isometric log2 fold change bars`;
  ui.intro.textContent = `Bar height = |log2FC|. Red = up · Blue = down. ${areas.length} areas with expression data.`;
  ui.summary.textContent =
    `${payload.summary.genesInput} genes input → ` +
    `${payload.summary.genesCorrelated} correlated → ` +
    `${payload.summary.areasWithData} areas`;
  ui.legendPos.textContent = `log2FC > 0 (up to ${log2Max.toFixed(2)})`;
  ui.legendNeg.textContent = `log2FC < 0 (down to ${log2Min.toFixed(2)})`;

  const PLANE_W = 40;
  const PLANE_H = PLANE_W * (mapH / mapW);
  const BAR_HEIGHT_SCALE = 6 / (absMax || 1);
  const MIN_BAR = 0.08;
  const imageUrl = `data:image/png;base64,${imageBase64}`;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1f2e);
  scene.fog = new THREE.Fog(0x1a1f2e, 80, 140);

  const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    500,
  );
  const ISO_DIST = 55;
  camera.position.set(ISO_DIST, ISO_DIST * 0.82, ISO_DIST);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    preserveDrawingBuffer: true,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  host.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.target.set(0, 0, 0);
  controls.minDistance = 20;
  controls.maxDistance = 120;
  controls.maxPolarAngle = Math.PI / 2.2;
  controls.minPolarAngle = 0.35;
  controls.update();

  scene.add(new THREE.AmbientLight(0xffffff, 0.55));
  const sun = new THREE.DirectionalLight(0xffffff, 0.85);
  sun.position.set(30, 50, 20);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xaaccff, 0.35);
  fill.position.set(-20, 15, -25);
  scene.add(fill);

  const isoGroup = new THREE.Group();
  isoGroup.rotation.x = -Math.PI / 2;
  scene.add(isoGroup);

  const barsGroup = new THREE.Group();
  isoGroup.add(barsGroup);

  const barMeshes: THREE.Mesh[] = [];
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();

  const mapX = (cx: number) => (cx / mapW - 0.5) * PLANE_W;
  const mapY = (cy: number) => (0.5 - cy / mapH) * PLANE_H;

  const colorForLog2 = (value: number) => (value >= 0 ? 0xb2182b : 0x2166ac);

  const buildBars = () => {
    const sorted = [...areas].sort((a, b) => a.abs - b.abs);
    sorted.forEach((area) => {
      const barW = Math.max(0.15, Math.min(0.55, (area.w / mapW) * PLANE_W * 0.85));
      const barD = Math.max(0.15, Math.min(0.55, (area.h / mapH) * PLANE_H * 0.85));
      const height = Math.max(MIN_BAR, area.abs * BAR_HEIGHT_SCALE);

      const geo = new THREE.BoxGeometry(barW, barD, height);
      geo.translate(0, 0, height / 2);

      const mat = new THREE.MeshStandardMaterial({
        color: colorForLog2(area.log2),
        roughness: 0.45,
        metalness: 0.08,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(mapX(area.cx), mapY(area.cy), 0.01);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData = area;
      barsGroup.add(mesh);
      barMeshes.push(mesh);
    });
  };

  const textureLoader = new THREE.TextureLoader();
  textureLoader.load(imageUrl, (texture) => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    const planeGeo = new THREE.PlaneGeometry(PLANE_W, PLANE_H);
    const planeMat = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.92,
      metalness: 0.02,
    });
    const plane = new THREE.Mesh(planeGeo, planeMat);
    plane.receiveShadow = true;
    isoGroup.add(plane);

    const edgeGeo = new THREE.EdgesGeometry(planeGeo);
    const edge = new THREE.LineSegments(
      edgeGeo,
      new THREE.LineBasicMaterial({
        color: 0x334455,
        transparent: true,
        opacity: 0.5,
      }),
    );
    isoGroup.add(edge);

    buildBars();

    const filter = createPvalueFilter(
      { dataMin: pvalueMin, dataMax: pvalueMax },
      {
        minInput: ui.pvalueMin,
        maxInput: ui.pvalueMax,
        minLabel: ui.pvalueMinLabel,
        maxLabel: ui.pvalueMaxLabel,
        count: ui.pvalueCount,
        reset: ui.pvalueReset,
      },
      (range) => {
        let visible = 0;
        barMeshes.forEach((mesh) => {
          const p = (mesh.userData as AreaData).pvalue;
          const show = p >= range.min && p <= range.max;
          mesh.visible = show;
          if (show) visible += 1;
        });
        filter.setCount(visible, barMeshes.length);
      },
    );

    ui.exportPng.addEventListener("click", () => {
      renderer.render(scene, camera);
      exportIsometricPng(renderer.domElement, mapId);
    });

    ui.exportSvg.addEventListener("click", () => {
      try {
        exportPathwaySvg(payload, filter.getRange());
      } catch (err) {
        console.error(err);
        alert("Could not export SVG. Please try again.");
      }
    });
  });

  renderer.domElement.addEventListener("pointermove", (event) => {
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster
      .intersectObjects(barMeshes, true)
      .filter((h) => h.object.visible);
    if (hits.length) {
      const area = hits[0].object.userData as AreaData;
      ui.tooltip.style.display = "block";
      ui.tooltip.style.left = `${event.clientX + 12}px`;
      ui.tooltip.style.top = `${event.clientY + 12}px`;
      ui.tooltip.innerHTML = formatTooltip(area.entries);
      renderer.domElement.style.cursor = "pointer";
    } else {
      ui.tooltip.style.display = "none";
      renderer.domElement.style.cursor = "grab";
    }
  });

  const onResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  };
  window.addEventListener("resize", onResize);

  const animate = () => {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  };
  animate();
}
