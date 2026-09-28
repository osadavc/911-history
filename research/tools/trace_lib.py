"""Helpers for turning reference photos / blueprints into car-space geometry.

Car space: x = metres from the front tip rearwards, y = metres above ground,
z = metres from the centre line (right half). Images use pixel coordinates
(x right, y down).
"""
import json
import math

import cv2
import numpy as np


# ---------------------------------------------------------------- calibration

class SideCalib:
    """Similarity transform for a side view, anchored on both wheel centres.

    wheel_f / wheel_r: pixel centres of the front and rear wheels.
    wheelbase: metres. axle_height: metres (tyre radius) of the front axle.
    tip_f: pixel x of the front tip (for the x origin).
    Works for cars facing either way; "up" is always image-up.
    """

    def __init__(self, wheel_f, wheel_r, wheelbase, axle_height, tip_f):
        self.f = np.array(wheel_f, float)
        self.r = np.array(wheel_r, float)
        d = self.r - self.f
        self.scale = wheelbase / np.linalg.norm(d)  # metres per pixel
        self.u = d / np.linalg.norm(d)  # towards the rear
        n = np.array([self.u[1], -self.u[0]])
        self.n = n if n[1] < 0 else -n  # image-up
        self.axle_height = axle_height
        self.front_axle = -float(np.dot(np.array([tip_f, self.f[1]]) - self.f, self.u)) * self.scale

    def to_car(self, p):
        """pixel -> (x from front tip, y above ground)."""
        q = np.asarray(p, float) - self.f
        return (
            self.front_axle + float(np.dot(q, self.u)) * self.scale,
            self.axle_height + float(np.dot(q, self.n)) * self.scale,
        )

    def to_px(self, x, y):
        a = (x - self.front_axle) / self.scale
        b = (y - self.axle_height) / self.scale
        p = self.f + a * self.u + b * self.n
        return (float(p[0]), float(p[1]))


class FrontCalib:
    """Front / rear view: centre line, ground line and a known width."""

    def __init__(self, centre_x, ground_y, left_px, right_px, width_m):
        self.cx = centre_x
        self.gy = ground_y
        self.scale = width_m / abs(right_px - left_px)

    def to_car(self, p):
        """pixel -> (z from centre line, y above ground). z is signed (image right = +)."""
        return ((p[0] - self.cx) * self.scale, (self.gy - p[1]) * self.scale)

    def to_px(self, z, y):
        return (self.cx + z / self.scale, self.gy - y / self.scale)


class TopCalib:
    """Top view: front tip / rear tip x (pixels) and the centre line y."""

    def __init__(self, tip_f_x, tip_r_x, centre_y, length_m):
        self.tf = tip_f_x
        self.dir = 1.0 if tip_r_x > tip_f_x else -1.0
        self.cy = centre_y
        self.scale = length_m / abs(tip_r_x - tip_f_x)

    def to_car(self, p):
        return ((p[0] - self.tf) * self.dir * self.scale, abs(p[1] - self.cy) * self.scale)

    def to_px(self, x, z, side=1):
        return (self.tf + x / self.scale * self.dir, self.cy - side * z / self.scale)


# ---------------------------------------------------------------- silhouettes

def silhouette_from_drawing(gray, roi=None, close=3, thresh=150):
    """Solid silhouette of a line drawing: everything not reachable from the border."""
    img = gray if roi is None else gray[roi[1]:roi[3], roi[0]:roi[2]]
    lines = (img < thresh).astype(np.uint8) * 255
    if close:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close))
        lines = cv2.dilate(lines, k)
    h, w = lines.shape
    flood = lines.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    for x in range(w):
        for y in (0, h - 1):
            if flood[y, x] == 0:
                cv2.floodFill(flood, mask, (x, y), 128)
    for y in range(h):
        for x in (0, w - 1):
            if flood[y, x] == 0:
                cv2.floodFill(flood, mask, (x, y), 128)
    sil = (flood != 128).astype(np.uint8) * 255
    if roi is not None:
        full = np.zeros_like(gray, dtype=np.uint8)
        full[roi[1]:roi[3], roi[0]:roi[2]] = sil
        sil = full
    return sil


def silhouette_grabcut(bgr, rect, iters=6):
    mask = np.zeros(bgr.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    x0, y0, x1, y1 = rect
    cv2.grabCut(bgr, mask, (x0, y0, x1 - x0, y1 - y0), bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        m = np.where(lab == k, 255, 0).astype(np.uint8)
    return m


def column_profile(mask):
    """{x: (top_y, bottom_y)} for every column containing silhouette pixels."""
    out = {}
    cols = np.nonzero(mask.any(axis=0))[0]
    for x in cols:
        ys = np.nonzero(mask[:, x])[0]
        out[int(x)] = (int(ys[0]), int(ys[-1]))
    return out


def row_profile(mask):
    """{y: (left_x, right_x)} for every row containing silhouette pixels."""
    out = {}
    rows = np.nonzero(mask.any(axis=1))[0]
    for y in rows:
        xs = np.nonzero(mask[y, :])[0]
        out[int(y)] = (int(xs[0]), int(xs[-1]))
    return out


# ---------------------------------------------------------------- curves

def to_curve(points, step=0.04, lo=None, hi=None):
    """Sort (x, v) pairs by x, average duplicates into bins, return [[x, v], ...]."""
    pts = sorted(points)
    if not pts:
        return []
    lo = pts[0][0] if lo is None else lo
    hi = pts[-1][0] if hi is None else hi
    bins = {}
    for x, v in pts:
        if x < lo - 1e-9 or x > hi + 1e-9:
            continue
        k = round((x - lo) / step)
        bins.setdefault(k, []).append(v)
    return [[round(lo + k * step, 4), round(float(np.mean(v)), 4)] for k, v in sorted(bins.items())]


def interp(curve, x):
    xs = [p[0] for p in curve]
    vs = [p[1] for p in curve]
    return float(np.interp(x, xs, vs))


def simplify(curve, tol=0.004):
    """Douglas-Peucker on a [[x, v]] curve (keeps end points)."""
    if len(curve) < 3:
        return curve
    pts = np.array(curve, float)

    def rec(a, b):
        p, q = pts[a], pts[b]
        seg = q - p
        n = np.linalg.norm(seg) or 1.0
        best, idx = 0.0, -1
        for i in range(a + 1, b):
            v = pts[i] - p
            d = abs(seg[0] * v[1] - seg[1] * v[0]) / n
            if d > best:
                best, idx = d, i
        if best > tol:
            return rec(a, idx)[:-1] + rec(idx, b)
        return [a, b]

    keep = rec(0, len(pts) - 1)
    return [[round(float(pts[i][0]), 4), round(float(pts[i][1]), 4)] for i in keep]


def dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


# ---------------------------------------------------------------- loft replica
# Mirrors src/lib/car/body.ts so traced bodies can be checked against photos.

SEGMENTS = [5, 7, 6, 5, 9, 9]
KEYS = ["floorY", "rockerY", "rockerZ", "sideY", "sideZ", "crestY", "crestZ", "beltY", "beltZ", "roofY", "roofZ", "topY"]


def mono(curve, x):
    """Monotone cubic sample, same as curve.ts."""
    n = len(curve)
    if n == 1 or x <= curve[0][0]:
        return curve[0][1]
    if x >= curve[-1][0]:
        return curve[-1][1]
    i = 0
    while i < n - 2 and x > curve[i + 1][0]:
        i += 1

    def slope(k):
        return (curve[k + 1][1] - curve[k][1]) / (curve[k + 1][0] - curve[k][0])

    def tangent(k):
        if k == 0:
            return slope(0)
        if k == n - 1:
            return slope(n - 2)
        a, b = slope(k - 1), slope(k)
        if a * b <= 0:
            return 0.0
        return 2 * a * b / (a + b)

    x0, y0 = curve[i]
    x1, y1 = curve[i + 1]
    h = x1 - x0
    t = (x - x0) / h
    m0, m1 = tangent(i), tangent(i + 1)
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * y0 + (t3 - 2 * t2 + t) * h * m0 + (-2 * t3 + 3 * t2) * y1 + (t3 - t2) * h * m1


def _catmull(p0, p1, p2, p3, t):
    def d(a, b):
        return max(1e-5, math.hypot(b[0] - a[0], b[1] - a[1]) ** 0.5)

    t0 = 0.0
    t1 = t0 + d(p0, p1)
    t2 = t1 + d(p1, p2)
    t3 = t2 + d(p2, p3)
    tt = t1 + (t2 - t1) * t

    def lp(a, b, ta, tb):
        k = (tt - ta) / (tb - ta)
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)

    a1, a2, a3 = lp(p0, p1, t0, t1), lp(p1, p2, t1, t2), lp(p2, p3, t2, t3)
    b1, b2 = lp(a1, a2, t0, t2), lp(a2, a3, t1, t3)
    return lp(b1, b2, t1, t2)


def half_section(body, x):
    s = lambda k: mono(body[k], x)
    pts = [
        (0.0, s("floorY")),
        (s("rockerZ"), s("rockerY")),
        (s("sideZ"), s("sideY")),
        (s("crestZ"), s("crestY")),
        (s("beltZ"), s("beltY")),
        (s("roofZ"), s("roofY")),
        (0.0, s("topY")),
    ]
    ext = [(-pts[1][0], pts[1][1])] + pts + [(-pts[5][0], pts[5][1])]
    out = []
    for seg in range(6):
        n = SEGMENTS[seg]
        for k in range(n):
            out.append(_catmull(ext[seg], ext[seg + 1], ext[seg + 2], ext[seg + 3], k / n))
    out.append((0.0, pts[6][1]))
    return out


def front_silhouette(body, length, samples=120):
    """Outer half-outline seen from the front/rear: for each height, the max |z| over all x."""
    pts = []
    for i in range(samples + 1):
        x = length * i / samples
        pts.extend(half_section(body, x))
    arr = np.array(pts)
    ys = np.linspace(arr[:, 1].min(), arr[:, 1].max(), 80)
    out = []
    for y in ys:
        sel = arr[np.abs(arr[:, 1] - y) < 0.012]
        if len(sel):
            out.append((float(sel[:, 0].max()), float(y)))
    return out
