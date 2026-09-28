"""Trace: 17-992-1-2019 — 911 Carrera Coupé, type 992 first phase (992.1), MY2020–2024.

Primary reference: the-blueprints.com vector preview "Porsche 911 Carrera 4S 992 (2019)"
(research/blueprints/17-992-1-2019/vec-17529_...4view-dims-watermarked.jpg, 1280 px:
side, plan, front and rear views). All 992 Carreras share this wide body (Porsche: the
rear-drive cars adopt the all-wheel-drive body width), so the C4S drawing is the Carrera
shell; the Carrera specifics (19/20-inch wheels, black louvres, single tailpipes) come
from geometry.json and the photos in research/photos/17-992-1-2019 (P03 official side
profile, P01 side, P11/P12 front, P14 official rear of a base Carrera, P22 official plan).
Porsche's own 992.1 dimension slide is not to scale: only its printed numbers are used
(tyre diameters 671 / 715 mm = the Carrera's 235/40 R19 and 295/35 R20).

Official dimensions (research/specs.json: porsche.com 2020, PCNA 2020 specs):
  L 4,519  W 1,852  H 1,298  WB 2,450  tracks 1,591 / 1,557 mm,
  tyres 235/40 ZR 19 on 8.5J / 295/35 ZR 20 on 11.5J.

--- Calibration --------------------------------------------------------------
VS  side view: hub centres from circle fits to the bright rim lips (F 229.35/272.30,
    R 648.49/269.05 px; the rear hub sits 19 mm higher = the C4S's 20/21-inch tyres)
    -> 419.14 px = 2,450 mm -> 5.8453 mm/px. Outline strokes ~2 px; readings are stroke
    centres. Nose 52.0 / tail 826.0 px -> 4,524 mm at this scale (official 4,519, +0.1 %;
    each overhang is trimmed 2.7 mm, remap_overhangs()). Roof stroke centre y 109.5;
    ground placed at 109.5 + 1.298 m / S = 331.56 (as the 1964 example: official height
    with the uniform scale). The drawn wheels then stand ~1.5 px above that ground; the
    C4S drawing is 9 mm lower than the official C4S height with its own tyres.
VT  plan view: tips 50.5 / 826.5 px (stroke centres) mapped onto the side view's tips;
    across: widest 320 px (stroke centres) = the official 1,852 mm -> 5.7875 mm/px;
    centre row 628.0.
VF  front view: centre 1053.75, body sides 894 / 1213.5 -> 5.797 mm/px across; up: the
    same mm/px, ground from the official height (roof 109.5 -> ground 333.4).
VR  rear view: centre 1054.25, sides 894 / 1214.5 -> 5.778 mm/px; ground 749.1.
Photo P03 (official, true right profile, 1920 px): rim-lip circle fits F 1321.87/974.17,
    R 543.79/979.45 -> 3.149 mm/px at the wheel plane; used for checks and details.

Run: <venv>/bin/python research/traces/17-992-1-2019.py
"""
import importlib.util
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import half_section, mono, simplify  # noqa: E402

_spec = importlib.util.spec_from_file_location("t15", os.path.join(HERE, "15-991-1-2012.py"))
t15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t15)
dedupe, keys = t15.dedupe, t15.keys

STOP = "17-992-1-2019"
VENDOR = os.path.join(ROOT, "research", "blueprints", STOP,
                      "vec-17529_porsche-911-carrera-4s-992-2019_4view-dims-watermarked.jpg")
PHOTO_SIDE = os.path.join(ROOT, "research", "photos", STOP, "03-side-right.jpg")

# ------------------------------------------------------------------ VS calibration
FA_X, FA_Y, RA_X, RA_Y = 229.35, 272.30, 648.49, 269.05
S = 2.450 / (RA_X - FA_X)
TIP_X, TAIL_X = 52.0, 826.0
ROOF_Y = 109.5
GROUND_Y = ROOF_Y + 1.298 / S


def X(px):
    return (px - TIP_X) * S


def Y(py):
    return (GROUND_Y - py) * S


# ------------------------------------------------------------------ VT / VF / VR calibration
VT_TIP, VT_TAIL, VT_CY = 50.5, 826.5, 628.0
VT_SZ = 0.926 / 160.0


def XT(px):
    """Plan x px -> car x (before the overhang trim), tips mapped onto the side view's."""
    return (px - VT_TIP) / (VT_TAIL - VT_TIP) * X(TAIL_X)


def ZT(py):
    return abs(VT_CY - py) * VT_SZ


VF_CX, VF_S = 1053.75, 0.926 / 159.75
VF_GROUND = ROOF_Y + 1.298 / VF_S
VR_CX, VR_S = 1054.25, 0.926 / 160.25
VR_GROUND = 524.5 + 1.298 / VR_S


def vf(px, py):
    return [round(abs(px - VF_CX) * VF_S, 3), round((VF_GROUND - py) * VF_S, 3)]


def vr(px, py):
    return [round(abs(px - VR_CX) * VR_S, 3), round((VR_GROUND - py) * VR_S, 3)]


# ================================================================== VS readings (px)
# Lower edge: front lip, arches (outer edge of the drawn wheel wells: ray casts from the
# hubs to the first body-colour pixel, minus 1 px of stroke), sill, rear apron, tail.
FRONT_ARCH_R = {200: 72.2, 190: 69.0, 180: 68.0, 170: 66.0, 160: 66.0, 150: 64.5, 140: 64.0, 130: 63.8,
                120: 63.5, 110: 63.8, 100: 64.0, 90: 63.0, 80: 63.0, 70: 62.8, 60: 63.5, 50: 62.5, 40: 63.5,
                30: 63.8, 20: 63.8, 10: 64.2, 0: 65.2, -10: 68.2, -20: 71.5}
REAR_ARCH_R = {200: 74.5, 190: 71.2, 180: 69.0, 170: 69.2, 160: 68.2, 150: 67.2, 140: 66.8, 130: 67.0,
               120: 66.5, 110: 66.8, 100: 65.8, 90: 65.8, 80: 65.8, 70: 66.8, 60: 67.5, 50: 67.2, 40: 67.2,
               30: 67.0, 20: 67.2, 10: 67.2, 0: 68.2, -10: 70.2, -20: 74.8}


def arch_pts(cx, cy, radii):
    out = []
    for deg in sorted(radii, reverse=True):
        a = math.radians(deg)
        r = radii[deg] - 1.0
        out.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return out


BOTTOM = ([(52, 306), (56, 308.5), (100, 308.5), (146, 308.5), (156, 304)]
          + arch_pts(FA_X, FA_Y, FRONT_ARCH_R)
          + [(300, 305), (312, 307.5), (400, 307.5), (500, 307.3), (566, 307), (574, 303)]
          + arch_pts(RA_X, RA_Y, REAR_ARCH_R)
          + [(722, 300), (740, 299), (760, 297.5), (780, 296), (800, 294), (810, 291.5), (816, 289),
             (822, 286), (825, 285), (826, 284)])

# Greenhouse (band centres of the dark frame lines, 4-6x gridded zooms / column maps):
# A-pillar rear edge = front edge of the side-glass frame, from the belt to the roof rail.
A_PILLAR_REAR = [(362, 179), (375, 164), (385, 158), (395, 150.5), (405, 145), (415, 139.5), (425, 135.5),
                 (435, 132.5)]
# Top of the side-glass opening (roof rail), door and quarter window.
DLO_TOP = [(440, 131), (460, 128.5), (480, 127), (500, 128), (520, 129), (530, 131)]
QUARTER_TOP = [(556, 139), (560, 137), (570, 139), (580, 142), (590, 144.5), (600, 147.5), (610, 151),
               (620, 155), (628, 163)]
# Glass base (belt): door glass, then the quarter window's rising base.
BELT = [(362, 180), (405, 179), (430, 179), (460, 177.5), (480, 176.5), (500, 176), (527, 175),
        (556, 170), (580, 168), (600, 166.5), (620, 165.5), (628, 163)]
# Door top / fender crease just below the glass base, from the cowl back to the B-pillar.
DOOR_TOP = [(300, 183.5), (325, 183), (355, 182.5), (400, 182.2), (430, 181.6), (475, 181.2), (520, 180.8),
            (535, 180.0)]
# Rear-window side edge on the C-pillar, continuing as the edge of the raised grille deck.
DECK = [(590, 127), (600, 133), (610, 134.5), (620, 136), (630, 140.5), (640, 143), (652, 146), (664, 149.5),
        (676, 152.5), (688, 156), (700, 159), (706, 160)]
# Dark band under the retracted spoiler's side (x 730-772), down to the light bar.
SPOILER = [(712, 164), (730, 168.5), (742, 168.5), (754, 172.5), (766, 175.5), (772, 176), (784, 181),
           (796, 186), (808, 190)]
# Door outline: front edge x 318-323, rear edge bulging back to x 544 at y 227 (the 992's
# C-shaped shut line; P03 shows the same), bottom y 292.
DOOR = [(345, 181), (330, 187), (322, 200), (318.5, 220), (318.5, 245), (320, 265), (322, 282), (326, 291.5),
        (400, 292), (480, 291.5), (512, 291), (519.5, 283), (519.5, 272), (522.4, 263), (527.5, 251),
        (535, 239), (541, 232), (544, 226), (540, 214), (537, 205), (534, 190), (533, 181)]
# Side glass outlines, lowest-front point first, clockwise (nose left).
DLO_DOOR = [(364, 178), (375, 166.5), (385, 160.5), (395, 153), (405, 147.5), (415, 142), (425, 138),
            (440, 134.5), (460, 131.5), (480, 130.5), (500, 130.5), (520, 132.5), (531, 134), (521, 174.5),
            (480, 175.5), (420, 177.5)]
DLO_QUARTER = [(557, 168.5), (557, 141), (570, 144), (580, 146), (590, 149), (600, 152), (610, 156),
               (620, 160.5), (627, 163), (620, 164.5), (600, 165.5), (580, 167.5)]
# Mirror (side view): housing x 360-402, y 158-176; black base to y 194.
MIRROR = (360, 402, 158, 194)
# Light bar wrapping into the flank, car (x, y). Official profile P03 through the hub similarity
# (rim-lip fits, tyres 245/35 R20 and 305/30 R21, roll -0.82 deg): red line v 851 -> 0.774 m,
# housing v 846-858 -> 0.752-0.789 m, from u 400 (x 3.93 m) to the tail; the vendor side band
# (VS 745-822 x 191-206 px) and rear view (bar rows 613-619 -> 0.769 m) agree.
LIGHT_SIDE_M = [(3.95, 0.762), (3.93, 0.770), (4.10, 0.781), (4.30, 0.788), (4.47, 0.790), (4.50, 0.772),
                (4.47, 0.753), (4.30, 0.754), (4.10, 0.760)]
# Rear face (P14, official straight rear of a base Carrera): EU plate 826.7-1033.9 px = 520 mm
# -> 2.512 mm/px, centre line u 930.3 (plate and tailpipe midpoints agree); heights relative to
# the red bar line (v 557.8), placed at BAR_Y (P03/vendor, above).
BAR_Y, P14_S, P14_BAR_V, P14_CX = 0.772, 0.002512, 557.8, 930.3


def p14(u, v):
    return [round(abs(u - P14_CX) * P14_S, 3), round(BAR_Y - (v - P14_BAR_V) * P14_S, 3)]


def side_silhouette_top():
    """First dark or body-colour pixel from the top (stroke top + 0.5 px = stroke centre),
    watermark spikes removed with a running median."""
    im = cv2.imread(VENDOR).astype(float)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    mx = im.max(axis=2)
    yel = (r + g) / 2 - b
    ink = (mx < 200) | (yel > 90)
    top = {}
    for x in range(52, 827):
        ys = np.nonzero(ink[104:345, x])[0]
        if len(ys):
            top[x] = float(ys[0] + 104) + 0.5
    # Isolated spikes (dimension-line ticks at x 422/582/742, watermark specks): running median.
    xs = sorted(top)
    arr = np.array([top[x] for x in xs])
    for i in range(len(arr)):
        lo, hi = max(0, i - 8), min(len(arr), i + 9)
        med = float(np.median(arr[lo:hi]))
        if abs(arr[i] - med) > 3.0:
            top[xs[i]] = med
    # The watermark text crosses the outline in a few places; those ranges are replaced by
    # stroke-centre readings from the 4-6x gridded zooms / column maps, linearly interpolated.
    for anchors in WATERMARK_FIX:
        ax = [a for a, _ in anchors]
        ay = [b for _, b in anchors]
        for x in range(int(ax[0]), int(ax[-1]) + 1):
            top[x] = float(np.interp(x, ax, ay))
    return top


# Watermark-contaminated stretches of the top outline: (x, stroke-centre y) anchors.
WATERMARK_FIX = [
    [(52, 250.0), (56, 250.0), (60, 246.0), (64, 243.0), (68, 240.0), (76, 235.5), (82, 232.0)],   # nose
    [(125, 212.0), (128, 210.5), (134, 208.5), (140, 204.5), (143, 202.0)],                     # lamp top
    [(174, 191.5), (176, 190.5), (182, 189.5), (188, 189.0), (194, 188.5), (198, 188.5)],       # fender
    [(286, 180.5), (292, 180.0), (296, 178.5), (300, 172.5), (304, 169.0)],                     # cowl/screen
    [(765, 171.5), (772, 175.0), (780, 179.0), (784, 181.5)],                                   # spoiler
    [(812, 193.0), (814, 199.5), (820, 206.0), (824, 212.0), (826, 216.0)],                     # tail
]


def plan_half_width():
    """VT plan outline -> {car x: half-width}. Per column the narrower of the two half-widths
    (the watermark text touches one edge at a time), a running median removes the rest;
    mirrors bridged between 346 and 412 px."""
    im = np.asarray(Image.open(VENDOR).convert("RGB")).astype(int)
    mx, mn = im.max(axis=2), im.min(axis=2)
    car = ((((mx - mn) > 60) | (mx < 185))).astype(np.uint8)
    reg = car[440:830, 30:850].copy()
    h, w = reg.shape
    ff = reg.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 2)
    filled = ff != 2
    xs, hw = [], []
    for x in range(51, 827):
        ys = np.nonzero(filled[:, x - 30])[0]
        if len(ys):
            top, bot = ys[0] + 440 + 1.0, ys[-1] + 440 - 1.0       # stroke centres
            xs.append(x)
            hw.append(min(VT_CY - top, bot - VT_CY))
    hw = np.array(hw)
    out = hw.copy()
    for i in range(len(hw)):
        lo, hi = max(0, i - 6), min(len(hw), i + 7)
        med = float(np.median(hw[lo:hi]))
        if abs(hw[i] - med) > 1.5:
            out[i] = med
    prof = dict(zip(xs, out))
    a, b = 346, 412
    for x in range(a, b + 1):
        prof[x] = prof[a] + (prof[b] - prof[a]) * (x - a) / (b - a)
    return {round(XT(x), 4): v * VT_SZ for x, v in sorted(prof.items())}


# ================================================================== shell
LAMP_TOP_DIP = 0.015   # lid centre under the lamp-top fender bump (m), front-3/4 photos P07/P12
LID_EDGE_DROP = 0.02   # lid shut line under the lid centre (m)


def correct_overshoots(curves, plan, sil, L, cab=(X(300), X(712)), iters=10):
    """The loft passes a Catmull-Rom spline through P0..P6, which bulges past P2 (sideZ) and
    past P3/P5 over the lids. Pull sideZ in so the lofted half-width equals the plan
    half-width, and where the section rises above the side silhouette lower the key that
    causes it: roofY when the highest point lies near the centre line (P5-P6), crestY when
    it lies near the fender crest (P3). The greenhouse (screen base to rear-window end), where
    the rail is a traced line, is left alone."""
    px = sorted(plan)
    pz = [plan[k] for k in px]
    for _ in range(iters):
        sz = []
        for x, z in curves["sideZ"]:
            if 0.02 < x < L - 0.02:
                zmax = max(p[0] for p in half_section(curves, x))
                floor = max(mono(curves["crestZ"], x), mono(curves["rockerZ"], x))
                z = max(floor, z - (zmax - float(np.interp(x, px, pz))))
            sz.append([x, round(z, 4)])
        curves["sideZ"] = sz
        for key in ("roofY", "crestY"):
            new = []
            for x, y in curves[key]:
                if 0.05 < x < L - 0.03 and not cab[0] <= x <= cab[1]:
                    sec = half_section(curves, x)
                    zm, ym = max(sec, key=lambda p: p[1])
                    excess = ym - sil(x)
                    near_centre = zm <= mono(curves["roofZ"], x) + 0.05
                    if excess > 0.0005 and ((key == "roofY") == near_centre):
                        y = y - excess
                new.append([x, round(y, 4)])
            curves[key] = new


def trace_992_shell():
    top_px = side_silhouette_top()
    L = X(TAIL_X)
    xs = sorted(top_px)

    def silY(px):
        return Y(float(np.interp(px, xs, [top_px[k] for k in xs])))

    def sil_car(x):
        return silY(TIP_X + x / S)

    def line(pts, lo=-1e9, hi=1e9):
        return [(X(a), Y(b)) for a, b in pts if lo <= a <= hi]

    # ---- topY: nose face (x 52, y 250 -> lip), silhouette; lamp tops (x 118-175 px) are the
    # fender, the lid centre runs LAMP_TOP_DIP lower there. Tail face to y 222 at x 826.
    nose = [(0.0, Y(250)), (X(56), silY(56))]
    front = []
    for x in range(62, 232, 8):
        t = min(1.0, abs(x - 160) / 70)
        front.append((X(x), silY(x) - LAMP_TOP_DIP * (1 - t * t)))
    body_top = [(X(x), silY(x)) for x in range(236, 812, 5)]
    # Tail face: vertical at x 823-827 px from y 216 (spoiler trailing edge) to 284 (VS rows).
    tail = [(X(814), Y(199.5)), (X(820), Y(206)), (X(824), Y(212)), (L, Y(216))]
    top_y = dedupe(nose + front + body_top + tail)

    # ---- crestY / crestZ: fender top over the lamp and to the cowl (silhouette), the door
    # top crease (DOOR_TOP) 1.5 cm lower in the cabin as the door shoulder, rear hip crest
    # (rear view: shoulder z 0.85-0.88 at 0.82-0.84 m, rising to the deck edge), tail.
    crest = [(0.0, Y(262)), (X(60), Y(252)), (X(90), silY(90) - 0.004)]
    crest += [(X(x), silY(x)) for x in range(118, 300, 10)]
    crest += [(X(x), Y(v) - (0.015 if x >= 380 else 0.0)) for x, v in DOOR_TOP]
    crest += [(X(600), Y(186)), (X(650), Y(190)), (X(700), Y(188)), (X(740), Y(186)), (X(772), Y(185)),
              (X(800), Y(188)), (X(816), Y(196)), (L, Y(222))]
    crest_y = dedupe(crest)
    # rear: kept 2-3 cm inside the plan taper (VT half-width 0.877 at 4.01 m, 0.848 at 4.10,
    # 0.810 at 4.19, 0.755 at 4.28, 0.680 at 4.36, 0.535 at 4.45).
    crest_z = keys([(0, 0), (X(60), 0.40), (X(90), 0.58), (X(118), 0.66), (X(145), 0.70), (X(175), 0.71),
                    (X(229), 0.72), (X(300), 0.74), (X(360), 0.79), (X(450), 0.80), (X(540), 0.81),
                    (X(600), 0.84), (X(650), 0.855), (XT(739), 0.85), (XT(754), 0.82), (XT(769), 0.78),
                    (XT(784), 0.72), (XT(799), 0.64), (XT(814), 0.48), (L, 0)])

    # ---- beltY / beltZ: front-lid shut line (plan line from z 0.42 at plan x 100 px to z 0.69
    # at 300 px, reaching the screen corner), glass base in the cabin (plan outer glass line
    # z 0.755 -> 0.735), then the foot of the raised grille deck under the spoiler.
    belt = [(0.0, Y(262)), (X(60), Y(254))]
    belt += [(x, y - LID_EDGE_DROP) for x, y in front if X(80) <= x <= X(230)]
    belt += [(X(270), silY(270) - 0.02), (X(300), Y(182)), (X(335), Y(181))]
    belt += line(BELT, 362, 628)
    belt += [(X(650), Y(170)), (X(690), Y(168))]
    belt += line(SPOILER, 712)
    belt += [(X(818), Y(200)), (L, Y(219))]
    belt_y = dedupe(belt)
    belt_z = keys([(0, 0), (X(60), 0.30), (XT(100), 0.422), (XT(150), 0.488), (XT(200), 0.555),
                   (XT(250), 0.617), (XT(300), 0.689), (X(335), 0.73), (X(362), 0.745), (X(460), 0.752),
                   (X(527), 0.74), (X(628), 0.72), (X(690), 0.66), (X(740), 0.62), (XT(784), 0.56),
                   (XT(799), 0.52), (XT(814), 0.40), (L, 0)])

    # ---- roofY / roofZ: under the lid centre ahead of the screen; screen base corner, the
    # A-pillar rear edge, the roof rail (DLO top), over the quarter window onto the rear
    # window's side edge (DECK), the grille deck and spoiler top edge, tail.
    roof = [(0.0, Y(252))]
    roof += [(x, y - 0.004) for x, y in nose[1:] + front]
    roof += [(X(x), silY(x) - 0.004) for x in (240, 260, 280)]
    roof += [(X(300), Y(181)), (X(330), Y(180))]
    roof += line(A_PILLAR_REAR, 362)
    roof += line(DLO_TOP)
    roof += [(X(560), Y(131)), (X(590), Y(129))]
    roof += line(DECK, 600)
    roof += [(X(x), silY(x) - 0.006) for x in (730, 760, 790)]
    roof += [(X(808), Y(192)), (L, Y(218))]
    roof_y = dedupe(roof)
    roof_z = keys([(0, 0), (X(60), 0.10), (X(145), 0.20), (X(230), 0.26), (X(290), 0.30),
                   (X(330), 0.70), (X(362), 0.745), (X(375), 0.73), (X(405), 0.69), (X(435), 0.645),
                   (X(460), 0.60), (X(500), 0.585), (X(530), 0.565), (X(590), 0.53), (X(640), 0.50),
                   (X(700), 0.49), (X(760), 0.50), (XT(799), 0.46), (XT(814), 0.36), (L, 0)])

    # ---- rockerY / floorY / sideY / sideZ / rockerZ -------------------------------
    rocker_y = dedupe([(X(a), Y(b)) for a, b in BOTTOM])
    floor_y = dedupe([(0.0, Y(306)), (X(60), Y(308.5)), (X(160), Y(312)), (X(300), 0.125), (X(580), 0.125),
                      (X(720), Y(302)), (X(810), Y(292)), (L, Y(284))])
    plan = plan_half_width()
    side_z = simplify([[x, round(z, 4)] for i, (x, z) in enumerate(plan.items()) if i % 3 == 0], 0.002)
    base_side = [(0, Y(280)), (X(100), 0.40), (X(160), 0.45), (X(300), 0.48), (X(560), 0.48),
                 (X(700), 0.52), (X(780), 0.50), (L, Y(262))]
    rock = rocker_y
    side_y = []
    for x in np.linspace(0, L, 181):
        b = float(np.interp(x, [p[0] for p in base_side], [p[1] for p in base_side]))
        r = float(np.interp(x, [p[0] for p in rock], [p[1] for p in rock]))
        side_y.append((x, max(b, r + 0.035) if 0.02 < x < L - 0.02 else b))
    side_y = simplify(keys(side_y), 0.003)

    def zside(x):
        return float(np.interp(x, [p[0] for p in side_z], [p[1] for p in side_z]))

    rocker_z = []
    for x in np.linspace(0, L, 91):
        near_arch = abs(x - X(FA_X)) < 0.34 or abs(x - X(RA_X)) < 0.37
        rocker_z.append((x, max(0.0, zside(x) - (0.012 if near_arch else 0.05))))
    rocker_z = simplify(keys(rocker_z), 0.003)

    curves = {"floorY": floor_y, "rockerY": rocker_y, "rockerZ": rocker_z, "sideY": side_y, "sideZ": side_z,
              "crestY": crest_y, "crestZ": crest_z, "beltY": belt_y, "beltZ": belt_z, "roofY": roof_y,
              "roofZ": roof_z, "topY": top_y}
    correct_overshoots(curves, plan, sil_car, L)
    return {"L": L, "FA": X(FA_X), "RA": X(RA_X), "silY": silY, **curves}


# ================================================================== 992.1 Carrera
D_FRONT = D_REAR = 0.0027     # 4,524 mm drawing -> 4,519 mm official
RIDE = 0.0                    # ground already placed for the Carrera's 1,298 mm


class Ctx(t15.Ctx):
    def __init__(self, shell, ride, d_front, d_rear):
        self.ride = ride
        self.shell = shell
        self.body, self.L = t15.shell_to_body(shell, ride, d_front, d_rear)
        self.FA = round(t15.remap_overhangs(shell["FA"], shell, d_front, d_rear), 4)
        self.RA = round(t15.remap_overhangs(shell["RA"], shell, d_front, d_rear), 4)
        self._df, self._dr = d_front, d_rear
        self.decals = []

    def sx(self, px):
        return round(t15.remap_overhangs(X(px), self.shell, self._df, self._dr), 4)

    def sxt(self, px):
        return round(t15.remap_overhangs(XT(px), self.shell, self._df, self._dr), 4)

    def sy(self, py):
        return round(Y(py) + self.ride, 4)


def shell_decals(c):
    """Glass, gaps and handles of the 992 shell (shared with stop 18)."""
    sx, sxt = c.sx, c.sxt
    c.side("side-glass", DLO_DOOR, "glass", "#1c2127", depth=[0.5, 2], facing=0.3)
    c.side("quarter-glass", DLO_QUARTER, "glass", "#1c2127", depth=[0.5, 2], facing=0.3)
    c.side("window-trim", A_PILLAR_REAR + DLO_TOP + [(556, 137)] + QUARTER_TOP[1:], "satin", "#15171a",
           kind="line", width=0.014, depth=[0.5, 2], facing=0.25)
    c.side("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.6, 2])
    # Flush pop-out door handle (geometry.json; P03 u 845-940, v 880-893): a slim flush bar
    # outlined by its gap, VS 474-514 x 205-212.
    c.side("door-handle", [(476, 212), (474, 208), (480, 205), (512, 205.5), (515, 209), (510, 212.5)], "satin",
           "#1d1e20", kind="band", width=0.006, depth=[0.6, 2], facing=0.3)
    # Windscreen in plan: base (cowl) at plan x 290 on the centre line curving back to the corners
    # at the A-pillar bases (plan 327 px, z 0.70); sides along the pillars to the header corners
    # (plan 400 px, z 0.60); header straight across at plan 402 px.
    scr = [[sxt(290), 0.0], [sxt(296), 0.30], [sxt(308), 0.52], [sxt(320), 0.64], [sxt(330), 0.70],
           [sxt(360), 0.672], [sxt(385), 0.63], [sxt(400), 0.60], [sxt(403), 0.30], [sxt(403), 0.0]]
    c.plane("windscreen", "top", scr, "glass", "#1c2127", facing=0.2, depth=[0.86, 2])
    # Rear window in plan: glass between plan 592 and 700 px, half-width 0.446 m (inner edge of
    # the dark frame band at row 551), rounded lower corners.
    rear = [[sxt(592), 0.0], [sxt(594), 0.43], [sxt(610), 0.446], [sxt(680), 0.44], [sxt(696), 0.40],
            [sxt(700), 0.25], [sxt(701), 0.0]]
    c.plane("rear-window", "top", rear, "glass", "#1c2127", facing=0.15, depth=[0.95, 2])
    # Front-lid shut line in plan: leading edge (plan 70.5 px, straight across) and the side
    # line (plan 100 px z 0.422 -> 300 px z 0.689) to the screen corner.
    c.plane("hood-gap", "top", [[sxt(70.5), 0.0], [sxt(71), 0.30], [sxt(78), 0.40], [sxt(100), 0.422],
                                [sxt(200), 0.555], [sxt(300), 0.689], [sxt(327), 0.72]],
            "satin", "#2a2a2a", kind="line", facing=0.3)
    # Engine lid / grille deck in plan: from behind the rear window (plan 703 px) to the spoiler's
    # trailing edge (plan 790 px), sides at z 0.52 (rear view deck edge).
    c.plane("lid-gap", "top", [[sxt(703), 0.0], [sxt(703), 0.50], [sxt(788), 0.52], [sxt(790), 0.0]],
            "satin", "#2a2a2a", kind="line", facing=0.3)
    # Porsche crest on the front lid (VT blob 79-91 px, rows 623-633).
    c.plane("crest", "top", [[sxt(79), 0.0], [sxt(79), 0.029], [sxt(91), 0.029], [sxt(91), 0.0]], "chrome",
            "#c9a24e", facing=0.3, depth=[0.4, 1.0])


def build():
    shell = trace_992_shell()
    c = Ctx(shell, RIDE, D_FRONT, D_REAR)
    L, FA, RA = c.L, c.FA, c.RA
    sx, sy, sxt, plane = c.sx, c.sy, c.sxt, c.plane
    shell_decals(c)

    # ---- side details ------------------------------------------------------------------
    # Fuel flap on the right front wing (geometry.json; P03: ellipse u 1185-1245, v 815-850 ->
    # 0.26-0.43 m behind the front axle, 0.76-0.87 m high).
    fcx, fcy = FA + 0.345, 0.815
    c.decals.append({"id": "fuel-flap", "plane": "side", "kind": "line", "side": "right",
                     "points": [[round(fcx + 0.09 * math.cos(a), 4), round(fcy + 0.052 * math.sin(a), 4)]
                                for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 17)],
                     "finish": "satin", "color": "#2a2a2a", "depth": [0.6, 2]})
    # Apron light strip on the intake's top edge, wrapping the corner (P03 u 1605-1690, v 936-944).
    plane("indicator-side", "side", [[0.06, 0.46], [0.05, 0.475], [0.20, 0.477], [0.215, 0.466]], "lens",
          "#e9edf0", depth=[0.4, 2], facing=0.25)
    # Light bar wrapping into the flank (photos P03/P01, see LIGHT_SIDE_M).
    plane("taillight-side", "side", [[round(a - D_REAR, 4), b] for a, b in LIGHT_SIDE_M], "lens", "#9c1a16",
          depth=[0.5, 2], facing=0.3)

    # ---- top: black louvred grille deck with the centre brake light (P14, P22, P27) -----------
    # Nine slats per side echoing the rear window (geometry.json); the body stripes run across
    # the car, so the slats are shown as a black field (plan 705-770 px, z 0-0.42).
    plane("engine-grille", "top", [[sxt(705), 0.0], [sxt(705), 0.40], [sxt(770), 0.42], [sxt(770), 0.0]],
          "satin", "#34373b", facing=0.3, depth=[0.85, 2],
          # Lengthwise louvres (geometry.json: "vertical/longitudinal louvres"; 992: nine
          # slats per side). Pitch ≈ 3 cm read from the lid close-ups (16/25, 17/27) and the
          # 992.1 studio plan view (17/22-top). Slats dark grey, gaps near-black.
          stripes=[0.03, 0.45], stripeAxis="b")

    # ---- front (VF; lowest point first, clockwise in the [z, y] plot) ---------------------------
    fd = [-0.05, 0.62]
    # Thin LED strip (position light / indicator) on the top edge of each outer intake, over its
    # outer half (geometry.json; P11: x 330-520 px of the 290-650 px intake -> z 0.49-0.72;
    # height: VF intake top 0.443 m).
    plane("indicator-front", "front", [[0.49, 0.443], [0.48, 0.452], [0.52, 0.458], [0.72, 0.458], [0.73, 0.448],
                                       [0.70, 0.443]], "lens", "#e9edf0", depth=fd, facing=0.2)
    # Outer intakes with three horizontal slats (VF dark field 911-1000 x 257-293 px; P11).
    plane("intake-front", "front", [vf(1000, 293), vf(1000, 258), vf(960, 257.5), vf(912, 258), vf(910, 275),
                                    vf(914, 293)], "satin", "#232528", stripes=[0.05, 0.3], depth=fd, facing=0.2)
    # Central opening (ACC radar; VF 1010 px to the centre, rows 262-293).
    plane("intake-front-centre", "front", [[0.0, vf(0, 293)[1]], [0.0, vf(0, 262)[1]],
                                           [0.245, vf(0, 262)[1]], [0.255, vf(0, 293)[1]]],
          "satin", "#1f2123", depth=fd, facing=0.2)
    # Licence plate over the central opening's upper part (P11: plate 725-1192 x 908-1005 px, its
    # bottom 65 px below the outer intakes' top at the plate's 1.113 mm/px -> 0.371-0.479 m).
    plane("plate-front", "front", [[0.0, 0.371], [0.0, 0.479], [0.26, 0.479], [0.26, 0.371]],
          "satin", "#d9dcdf", depth=fd, facing=0.2)
    # Black lower lip / splitter (VF rows 296-310; P11 y 1135-1185).
    plane("bumper-front-face", "front", [[0.0, 0.13], [0.0, vf(0, 296)[1]], [0.80, vf(0, 296)[1]],
                                         [0.84, vf(0, 302)[1]], [0.80, 0.13]],
          "satin", "#1b1c1e", depth=[-0.05, 0.45], facing=0.2)

    # ---- rear (P14 via p14(); lowest point first, clockwise in the [z, y] plot) ----------------
    rd = [L - 0.75, L + 0.05]
    # Seamless full-width LED light bar (reflector-band slot): P14 red line 555-561 px, full width.
    plane("reflector-band", "rear", [[0.0, p14(0, 561)[1]], [0.0, p14(0, 554.5)[1]], [0.60, p14(0, 554.5)[1]],
                                     [0.60, p14(0, 561)[1]]], "lens", "#b3201a", depth=rd, facing=0.15)
    # Lamp modules at the bar ends (taillight): P14 dark/red units from u 755 outward, v 545-583.
    plane("taillight", "rear", [p14(745, 583), p14(760, 578), p14(762, 562), p14(752, 546), p14(640, 543),
                                p14(600, 548), p14(598, 566), p14(612, 580)],
          "lens", "#9c1a16", depth=rd, facing=0.15)
    # 'PORSCHE' lettering on the body just below the bar (P14 u 826.7-1039.4, v 565.6-574.4).
    plane("badge-rear", "rear", [[0.0, p14(0, 574.4)[1]], [0.0, p14(0, 565.6)[1]], [0.267, p14(0, 565.6)[1]],
                                 [0.267, p14(0, 574.4)[1]]], "satin", "#3b3d40", depth=rd, facing=0.2)
    # Rear plate low in the black lower section between the tailpipes (P14 v 703.9-748.3).
    plane("plate-rear", "rear", [[0.0, p14(0, 748.3)[1]], [0.0, p14(0, 703.9)[1]], [0.26, p14(0, 703.9)[1]],
                                 [0.26, p14(0, 748.3)[1]]], "satin", "#d9dcdf", depth=rd, facing=0.2)
    # Red reflectors at the outer ends of the black section's top edge (P18/P21; vendor VR
    # 915-957 x 672-679 px -> z 0.56-0.80, 0.40-0.44 m).
    plane("reflector-rear", "rear", [[0.58, 0.402], [0.58, 0.425], [0.80, 0.43], [0.80, 0.405]], "lens",
          "#a51d18", depth=rd, facing=0.2)
    # Black lower rear section (P14 top edge v 691 -> 0.437 m; vendor rows 670-726).
    top_black = p14(0, 691)[1]
    plane("bumper-rear-face", "rear", [[0.0, 0.13], [0.0, top_black], [0.84, top_black], [0.90, 0.38],
                                       [0.90, 0.20], [0.84, 0.13]], "satin", "#1c1d1f",
          depth=[L - 0.45, L + 0.05], facing=0.2)

    car = {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.591,
        "trackRear": 1.557,
        "body": c.body,
        "decals": c.decals,
        # 235/40 ZR 19 -> 0.671 m, 295/35 ZR 20 -> 0.7145 m (= Porsche's 671 / 715 mm). The standard
        # "Carrera" wheel of the official base-Carrera photos (P18, P21): ten slim spokes in five
        # V-pairs -> twin-spoke; silver finish (P18's gold and P21's black are options).
        "wheels": {
            "front": {"diameter": round(0.4826 + 2 * 0.235 * 0.40, 4), "width": 0.235, "rim": 0.4826,
                      "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
            "rear": {"diameter": round(0.508 + 2 * 0.295 * 0.35, 4), "width": 0.295, "rim": 0.508,
                     "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
        },
        # Round LED lamp with the four-point DRL (geometry.json): VF ring 910-955 x 193-231 ->
        # z 0.703, y 0.70, 0.255 m across the ring (P11: lens ~0.24 m); plan centre x (VT
        # 137.5 px); pitch from the front view's 0.223/0.255 foreshortening (~30 deg).
        "headlight": {
            "centre": [sxt(137.5), vf(0, 212)[1], 0.703],
            "outline": [[round(0.12 * math.cos(a), 4), round(0.12 * math.sin(a), 4)]
                        for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)],
            "yaw": 10, "pitch": 30, "ring": 0.012, "ringColor": "#2a2d31", "ringFinish": "satin",
            "lensColor": "#d5dde4", "graphic": "led4",
        },
        # Rectangular door-top mirrors (geometry.json): VS housing 360-402 x 158-194, VF z 0.80-1.015.
        "mirror": {"at": [sx(381), sy(176), 0.80], "size": [0.24, 0.13, 0.215], "shape": "aero",
                   "color": "paint", "finish": "paint"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # Base Carrera: one oval tailpipe each side (geometry.json; P14 centres u 763.3 / 1102.2,
        # v 739.4 -> z +-0.426 m, 0.316 m; 0.14 x 0.095 m ovals -> radius 0.048).
        "exhausts": [[round(L - 0.05, 4), p14(0, 739.4)[1], 0.426, 0.048],
                     [round(L - 0.05, 4), p14(0, 739.4)[1], -0.426, 0.048]],
    }
    return car, shell


def main():
    car, shell = build()
    out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
    with open(out, "w") as f:
        json.dump(car, f, indent=1)
    tyre_r = car["wheels"]["front"]["diameter"] / 2
    rel = os.path.relpath(VENDOR, ROOT)
    calib = {
        "side": {"image": rel, "wheelF": [FA_X, GROUND_Y - tyre_r / S],
                 "wheelR": [RA_X, GROUND_Y - tyre_r / S], "tipF": TIP_X + D_FRONT / S, "crop": [30, 90, 850, 345]},
        "top": {"image": rel, "tipF": VT_TIP, "tipR": VT_TAIL, "centreY": VT_CY, "crop": [30, 440, 850, 820]},
        "front": {"image": rel, "centreX": VF_CX, "groundY": VF_GROUND, "left": 894, "right": 1213.5,
                  "width": 1.852, "crop": [860, 95, 1260, 340]},
        "rear": {"image": rel, "centreX": VR_CX, "groundY": VR_GROUND, "left": 894, "right": 1214.5,
                 "width": 1.852, "crop": [860, 510, 1260, 755]},
    }
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    print("wrote", os.path.relpath(out, ROOT), "length", car["length"], "axles", car["frontAxle"], car["rearAxle"])
    # Photo check on the official P03 profile (nose right -> flip).
    # The photo is a cropped press image: the principal point is put at hub height (camera at
    # about wheel-hub height, research/photos/17-992-1-2019/sources.json) and mid-wheelbase.
    t15.perspective_side_check(car, PHOTO_SIDE, (1321.87, 974.17, 543.79, 979.45), 14.0,
                               os.path.join(ROOT, "research", "traces", STOP, "check-photo-side.png"),
                               crop=[150, 640, 1700, 1110], flip=True, u0=932.8, v0=976.8, roof_span=None)


if __name__ == "__main__":
    main()
