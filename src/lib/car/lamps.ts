import * as THREE from "three";
import { FINISH_ID, SHADING_GLSL, shared } from "@/lib/pixel/materials";
import { resample } from "./decals";
import type { LampDef, Pt } from "./types";

export const LAMP_POINTS = 40;
const GRAPHIC_ID = { sealed: 0, projector: 1, led4: 2, bar: 3 } as const;

/** Vertex layout: lens centre + lens rim + ring outer + bucket back. */
export const LAMP_VERTS = 1 + LAMP_POINTS * 3;

export function createLampIndex(): number[] {
  const n = LAMP_POINTS;
  const idx: number[] = [];
  const rim = (i: number) => 1 + (i % n);
  const outer = (i: number) => 1 + n + (i % n);
  const back = (i: number) => 1 + 2 * n + (i % n);
  for (let i = 0; i < n; i++) {
    idx.push(0, rim(i), rim(i + 1));
    idx.push(rim(i), outer(i), rim(i + 1), rim(i + 1), outer(i), outer(i + 1));
    idx.push(
      outer(i),
      back(i),
      outer(i + 1),
      outer(i + 1),
      back(i),
      back(i + 1),
    );
  }
  return idx;
}

/** Part id per vertex: 0 lens, 1 ring, 2 bucket. */
export function createLampParts(): Float32Array {
  const parts = new Float32Array(LAMP_VERTS);
  for (let i = 0; i < LAMP_POINTS; i++) {
    parts[1 + i] = 0;
    parts[1 + LAMP_POINTS + i] = 1;
    parts[1 + 2 * LAMP_POINTS + i] = 2;
  }
  return parts;
}

/**
 * Lamp vertices in lamp space (u right, v up, w out of the lens), before
 * placement. Also returns per-vertex lens coordinates for the graphic.
 */
export function buildLampLocal(def: LampDef) {
  const outline = resample(def.outline, LAMP_POINTS, true);
  // Start the outline at the point with the largest u so every lamp shares a seam.
  let startIdx = 0;
  for (let i = 1; i < outline.length; i++) {
    if (outline[i][0] > outline[startIdx][0]) startIdx = i;
  }
  const pts: Pt[] = outline.slice(startIdx).concat(outline.slice(0, startIdx));
  // Enforce counter-clockwise order.
  let area = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    area += a[0] * b[1] - b[0] * a[1];
  }
  if (area < 0) pts.reverse();

  let radius = 0;
  for (const p of pts) radius = Math.max(radius, Math.hypot(p[0], p[1]));
  const pos = new Float32Array(LAMP_VERTS * 3);
  const uv = new Float32Array(LAMP_VERTS * 2);
  const dome = radius * 0.12;
  pos.set([0, 0, dome], 0);
  for (let i = 0; i < LAMP_POINTS; i++) {
    const [u, v] = pts[i];
    const len = Math.hypot(u, v) || 1;
    const k = (len + def.ring) / len;
    pos.set([u, v, 0], (1 + i) * 3);
    pos.set([u * k, v * k, -0.002], (1 + LAMP_POINTS + i) * 3);
    pos.set([u * k, v * k, -0.06], (1 + 2 * LAMP_POINTS + i) * 3);
    uv.set([u / radius, v / radius], (1 + i) * 2);
    uv.set([(u * k) / radius, (v * k) / radius], (1 + LAMP_POINTS + i) * 2);
    uv.set([(u * k) / radius, (v * k) / radius], (1 + 2 * LAMP_POINTS + i) * 2);
  }
  return { pos, uv, radius };
}

const lampVertex = /* glsl */ `
  attribute float aPart;
  attribute vec2 aLens;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying float vPart;
  varying vec2 vLens;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorldPos = world.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);
    vPart = aPart;
    vLens = aLens;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const lampFragment = /* glsl */ `
  ${SHADING_GLSL}
  uniform vec3 uPaint;
  uniform vec3 uRingColor;
  uniform float uRingFinish;
  uniform vec3 uLens;
  uniform float uGraphicA;
  uniform float uGraphicB;
  uniform float uMix;
  uniform float uVisibility;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying float vPart;
  varying vec2 vLens;

  vec3 graphic(int g, vec2 p, vec3 lens) {
    float r = length(p);
    if (g == 0) {
      // Sealed beam: fluted glass rings and a bright centre.
      vec3 c = lens * (0.86 + 0.14 * step(0.5, fract(r * 5.0)));
      if (r < 0.2) c = vec3(0.97);
      return c;
    } else if (g == 1) {
      vec3 c = lens * 0.7;
      if (length(p - vec2(-0.25, -0.05)) < 0.3) c = vec3(0.95);
      if (r > 0.82) c = lens * 0.9;
      return c;
    } else if (g == 2) {
      // Four-point LED signature around a projector.
      vec3 c = vec3(0.16, 0.17, 0.19);
      if (r < 0.34) c = vec3(0.82, 0.86, 0.9);
      vec2 q = abs(p);
      if (abs(q.x - 0.52) < 0.14 && abs(q.y - 0.52) < 0.07) c = vec3(1.0);
      return c;
    }
    vec3 c = vec3(0.2, 0.21, 0.23);
    if (abs(p.y + 0.55) < 0.08) c = vec3(1.0);
    if (length(p - vec2(0.0, 0.1)) < 0.35) c = vec3(0.85);
    return c;
  }

  void main() {
    float dither = bayer4(gl_FragCoord.xy);
    if (uVisibility < 0.999 && dither >= uVisibility) discard;
    if (uPass > 0.5) { gl_FragColor = normalOutput(vViewNormal); return; }
    vec3 N = normalize(vWorldNormal);
    if (!gl_FrontFacing) N = -N;
    vec3 col;
    if (vPart < 0.5) {
      int g = int((dither < uMix ? uGraphicB : uGraphicA) + 0.5);
      col = shade(5, graphic(g, vLens, uLens), N, vWorldPos, dither);
    } else if (vPart < 1.5) {
      col = shade(int(uRingFinish + 0.5), uRingColor, N, vWorldPos, dither);
    } else {
      col = shade(0, uPaint, N, vWorldPos, dither);
    }
    gl_FragColor = vec4(col, 1.0);
  }
`;

export type LampMaterial = THREE.ShaderMaterial;

export function createLampMaterial(): LampMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: lampVertex,
    fragmentShader: lampFragment,
    uniforms: {
      uPass: shared.uPass,
      uLightDir: shared.uLightDir,
      uPaint: { value: new THREE.Color() },
      uRingColor: { value: new THREE.Color() },
      uRingFinish: { value: FINISH_ID.chrome },
      uLens: { value: new THREE.Color("#dfe6ea") },
      uGraphicA: { value: 0 },
      uGraphicB: { value: 0 },
      uMix: { value: 0 },
      uVisibility: { value: 1 },
    },
    side: THREE.DoubleSide,
  });
}

export function graphicId(def: LampDef) {
  return GRAPHIC_ID[def.graphic];
}
