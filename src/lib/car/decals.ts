import * as THREE from "three";
import { FINISH_ID } from "@/lib/pixel/materials";
import {
  type BodyMaterial,
  DECAL_TEXELS,
  MAX_DECALS,
  MAX_POINTS,
} from "./body-material";
import type { CarDef, Decal, Pt } from "./types";

const PLANE_ID = { side: 0, top: 1, front: 2, rear: 3 } as const;
const KIND_ID = { fill: 0, line: 1, band: 2 } as const;

/**
 * Resample a polyline/polygon to n points evenly spaced by arc length, then
 * snap each original vertex onto its nearest sample so corners survive
 * (a 4-point box must stay a box, not become an octagon).
 */
export function resample(
  points: readonly Pt[],
  n: number,
  closed: boolean,
): Pt[] {
  if (points.length === 0) return Array.from({ length: n }, () => [0, 0] as Pt);
  if (points.length === 1) return Array.from({ length: n }, () => points[0]);
  const pts = closed ? [...points, points[0]] : [...points];
  const lengths = [0];
  for (let i = 1; i < pts.length; i++) {
    lengths.push(
      lengths[i - 1] +
        Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]),
    );
  }
  const total = lengths[lengths.length - 1] || 1;
  const out: Pt[] = [];
  const steps = closed ? n : n - 1;
  let seg = 0;
  for (let k = 0; k < n; k++) {
    const target = (k / steps) * total;
    while (seg < pts.length - 2 && lengths[seg + 1] < target) seg++;
    const span = lengths[seg + 1] - lengths[seg] || 1;
    const t = Math.min(1, Math.max(0, (target - lengths[seg]) / span));
    out.push([
      pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * t,
      pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * t,
    ]);
  }
  if (n >= points.length) {
    for (let i = 0; i < points.length; i++) {
      const k = Math.round((lengths[i] / total) * steps) % n;
      out[k] = points[i];
    }
  }
  return out;
}

/** A decal flattened to numbers, with a fixed point count so two can be lerped. */
export type FlatDecal = {
  id: string;
  plane: number;
  kind: number;
  points: Float32Array; // object space pairs
  finish: number;
  alpha: number;
  width: number;
  facing: number;
  depth: [number, number];
  stripes: [number, number];
  side: number; // 0 both, 1 right (+Z), -1 left (-Z)
  color: THREE.Color | null; // null = paint
};

const centreOf = (car: CarDef) => (car.frontAxle + car.rearAxle) / 2;

/**
 * Closed outlines from different tracers may start anywhere and wind either
 * way; morphing them point-by-point would twist. Normalise to clockwise
 * winding, starting at the lowest-front corner (min a + b).
 */
function canonical(points: readonly Pt[]): Pt[] {
  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const [a0, b0] = points[i];
    const [a1, b1] = points[(i + 1) % points.length];
    area += a0 * b1 - a1 * b0;
  }
  const ordered = area > 0 ? [...points].reverse() : [...points];
  let start = 0;
  for (let i = 1; i < ordered.length; i++) {
    if (ordered[i][0] + ordered[i][1] < ordered[start][0] + ordered[start][1])
      start = i;
  }
  return ordered.slice(start).concat(ordered.slice(0, start));
}

function flatten(
  decal: Decal,
  car: CarDef,
  count: number,
  alpha: number,
): FlatDecal {
  const closed = decal.kind !== "line";
  const pts = resample(
    closed ? canonical(decal.points) : decal.points,
    count,
    closed,
  );
  const centre = centreOf(car);
  const flat = new Float32Array(count * 2);
  for (let i = 0; i < count; i++) {
    const [a, b] = pts[i];
    // Car space x (from the front tip) → object space X (forward = +X).
    if (decal.plane === "side" || decal.plane === "top") {
      flat[i * 2] = centre - a;
      flat[i * 2 + 1] = b;
    } else {
      flat[i * 2] = a;
      flat[i * 2 + 1] = b;
    }
  }
  let depth: [number, number] = [-1e3, 1e3];
  if (decal.depth) {
    const [d0, d1] = decal.depth;
    depth =
      decal.plane === "front" || decal.plane === "rear"
        ? [
            Math.min(centre - d0, centre - d1),
            Math.max(centre - d0, centre - d1),
          ]
        : [d0, d1];
  }
  return {
    id: decal.id,
    plane: PLANE_ID[decal.plane],
    kind: KIND_ID[decal.kind],
    points: flat,
    finish: FINISH_ID[decal.finish],
    alpha,
    width: decal.width ?? 0,
    facing: decal.facing ?? 0.25,
    depth,
    // A negative period tells the shader to stripe along the other axis.
    stripes: decal.stripes
      ? [
          decal.stripeAxis &&
          decal.stripeAxis !== (decal.plane === "top" ? "a" : "b")
            ? -decal.stripes[0]
            : decal.stripes[0],
          decal.stripes[1],
        ]
      : [0, 0],
    side: decal.side === "right" ? 1 : decal.side === "left" ? -1 : 0,
    color: decal.color === "paint" ? null : new THREE.Color(decal.color),
  };
}

/**
 * Pairs the decals of two neighbouring stops slot by slot. A slot missing on
 * one side keeps the other side's shape and simply dissolves out.
 */
export function pairDecals(a: CarDef, b: CarDef): [FlatDecal[], FlatDecal[]] {
  const ids: string[] = [];
  for (const d of a.decals) if (!ids.includes(d.id)) ids.push(d.id);
  for (const d of b.decals) if (!ids.includes(d.id)) ids.push(d.id);
  const outA: FlatDecal[] = [];
  const outB: FlatDecal[] = [];
  for (const id of ids) {
    const da = a.decals.find((d) => d.id === id);
    const db = b.decals.find((d) => d.id === id);
    const count =
      Math.max(da?.points.length ?? 0, db?.points.length ?? 0, 2) * 2;
    if (da && db && da.plane === db.plane) {
      outA.push(flatten(da, a, count, 1));
      outB.push(flatten(db, b, count, 1));
    } else if (da && db) {
      // Same slot on a different projection plane: dissolve across, don't jump.
      outA.push(flatten(da, a, count, 1));
      outB.push(flatten(da, a, count, 0));
      outA.push(flatten(db, b, count, 0));
      outB.push(flatten(db, b, count, 1));
    } else if (da) {
      outA.push(flatten(da, a, count, 1));
      outB.push(flatten(da, a, count, 0));
    } else if (db) {
      outA.push(flatten(db, b, count, 0));
      outB.push(flatten(db, b, count, 1));
    }
  }
  return [outA, outB];
}

const tmpColor = new THREE.Color();

/** Blend two paired decal lists into the body material's uniforms. */
export function applyDecals(
  material: BodyMaterial,
  a: FlatDecal[],
  b: FlatDecal[],
  t: number,
  paint: THREE.Color,
) {
  const u = material.uniforms;
  const pts = u.uPts.value.image.data as Float32Array;
  const params = u.uDecals.value.image.data as Float32Array;
  let cursor = 0;
  let slot = 0;
  for (let i = 0; i < a.length && slot < MAX_DECALS; i++) {
    const da = a[i];
    const db = b[i];
    const count = da.points.length / 2;
    if (cursor + count > MAX_POINTS) break;
    const alpha = da.alpha + (db.alpha - da.alpha) * t;
    if (alpha <= 0.001) continue;
    for (let k = 0; k < count * 2; k++) {
      pts[cursor * 2 + k] = da.points[k] + (db.points[k] - da.points[k]) * t;
    }
    // Discrete properties switch at the midpoint of the morph.
    const d = t < 0.5 ? da : db;
    const color = mixOklab(da.color ?? paint, db.color ?? paint, t, tmpColor);
    const o = slot * DECAL_TEXELS * 4;
    params.set([cursor, count, d.plane, d.kind], o);
    params.set(
      [
        d.finish,
        alpha,
        da.width + (db.width - da.width) * t,
        da.facing + (db.facing - da.facing) * t,
      ],
      o + 4,
    );
    params.set([color.r, color.g, color.b, d.side], o + 8);
    params.set(
      [
        da.depth[0] + (db.depth[0] - da.depth[0]) * t,
        da.depth[1] + (db.depth[1] - da.depth[1]) * t,
        d.stripes[0],
        d.stripes[1],
      ],
      o + 12,
    );
    cursor += count;
    slot++;
  }
  u.uDecalCount.value = slot;
  u.uPts.value.needsUpdate = true;
  u.uDecals.value.needsUpdate = true;
}

// OKLab blending so colour morphs stay vivid instead of passing through grey.
function toOklab(c: THREE.Color): [number, number, number] {
  const lin = (v: number) =>
    v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  const r = lin(c.r);
  const g = lin(c.g);
  const b = lin(c.b);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [
    0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
  ];
}

function fromOklab([L, A, B]: [number, number, number], out: THREE.Color) {
  const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3;
  const m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3;
  const s = (L - 0.0894841775 * A - 1.291485548 * B) ** 3;
  const r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
  const g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
  const b = -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s;
  const enc = (v: number) => {
    const c = Math.min(1, Math.max(0, v));
    return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055;
  };
  return out.setRGB(enc(r), enc(g), enc(b));
}

export function mixOklab(
  a: THREE.Color,
  b: THREE.Color,
  t: number,
  out: THREE.Color,
) {
  if (t <= 0) return out.copy(a);
  if (t >= 1) return out.copy(b);
  const la = toOklab(a);
  const lb = toOklab(b);
  return fromOklab(
    [
      la[0] + (lb[0] - la[0]) * t,
      la[1] + (lb[1] - la[1]) * t,
      la[2] + (lb[2] - la[2]) * t,
    ],
    out,
  );
}
