import { type Curve, sample } from "./curve";

/**
 * A car body is lofted through cross-sections along its length. Every section
 * is a Catmull-Rom curve through seven control points on the right half,
 * mirrored to the left:
 *
 *   P0 floor centre → P1 rocker/sill (or wheel-arch edge) → P2 widest point →
 *   P3 shoulder / fender crest → P4 belt line (window sill; hood edge ahead
 *   of the windscreen) → P5 roof rail (collapses onto the hood/deck outside
 *   the cabin) → P6 top centre (hood, roof, engine lid)
 *
 * Each control coordinate is a curve over x, where x is metres measured from
 * the front tip rearwards. All values are traced from reference photos and
 * drawings of the specific car — see research/.
 */
export type BodyCurves = {
  floorY: Curve;
  rockerY: Curve;
  rockerZ: Curve;
  sideY: Curve;
  sideZ: Curve;
  crestY: Curve;
  crestZ: Curve;
  beltY: Curve;
  beltZ: Curve;
  roofY: Curve;
  roofZ: Curve;
  topY: Curve;
};

export type BodyLandmarks = {
  length: number;
  frontAxle: number; // x of the front axle
  rearAxle: number; // x of the rear axle
};

/** Fixed station layout (shared by every car so bodies morph vertex-for-vertex). */
export const STATIONS = 168;
const S_FRONT_AXLE = 0.19;
const S_REAR_AXLE = 0.74;

/** Samples per section segment P0→P1 … P5→P6. */
const SEGMENTS = [5, 7, 6, 5, 9, 9] as const;
export const HALF = SEGMENTS.reduce((a, b) => a + b, 0) + 1;
/** Points per closed ring: half section + mirrored half without the two centre points. */
export const RING = HALF * 2 - 2;
/** Index range (in the half section) that belongs to the underbody / wheel wells. */
export const UNDERBODY_END = SEGMENTS[0];

function stationS(i: number) {
  // Cosine clustering: more stations at the nose and tail where curvature is high.
  const u = i / (STATIONS - 1);
  const c = 0.5 - 0.5 * Math.cos(Math.PI * u);
  return 0.62 * u + 0.38 * c;
}

export function stationX(i: number, m: BodyLandmarks) {
  const s = stationS(i);
  if (s <= S_FRONT_AXLE) return (s / S_FRONT_AXLE) * m.frontAxle;
  if (s <= S_REAR_AXLE) {
    const t = (s - S_FRONT_AXLE) / (S_REAR_AXLE - S_FRONT_AXLE);
    return m.frontAxle + t * (m.rearAxle - m.frontAxle);
  }
  const t = (s - S_REAR_AXLE) / (1 - S_REAR_AXLE);
  return m.rearAxle + t * (m.length - m.rearAxle);
}

type P = [number, number];

// Centripetal Catmull-Rom between p1 and p2.
function catmull(p0: P, p1: P, p2: P, p3: P, t: number): P {
  const d = (a: P, b: P) =>
    Math.max(1e-5, Math.hypot(b[0] - a[0], b[1] - a[1]) ** 0.5);
  const t0 = 0;
  const t1 = t0 + d(p0, p1);
  const t2 = t1 + d(p1, p2);
  const t3 = t2 + d(p2, p3);
  const tt = t1 + (t2 - t1) * t;
  const lerpP = (a: P, b: P, ta: number, tb: number): P => {
    const k = (tt - ta) / (tb - ta);
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
  };
  const a1 = lerpP(p0, p1, t0, t1);
  const a2 = lerpP(p1, p2, t1, t2);
  const a3 = lerpP(p2, p3, t2, t3);
  const b1 = lerpP(a1, a2, t0, t2);
  const b2 = lerpP(a2, a3, t1, t3);
  return lerpP(b1, b2, t1, t2);
}

/** Half cross-section (z ≥ 0) at x, from floor centre to top centre. */
export function halfSection(c: BodyCurves, x: number, out: P[] = []): P[] {
  const pts: P[] = [
    [0, sample(c.floorY, x)],
    [sample(c.rockerZ, x), sample(c.rockerY, x)],
    [sample(c.sideZ, x), sample(c.sideY, x)],
    [sample(c.crestZ, x), sample(c.crestY, x)],
    [sample(c.beltZ, x), sample(c.beltY, x)],
    [sample(c.roofZ, x), sample(c.roofY, x)],
    [0, sample(c.topY, x)],
  ];
  // Mirror across the centre line so the section meets itself smoothly.
  const ext: P[] = [[-pts[1][0], pts[1][1]], ...pts, [-pts[5][0], pts[5][1]]];
  out.length = 0;
  for (let seg = 0; seg < 6; seg++) {
    const n = SEGMENTS[seg];
    for (let k = 0; k < n; k++) {
      out.push(
        catmull(ext[seg], ext[seg + 1], ext[seg + 2], ext[seg + 3], k / n),
      );
    }
  }
  out.push([0, pts[6][1]]);
  return out;
}

/** Ring index → half-section index and side (+1 right, -1 left). */
export function ringToHalf(j: number): [number, number] {
  if (j < HALF) return [j, 1];
  return [RING - j, -1];
}

/**
 * Writes body vertex positions (x forward = +X, centred on the wheelbase
 * midpoint) into `out` for the given curves.
 */
export function buildBodyPositions(
  curves: BodyCurves,
  marks: BodyLandmarks,
  out: Float32Array,
) {
  const half: P[] = [];
  const centre = (marks.frontAxle + marks.rearAxle) / 2;
  for (let i = 0; i < STATIONS; i++) {
    const x = stationX(i, marks);
    halfSection(curves, x, half);
    const wx = centre - x;
    for (let j = 0; j < RING; j++) {
      const [h, side] = ringToHalf(j);
      const p = half[h];
      const o = (i * RING + j) * 3;
      out[o] = wx;
      out[o + 1] = p[1];
      out[o + 2] = p[0] * side;
    }
  }
}

export function buildBodyIndex(): Uint32Array {
  const idx: number[] = [];
  for (let i = 0; i < STATIONS - 1; i++) {
    for (let j = 0; j < RING; j++) {
      const a = i * RING + j;
      const b = i * RING + ((j + 1) % RING);
      const c = (i + 1) * RING + j;
      const d = (i + 1) * RING + ((j + 1) % RING);
      // Counter-clockwise from outside, so normals point outward.
      idx.push(a, b, c, b, d, c);
    }
  }
  return new Uint32Array(idx);
}

export const BODY_VERTEX_COUNT = STATIONS * RING;
