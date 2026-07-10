"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export type OrbState = "idle" | "listening" | "thinking" | "speaking";

interface NeuralOrbProps {
  state: OrbState;
  audioLevel?: number;
  mode?: "particle" | "neural";
}

const STATE_COLORS: Record<OrbState, number> = {
  idle: 0x00d4ff,
  listening: 0x00ff88,
  thinking: 0x9d4edd,
  speaking: 0x00d4ff,
};

// ── Particle Sphere (vanilla Three.js) ───────────────────────────────────────

function createParticleScene(container: HTMLDivElement) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 100);
  camera.position.z = 4;

  const COUNT = 800;
  const positions = new Float32Array(COUNT * 3);
  const base = new Float32Array(COUNT * 3);

  for (let i = 0; i < COUNT; i++) {
    const phi = Math.acos(2 * Math.random() - 1);
    const theta = Math.random() * Math.PI * 2;
    const r = 1.5;
    const x = r * Math.sin(phi) * Math.cos(theta);
    const y = r * Math.sin(phi) * Math.sin(theta);
    const z = r * Math.cos(phi);
    positions[i * 3] = base[i * 3] = x;
    positions[i * 3 + 1] = base[i * 3 + 1] = y;
    positions[i * 3 + 2] = base[i * 3 + 2] = z;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({ color: 0x00d4ff, size: 0.025, sizeAttenuation: true, transparent: true, opacity: 0.85 });
  const points = new THREE.Points(geometry, material);
  scene.add(points);

  let currentState: OrbState = "idle";
  let currentLevel = 0;
  let animId: number;
  const t0 = Date.now();

  function animate() {
    animId = requestAnimationFrame(animate);
    const t = (Date.now() - t0) / 1000;
    const pulseAmp = currentState === "listening" ? 0.15 + currentLevel * 0.4
      : currentState === "speaking" ? 0.1 + currentLevel * 0.3 : 0.02;
    const speed = currentState === "thinking" ? 3.5 : currentState === "speaking" ? 2.0 : 0.8;

    const pos = geometry.attributes.position.array as Float32Array;
    for (let i = 0; i < COUNT; i++) {
      const bx = base[i * 3], by = base[i * 3 + 1], bz = base[i * 3 + 2];
      const r = Math.sqrt(bx * bx + by * by + bz * bz);
      const offset = Math.sin(t * speed + i * 0.05) * pulseAmp;
      pos[i * 3] = bx * (1 + offset / r);
      pos[i * 3 + 1] = by * (1 + offset / r);
      pos[i * 3 + 2] = bz * (1 + offset / r);
    }
    geometry.attributes.position.needsUpdate = true;
    points.rotation.y += currentState === "thinking" ? 0.008 : 0.002;
    points.rotation.x += 0.001;
    material.color.setHex(STATE_COLORS[currentState]);
    renderer.render(scene, camera);
  }
  animate();

  function onResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  }
  window.addEventListener("resize", onResize);

  return {
    setState(s: OrbState, level: number) { currentState = s; currentLevel = level; },
    destroy() {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", onResize);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    },
  };
}

// ── Neural Network (vanilla Three.js) ────────────────────────────────────────

function createNeuralScene(container: HTMLDivElement) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 100);
  camera.position.z = 4;

  const NODE_COUNT = 40;
  const nodes: THREE.Vector3[] = [];
  for (let i = 0; i < NODE_COUNT; i++) {
    nodes.push(new THREE.Vector3((Math.random() - 0.5) * 3, (Math.random() - 0.5) * 3, (Math.random() - 0.5) * 3));
  }

  const group = new THREE.Group();
  const nodeMeshes: THREE.Mesh[] = [];
  nodes.forEach((pos) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 8), new THREE.MeshBasicMaterial({ color: 0x00d4ff }));
    m.position.copy(pos);
    group.add(m);
    nodeMeshes.push(m);
  });

  const edgeLines: THREE.Line[] = [];
  for (let i = 0; i < NODE_COUNT; i++) {
    for (let j = i + 1; j < NODE_COUNT; j++) {
      if (nodes[i].distanceTo(nodes[j]) < 1.2) {
        const geo = new THREE.BufferGeometry().setFromPoints([nodes[i], nodes[j]]);
        const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.3 }));
        group.add(line);
        edgeLines.push(line);
      }
    }
  }
  scene.add(group);

  let currentState: OrbState = "idle";
  let animId: number;

  function animate() {
    animId = requestAnimationFrame(animate);
    group.rotation.y += currentState === "thinking" ? 0.006 : 0.002;
    const color = new THREE.Color(STATE_COLORS[currentState]);
    nodeMeshes.forEach((m) => (m.material as THREE.MeshBasicMaterial).color.copy(color));
    edgeLines.forEach((l) => (l.material as THREE.LineBasicMaterial).color.copy(color));
    renderer.render(scene, camera);
  }
  animate();

  function onResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  }
  window.addEventListener("resize", onResize);

  return {
    setState(s: OrbState, _level: number) { currentState = s; },
    destroy() {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    },
  };
}

// ── React component ───────────────────────────────────────────────────────────

export default function NeuralOrb({ state, audioLevel = 0, mode = "particle" }: NeuralOrbProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{ setState: (s: OrbState, l: number) => void; destroy: () => void } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const scene = mode === "particle"
      ? createParticleScene(containerRef.current)
      : createNeuralScene(containerRef.current);
    sceneRef.current = scene;
    return () => scene.destroy();
  }, [mode]);

  useEffect(() => {
    sceneRef.current?.setState(state, audioLevel);
  }, [state, audioLevel]);

  return <div ref={containerRef} className="w-full h-full" />;
}
