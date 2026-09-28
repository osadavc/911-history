"""Trace: 00-t7-1959 — Porsche Type 754 "T7", F. A. Porsche's four-seat design study (1959/60).

There is NO drawing of the T7 anywhere (blueprints/00…/sources.json). The car is traced from its
photos, calibrated on the official figures of research/specs.json 00 (AutoBild Klassik data box;
wheelbase also Porsche Newsroom): L 4340, W 1730, H 1350, WB 2400 mm, tyres 165/80 R 15.

Research that shapes the model (history.md 00, geometry.json 00, specs.json 00):
  * "the front half is identical to the production 911" (PCA archive), "viewed head on, the
    concept could easily be mistaken for its production successor" (Car and Driver), Porsche:
    "the flattened bonnet between the free-standing wings, the inclined built-in headlights, the
    A-pillars with the windscreen" -> the nose / wings / lamps follow the 901 (stop 01) and are
    checked on the photo;
  * four-seat notchback: long flat roof, wrap-around rear glass over a separate, flat engine lid;
  * front: body-colour bumper with a full-width chrome strip, no guards; clear lamp + chrome
    horn grille under each headlamp; two dark intakes in the valance; crest on the lid;
  * rear: flat tail, horizontal lamps at the corners on the bumper line (red + clear), slatted
    chrome grilles on the rear flanks ahead of the lamps (no lid grille), body-colour bumper with
    a chrome strip, two tall black guards flanking a recessed mesh panel, two tailpipes, gold
    'PORSCHE' on the lid;
  * steel disc wheels with slots and domed chrome caps; one round chrome mirror on a stalk on
    the left front wing; chrome drip rails and window frames; plain sills; green metallic.

Photo 01 (research/photos/00…/01-side-left.jpg, marked "tracing": "side"; Commons "Projet T7",
Retromobile 2013): Panasonic DMC-FZ8 at 6 mm = 36 mm equiv (EXIF on the Commons page), native
3072 x 2304 frame, the research copy is that frame at 1920 x 1440 -> F = 2000 px, principal point
= image centre (960, 720). The camera is close (~5 m) and at eye height, so the photo is NOT
treated as orthographic: a full pinhole camera (yaw / pitch / roll + position) is fitted to
  - the two hub centres (rim-flange circle fits) at the official wheelbase 2.400 m, hub height
    0.31 m (loaded 165/80 R 15; free radius 0.3225) and wheel plane z 0.70 +- 0.04,
  - the near / far headlamp pair (same x, y; z +-0.611 +- 0.02 = the 901's lamp spacing, per
    "front half identical to the 911"),
  - the near window-sill chrome and the far glass base seen through the cabin (same height).
  -> camera 1.62 m high, 4.95 m from the centre plane, pitched 8.8 deg down (see .md).
Checks that were NOT fitted: with that camera and the 2.400 m wheelbase the photo gives the
length 4.345 m (specs 4.340) and roof 1.33-1.34 m (specs 1.350); the 901 model placed on the
same camera sits on the T7's nose, wings and lamps (research: front half = 911).
Every photo point is back-projected onto the plane z of the surface it lies on (near side: the
body side, the glass, the belt; outline: the far fender crest, the roof crown, the near corners
of nose and tail) - see the z value next to each reading.

Other photos: 14-rear-34-left (rear face: lamps, grilles, guards, mesh panel, tailpipes,
script; lateral positions by a projective map across the rear face), 09/10-front-34-right
(front details), 04-top (plan shape: rear wings), 05/07 (front 3/4 left, mirror side).

Run: <venv python> research/traces/00-t7-1959.py
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import half_section, mono, simplify  # noqa: E402

STOP = "00-t7-1959"
PH = os.path.join(ROOT, "research", "photos", STOP)
PHOTO_SIDE = os.path.join(PH, "01-side-left.jpg")
PHOTO_REAR = os.path.join(PH, "14-rear-34-left.jpg")

# ------------------------------------------------------------------ official figures (specs.json 00)
WB = 2.400
L = 4.340
W = 1.730
H = 1.350
TYRE_D = round(0.381 + 2 * 0.165 * 0.80, 4)       # 165/80 R 15 -> 0.645 m (TRACING.md: computed)

# ------------------------------------------------------------------ photo-01 camera
F_PX, U0, V0 = 2000.0, 960.0, 720.0


class Cam:
    """Pinhole camera. Car frame: xa = metres behind the FRONT AXLE, y up, z right (the camera
    looks at the car's left side from z < 0). psi yaw, th pitch (down +), phi roll."""

    def __init__(self, cx, cy, cz, psi, th, phi):
        self.C = np.array([cx, cy, cz])
        fy = np.array([math.sin(psi), 0.0, math.cos(psi)])
        ry = np.array([math.cos(psi), 0.0, -math.sin(psi)])
        down = np.array([0.0, -1.0, 0.0])
        f = fy * math.cos(th) + down * math.sin(th)
        d = -fy * math.sin(th) + down * math.cos(th)
        self.f = f
        self.r = ry * math.cos(phi) + d * math.sin(phi)
        self.d = -ry * math.sin(phi) + d * math.cos(phi)

    def project(self, xa, y, z):
        P = np.stack(np.broadcast_arrays(np.asarray(xa, float), np.asarray(y, float), np.asarray(z, float)), -1)
        q = P - self.C
        zc = q @ self.f
        return U0 + F_PX * (q @ self.r) / zc, V0 + F_PX * (q @ self.d) / zc

    def on_z(self, u, v, z):
        """image point -> (xa, y) on the plane z = const."""
        dv = self.f + (u - U0) / F_PX * self.r + (v - V0) / F_PX * self.d
        t = (z - self.C[2]) / dv[2]
        P = self.C + t * dv
        return float(P[0]), float(P[1])

    def row_of_line(self, u, y, z):
        """image row where the 3D line (x free, y, z) crosses image column u."""
        lo, hi = -3.0, 6.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.project(mid, y, z)[0] < u:
                lo = mid
            else:
                hi = mid
        return float(self.project((lo + hi) / 2, y, z)[1])


# Observations (photo-01 px): hub centres = circle fits to the rim-flange outer edge (bright rim ->
# black tyre, radial scans, level 110: rms 1.1-2.0 px); lamp-ring centres from 6x zooms (+-8 px);
# near sill chrome / far glass base at column 1000 (3.5x zoom).
OBS = dict(hubF=(363.73, 1009.56), hubR=(1453.28, 1020.14), lampN=(80.0, 820.0), lampF=(276.0, 738.0),
           beltN=(1000.0, 758.0), beltF=(1000.0, 681.0))
# priors: loaded hub height, wheel plane z, 901 lamp z (front half = 911), 901 cabin belt z, far glass
PRIORS = {6: (0.31, 0.01), 7: (0.70, 0.04), 10: (0.611, 0.02), 12: (0.645, 0.03), 13: (0.60, 0.04)}


def _cam_residuals(p):
    cx, cy, cz, psi, th, phi, rh, zw, xl, yl, zl, yb, zbn, zbf = p
    cam = Cam(cx, cy, cz, psi, th, phi)
    out = []
    for key, xa in (("hubF", 0.0), ("hubR", WB)):
        u, v = cam.project(xa, rh, -zw)
        out += [u - OBS[key][0], v - OBS[key][1]]
    for key, s in (("lampN", -1), ("lampF", 1)):
        u, v = cam.project(xl, yl, s * zl)
        out += [(u - OBS[key][0]) / 8.0, (v - OBS[key][1]) / 8.0]
    out += [(cam.row_of_line(OBS["beltN"][0], yb, -zbn) - OBS["beltN"][1]) / 2.0,
            (cam.row_of_line(OBS["beltF"][0], yb, zbf) - OBS["beltF"][1]) / 3.0]
    out += [(p[i] - mu) / sd for i, (mu, sd) in PRIORS.items()]
    return np.array(out)


_sol = least_squares(_cam_residuals, [1.3, 1.55, -5.1, 0.0, math.radians(8), 0.0, 0.31, 0.70, -0.68, 0.70,
                                      0.61, 0.87, 0.645, 0.60])
CAM_P = _sol.x
CAM = Cam(*CAM_P[:6])
LAMP_XA, LAMP_Y, LAMP_Z = CAM_P[8], CAM_P[9], CAM_P[10]
BELT_Y = CAM_P[11]

# ------------------------------------------------------------------ car frame
# Front overhang: the nose's left-most image point (u 28, v 937) is the bumper's near corner
# where the plan outline turns 25 deg to the view ray; on the 911 nose plan (03 row scans) that
# tangent point is at z 0.54, 0.076 m behind the tip -> tip 0.898-0.912 m ahead of the front axle
# for tangent z 0.45-0.60. Tail: (u 1875, v 950) on the 911 tail plan (tangent z 0.50, 0.043 m
# ahead of the tip) -> 1.026-1.054 m behind the rear axle. -> L = 0.905 + 2.400 + 1.04 = 4.345
# (specs 4.340): the front overhang 0.905 is kept and the tail set by the official length.
FA = 0.905
RA = round(FA + WB, 4)


def bp(u, v, z):
    """photo-01 point on the plane z -> model [x, y] (x from the front tip)."""
    xa, y = CAM.on_z(u, v, z)
    return [round(xa + FA, 4), round(y, 4)]


def bps(points, z):
    return [bp(u, v, z) for u, v in points]



# ------------------------------------------------------------------ readings (photo-01 px) -> model
def arches(hub, readings, z):
    return [bp(u, v, z) for u, v in readings]


# Wheel arches: edge of the green paint on radial scans every 10 deg from the hub centres (paint
# "greenness" G - (R + B) / 2 > 6 over 4 px; the black wheel well and tyre read ~0). z: the arch
# lip at the body side (front 0.79 = 901 sideZ at the axle; rear 0.84, the wider rear wing).
FRONT_ARCH_PX = [(192.7, 1009.6), (182.5, 977.6), (188.9, 945.9), (205.2, 918.1), (224.3, 892.6), (248.0, 871.7),
                 (278.7, 862.3), (307.3, 854.5), (336.1, 853.0), (363.7, 852.6), (390.6, 856.9), (417.1, 863.0),
                 (443.2, 871.9), (464.0, 890.1), (484.8, 908.0), (504.9, 928.1), (509.4, 956.5), (518.3, 982.3),
                 (522.7, 1009.6)]
REAR_ARCH_PX = [(1303.3, 1020.1), (1310.5, 995.0), (1317.0, 970.5), (1325.1, 946.1), (1336.8, 922.4), (1354.9, 902.9),
                (1376.3, 886.8), (1400.3, 874.5), (1426.4, 867.5), (1453.3, 861.1), (1481.4, 860.6), (1510.1, 864.2),
                (1539.8, 870.3), (1567.1, 884.6), (1588.9, 906.4), (1611.8, 928.6), (1614.9, 961.3), (1618.7, 991.0)]
FRONT_ARCH = arches(0, FRONT_ARCH_PX, -0.79)
# the lip's front edge is vertical from the hub row up to 945 px (u 183-193, x 0.542-0.561, mean
# 0.555): kept vertical-but-monotone (x must increase along the curve)
_xf = round(float(np.mean([p[0] for p in FRONT_ARCH[:3]])), 4)
FRONT_ARCH = [[round(_xf - 0.005 + 0.005 * i, 4), p[1]] if i < 3 else p for i, p in enumerate(FRONT_ARCH)]
REAR_ARCH = arches(0, REAR_ARCH_PX, -0.84)
# Sill: lower body edge v 1052 (greenness mask, u 540-1290) on the sill plane z 0.76.
SILL_Y = bp(1000, 1052, -0.76)[1]
# Nose (brightened 4x zoom): bumper face u 28 (v 930-955), chrome strip v 952-974 (u 30-164),
# valance below it curving from (45, 985) to its bottom edge v 1020-1022 (u 80-185), which ends at
# the arch. Tail (3.4x zoom): bumper bottom v 1013-1015 (u 1625-1780) turning up to (1860, 985)
# and the rear-most bumper point (1870, 950); bumper top gap v 930-935; lamp (1808-1850, 888-922).
NOSE_BOT_PX = [(45, 985), (80, 1020), (130, 1021), (185, 1022)]
TAIL_BOT_PX = [(1625, 1015), (1700, 1014), (1780, 1013), (1840, 1005), (1860, 985)]
# (back-projected below, on the model's own lower-edge z = plan half-width - 0.04 at that x)

# Fender crests (front): near crest highlight v 767-771 (u 150-500, z -0.56..-0.63) and the far crest
# = the image outline v 694-683 (u 320-520, z +0.60..+0.62) give the same line (0.82-0.86 m) -> a
# check of the camera; used for crestY ahead of the cowl.
CREST_F = sorted([bp(150, 771, -0.56), bp(300, 767, -0.60), bp(500, 764, -0.63), bp(320, 694, 0.60), bp(420, 690, 0.61),
                  bp(520, 683, 0.62)])
_cc = np.polyfit([p[0] for p in CREST_F], [p[1] for p in CREST_F], 2)   # near and far readings agree to 1 cm
CREST_F_SMOOTH = [[round(float(x), 4), round(float(np.polyval(_cc, x)), 4)] for x in (0.40, 0.60, 0.80, 1.00, 1.20)]
# Glasshouse (3-5x zooms): windscreen's near lower corner (720, 742) on z 0.62, A-pillar front edge to
# the roof (850, 548) z 0.55; vent-window frame (768, 745)-(897, 578); door-glass top frame v 580-585;
# B-pillar (door glass rear) (1123, 580)-(1178, 760); quarter window front (1140, 587)-(1195, 762),
# rear (1260, 603)-(1447, 760); rear window's side (wrap-round) frame from the C-pillar top
# (1340, 597) via (1393, 617) (1447, 640) (1493, 670) (1550, 700) to its lower rear corner (1570, 725)
# and back along its lower edge (1480, 757); belt (sill chrome) v 757 (u 770-1450).
SCREEN_CORNER = bp(720, 742, -0.62)
PILLAR_TOP = bp(850, 548, -0.55)
DRIP_Y = bp(1000, 576, -0.55)[1]
BELT = [bp(u, 757, -0.645) for u in (770, 1000, 1200, 1450)]
RW_SIDE = [bp(1340, 597, -0.53), bp(1393, 617, -0.54), bp(1447, 640, -0.56), bp(1493, 670, -0.58), bp(1550, 700, -0.60),
           bp(1570, 725, -0.60)]
# Roof crown: image outline v 526-555 (u 920-1280) = the roof's far shoulder (camera 0.3 m above the
# roof) back-projected on z +0.25; the crown at z 0 is ~1 cm higher and is set to the official
# 1.350 m at its peak (photo peak 1.33-1.34 m).
ROOF_OUT = [bp(u, v, 0.25) for u, v in ((920, 532), (960, 526), (1000, 531), (1040, 528), (1080, 529), (1120, 536),
                                        (1160, 535), (1200, 539), (1240, 544), (1280, 555))]
_rx = np.array([p[0] for p in ROOF_OUT])
_rc = np.polyfit(_rx, [p[1] for p in ROOF_OUT], 3)          # smooth the 1-2 px outline noise
ROOF_SMOOTH = [[round(float(x), 4), round(float(np.polyval(_rc, x)), 4)] for x in np.linspace(_rx[0], _rx[-1], 7)]
ROOF_LIFT = round(H - max(y for _, y in ROOF_SMOOTH), 4)
# Engine lid and tail (4x high-contrast zoom of u 1660-1890, v 730-950 + half-level column scans
# against the light wall): the lid's outline (1680, 765) (1700, 772) (1720, 779) (1740, 789)
# (1760, 801) is the lid's crown seen from 1.6 m: a crowned surface is tangent to the ray where it
# falls by the ray's 9-10 deg, i.e. ~0.18 m beyond the centre line (z +0.18), and the centre line is
# ~0.016 m higher there. Behind u 1790 the outline would land beyond the car's length on z >= 0, so
# it is the NEAR tail corner (z -0.45): (1790, 822) (1810, 830) (1830, 845) (1845, 868), down to the
# lamp top (1847, 880). Near lid gap (dark line) (1600, 752) (1590, 777) (1680, 810) (1780, 833)
# (1840, 863) on z 0.48; bumper tangent ray (1868, 950) and lower corner (1850, 1000).
LID_CROWN = [[x, round(y + 0.016, 4)] for x, y in (bp(1680, 765, 0.18), bp(1700, 772, 0.18), bp(1720, 779, 0.18),
                                                   bp(1740, 789, 0.18), bp(1760, 801, 0.18))]
TAIL_CORNER = [bp(u, v, -0.45) for u, v in ((1790, 822), (1810, 830), (1830, 845), (1845, 868))]
LID_EDGE = [bp(1600, 752, -0.48), bp(1590, 777, -0.48), bp(1680, 810, -0.48), bp(1780, 833, -0.48), bp(1840, 863, -0.48)]


def keys(pairs):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pairs]


# ------------------------------------------------------------------ body curves
X_SCREEN = 1.50            # windscreen base at the centre: 0.19 m ahead of its near lower corner
                           # (911 plan sweep, 01 SCREEN_SWEEP: 0.201 m at z 0.668)
X_HEADER = round(PILLAR_TOP[0] - 0.01, 4)
X_RW_TOP = 3.10            # roof's rear edge at the centre (near C-pillar top 3.057 at z 0.53)
X_RW_BASE = 3.62           # rear window base = lid front at the centre (near lower corner 3.555)
X_FACE = 4.295             # flat rear face (lamps, mesh recess) - lid's rear edge at the centre
X_BUMPER = 4.305           # the rear bumper starts behind the face; rear-most point = L (bumper)
crest_front = [[0.0, 0.43], [0.06, 0.49], [0.13, 0.56], [0.20, 0.66], [0.26, 0.74], [0.31, 0.80]] + CREST_F_SMOOTH + [[1.35, 0.862], [1.45, 0.87]]
# Hood (lid) centre line: below the fender crest by 0.11 m at the lamps -> 0.04 m at the cowl (the
# 911's relation, 03 trace), bumper/nose as the photo (bumper top 0.44 at the face).
hood = [[0.0, 0.44], [0.012, 0.47], [0.04, 0.51], [0.07, 0.55], [0.12, 0.60], [0.25, 0.67], [0.45, 0.73], [0.75, 0.80],
        [1.05, 0.84], [1.30, 0.86], [X_SCREEN, 0.905]]
screen = [[X_SCREEN + 0.08, 0.98], [X_SCREEN + 0.22, 1.10], [X_SCREEN + 0.34, 1.22], [X_HEADER, 1.315]]
roof = [[x, round(y + ROOF_LIFT, 4)] for x, y in ROOF_SMOOTH if x > X_HEADER + 0.05]
rear_window = [[X_RW_TOP, 1.268], [3.25, 1.17], [3.40, 1.06], [3.52, 0.97], [X_RW_BASE, 0.905]]
# Lid centre line: front at the glass base, crown readings, rounding down into the flat rear face.
lid = [[3.70, 0.865], [3.85, 0.81]] + LID_CROWN + [[4.25, 0.665], [4.28, 0.635], [X_FACE, 0.60]]

# Tail keyframes (x >= 3.62): section points (z, y) for P3 crest (rear-wing hip), P4 belt (lid side
# edge = the near lid-gap line, z 0.48 -> 0.46), P5 (lid shoulder at z 0.30, 0.025 below the crown).
# Upper tail corner = the near outline TAIL_CORNER (z 0.45): (4.10, 0.706) (4.15, 0.688)
# (4.20, 0.654) (4.24, 0.600). The flat rear face at X_FACE carries the lamps (0.53-0.63) and the
# mesh recess; behind it only the bumper remains (top 0.50, strip 0.45-0.50, face 0.44, bottom 0.35).
def lid_y(x):
    xs, ys = zip(*lid)
    return float(np.interp(x, xs, ys))


def lid_edge_y(x):
    pts = sorted([p for p in LID_EDGE[2:]] + [[3.66, 0.80]])
    return float(np.interp(x, [p[0] for p in pts], [p[1] for p in pts]))


TAIL = {}
for x in (3.70, 3.85, 4.00, 4.10, 4.16, 4.21):
    TAIL[x] = (
        (float(np.interp(x, [3.70, 4.00, 4.10, 4.16, 4.21], [0.745, 0.70, 0.64, 0.58, 0.50])),
         float(np.interp(x, [3.70, 3.85, 4.00, 4.10, 4.15, 4.20, 4.24], [0.80, 0.76, 0.725, 0.70, 0.688, 0.655, 0.60]))),
        (float(np.interp(x, [3.70, 4.10, 4.21], [0.48, 0.46, 0.40])), round(lid_edge_y(x), 4)),
        (0.30, round(lid_y(x) - 0.025, 4)),
    )
# upper tail corner inside the near outline rays (1845, 875): x <= 4.24 at z 0.45, <= 4.30 at z 0.30;
# the bumper below stays wider (its own tangent ray (1868, 950))
TAIL[4.25] = ((0.44, 0.595), (0.36, 0.61), (0.24, 0.635))
TAIL[4.275] = ((0.37, 0.585), (0.30, 0.60), (0.20, 0.615))
TAIL[X_FACE] = ((0.31, 0.575), (0.25, 0.585), (0.15, 0.59))
TAIL[X_BUMPER] = ((0.44, 0.50), (0.36, 0.50), (0.25, 0.50))
TAIL[4.325] = ((0.38, 0.49), (0.30, 0.495), (0.21, 0.495))
TAIL[L] = ((0.0, 0.45), (0.0, 0.45), (0.0, 0.45))
tail_xs = sorted(TAIL)
top_tail = [[X_FACE + 0.004, 0.54], [X_BUMPER, 0.50], [4.325, 0.495], [L, 0.45]]
top_y = hood + screen + roof + rear_window + lid + top_tail

# P4 belt: hood edge (01 relation: hood centre - 0.03), cabin glass base, the lid's side edge.
belt = [[0.0, 0.43], [0.012, 0.455]] + [[x, round(y - 0.03, 4)] for x, y in hood[2:-1]] + [[X_SCREEN, 0.88]]
belt += [[SCREEN_CORNER[0], SCREEN_CORNER[1] - 0.01]] + BELT + [[3.36, 0.886], [3.60, 0.87]]
belt += [[x, TAIL[x][1][1]] for x in tail_xs]
# P5 roof rail: on the hood ahead of the screen, the A-pillar, the drip rail, the rear window's side edge.
rail = [[0.0, 0.43], [0.012, 0.465]] + [[x, round(y - 0.004, 4)] for x, y in hood[2:-1]] + [[X_SCREEN, 0.90]]
rail += [SCREEN_CORNER, [1.80, 1.08], [1.90, 1.21], PILLAR_TOP, [2.10, DRIP_Y], [2.60, DRIP_Y], [2.95, DRIP_Y - 0.01]]
rail += RW_SIDE + [[3.64, 0.87]] + [[x, TAIL[x][2][1]] for x in tail_xs]
# P3 crest: fender crest, door shoulder just under the glass base, rear-wing hip, tail corner.
crest = crest_front + [[1.70, 0.865], [2.20, 0.865], [2.70, 0.87], [3.10, 0.87], [3.40, 0.85], [3.60, 0.82]]
crest += [[x, TAIL[x][0][1]] for x in tail_xs]
# P2 widest point height; P1 lower edge; P0 floor.
side_y = keys([(0, 0.40), (0.10, 0.44), (0.45, 0.50), (FA, 0.54), (1.60, 0.52), (2.70, 0.52), (RA, 0.54),
               (3.90, 0.52), (4.20, 0.47), (X_FACE, 0.45), (L, 0.44)])
floor_y = keys([(0, 0.40), (0.05, 0.33), (0.20, 0.26), (0.45, 0.25), (FA, 0.21), (1.40, 0.195), (2.90, 0.195),
                (RA, 0.21), (3.65, 0.30), (4.10, 0.34), (4.28, 0.35), (4.33, 0.39), (L, 0.44)])

# ------------------------------------------------------------------ plan and z of the section lines
with open(os.path.join(ROOT, "src", "data", "cars", "01-901-1963.json")) as _f:
    _C01 = json.load(_f)["body"]
SIDE_Z_01 = _C01["sideZ"]           # 901 plan (1967 factory plan + 01 nose): front half = 911
W_HALF = W / 2


def side_z_at(x):
    if x <= 2.70:
        return float(np.interp(x, [p[0] for p in SIDE_Z_01], [p[1] for p in SIDE_Z_01]))
    # behind the B-pillar the rear wing swells to the official 1.730 m at the rear axle, then
    # rounds into the flat tail (photos 04 / 14: the rear wings are the widest part of the car)
    # tail corner in plan tangent to the bumper silhouette ray through (1868, 950) (dx/dz -0.44:
    # (4.339, 0.40) (4.295, 0.50) (4.251, 0.60)) and closing on the official length
    return float(np.interp(x, [2.70, 3.00, RA, 3.70, 3.95, 4.08, 4.16, 4.23, 4.28, 4.315, 4.335, 4.3395, L],
                           [0.796, 0.835, W_HALF, 0.855, 0.815, 0.76, 0.70, 0.62, 0.53, 0.45, 0.37, 0.27, 0.0]))


def on_lower_edge(u, v, z0=0.65):
    """back-project onto the body's lower edge: z = plan half-width - 0.04 at the resulting x."""
    z = z0
    for _ in range(4):
        x, y = bp(u, v, -z)
        z = max(0.2, side_z_at(x) - 0.04)
    return bp(u, v, -z)


NOSE_BOT = [on_lower_edge(u, v, 0.6) for u, v in NOSE_BOT_PX]
TAIL_BOT = [on_lower_edge(u, v, 0.75) for u, v in TAIL_BOT_PX]
bottom = [[0.0, 0.40], [0.02, 0.36]] + NOSE_BOT + FRONT_ARCH + [[1.30, SILL_Y + 0.03], [1.36, SILL_Y], [2.90, SILL_Y]]
bottom += REAR_ARCH + [[3.64, 0.37]] + TAIL_BOT + [[4.30, 0.38], [4.33, 0.41], [L, 0.44]]

side_z = [[round(x, 4), round(side_z_at(x), 4)] for x in list(np.arange(0.0, 0.30, 0.01)) + list(np.arange(0.30, 4.20, 0.03))
          + [4.20, 4.23, 4.26, 4.28, 4.30, 4.315, 4.325, 4.335, 4.3395, L]]
ARCH_F = (FRONT_ARCH[0][0] - 0.02, FRONT_ARCH[-1][0] + 0.02)
ARCH_R = (REAR_ARCH[0][0] - 0.02, REAR_ARCH[-1][0] + 0.02)
rocker_z = [[x, round(max(0.0, z - (0.005 if (ARCH_F[0] <= x <= ARCH_F[1] or ARCH_R[0] <= x <= ARCH_R[1]) else 0.04)), 4)]
            for x, z in side_z if x < 4.30]
rocker_z += [[4.315, 0.36], [4.335, 0.28], [L, 0.0]]
crest_z = keys([(0, 0), (0.03, 0.34), (0.15, 0.61), (0.29, 0.641), (X_SCREEN, 0.66), (1.75, 0.70), (2.70, 0.71),
                (3.10, 0.73), (RA, 0.76), (3.60, 0.75)] + [(x, TAIL[x][0][0]) for x in tail_xs])
belt_z = keys([(0, 0), (0.042, 0.30), (0.064, 0.39), (X_SCREEN, 0.585), (SCREEN_CORNER[0], 0.62), (1.85, 0.645),
               (2.70, 0.645), (3.36, 0.62), (3.60, 0.55)] + [(x, TAIL[x][1][0]) for x in tail_xs])
roof_z = keys([(0, 0), (0.044, 0.16), (1.30, 0.30), (X_SCREEN, 0.50), (SCREEN_CORNER[0], 0.62), (PILLAR_TOP[0], 0.55),
               (2.95, 0.55), (3.10, 0.53), (3.40, 0.56), (3.56, 0.60), (3.64, 0.40)] + [(x, TAIL[x][2][0]) for x in tail_xs])

body = {
    "floorY": floor_y,
    "rockerY": simplify(sorted(bottom), 0.002),
    "rockerZ": simplify(rocker_z, 0.003),
    "sideY": side_y,
    "sideZ": simplify(side_z, 0.002),
    "crestY": simplify(sorted(crest), 0.002),
    "crestZ": crest_z,
    "beltY": simplify(sorted(belt), 0.002),
    "beltZ": belt_z,
    "roofY": simplify(sorted(rail), 0.002),
    "roofZ": roof_z,
    "topY": simplify(sorted(top_y), 0.002),
}
for k in ("sideZ", "rockerZ"):
    c = body[k]
    c[0][1] = 0.0 if c[0][0] <= 0 else c[0][1]
    if c[0][0] > 0:
        c.insert(0, [0.0, 0.0])
    if c[-1][0] < L:
        c.append([L, 0.0])
    else:
        c[-1][1] = 0.0
for k, c in body.items():
    out = []
    for x, v in c:
        x, v = round(float(x), 4), round(float(v), 4)
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([x, v])
    body[k] = out


# ------------------------------------------------------------------ decals
# Slot ids as the 901 (stop 01, the morph partner) wherever the T7 has the same part. New ids for
# T7-only parts: rear-glass-side (the wrap-around rear glass seen from the side), grille-side
# (slatted chrome engine-air grilles on the rear flanks), intake-front (TRACING.md table id),
# guard-rear (as 02/03), mesh-rear (mesh-covered recess between the rear guards).
def glass_z(v):
    """side-glass surface z at image row v: tumblehome from z 0.64 at the sill (v 757) to 0.56 at
    the frame top (v 587) - the 901's glass base / rail z (01: 0.65 / 0.538)."""
    t = min(1.0, max(0.0, (757 - v) / (757 - 587)))
    return -(0.64 - 0.08 * t)


def gl(points):
    return [bp(u, v, glass_z(v)) for u, v in points]


def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": pts, "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, **kw):
    d = {"id": id_, "plane": plane, "kind": "fill", "points": [[a0, b0], [a0, b1], [a1, b1], [a1, b0]],
         "finish": finish, "color": color}
    d.update(kw)
    return d


CHROME = "#dfe2e5"
GLASS = "#1d2329"
RUBBER = "#1c1c1c"
CLEAR = "#eef1f2"
GOLD = "#c9a24e"
FRONT = [-0.05, 0.45]
REAR = [L - 0.45, L + 0.05]

# Side glass (3-5x zooms of photo 01; inner edges of the chrome frames), lowest-front first,
# clockwise in this view. Vent + door glass: A-pillar rear edge (757, 757) -> (885, 587), top frame
# v 587-590, B-pillar frame (1112, 590) -> (1162, 757), sill v 757.
DLO_DOOR = gl([(757, 757), (790, 700), (830, 640), (860, 600), (885, 587), (1000, 588), (1110, 590), (1162, 757),
               (1000, 757), (850, 757)])
# Rear side window (four seats): B-pillar (1140, 585) -> (1195, 760), top frame to the rounded
# top-rear corner (1270, 600), C-pillar front edge down to (1440, 760), sill v 760.
DLO_QUARTER = gl([(1195, 760), (1140, 587), (1200, 588), (1250, 592), (1272, 602), (1440, 760), (1320, 761)])
# Wrap-around rear glass, side portion: C-pillar rear edge (1300, 592) -> (1466, 762), the glass's
# upper/rear frame (1340, 597) (1393, 617) (1447, 640) (1493, 670) (1550, 700) (1570, 725), its lower
# rear corner (1572, 745) and the lid edge v 760.
RW_GLASS = [bp(1466, 762, -0.62), bp(1345, 600, -0.53), bp(1393, 617, -0.54), bp(1447, 640, -0.56), bp(1493, 670, -0.58),
            bp(1550, 700, -0.60), bp(1570, 725, -0.60), bp(1572, 745, -0.61), bp(1540, 760, -0.62)]
# Chrome frame (outer edge): A-pillar foot, up the A-pillar, along the roof edge, down the C-pillar.
TRIM = gl([(752, 760), (790, 698), (850, 598), (880, 578), (1000, 579), (1120, 581), (1265, 590), (1290, 600),
           (1452, 762)])
VENT = gl([(850, 755), (897, 588)])
DRIP = [bp(u, v, -0.55) for u, v in ((880, 572), (1000, 574), (1150, 578), (1260, 585), (1330, 596))]
# Door (sill zoom): front edge u 596-600 from the belt down to v 1040, bottom v 1043, rear edge
# u 1182-1197 (slanted), up to the belt.
DOOR = [bp(u, v, -0.79) for u, v in ((602, 765), (598, 900), (598, 1030), (610, 1043), (900, 1044), (1170, 1043),
                                      (1182, 1030), (1190, 900), (1197, 765))]
HANDLE = [bp(u, v, -0.81) for u, v in ((1107, 843), (1107, 829), (1188, 829), (1188, 843))]
# Bumper strips from the side: front v 958-975 (u 30-165), rear v 945-970 (u 1640-1850); heights
# taken at the side (the strip ends wrap round the corners): front 0.40-0.44, rear 0.45-0.50.
F_STRIP = (0.40, 0.44)
R_STRIP = (0.45, 0.50)
decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("rear-glass-side", RW_GLASS, "glass", GLASS, depth=[0.4, 2], facing=0.3),
    side_decal("window-trim", TRIM, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("vent-divider", VENT, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", DRIP, "chrome", CHROME, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.55, 2]),
    side_decal("door-handle", HANDLE, "chrome", CHROME, depth=[0.6, 2]),
    # plain sills (geometry.json 00 rocker_sills) -> no rocker-trim, as the 901 show car
    box("side", "bumper-front", 0.0, round(bp(165, 966, -0.76)[0], 4), F_STRIP[0], F_STRIP[1], "chrome", CHROME,
        depth=[0.0, 2], facing=0.2),
    box("side", "bumper-rear", round(bp(1640, 958, -0.84)[0], 4), L, R_STRIP[0], R_STRIP[1], "chrome", CHROME,
        depth=[0.0, 2], facing=0.2),
    # Front lamp wrap-round (clear lens, photo 01 u 60-125, v 905-930; photo 10: clear).
    side_decal("indicator-side", [bp(60, 930, -0.64), bp(62, 905, -0.64), bp(125, 905, -0.70), bp(125, 930, -0.70)],
               "lens", CLEAR, depth=[0.5, 2], facing=0.25),
    # Rear lamp wrap-round (red, photo 01 u 1825-1875, v 885-920).
    side_decal("taillight-side", [bp(1825, 920, -0.76), bp(1825, 885, -0.76), bp(1875, 885, -0.66), bp(1875, 920, -0.66)],
               "lens", "#b8231d", depth=[0.5, 2], facing=0.25),
    # Engine-air grilles on the rear flanks ahead of the lamps (photo 01 u 1685-1825, v 890-925;
    # Car and Driver: "small side-mounted vents").
    side_decal("grille-side", [bp(1685, 925, -0.82), bp(1690, 890, -0.82), bp(1825, 890, -0.77), bp(1825, 925, -0.77)],
               "chrome", CHROME, depth=[0.6, 2], facing=0.3, stripes=[0.018, 0.5]),
]

# Front plane. Lateral layout = the 901's (research: "the front half is identical to the
# production 911"; photos 07/09/10/13: chrome slatted horn grille inboard, long clear lamp
# outboard wrapping round the corner): grille z 0.396-0.569, lamp 0.580-0.742 (01 front sketch).
# The T7 lamp is one clear lens; it is split at the 901's parking/indicator divide (0.648) so each
# half pairs with the 901's lamp in the morph. Heights: photo 01 side view of the lamp y 0.475-0.535.
LAMP_B, LAMP_T = 0.475, 0.535
decals += [
    box("front", "bumper-front-face", 0.0, 0.78, F_STRIP[0], F_STRIP[1], "chrome", CHROME, depth=FRONT, facing=0.3),
    box("front", "horn-grille", 0.396, 0.569, LAMP_B, LAMP_T, "chrome", CHROME, depth=FRONT, facing=0.3,
        stripes=[0.012, 0.45]),
    box("front", "parking-front", 0.580, 0.648, LAMP_B, LAMP_T, "lens", CLEAR, depth=FRONT, facing=0.25),
    box("front", "indicator-front", 0.648, 0.742, LAMP_B, LAMP_T, "lens", CLEAR, depth=FRONT, facing=0.25),
    # Two dark openings in the valance below the strip (geometry.json 00 front.air_intakes; photos
    # 07/10: ~0.2 m wide slots just below the strip, either side of the centre).
    box("front", "intake-front", 0.10, 0.30, 0.31, 0.36, "satin", RUBBER, depth=FRONT, facing=0.3),
]

# Rear plane (photo 14, rear 3/4 left): lateral positions by a projective map across the flat rear
# face, fitted on the symmetric lamp ends (outer corners u 1212 / 1835, clear-lens inner ends
# u 1457 / 1766) and scaled on the lamp corner z 0.76 (the body half-width there); heights from the
# side photo (lamp 0.53-0.63, strip 0.45-0.50). From the outside: red lens with a red square
# (0.76 -> 0.47), clear reversing lens (0.47 -> 0.41), black guard (0.40 -> 0.29), mesh-covered
# recess between the guards (the 901's plate position; no plate on the museum car).
T_BOT, T_TOP = 0.53, 0.63
decals += [
    box("rear", "taillight", 0.47, 0.76, T_BOT, T_TOP, "lens", "#b8231d", depth=REAR, facing=0.25),
    box("rear", "reverse-light", 0.41, 0.47, T_BOT, T_TOP, "lens", CLEAR, depth=REAR, facing=0.25),
    box("rear", "bumper-rear-face", 0.40, 0.80, R_STRIP[0], R_STRIP[1], "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", "guard-rear", 0.29, 0.40, 0.33, 0.64, "rubber", RUBBER, depth=REAR, facing=0.3),
    box("rear", "mesh-rear", 0.0, 0.29, 0.50, 0.635, "satin", "#3a3d40", depth=REAR, facing=0.3, stripes=[0.012, 0.5]),
    # gold 'PORSCHE' script on the lid, centred (photo 14: 0.45 m long, just above the lid's rear edge)
    box("rear", "badge-rear", 0.0, 0.225, 0.70, 0.725, "chrome", GOLD, depth=REAR, facing=0.2),
]

# Top plane. Windscreen: base 0.19 m behind its centre at the corners (911 plan sweep, 01), near
# lower corner x 1.694 (photo 01), header at the A-pillar top x 1.978. Rear window: roof edge at
# the centre x 3.10 (3.06 at the C-pillar tops, z 0.53), base = the lid's front edge x 3.62 (3.57 at
# the lower corners, z 0.60) - photo 01 back-projections; plan shape of the wrap-round from photo 16.
screen_top = [[X_SCREEN, 0.0], [X_SCREEN + 0.03, 0.40], [SCREEN_CORNER[0], 0.60], [PILLAR_TOP[0], 0.52],
              [X_HEADER + 0.02, 0.0]]
rw_top = [[X_RW_TOP, 0.0], [3.06, 0.50], [3.30, 0.57], [3.57, 0.57], [X_RW_BASE, 0.0]]
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rw_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.88, 2]},
    # chrome-framed fresh-air vent on the lid ahead of the windscreen (geometry.json 00; photo 09) - as 01
    box("top", "cowl-grille", X_SCREEN - 0.116, X_SCREEN - 0.03, 0.0, 0.26, "satin", "#2b2b2b", stripes=[0.012, 0.5],
        facing=0.3, depth=[0.8, 2]),
    # coloured crest on the lid nose (photos 07/09/10), position as the 901's
    box("top", "crest", 0.035, 0.075, 0.0, 0.025, "chrome", GOLD, facing=0.3, depth=[0.45, 2]),
    {"id": "hood-gap", "plane": "top", "kind": "line",
     "points": [[0.042, 0.0], [0.044, 0.3], [0.056, 0.378], [0.064, 0.39], [X_SCREEN - 0.02, 0.585]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
    # engine lid: front edge at the rear-window base, sides converging to the tail (photos 01/16)
    {"id": "lid-gap", "plane": "top", "kind": "line",
     "points": [[X_RW_BASE + 0.02, 0.0], [X_RW_BASE + 0.02, 0.50], [3.85, 0.49], [4.10, 0.46], [4.27, 0.40], [4.29, 0.0]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]
assert len({d["id"] for d in decals}) == len(decals), "duplicate decal ids"

# ------------------------------------------------------------------ parts
# Tracks are not published (specs.json 00: null). The front half is the 911's (research), so the
# 901's tracks (01: 1.332 / 1.312, 901 brochure) are used - see the .md.
TRACK_F, TRACK_R = 1.332, 1.312
MIRROR_C = bp(515, 712, -0.64)             # round head, photo 01: centre, 0.10 m tall (v 690-735)
car = {
    "id": STOP,
    "length": L,
    "frontAxle": FA,
    "rearAxle": RA,
    "trackFront": TRACK_F,
    "trackRear": TRACK_R,
    "body": body,
    "decals": decals,
    "wheels": {
        # silver-painted steel disc wheels with slots and domed chrome caps (geometry.json 00)
        "front": {"diameter": TYRE_D, "width": 0.165, "rim": 0.381, "design": "steel-hubcap",
                  "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
        "rear": {"diameter": TYRE_D, "width": 0.165, "rim": 0.381, "design": "steel-hubcap",
                 "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
    },
    # Round chrome-ringed headlamps (Motor1: "inherited from the 356"; research: 911 front):
    # centre from the camera fit (near/far lamp pair) xa -0.652, y 0.709, z 0.608; lens / ring and
    # tilt as the 901 (same front).
    "headlight": {
        "centre": [round(FA + LAMP_XA, 4), round(LAMP_Y, 4), round(LAMP_Z, 4)],
        "outline": [[round(math.cos(a) * 0.0975, 4), round(math.sin(a) * 0.0975, 4)]
                    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)],
        "yaw": 4,
        "pitch": 24,
        "ring": 0.022,
        "ringColor": "#e3e6e9",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    },
    # One round chrome mirror on a stalk on top of the LEFT front wing ahead of the A-pillar
    # (geometry.json 00 body.mirrors; photos 01/06/08/09/10/13 - never on the right wing).
    "mirror": {"at": [MIRROR_C[0], MIRROR_C[1], 0.60], "size": [0.03, 0.10, 0.10], "shape": "round", "color": CHROME,
               "finish": "chrome", "sides": "left"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    # Two tailpipes under the bumper either side of the centre (Motor1 "two central exhaust
    # outlets"; photo 14: pipes 0.33 m apart about the centre after the parallax of the rear-face map).
    "exhausts": [[round(L - 0.01, 4), 0.30, -0.165, 0.032], [round(L - 0.01, 4), 0.30, 0.165, 0.032]],
}

out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
with open(out, "w") as f:
    json.dump(car, f, indent=1)

# ------------------------------------------------------------------ calibration for check_car.py
# Only photos exist. side_photo: hub-calibrated flat overlay (the camera is 5 m away and 1.6 m
# high, so centre-line features are displaced - the perspective check below is the real test).
S_FLAT = WB / math.hypot(OBS["hubR"][0] - OBS["hubF"][0], OBS["hubR"][1] - OBS["hubF"][1])
calib = {
    "side_photo": {"image": os.path.relpath(PHOTO_SIDE, ROOT), "wheelF": list(OBS["hubF"]), "wheelR": list(OBS["hubR"]),
                   "tipF": round(OBS["hubF"][0] - FA / S_FLAT, 1), "crop": [0, 450, 1920, 1170]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)


def perspective_check(path, crop=(0, 450, 1920, 1170)):
    """Project the lofted car through the fitted photo-01 camera and draw it on the photo."""
    img = cv2.imread(PHOTO_SIDE)
    vis = cv2.addWeighted(img, 0.72, np.full_like(img, 255), 0.28, 0)
    n = 320
    xs = [L * (0.5 - 0.5 * math.cos(math.pi * i / (n - 1))) for i in range(n)]
    mask = np.zeros(img.shape[:2], np.uint8)
    prev = None
    for x in xs:
        sec = half_section(body, x)
        a = np.array([(x, y, z) for z, y in sec] + [(x, y, -z) for z, y in sec[::-1]])
        u, v = CAM.project(a[:, 0] - FA, a[:, 1], a[:, 2])
        pts = np.stack([u, v], 1)
        if prev is not None:
            for j in range(len(pts) - 1):
                cv2.fillConvexPoly(mask, np.array([prev[j], prev[j + 1], pts[j + 1], pts[j]], np.int32), 255)
        prev = pts
    cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, cnt, -1, (40, 40, 255), 2)
    lx = np.linspace(0, L, 400)

    def poly(p3, col, th=1, closed=False):
        a = np.array(p3)
        u, v = CAM.project(a[:, 0] - FA, a[:, 1], a[:, 2])
        cv2.polylines(vis, [np.stack([u, v], 1).astype(np.int32)], closed, col, th, cv2.LINE_AA)

    poly([(x, mono(body["rockerY"], x), -mono(body["rockerZ"], x)) for x in lx], (0, 150, 255), 1)
    poly([(x, mono(body["crestY"], x), -mono(body["crestZ"], x)) for x in lx], (60, 200, 60))
    poly([(x, mono(body["beltY"], x), -mono(body["beltZ"], x)) for x in lx], (255, 120, 0))
    poly([(x, mono(body["roofY"], x), -mono(body["roofZ"], x)) for x in lx], (200, 60, 170))
    poly([(x, mono(body["topY"], x), 0.0) for x in lx], (0, 0, 160))

    def surf_z(x, y):
        sec = half_section(body, x)
        best = None
        for (z0, y0), (z1, y1) in zip(sec[5:-9], sec[6:-8]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                zz = z0 + (z1 - z0) * (y - y0) / (y1 - y0)
                best = zz if best is None else max(best, zz)
        return best if best is not None else max(zz for zz, _ in sec)

    for d in decals:
        if d["plane"] != "side" or d.get("side") == "right":
            continue
        poly([(x, y, -surf_z(x, y)) for x, y in d["points"]], (0, 230, 230), 1, d["kind"] != "line")
    for ax, key, tr in ((FA, "front", TRACK_F), (RA, "rear", TRACK_R)):
        w = car["wheels"][key]
        zt = -(tr / 2 + w["width"] / 2)
        for rr in (w["diameter"] / 2, w["rim"] / 2):
            poly([(ax + rr * math.cos(t), w["diameter"] / 2 + rr * math.sin(t), zt) for t in np.linspace(0, 2 * math.pi, 60)],
                 (200, 200, 0), 1, True)
    cx_, cy_, cz_ = car["headlight"]["centre"]
    for sgn in (-1, 1):
        poly([(cx_, cy_ + 0.1 * math.sin(t), sgn * cz_ + 0.1 * math.cos(t)) for t in np.linspace(0, 2 * math.pi, 30)],
             (0, 0, 255), 1, True)
    x0, y0, x1, y1 = crop
    cv2.imwrite(path, vis[y0:y1, x0:x1])

if __name__ == "__main__":
    names = ["cx", "cy", "cz", "psi", "th", "phi", "rh", "zw", "xl", "yl", "zl", "yb", "zbn", "zbf"]
    print("camera:", {n: round(math.degrees(v), 3) if n in ("psi", "th", "phi") else round(float(v), 4)
                      for n, v in zip(names, CAM_P)})
    print("residuals:", np.round(_sol.fun, 2))
    os.makedirs(os.path.join(HERE, STOP), exist_ok=True)
    perspective_check(os.path.join(HERE, STOP, "check-side-photo-persp.png"))
    print("wrote", os.path.relpath(out, ROOT), "L", L, "FA", FA, "RA", RA, "height", max(v for _, v in body["topY"]),
          "width", round(2 * max(v for _, v in body["sideZ"]), 3), "decals", len(decals))
