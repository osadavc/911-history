"""Seat the lofted wing on a flat headlamp (helper for stops 11–14).

The renderer (src/lib/car/model.ts placeLamp) seats the flat lens on the OUTERMOST body
hit among nine rays cast along the lamp axis: one through the lens centre and eight on a
circle of radius max|outline| + ring around it. Any body surface inside that circle that
rises above the lens plane pushes the whole lamp out along its axis. Real lamp covers are
flush with the wing, so over the lamp's length the section is made to lie on the lens
plane: P4 (belt) on the lamp's inner side — extended inboard to the probe circle — and
P3 (crest) on its outer edge, both a few mm under the plane. Optionally the lid centre
(topY / roofY) is capped just above the inner edge (996: lid lower than the wings); the
997's domed lid is left alone (cap_top=False).

Only data already traced for the lamp is used (its centre, pitch, yaw and outline).
"""
import math

import numpy as np


def basis(pitch_deg, yaw_deg):
    """Renderer lens basis in car coords (x rearward, y up, z outboard): U (outline u), V (outline v), N (axis)."""
    p, w = math.radians(pitch_deg), math.radians(yaw_deg)
    U = np.array([-math.sin(w), 0.0, -math.cos(w)])
    V = np.array([math.sin(p) * math.cos(w), math.cos(p), -math.sin(p) * math.sin(w)])
    N = np.array([-math.cos(w) * math.cos(p), math.sin(p), math.sin(w) * math.cos(p)])
    return U, V, N


def outline_3d(headlight):
    """Lamp outline in car coordinates as the renderer would place it on a flush surface."""
    U, V, _ = basis(headlight["pitch"], headlight["yaw"])
    c = np.array(headlight["centre"], float)
    return np.array([c + u * U + v * V for u, v in headlight["outline"]])


def plane_y(headlight, x, z):
    """Height of the lens plane at (x, z)."""
    _, _, N = basis(headlight["pitch"], headlight["yaw"])
    c = np.array(headlight["centre"], float)
    return float(c[1] - (N[0] * (x - c[0]) + N[2] * (z - c[2])) / N[1])


def probe_radius(headlight):
    return max(math.hypot(u, v) for u, v in headlight["outline"]) + headlight.get("ring", 0.0)


def chord(poly3, x):
    """Where the plane x = const cuts the closed lamp outline: (z_in, y_in, z_out, y_out) or None."""
    hits = []
    n = len(poly3)
    for i in range(n):
        a, b = poly3[i], poly3[(i + 1) % n]
        if (a[0] - x) * (b[0] - x) <= 0 and a[0] != b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            hits.append(a + t * (b - a))
    if len(hits) < 2:
        return None
    hits.sort(key=lambda q: q[2])
    return hits[0][2], hits[0][1], hits[-1][2], hits[-1][1]


def _splice(curve, x0, x1, keys):
    """Replace the keys of a [[x, v]] curve inside [x0, x1] by `keys` (sorted)."""
    out = [p for p in curve if p[0] < x0 or p[0] > x1] + [list(k) for k in keys]
    out.sort(key=lambda p: p[0])
    return [[round(float(x), 4), round(float(v), 4)] for x, v in out]


def seat(body, headlight, sink=0.004, crown=0.012, n=11, margin=0.15, inboard=0.0, full=False,
         cap_top=True, ends=0.0):
    """Modify body curves in place so the section lies on the lens plane over the lamp.

    margin  — fraction of the lamp length trimmed at each tip (ignored when full=True)
    full    — cover the lamp's whole x-range (+ `ends` m beyond each tip); where the outline
              chord is short, P3/P4 keep the chord's end z but take the plane's height
    inboard — extra inboard offset (m, in z) of P4 beyond the lamp's inner edge, so the
              probe circle's inner rays also land on the plane
    cap_top — keep the lid centre (topY/roofY) just above the lamp's inner edge"""
    poly = outline_3d(headlight)
    xa, xb = poly[:, 0].min(), poly[:, 0].max()
    if full:
        x0, x1 = xa - ends, xb + ends
    else:
        x0, x1 = xa + margin * (xb - xa), xb - margin * (xb - xa)
    xs = np.linspace(x0, x1, n)
    zc = float(headlight["centre"][2])
    crest_y, crest_z, belt_y, belt_z, top_cap = [], [], [], [], []
    last = None
    for x in xs:
        c = chord(poly, float(np.clip(x, xa + 1e-4, xb - 1e-4)))
        if c is None:
            if last is None:
                continue
            c = last
        last = c
        z_in, _, z_out, _ = c
        z4 = max(z_in - inboard, 0.02)
        crest_y.append((x, plane_y(headlight, x, z_out) - sink))
        crest_z.append((x, z_out))
        belt_y.append((x, plane_y(headlight, x, z4) - sink))
        belt_z.append((x, z4))
        top_cap.append((x, plane_y(headlight, x, z4) + crown))
    body["crestY"] = _splice(body["crestY"], x0 - 1e-4, x1 + 1e-4, crest_y)
    body["crestZ"] = _splice(body["crestZ"], x0 - 1e-4, x1 + 1e-4, crest_z)
    body["beltY"] = _splice(body["beltY"], x0 - 1e-4, x1 + 1e-4, belt_y)
    body["beltZ"] = _splice(body["beltZ"], x0 - 1e-4, x1 + 1e-4, belt_z)

    if cap_top:
        def cap(curve, dy):
            xs_c = [p[0] for p in curve]
            vs_c = [p[1] for p in curve]
            keys = []
            for x, ycap in top_cap:
                v = float(np.interp(x, xs_c, vs_c))
                keys.append((x, min(v, ycap + dy)))
            return _splice(curve, x0 - 1e-4, x1 + 1e-4, keys)

        body["topY"] = cap(body["topY"], 0.0)
        body["roofY"] = cap(body["roofY"], -0.004)
    return (float(x0), float(x1))


def placement(body, headlight, half_section):
    """Replicates model.ts placeLamp (nine probes, outermost hit) on the section loft.
    Returns (push along the axis in m, per-probe depths)."""
    import cv2

    U, V, N = basis(headlight["pitch"], headlight["yaw"])
    c = np.array(headlight["centre"], float)
    r = probe_radius(headlight)

    def inside(q):
        sec = np.array(half_section(body, float(q[0])), np.float32)
        ring = np.concatenate([sec, sec[::-1] * np.array([-1, 1], np.float32)])
        return cv2.pointPolygonTest(ring.reshape(-1, 1, 2), (float(q[2]), float(q[1])), False) >= 0

    depths = []
    probes = [(0.0, 0.0)] + [(math.cos(k / 8 * 2 * math.pi) * r, math.sin(k / 8 * 2 * math.pi) * r) for k in range(8)]
    for pu, pv in probes:
        start = c + pu * U + pv * V + 0.5 * N
        d = None
        for t in np.arange(0.0, 1.2, 0.002):
            q = start - t * N
            if 0 <= q[0] and inside(q):
                d = 0.5 - t
                break
        depths.append(d)
    valid = [d for d in depths if d is not None]
    push = (max(valid) + 0.003) if valid else 0.0
    return push, depths
