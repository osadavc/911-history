"""Trace: 10-993-1994 — 911 Carrera Coupé (993, MY1994–95, European), spoiler retracted.

References (research/blueprints/10-993-1994/sources.json, research/photos/10-993-1994/sources.json):
  LINE    blueprints/tbp-92535 "Porsche 911 Carrera (1997)" 4-view line drawing (side = car's right
          side, nose right; plan; front; rear). Primary drawing: upper side silhouette, plan outline,
          lid / glass / grille lines, front and rear views (lateral positions).
  VENDOR  blueprints/vec-10962 colour 5-view preview: cross-check only (its printed 1800 mm width is
          wrong and its tyres are drawn 4 % large).
  PHOTO01 photos/01-side-left.jpg — official Porsche studio photo "1994, 911 Carrera Coupé, Type 993"
          ("tracing": "side"). Lower body (arch lips, sills, bumper lower edges), door / glass / handle /
          repeater / mirror / filler flap, lamp positions, windscreen silhouette; axle positions.
  PHOTO09 photos/09-front.jpg, PHOTO26 photos/26-rear.jpg (Polar Silver 1995 Carrera, head-on;
          US car) + PHOTO14 (1994 press car, German plate), PHOTO31 / PHOTO39 (European rear lamps):
          lamp / intake / plate / light-strip layout and colours.
Official figures (specs.json / geometry.json 10): L 4245 (European; US 4260), W 1735, H 1310 (AMS 1300),
WB 2272, tracks 1405 / 1445 mm, 205/55 ZR16 front, 245/45 ZR16 rear on 7J / 9J x 16 Cup wheels.

Calibration (every image on its own):
  PHOTO01 — rim-lip circles fitted on 180 rays (residual 0.2–0.3 px): front (524.06, 627.76),
          rear (1321.09, 635.85) → 797.07 px = 2272 mm → 2.8504 mm/px (wheel plane), axle 0.316 m.
          Centre-line tips (nose px 213, tail px 1666) appear 2.4 % short (k = 0.9757, camera
          ≈ 30 m away — the 964 studio photo of the same series gives k = 0.980); corrected about the
          image centre they give L 4.245 with the front axle 0.940 m behind the nose.
  LINE side — the drawing's wheels are drawn 1.8 % too close together (WB 355.14 px vs 675.4 px
          overall length: 0.526 vs 0.535 official) and its tyres 5 % small. Its BODY matches PHOTO01
          (corrected) within ±1 cm along the wings, roof and C-pillar when scaled on its overall
          length: nose 986.8 px, tail 311.4 px → 6.2852 mm/px both ways, heights referenced to the
          drawn axle row 169.22 px = 0.316 m (roof 1.304 m; official 1.310 / 1.300).
          Front axle position in this frame: door front shut line, door rear shut line (at 0.60 m),
          belt corner and handle in PHOTO01 vs the LINE give 0.958 / 0.938 / 0.942 / 0.920 m →
          FA = 0.940 m (the photo-perspective estimate is 0.9397). RA = FA + 2.272 = 3.212 m.
          The drawn wheels (0.957 / 3.189 m) are therefore NOT used; check-side.png is calibrated on
          virtual wheel centres at the model's axles (837.24 / 475.76 px).
  LINE plan — nose 679.3 px, tail 0 px (own length → L), centre row 367.5; lateral scale from the
          official width (1735 mm) over the widest outline (rear hips).
  LINE front / rear — centre 831.5 / 155.2 px, lateral scale = official width over the widest
          outline; heights of features visible in the side view come from the side view (these views
          are 1–5 % out of proportion), others with a uniform scale anchored on the roof.

Run: research/tools/venv python research/traces/10-993-1994.py
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
from trace_lib import half_section, mono, silhouette_from_drawing, simplify  # noqa: E402

STOP = "10-993-1994"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
LINE = os.path.join(BP, "tbp-92535_porsche-911-carrera-1997_4view.png")
PHOTO01 = os.path.join(PH, "01-side-left.jpg")
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------ official figures
L = 4.245
WB = 2.272
WIDTH = 1.735
TRACK_F, TRACK_R = 1.405, 1.445
TYRE_F = 0.4064 + 2 * 0.205 * 0.55     # 205/55 R16 → 0.6319 m
TYRE_R = 0.4064 + 2 * 0.245 * 0.45     # 245/45 R16 → 0.6269 m
RIM = 0.4064
AX = 0.316                             # axle height = front tyre radius
FA = 0.940                             # see calibration notes
RA = round(FA + WB, 4)

# ------------------------------------------------------------------ LINE drawing
lg = cv2.imread(LINE, cv2.IMREAD_GRAYSCALE).astype(float)
L_NOSE, L_TAIL, L_AXROW = 986.8, 311.4, 169.22
LS = L / (L_NOSE - L_TAIL)             # 6.2852 mm/px


def LX(px):
    return round((L_NOSE - px) * LS, 4)


def LY(py):
    return round(AX + (L_AXROW - py) * LS, 4)


def lpt(points):
    return [[LX(px), LY(py)] for px, py in points]


def first_edge(g, x, y0, y1, thr=160.0):
    col = g[y0:y1, x]
    for i in range(1, len(col)):
        if col[i] < thr <= col[i - 1]:
            return y0 + i - 1 + (col[i - 1] - thr) / (col[i - 1] - col[i])
    return None


def last_edge(g, x, y0, y1, thr=160.0):
    col = g[y0:y1, x]
    for i in range(len(col) - 1, 0, -1):
        if col[i - 1] < thr <= col[i]:
            return y0 + i - 1 + (thr - col[i - 1]) / (col[i] - col[i - 1])
    return None


# Upper side silhouette: outer edge of the outline stroke, every column.
LINE_TOP = {}
for px in range(312, 987):
    y = first_edge(lg, px, 0, 215)
    if y is not None:
        LINE_TOP[LX(px)] = LY(y)
_lt = sorted(LINE_TOP.items())


def line_top(x):
    return float(np.interp(x, [a for a, _ in _lt], [b for _, b in _lt]))


# ------------------------------------------------------------------ PHOTO01
pgray = cv2.GaussianBlur(cv2.imread(PHOTO01, cv2.IMREAD_GRAYSCALE).astype(float), (3, 3), 0)
P_WF, P_WR = np.array([524.06, 627.76]), np.array([1321.09, 635.85])
P_S = WB / np.linalg.norm(P_WR - P_WF)
P_U = (P_WR - P_WF) / np.linalg.norm(P_WR - P_WF)
P_N = np.array([P_U[1], -P_U[0]])
if P_N[1] > 0:
    P_N = -P_N


def photo_px(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return P_WF[None, :] + ((x - FA) / P_S)[..., None] * P_U[None, :] + ((y - AX) / P_S)[..., None] * P_N[None, :]


def photo_car(px, py):
    q = np.array([px, py], float) - P_WF
    return round(FA + float(q @ P_U) * P_S, 4), round(AX + float(q @ P_N) * P_S, 4)


# Perspective of centre-line features (tips, roof, screen, deck): they lie ≈ 0.72 m behind the
# calibrated wheel plane and appear scaled by K about the principal point (image centre).
K = 0.9757
PC = photo_car(960, 535)


def centre_line(x, y):
    return (round(PC[0] + (x - PC[0]) / K, 4), round(PC[1] + (y - PC[1]) / K, 4))


def photo_low_edge(x, y_start, dark=45.0, run=0.02, step=0.0025):
    """Scan down from y_start at car x: first y where PHOTO01 turns black for ≥ run (wheel well /
    shadowed underside), i.e. the lower edge of the body side."""
    ys = np.arange(y_start, 0.05, -step)
    p = photo_px(np.full_like(ys, x), ys)
    v = map_coordinates(pgray, [p[:, 1], p[:, 0]], order=1, mode="nearest")
    need = int(round(run / step))
    d = v < dark
    for i in range(1, len(ys) - need):
        if d[i:i + need].all() and not d[i - 1]:
            return float(ys[i] + step / 2)
    return None


def photo_top_edge(x, y_top=1.25, y_min=0.55, thr=11.0, step=0.0025):
    """Scan down at car x: first y where PHOTO01 departs from the studio backdrop (a smooth vertical
    gradient, tracked by a running median of the previous 10 samples) by more than thr for 3
    samples — finds light paint and the black spoiler grille alike."""
    ys = np.arange(y_top, y_min, -step)
    p = photo_px(np.full_like(ys, x), ys)
    v = map_coordinates(pgray, [p[:, 1], p[:, 0]], order=1, mode="nearest")
    for i in range(10, len(ys) - 3):
        bg = np.median(v[i - 10:i])
        if all(abs(v[i + j] - bg) > thr for j in range(3)):
            return float(ys[i] + step / 2)
    return None


# ------------------------------------------------------------------ side silhouettes
# Windscreen: the dark glass seen above the wing / A-pillar in PHOTO01 (contrast-enhanced, 2 cm grid),
# upper edge, perspective-corrected (centre line). The LINE's screen line runs 2 cm high and on down
# to the wing at x 1.24 m, ahead of the cowl — not used.
SCREEN_RAW = [(1.40, 0.900), (1.46, 0.935), (1.53, 1.000), (1.60, 1.030), (1.70, 1.090), (1.80, 1.160),
              (1.88, 1.220), (1.93, 1.245)]
SCREEN = [centre_line(x, y) for x, y in SCREEN_RAW]
COWL = SCREEN[0]
X_ROOF0 = 2.0                       # LINE silhouette from here (roof front)
# Deck: LINE silhouette vs PHOTO01 background-difference edge (corrected) — see the md; the LINE
# is kept where they agree; x 3.62–3.95 is the black spoiler grille.
DECK_CHECK = []
for x in np.arange(3.30, 4.16, 0.05):
    y = photo_top_edge(float(x))
    if y is not None:
        DECK_CHECK.append((round(float(x), 3), centre_line(float(x), y), round(line_top(centre_line(float(x), y)[0]), 4)))

# Lower edge: PHOTO01 (black wheel wells / shadowed underside). Arch spans from the scan.
FRONT_ARCH_X = (0.565, 1.345)
REAR_ARCH_X = (2.83, 3.61)
LOW_START = [(0.55, 0.35), (FRONT_ARCH_X[0] - 0.01, 0.95), (FRONT_ARCH_X[1], 0.60), (REAR_ARCH_X[0] - 0.02, 0.80),
             (REAR_ARCH_X[1], 0.46)]


def low_start(x):
    s = None
    for x0, y0 in LOW_START:
        if x >= x0:
            s = y0
    return s


LOW = {}
for x in np.round(np.arange(0.56, 4.05, 0.01), 3):
    y = photo_low_edge(float(x), low_start(x))
    if y is not None:
        LOW[float(x)] = round(y, 4)
# Nose and tail lower outlines, read on 1 cm car-space grids of the contrast-enhanced PHOTO01
# (FA 0.94 frame): lamp-unit housing front (0.06–0.10 m), bumper face curving under to the lower lip
# (0.19 m); rear bumper corner, valance.
NOSE_LOW = [(0.0, 0.40), (0.06, 0.345), (0.10, 0.345), (0.13, 0.33), (0.155, 0.30), (0.18, 0.262), (0.20, 0.232),
            (0.22, 0.212), (0.25, 0.197), (0.30, 0.192), (0.40, 0.19), (0.50, 0.19)]
TAIL_LOW = [(4.02, 0.26), (4.06, 0.29), (4.10, 0.325), (4.14, 0.37), (4.17, 0.42), (4.19, 0.46), (L, 0.50)]

# Photo deck (corrected) used from x 3.50 (LINE and photo agree within 1 cm up to 3.48, the LINE is
# 1.3–3.9 cm too full behind — its rear overhang is also its least accurate part).
DECK = []
for x in np.arange(3.46, 4.13, 0.02):
    y = photo_top_edge(float(x))
    if y is not None:
        DECK.append(centre_line(float(x), y))

# ------------------------------------------------------------------ plan view (LINE)
PL_NOSE, PL_TAIL, PL_CY = 679.3, 0.0, 367.5
plan_half_px = {}
for px in range(1, 679):
    t = first_edge(lg, px, 218, 367)
    b = last_edge(lg, px, 368, 519)
    if t is not None and b is not None:
        plan_half_px[px] = (b - t) / 2
for a, b in ((392, 424), (260, 300)):          # door mirrors and door handles stick out: bridged
    for px in range(a + 1, b):
        plan_half_px[px] = plan_half_px[a] + (plan_half_px[b] - plan_half_px[a]) * (px - a) / (b - a)
MAX_HALF_PX = max(plan_half_px.values())
P_LAT = (WIDTH / 2) / MAX_HALF_PX              # m/px across the car


def PX(px):
    """plan column → car x (plan's own nose/tail = 0 / L)."""
    return round((PL_NOSE - px) / (PL_NOSE - PL_TAIL) * L, 4)


def PZ(py):
    return round(abs(py - PL_CY) * P_LAT, 4)


# ------------------------------------------------------------------ front / rear views (LINE)
F_CX, F_ROOF = 831.5, 281.6
R_CX, R_ROOF = 155.2, 4.0
F_LAT = (WIDTH / 2) / 136.7                    # widest outline (rear hips seen from the front)
R_LAT = (WIDTH / 2) / 142.3
ROOF_H = round(max(line_top(x) for x in np.arange(2.0, 2.6, 0.01)), 4)


def FZ(px):
    return round(abs(px - F_CX) * F_LAT, 4)


def FY(py):
    return round(ROOF_H - (py - F_ROOF) * F_LAT, 4)


def RZ(px):
    return round(abs(px - R_CX) * R_LAT, 4)


def RY(py):
    return round(ROOF_H - (py - R_ROOF) * R_LAT, 4)


# ------------------------------------------------------------------ hand-read features
def ph(points):
    """PHOTO01 pixels → car (wheel-plane features: door, glass, handle, lamps' side faces)."""
    return [list(photo_car(px, py)) for px, py in points]


# PHOTO01 (px), read on 4–5x gridded zooms.
DLO_DOOR_PX = [(836, 433), (848, 415), (862, 394), (876, 373), (890, 353), (903, 336), (916, 328), (950, 326),
               (1000, 327), (1050, 330), (1100, 336), (1141, 342), (1113, 436), (1000, 435), (900, 434)]
DLO_QUARTER_PX = [(1131, 437), (1160, 343), (1200, 351), (1250, 368), (1290, 390), (1318, 409), (1332, 423),
                  (1326, 432), (1300, 436), (1200, 437)]
RAIL_PX = [(916, 322), (966, 320), (1036, 322), (1100, 327), (1150, 334), (1200, 343), (1250, 357), (1290, 372)]
DOOR_PX = [(745, 437), (726, 446), (716, 458), (712, 475), (710, 520), (709, 560), (709, 600), (711, 621), (800, 621),
           (1000, 620), (1025, 617), (1045, 610), (1060, 598), (1072, 580), (1085, 550), (1098, 520), (1108, 490),
           (1115, 460), (1118, 437)]
HANDLE_PX = [(1038, 473), (1045, 466), (1070, 463), (1100, 461), (1112, 466), (1113, 476), (1105, 484), (1075, 484),
             (1050, 480), (1040, 477)]
SILL_LINE_Y = 0.292                  # sill cover top edge (bright line, PHOTO01 y 638 px)
BELT_Y = 0.873                       # glass sill seal / door top (PHOTO01 profiles at x 2.2 and 2.4 m)
DOOR_SHOULDER = 0.860                # door shoulder just below the seal
# Car-space readings (PHOTO01, FA 0.94 frame, 1 cm grids):
F_JOINT = [(0.20, 0.545), (0.35, 0.542), (0.50, 0.540), (0.60, 0.535)]   # front bumper / wing joint
R_JOINT = [(3.56, 0.585), (3.87, 0.585)]                                   # rear bumper / wing joint
F_LAMP_SIDE = [(0.12, 0.398), (0.12, 0.462), (0.35, 0.467), (0.365, 0.455), (0.365, 0.405), (0.35, 0.398)]
R_LAMP_AMBER = [(3.87, 0.585), (3.90, 0.665), (4.03, 0.665), (4.03, 0.585)]  # wrap-round indicator part
R_LAMP_RED = [(4.03, 0.585), (4.03, 0.665), (4.06, 0.662), (4.10, 0.63), (4.11, 0.585)]
REPEATER = (1.368, 0.750, 0.055, 0.030)
MIRROR = (1.69, 0.93, 0.145, 0.11)   # teardrop head: centre x, y, length, height
FLAP = (1.285, 0.67, 0.18, 0.10)     # filler flap (LEFT wing top): side view x 1.195–1.375; plan z
HIP = [(2.95, 0.868), (3.15, 0.872), (3.35, 0.862), (3.55, 0.835), (3.70, 0.795), (3.80, 0.755), (3.87, 0.71),
       (3.90, 0.672)]                # rear wing shoulder (upper edge of the hip highlight, PHOTO01)
A_PILLAR = [(1.52, 0.90), (1.60, 0.965), (1.70, 1.03), (1.80, 1.10), (1.90, 1.175), (1.95, 1.21)]
C_PILLAR_LINE = [(2.93, 1.203), (3.247, 1.096), (3.562, 0.990)]   # rear-window side edge (LINE px 520/470/420)
# Front lamp (LINE side view lens edge (921,103)-(953,132) px; PHOTO01 bowl line (0.20,0.535)-(0.46,0.77))
LAMP_PITCH = 48.0                    # side-view slope 47.8° (LINE) / 49.6° (PHOTO01); front-view ellipse
                                     # 39 x 26 px → cos p = 0.67 → 48°
# LINE plan (px): lid, glass, grille, lamp.
LID_FRONT_PX = 650.0                 # front-lid front edge (bumper joint) at the centre
LID_EDGE_PX = [(648, 306), (600, 297), (540, 288), (480, 279), (440, 270)]   # lid side shut line
LAMP_PLAN = (624.0, 277.0)           # lamp oval centre
REAR_WIN_PX = (110.0, 215.0, 288.0)  # rear window: rear x, front x, side row
GRILLE_PX = (50.0, 100.0, 293.0)     # engine grille: rear x, front x, side row
GLASS_PLAN_ROWS = (258.0, 282.0)     # side glass seen from above: outer (belt) / inner (rail) rows
# LINE front view (px): lamp unit, intake; PHOTO09 segment split (amber 457–510, black 510–548,
# clear 548–697 px of the image-left unit, centre 958 px, scale from the intake width).
F_UNIT_Z = (0.404, 0.78)             # whole corner unit (LINE 705–768 px → 0.40–0.80; PHOTO09 0.404–0.775)
F_AMBER_Z = (0.693, 0.775)
F_CLEAR_Z = (0.404, 0.634)
F_UNIT_Y = (0.395, 0.467)            # PHOTO01 side view
F_INTAKE = (0.536, 0.23, 0.34)       # half-width (LINE 747–916 px), y0, y1
F_PLATE = (0.26, 0.365, 0.475)       # EU plate 520 x 110 at the lamp-unit level (PHOTO14)
# LINE rear view + PHOTO26 (strip ends 345/1565 px ↔ ±0.733 m): segments of the light strip.
R_STRIP_Y = (0.588, 0.668)           # side views (PHOTO01 0.585–0.665, LINE 0.594–0.676)
R_BAND_Z = 0.342
R_REVERSE_Z = (0.342, 0.439)
R_TAIL_Z = (0.457, 0.556)           # LINE rear view dividers at 64 / 81 px → z 0.556 / 0.459 (PHOTO26: 0.457)
R_AMBER_Z = (0.556, 0.733)           # European amber indicator = the outer segment (PHOTO31 / PHOTO39)
R_PLATE = (0.26, 0.38, 0.49)         # LINE rear recess y 136–157 px (0.371–0.499)
R_BADGE = (0.108, 0.73, 0.75)        # "Carrera" script: PHOTO26 865–1045 px wide
EXHAUST = (4.07, 0.215, 0.50, 0.04)  # oval tailpipes (MY94–95), one each side: LINE z 0.476, PHOTO26 0.52

# ------------------------------------------------------------------ body curves
X_LID0 = PX(LID_FRONT_PX)            # 0.183 m
Y_LID0 = 0.54                        # lid front edge = bumper top at the centre (PHOTO09 / PHOTO01 joint)
X_COWL, Y_COWL = COWL
TIP_Y = 0.43                         # nose tip at the centre line (LINE 0.424, PHOTO01 corrected 0.436)
TAIL_Y = 0.50                        # rear-most bumper point (PHOTO01 corrected x 4.23, y 0.49–0.50)


def lid_y(x):
    """Front-lid centre line (hidden behind the wings in every side view): PROVISIONAL convex profile
    from the measured lid front edge to the cowl, same form as the 964 trace."""
    t = min(1.0, max(0.0, (x - X_LID0) / (X_COWL - X_LID0)))
    return Y_LID0 + (Y_COWL - Y_LID0) * (1 - (1 - t) ** 2.2)


lid = [[round(x, 4), round(lid_y(x), 4)] for x in np.linspace(X_LID0, X_COWL, 12)]
NOSE_TOP = [(0.0, TIP_Y), (0.03, 0.47), (0.07, 0.505), (0.12, 0.528), (X_LID0, Y_LID0)]
TAIL_TOP = [(4.147, 0.668), (4.19, 0.588), (4.22, 0.555), (L, TAIL_Y)]   # strip face, bumper (LINE tail outline)


def band(a, b, step=0.01):
    return [[round(float(x), 4), round(line_top(float(x)), 4)] for x in np.arange(a, b + 1e-9, step)]


deck = [[x, y] for x, y in DECK if 3.50 <= x <= 4.12]
topY = [list(p) for p in NOSE_TOP] + lid[1:-1] + [list(p) for p in SCREEN] + band(X_ROOF0, 3.45) + deck
topY += [list(p) for p in TAIL_TOP]

# Crest: the side silhouette ahead of the cabin is the wing crest (LINE), door shoulder in the cabin,
# rear wing shoulder (PHOTO01) down to the tail lamp, lamp corner, bumper.
crestY = [[0.0, TIP_Y], [0.03, 0.475]] + band(0.06, 1.40, 0.02)
crestY += [[1.55, DOOR_SHOULDER + 0.004], [2.0, DOOR_SHOULDER], [2.7, DOOR_SHOULDER]] + [list(p) for p in HIP]
crestY += [[4.03, 0.665], [4.08, 0.645], [4.12, 0.60], [4.17, 0.56], [4.21, 0.53], [L, TAIL_Y]]

# Belt: lid side edge (2 cm under the lid crown) ahead of the screen, glass sill in the cabin,
# engine-lid side edge behind (2.5 cm under the deck), then the strip and bumper.
beltY = [list(p) for p in NOSE_TOP[:-1]]
beltY += [[round(x, 4), round(lid_y(x) - 0.02 * min(1.0, (x - X_LID0) / 0.25), 4)] for x in np.linspace(X_LID0, X_COWL - 0.05, 10)]
beltY += [[1.47, BELT_Y - 0.01], [1.60, BELT_Y], [2.4, BELT_Y], [3.2, BELT_Y + 0.004]]
beltY += [[x, round(y - 0.025, 4)] for x, y in DECK if 3.56 <= x <= 4.10 and int(round(x * 100)) % 6 == 0]
beltY += [[4.12, 0.64], [4.16, 0.63], [4.19, 0.585], [4.22, 0.55], [L, TAIL_Y]]

# Roof rail: on the lid ahead of the cabin, up the A-pillar, along the drip rail, down the rear-window
# side edge (LINE), then onto the deck.
roofY = [list(p) for p in NOSE_TOP[:-1]] + [[x, round(y - 0.004, 4)] for x, y in lid[:-2]]
roofY += [list(p) for p in A_PILLAR] + ph(RAIL_PX)[1:] + [list(p) for p in C_PILLAR_LINE]
roofY += [[x, round(y - 0.006, 4)] for x, y in DECK if 3.66 <= x <= 4.10 and int(round(x * 100)) % 6 == 0]
roofY += [[4.13, 0.655], [4.16, 0.64], [4.19, 0.588], [4.22, 0.555], [L, TAIL_Y]]

# Floor (centre-line underside): in the overhangs it follows the side-view lower outline (the bumper
# faces curve under, so nothing hangs below it); under the car the floor pan (ground clearance 120 mm
# laden → 0.15 m unladen, LINE bottom outline 0.154 m); black rear valance 0.21 m (PHOTO01).
floorY = [list(p) for p in NOSE_LOW[:8]] + [[0.30, 0.18], [0.6, 0.155], [FA, 0.155], [1.5, 0.15], [2.8, 0.15],
                                            [RA, 0.17], [3.7, 0.20], [4.0, 0.21], [4.06, 0.235]] + [list(p) for p in TAIL_LOW[2:]]

rockerY = [list(p) for p in NOSE_LOW] + [[x, y] for x, y in sorted(LOW.items()) if 0.56 <= x < 4.02]
rockerY += [list(p) for p in TAIL_LOW]

# Widest point: plan outline x lateral scale; height: bumper corners 0.43, front wing 0.52, door 0.48,
# rear hips 0.69 (LINE rear / front views: widest rows y 104 / 381 px → 0.67–0.69 m); kept 3 cm
# above the arch lips.
sideZ = [[0.0, 0.0]] + [[PX(px), round(h * P_LAT, 4)] for px, h in sorted(plan_half_px.items(), reverse=True)
                        if px % 3 == 0] + [[L, 0.0]]
side_base = [[0.0, 0.42], [0.1, 0.43], [0.4, 0.46], [0.6, 0.52], [1.3, 0.50], [1.6, 0.48], [2.6, 0.50],
             [2.9, 0.62], [3.2, 0.69], [3.6, 0.66], [3.9, 0.56], [4.1, 0.50], [L, 0.48]]


def rocker_at(x):
    return float(np.interp(x, [p[0] for p in rockerY], [p[1] for p in rockerY]))


sideY = []
for x in np.linspace(0, L, 150):
    base = float(np.interp(x, *zip(*side_base)))
    y = max(base, rocker_at(x) + 0.03) if 0.03 < x < L - 0.03 else base
    sideY.append([round(float(x), 4), round(y, 4)])

LAMP_Z = 0.585                         # lamp centre z: LINE front view 0.584, plan 0.571, PHOTO09 ≈ 0.59
LID_Z = [[X_LID0, PZ(306)]] + [[PX(px), PZ(py)] for px, py in LID_EDGE_PX[1:]]
BELT_Z = PZ(GLASS_PLAN_ROWS[0])        # 0.69 m (outer edge of the glass seen from above)
RAIL_Z = PZ(GLASS_PLAN_ROWS[1])        # 0.54 m


def sidez_at(x):
    return float(np.interp(x, [p[0] for p in sideZ], [p[1] for p in sideZ]))


rockerZ = []
for x in np.linspace(0, L, 150):
    in_arch = FRONT_ARCH_X[0] <= x <= FRONT_ARCH_X[1] or REAR_ARCH_X[0] <= x <= REAR_ARCH_X[1]
    off = 0.008 if in_arch else (0.03 if FRONT_ARCH_X[1] < x < REAR_ARCH_X[0] else 0.02)
    rockerZ.append([round(float(x), 4), round(max(0.0, sidez_at(x) - off), 4)])

crestZ = [[0.0, 0.0], [0.03, 0.30], [0.08, 0.50], [0.15, 0.58], [0.3, LAMP_Z + 0.02], [0.6, 0.64], [FA, 0.66],
          [X_COWL, 0.69], [1.6, 0.715], [2.4, 0.72], [2.9, 0.735], [RA, 0.77], [3.6, 0.76], [3.9, 0.72],
          [4.1, 0.66], [L - 0.05, 0.50], [L, 0.0]]
beltZ = [[0.0, 0.0], [0.03, 0.25], [X_LID0, LID_Z[0][1]]] + LID_Z[1:] + [[1.50, 0.64], [1.60, BELT_Z - 0.01],
         [2.0, BELT_Z], [2.8, BELT_Z], [3.2, BELT_Z - 0.03], [3.45, 0.56], [3.7, 0.50], [4.0, 0.47], [4.12, 0.45],
         [L - 0.05, 0.30], [L, 0.0]]
roofZ = [[0.0, 0.0], [0.03, 0.12], [X_LID0, 0.16], [X_COWL - 0.1, 0.30], [1.52, 0.48], [1.70, 0.51],
         [1.95, RAIL_Z], [2.8, RAIL_Z - 0.005], [3.0, 0.52], [3.25, 0.49], [3.56, 0.42], [3.8, 0.30], [4.1, 0.22],
         [L, 0.0]]

body = {"floorY": floorY, "rockerY": rockerY, "rockerZ": rockerZ, "sideY": sideY, "sideZ": sideZ,
        "crestY": crestY, "crestZ": crestZ, "beltY": beltY, "beltZ": beltZ, "roofY": roofY, "roofZ": roofZ,
        "topY": topY}
TOL = {"rockerY": 0.002, "topY": 0.002, "crestY": 0.002, "sideZ": 0.0015, "rockerZ": 0.0015, "sideY": 0.002}
for k, c in body.items():
    c = sorted([[round(float(a), 4), round(float(b), 4)] for a, b in c])
    out = []
    for x, v in c:
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([x, v])
    out[0][0] = 0.0
    out[-1][0] = L
    body[k] = simplify(out, TOL.get(k, 0.003))
for k in ("sideZ", "rockerZ", "crestZ", "beltZ", "roofZ"):
    body[k][0][1] = 0.0
    body[k][-1][1] = 0.0


# ------------------------------------------------------------------ decals
def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": [list(p) for p in pts], "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, n=4, **kw):
    """Axis-aligned rectangle, lowest-front first, clockwise; n > 4 spreads points along the edges
    (the app resamples outlines by arc length, which chamfers 4-point boxes)."""
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
TRIM = "#1b1c1e"
AMBER = "#e59a35"
CLEAR = "#eef1f2"
RED = "#b3201a"
GAP = "#2a2a2a"
FRONT_DEPTH = [-0.05, 0.45]
REAR_DEPTH = [L - 0.45, L + 0.05]
dlo = ph(DLO_DOOR_PX)
qtr = ph(DLO_QUARTER_PX)
decals = [
    side_decal("side-glass", dlo, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", qtr, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("window-trim", dlo[:12] + qtr[1:8], "satin", TRIM, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", ph(RAIL_PX), "satin", TRIM, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", ph(DOOR_PX), "satin", GAP, kind="line", depth=[0.55, 2]),
    # Body-colour pull handle in a recess (geometry.json 993): the recess outline.
    side_decal("door-handle", ph(HANDLE_PX) + [ph(HANDLE_PX)[0]], "satin", GAP, kind="line", depth=[0.6, 2]),
    side_decal("rocker-trim", [(FRONT_ARCH_X[1] + 0.02, SILL_LINE_Y), (REAR_ARCH_X[0] - 0.02, SILL_LINE_Y)], "satin", GAP,
               kind="line", depth=[0.6, 2]),
    side_decal("bumper-front", F_JOINT, "satin", GAP, kind="line", depth=[0.3, 2], facing=0.2),
    side_decal("bumper-rear", R_JOINT, "satin", GAP, kind="line", depth=[0.3, 2], facing=0.2),
    side_decal("indicator-side", F_LAMP_SIDE, "lens", AMBER, depth=[0.4, 2], facing=0.25),
    side_decal("side-marker", R_LAMP_AMBER, "lens", AMBER, depth=[0.4, 2], facing=0.25),
    side_decal("taillight-side", R_LAMP_RED, "lens", RED, depth=[0.4, 2], facing=0.25),
    side_decal("side-repeater", ellipse(REPEATER[0], REPEATER[1], REPEATER[2] / 2, REPEATER[3] / 2, 12), "lens", AMBER,
               depth=[0.6, 2], facing=0.3),
]
decals += [
    box("front", "lamp-unit-front", F_UNIT_Z[0], F_UNIT_Z[1], F_UNIT_Y[0], F_UNIT_Y[1], "satin", "#1b1c1e", n=12, depth=FRONT_DEPTH, facing=0.25),
    box("front", "indicator-front", F_AMBER_Z[0], F_AMBER_Z[1], F_UNIT_Y[0] + 0.004, F_UNIT_Y[1] - 0.004, "lens", AMBER, n=12, depth=FRONT_DEPTH, facing=0.25),
    box("front", "fog-front", F_CLEAR_Z[0], F_CLEAR_Z[1], F_UNIT_Y[0] + 0.004, F_UNIT_Y[1] - 0.004, "lens", CLEAR, n=14, depth=FRONT_DEPTH, facing=0.25),
    box("front", "plate-front", 0.0, F_PLATE[0], F_PLATE[1], F_PLATE[2], "satin", "#e9e9e6", n=20, depth=FRONT_DEPTH, facing=0.3),
    box("front", "intake-front", 0.0, F_INTAKE[0], F_INTAKE[1], F_INTAKE[2], "satin", "#1f2022", n=20, depth=FRONT_DEPTH, facing=0.3,
        stripes=[round((F_INTAKE[2] - F_INTAKE[1]) / 3, 4), 0.3]),
]
decals += [
    box("rear", "indicator-rear", R_AMBER_Z[0], R_AMBER_Z[1], R_STRIP_Y[0], R_STRIP_Y[1], "lens", AMBER, n=12, depth=REAR_DEPTH, facing=0.25),
    box("rear", "taillight", R_TAIL_Z[0], R_TAIL_Z[1], R_STRIP_Y[0], R_STRIP_Y[1], "lens", RED, n=16, depth=REAR_DEPTH, facing=0.25),
    box("rear", "reverse-light", R_REVERSE_Z[0], R_REVERSE_Z[1], R_STRIP_Y[0] + 0.012, R_STRIP_Y[1] - 0.012, "lens", CLEAR, n=12, depth=REAR_DEPTH, facing=0.25),
    box("rear", "reflector-band", 0.0, R_BAND_Z, R_STRIP_Y[0] + 0.004, R_STRIP_Y[1] - 0.004, "lens", "#8f1a1f", n=24, depth=REAR_DEPTH, facing=0.25),
    box("rear", "plate-rear", 0.0, R_PLATE[0], R_PLATE[1], R_PLATE[2], "satin", "#e9e9e6", n=20, depth=REAR_DEPTH, facing=0.3),
    box("rear", "badge-rear", 0.0, R_BADGE[0], R_BADGE[1], R_BADGE[2], "satin", "#2a2b2e", n=16, depth=REAR_DEPTH, facing=0.2),
]
# Windscreen in plan (LINE plan: glass base 446 px → 1.458 m at the centre, header 362 px → 1.98 m;
# ahead of the glass the black cowl panel / wipers that PHOTO01 shows from 1.38 m).
screen_top = [[1.458, 0.0], [1.462, 0.30], [1.49, 0.50], [1.55, 0.58], [1.80, 0.555], [1.93, 0.49], [1.955, 0.30],
              [1.96, 0.0]]
cowl_top = [[X_COWL, 0.0], [X_COWL, 0.45], [1.49, 0.50], [1.462, 0.30], [1.458, 0.0]]
rear_top = [[PX(REAR_WIN_PX[1]), 0.0], [PX(REAR_WIN_PX[1]), PZ(REAR_WIN_PX[2]) - 0.02], [PX(REAR_WIN_PX[1]) + 0.05, PZ(REAR_WIN_PX[2])],
            [PX(REAR_WIN_PX[0]) - 0.05, PZ(REAR_WIN_PX[2])], [PX(REAR_WIN_PX[0]), PZ(REAR_WIN_PX[2]) - 0.03], [PX(REAR_WIN_PX[0]), 0.0]]
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rear_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    {"id": "cowl-grille", "plane": "top", "kind": "fill", "points": cowl_top, "finish": "satin", "color": "#1f2022", "facing": 0.15,
     "depth": [0.8, 2]},
    box("top", "engine-grille", PX(GRILLE_PX[1]), PX(GRILLE_PX[0]), 0.0, PZ(GRILLE_PX[2]), "satin", "#1f2022", n=20,
        stripes=[0.014, 0.5], facing=0.3, depth=[0.7, 2]),
    box("top", "crest", PX(634), PX(627), 0.0, 0.022, "chrome", "#c9a24e", facing=0.3, depth=[0.5, 2]),
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left", "finish": "satin", "color": GAP, "facing": 0.3,
     "depth": [0.7, 2], "points": ellipse(FLAP[0], FLAP[1], FLAP[2] / 2, FLAP[3] / 2, 14)},
    {"id": "hood-gap", "plane": "top", "kind": "line", "finish": "satin", "color": GAP, "facing": 0.3,
     "points": [[X_LID0, 0.0]] + LID_Z},
    {"id": "lid-gap", "plane": "top", "kind": "line", "finish": "satin", "color": GAP, "facing": 0.3,
     "points": [[PX(REAR_WIN_PX[0]), 0.0], [PX(REAR_WIN_PX[0]), 0.50], [3.9, 0.48], [4.10, 0.45], [4.14, 0.0]]},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]

# ------------------------------------------------------------------ parts
LAMP_R = 0.112          # round lens Ø 0.224 + 9 mm bezel = 0.242 (LINE front view lens 39 px = 0.247 m;
                        # PHOTO09 lamp incl. bezel 0.23–0.24 m)
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
        "front": {"diameter": round(TYRE_F, 4), "width": 0.205, "rim": RIM, "design": "cup", "face": "#c9ccd1", "lip": "#d6d8dc", "caliper": "#202022"},
        "rear": {"diameter": round(TYRE_R, 4), "width": 0.245, "rim": RIM, "design": "cup", "face": "#c9ccd1", "lip": "#d6d8dc", "caliper": "#202022"},
    },
    "headlight": {
        # Poly-ellipsoid lamp laid back into the wing: lens mid-point from the side views (LINE (0.313,
        # 0.641), PHOTO01 bowl (0.33, 0.65)), z from the front / plan views and PHOTO09.
        "centre": [0.315, 0.645, LAMP_Z],
        "outline": [[round(float(np.cos(a)) * LAMP_R, 4), round(float(np.sin(a)) * LAMP_R, 4)] for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)],
        "yaw": 6,
        "pitch": LAMP_PITCH,
        "ring": 0.009,
        "ringColor": "#c9ced3",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "projector",
    },
    # Teardrop "Cup design" mirror on each door, body colour (geometry.json 993; PHOTO01 head
    # x 1.615–1.76, y 0.82–0.995; LINE plan z 0.80–0.90, front view to 0.98).
    "mirror": {"at": [MIRROR[0], MIRROR[1], 0.79], "size": [MIRROR[2], MIRROR[3], 0.16], "shape": "aero", "color": "paint", "finish": "paint"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    "exhausts": [[EXHAUST[0], EXHAUST[1], EXHAUST[2], EXHAUST[3]], [EXHAUST[0], EXHAUST[1], -EXHAUST[2], EXHAUST[3]]],
}


# ------------------------------------------------------------------ outputs
def rescaled(crop, sx, sy, name):
    x0, y0, x1, y1 = crop
    img = cv2.imread(LINE)[y0:y1, x0:x1]
    h, w = img.shape[:2]
    out = cv2.resize(img, (int(round(w * sx)), int(round(h * sy))), interpolation=cv2.INTER_CUBIC)
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, out)
    return os.path.relpath(path, ROOT)


def photo_check(path):
    from PIL import Image, ImageDraw
    im = Image.open(PHOTO01).convert("RGB")
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.3)
    dr = ImageDraw.Draw(im)
    P = lambda x, y: tuple(float(v) for v in np.asarray(photo_px(x, y)).reshape(-1)[:2])
    # centre-line features are drawn where the camera sees them (inverse of centre_line()).
    Pc = lambda x, y: P(PC[0] + (x - PC[0]) * K, PC[1] + (y - PC[1]) * K)
    xs = [L * i / 300 for i in range(301)]
    secs = [half_section(body, x) for x in xs]
    dr.line([P(x, max(p[1] for p in s)) for x, s in zip(xs, secs)], fill="#ff2d55", width=2)
    dr.line([Pc(x, mono(body["topY"], x)) for x in xs], fill="#ff8fab", width=1)
    dr.line([P(x, mono(body["rockerY"], x)) for x in xs], fill="#ff9500", width=2)
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
    im.crop((150, 230, 1760, 760)).save(path)


P_LONG = L / (PL_NOSE - PL_TAIL)
k_plan = P_LAT / P_LONG
PLAN_CROP = (0, 215, 684, 519)
FRONT_CROP = (672, 272, 988, 492)
REAR_CROP = (0, 0, 312, 212)
if __name__ == "__main__":
    top_img = rescaled(PLAN_CROP, 1.0, k_plan, "ref-top.png")
    front_img = rescaled(FRONT_CROP, 1.0, 1.0, "ref-front.png")
    rear_img = rescaled(REAR_CROP, 1.0, 1.0, "ref-rear.png")
    calib = {
        # Virtual wheel centres at the model's axles in the LINE frame (the drawn wheels are 1.8 % too
        # close together); scale = 6.2852 mm/px, axle row 169.22 px.
        "side": {"image": os.path.relpath(LINE, ROOT), "wheelF": [round(L_NOSE - FA / LS, 2), L_AXROW],
                 "wheelR": [round(L_NOSE - RA / LS, 2), L_AXROW], "tipF": L_NOSE, "crop": [300, 0, 988, 222]},
        "top": {"image": top_img, "tipF": PL_NOSE - PLAN_CROP[0], "tipR": PL_TAIL - PLAN_CROP[0],
                "centreY": (PL_CY - PLAN_CROP[1]) * k_plan, "crop": None},
        # End views: uniform scale anchored on the roof (the drawn ground lines are not consistent).
        "front": {"image": front_img, "centreX": F_CX - FRONT_CROP[0], "groundY": F_ROOF - FRONT_CROP[1] + ROOF_H / F_LAT,
                  "left": F_CX - FRONT_CROP[0] - (WIDTH / 2) / F_LAT, "right": F_CX - FRONT_CROP[0] + (WIDTH / 2) / F_LAT,
                  "width": WIDTH, "crop": None},
        "rear": {"image": rear_img, "centreX": R_CX - REAR_CROP[0], "groundY": R_ROOF - REAR_CROP[1] + ROOF_H / R_LAT,
                 "left": R_CX - REAR_CROP[0] - (WIDTH / 2) / R_LAT, "right": R_CX - REAR_CROP[0] + (WIDTH / 2) / R_LAT,
                 "width": WIDTH, "crop": None},
    }
    with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
        json.dump(car, f, indent=1)
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    photo_check(os.path.join(OUT_DIR, "check-photo-side.png"))
    print("wrote", STOP, "L", L, "FA", FA, "RA", RA, "roof", ROOF_H, "plan lat mm/px", round(P_LAT * 1000, 4),
          "long", round(P_LONG * 1000, 4), "max half px", MAX_HALF_PX)
