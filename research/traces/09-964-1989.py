"""Trace: 09-964-1989 — 911 Carrera 2 Coupé (964, MY1990–91), spoiler retracted.

References (see research/blueprints/09-964-1989/sources.json, research/photos/09-964-1989/sources.json):
  COUPE   blueprints/vec-10947 "Porsche 911 Carrera 964 (1990)" colour 4-view (side / front /
          rear / plan), the-blueprints.com vector preview (watermarked). Upper envelope (roof,
          glasshouse, wings, deck, tail), plan view, front/rear views (lateral positions).
  TARGA   blueprints/vec-23631 "Porsche 911 964 Targa (1993)", same vendor: cross-check.
  AUTOCAR blueprints/tbp-8812 package drawing (side, spoiler raised): lower-body check.
  PHOTO01 photos/01-side-left.jpg — official Porsche studio photo (P13_0147) of a launch
          Carrera 4, orthographic left profile ("tracing": "side"). Lower body: arch lips, sills,
          bumper bottoms, bumper joints, lamp units, door shut lines, handle, repeater, mirror,
          filler flap.
  PHOTO10 photos/10-front.jpg, PHOTO20 photos/20-rear.jpg (white-studio 1991 Carrera 2, head-on)
          and photos/21-rear.jpg (period press photo, European plate): lamp / plate / intake /
          exhaust layout of the front and rear faces.
Official figures (research/specs.json, geometry.json → Porsche 1991 brochure): L 4250, W 1652,
H 1310 (unladen), WB 2272, tracks 1380 / 1374 mm, 205/55 ZR16 front, 225/50 ZR16 rear on 6J / 8J
x 16 "Design 90" wheels.

Calibration (every image on its own):
  COUPE side — tyre outlines fitted as circles (40 edge points each, mean residual 0.25 px):
          front (229.82, 279.38), rear (624.34, 277.90) → WB 394.52 px = 2272 mm → 5.7589 mm/px;
          axle height = official tyre radius 0.316 m. Tips 72.5 / 809.5 px → length 4.245 m
          (official 4.250, -0.1 %); roof 1.299 m (official 1.310 unladen, -0.8 %).
  PHOTO01 — rim-lip circles fitted on 180 rays (research: scratch rimfit, residual 0.5 px):
          front (457.56, 529.91) r 95.64, rear (1426.16, 533.25) r 95.51 → WB 968.6 px →
          2.3457 mm/px. Check: rim-lip Ø 448 mm = 16" flange ✓. Apparent length 4.17 m: the
          tips lie on the centre line, 0.69 m behind the calibrated wheel plane, so they appear
          ~4 % closer to the image centre (camera ≈ 17 m away) — the COUPE tips are kept.
          Lower-body heights read here sit on the wheel plane (sills, arch lips, bumper
          corners), so they need no perspective correction.
  COUPE plan — tips 73.0 / 808.0 px, centre row 629.0. Its drawn width is 2.6 % over the
          official 1652 mm, so it has its own lateral scale (1652 mm / widest outline).
  COUPE front / rear — centre 1056.1 / 1056.0 px, lateral scale = plan lateral scale (both
          widest outlines = 149.4 px), vertical: ground (tyre bottoms) ↔ roof = 1.299 m.
Discrepancies found and how they were resolved (details in research/traces/09-964-1989.md):
  the vendor side view puts the bumpers 3 cm low, the rear arch lip 2.6 cm low and the
  body-colour rear bumper 7 cm too deep; PHOTO01, PHOTO05/08, PHOTO20 and the AUTOCAR drawing
  agree with each other, so the lower body comes from PHOTO01.

Run: research/tools/venv python research/traces/09-964-1989.py
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import SideCalib, half_section, mono, simplify  # noqa: E402

STOP = "09-964-1989"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
COUPE = os.path.join(BP, "vec-10947_porsche-911-carrera-964-1990_4view-dims-watermarked.jpg")
PHOTO01 = os.path.join(PH, "01-side-left.jpg")
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------ official figures
WB = 2.272
WIDTH = 1.652
TRACK_F, TRACK_R = 1.380, 1.374
TYRE_F = 0.4064 + 2 * 0.205 * 0.55     # 205/55 R16 → 0.6319 m
TYRE_R = 0.4064 + 2 * 0.225 * 0.50     # 225/50 R16 → 0.6314 m
RIM = 0.4064                          # 16 in

# ------------------------------------------------------------------ COUPE drawing
img = cv2.imread(COUPE)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
PAINT_HUE = 102  # the sheet's body colour (OpenCV hue)
paint = ((np.abs(hsv[:, :, 0].astype(int) - PAINT_HUE) <= 8) & (hsv[:, :, 1] >= 110)).astype(np.uint8)
paint = cv2.morphologyEx(paint, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))


def first_edge(x, y0, y1, thr=200.0):
    """Top-down: first crossing of the outline stroke (outer edge), sub-pixel."""
    col = gray[y0:y1, x]
    for i in range(1, len(col)):
        if col[i] < thr <= col[i - 1]:
            return y0 + i - 1 + (col[i - 1] - thr) / (col[i - 1] - col[i])
    return None


def last_edge(x, y0, y1, thr=200.0):
    """Bottom-up: last crossing of the outline stroke, sub-pixel."""
    col = gray[y0:y1, x]
    for i in range(len(col) - 1, 0, -1):
        if col[i - 1] < thr <= col[i]:
            return y0 + i - 1 + (thr - col[i - 1]) / (col[i] - col[i - 1])
    return None


def paint_span(x, y0, y1):
    ys = np.nonzero(paint[y0:y1, x])[0]
    return (y0 + ys[0], y0 + ys[-1]) if len(ys) else None


WHEEL_F = (229.82, 279.38)
WHEEL_R = (624.34, 277.90)
TIP_X, TAIL_X = 72.5, 809.5
side = SideCalib(WHEEL_F, WHEEL_R, WB, TYRE_F / 2, TIP_X)


def C(px, py):
    """COUPE side-view pixel → car [x, y]."""
    x, y = side.to_car((px, py))
    return [round(x, 4), round(y, 4)]


def curve(points):
    return [C(px, py) for px, py in points]


def ycar(px, py):
    return C(px, py)[1]


def xcar(px):
    return C(px, 200)[0]


L = round(side.to_car((TAIL_X, 250))[0], 4)
FA = round(side.front_axle, 4)
RA = round(FA + WB, 4)

# ------------------------------------------------------------------ PHOTO01
pgray = cv2.GaussianBlur(cv2.imread(PHOTO01, cv2.IMREAD_GRAYSCALE).astype(float), (3, 3), 0)
P_WF, P_WR = (457.56, 529.91), (1426.16, 533.25)
_pf, _pr = np.array(P_WF), np.array(P_WR)
P_S = WB / np.linalg.norm(_pr - _pf)
P_U = (_pr - _pf) / np.linalg.norm(_pr - _pf)
P_N = np.array([P_U[1], -P_U[0]])
if P_N[1] > 0:
    P_N = -P_N


def photo_px(x, y):
    """car (x, y) arrays → PHOTO01 pixel coordinates (wheel-plane similarity transform)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    p = _pf[None, :] + ((x - FA) / P_S)[..., None] * P_U[None, :] + ((y - TYRE_F / 2) / P_S)[..., None] * P_N[None, :]
    return p


def photo_low_edge(x, y_start, dark=45.0, run=0.02, step=0.0025):
    """Scan down from y_start at car x; first y where PHOTO01 turns black (< dark) for ≥ run m.
    The black is the wheel well inside the arches and the shadowed underside elsewhere."""
    ys = np.arange(y_start, 0.05, -step)
    p = photo_px(np.full_like(ys, x), ys)
    v = map_coordinates(pgray, [p[:, 1], p[:, 0]], order=1, mode="nearest")
    need = int(round(run / step))
    d = v < dark
    for i in range(1, len(ys) - need):
        if d[i:i + need].all() and not d[i - 1]:
            return float(ys[i] + step / 2)
    return None


# ------------------------------------------------------------------ upper side silhouette (COUPE)
# Outer edge of the outline stroke (grey < 200). Watermark shadows (grey ≥ 179 on white) push
# that edge up; where it is not 0.5–3.5 px above the paint (a clean stroke), paint top − 2 px
# (the stroke width) is used. In the glass bands (screen, rear window, spoiler grille, tail lamp)
# the stroke edge is used and watermark hits are bridged from the neighbours.
GLASS_BANDS = [(322, 404), (572, 681), (700, 738), (783, 795), (116, 138)]


def in_bands(x):
    return any(a <= x <= b for a, b in GLASS_BANDS)


top_px = {}
for x in range(int(TIP_X), int(TAIL_X) + 1):
    fe = first_edge(x, 100, 300)
    ps = paint_span(x, 100, 335)
    pt = ps[0] if ps else None
    if in_bands(x):
        top_px[x] = fe
    elif fe is not None and pt is not None and 0.5 <= pt - fe <= 3.5:
        top_px[x] = fe
    elif pt is not None:
        top_px[x] = pt - 2.0
    else:
        top_px[x] = fe
xs_sorted = sorted(top_px)
vals = np.array([top_px[x] if top_px[x] is not None else np.nan for x in xs_sorted])
for i, x in enumerate(xs_sorted):
    if not in_bands(x):
        continue
    lo, hi = max(0, i - 8), min(len(vals), i + 9)
    if np.isnan(vals[i]) or vals[i] < np.nanmedian(vals[lo:hi]) - 3:
        top_px[x] = None
known = [(x, top_px[x]) for x in xs_sorted if top_px[x] is not None]
kx, ky = zip(*known)
for x in xs_sorted:
    if top_px[x] is None:
        top_px[x] = float(np.interp(x, kx, ky))
# Headlamp glass seen edge-on (hand-read at 10x; the watermark "eprints.com" crosses it).
LAMP_EDGE = [(117, 238), (119, 235), (120.5, 230), (122, 225), (123.5, 220), (125, 215), (127, 210),
             (130, 205), (135, 201), (140, 200)]
for x in range(117, 141):
    top_px[x] = float(np.interp(x, *zip(*LAMP_EDGE)))
# Antenna foot + watermark on the roof (x 420–433) and watermark on the rear window (x 596–621,
# read by hand at 590 / 605 / 620 / 635 px: 129 / 134.5 / 140.5 / 146): bridged.
for x in range(420, 434):
    top_px[x] = top_px[419] + (top_px[434] - top_px[419]) * (x - 419) / 15
for x in range(596, 622):
    top_px[x] = float(np.interp(x, [590, 605, 620, 635], [129.0, 134.5, 140.5, 146.0]))
TOP = {x: C(x, top_px[x]) for x in sorted(top_px)}

# ------------------------------------------------------------------ lower side silhouette (PHOTO01)
# Body-colour lower edge = where PHOTO01 turns black: the wheel wells above the tyres and the
# shadowed underside below the sills / bumpers. Scans start below the lamp units and the
# quarter window. Arch ranges from the scan itself (front 0.55–1.31, rear 2.80–3.57 m).
LOW_START = [(0.16, 0.33), (0.545, 0.95), (1.31, 0.60), (2.795, 0.78), (3.57, 0.46), (4.15, None)]


def low_start(x):
    s = None
    for x0, y0 in LOW_START:
        if x >= x0:
            s = y0
    return s


LOW = {}
for x in np.round(np.arange(0.16, 4.15, 0.01), 3):
    y = photo_low_edge(float(x), low_start(x))
    if y is not None:
        LOW[float(x)] = round(y, 4)
# Nose: bumper-corner profile read on a 1 cm car-space grid of PHOTO01; x shifted by the
# perspective offset of the centre-line nose (-0.065 m at the tip, tapering to 0 at 0.3 m).
NOSE_PHOTO = [(0.065, 0.30), (0.08, 0.27), (0.10, 0.24), (0.13, 0.215), (0.16, 0.20)]
# Tail: rear-bumper lower corner and rear face (PHOTO01 1 cm grid; tail tip = COUPE length).
TAIL_PHOTO = [(4.17, 0.325), (4.20, 0.345), (4.225, 0.375), (L, 0.41)]


def nose_x(xp):
    return xp - 0.065 * max(0.0, 1 - xp / 0.3)


rockerY = [[0.0, 0.30]] + [[round(nose_x(x), 4), y] for x, y in NOSE_PHOTO[1:]]
rockerY += [[x, y] for x, y in sorted(LOW.items())]
rockerY += [[x, y] for x, y in TAIL_PHOTO]

# ------------------------------------------------------------------ plan view (COUPE)
PLAN_TIP_F, PLAN_TIP_R = 73.0, 808.0
PLAN_CY = 629.0
P_LONG = L / (PLAN_TIP_R - PLAN_TIP_F)


def plan_edges(x):
    col_paint = np.nonzero(paint[460:800, x])[0]
    if not len(col_paint):
        return None
    pt, pb = 460 + col_paint[0], 460 + col_paint[-1]
    ft = first_edge(x, 460, 640)
    fb = last_edge(x, 620, 800)
    top = ft if (ft is not None and 0.5 <= pt - ft <= 3.5) else pt - 2.0
    bot = fb if (fb is not None and 0.5 <= fb - pb <= 3.5) else pb + 2.0
    return top, bot


plan_half_px = {}
for x in range(int(PLAN_TIP_F) + 1, int(PLAN_TIP_R)):
    e = plan_edges(x)
    if e:
        plan_half_px[x] = (e[1] - e[0]) / 2
for x in range(372, 399):   # door mirrors: bridged
    plan_half_px[x] = plan_half_px[371] + (plan_half_px[399] - plan_half_px[371]) * (x - 371) / 28
MAX_HALF_PX = max(plan_half_px.values())
P_LAT = (WIDTH / 2) / MAX_HALF_PX


def PX(px):
    return round((px - PLAN_TIP_F) * P_LONG, 4)


# ------------------------------------------------------------------ end views (COUPE)
FRONT_CX, FRONT_GROUND, FRONT_ROOF = 1056.1, 332.64, 108.3
REAR_CX, REAR_GROUND, REAR_ROOF = 1056.0, 748.4, 523.7
ROOF_H = round(side.to_car((450, 107.8))[1], 4)
F_VERT = ROOF_H / (FRONT_GROUND - FRONT_ROOF)
R_VERT = ROOF_H / (REAR_GROUND - REAR_ROOF)
E_LAT = P_LAT


def FZ(px):
    return round(abs(px - FRONT_CX) * E_LAT, 4)


def RZ(px):
    return round(abs(px - REAR_CX) * E_LAT, 4)


# ------------------------------------------------------------------ hand-read features
# COUPE side view (5–10x gridded zooms), px.
COWL = (321.0, 176.0)            # windscreen foot on the centre line
# Glasshouse: shapes from the COUPE sheet, raised by GLASS_SHIFT = 2.1 px (1.2 cm): the door-top seal
# (glass sill) sits at 0.870–0.875 m and the glass-top seal at ≈ 1.19 m in BOTH Porsche studio photos
# (964 PHOTO01 and the 993's studio photo, whose greenhouse is carried over — vertical intensity
# profiles at x 2.2 / 2.4 m), vs 0.861 / 1.175 m on the vendor sheet.
GLASS_SHIFT = -2.1
BELT_PY = 184.8 + GLASS_SHIFT    # side-window sill, A-pillar to quarter window → 0.873 m
DLO_DOOR = [(x, y + GLASS_SHIFT) for x, y in [
    (385, 184.8), (385, 170), (390, 157.5), (397.5, 145), (405, 136), (412.5, 131), (420, 129.5),
    (440, 130), (470, 130.5), (500, 133), (520, 136), (533, 138), (521, 184.8)]]
DLO_QUARTER = [(x, y + GLASS_SHIFT) for x, y in [
    (528, 185.2), (540, 139), (560, 143), (580, 148), (600, 157), (615, 167), (622, 175), (623, 179.5),
    (620, 182.5), (600, 185.3), (560, 185.5)]]
RAIL = [(405, 124), (420, 121.5), (440, 121), (470, 122.5), (500, 124), (530, 125.5), (560, 128), (580, 131),
        (600, 139), (620, 148), (640, 156), (660, 162)]
A_PILLAR = [(345, 181.0), (363, 175.0), (376, 160.0), (385, 150.0), (393, 140.0), (401, 130.0), (408, 120.5)]
HIP = [(600, 187.5), (620, 188), (650, 190), (670, 193), (700, 199.5), (720, 205.5), (740, 212), (753, 215.5),
       (765, 221), (778, 228)]
# PHOTO01, read on 1 cm car-space grids (x, y in metres).
DOOR = [(1.595, 0.855), (1.53, 0.845), (1.47, 0.83), (1.44, 0.80), (1.428, 0.73), (1.425, 0.53), (1.435, 0.33),
        (1.44, 0.318), (2.25, 0.325), (2.38, 0.332), (2.42, 0.34), (2.46, 0.365), (2.495, 0.42), (2.53, 0.50),
        (2.56, 0.60), (2.585, 0.70), (2.60, 0.78), (2.605, 0.83), (2.60, 0.865)]
HANDLE = [(2.37, 0.745), (2.37, 0.78), (2.575, 0.78), (2.575, 0.745)]
SILL_TOP = 0.31                   # joint between door bottom and sill cover
SILL_END = [(2.585, 0.315), (2.62, 0.33), (2.67, 0.345), (2.70, 0.37), (2.73, 0.40), (2.76, 0.43), (2.80, 0.465)]
BUMPER_F_TOP = 0.52               # front bumper / wing joint (x 0.18–0.60)
BUMPER_R_TOP = 0.495              # rear bumper / wing joint under the tail lamp (x 3.55–4.08)
LAMP_UNIT = (0.065, 0.41, 0.355, 0.455)   # front corner unit (photo x0, x1, y0, y1); clear lens x < 0.15
TAIL_LAMP = [(3.82, 0.495), (3.855, 0.589), (4.02, 0.589), (4.09, 0.495)]
REPEATER = (1.316, 0.711, 0.057, 0.032)  # centre x, y, length, height
MIRROR = (1.645, 0.91, 0.095, 0.105)     # head centre x, y, length, height (flag mirror)
FLAP = (1.245, 0.64, 0.18, 0.09)         # filler flap on the LEFT wing top (PHOTO01 side: x 1.155–1.335 m,
#                                          0.045 m tall; PHOTO30 overhead: on the wing crest just ahead of the
#                                          screen corner, ≈ 5 cm outboard of the lid edge → z 0.64); none on the
#                                          right wing (PHOTO03). x, z, length, width
# PHOTO10 (front, bumper-plane scale 1.507 mm/px from the bumper width at the lamp units,
# centre x 961 px) and PHOTO20 / PHOTO21 (rear, lamp band = 1.385 m wide, centre 961 px).
F_INDICATOR_Z = (0.68, 0.78)      # amber, outermost (x 443–508 px)
F_FOG_Z = (0.446, 0.634)          # clear rectangular fog lamp incl. frame (540–665 px)
F_UNIT_Y = (0.345, 0.455)         # heights: PHOTO01 side view (PHOTO10 gives 0.342–0.46)
F_FOG_Y = (0.335, 0.435)
F_PLATE = (0.26, 0.268, 0.377)    # EU plate 520 x 110 mm in the recess (PHOTO10 recess 770–1152 px, 850–922 px)
F_GRILLE = (0.58, 0.18, 0.265)    # two mesh slots across the apron (577–1347 px, 925–982 px)
R_LAMP_Z = (0.452, 0.693)         # outer tail lamps (1277–1445 px)
R_BAND_Z = 0.435                  # red PORSCHE reflector band (655–1265 px)
R_PLATE = (0.26, 0.336, 0.443)    # EU plate on the rear bumper (PHOTO21: plate top 0.055 m under the band, 110 mm tall)
R_EXHAUST = (0.59, 0.29, 0.045, 4.02)  # right-hand tailpipe: z, y (PHOTO20: oval 1316–1407 x 897–965 px), radius,
#                                       x centre (PHOTO03 right profile: tip reaches x 4.08 m; model pipe is 0.12 m long)
R_BADGE = (0.173, 0.738, 0.762)   # "Carrera 2" script on the lid (PHOTO20: 845–1080 px wide, 34 % of the way
#                                   from the grille bottom (0.82 m) to the band top (0.59 m); PHOTO21 agrees)
LAMP_F = (944.96, 221.48, 18.95)  # COUPE front view headlamp circle (fitted) → z 0.614, Ø 0.209

# ------------------------------------------------------------------ body curves
X_HOOD0 = round((98.0 - PLAN_TIP_F) * P_LONG, 4)     # lid front edge (plan view, 98 px): 0.144 m
Y_HOOD0 = BUMPER_F_TOP                                 # lid lip = bumper top joint (PHOTO10: level)
X_COWL, Y_COWL = C(*COWL)
TIP_TOP, TIP_BOT = 0.46, 0.30                          # nose face (PHOTO01 bumper corner)
TAIL_TOP = ycar(TAIL_X, 258.0)                         # tail face top (COUPE): 0.43 m


def hood_y(x):
    """Front-lid centre line (hidden behind the wings in every side view): PROVISIONAL convex
    profile between the measured lid lip (0.144 m, 0.52 m) and the cowl (COUPE)."""
    t = min(1.0, max(0.0, (x - X_HOOD0) / (X_COWL - X_HOOD0)))
    return Y_HOOD0 + (Y_COWL - Y_HOOD0) * (1 - (1 - t) ** 2.2)


hood = [[round(x, 4), round(hood_y(x), 4)] for x in np.linspace(X_HOOD0, X_COWL, 12)]
TAIL_XS = (4.11, 4.12, 4.13, 4.14, 4.15, 4.17, 4.19, 4.22)


def top_at(x):
    """COUPE side silhouette (centre line at the tail) at car x."""
    xs = sorted(TOP)
    return float(np.interp(x, [TOP[k][0] for k in xs], [TOP[k][1] for k in xs]))
# Nose top: face top → bumper top rounding into the lid lip (PHOTO01 1 cm grid, x shifted).
NOSE_TOP = [(0.0, TIP_TOP), (0.025, 0.49), (0.06, 0.51), (0.10, 0.518)]


def sil_top(a, b, step=2):
    return [TOP[x] for x in sorted(TOP) if a <= x <= b and (x - a) % step == 0]


topY = [list(p) for p in NOSE_TOP] + hood[1:-1] + sil_top(321, 809)
topY[-1] = [L, TAIL_TOP]

# Crest: bumper corner and headlamp bowl, wing crest (COUPE silhouette ahead of the A-pillar),
# door shoulder 1.4 cm under the glass sill, rear hip, down over the tail lamp to the bumper.
crestY = [list(p) for p in NOSE_TOP] + [[0.14, 0.522], [0.2, 0.53]] + sil_top(117, 335)
crestY += curve([(360, BELT_PY + 2.5), (450, BELT_PY + 2.5), (560, BELT_PY + 2.5)])
crestY += curve(HIP)                      # ends at (4.063, 0.612), above the tail lamp's rear corner
crestY += [[4.09, 0.55], [4.11, 0.50]] + [[x, round(top_at(x) - 0.01, 4)] for x in (4.15, 4.19, 4.22)] + [[L, TAIL_TOP]]

# Belt: lid side edge ahead of the screen (2 cm under the lid crown), glass sill in the cabin,
# engine-lid side edge behind (COUPE rear/side views), then the tail.
beltY = [list(p) for p in NOSE_TOP]
beltY += [[round(x, 4), round(hood_y(x) - 0.02 * min(1.0, (x - X_HOOD0) / 0.25), 4)] for x in np.linspace(X_HOOD0, X_COWL - 0.05, 10)]
beltY += curve([(345, BELT_PY), (450, BELT_PY), (560, BELT_PY), (623, BELT_PY + 0.5)])
beltY += curve([(660, 176.0), (690, 180.0), (720, 196.0), (750, 213.0), (775, 226.0)])
# Tail: the lid's crown fades out towards its lower edge, which is the straight, level top of
# the light strip (PHOTO20), so belt and rail follow the centre line (COUPE silhouette) down the
# strip face (x 4.106–4.164) and along the bumper ledge; crown 1.2 cm / 0.4 cm.
beltY += [[4.08, 0.607], [4.10, 0.593]] + [[x, round(top_at(x) - 0.012, 4)] for x in TAIL_XS] + [[L, TAIL_TOP]]

# Roof rail: on the lid ahead of the cabin, up the A-pillar, along the drip rail, down the
# C-pillar and onto the deck.
roofY = [list(p) for p in NOSE_TOP] + [[x, round(y - 0.004, 4)] for x, y in hood[1:-2]]
roofY += curve(A_PILLAR) + curve(RAIL[1:])
roofY += curve([(680, 166.5), (700, 175.0), (720, 186.0), (740, 196.0), (760, 208.0), (780, 224.0)])
roofY += [[4.08, 0.621], [4.10, 0.597]] + [[x, round(top_at(x) - 0.004, 4)] for x in TAIL_XS] + [[L, TAIL_TOP]]

# Floor (centre-line underside, drawn dark): front spoiler lip (COUPE grey lip 0.142 m, PHOTO10
# apron bottom ≈ 0.15 m), floor pan, rear valance (PHOTO01 / PHOTO20: black band to 0.205 m).
floorY = [[0.0, TIP_BOT], [0.05, 0.20], [0.10, 0.15], [0.5, 0.145], [FA, 0.15], [1.5, 0.155], [2.8, 0.16],
          [RA, 0.18], [3.6, 0.205], [4.05, 0.205], [4.15, 0.25], [4.22, 0.33], [L, 0.40]]

# Widest point: plan half-width (lateral scale from the official width) at the door bulge
# height (0.45 m), bumper corners (0.40 m); inside the arches kept 3 cm above the lip so the
# section does not fold under the flare.
sideZ = [[0.0, 0.0]] + [[PX(x), round(plan_half_px[x] * P_LAT, 4)] for x in sorted(plan_half_px) if (x - 74) % 4 == 0] + [[L, 0.0]]
side_base = [[0.0, 0.38], [0.05, 0.40], [0.4, 0.40], [0.6, 0.42], [1.35, 0.45], [2.8, 0.46], [3.6, 0.45],
             [4.05, 0.42], [L, 0.42]]


def rocker_at(x):
    return float(np.interp(x, [p[0] for p in rockerY], [p[1] for p in rockerY]))


sideY = []
for x in np.linspace(0, L, 140):
    base = float(np.interp(x, *zip(*side_base)))
    y = max(base, rocker_at(x) + 0.03) if 0.03 < x < L - 0.03 else base
    sideY.append([round(float(x), 4), round(y, 4)])

LAMP_Z = FZ(LAMP_F[0])                                              # 0.614 m
HOOD_EDGE_PLAN = [(100, 72.0), (200, 89.0), (298, 106.0)]          # lid side edge: (x px, half px)
HOOD_Z = [[X_HOOD0, round(72.0 * P_LAT, 4)]] + [[PX(x), round(h * P_LAT, 4)] for x, h in HOOD_EDGE_PLAN[1:]]
BELT_Z = round(120.5 * P_LAT, 4)     # glass sill (plan: outer edge of the glass band) 0.665 m
RAIL_Z = round(99.0 * P_LAT, 4)      # roof rail (plan: inner edge of the glass band) 0.546 m


def sidez_at(x):
    return float(np.interp(x, [p[0] for p in sideZ], [p[1] for p in sideZ]))


FRONT_ARCH_X = (0.545, 1.31)
REAR_ARCH_X = (2.795, 3.57)
rockerZ = []
for x in np.linspace(0, L, 140):
    in_arch = FRONT_ARCH_X[0] <= x <= FRONT_ARCH_X[1] or REAR_ARCH_X[0] <= x <= REAR_ARCH_X[1]
    off = 0.008 if in_arch else (0.03 if FRONT_ARCH_X[1] < x < REAR_ARCH_X[0] else 0.02)
    rockerZ.append([round(float(x), 4), round(max(0.0, sidez_at(x) - off), 4)])

crestZ = [[0.0, 0.0], [0.03, 0.30], [0.10, 0.50], [0.2, 0.57], [xcar(128), LAMP_Z - 0.01],
          [xcar(160), LAMP_Z], [FA, 0.625], [X_COWL, 0.655], [xcar(360), 0.695], [xcar(560), 0.70],
          [xcar(620), 0.70], [RA, 0.70], [xcar(740), 0.695], [4.02, 0.69], [L - 0.06, 0.55], [L, 0.0]]
beltZ = [[0.0, 0.0], [0.03, 0.25], [X_HOOD0, HOOD_Z[0][1]]] + HOOD_Z[1:] + [[X_COWL, 0.60], [xcar(345), BELT_Z - 0.01],
         [xcar(400), BELT_Z], [xcar(560), BELT_Z], [xcar(623), BELT_Z - 0.01], [xcar(660), 0.53], [xcar(690), 0.47],
         [xcar(750), 0.45], [4.05, 0.43], [L - 0.05, 0.30], [L, 0.0]]
roofZ = [[0.0, 0.0], [0.03, 0.12], [X_HOOD0, 0.16], [X_COWL - 0.1, 0.28], [xcar(345), 0.46], [xcar(376), 0.50],
         [xcar(408), RAIL_Z], [xcar(560), RAIL_Z - 0.005], [xcar(620), 0.51], [xcar(680), 0.45], [xcar(720), 0.30],
         [xcar(780), 0.20], [L, 0.0]]

body = {"floorY": floorY, "rockerY": rockerY, "rockerZ": rockerZ, "sideY": sideY, "sideZ": sideZ,
        "crestY": crestY, "crestZ": crestZ, "beltY": beltY, "beltZ": beltZ, "roofY": roofY, "roofZ": roofZ,
        "topY": topY}
TOL = {"rockerY": 0.002, "topY": 0.002, "crestY": 0.002, "sideZ": 0.0015, "rockerZ": 0.0015, "sideY": 0.002}
for k, c in body.items():
    c = sorted([[round(float(a), 4), round(float(b), 4)] for a, b in c])
    out = []
    for x, v in c:                      # strictly increasing x (monotone cubic)
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([x, v])
    out[0][0] = 0.0
    out[-1][0] = L
    body[k] = simplify(out, TOL.get(k, 0.003))
for k in ("sideZ", "rockerZ", "crestZ", "beltZ", "roofZ"):   # sections close at both tips
    body[k][0][1] = 0.0
    body[k][-1][1] = 0.0


# ------------------------------------------------------------------ decals
def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": [list(p) for p in pts], "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, n=4, **kw):
    """Axis-aligned rectangle: (a, b) = (x, y) side, (x, z) top, (z, y) front/rear; lowest-front first,
    clockwise. n > 4 spreads the points evenly along the perimeter (corners kept): the app resamples
    every outline by arc length to 2 x the larger point count of the two stops being morphed, which
    chamfers the corners of 4-point boxes (a visible V notch where a box meets the centre line)."""
    corners = [[a0, b0], [a0, b1], [a1, b1], [a1, b0]]
    if n <= 4:
        pts = corners
    else:
        per = 2 * (abs(a1 - a0) + abs(b1 - b0))
        pts = []
        for i in range(4):
            p0, p1 = np.array(corners[i], float), np.array(corners[(i + 1) % 4], float)
            k = max(1, int(round(n * np.linalg.norm(p1 - p0) / per)))
            pts += [list(p0 + (p1 - p0) * j / k) for j in range(k)]
    d = {"id": id_, "plane": plane, "kind": "fill", "points": pts, "finish": finish, "color": color}
    d.update(kw)
    return d


def ellipse(cx, cy, rx, ry, n=16):
    return [[round(cx + rx * np.cos(a), 4), round(cy + ry * np.sin(a), 4)] for a in np.linspace(np.pi, -np.pi, n, endpoint=False)]


GLASS = "#1d2329"
TRIM = "#1b1c1e"        # black window surrounds and seals (PHOTO01: satin black frames)
AMBER = "#e59a35"
CLEAR = "#eef1f2"
RED = "#b3201a"
GAP = "#2a2a2a"
FRONT_DEPTH = [-0.05, 0.45]
REAR_DEPTH = [L - 0.45, L + 0.05]
lx0 = nose_x(LAMP_UNIT[0])

decals = [
    side_decal("side-glass", curve(DLO_DOOR), "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", curve(DLO_QUARTER), "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("window-trim", curve(DLO_DOOR[1:12] + [(540, 139 + GLASS_SHIFT)] + DLO_QUARTER[2:8]), "satin", TRIM, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", curve(RAIL), "satin", TRIM, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", GAP, kind="line", depth=[0.55, 2]),
    side_decal("door-handle", HANDLE, "satin", "#1f2022", depth=[0.6, 2]),
    # Body-colour sill cover: its joint to the door and the kick-up in front of the rear arch.
    side_decal("rocker-trim", [(1.33, SILL_TOP), (2.585, SILL_TOP)] + SILL_END[1:], "satin", GAP, kind="line", depth=[0.6, 2]),
    # Integrated body-colour bumpers: the joint lines to the wings.
    side_decal("bumper-front", [(0.17, BUMPER_F_TOP + 0.015), (0.22, BUMPER_F_TOP), (0.60, BUMPER_F_TOP)], "satin", GAP, kind="line", depth=[0.3, 2], facing=0.2),
    side_decal("bumper-rear", [(3.55, BUMPER_R_TOP), (4.09, BUMPER_R_TOP), (4.2, 0.48)], "satin", GAP, kind="line", depth=[0.3, 2], facing=0.2),
    # Corner lamp unit: amber indicator wrapping round the bumper corner (clear lens ahead).
    side_decal("indicator-side", [(0.15, LAMP_UNIT[2]), (0.15, LAMP_UNIT[3]), (0.40, LAMP_UNIT[3]), (0.41, 0.44), (0.41, 0.37), (0.40, LAMP_UNIT[2])],
               "lens", AMBER, depth=[0.4, 2], facing=0.25),
    side_decal("taillight-side", TAIL_LAMP, "lens", RED, depth=[0.4, 2], facing=0.25),
    side_decal("side-repeater", ellipse(REPEATER[0], REPEATER[1], REPEATER[2] / 2, REPEATER[3] / 2, 12), "lens", AMBER, depth=[0.6, 2], facing=0.3),
]
# Front face: amber indicator outermost, clear fog lamp, plate recess, two intake slots.
decals += [
    # Black housing of the corner lamp unit (PHOTO10: amber indicator and clear fog lamp sit in one
    # black surround, 443–680 px), drawn first so the lenses print over it.
    box("front", "lamp-unit-front", F_FOG_Z[0], F_INDICATOR_Z[1], F_UNIT_Y[0], F_UNIT_Y[1], "satin", "#1b1c1e", n=12, depth=FRONT_DEPTH, facing=0.25),
    box("front", "indicator-front", F_INDICATOR_Z[0], F_INDICATOR_Z[1], F_UNIT_Y[0], F_UNIT_Y[1], "lens", AMBER, n=12, depth=FRONT_DEPTH, facing=0.25),
    box("front", "fog-front", F_FOG_Z[0], F_FOG_Z[1], F_FOG_Y[0], F_FOG_Y[1], "lens", CLEAR, n=14, depth=FRONT_DEPTH, facing=0.25),
    # Black rubber lip between the front lid and the bumper (geometry.json 964, PHOTO10).
    box("front", "bumper-strip-front", 0.0, HOOD_Z[0][1], Y_HOOD0 - 0.006, Y_HOOD0 + 0.006, "rubber", "#1c1c1c", n=12, depth=FRONT_DEPTH, facing=0.3),
    box("front", "plate-front", 0.0, F_PLATE[0], F_PLATE[1], F_PLATE[2], "satin", "#e9e9e6", n=20, depth=FRONT_DEPTH, facing=0.3),
    box("front", "intake-front", 0.0, F_GRILLE[0], F_GRILLE[1], F_GRILLE[2], "satin", "#1f2022", n=20, depth=FRONT_DEPTH, facing=0.3,
        stripes=[round((F_GRILLE[2] - F_GRILLE[1]) / 2, 4), 0.35]),
]
# Rear face: tail lamps at the corners joined by the red PORSCHE reflector strip (geometry.json
# 964: red reflective panel, red rear indicators), European plate recess.
T_Y0, T_Y1 = TAIL_LAMP[0][1], TAIL_LAMP[1][1]
decals += [
    box("rear", "taillight", R_LAMP_Z[0], R_LAMP_Z[1], T_Y0, T_Y1, "lens", RED, n=16, depth=REAR_DEPTH, facing=0.25),
    # The band runs up to the lamps (the 1.7 cm black divider between them is below one art pixel).
    box("rear", "reflector-band", 0.0, R_LAMP_Z[0], T_Y0 + 0.004, T_Y1 - 0.004, "lens", "#8f1a1f", n=28, depth=REAR_DEPTH, facing=0.25),
    box("rear", "plate-rear", 0.0, R_PLATE[0], R_PLATE[1], R_PLATE[2], "satin", "#e9e9e6", n=20, depth=REAR_DEPTH, facing=0.3),
    box("rear", "badge-rear", 0.0, R_BADGE[0], R_BADGE[1], R_BADGE[2], "satin", "#2a2b2e", n=16, depth=REAR_DEPTH, facing=0.2),
]
# Plan view: glass, lid gaps, retracted-spoiler grille, crest, filler flap (left wing).
SCREEN_BASE_PLAN = [(325, 0.0), (327, 60.0), (333, 95.0), (340, 104.0)]
SCREEN_TOP_PLAN = [(405, 0.0), (405, 80.0), (400, 97.0), (395, 103.0)]
REAR_WIN_PLAN = [(572, 0.0), (572, 74.0), (578, 80.0), (668, 80.0), (677, 72.0), (678, 0.0)]
# Engine-lid side edge (plan view) down to its lower edge, which sits on the top of the light
# strip (PHOTO20): constant x where the tail centre line is at 0.595 m (783 px), 0.44 m half-width
# there (plan 76 px = 0.42, PHOTO20 0.45 → mean).
LID_EDGE_PLAN = [(680, 83.0), (730, 80.0), (783, 0.44 / P_LAT)]
GRILLE_PLAN = (695, 738, 74.0)
screen_top = [[PX(x), round(h * P_LAT, 4)] for x, h in SCREEN_BASE_PLAN] + [[PX(x), round(h * P_LAT, 4)] for x, h in reversed(SCREEN_TOP_PLAN)]
rear_top = [[PX(x), round(h * P_LAT, 4)] for x, h in REAR_WIN_PLAN]
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rear_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    box("top", "engine-grille", PX(GRILLE_PLAN[0]), PX(GRILLE_PLAN[1]), 0.0, round(GRILLE_PLAN[2] * P_LAT, 4), "satin", "#1f2022", n=20,
        stripes=[0.014, 0.5], facing=0.3, depth=[0.7, 2]),
    box("top", "crest", PX(118), PX(127), 0.0, 0.022, "chrome", "#c9a24e", facing=0.3, depth=[0.5, 2]),
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left", "finish": "satin", "color": GAP, "facing": 0.3, "depth": [0.7, 2],
     "points": ellipse(FLAP[0], FLAP[1], FLAP[2] / 2, FLAP[3] / 2, 14)},
    {"id": "hood-gap", "plane": "top", "kind": "line", "finish": "satin", "color": GAP, "facing": 0.3,
     "points": [[X_HOOD0, 0.0]] + HOOD_Z},
    {"id": "lid-gap", "plane": "top", "kind": "line", "finish": "satin", "color": GAP, "facing": 0.3,
     "points": [[PX(x), round(h * P_LAT, 4)] for x, h in reversed(LID_EDGE_PLAN)] + [[PX(680), 0.0]]},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]

# ------------------------------------------------------------------ parts
LAMP_X = 0.345
LAMP_R = 0.096          # glass; + 0.009 chrome ring = Ø 0.21 m (COUPE front view Ø 0.209, PHOTO10 Ø 0.21)
# Lens centre: PHOTO01 shows the ring edge-on as a line from (0.315, 0.585) to (0.40, 0.795) m →
# centre (0.357, 0.69), tilted back 22° from vertical; the lamp is 0.13 m inboard of the wheel
# plane (camera ≈ 24 m away, from the centre-line nose offset) → -0.9 cm → x 0.348. COUPE side
# view: 0.32 m. Used: x 0.345 (photo), pitch 22°.
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
        # "Design 90": flat cast disc with 7 teardrop openings (PHOTO01) → closest RIM_DESIGNS entry.
        "front": {"diameter": round(TYRE_F, 4), "width": 0.205, "rim": RIM, "design": "cookie", "face": "#c9ccd1", "lip": "#d6d8dc", "caliper": "#202022"},
        "rear": {"diameter": round(TYRE_R, 4), "width": 0.225, "rim": RIM, "design": "cookie", "face": "#c9ccd1", "lip": "#d6d8dc", "caliper": "#202022"},
    },
    "headlight": {
        # Upright round lamp in the wing "tunnel": centre x from the COUPE side view, height from
        # PHOTO01 / PHOTO10 (0.68 m), z from the COUPE front and plan views (0.614 / 0.607 m).
        "centre": [LAMP_X, 0.685, LAMP_Z],
        "outline": [[round(float(np.cos(a)) * LAMP_R, 4), round(float(np.sin(a)) * LAMP_R, 4)] for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)],
        "yaw": 4,
        "pitch": 22,
        "ring": 0.009,
        "ringColor": "#dfe2e5",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    },
    # MY1989–91 flag mirror on each door, body-colour housing on a black foot (PHOTO01).
    "mirror": {"at": [MIRROR[0], MIRROR[1], 0.72], "size": [MIRROR[2], MIRROR[3], 0.15], "shape": "flag", "color": "paint", "finish": "paint"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    "exhausts": [[R_EXHAUST[3], R_EXHAUST[1], R_EXHAUST[0], R_EXHAUST[2]]],
}


# ------------------------------------------------------------------ outputs
def rescaled(view_crop, sx, sy, name):
    """Crop a view and resample it so both axes share one m/px scale."""
    x0, y0, x1, y1 = view_crop
    sub = img[y0:y1, x0:x1]
    h, w = sub.shape[:2]
    out = cv2.resize(sub, (int(round(w * sx)), int(round(h * sy))), interpolation=cv2.INTER_CUBIC)
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, out)
    return os.path.relpath(path, ROOT)


def photo_check(path):
    """Lofted car drawn over PHOTO01 (wheel-plane calibration)."""
    from PIL import Image, ImageDraw
    im = Image.open(PHOTO01).convert("RGB")
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.3)
    dr = ImageDraw.Draw(im)
    P = lambda x, y: tuple(float(v) for v in np.asarray(photo_px(x, y)).reshape(-1)[:2])
    xs = [L * i / 300 for i in range(301)]
    secs = [half_section(body, x) for x in xs]
    dr.line([P(x, max(p[1] for p in s)) for x, s in zip(xs, secs)], fill="#ff2d55", width=2)
    dr.line([P(x, mono(body["rockerY"], x)) for x in xs], fill="#ff9500", width=2)
    dr.line([P(x, mono(body["floorY"], x)) for x in xs], fill="#8e8e93", width=1)
    for k, col in (("crestY", "#34c759"), ("beltY", "#007aff"), ("roofY", "#af52de")):
        dr.line([P(x, mono(body[k], x)) for x in xs], fill=col, width=1)
    for ax, key in ((FA, "front"), (RA, "rear")):
        r = car["wheels"][key]["diameter"] / 2
        cx, cy = P(ax, r)
        rp = r / P_S
        dr.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], outline="#00c7be", width=2)
    for dec in decals:
        if dec["plane"] != "side":
            continue
        pts = [P(x, y) for x, y in dec["points"]]
        if dec["kind"] != "line":
            pts.append(pts[0])
        dr.line(pts, fill="#ffcc00", width=2)
    im.crop((40, 60, 1900, 700)).save(path)


k_plan = P_LAT / P_LONG
PLAN_CROP = (40, 455, 845, 805)
FRONT_CROP = (880, 90, 1235, 345)
REAR_CROP = (880, 505, 1235, 760)
fk, rk = F_VERT / E_LAT, R_VERT / E_LAT
if __name__ == "__main__":
    top_img = rescaled(PLAN_CROP, 1.0, k_plan, "ref-top.png")
    front_img = rescaled(FRONT_CROP, 1.0, fk, "ref-front.png")
    rear_img = rescaled(REAR_CROP, 1.0, rk, "ref-rear.png")
    calib = {
        "side": {"image": os.path.relpath(COUPE, ROOT), "wheelF": list(WHEEL_F), "wheelR": list(WHEEL_R), "tipF": TIP_X,
                 "crop": [50, 60, 830, 345]},
        "top": {"image": top_img, "tipF": PLAN_TIP_F - PLAN_CROP[0], "tipR": PLAN_TIP_R - PLAN_CROP[0],
                "centreY": (PLAN_CY - PLAN_CROP[1]) * k_plan, "crop": None},
        "front": {"image": front_img, "centreX": FRONT_CX - FRONT_CROP[0], "groundY": (FRONT_GROUND - FRONT_CROP[1]) * fk,
                  "left": FRONT_CX - FRONT_CROP[0] - (WIDTH / 2) / E_LAT, "right": FRONT_CX - FRONT_CROP[0] + (WIDTH / 2) / E_LAT,
                  "width": WIDTH, "crop": None},
        "rear": {"image": rear_img, "centreX": REAR_CX - REAR_CROP[0], "groundY": (REAR_GROUND - REAR_CROP[1]) * rk,
                 "left": REAR_CX - REAR_CROP[0] - (WIDTH / 2) / E_LAT, "right": REAR_CX - REAR_CROP[0] + (WIDTH / 2) / E_LAT,
                 "width": WIDTH, "crop": None},
    }
    with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
        json.dump(car, f, indent=1)
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    photo_check(os.path.join(OUT_DIR, "check-photo-side.png"))
    print("wrote", STOP, "length", L, "axles", FA, RA, "lat/long", round(k_plan, 4), "roof", ROOF_H)
