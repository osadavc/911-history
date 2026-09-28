"""Perspective check of a traced car against a real side photo (helper for stops 11–14).

A flat (hub-calibrated) overlay makes centre-line features look a few % too high/long
because they are farther from the camera than the near-side hubs. Here the lofted body
(the same section model as src/lib/car/body.ts, via trace_lib.half_section) and the
tyres are projected through a pinhole camera looking square-on at the car:

  * the two near-side hub centres measured in the photo pin the scale, the roll and the
    camera's position along the car (principal point = image centre column);
  * the camera distance D and height Yc are found by a small grid search that
    maximises the overlap (IoU) of the projected car with a GrabCut mask of the photo.

Outputs an overlay PNG (photo + projected silhouette, arch/belt/roof lines, side
decals, tyre outlines) and returns the fit statistics. Nothing here feeds back into
the trace: it only checks it.

usage (from a trace script):
    spec = importlib.util.spec_from_file_location("pf", ".../11-996-1-1998.photofit.py")
    pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
    pf.check(car, photo_path, hub_front, hub_rear, rect, out_png, facing="left")
"""
import math
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from trace_lib import half_section, mono, silhouette_grabcut  # noqa: E402


def _loft(car, n=260):
    L = car["length"]
    xs = [L * (0.5 - 0.5 * math.cos(math.pi * i / (n - 1))) for i in range(n)]
    rings = []
    for x in xs:
        sec = half_section(car["body"], x)
        rings.append([(x, y, z) for z, y in sec])
    return xs, rings


def _tyres(car, near_sign):
    out = []
    for axle, key, track in ((car["frontAxle"], "front", car["trackFront"]),
                             (car["rearAxle"], "rear", car["trackRear"])):
        w = car["wheels"][key]
        r = w["diameter"] / 2
        for side in (1, -1):
            zc = side * track / 2
            faces = []
            for zf in (zc - w["width"] / 2, zc + w["width"] / 2):
                faces.append([(axle + r * math.cos(a), r + r * math.sin(a), zf)
                              for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)])
            out.append((side == near_sign, faces, (axle, r, zc + near_sign * w["width"] / 2), w["rim"] / 2))
    return out


class Camera:
    def __init__(self, car, hub_f, hub_r, img_w, D, Yc, facing, hub_height=None, u0=None):
        self.facing = facing                      # "left": car's left side faces the camera (nose left)
        self.s = -1.0 if facing == "left" else 1.0  # sign of the camera's z
        near_z = self.s * car["trackFront"] / 2   # near-side wheel plane
        wb = car["rearAxle"] - car["frontAxle"]
        hf, hr = np.array(hub_f, float), np.array(hub_r, float)
        d = hr - hf
        # The hub line is not level when the rear tyre is taller: remove that slope from the roll.
        dr = (car["wheels"]["rear"]["diameter"] - car["wheels"]["front"]["diameter"]) / 2
        if facing == "left":
            self.roll = math.atan2(d[1], d[0]) - math.atan2(-dr, wb)
        else:
            self.roll = math.atan2(-d[1], -d[0]) - math.atan2(dr, wb)
        k = np.linalg.norm(d) / math.hypot(wb, dr)  # px per metre at the near-wheel plane
        self.D = D
        self.f = k * D
        self.u0 = img_w / 2 if u0 is None else u0   # principal point (image centre unless cropped)
        self.cz = near_z + self.s * D
        # Along-car camera position from the front hub (principal point = image centre).
        uf = self._unroll(hf, None)
        dirx = 1.0 if facing == "left" else -1.0  # image-right is car +x for a left-side view
        self.cx = car["frontAxle"] - dirx * (uf[0] - self.u0) / k
        self.cy = Yc
        # Front hub height above the ground: the free tyre radius unless the loaded radius
        # was measured in the photo (hub-to-contact distance).
        r = car["wheels"]["front"]["diameter"] / 2 if hub_height is None else hub_height
        self.v0 = uf[1] + k * (r - Yc)
        self.hub = hf

    def _unroll(self, p, centre):
        return np.array(p, float)  # roll applied in project(); hubs define the frame

    def backproject(self, U, V, z):
        """Image point → car (x, y) on the plane at car z (signed)."""
        c, s = math.cos(-self.roll), math.sin(-self.roll)
        du, dv = U - self.hub[0], V - self.hub[1]
        u, v = self.hub[0] + c * du - s * dv, self.hub[1] + s * du + c * dv
        depth = self.s * (self.cz - z)
        dirx = 1.0 if self.facing == "left" else -1.0
        return self.cx + (u - self.u0) * depth / (self.f * dirx), self.cy - (v - self.v0) * depth / self.f

    def project(self, pts):
        pts = np.asarray(pts, float)
        depth = self.s * (self.cz - pts[:, 2])          # distance in front of the camera
        dirx = 1.0 if self.facing == "left" else -1.0
        u = self.u0 + self.f * dirx * (pts[:, 0] - self.cx) / depth
        v = self.v0 - self.f * (pts[:, 1] - self.cy) / depth
        # roll about the front hub
        c, s = math.cos(self.roll), math.sin(self.roll)
        du, dv = u - self.hub[0], v - self.hub[1]
        return np.stack([self.hub[0] + c * du - s * dv, self.hub[1] + s * du + c * dv], 1)


def _mask(car, cam, shape, rings, tyres):
    m = np.zeros(shape[:2], np.uint8)
    for side in (1, -1):
        prev = None
        for ring in rings:
            p = cam.project([(x, y, side * z) for x, y, z in ring])
            if prev is not None:
                for j in range(len(p) - 1):
                    quad = np.array([prev[j], prev[j + 1], p[j + 1], p[j]], np.int32)
                    cv2.fillConvexPoly(m, quad, 255)
            prev = p
    for _, faces, _, _ in tyres:
        a, b = cam.project(faces[0]), cam.project(faces[1])
        cv2.fillPoly(m, [a.astype(np.int32)], 255)
        cv2.fillPoly(m, [b.astype(np.int32)], 255)
        for j in range(len(a)):
            k = (j + 1) % len(a)
            cv2.fillConvexPoly(m, np.array([a[j], a[k], b[k], b[j]], np.int32), 255)
    return m


def _surface_z(car, x, y):
    """Near-side body surface z at (x, y) (outer part of the section, P1..P5)."""
    sec = half_section(car["body"], x)
    best = None
    for (z0, y0), (z1, y1) in zip(sec[5:-9], sec[6:-8]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            z = z0 + (z1 - z0) * (y - y0) / (y1 - y0)
            best = z if best is None else max(best, z)
    if best is None:
        best = max(z for z, _ in sec)
    return best


def surface_point(cam, car, U, V, near_sign, z0=0.8, iters=5):
    """Back-project an image point onto the lofted body's near-side surface → (x, y, z)."""
    z = z0
    for _ in range(iters):
        x, y = cam.backproject(U, V, near_sign * z)
        x = min(max(x, 0.0), car["length"])
        z = _surface_z(car, x, y)
    x, y = cam.backproject(U, V, near_sign * z)
    return x, y, z


def fit_camera(car, photo, hub_f, hub_r, rect, facing="left", ground_row=None,
               D_grid=(6, 8, 10, 13, 16, 20, 25, 32, 40, 55), Y_grid=None, ends=None, mask=None,
               hub_height=None, U0_grid=(None,)):
    """Grid-search the camera distance D and height Yc (hubs pinned). Returns
    (cam, iou, D, Yc, model_mask, photo_mask, img)."""
    img = cv2.imread(photo)
    H, W = img.shape[:2]
    photo_mask = silhouette_grabcut(img, rect) if mask is None else mask
    if ground_row is not None:
        photo_mask[int(ground_row):, :] = 0
    xs, rings = _loft(car)
    near_sign = -1 if facing == "left" else 1
    tyres = _tyres(car, near_sign)
    Y_grid = Y_grid or [0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2]
    best = None
    for D, Yc, u0 in [(a, b, c) for a in D_grid for b in Y_grid for c in U0_grid]:
        if True:
            cam = Camera(car, hub_f, hub_r, W, D, Yc, facing, hub_height, u0)
            m = _mask(car, cam, img.shape, rings, tyres)
            if ground_row is not None:
                m[int(ground_row):, :] = 0
            inter = np.logical_and(m > 0, photo_mask > 0).sum()
            union = np.logical_or(m > 0, photo_mask > 0).sum()
            iou = inter / max(union, 1)
            score = iou
            if ends is not None:
                cols_m = np.nonzero(m.any(0))[0]
                fm, rm = (cols_m[0], cols_m[-1]) if facing == "left" else (cols_m[-1], cols_m[0])
                score -= 0.004 * (abs(fm - ends[0]) + abs(rm - ends[1]))
            if best is None or score > best[5]:
                best = (iou, D, Yc, cam, m, score)
    iou, D, Yc, cam, m, _ = best
    return cam, iou, D, Yc, m, photo_mask, img


def check(car, photo, hub_f, hub_r, rect, out_png, facing="left", ground_row=None,
          D_grid=(6, 8, 10, 13, 16, 20, 25, 32, 40, 55), Y_grid=None, ends=None, mask=None, hub_height=None,
          fit=None, U0_grid=(None,)):
    """ends: optional hand-read (front, rear) image x of the car's extremes; when given the
    fit score also penalises end mismatch (0.004 IoU per px), for photos whose GrabCut mask
    is unreliable (car colour close to the background). mask: optional precomputed photo
    silhouette (e.g. a colour mask) instead of GrabCut."""
    if fit is None:
        fit = fit_camera(car, photo, hub_f, hub_r, rect, facing, ground_row, D_grid, Y_grid, ends, mask, hub_height,
                         U0_grid)
    cam, iou, D, Yc, m, photo_mask, img = fit
    H, W = img.shape[:2]
    near_sign = -1 if facing == "left" else 1
    tyres = _tyres(car, near_sign)

    # Per-column top/bottom differences (model − photo), in px and mm at the near plane.
    k = cam.f / cam.D
    cols = [c for c in range(W) if m[:, c].any() and photo_mask[:, c].any()]
    d_top = [int(np.nonzero(m[:, c])[0][0]) - int(np.nonzero(photo_mask[:, c])[0][0]) for c in cols]
    d_bot = [int(np.nonzero(m[:, c])[0][-1]) - int(np.nonzero(photo_mask[:, c])[0][-1]) for c in cols]
    pm_cols = np.nonzero(photo_mask.any(0))[0]
    mm_cols = np.nonzero(m.any(0))[0]
    stats = {
        "iou": round(float(iou), 4), "D": D, "Yc": Yc, "u0": round(float(cam.u0), 1), "px_per_m": round(k, 2),
        "top_median_mm": round(float(np.median(d_top)) / k * 1000, 1) if cols else None,
        "top_p90_mm": round(float(np.percentile(np.abs(d_top), 90)) / k * 1000, 1) if cols else None,
        "front_end_px": [int(mm_cols[0]), int(pm_cols[0])] if facing == "left" else [int(mm_cols[-1]), int(pm_cols[-1])],
        "rear_end_px": [int(mm_cols[-1]), int(pm_cols[-1])] if facing == "left" else [int(mm_cols[0]), int(pm_cols[0])],
    }

    # Overlay.
    vis = cv2.addWeighted(img, 0.75, np.full_like(img, 255), 0.25, 0)
    cnt, _ = cv2.findContours(photo_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, cnt, -1, (0, 200, 255), 1)       # photo mask (amber)
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, cnt, -1, (60, 40, 255), 2)       # projected model (red)
    body = car["body"]
    L = car["length"]
    lx = np.linspace(0, L, 200)

    def poly(pts3, col, th=1):
        p = cam.project(pts3).astype(np.int32)
        cv2.polylines(vis, [p], False, col, th, cv2.LINE_AA)

    poly([(x, mono(body["rockerY"], x), near_sign * mono(body["rockerZ"], x)) for x in lx], (0, 150, 255), 2)
    poly([(x, mono(body["beltY"], x), near_sign * mono(body["beltZ"], x)) for x in lx], (255, 120, 0))
    poly([(x, mono(body["roofY"], x), near_sign * mono(body["roofZ"], x)) for x in lx], (220, 60, 170))
    poly([(x, mono(body["crestY"], x), near_sign * mono(body["crestZ"], x)) for x in lx], (80, 200, 60))
    for d in car["decals"]:
        if d["plane"] != "side":
            continue
        if d.get("side") == "right" and facing == "left":
            continue
        if d.get("side") == "left" and facing != "left":
            continue
        p3 = [(x, y, near_sign * _surface_z(car, x, y)) for x, y in d["points"]]
        if d["kind"] != "line":
            p3.append(p3[0])
        poly(p3, (0, 230, 230))
    for near, faces, (ax, r, zf), rim in tyres:
        if not near:
            continue
        poly(faces[0 if facing == "left" else 1] + [faces[0 if facing == "left" else 1][0]], (200, 200, 0), 1)
        rimc = [(ax + rim * math.cos(a), r + rim * math.sin(a), zf) for a in np.linspace(0, 2 * math.pi, 40)]
        poly(rimc, (200, 200, 0), 1)
    x0, y0, x1, y1 = rect
    pad = 30
    crop = vis[max(0, y0 - pad):min(H, y1 + pad), max(0, x0 - pad):min(W, x1 + pad)]
    txt = f"IoU {stats['iou']:.3f}  D {D} m  cam h {Yc} m  u0 {cam.u0:.0f}  red=model amber=photo"
    cv2.putText(crop, txt, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(crop, txt, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out_png, crop)
    return stats
