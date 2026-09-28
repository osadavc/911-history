"""Trace: 04-carrera-rs-27-1973 — 911 Carrera RS 2.7 Coupe, MY1973 (F-series), Sport (M471).

Traced car: the Porsche Museum's white Carrera RS 2.7 with green 'Carrera' script and green
Fuchs centres (research/photos/04…/01-side-left, 02-front, 03-rear = Porsche Museum studio shots,
marked "tracing" in sources.json; 04/05/17/18 are the same car). sources.json: "No bumper
overriders (Sport)".

What the research says changed vs stop 03 (history.md "What changed visually vs the 1969–73
911 (stop 03)", geometry.json 04 changes_from_previous_stop / body / rear_spoiler / rear,
specs.json 04):
  * ducktail ('Entenbuerzel'): fixed upswept lip integral with the glass-fibre engine lid ->
    part of the body (TRACING.md: topY/crestY kick up at the tail); slatted grille ahead of the
    lip; 'Carrera RS' script on the right-hand side of the ducktail;
  * rear wings widened (+42 mm; body width 1652 mm across the rear wings); 6J / 7J x 15 Fuchs;
    185/70 VR 15 / 215/60 VR 15; tracks 1372 / 1394; WB 2271; L 4147; H 1320;
  * front spoiler (chin spoiler) under the bumper;
  * 'Carrera' script along the flanks between the arches, colour-matched wheel centres; the
    side stripe continues along the bumper flanks; 'PORSCHE' decal across the rear;
  * MY1973: black horn grilles, rectangular door mirror (history.md 03 "MY1973");
  * Sport (the museum car): no overriders, lightweight rear bumper with a raised centre
    (plate) section, no sill trim strip (photos 01/03/05).
Everything else is the F-series shell ("lighting signature identical to the 1973 911 F series",
geometry.json 04) = the shell of stop 03, traced from the same 1967 factory body drawing.

References
  SHELL  research/blueprints/02-911-swb-1964/tbp-40868_porsche-911-1967_factory-body-4view-mm.png
         (factory body-in-white drawing; calibration of the 02/03 traces: 2.4567 mm/px, ground
         y 644.3, front axle "Plan 0" x 2066, bumper face x 1713). Readings marked "02"/"03" are
         those traces' readings of this sheet. NOTE: the sheet is a body-in-white; its door and
         window lines are the APERTURES (door front edge x 2275, DLO frame from (2381, 283)), which
         the RS photo confirms (door front edge 1.383 m vs sheet 1.381 m). The 02/03 door-gap
         (x 2296) and DLO (from (2342, 265)) readings sit 5-9 cm ahead of these lines, so the door
         / glass decals here are re-traced (photo 01, checked on the sheet) - see the .md.
  SIDE   photos/04…/01-side-left.jpg (studio profile, long lens): RS parts (front bumper and
         spoiler, rear bumper, ducktail, wheel arches), door, glass, lamps, handle, mirror,
         stripe + script. Hub centres by rim-lip circle fits (414.78, 787.30) / (1397.76, 788.02)
         -> 982.98 px = WB 2271 mm (2.3103 mm/px near the wheel planes); tyre contact y 919.
  DRAW   blueprints/04…/tbp-83845_…_4view.png (RS line drawing): plan-view shape of the rear
         flare; side/top views for the check overlays. Hub fits (895.63, 325.98) / (1612.33,
         325.89) -> 716.7 px = 2271 mm: L 4.151, front overhang 0.870, rear 1.010, roof 1.288 m;
         plan width ~2.6 % wide (the sources.json "-3.2 %" WB/L came from a coarser hub read).
         vec-4925 (printed 2271 / 4102 / 1320 / 1652 / 1372 / 1404): tyre-edge hub fits
         (275.2, 282.6) / (673.7, 282.6) -> 398.4 px = 2271 mm; bumper face x 124.3, rear
         extreme x 832.5 -> front overhang 0.860, rear 0.906, L 4.037 (its own 4102 line is
         internally inconsistent, sources.json); its rear overhang is 10 cm shorter than the
         photo shows even at the near-plane scale (0.982), so it is not used for the rear.
  FRONT  photos/04…/02-front.jpg; REAR photos/04…/03-rear.jpg: lateral positions. Scale per
         depth from the 520 mm plates (front 360 px, rear 367 px) and the tracks (tyre centres
         872 / 890 px): camera ~9.7 / 9.4 m from the plates; z = (u - centre) * s(x).

Photo 01 -> model. x: near-plane scale about the front hub (features near the wheel planes);
centre-plane tail features are stretched about the rear hub by KT so that the rear-most bumper
point lands on the official length (perspective: they are ~0.4-0.8 m farther from the camera).
y: the shell features the photo shares with the factory sheet sit 3-6 cm lower above the tyre
contact than the sheet at the official 1320 mm height (as in the 03 photo check). The model keeps
the official-height frame of 03 and maps photo heights with a linear offset DELTA(x) fitted on
those shell landmarks (belt, glass top, roof, fastback, front arch top, headlamp; rms ~1 cm).

Length: specs.json 04 chose 4147 (geometry.json: factory brochure 4102, de.wikipedia 4163). The
model uses FA 0.867 (03's bumper face; RS drawings 0.870 / 0.860) and L 4.147 (rear overhang
1.009; tbp-83845 1.010).

Run: <venv python> research/traces/04-carrera-rs-27-1973.py
"""
import json
import math
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import column_profile, half_section, mono, silhouette_from_drawing, simplify  # noqa: E402

STOP = "04-carrera-rs-27-1973"
BP = os.path.join(ROOT, "research", "blueprints")
PH = os.path.join(ROOT, "research", "photos", STOP)
SHEET = os.path.join(BP, "02-911-swb-1964", "tbp-40868_porsche-911-1967_factory-body-4view-mm.png")
RSDRAW = os.path.join(BP, STOP, "tbp-83845_porsche-911-carrera-rs-27-1973_4view.png")
PHOTO_SIDE = os.path.join(PH, "01-side-left.jpg")
PHOTO_FRONT = os.path.join(PH, "02-front.jpg")
PHOTO_REAR = os.path.join(PH, "03-rear.jpg")

# ------------------------------------------------------------------ official figures (specs.json 04)
WB = 2.271
L = 4.147
TRACK_F, TRACK_R = 1.372, 1.394
WIDTH = 1.652                      # across the rear wings (geometry.json 04 body.rear_arch_width)

# ------------------------------------------------------------------ shell calibration (factory sheet, as 02/03)
S = 2.4567 / 1000
TIP_X = 1713                       # bumper face at the centre line (03: side 1712, plan 1714)
GROUND_Y = 644.3
FRONT_AXLE_X = 2066                # "Plan 0"


def X(px):
    return round((px - TIP_X) * S, 4)


def Y(py):
    return round((GROUND_Y - py) * S, 4)


def curve(points):
    return [[X(px), Y(py)] for px, py in points]


def keys(pairs):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pairs]


FA = X(FRONT_AXLE_X)               # 0.8672
RA = round(FA + WB, 4)             # 3.1382
SHIFT_03 = (FA + 2.268 - X(2966)) / S   # 03: LWB rear-arch shift on the SWB sheet (px)

# ------------------------------------------------------------------ photo 01 calibration
HUB_F, HUB_R = (414.78, 787.30), (1397.76, 788.02)   # rim-lip circle fits (rms 0.4 px)
S01 = WB / math.hypot(HUB_R[0] - HUB_F[0], HUB_R[1] - HUB_F[1])   # 2.3103 mm/px
GROUND_V = 919.0                   # tyre contact (column scans under both hubs)
TAIL_U = 1823.0                    # rear-most bumper point (row scans v 720-730)
KT = (L - RA) / ((TAIL_U - HUB_R[0]) * S01)           # 1.027


def xn(u):
    """photo 01 x -> model x for features near the wheel planes (near-plane scale)."""
    return FA + (u - HUB_F[0]) * S01


def xt(u):
    """photo 01 x -> model x for centre-plane tail features (tips, ducktail, bumper profile)."""
    return RA + (u - HUB_R[0]) * S01 * KT


with open(os.path.join(ROOT, "src", "data", "cars", "03-911-lwb-1969.json")) as _f:
    _TOP03 = json.load(_f)["body"]["topY"]


def _top03(x):
    return float(np.interp(x, [p[0] for p in _TOP03], [p[1] for p in _TOP03]))


# (name, photo u, photo v, model y at xn(u)) - shell features common to the sheet and the photo.
LANDMARKS = [
    ("belt: door top / glass base line", 1000, 552.5, Y(286.5)),   # sheet x 2600 run 285-288
    ("side-glass top (inner frame edge)", 1000, 416.5, Y(151)),     # sheet x 2600 run 150-152
    ("roof", 1000, 366.5, Y(108.5)),                                # sheet x 2600 run 108-110
    ("fastback", 1400, 456.0, None),                                # 03 topY (sheet silhouette)
    ("front arch top", 440, 636.5, Y(353)),                         # sheet x 2060 run 350-359
    ("headlamp centre (side view)", 172, 632.0, 0.716),             # 02/03 headlamp centre
]


def _fit_delta():
    rows = []
    for name, u, v, y in LANDMARKS:
        x = xn(u)
        y = _top03(x) if y is None else y
        rows.append((name, round(x, 3), round(y - (GROUND_V - v) * S01, 4)))
    xs = np.array([r[1] for r in rows])
    ds = np.array([r[2] for r in rows])
    a, b = np.linalg.lstsq(np.c_[np.ones_like(xs), xs], ds, rcond=None)[0]
    return float(a), float(b), rows, ds - (a + b * xs)


DELTA_A, DELTA_B, DELTA_ROWS, DELTA_RES = _fit_delta()


def yp(v, x):
    """photo 01 row at model x -> model y."""
    return round((GROUND_V - v) * S01 + DELTA_A + DELTA_B * x, 4)


def pn(u, v):
    """near-plane photo point -> model [x, y]."""
    x = xn(u)
    return [round(x, 4), yp(v, x)]


def pt(u, v):
    """centre-plane tail photo point -> model [x, y]."""
    x = xt(u)
    return [round(x, 4), yp(v, x)]


def pns(points):
    return [pn(u, v) for u, v in points]


# ------------------------------------------------------------------ shell: factory sheet (as 02/03)
gray = cv2.imread(SHEET, cv2.IMREAD_GRAYSCALE)
side = silhouette_from_drawing(gray, (1680, 90, 3400, 545), close=3, thresh=150)
side = cv2.morphologyEx(side, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
prof = column_profile(side)


def clean(values, window=9, tol=10):
    xs = sorted(values)
    arr = np.array([values[x] for x in xs], float)
    out = arr.copy()
    for i in range(len(arr)):
        lo, hi = max(0, i - window), min(len(arr), i + window + 1)
        med = np.median(arr[lo:hi])
        if abs(arr[i] - med) > tol:
            out[i] = med
    return dict(zip(xs, out))


top_px = clean({x: t for x, (t, b) in prof.items()}, window=30, tol=8)
for a, b in ((2036, 2080), (2160, 2186), (2368, 2388), (3004, 3022)):   # 02: leader lines bridged
    ya, yb = top_px[a], top_px[b]
    for x in range(a, b + 1):
        top_px[x] = ya + (yb - ya) * (x - a) / (b - a)
silhouette_top = [[X(x), Y(v)] for x, v in sorted(top_px.items()) if x % 4 == 0 and x >= 1850]

plan = silhouette_from_drawing(gray, (1660, 670, 3420, 1340), close=3, thresh=150)
plan = cv2.morphologyEx(plan, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
pprof = column_profile(plan)
half_width_sheet = [[X(x), round((b - t) / 2 * S, 4)] for x, (t, b) in sorted(pprof.items())
                    if 1860 <= x and x % 4 == 0]
# Bumper-face plan outline (03 row scans, guard-less): (x px, half-width px).
NOSE_PLAN = [(1713, 0), (1714.5, 42), (1715, 62), (1716, 82), (1718, 102), (1718.5, 122),
             (1722.5, 142), (1726.5, 162), (1731.5, 182), (1737, 202), (1744.5, 222),
             (1756.5, 242), (1771.5, 262), (1794.5, 282), (1857.5, 302)]
nose_plan = [[X(x), round(h * S, 4)] for x, h in NOSE_PLAN]

# ------------------------------------------------------------------ RS rear flare (plan shape)
# tbp-83845 plan view (x scale = its side view: bumper face 622 / tail 1933 px vs side 621 /
# 1931): upper half of the outline (above its centre row 740.5; the lower half carries glitches)
# by column scans, 9-px running mean, as a fraction of its maximum (at 0.1-0.2 m behind its rear
# hub). Its absolute widths read ~2.6 % wide, so only the shape is used, scaled to 1652 mm.
rs_gray = cv2.imread(RSDRAW, cv2.IMREAD_GRAYSCALE)
rs_plan = silhouette_from_drawing(rs_gray, (600, 445, 1946, 1020), close=3, thresh=150)
rs_prof = column_profile(rs_plan)
RS_S = WB / (1612.33 - 895.63)
RS_RA_PX, RS_CY = 1612.33, 740.5
_rs = sorted((x, RS_CY - t) for x, (t, b) in rs_prof.items() if 1400 <= x <= 1920)
_rs_x = np.array([x for x, _ in _rs], float)
_rs_w = np.convolve(np.array([w for _, w in _rs], float), np.ones(9) / 9, mode="same")
_rs_x, _rs_w = _rs_x[4:-4], _rs_w[4:-4]
RS_W_MAX = float(_rs_w[(_rs_x > 1560) & (_rs_x < 1720)].max())


def rs_flare(x):
    xd = RS_RA_PX + (x - RA) / RS_S
    return float(np.interp(xd, _rs_x, _rs_w)) / RS_W_MAX * WIDTH / 2


# ------------------------------------------------------------------ photo 01 readings (px), RS parts
# Hand-read on 4x zooms and column/row scans of 01-side-left.jpg.
# Front bumper with its chin spoiler (Sport, body colour, no guards, no rubber strip): flat
# vertical face u 88-92 from v 725 to 816; top edge v 727 at the face; lower edge 815 -> 824
# (u 100 -> 208, mask column scans) into the front arch.
f_top = yp(727, 0.03)
f_bot = yp(816, 0.03)
SPOILER_EDGE = pns([(100, 815), (124, 819), (148, 820), (172, 823), (208, 824), (240, 823.5)])
# Tail, centre plane (row scans for the rear-most body pixel, column scans for the top edge):
# rear-window base trim u 1510, engine lid dipping to v 544 at u 1640 (black louvres in the
# silhouette), lip rising to v 508 at u 1725-1740, trailing-edge tip (1758, 520); below the lip
# the rear face (1765, 640) -> (1781, 665) meets the Sport bumper's raised centre section,
# which bulges to u 1823 at v 722-730 and turns under at (1801, 765); bumper bottom v 787.
LID_TOP = [(1510, 503), (1535, 506), (1560, 518), (1580, 524), (1600, 531), (1620, 538), (1640, 544),
           (1650, 540), (1660, 535), (1680, 526), (1700, 517), (1715, 511), (1728, 508), (1740, 508),
           (1750, 512), (1755, 515), (1758, 520)]
REAR_FACE = [(1765, 640), (1774, 650), (1781, 665)]
BUMPER_UPPER = [(1794, 670), (1803, 680), (1810, 690), (1815, 700), (1820, 710), (1823, 722)]
BUMPER_LOWER = [(1822, 732), (1819, 740), (1813, 750), (1806, 760), (1801, 765)]
lid = [pt(u, v) for u, v in LID_TOP]
tip_x, tip_y = lid[-1]
rear_face = [pt(u, v) for u, v in REAR_FACE]
bump_up = [pt(u, v) for u, v in BUMPER_UPPER]
bump_lo = [pt(u, v) for u, v in BUMPER_LOWER]
TAIL_Y = bump_up[-1][1]                          # the rear-most point's height (0.487)
R_BUMPER_BOT = yp(789, 3.95)                     # bottom edge v 787-793 (u 1560-1800)
R_SIDE_TOP = yp(716.5, 3.95)                     # side portion's top under the lamp (v 716-717)
R_SIDE_END_X = round(xn(1810), 4)                # side portion's rear corner (black end piece u 1805-1815)


def arch_scan(hub, degs):
    """Arch edge = first body pixel (bright or green stripe) on radial scans from the hub."""
    im = cv2.imread(PHOTO_SIDE).astype(float)
    g = im.mean(axis=2)
    green = (im[:, :, 1] > im[:, :, 2] + 50) & (im[:, :, 1] > im[:, :, 0] + 50)
    body_mask = (g > 125) | green
    out = []
    for deg in degs:
        a = math.radians(deg)
        dx, dy = math.cos(a), -math.sin(a)
        for r in np.arange(125, 240, 0.5):
            u, v = hub[0] + dx * r, hub[1] + dy * r
            ui, vi = int(round(u)), int(round(v))
            if body_mask[vi - 1:vi + 2, ui - 1:ui + 2].mean() > 0.6:
                out.append(pn(u, v))
                break
    return out


FRONT_ARCH = arch_scan(HUB_F, range(185, -1, -5))       # front foot -> rear foot
REAR_ARCH = arch_scan(HUB_R, range(185, -5, -5))

# ------------------------------------------------------------------ centre line (topY)
NOSE_LID = [(1728, 435), (1732, 426), (1736, 419), (1740, 414.5), (1744, 410), (1752, 404.5),
            (1760, 398.5), (1768, 393.5), (1776, 388.5), (1784, 384.5), (1792, 381), (1800, 377),
            (1808, 373.5), (1816, 369.5), (1830, 362)]                                   # 03
LID = [(1850, 356), (1875, 346), (1900, 337), (1925, 329.5), (1950, 323), (1975, 316), (2000, 309.5),
       (2025, 303), (2050, 298), (2075, 293)]                                              # 03
COWL = [(2100, 292), (2150, 287), (2200, 283), (2255, 279)]                                 # 02
SCREEN = [(2262, 262), (2300, 234), (2350, 198), (2400, 162), (2440, 133), (2470, 114)]    # 02
hood = [[0.0, f_top], [0.012, round(f_top + 0.002, 4)], [0.026, round(f_top + 0.004, 4)]] + curve(NOSE_LID + LID + COWL)
screen = curve(SCREEN)
RW_BASE_X = lid[0][0]                    # rear-window base at the centre (photo 1510 px; 03: 3.407)
roof_line = [p for p in silhouette_top if screen[-1][0] < p[0] < RW_BASE_X - 0.02]
# Behind the lip tip the silhouette drops to the rear face (the undercut under the lip cannot be
# represented by a section loft - see the .md), then follows the bumper's centre section.
top_tail = lid + [[round(tip_x + 0.005, 4), 0.86], [round(tip_x + 0.011, 4), 0.72]] + rear_face + bump_up
top_y = hood + screen[1:] + roof_line + top_tail

# ------------------------------------------------------------------ tail keyframes (x > 3.4)
# Section points P1..P5 as (z, y) behind the rear window. Sources: lid edge = 03's lid gap line
# (same body opening; rear photo: the lid's side gaps run from the lip down to the lamp tops);
# lip = side-photo profile (heights) and rear-photo width (lid 0.46 m half-width at the lip,
# 329 px at 1.44 mm/px); hips/crest = 03 + 0.015 m (rear photo: silhouette at 0.86 m height
# 0.705 m half-width vs 03 0.69); lamp top 0.62 (side photo); bumper side portions 0.745 m
# half-width (the green stripe wraps round their corners to z 0.743, rear photo) and
# 0.33-0.50 m high (side photo); raised centre section 0.43 m half-width (rear photo x 655 /
# 1265 at 1.42 mm/px) up to the lid's lower edge (0.61 m).
TAIL = {
    #  x       crest (z, y)     belt (z, y)      roof (z, y)
    3.40: ((0.672, 0.928), (0.47, 0.9735), (0.477, 0.990)),
    3.53: ((0.665, 0.915), (0.462, 0.918), (0.30, 0.948)),
    3.66: ((0.652, 0.870), (0.458, 0.868), (0.30, 0.896)),
    3.75: ((0.642, 0.822), (0.455, 0.870), (0.36, 0.895)),
    3.82: ((0.640, 0.790), (0.452, 0.905), (0.42, 0.935)),
    3.90: ((0.660, 0.735), (0.448, 0.930), (0.43, 0.962)),
    3.96: ((0.675, 0.690), (0.446, 0.935), (0.43, 0.968)),
    round(tip_x, 4): ((0.682, 0.660), (0.445, 0.915), (0.43, 0.945)),
    4.005: ((0.688, 0.640), (0.452, 0.668), (0.42, 0.690)),
    4.03: ((0.695, 0.622), (0.445, 0.635), (0.41, 0.650)),
    4.055: ((0.705, 0.505), (0.44, 0.525), (0.42, 0.610)),
    4.08: ((0.66, 0.498), (0.435, 0.52), (0.42, 0.600)),
    R_SIDE_END_X + 0.004: ((0.45, 0.50), (0.43, 0.54), (0.41, 0.590)),
    4.115: ((0.42, 0.515), (0.40, 0.545), (0.36, 0.565)),
    4.135: ((0.34, 0.50), (0.31, 0.515), (0.25, 0.525)),
    L: ((0.0, TAIL_Y), (0.0, TAIL_Y), (0.0, TAIL_Y)),
}
# Ahead of the lip (x < 3.78) the GRP lid is crowned 3-7 cm above its side gaps (photo 01: its
# centre line runs 1-5 cm above 03's flush lid), so P5 sits on that crown at z 0.30. On the lip
# (x 3.82 to the tip) P5 is the lip's square top corner (rear photo: lip top flat to z 0.46) and
# P4 the lid's side edge just under it (the lid gap runs along the lip's outer ends, photos
# 03/05/17). The lip's undercut (photo 01: the lip underside curves forward-down to (3.91, 0.79)
# before the rear face runs back to the lid's lower edge) cannot exist in a one-ring-per-x loft:
# the P3 -> P4 segment closes it as a slope from the hip crest up to the lip's side edge.
tail_xs = sorted(TAIL)
crest_tail_z = [[x, TAIL[x][0][0]] for x in tail_xs]
crest_tail_y = [[x, TAIL[x][0][1]] for x in tail_xs]
belt_tail_z = [[x, TAIL[x][1][0]] for x in tail_xs]
belt_tail_y = [[x, TAIL[x][1][1]] for x in tail_xs]
roof_tail_z = [[x, TAIL[x][2][0]] for x in tail_xs]
roof_tail_y = [[x, TAIL[x][2][1]] for x in tail_xs]

# ------------------------------------------------------------------ crest / belt / rail (front + cabin)
# Cabin: the door top (crest) and the glass base (belt) from photo 01 (body top edge v 553 /
# chrome trim top v 545 at u 800-1400; the sheet's belt line y 285-288 = 0.88 agrees); 03 had
# them 1.5-2 cm higher (0.905 / 0.92). Rail / drip rail and everything ahead of the cowl as 03.
CREST_CABIN = [[round(x, 3), yp(553, x)] for x in (1.65, 2.0, 2.4, 2.8, 3.1)]
BELT_CABIN = [[round(x, 3), yp(545, x)] for x in (1.69, 2.0, 2.4, 2.8, 3.1)]
RAIL_CABIN = [(2478, 146), (2520, 140), (2600, 139), (2700, 143), (2790, 154), (2880, 172),
              (2950, 202), (2990, 232)]                                                   # 02
crest = [[0.0, f_top], [X(1716), Y(440)], [X(1745), Y(410)], [X(1812), Y(392)], [X(1840), Y(318)]]
crest += [p for p in silhouette_top if X(1850) <= p[0] <= X(2255)]
crest += [[X(2300), Y(272)]] + CREST_CABIN + [[3.25, 0.93]] + crest_tail_y
hood_lids = [p for p in hood if p[0] >= 0.03]
belt = [[0.0, f_top], [X(1716), Y(441)]] + [[x, round(y - 0.03, 4)] for x, y in hood_lids]
belt += BELT_CABIN + [[3.25, 0.955]] + belt_tail_y
rail = [[0.0, f_top], [X(1716), Y(441)]] + [[x, round(y - 0.004, 4)] for x, y in hood_lids]
rail += screen[1:-1] + curve(RAIL_CABIN) + [[3.26, 1.0227]] + roof_tail_y

# ------------------------------------------------------------------ lower edge (rockerY) and floor
SILL_Y = Y(530)                                                        # 03 / sheet sill line
BOTTOM = ([[0.0, f_bot], [0.012, round(f_bot - 0.003, 4)]] + SPOILER_EDGE
          + [[0.44, 0.276], [0.476, 0.288]] + FRONT_ARCH
          + [[1.262, 0.31], [1.285, SILL_Y + 0.004], [1.33, SILL_Y], [2.70, SILL_Y], [2.735, 0.29]]
          + REAR_ARCH
          + [[3.62, R_BUMPER_BOT + 0.003], [3.80, R_BUMPER_BOT], [4.0, R_BUMPER_BOT], [4.05, R_BUMPER_BOT + 0.004]]
          + [[x, round(y + 0.004, 4)] for x, y in bump_lo[::-1] if x > 4.05] + [[L, TAIL_Y]])
floor_y = keys([(0, f_bot), (0.03, round(f_bot - 0.012, 4)), (0.2, 0.268), (0.4, 0.258), (0.46, 0.25),
                (FA, 0.2), (X(2300), 0.181), (X(2800), 0.181), (RA, 0.21), (3.653, 0.28), (3.85, 0.318),
                (4.0, R_BUMPER_BOT - 0.01), (4.06, R_BUMPER_BOT - 0.005)]
               + [(x, y) for x, y in bump_lo[::-1]] + [(L, TAIL_Y)])
side_y = keys([(0, 0.40), (0.1155, 0.45), (0.45, 0.50), (FA, 0.56), (X(2300), 0.54), (X(2750), 0.535),
               (RA, 0.54), (3.6, 0.50), (3.9, 0.46), (4.09, 0.45), (4.12, 0.47), (L, TAIL_Y)])

# ------------------------------------------------------------------ plan (sideZ) and z of the section lines
# Nose: bumper face outline (03); cabin: factory plan; 2.45-2.75 blend into the tbp flare shape
# (peak 0.826); behind 3.6 the flare tapers into the bumper side portions (0.745 at 4.0, rear
# photo stripe end) whose rear corners (x 4.09, side photo) turn in to the raised centre section
# (0.43, rear photo) that ends at L.
def side_z_at(x):
    fac = float(np.interp(x, [p[0] for p in half_width_sheet], [p[1] for p in half_width_sheet]))
    if x <= 2.45:
        return fac
    if x <= 2.75:
        t = (x - 2.45) / 0.30
        t = t * t * (3 - 2 * t)
        return fac + (rs_flare(x) - fac) * t
    return rs_flare(x)


side_z = [p for p in nose_plan]
side_z += [[round(x, 4), round(side_z_at(x), 4)] for x in np.arange(0.40, 3.60, 0.02)]
side_z += keys([(3.6, round(side_z_at(3.6), 4)), (3.7, 0.786), (3.8, 0.768), (3.9, 0.754), (4.0, 0.746),
                (4.04, 0.742), (4.065, 0.728), (R_SIDE_END_X - 0.01, 0.70), (R_SIDE_END_X - 0.002, 0.62),
                (R_SIDE_END_X + 0.003, 0.50), (R_SIDE_END_X + 0.007, 0.435), (4.12, 0.425), (4.132, 0.395),
                (4.141, 0.33), (4.1455, 0.22), (L, 0.0)])

ARCH_F = (FRONT_ARCH[0][0] - 0.02, FRONT_ARCH[-1][0] + 0.02)
ARCH_R = (REAR_ARCH[0][0] - 0.02, REAR_ARCH[-1][0] + 0.02)
rocker_z = []
TAIL_UNDER_X = 4.02
for x, z in side_z:
    if ARCH_F[0] <= x <= ARCH_F[1] or ARCH_R[0] <= x <= ARCH_R[1]:
        gap = 0.005                       # arch edge at the flare lip (as 03)
    else:
        gap = 0.04
    if x >= TAIL_UNDER_X:
        continue
    rocker_z.append([x, round(max(0.0, z - gap), 4)])
# Behind x 4.02 the bumper's flat underside runs to the centre and its rounded lower rear corner
# (side photo: face 0.39 m -> bottom 0.34 m) is body colour on the car (rear photo: white down to
# 0.31-0.33 m), so P1 moves in to z 0.10 there and the loft paints that corner (P1->P2) instead
# of drawing it as underbody (P0->P1).
rocker_z += [[TAIL_UNDER_X + 0.012, 0.10], [L - 0.004, 0.08], [L, 0.0]]

# z of the section lines ahead of the tail (03 readings of the factory end views / B-pillar
# section; lid edges at the nose re-read on the plan in 03).
CREST_Z_FRONT, CREST_Z_COWL = 0.56, 0.64
HOOD_EDGE_Z_NOSE, HOOD_EDGE_Z_COWL, HOOD_CORNER_X, HOOD_FRONT_X = 0.383, 0.582, 0.064, 0.042
CABIN_BELT_Z, CABIN_RAIL_Z, REAR_WINDOW_Z = 0.646, 0.538, 0.495
crest_z = keys([(0, 0), (X(1716), 0.3), (X(1745), 0.4), (X(1812), CREST_Z_FRONT - 0.03), (X(1850), CREST_Z_FRONT),
                (X(2255), CREST_Z_COWL), (X(2342), 0.70), (X(2750), 0.71), (X(2990), 0.70), (3.25, 0.69)]
               + crest_tail_z)
belt_z = keys([(0, 0), (HOOD_FRONT_X, 0.3), (HOOD_CORNER_X, HOOD_EDGE_Z_NOSE), (X(2255), HOOD_EDGE_Z_COWL),
               (X(2342), CABIN_BELT_Z), (X(2990), CABIN_BELT_Z - 0.01), (3.25, 0.56)] + belt_tail_z)
roof_z = keys([(0, 0), (HOOD_CORNER_X, 0.16), (X(2255), 0.3), (X(2300), 0.44), (X(2470), CABIN_RAIL_Z),
               (X(2857), CABIN_RAIL_Z - 0.01), (X(2990), REAR_WINDOW_Z), (3.26, 0.49)] + roof_tail_z)

body = {
    "floorY": floor_y,
    "rockerY": simplify(sorted(BOTTOM), 0.002),
    "rockerZ": simplify(rocker_z, 0.003),
    "sideY": side_y,
    "sideZ": simplify(side_z, 0.002),
    "crestY": simplify(sorted(crest), 0.003),
    "crestZ": crest_z,
    "beltY": simplify(sorted(belt), 0.003),
    "beltZ": belt_z,
    "roofY": simplify(sorted(rail), 0.003),
    "roofZ": roof_z,
    "topY": simplify(sorted(top_y), 0.002),
}
for k in ("sideZ", "rockerZ"):
    c = body[k]
    if c[0][0] > 0:
        c.insert(0, [0.0, 0.0])
    else:
        c[0][1] = 0.0
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


def body_half_width(x, y):
    """Outer z of the lofted section at x, at height y."""
    sec = half_section(body, x)
    best = 0.0
    for (z0, y0), (z1, y1) in zip(sec, sec[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            best = max(best, z0 + (z1 - z0) * (y - y0) / (y1 - y0))
    return best


# ------------------------------------------------------------------ end-photo calibration (02 / 03)
# Lateral scale per depth from the 520 mm plates and the tracks (tyre centres at the ground):
#   front: plate x 760-1120 (360 px), tyres 507.5 / 1379.5 (872 px = 1.372 m) -> camera 9.7 m
#          from the plate; centre line u 943.5 (tyres, silhouette).
#   rear:  plate x 776-1143 (367 px), tyres 514 / 1404 (890 px = 1.394 m) -> 9.4 m; centre 959.5.
F_PLATE_S, F_D, F_XP, F_CU = 0.520 / 360, 9.71, 0.01, 943.5
R_PLATE_S, R_D, R_XP, R_CU = 0.520 / 367, 9.43, 4.13, 959.5


def fz(u, x):
    """front photo column -> |z| for a feature at car x."""
    return round(abs(u - F_CU) * F_PLATE_S * (F_D + x - F_XP) / F_D, 4)


def rz(u, x):
    """rear photo column -> |z| for a feature at car x."""
    return round(abs(u - R_CU) * R_PLATE_S * (R_D + R_XP - x) / R_D, 4)


def rz2(ul, ur, x):
    """mean |z| of a feature seen on both halves (left column, right column)."""
    return round((rz(ul, x) + rz(ur, x)) / 2, 4)


def fz2(ul, ur, x):
    return round((fz(ul, x) + fz(ur, x)) / 2, 4)


# ------------------------------------------------------------------ decals
# Slot ids as 03 (and 01/02) wherever the RS has the same part; new: carrera-script (side stripe
# with the 'Carrera' lettering) and script-rear ('Carrera RS' on the ducktail; 05 uses the same id
# for its '911' script). Budget: <= 40 ids in the union with each neighbour (the shader draws 40).
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
AMBER = "#e59a35"
BLACK = "#1c1c1c"
# Museum car's decal / wheel green: median of the lit stripe (photo 01: #0e881d) and 'PORSCHE'
# decal (photo 03: #26a421) pixels -> #1a9630.
GREEN = "#1a9630"
FRONT = [-0.05, 0.45]
REAR = [L - 0.45, L + 0.05]

# Side glass (photo 01, inner edges of the chrome frames; vent window + door glass one outline,
# lowest-front first, clockwise in this view).
DLO_DOOR = pns([(792, 541), (850, 474), (895, 428), (915, 419), (1000, 418), (1080, 419), (1150, 421),
                (1168, 424), (1150, 480), (1138, 541), (1000, 541), (900, 541)])
DLO_QUARTER = pns([(1172, 541), (1186, 480), (1196, 441), (1207, 437), (1260, 450), (1320, 474), (1370, 501),
                   (1400, 521), (1411, 532), (1398, 540), (1300, 542), (1200, 542)])
# Chrome frame, outer edge: A-pillar base -> over the door glass -> quarter window -> rear tip.
TRIM = pns([(758, 548), (820, 478), (880, 413), (900, 405), (1000, 404), (1100, 406), (1172, 410),
            (1200, 425), (1260, 437), (1330, 463), (1385, 494), (1414, 520), (1420, 537)])
VENT = pns([(887, 545), (933, 418)])
# Drip rail (roof gutter) above the frame, continuing down the fastback edge (photos 01/05).
DRIP = pns([(880, 400), (1000, 397), (1100, 399), (1170, 402), (1230, 410), (1300, 430), (1380, 458),
            (1450, 480)])
# Door gap (photo 01: front edge u 637-640, bottom v 782-785, slanted rear edge to the B-pillar;
# the sheet's aperture front edge x 2275 = 1.381 m agrees).
DOOR = pns([(690, 560), (660, 572), (645, 592), (639, 620), (637, 660), (638, 700), (640, 740), (643, 760),
            (648, 778), (660, 784), (800, 784), (1000, 782), (1030, 780), (1060, 775), (1080, 765),
            (1095, 745), (1110, 710), (1125, 670), (1140, 630), (1150, 600), (1155, 570), (1153, 550)])
# Pull handle with push button (photo 01, bar u 1052-1128, button 1128-1143, v 588-608).
HANDLE = pns([(1052, 594), (1052, 607), (1143, 608), (1143, 591)])
# Front lamp's amber wrap-round (photo 01 zoom): front end u 120, top v 699-700, slanted rear edge
# (200, 700) -> (218, 728), bottom on the bumper line v 728.
IND_SIDE = pns([(121, 728), (123, 701), (200, 699), (218, 728)])
# Rear lamp side lens: bottom v 712 (u 1680-1781), slanted front edge to (1700, 665), top v 663-667.
TAIL_SIDE = pns([(1680, 712), (1700, 665), (1778, 663), (1781, 712)])
# Stripe on the bumpers: the flank stripe continues round both bumpers (front: across the full
# face, photo 02; rear: to the reflectors, photo 03). Side-plane bands at the side-photo heights
# with facing 0 so they wrap onto the bumper faces; the rear one stops at |z| 0.535 (the
# stripe's inner end on the rear face, rear photo x 587 / 1339).
F_STRIPE = (yp(756.5, 0.3), yp(746, 0.3))            # v 745-757 (u 150-280)
R_STRIPE = (yp(735, 3.9), yp(722, 3.9))              # v 722-735 (u 1600-1800)
R_STRIPE_Z0 = rz2(587, 1339, 4.08)


def script_blobs():
    """'Carrera' stripe + lettering on the LEFT flank (photo 01 green pixels, u 540-1280,
    v 690-775): the green areas (stripe pieces, letter outlines and counters - the letters
    themselves are white, reversed out of the stripe) as simplified rings (blobs >= 180 px^2,
    Douglas-Peucker 4.5 px = 1 cm; smaller specks are below one art pixel)."""
    im = cv2.imread(PHOTO_SIDE).astype(np.int32)
    b_, g_, r_ = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    x0, y0, x1, y1 = 540, 690, 1280, 775
    m = (((g_ - r_) > 45) & ((g_ - b_) > 35)).astype(np.uint8)[y0:y1, x0:x1] * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    blobs = []
    for c in cnts:
        if cv2.contourArea(c) < 180:
            continue
        ap = cv2.approxPolyDP(c, 4.5, True)[:, 0, :].astype(float)
        ap[:, 0] += x0
        ap[:, 1] += y0
        blobs.append([pn(u, v) for u, v in ap])
    return sorted(blobs, key=lambda b: min(p[0] for p in b))


def even_odd_path(blobs):
    """One closed polygon for several rings (even-odd fill): each ring starts and ends at its
    lowest point (the anchor); the path hops forward from anchor to anchor and finally returns
    over the same anchors, so every bridge is traversed twice (zero area)."""
    path, anchors = [], []
    for b in blobs:
        k = min(range(len(b)), key=lambda i: (b[i][1], b[i][0]))
        ring = b[k:] + b[:k + 1]
        anchors.append(ring[0])
        path.extend(ring)
    return path + anchors[::-1][1:]


SCRIPT_BLOBS = script_blobs()
# The right flank carries the mirror image: the script reads front-to-back on the left side
# and rear-to-front on the right, 'C' behind the front arch on the left and ahead of the rear
# arch on the right (photos 07 / 22: right side of two other RS 2.7, lettering reading normally
# with the 'C' at the rear). Mirror about the middle of the stripe's own extent, so the stripe
# ends stay at the arches.
_SX = [p[0] for b in SCRIPT_BLOBS for p in b]
SCRIPT_XM = round((min(_SX) + max(_SX)) / 2, 4)
SCRIPT_L = even_odd_path(SCRIPT_BLOBS)
SCRIPT_R = even_odd_path(sorted([[[round(2 * SCRIPT_XM - x, 4), y] for x, y in b[::-1]] for b in SCRIPT_BLOBS],
                                key=lambda b: min(p[0] for p in b)))

decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("window-trim", TRIM, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("vent-divider", VENT, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", DRIP, "chrome", CHROME, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.55, 2]),
    side_decal("door-handle", HANDLE, "chrome", CHROME, depth=[0.6, 2]),
    # No sill trim strip on the museum Sport (photo 01: white sill below the stripe) -> no rocker-trim.
    box("side", "bumper-front", 0.0, FRONT_ARCH[0][0] - 0.01, F_STRIPE[0], F_STRIPE[1], "paint", GREEN,
        depth=[0.0, 2], facing=0.0),
    box("side", "bumper-rear", REAR_ARCH[-1][0] + 0.01, L, R_STRIPE[0], R_STRIPE[1], "paint", GREEN,
        depth=[R_STRIPE_Z0, 2], facing=0.0),
    side_decal("indicator-side", IND_SIDE, "lens", AMBER, depth=[0.5, 2], facing=0.25),
    side_decal("taillight-side", TAIL_SIDE, "lens", AMBER, depth=[0.5, 2], facing=0.25),
    side_decal("carrera-script", SCRIPT_L, "paint", GREEN, depth=[0.6, 2], facing=0.3, side="left"),
    side_decal("carrera-script-r", SCRIPT_R, "paint", GREEN, depth=[0.6, 2], facing=0.3, side="right"),
]

# Front plane (photo 02, averaged left/right, at the lamp plane x ~0.1): black horn grille
# (MY1973) u 567-662 / 1210-1305, clear lens to the divider 562 / 1312, amber outboard to
# 440 / 1440; heights as 03 (same F-series unit; photo 01: 0.50-0.57 incl. the wrap-round).
LAMP_B, LAMP_T = Y(437), Y(405)                                   # 03 (factory sheet housing)
G_IN, G_OUT = fz2(665, 1208, 0.1), fz2(562, 1312, 0.1)
A_IN, A_OUT = fz2(505, 1368, 0.12), fz2(440, 1440, 0.15)
# No front plate: the studio car wears a museum display plate, the 1972 factory photos
# (photos 14 / 15) show the car without one; the decal budget (40 slots per morph) goes to the
# right-hand script instead.
decals += [
    box("front", "horn-grille", G_IN, G_OUT, LAMP_B, LAMP_T, "satin", BLACK, depth=FRONT, facing=0.3,
        stripes=[0.012, 0.45]),
    box("front", "parking-front", G_OUT, A_IN, LAMP_B, LAMP_T, "lens", "#eef1f2", depth=FRONT, facing=0.25),
    box("front", "indicator-front", A_IN, A_OUT, LAMP_B, LAMP_T, "lens", AMBER, depth=FRONT, facing=0.25),
]

# Rear plane (photo 03, lateral scale at each part's depth; heights from the side photo: lamp
# lens bottom 0.511 (v 712), rear-face lens 61 px tall at 1.43 mm/px).
T_BOT = yp(712, 3.95)
T_TOP = round(T_BOT + 61 * 1.432e-3, 4)
RED_IN, RED_CLR = rz2(652, 1278, 4.03), rz2(611, 1318, 4.03)     # red 611-652 (L) / 1278-1318 (R)
CLR_AMB, AMB_OUT = rz2(578, 1346, 4.03), rz2(492, 1427, 4.02)    # clear 578-610, amber 492-577 / 1346-1427
REFL_IN, REFL_OUT = rz2(651, 1277, 4.09), rz2(594, 1332, 4.09)   # reflectors 594-651 / 1277-1332
REFL_TOP = round(T_BOT - (897 - 869) * 1.423e-3, 4)              # v 897-930, lens bottom v 869
REFL_BOT = round(T_BOT - (930 - 869) * 1.423e-3, 4)
PLATE_TOP = round(T_BOT + (869 - 843) * 1.417e-3, 4)             # plate v 843-937
PLATE_BOT = round(T_BOT - (937 - 869) * 1.417e-3, 4)
LID_BOT = rear_face[-1][1]                                        # lid's lower edge (0.62)
# 'PORSCHE' decal on the lid's rear face just above its lower edge (v 762-793, lid edge v 805):
# end bars + letter blocks, symmetric comb (distances from the centre line, px at 1.430 mm/px).
BADGE_B = round(LID_BOT + (805 - 793) * 1.43e-3, 4)
BADGE_T = round(LID_BOT + (805 - 763) * 1.43e-3, 4)
BADGE_BLOCKS = [(0, 45), (55, 122), (134, 201), (212, 262), (271, 303)]
badge = [[0.0, BADGE_B], [0.0, BADGE_T]]
for i, (a, b_) in enumerate(BADGE_BLOCKS):
    za, zb = round(a * 1.43e-3, 4), round(b_ * 1.43e-3, 4)
    if i:
        badge += [[za, BADGE_B], [za, BADGE_T]]
    badge += [[zb, BADGE_T], [zb, BADGE_B]]
# 'Carrera RS' on the right-hand side of the lip's rear face: x 1030-1200, v 640-665.
LIP_SCRIPT = (rz(1030, 3.97), rz(1200, 3.97), round(LID_BOT + (805 - 665) * 1.44e-3, 4),
            round(LID_BOT + (805 - 640) * 1.44e-3, 4))
decals += [
    box("rear", "taillight", RED_IN, RED_CLR, T_BOT, T_TOP, "lens", "#b8231d", depth=REAR, facing=0.25),
    box("rear", "reverse-light", RED_CLR, CLR_AMB, T_BOT, T_TOP, "lens", "#eef1f2", depth=REAR, facing=0.25),
    box("rear", "indicator-rear", CLR_AMB, AMB_OUT, T_BOT, T_TOP, "lens", AMBER, depth=REAR, facing=0.25),
    box("rear", "reflector-rear", REFL_IN, REFL_OUT, REFL_BOT, REFL_TOP, "lens", "#a51d1a", depth=REAR, facing=0.3),
    box("rear", "plate-rear", 0.0, rz(1143, 4.13), PLATE_BOT, PLATE_TOP, "satin", BLACK, depth=REAR, facing=0.3),
    {"id": "badge-rear", "plane": "rear", "kind": "fill", "points": badge, "finish": "paint", "color": GREEN,
     "depth": REAR, "facing": 0.2},
    box("rear", "script-rear", LIP_SCRIPT[0], LIP_SCRIPT[1], LIP_SCRIPT[2], LIP_SCRIPT[3], "paint", GREEN,
        depth=[3.85, L + 0.05], facing=0.2, side="right"),
]

# Top plane. Windscreen / rear window / cowl slot / crest / filler flap / lid front: the 03
# shell values (same parts). Engine grille: black louvres at the front of the ducktail lid,
# photo 01 x 3.51-3.74 (u 1555-1650), half-width 0.36 (tbp-83845 plan 115 px; photos 09/21: ~80 %
# of the lid width).
screen_top = [[X(2262), 0.0], [X(2262), 0.60], [X(2470), 0.5], [X(2478), 0.0]]       # 02/03
rear_top = [[X(2862), 0.0], [X(2862), 0.47], [X(3100), 0.46], [X(3105), 0.0]]        # 02/03
GRILLE_X0, GRILLE_X1 = round(xt(1555), 4), round(xt(1650), 4)
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rear_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.9, 2]},
    box("top", "engine-grille", GRILLE_X0, GRILLE_X1, 0.0, 0.36, "satin", BLACK, stripes=[0.016, 0.5],
        facing=0.3, depth=[0.8, 2]),
    box("top", "cowl-grille", X(2215), X(2250), 0.0, 0.25, "satin", "#2b2b2b", stripes=[0.012, 0.5], facing=0.3,
        depth=[0.8, 2]),
    box("top", "crest", HOOD_FRONT_X + 0.012, HOOD_FRONT_X + 0.052, 0.0, 0.022, "chrome", "#c9a24e", facing=0.3,
        depth=[0.45, 2]),
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left",
     "points": [[round(X(2195) + 0.097 * math.cos(a), 4), round(0.678 + 0.0465 * math.sin(a), 4)]
                for a in np.linspace(0, 2 * math.pi, 13)],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3, "depth": [0.7, 2]},
    {"id": "hood-gap", "plane": "top", "kind": "line",
     "points": [[HOOD_FRONT_X, 0.0], [HOOD_FRONT_X + 0.002, 0.3], [HOOD_CORNER_X - 0.008, HOOD_EDGE_Z_NOSE - 0.012],
                [HOOD_CORNER_X, HOOD_EDGE_Z_NOSE], [X(2250), HOOD_EDGE_Z_COWL]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
    # Lid gap along the ducktail lid's sides (03's lid edge line), to the lid's lower edge.
    {"id": "lid-gap", "plane": "top", "kind": "line",
     "points": [[RW_BASE_X + 0.028, 0.0], [RW_BASE_X + 0.028, 0.47], [3.90, 0.458], [4.03, 0.445], [4.035, 0.0]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]
assert len({d["id"] for d in decals}) == len(decals), "duplicate decal ids"

# ------------------------------------------------------------------ parts
# Tyres with explicit aspect ratios -> computed (TRACING.md): 185/70 R15 = 0.381 + 2*0.185*0.70 =
# 0.640 m, 215/60 R15 = 0.381 + 2*0.215*0.60 = 0.639 m (photo 01: loaded radius hub -> contact
# 131.7 px = 0.304 m, i.e. ~1.6 cm deflection of a 0.640 m tyre). Fuchs forged 5-spoke (specs /
# geometry.json 04); museum car: green spoke star matching the script (photos 01/02/05),
# polished lip.
TYRE_F = round(0.381 + 2 * 0.185 * 0.70, 4)
TYRE_R = round(0.381 + 2 * 0.215 * 0.60, 4)
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
        "front": {"diameter": TYRE_F, "width": 0.185, "rim": 0.381, "design": "fuchs",
                  "face": GREEN, "lip": "#d9dcdf", "caliper": None},
        "rear": {"diameter": TYRE_R, "width": 0.215, "rim": 0.381, "design": "fuchs",
                 "face": GREEN, "lip": "#d9dcdf", "caliper": None},
    },
    # Same headlamp as 02/03 (unchanged part; photo 02: ring 160 px = 0.238 m, centres 0.607 /
    # 0.622 m from the centre line, mean 0.614).
    "headlight": {
        "centre": [X(1832), 0.716, 0.614],
        "outline": [[round(math.cos(a) * 0.095, 4), round(math.sin(a) * 0.095, 4)]
                    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)],
        "yaw": 3,
        "pitch": 15,
        "ring": 0.024,
        "ringColor": "#e3e6e9",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    },
    # Rectangular chrome mirror on the driver's (left) door (MY1973, geometry.json 04): photo 02
    # head u 1405-1495 / v 535-580 at the door (x 1.5): 0.15 m wide, 0.075 m tall, inner edge
    # z 0.769; photo 01: head centre u 695 -> x 1.515, v 525.
    "mirror": {"at": [round(xn(695), 4), yp(525, 1.5), fz(1405, 1.5)], "size": [0.05, 0.075, 0.15],
               "shape": "flag", "color": CHROME, "finish": "chrome", "sides": "left"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    # Single tailpipe under the bumper on the car's LEFT (geometry.json 04; photo 03: pipe
    # u 530-590 / v 955-1020 -> z 0.54, r 0.03; side photo: tip at u 1826, v 783).
    "exhausts": [[round(xt(1826), 4), yp(783, 4.1), -rz(560, 4.1), 0.03]],
}

out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
with open(out, "w") as f:
    json.dump(car, f, indent=1)

# ------------------------------------------------------------------ calibration for the checks
RS_SIDE_S = WB / (1612.33 - 895.63)
# Side photo, body-aligned: the model's hubs placed where the DELTA mapping puts them (the
# model body then overlays the photo's body; the drawn tyres show the model's unladen 0.64 m
# tyres vs the loaded, lower-riding museum car).
wf_v = GROUND_V - (TYRE_F / 2 - (DELTA_A + DELTA_B * FA)) / S01
wr_v = GROUND_V - (TYRE_R / 2 - (DELTA_A + DELTA_B * RA)) / S01
calib = {
    # tbp-83845 side view: hub circle fits; tipF places the model's front axle on the drawn hub.
    "side": {"image": os.path.relpath(RSDRAW, ROOT), "wheelF": [895.63, 325.98], "wheelR": [1612.33, 325.89],
             "tipF": round(895.63 - FA / RS_SIDE_S, 1), "crop": [590, 0, 1946, 440]},
    "side_photo": {"image": os.path.relpath(PHOTO_SIDE, ROOT), "wheelF": [HUB_F[0], round(wf_v, 1)],
                   "wheelR": [HUB_R[0], round(wr_v, 1)], "tipF": round(HUB_F[0] - FA / S01, 1),
                   "crop": [40, 330, 1880, 950]},
    # tbp-83845 plan (x scale of its side view; widths ~2.6 % wide).
    "top": {"image": os.path.relpath(RSDRAW, ROOT), "tipF": round(RS_RA_PX - RA / RS_S, 1),
            "tipR": round(RS_RA_PX + (L - RA) / RS_S, 1), "centreY": RS_CY, "crop": [590, 440, 1946, 1026]},
    # Studio end photos at the bumper-plane scale. groundY = where the ground would be at that
    # plane (the camera is ~1.1 m high, so it lies below the tyre contact rows 1133 / 1137):
    # fitted on the bumper-plane parts (front stripe / plate / lamps; rear lamps / reflectors /
    # plate) -> 1250 / 1228. Parts farther from the camera draw too high and too wide.
    "front": {"image": os.path.relpath(PHOTO_FRONT, ROOT), "centreX": F_CU, "groundY": 1250,
              "left": F_CU - 0.8 / F_PLATE_S, "right": F_CU + 0.8 / F_PLATE_S, "width": 1.6, "crop": [300, 250, 1640, 1180]},
    "rear": {"image": os.path.relpath(PHOTO_REAR, ROOT), "centreX": R_CU, "groundY": 1228,
             "left": R_CU - 0.8 / R_PLATE_S, "right": R_CU + 0.8 / R_PLATE_S, "width": 1.6, "crop": [300, 250, 1640, 1180]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)

if __name__ == "__main__":
    print("wrote", os.path.relpath(out, ROOT), "L", L, "axles", FA, RA, "KT", round(KT, 4),
          "DELTA %.4f %+.5f x" % (DELTA_A, DELTA_B))
    for (name, x, d), r in zip(DELTA_ROWS, DELTA_RES):
        print("   landmark %-36s x %.3f  delta %.4f  resid %+.4f" % (name, x, d, r))
    print("decals", len(decals), "points", sum(len(d["points"]) for d in decals), "script pts", len(SCRIPT_L), len(SCRIPT_R), "XM", SCRIPT_XM)
    print("height", max(v for _, v in body["topY"]), "width", 2 * max(v for _, v in body["sideZ"]))

    # Perspective check of the side photo (the flat, hub-calibrated check-side-photo.png cannot
    # place the centre-plane nose / tail: they are ~0.4-0.8 m farther from the camera than the
    # hubs). Uses the pinhole photo-fit helper of the 996 trace (research/traces/
    # 11-996-1-1998.photofit.py): hubs pinned, camera distance / height grid-searched on a
    # GrabCut mask of the photo. Hub height in the model frame 0.349 m = the photo's loaded hub
    # height (0.304 m) + the mean DELTA (0.045 m) - the museum car sits lower on its wheels.
    import importlib.util
    spec = importlib.util.spec_from_file_location("photofit", os.path.join(HERE, "11-996-1-1998.photofit.py"))
    photofit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(photofit)
    stats = photofit.check(car, PHOTO_SIDE, HUB_F, HUB_R, (60, 350, 1860, 935),
                           os.path.join(HERE, STOP, "check-side-photo-persp.png"), facing="left", ground_row=905,
                           D_grid=(6, 8, 9, 10, 11, 12, 14, 17, 20, 25), Y_grid=[0.5, 0.7, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5],
                           hub_height=0.349)
    print("perspective side-photo check:", stats)
