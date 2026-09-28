import * as THREE from "three";
import { SHADING_GLSL, shared } from "@/lib/pixel/materials";
import type { WheelDef, WheelDesign } from "./types";

/**
 * Rim faces are procedural: a disc whose pixels are classified as spoke,
 * gap (brake disc / caliper visible behind), hub or lip. Designs are just
 * parameter sets, so neighbouring generations blend smoothly.
 */
export type RimParams = {
  spokes: number;
  /** Spoke width as a fraction of the angular pitch at the hub and at the rim. */
  widthHub: number;
  widthRim: number;
  /** Radians of twist from hub to rim. */
  twist: number;
  /** Split each spoke into two (twin-spoke designs): gap fraction of spoke width. */
  split: number;
  /** Hub cap radius as a fraction of the rim radius. */
  hub: number;
  /** Outer lip width as a fraction of the rim radius. */
  lip: number;
  /** 1 = solid disc with round holes (steel / cookie-cutter style). */
  disc: number;
  /** Hole radius (fraction) and ring position (fraction) for disc designs. */
  holeSize: number;
  holeRing: number;
  /** Radial stretch of disc holes (1 = round, >1 = petal-shaped). */
  holeAspect: number;
};

export const RIM_DESIGNS: Record<WheelDesign, RimParams> = {
  "steel-hubcap": {
    spokes: 10,
    widthHub: 1,
    widthRim: 1,
    twist: 0,
    split: 0,
    hub: 0.62,
    lip: 0.09,
    disc: 1,
    holeSize: 0.05,
    holeRing: 0.74,
    holeAspect: 1,
  },
  fuchs: {
    spokes: 5,
    widthHub: 0.62,
    widthRim: 0.34,
    twist: 0,
    split: 0,
    hub: 0.24,
    lip: 0.1,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
  cookie: {
    spokes: 7,
    widthHub: 1,
    widthRim: 1,
    twist: 0,
    split: 0,
    hub: 0.26,
    lip: 0.08,
    disc: 1,
    holeSize: 0.2,
    holeRing: 0.6,
    holeAspect: 1,
  },
  // ATS cast wheel (911 SC): a dished disc with five petal-shaped openings.
  ats: {
    spokes: 5,
    widthHub: 1,
    widthRim: 1,
    twist: 0,
    split: 0,
    hub: 0.24,
    lip: 0.07,
    disc: 1,
    holeSize: 0.15,
    holeRing: 0.58,
    holeAspect: 1.8,
  },
  cup: {
    spokes: 5,
    widthHub: 0.5,
    widthRim: 0.5,
    twist: 0,
    split: 0,
    hub: 0.3,
    lip: 0.07,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
  twist: {
    spokes: 5,
    widthHub: 0.44,
    widthRim: 0.3,
    twist: 0.5,
    split: 0,
    hub: 0.24,
    lip: 0.06,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
  "five-spoke": {
    spokes: 5,
    widthHub: 0.38,
    widthRim: 0.3,
    twist: 0,
    split: 0,
    hub: 0.22,
    lip: 0.05,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
  "twin-spoke": {
    spokes: 5,
    widthHub: 0.46,
    widthRim: 0.42,
    twist: 0,
    split: 0.34,
    hub: 0.2,
    lip: 0.045,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
  "ten-spoke": {
    spokes: 10,
    widthHub: 0.4,
    widthRim: 0.32,
    twist: 0,
    split: 0,
    hub: 0.2,
    lip: 0.045,
    disc: 0,
    holeSize: 0,
    holeRing: 0,
    holeAspect: 1,
  },
};

const faceVertex = /* glsl */ `
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec2 vDisc;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorldPos = world.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);
    vDisc = position.xy;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const faceFragment = /* glsl */ `
  ${SHADING_GLSL}
  uniform float uRadius;
  uniform float uSpokes;
  uniform float uWidthHub;
  uniform float uWidthRim;
  uniform float uTwist;
  uniform float uSplit;
  uniform float uHub;
  uniform float uLip;
  uniform float uDisc;
  uniform float uHoleSize;
  uniform float uHoleRing;
  uniform float uHoleAspect;
  uniform float uVisibility;
  uniform float uSpin;
  uniform vec3 uFace;
  uniform vec3 uLipColor;
  uniform vec3 uCaliper;
  uniform float uHasCaliper;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec2 vDisc;

  void main() {
    float dither = bayer4(gl_FragCoord.xy);
    if (uVisibility < 0.999 && dither >= uVisibility) discard;
    if (uPass > 0.5) { gl_FragColor = normalOutput(vViewNormal); return; }
    vec3 N = normalize(vWorldNormal);
    if (!gl_FrontFacing) N = -N;

    float r = length(vDisc) / uRadius;
    float a = atan(vDisc.y, vDisc.x);
    int finish = 4;
    vec3 base = uFace;

    if (r > 1.0 - uLip) {
      finish = 1; base = uLipColor;
    } else if (r < uHub) {
      finish = 1; base = uFace;
      if (r < uHub * 0.45) base = uFace * 0.55;
    } else {
      bool spoke;
      if (uDisc > 0.5) {
        float pitch = 6.2831853 / uSpokes;
        float k = floor((a + uSpin) / pitch + 0.5);
        float ca = k * pitch - uSpin;
        vec2 dir = vec2(cos(ca), sin(ca));
        vec2 q = vDisc / uRadius - dir * uHoleRing;
        // Distance in the hole's radial/tangential frame; aspect > 1 gives petals.
        vec2 rt = vec2(dot(q, dir) / uHoleAspect, dot(q, vec2(-dir.y, dir.x)));
        spoke = length(rt) > uHoleSize;
      } else {
        float t = clamp((r - uHub) / (1.0 - uLip - uHub), 0.0, 1.0);
        float pitch = 6.2831853 / uSpokes;
        float ang = a + uSpin - uTwist * t;
        float local = mod(ang + pitch * 0.5, pitch) - pitch * 0.5;
        float w = mix(uWidthHub, uWidthRim, t) * pitch * 0.5;
        spoke = abs(local) < w;
        if (uSplit > 0.0 && abs(local) < w * uSplit) spoke = false;
      }
      if (!spoke) {
        // Brake disc behind the spokes, caliper at the trailing top.
        finish = 4;
        base = vec3(0.23, 0.23, 0.24);
        if (r > 0.9 - uLip) base = vec3(0.12);
        if (uHasCaliper > 0.5 && r > 0.48 && r < 0.86 && a > 0.35 && a < 1.25) base = uCaliper;
      }
    }
    gl_FragColor = vec4(shade(finish, base, N, vWorldPos, dither), 1.0);
  }
`;

export type RimMaterial = THREE.ShaderMaterial;

export function createRimMaterial(): RimMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: faceVertex,
    fragmentShader: faceFragment,
    uniforms: {
      uPass: shared.uPass,
      uLightDir: shared.uLightDir,
      uRadius: { value: 0.2 },
      uSpokes: { value: 5 },
      uWidthHub: { value: 0.5 },
      uWidthRim: { value: 0.4 },
      uTwist: { value: 0 },
      uSplit: { value: 0 },
      uHub: { value: 0.2 },
      uLip: { value: 0.08 },
      uDisc: { value: 0 },
      uHoleSize: { value: 0 },
      uHoleRing: { value: 0 },
      uHoleAspect: { value: 1 },
      uVisibility: { value: 1 },
      uSpin: { value: 0 },
      uFace: { value: new THREE.Color("#b8b8b8") },
      uLipColor: { value: new THREE.Color("#d8d8d8") },
      uCaliper: { value: new THREE.Color("#1a1a1a") },
      uHasCaliper: { value: 0 },
    },
    side: THREE.DoubleSide,
  });
}

export function applyRim(
  material: RimMaterial,
  params: RimParams,
  def: WheelDef,
) {
  const u = material.uniforms;
  // The face mesh is a unit disc scaled to the rim radius.
  u.uRadius.value = 1;
  u.uSpokes.value = params.spokes;
  u.uWidthHub.value = params.widthHub;
  u.uWidthRim.value = params.widthRim;
  u.uTwist.value = params.twist;
  u.uSplit.value = params.split;
  u.uHub.value = params.hub;
  u.uLip.value = params.lip;
  u.uDisc.value = params.disc;
  u.uHoleSize.value = params.holeSize;
  u.uHoleRing.value = params.holeRing;
  u.uHoleAspect.value = params.holeAspect;
  (u.uFace.value as THREE.Color).set(def.face);
  (u.uLipColor.value as THREE.Color).set(def.lip);
  (u.uCaliper.value as THREE.Color).set(def.caliper ?? "#1a1a1a");
  u.uHasCaliper.value = def.caliper ? 1 : 0;
}

/** Unit tyre: outer radius 1, width 1 along Z, sidewall bulge; scaled per wheel. */
export function createTyreGeometry(rimRatio: number) {
  const profile: THREE.Vector2[] = [];
  const inner = rimRatio;
  const steps = 10;
  // Inner lip → shoulder → tread → shoulder → inner lip (x = radius, y = z).
  profile.push(new THREE.Vector2(inner, -0.5));
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const ang = -Math.PI / 2 + t * Math.PI;
    const bulge = Math.cos(ang);
    const z = Math.sin(ang) * 0.5;
    const rr = inner + (1 - inner) * (0.55 + 0.45 * bulge);
    profile.push(new THREE.Vector2(rr, z));
  }
  profile.push(new THREE.Vector2(inner, 0.5));
  const lathe = new THREE.LatheGeometry(profile, 48);
  // Lathe spins around Y; wheels spin around Z.
  lathe.rotateX(Math.PI / 2);
  return lathe;
}

export function createFaceGeometry() {
  return new THREE.CircleGeometry(1, 48);
}
