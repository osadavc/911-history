/** A 1D curve given as [x, value] keys, sorted by x. */
export type Curve = readonly (readonly [number, number])[];

/**
 * Monotone cubic (Fritsch–Carlson) interpolation: passes through every key
 * without overshooting, so traced silhouettes never bulge between points.
 * Values outside the key range clamp to the end keys.
 */
export function sample(curve: Curve, x: number): number {
  const n = curve.length;
  if (n === 0) return 0;
  if (n === 1 || x <= curve[0][0]) return curve[0][1];
  if (x >= curve[n - 1][0]) return curve[n - 1][1];

  let i = 0;
  while (i < n - 2 && x > curve[i + 1][0]) i++;

  const [x0, y0] = curve[i];
  const [x1, y1] = curve[i + 1];
  const h = x1 - x0;
  const t = (x - x0) / h;
  const m0 = tangent(curve, i);
  const m1 = tangent(curve, i + 1);
  const t2 = t * t;
  const t3 = t2 * t;
  return (
    (2 * t3 - 3 * t2 + 1) * y0 +
    (t3 - 2 * t2 + t) * h * m0 +
    (-2 * t3 + 3 * t2) * y1 +
    (t3 - t2) * h * m1
  );
}

function slope(curve: Curve, i: number) {
  return (curve[i + 1][1] - curve[i][1]) / (curve[i + 1][0] - curve[i][0]);
}

function tangent(curve: Curve, i: number) {
  const n = curve.length;
  if (i === 0) return slope(curve, 0);
  if (i === n - 1) return slope(curve, n - 2);
  const a = slope(curve, i - 1);
  const b = slope(curve, i);
  if (a * b <= 0) return 0;
  // Harmonic mean keeps the curve monotone between keys.
  return (2 * a * b) / (a + b);
}

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

export const smoothstep = (a: number, b: number, v: number) => {
  const t = clamp01((v - a) / (b - a));
  return t * t * (3 - 2 * t);
};
