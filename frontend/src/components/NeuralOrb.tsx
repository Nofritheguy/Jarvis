"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

export type OrbState = "idle" | "listening" | "thinking" | "speaking";

interface NeuralOrbProps {
  state: OrbState;
  audioLevel?: number;
  mode?: "particle" | "neural";
}

// ── State colours ─────────────────────────────────────────────────────────────
const STATE_COLORS: Record<OrbState, string> = {
  idle: "#00D4FF",
  listening: "#00FF88",
  thinking: "#9D4EDD",
  speaking: "#00D4FF",
};

// ── Particle Sphere ───────────────────────────────────────────────────────────
function ParticleSphere({ state, audioLevel = 0 }: { state: OrbState; audioLevel: number }) {
  const pointsRef = useRef<THREE.Points>(null!);
  const count = 800;

  const { positions, basePositions } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const base = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const phi = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;
      const r = 1.5;
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      pos[i * 3] = base[i * 3] = x;
      pos[i * 3 + 1] = base[i * 3 + 1] = y;
      pos[i * 3 + 2] = base[i * 3 + 2] = z;
    }
    return { positions: pos, basePositions: base };
  }, []);

  useFrame(({ clock }) => {
    if (!pointsRef.current) return;
    const t = clock.getElapsedTime();
    const geo = pointsRef.current.geometry;
    const pos = geo.attributes.position.array as Float32Array;

    const pulseAmp = state === "listening" ? 0.15 + audioLevel * 0.4 : state === "speaking" ? 0.1 + audioLevel * 0.3 : 0.02;
    const speed = state === "thinking" ? 3.5 : state === "speaking" ? 2.0 : 0.8;

    for (let i = 0; i < count; i++) {
      const bx = basePositions[i * 3];
      const by = basePositions[i * 3 + 1];
      const bz = basePositions[i * 3 + 2];
      const offset = Math.sin(t * speed + i * 0.05) * pulseAmp;
      const r = Math.sqrt(bx * bx + by * by + bz * bz);
      pos[i * 3] = bx * (1 + offset / r);
      pos[i * 3 + 1] = by * (1 + offset / r);
      pos[i * 3 + 2] = bz * (1 + offset / r);
    }
    geo.attributes.position.needsUpdate = true;
    pointsRef.current.rotation.y += state === "thinking" ? 0.008 : 0.002;
    pointsRef.current.rotation.x += 0.001;
  });

  const color = STATE_COLORS[state];

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial color={color} size={0.025} sizeAttenuation transparent opacity={0.85} />
    </points>
  );
}

// ── Neural Network ────────────────────────────────────────────────────────────
function NeuralNetwork({ state, audioLevel = 0 }: { state: OrbState; audioLevel: number }) {
  const groupRef = useRef<THREE.Group>(null!);
  const nodeCount = 40;

  const { nodes, edges } = useMemo(() => {
    const n: THREE.Vector3[] = [];
    for (let i = 0; i < nodeCount; i++) {
      n.push(
        new THREE.Vector3(
          (Math.random() - 0.5) * 3,
          (Math.random() - 0.5) * 3,
          (Math.random() - 0.5) * 3,
        )
      );
    }
    const e: [number, number][] = [];
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < nodeCount; j++) {
        if (n[i].distanceTo(n[j]) < 1.2) e.push([i, j]);
      }
    }
    return { nodes: n, edges: e };
  }, []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y += state === "thinking" ? 0.006 : 0.002;
  });

  const color = new THREE.Color(STATE_COLORS[state]);

  return (
    <group ref={groupRef}>
      {nodes.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ))}
      {edges.map(([a, b], i) => {
        const points = [nodes[a], nodes[b]];
        const geo = new THREE.BufferGeometry().setFromPoints(points);
        return (
          <line key={i} geometry={geo}>
            <lineBasicMaterial color={color} transparent opacity={0.3} />
          </line>
        );
      })}
    </group>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function NeuralOrb({ state, audioLevel = 0, mode = "particle" }: NeuralOrbProps) {
  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [0, 0, 4], fov: 60 }}>
        <ambientLight intensity={0.2} />
        {mode === "particle" ? (
          <ParticleSphere state={state} audioLevel={audioLevel} />
        ) : (
          <NeuralNetwork state={state} audioLevel={audioLevel} />
        )}
      </Canvas>
    </div>
  );
}
