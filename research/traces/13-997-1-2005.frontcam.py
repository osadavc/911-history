"""Straight-on front (or rear) photo → car coordinates (helper for stops 13–14).

A pinhole camera looking along the car's axis, fitted from features of known position:
  * two symmetric features at one depth (e.g. the headlamp centres: x_a, ±z_a),
  * two symmetric features at a second depth (e.g. the front tyres' outer edges: x_b, ±z_b),
  * one feature of known height at each depth (lamp centre height, tyre contact y = 0).
Horizontal:  u = u0 ± f z / (D + x)          → f, D, u0
Vertical:    v = v_off + f (hc − y) / (D + x)  → hc, v_off  (v_off absorbs a small pitch)
Image points on the body are back-projected at their own depth: the body surface depth x
for a given lateral z comes from the plan outline (x where the plan half-width equals z),
iterated because z itself depends on the depth.
"""
import numpy as np


class FrontCam:
    def __init__(self, ua, za, xa, ub, zb, xb, va, ya, vb, yb):
        """ua/ub: (u_left, u_right) image columns of the symmetric pairs; va/vb: rows of the
        height references (ya at depth xa, yb at depth xb)."""
        ka = (ua[1] - ua[0]) / (2 * za)       # f / (D + xa)
        kb = (ub[1] - ub[0]) / (2 * zb)       # f / (D + xb)
        # ka (D + xa) = kb (D + xb)
        self.D = (kb * xb - ka * xa) / (ka - kb)
        self.f = ka * (self.D + xa)
        self.u0 = (ua[0] + ua[1] + ub[0] + ub[1]) / 4
        # vertical: va - vb = f[(hc - ya)/(D+xa) - (hc - yb)/(D+xb)]
        A = self.f / (self.D + xa) - self.f / (self.D + xb)
        B = -self.f * ya / (self.D + xa) + self.f * yb / (self.D + xb)
        self.hc = (va - vb - B) / A
        self.v_off = va - self.f * (self.hc - ya) / (self.D + xa)

    def project(self, x, y, z):
        s = self.f / (self.D + x)
        return self.u0 + s * z, self.v_off + s * (self.hc - y)

    def back(self, u, v, depth, iters=10):
        """Image (u, v) → (z signed image-right positive, y, x) on a surface of depth x(z, y)."""
        x = 0.2
        for _ in range(iters):
            s = self.f / (self.D + x)
            z = (u - self.u0) / s
            y = self.hc - (v - self.v_off) / s
            x = depth(abs(z), y)
        s = self.f / (self.D + x)
        return (u - self.u0) / s, self.hc - (v - self.v_off) / s, x


def section_depth(body, half_section, x_max=1.2, step=0.004):
    """Depth (x from the front tip) of the lofted body surface at lateral |z| and height y:
    the first station whose section reaches out to z at that height."""
    xs = np.arange(0.0, x_max, step)
    reach = []
    for x in xs:
        sec = half_section(body, float(x))
        reach.append(sec)

    def zmax_at(sec, y):
        best = 0.0
        for (z0, y0), (z1, y1) in zip(sec[:-1], sec[1:]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                best = max(best, z0 + (z1 - z0) * (y - y0) / (y1 - y0))
        return best

    def f(z, y):
        for x, sec in zip(xs, reach):
            if zmax_at(sec, y) >= z:
                return float(x)
        return float(xs[-1])

    return f


def plan_depth(half_width_curve, x_max=0.9):
    """Depth (x from the tip) of the body surface at lateral |z|, from the plan outline
    [[x, half-width], ...] (front end: half-width increasing with x)."""
    xs = np.array([p[0] for p in half_width_curve])
    zs = np.array([p[1] for p in half_width_curve])
    sel = xs <= x_max
    xs, zs = xs[sel], np.maximum.accumulate(zs[sel])

    def f(z):
        return float(np.interp(z, zs, xs))

    return f


def order_front(poly):
    """Closed outline in the front/rear plane (z ≥ 0 right, y up) → the convention used by
    every stop: start at the inner-bottom corner, up the inner side, outward along the top,
    down the outer side, back along the bottom (clockwise in z-right / y-up)."""
    p = [list(v) for v in poly]
    area = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))
    if area > 0:
        p.reverse()
    zs = [v[0] for v in p]
    ys = [v[1] for v in p]
    sz, sy = (max(zs) - min(zs)) or 1, (max(ys) - min(ys)) or 1
    i0 = min(range(len(p)), key=lambda i: (p[i][0] - min(zs)) / sz + (p[i][1] - min(ys)) / sy)
    return p[i0:] + p[:i0]


def photo_outline(cam, pts, depth, clip_centre=True):
    """Image outline (image-left half of the car) → car [z, y], z ≥ 0, in the standard order."""
    out = []
    for u, v in pts:
        z, y, _ = cam.back(u, v, depth)
        out.append([round(max(-z, 0.0) if clip_centre else -z, 4), round(y, 4)])
    return order_front(out)
