"""Trace: 05-g-series-1974 — 911 2.7 Coupé, G-series, narrow body (MY1974–77).

Spec car (research/specs.json 05 + history.md "Timeline stop recommendations"): base 911 2.7
Coupé, 150 PS, narrow body, no spoiler, 5.5J x 15 steel wheels with chromed hub caps,
165 HR 15 tyres. Official figures: L 4291, W 1610, H 1320, WB 2271, tracks 1360 / 1342 mm
(specs.json 05); front overhang 932 mm (drawing dimension 36.69 in, geometry.json 05).

This script also holds the G-series body model shared by 06 (Turbo), 07 (SC) and 08
(Carrera 3.2): they import `gseries_body()` and pass their own widths / flares / references.

References (research/blueprints/05-g-series-1974/, research/photos/05-g-series-1974/):
  SIDE   brochure_1975-US-911S_side-front-rear.png — official Porsche dimension drawing of
         the 1975 US 911 S (side / front / rear, inch dimensions). Primary for the side view.
  PHOTO  photos/05…/01-side-left.jpg — Porsche studio profile of a 1974 G-series coupé
         (near-orthographic; "tracing": "side"). Door handle, filler flap, bumper details and
         the side-photo overlay.
  FRONT/REAR  the same brochure sheet's end views: lateral positions (scaled by the official
         width); heights only for features not visible in the side view (their vertical
         scale differs from the lateral one by ~4 %).
  PLAN   no 1974–77 plan view exists in the research set; blueprints/05 sources.json says to
         use the SC / Carrera 3.2 plan views. Composite of vec-30946 (07), vec-1941 (08) and
         the Autocar SC package drawing tbp-58380 (07), normalised per drawing, scaled to the
         official widths (narrow body: 1610 mm at both axles; SC/Carrera: 1610 / 1652 mm,
         FISA B-207 via geometry.json 07).
  LID    the front-lid centre line (hidden behind the wings in every side view) is the dashed
         hidden line of the Polish 930 plan (blueprints/06…/dd_911-turbo_plan01…, same
         G-series lid), expressed as a drop below the wing silhouette.

Calibration (side view, every number measured on the sheet):
  front / rear axle x = 327.4 / 1069.4 px (centroids of the vertical extension lines of the
  36.69 in / 89.41 in dimensions, which pass through the wheel centres; the drawn tyres
  (r 104.6 px) are centred on them) → WB 742.0 px = 2271 mm → 3.0606 mm/px.
  ground line y = 534.5 px (centre of the thick ground line = tyre bottoms).
  Checks: roof outer edge y 102 → height 1.3237 m (official 1.320, +0.3 %);
  front tip (extension line) x 23.5 → front overhang 0.930 m (official 0.932);
  drawn tyre r 104.6 px = 0.320 m = the labelled 185/70 VR 15 (0.640 m).
  Rear overhang: drawn 5 % too long relative to the printed figures (see K_REAR below);
  the region behind the rear arch is compressed so the drawn extreme (the rubber bumper
  guard, x 1443.5) lands on the official length.
Front view: centre x 303.5 (body outline 31 / 576 px) → lateral 1610 mm / 545 px =
  2.954 mm/px; vertical: ground y 1165.5, roof y 736.5 ↔ 1.320 m → 3.077 mm/px.
Rear view: centre x 1128 (outline 853 / 1403) → lateral 1610 / 550 px = 2.927 mm/px (check:
  the printed 36.82 in = 935 mm rear-window width spans 320 px → 2.922 mm/px);
  vertical: printed 51.97 in spans y 735.5 → 1168 → 3.052 mm/px.

Run: research/tools/venv python research/traces/05-g-series-1974.py
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from scipy.signal import savgol_filter  # noqa: E402
from trace_lib import half_section, silhouette_from_drawing, simplify  # noqa: E402

STOP = "05-g-series-1974"
BP = os.path.join(ROOT, "research", "blueprints")
SHEET = os.path.join(BP, STOP, "brochure_1975-US-911S_side-front-rear.png")
PHOTO_SIDE = os.path.join(ROOT, "research", "photos", STOP, "01-side-left.jpg")

# ------------------------------------------------------------------ official figures (G-series body)
L = 4.291            # specs.json 05 length (identical for 06/07/08, geometry.json)
WB = 2.271           # specs.json 05 wheelbase (07/08/06: 2272 — 1 mm, ignored for the shell)
FA = 0.932           # geometry.json 05 overhang front (36.69 in; FISA 209a = 932 for 06/07/08)
RA = round(FA + WB, 4)

# ------------------------------------------------------------------ side calibration
FA_PX, RA_PX = 327.4, 1069.4
GROUND_Y = 534.5
S = WB / (RA_PX - FA_PX)          # metres per pixel (3.0606 mm/px)
# Rear overhang: the sheet's extreme (the rubber bumper guard, dimension extension line at
# x 1443.5) is drawn 374 px = 1.145 m behind the rear axle, but the printed dimensions give
# 168.94 − 89.41 − 36.69 = 42.84 in = 1.088 m (the source notes list "rear overhang measures
# 44.2 in vs derived 42.8 in"). The rear arch is drawn symmetric about the axle (legs at
# 946 / 1192 px), and the dd930 official drawing and three side photos place the rear
# bellows 0.59–0.634 m behind the axle (this sheet: 0.654 at the wheelbase scale), so the
# stretch lies behind the arch: x > 1192 px is compressed by K_REAR so the guard tip lands
# on the official length (bellows → 0.633 m).
ARCH_R_PX = 1192.0
TAIL_PX = 1443.5
K_REAR = (L - (FA + (ARCH_R_PX - FA_PX) * S)) / ((TAIL_PX - ARCH_R_PX) * S)   # 0.926


def X(px):
    if px <= ARCH_R_PX:
        return round(FA + (px - FA_PX) * S, 4)
    return round(FA + (ARCH_R_PX - FA_PX) * S + (px - ARCH_R_PX) * S * K_REAR, 4)


def Y(py):
    return round((GROUND_Y - py) * S, 4)


def PXX(x):
    """car x (m) → side-sheet px."""
    x_arch = FA + (ARCH_R_PX - FA_PX) * S
    if x <= x_arch:
        return FA_PX + (x - FA) / S
    return ARCH_R_PX + (x - x_arch) / (S * K_REAR)


def curve(points):
    return [[X(px), Y(py)] for px, py in points]


def lerp_keys(pairs):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pairs]


def lin(c, x):
    return float(np.interp(x, [p[0] for p in c], [p[1] for p in c]))


# ------------------------------------------------------------------ side view: top edge (auto)
def top_edge():
    """First dark pixel per column; the 23.03 in / 25.39 in dimension annotations that sit
    on the windscreen and rear window are masked first."""
    g = cv2.imread(SHEET, cv2.IMREAD_GRAYSCALE)
    h = g.copy()
    masks = [
        np.array([[455, 170], [480, 150], [640, 55], [660, 60], [668, 100], [650, 112], [505, 214], [488, 216], [462, 185]]),
        np.array([[975, 60], [1000, 55], [1210, 135], [1205, 175], [1195, 200], [1180, 196], [990, 118], [978, 112]]),
    ]
    for m in masks:
        cv2.fillPoly(h, [m], 255)
    dark = h < 140
    top = {}
    for x in range(26, 1440):
        ys = np.nonzero(dark[60:540, x])[0]
        if len(ys):
            top[x] = int(ys[0] + 60)
    # Behind x 1395 the outline is the bumper top (y 372) and the US guard.
    for x in range(1395, 1445):
        top[x] = 372
    # The engine-lid grille (x 1203–1285) is drawn as a row of dots standing on the lid
    # line; bridge the lid surface under it.
    for a, b in ((1199, 1289), (1383, 1389)):   # (2nd: a break in the drawn lid line)
        for x in range(a, b + 1):
            top[x] = top[a] + (top[b] - top[a]) * (x - a) / (b - a)
    return top


TOP = top_edge()


def top_y_at(x):
    return Y(TOP[int(round(PXX(x)))])


# ------------------------------------------------------------------ side view: lower edge (hand-read, 10 px grids)
# Nose rubber → bumper bottom → apron → front arch (outer edge of the black wheel-well band)
# → painted sill bottom → rear arch → rear apron → rear bumper bottom → bumper face.
# The bumper faces are modelled blunt (the section at x = 0 / L spans the bumper face):
# the rounded rubber nose / US guard tips would otherwise make the loft converge to a point.
BOTTOM = [(22.9, 399), (35, 402), (45, 403), (52, 410), (57, 425), (63, 436), (72, 441),
          (100, 443), (130, 446), (160, 449), (185, 451), (197, 451),
          (198, 440), (200, 430), (203, 420), (205, 410), (208, 400), (211, 390), (215, 380), (220, 370),
          (226, 360), (234, 350), (243, 340), (255, 330), (270, 321), (280, 316), (290, 313), (300, 311),
          (310, 309), (320, 308), (330, 308), (340, 308), (350, 309), (360, 311), (370, 313), (380, 317),
          (390, 322), (402, 330), (413, 340), (421, 350), (428, 360), (434, 370), (438, 380), (442, 390),
          (445, 400), (448, 410), (451, 420), (453, 430), (456, 440), (458, 450), (462, 457),
          (475, 458), (600, 458), (800, 458), (940, 458),
          (946, 455), (947, 450), (948, 440), (949, 430), (950, 420), (952, 410), (954, 400), (957, 390),
          (961, 380), (965, 370), (970, 360), (978, 350), (988, 340), (1004, 330), (1020, 324), (1030, 321),
          (1040, 319), (1050, 318), (1060, 317), (1080, 317), (1090, 318), (1100, 320), (1110, 322),
          (1120, 326), (1129, 330), (1144, 340), (1154, 350), (1162, 360), (1169, 370), (1173, 380),
          (1177, 390), (1180, 400), (1183, 410), (1185, 420), (1187, 430), (1189, 440), (1192, 448),
          (1198, 452), (1250, 450), (1300, 447), (1330, 443), (1345, 433), (1360, 425), (1390, 420),
          (1425, 420), (TAIL_PX, 418)]
SILHOUETTE_BOT = curve(BOTTOM)

# ------------------------------------------------------------------ side view: hand-read lines (px)
COWL_PX, SCREEN_TOP_PX = 497, 660     # windscreen base (cowl) and top (roof front), silhouette
# Door glass incl. the front vent window, lowest-front first, clockwise in side view.
DLO_DOOR = [(608, 240), (640, 205), (670, 172), (695, 150), (703, 144), (711, 143), (740, 141), (780, 141),
            (820, 145), (860, 150), (905, 157), (911, 158), (900, 185), (890, 210), (879, 240), (800, 241),
            (700, 241)]
VENT = [(665, 240), (706, 144)]       # vent-window frame behind the A-pillar
DLO_QUARTER = [(894, 241), (910, 205), (929, 161), (940, 160), (975, 167), (1020, 178), (1050, 189),
               (1070, 200), (1080, 210), (1085, 222), (1080, 232), (1060, 236), (1000, 239), (940, 241)]
BELT_CABIN = [(606, 243), (700, 243), (800, 243), (900, 243), (1000, 242), (1080, 238)]
RAIL_CABIN = [(676, 124), (700, 136), (720, 133), (780, 132), (830, 136), (880, 143), (930, 152),
              (980, 164), (1030, 180), (1070, 195)]
# Drip rail continuing down the C-pillar as the "flyline" (edge of the engine-lid deck).
FLYLINE = [(1100, 200), (1150, 221), (1200, 243), (1250, 266), (1300, 290), (1313, 297), (1360, 324), (1380, 337)]
DOOR = [(522, 257), (510, 262), (503, 290), (498, 330), (497, 380), (500, 415), (504, 426), (835, 426),
        (843, 390), (855, 340), (868, 290), (877, 258), (880, 248)]
# Impact bumpers, side view: top 352 / bottom 404 (front), top 372 / bottom 420 (rear).
BUMPER_F_TOP, BUMPER_F_BOT = 352, 404
BUMPER_R_TOP, BUMPER_R_BOT = 372, 420
STRIP_F = (366, 388)                  # black rubbing strip band on the bumper side (front)
STRIP_R = (384, 400)                  # … rear
BELLOWS_F_X = (140, 190)              # accordion bellows between bumper and wing (ribbed)
BELLOWS_R_X = (1283, 1330)
INDICATOR_SIDE_X = (26, 50)           # amber lens wrapping round the bumper corner (photo: front 45 mm)
TAIL_SIDE = [(1283, 372), (1305, 343), (1373, 343), (1377, 372)]
ROCKER_STRIP = (426, 438)             # black rubbing strip above the painted sill (x 462–945)
EXHAUST_SIDE = (1368, 435)            # pipe outlet (x, y) in the side view


# ------------------------------------------------------------------ plan view composite
def plan_profiles():
    """Half-width profiles of three G-series plan views (SC / Carrera 3.2 body), each
    normalised: u = (x - tip) / (bumper face - tip); h = min(both sides) (mirrors and the
    side of the car with the door-mirror spike drop out)."""
    out = {}

    def by_saturation(path, roi, tip, face, centre):
        im = cv2.imread(path)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        x0, y0, x1, y1 = roi
        m = hsv[y0:y1, x0:x1, 1] > 50
        us, hs = [], []
        for i in range(m.shape[1]):
            ys = np.nonzero(m[:, i])[0]
            if len(ys) > 3 and tip <= x0 + i <= face:
                us.append((x0 + i - tip) / (face - tip))
                hs.append(min(centre - (ys[0] + y0), (ys[-1] + y0) - centre))
        return np.array(us), np.array(hs, float)

    def by_lines(path, roi, tip, face, centre):
        g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        m = silhouette_from_drawing(g, roi, close=3, thresh=150)
        us, hs = [], []
        for x in range(tip, face + 1):
            ys = np.nonzero(m[:, x])[0]
            if len(ys):
                us.append((x - tip) / (face - tip))
                hs.append(min(centre - ys[0], ys[-1] - centre))
        return np.array(us), np.array(hs, float)

    # tip / bumper face (rubber buffers excluded) / centre row, read on 10 px grids
    out["vec-30946 (SC)"] = by_saturation(os.path.join(BP, "07-911-sc-1978", "vec-30946_porsche-911sc_4view-dims-watermarked.jpg"),
                                          (60, 470, 840, 790), 84, 806, 629.0)
    out["vec-1941 (Carrera 3.2)"] = by_saturation(os.path.join(BP, "08-carrera-32-1984", "vec-1941_porsche-911-carrera-1985_4view-dims-watermarked.jpg"),
                                                  (60, 472, 820, 782), 68, 797, 628.5)
    out["tbp-58380 (SC Autocar)"] = by_lines(os.path.join(BP, "07-911-sc-1978", "tbp-58380_porsche-911-sc-1981_autocar-top-side.png"),
                                             (2, 0, 845, 330), 2, 836, 166.5)
    return out


def plan_shape(grid):
    """Median normalised half-width (value 1 at the front axle); door mirrors bridged; a
    Savitzky–Golay filter (0.15 m window) removes the pixel steps / watermark noise of the
    small vendor drawings (±1 %) without blunting the nose and tail."""
    rows = []
    for us, hs in plan_profiles().values():
        hs = hs / np.interp(FA / L, us, hs)
        keep = (us < 0.33) | (us > 0.43)
        rows.append(np.interp(grid, us[keep], hs[keep]))
    med = np.median(np.array(rows), axis=0)
    return savgol_filter(med, 15, 2)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def plan_half_width(front_half, rear_half, flare=(0.37, 0.25, 0.30, 0.45)):
    """sideZ: the composite SC-body plan shape scaled to the official width at the front
    axle; the SC's rear-wing widening (composite: rises from RA-0.37 to RA-0.25, plateau,
    falls from RA+0.30 to RA+0.45 into the tail taper) is rescaled so the half-width at the
    rear axle equals `rear_half` (narrow body: the widening is removed)."""
    grid = np.linspace(0, 1, 431)
    shape = plan_shape(grid)
    xs = grid * L
    base = shape * front_half
    at_ra = float(np.interp(RA, xs, base))
    a0, a1, b0, b1 = flare
    w = smoothstep(RA - a0, RA - a1, xs) * (1 - smoothstep(RA + b0, RA + b1, xs))
    z = base + w * (rear_half - at_ra)
    return [[round(float(x), 4), round(float(v), 4)] for x, v in zip(xs, z)]


# ------------------------------------------------------------------ end views
F_CX, F_S, F_GY, F_VS = 303.5, 2.954 / 1000, 1165.5, 3.077 / 1000
R_CX, R_S, R_GY, R_VS = 1128.0, 2.927 / 1000, 1168.0, 3.052 / 1000


def FZ(px):
    return round(abs(px - F_CX) * F_S, 4)


def FY(py):
    return round((F_GY - py) * F_VS, 4)


def RZ(px):
    return round(abs(px - R_CX) * R_S, 4)


def RY(py):
    return round((R_GY - py) * R_VS, 4)


# Headlamp (front view, 10 px grid): chrome ring circle x 51–131 / y 896–976 → centre x 91,
# ring Ø 80 px, lens Ø 66 px (dd930 official front view, scaled by its 1775 mm width: 0.62 m).
LAMP_Z = FZ(91)                       # 0.628
LAMP_RING_D = round(80 * F_S, 4)      # 0.236
LAMP_LENS_D = round(66 * F_S, 4)      # 0.195
FENDER_CREST_Z_FRONT = 0.61           # wing ridge over the lamp, just inboard of its centre
FENDER_CREST_Z_COWL = FZ(80)          # front view: wing top meets the A-pillar base, x ≈ 80 → 0.660
HOOD_EDGE_Z_NOSE = FZ(160)            # front view: lid front corner x 160 → 0.424
HOOD_EDGE_Z_COWL = 0.585              # dd930 plan: lid side edge at the cowl, (1213.5-1050) px × 3.576 mm/px
# Front view: the printed 51.97 in dimension spans the A-pillar bases (door tops) x 90–528;
# measured with the width scale that is 1.294 m (printed 1.320 m — the same figure as the
# height, possibly a re-used label). The measured value is used.
CABIN_BELT_Z = round(438 * F_S / 2, 4)   # 0.647
CABIN_RAIL_Z = RZ(945)                # rear view: roof / C-pillar corner x 945 → 0.536
REAR_WINDOW_Z = round(0.9352 / 2, 4)  # rear view: printed 36.82 in rear-window width → 0.468
HIP_CREST_Z = RZ(897)                 # rear view: rear-wing ridge leaves the C-pillar base x 897 → 0.676
LID_EDGE_Z_TOP = RZ(963)              # rear view: engine-lid side edge at y 880 → 0.483
LID_EDGE_Z = RZ(982)                  # … and at the tail panel (y 960) → 0.427
WING_TOP_Y_COWL = FY(878)             # front view: wing top at the A-pillar base → 0.885 m

# Front-lid centre line = wing silhouette minus the drop measured on the Polish 930 side
# view (dashed hidden lid line; 3.870 mm/px from its 2272 mm wheelbase): 0.124 m at 0.50 m
# ahead of the front axle, 0.091 at 0.35, 0.066 at 0.23, 0.050 at 0.15, 0.031 at 0.04,
# merging ≈0.06 m behind the axle. Lid front edge: front view y 976 → 0.583 m at x ≈ 0.16.
LID_DROP = [(0.34, 0.124), (FA - 0.50, 0.124), (FA - 0.35, 0.091), (FA - 0.23, 0.066), (FA - 0.15, 0.05),
            (FA - 0.04, 0.031), (FA + 0.06, 0.0), (L, 0.0)]
LID_NOSE = [(0.16, FY(976)), (0.25, 0.655)]


def lid_centre():
    pts = list(LID_NOSE)
    for x in np.arange(0.34, X(COWL_PX) + 1e-6, 0.04):
        pts.append((x, top_y_at(x) - lin(LID_DROP, x)))
    pts.append((X(COWL_PX), Y(TOP[COWL_PX])))
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pts]


# ------------------------------------------------------------------ body model
def dedupe(c):
    out = []
    for x, v in sorted(c):
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([round(float(x), 4), round(float(v), 4)])
    return out


def top_between(x0px, x1px, step=3):
    return [[X(x), Y(v)] for x, v in sorted(TOP.items()) if x0px <= x <= x1px and x % step == 0]


def tail_keys(drop):
    """Common tail for P3–P6: the engine lid's rear edge sits on the tail-lamp / reflector
    row (rear view: lid edge y ≈ 970 → 0.60 m; side view: lid line ends at x 1394, y 339),
    which drops vertically to the bumper top (y 372) at x 1396–1398; the bumper top then
    runs to the bumper face. `drop` lowers the outer curves slightly (crowned deck)."""
    return [[X(1388), round(0.600 - drop, 4)], [X(1394), round(0.598 - drop, 4)], [X(1396.5), round(0.53 - drop / 2, 4)],
            [X(1398.5), round(Y(372) - drop / 3, 4)], [X(1420), round(Y(372) - drop / 3, 4)], [L, round(Y(374) - drop / 3, 4)]]


def gseries_body(side_z, bottom=None, crest_z_over=None, arch_lift=0.03, floor_over=None, apron=True):
    """The G-series coupé body. `side_z`: plan half-width curve; `bottom`: lower silhouette
    (arches, aprons) — defaults to the 05 drawing; `crest_z_over`: replacement crestZ keys
    (flared wings); `floor_over`: replacement floorY keys; `apron`: pull P1 in over the front
    apron drop (the body-coloured apron face under the bumper)."""
    bottom = bottom or SILHOUETTE_BOT
    lid = lid_centre()

    # P6 top centre: bumper nose → lid → windscreen → roof → rear window → engine lid →
    # tail panel → rear bumper top.
    # At the tips the section degenerates to a line, so P0…P6 must rise monotonically there
    # (otherwise the fan of triangles folds and the normals flip): the bumper top is modelled
    # crowned, crest < belt < rail < top by 3 mm steps over the first 0.1 m.
    top_y = [[0.0, Y(358)]] + curve([(26, 355), (38, 353), (50, 353)]) + lid
    top_y += top_between(COWL_PX + 1, 1382) + tail_keys(0.0)

    # P3 crest: bumper top → wing front face (silhouette up to the lamp top) → wing ridge
    # (= silhouette until the lid takes over at FA+0.06) → wing top level to the A-pillar
    # base (front view 0.885 m) → door shoulder (7 px = 21 mm below the window sill) →
    # rear-wing ridge (rear view: 0.888 m at the C-pillar base; then 40 mm below the
    # flyline) → tail-lamp top → bumper top.
    crest = [[0.0, Y(358) - 0.009], [X(26), Y(355) - 0.009], [X(38), Y(353) - 0.009], [X(50), Y(353) - 0.006]]
    crest += curve([(62, 352), (74, 349), (92, 337), (110, 328),
                                     (116, 317), (122, 293), (128, 271)])
    crest += top_between(134, int(PXX(FA + 0.06)))
    crest += [[FA + 0.25, 0.884], [X(COWL_PX - 17), WING_TOP_Y_COWL], [X(560), 0.878]]
    crest += curve([(606, 250), (700, 250), (800, 250), (900, 250), (1000, 249), (1085, 245)])
    crest += [[X(1110), RY(877)]]
    for px, py in FLYLINE:
        if 1150 <= px < 1373:
            crest.append([X(px), round(Y(py) - 0.04, 4)])
    crest += curve([(1373, 343)]) + tail_keys(0.014)

    # P4 belt: lid side edge ahead of the windscreen (lid crown 30 mm, as 02), window sill,
    # engine-lid side edge (flyline) behind the quarter window.
    belt = [[0.0, Y(358) - 0.006], [X(26), Y(355) - 0.006], [X(38), Y(353) - 0.006], [X(50), Y(353) - 0.004],
            [0.16, LID_NOSE[0][1] - 0.02]]
    for x, y in lid:
        if 0.2 <= x < X(600):
            belt.append([x, min(y - 0.03, lin(crest, x) - 0.012)])
    belt += curve(BELT_CABIN)
    belt += curve([(p[0], p[1] + 1) for p in FLYLINE]) + tail_keys(0.010)

    # P5 roof rail: on the lid ahead of the cowl, up the A-pillar with the screen, drip
    # rail over the doors, flyline behind the cabin.
    rail = [[0.0, Y(358) - 0.003], [X(26), Y(355) - 0.003], [X(38), Y(353) - 0.003], [X(50), Y(353) - 0.002]]
    for x, y in lid:
        if x >= 0.16:
            rail.append([x, round(y - 0.004, 4)])
    rail += top_between(COWL_PX + 6, SCREEN_TOP_PX - 12)
    rail += curve(RAIL_CABIN)   # the deck part behind the cabin is added after the z curves

    # P0 floor centre: bumper bottoms, aprons, floor pan (6.3 in = 160 mm printed under the
    # floor centre), rear apron.
    floor_keys = floor_over or lerp_keys([(0.0, Y(401)), (X(45), Y(404)), (X(72), Y(442)), (X(190), Y(452)), (FA, 0.20),
                                          (X(470), Y(482)), (X(940), Y(482)), (RA, 0.21), (X(1250), Y(452)), (X(1345), Y(436)),
                                          (X(1390), Y(421)), (L, Y(420))])
    # The floor centre never sits above the lower edge (no notch at the centre line).
    floor_y = [[x, round(min(lin(floor_keys, x), lin(bottom, x) - 0.004), 4)]
               for x in sorted(set([p[0] for p in floor_keys] + list(np.linspace(0, 0.6, 31)) + list(np.linspace(L - 0.8, L, 31))))]

    # P2 widest point height: bumper rubbing-strip level at the ends, mid-door elsewhere;
    # never below the arch edge + 30 mm so the arch cut-out stays the lower boundary.
    # Over the front apron (see the P1 dip below) P2 sits at the apron's lower corner, so
    # the section is a box: flat bottom from the centre line out to the plan width, then
    # the bumper side face up to the crest.
    base_side = [(0.0, Y(377)), (0.40, Y(377)), (0.60, 0.55), (L - 0.62, 0.55), (L - 0.42, Y(392)), (L, Y(392))]
    side_y = []
    for x in sorted(set(list(np.linspace(0, L, 140)) + list(np.linspace(0.04, 0.40, 37)))):
        b = float(np.interp(x, [a for a, _ in base_side], [v for _, v in base_side]))
        b = max(b, lin(bottom, x) + arch_lift)
        k = float(smoothstep(0.05, 0.075, x) * (1 - smoothstep(0.26, 0.36, x))) if apron else 0.0
        side_y.append([x, b + k * (lin(bottom, x) + 0.015 - b)])

    # z curves
    arch = lambda x: abs(x - FA) < 0.34 or abs(x - RA) < 0.33   # noqa: E731
    # Front apron: behind the bumper the lower edge drops from the bumper bottom (0.40 m) to
    # the apron (0.285 m) between x 0.07 and 0.15. A drop swept by the P0→P1 (underbody)
    # segment would paint the apron face underbody-black; the front view of the drawing
    # shows it body-coloured, so P1 is pulled to the centre line over the drop (the apron
    # face is then formed by P1→P2) and moved back out by x ≈ 0.28.
    dip = lambda x: 1 - float(smoothstep(0.055, 0.075, x) * (1 - smoothstep(0.155, 0.28, x))) if apron else 1.0   # noqa: E731
    rocker_z = [[x, round(max(0.0, (z - (0.012 if arch(x) else 0.04)) * dip(x)), 4)] for x, z in side_z]
    crest_base = crest_z_over or lerp_keys([
        (0, 0), (X(30), 0.50), (X(62), 0.60), (X(110), FENDER_CREST_Z_FRONT - 0.02), (X(128), FENDER_CREST_Z_FRONT),
        (FA + 0.25, 0.63), (X(COWL_PX - 17), FENDER_CREST_Z_COWL), (X(606), 0.70), (X(900), 0.71), (X(1085), 0.69),
        (X(1110), HIP_CREST_Z), (X(1313), 0.60), (X(1373), 0.55), (L - 0.03, 0.40), (L, 0)])
    belt_base = lerp_keys([(0, 0), (X(30), 0.30), (0.16, HOOD_EDGE_Z_NOSE), (X(COWL_PX - 17), HOOD_EDGE_Z_COWL),
                           (X(606), CABIN_BELT_Z), (X(1000), CABIN_BELT_Z - 0.005), (X(1080), CABIN_BELT_Z - 0.01),
                           (X(1150), LID_EDGE_Z_TOP), (X(1380), LID_EDGE_Z), (L - 0.03, 0.30), (L, 0)])
    roof_base = lerp_keys([(0, 0), (X(30), 0.12), (0.16, 0.16), (X(COWL_PX - 17), 0.30), (X(560), 0.44),
                           (X(SCREEN_TOP_PX), CABIN_RAIL_Z), (X(930), CABIN_RAIL_Z - 0.008), (X(1085), REAR_WINDOW_Z),
                           (X(1185), REAR_WINDOW_Z - 0.02), (X(1330), 0.26), (L, 0)])
    # Keep the section ordered at the tips (crest inside the plan outline, belt inside the
    # crest, rail inside the belt): the bumper ends are only ~0.1 m long.
    grid = sorted(set([p[0] for p in crest_base + belt_base + roof_base] + list(np.linspace(0, 0.6, 25)) +
                      list(np.linspace(L - 0.6, L, 25))))
    crest_z, belt_z, roof_z = [], [], []
    for x in grid:
        w = lin(side_z, x)
        c = min(lin(crest_base, x), 0.93 * w)
        b = min(lin(belt_base, x), 0.88 * c)
        r = min(lin(roof_base, x), 0.75 * b)
        crest_z.append([x, c])
        belt_z.append([x, b])
        roof_z.append([x, r])
    crest_z, belt_z, roof_z = (simplify(dedupe(c), 0.002) for c in (crest_z, belt_z, roof_z))

    # Rail behind the cabin: P4 is the drawn deck-edge line (drip rail down the rear-window
    # side, then the engine-lid gutter), so P5 (inboard, at roofZ) must lie ON the crowned
    # deck between the centre line and that edge: y5 = top − (top − y4)·(z5/z4)^p. Putting P5
    # at the edge height instead (02's convention) makes a W-shaped deck section with a
    # ridge along the centre line (scalloped decals on the rear window / grille). The
    # exponent is fitted to the rear view: the grille's top edge is 11 px (3.4 cm) lower at
    # z 0.375 (x 1000) than on the centre line (x 1128), while the side view puts the deck
    # edge 8.7 cm below the centre at z 0.48 → p = ln(0.034/0.087)/ln(0.375/0.48) = 3.8
    # (flat centre, rounded lid edges).
    for px in list(range(1100, 1381, 20)) + [1380]:
        x = X(px)
        top, y4 = lin(top_y, x), lin(belt, x)
        z4, z5 = lin(belt_z, x), lin(roof_z, x)
        rail.append([x, round(top - max(0.0, top - y4) * (z5 / z4) ** 3.8, 4)])
    rail += tail_keys(0.005)
    rail = dedupe(rail)

    body = {
        "floorY": floor_y,
        "rockerY": bottom,
        "rockerZ": simplify(rocker_z, 0.002),
        "sideY": simplify(side_y, 0.003),
        "sideZ": simplify(side_z, 0.0015),
        "crestY": simplify(dedupe(crest), 0.003),
        "crestZ": crest_z,
        "beltY": simplify(dedupe(belt), 0.003),
        "beltZ": belt_z,
        "roofY": simplify(dedupe(rail), 0.003),
        "roofZ": roof_z,
        "topY": simplify(dedupe(top_y), 0.003),
    }
    for k in ("sideZ", "rockerZ"):
        body[k][0] = [0.0, 0.0]
        body[k][-1] = [L, 0.0]
    for k, c in body.items():
        c = dedupe(c)
        c[0][0] = 0.0
        c[-1][0] = L
        body[k] = c
    fit_plan_width(body, side_z)
    return body


def fit_plan_width(body, target, iters=3):
    """The lofted section bulges ~1 cm beyond P2 between the sill and the shoulder, so the
    top-view outline (the section's max z) would exceed the traced plan half-width. Scale
    sideZ / rockerZ at their keys so the section max equals the plan target (official
    width)."""
    for _ in range(iters):
        for k in ("sideZ", "rockerZ"):
            for key in body[k][1:-1]:
                x = key[0]
                zmax = max(p[0] for p in half_section(body, x))
                want = lin(target, x)
                if zmax > 0.3 and zmax > want + 0.001:
                    key[1] = round(key[1] * want / zmax, 4)


# ------------------------------------------------------------------ decals
GLASS = "#1d2329"
CHROME = "#dfe2e5"
RUBBER = "#1b1b1c"
GAP = "#2a2a2a"
AMBER = "#e59a35"
RED = "#b8231d"
CLEAR = "#eef1f2"
BAND_RED = "#9e1c18"
FRONT = [-0.05, 0.45]
REAR = [L - 0.45, L + 0.05]


def even(pts, closed=True, spacing=0.05):
    """Re-space a polygon / polyline: every edge is split into equal parts no longer than
    `spacing`, keeping the original corners. The app resamples each decal to twice its
    point count evenly by arc length, so evenly spaced input keeps the corners (otherwise a
    rectangle's corners are cut off diagonally)."""
    ring = list(pts) + ([pts[0]] if closed else [])
    out = []
    for a, b in zip(ring[:-1], ring[1:]):
        n = max(1, int(round(float(np.hypot(b[0] - a[0], b[1] - a[1])) / spacing)))
        for k in range(n):
            t = k / n
            out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    if not closed:
        out.append(list(ring[-1]))
    return out


def side_decal(id_, pts, finish, color, kind="fill", spacing=0.06, **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": even(curve(pts), kind != "line", spacing),
         "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, spacing=None, **kw):
    """Axis-aligned rectangle decal: (a, b) = (x, y) side, (x, z) top, (z, y) front/rear."""
    w, h = abs(a1 - a0), abs(b1 - b0)
    sp = spacing or max(min(w, h), 2 * (w + h) / 14)
    d = {"id": id_, "plane": plane, "kind": "fill", "points": even([[a0, b0], [a0, b1], [a1, b1], [a1, b0]], True, sp),
         "finish": finish, "color": color}
    d.update(kw)
    return d


def strip(plane, id_, a0, a1, b0, b1, finish, color, **kw):
    """A thin straight band as a line decal (half-width = half the band height): long thin
    rectangles lose their ends when the app resamples them. Never with the satin finish:
    satin *lines* are drawn as panel gaps (darker paint) by the body shader."""
    assert finish != "satin", id_
    d = {"id": id_, "plane": plane, "kind": "line", "points": [[a0, (b0 + b1) / 2], [a1, (b0 + b1) / 2]],
         "width": round(abs(b1 - b0) / 2, 4), "finish": finish, "color": color}
    d.update(kw)
    return d


def lid_badge(body, y_lo, y_hi, half_w, finish, color):
    """Model script on the engine lid ("911", "911SC", "turbo", "Carrera"), given by its
    height range in the rear view and its half-width. It uses the `badge-model` slot in the
    top plane like the 1969–73 stop (03), so the script morphs across the timeline: the
    heights are converted to x on the sloping lid via the centre-line topY."""
    xs = np.linspace(3.7, 4.2, 501)
    ys = np.array([lin(body["topY"], x) for x in xs])
    x_hi = float(xs[np.argmin(np.abs(ys - y_hi))])
    x_lo = float(xs[np.argmin(np.abs(ys - y_lo))])
    return box("top", "badge-model", x_hi, x_lo, 0.0, half_w, finish, color, facing=0.15, depth=[y_lo - 0.02, y_hi + 0.02])


def ellipse(cx, cy, rx, ry, n=16):
    return [[cx + rx * float(np.cos(a)), cy + ry * float(np.sin(a))] for a in np.linspace(np.pi, 3 * np.pi, n, endpoint=False)]


def gseries_decals(trim="chrome", trim_color=CHROME, handle=("chrome", CHROME), rear_script=None, grille_z=None,
                   side_repeater=None, fog=None, guard=True, plate_front=False, extra=()):
    """Decals shared by the G-series stops (positions from the 05 references unless the
    caller overrides). `trim`: window frames / drip rail finish — chrome on 05 and the
    MY1978 SC; the anodised-black trim of 06 / 08 uses the rubber finish, because satin
    *line* decals are drawn as panel gaps (darker paint) by the body shader."""
    sill_top, sill_bot = ROCKER_STRIP
    decals = [
        side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35, spacing=0.09),
        side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35, spacing=0.09),
        side_decal("window-trim", DLO_DOOR[:12] + DLO_QUARTER[2:10], trim, trim_color, kind="line", depth=[0.45, 2], facing=0.4, spacing=0.1),
        side_decal("vent-divider", VENT, trim, trim_color, kind="line", depth=[0.45, 2], facing=0.3, spacing=1),
        side_decal("drip-rail", RAIL_CABIN + FLYLINE[:2], trim, trim_color, kind="line", depth=[0.4, 2], facing=0.45, spacing=0.12),
        side_decal("door-gap", DOOR, "satin", GAP, kind="line", depth=[0.55, 2], spacing=0.12),
        # Studio photo (G-series pull handle with the lock at its rear): X 2.42–2.60, Y 0.755–0.785.
        strip("side", "door-handle", 2.43, 2.59, 0.756, 0.784, handle[0], handle[1], depth=[0.6, 2]),
        # Black rubbing strip along the sill ("body-coloured sill panel with black rubbing strip").
        strip("side", "rocker-trim", X(462), X(945), Y(sill_bot), Y(sill_top), "rubber", RUBBER, depth=[0.6, 2]),
        # Impact bumpers in side view: the rubbing strip along the painted bumper side; the
        # amber indicator wraps round the front corner; accordion bellows behind the bumpers.
        strip("side", "bumper-front", 0.0, X(BELLOWS_F_X[0]), Y(STRIP_F[1]), Y(STRIP_F[0]), "rubber", RUBBER, depth=[0.0, 2], facing=0.2),
        strip("side", "bumper-rear", X(BELLOWS_R_X[1]), L, Y(STRIP_R[1]), Y(STRIP_R[0]), "rubber", RUBBER, depth=[0.0, 2], facing=0.2),
        box("side", "bellows-front", X(BELLOWS_F_X[0]), X(BELLOWS_F_X[1]), Y(BUMPER_F_BOT + 2), Y(BUMPER_F_TOP), "rubber", RUBBER, depth=[0.4, 2], facing=0.3),
        box("side", "bellows-rear", X(BELLOWS_R_X[0]), X(BELLOWS_R_X[1]), Y(BUMPER_R_BOT), Y(BUMPER_R_TOP), "rubber", RUBBER, depth=[0.4, 2], facing=0.3),
        box("side", "indicator-side", X(INDICATOR_SIDE_X[0]), X(INDICATOR_SIDE_X[1]), Y(STRIP_F[1] - 2), Y(STRIP_F[0] + 3), "lens", AMBER, depth=[0.3, 2], facing=0.25),
        side_decal("taillight-side", TAIL_SIDE, "lens", AMBER, depth=[0.5, 2], facing=0.25, spacing=0.05),
    ]
    if side_repeater:
        # (x0, x1, y0, y1) of the front-wing repeater, measured by the caller.
        decals.append(box("side", "side-repeater", *side_repeater, "lens", AMBER, depth=[0.6, 2], facing=0.3))

    # Front view (lateral from the 05 front view, heights from the side view).
    bf_top, bf_bot = Y(BUMPER_F_TOP), Y(BUMPER_F_BOT)
    decals += [
        # Rubbing strip across the bumper face: front view y 1000–1018, from the centre out to
        # the indicator (x 113) → z 0.563; side view band y 366–388.
        strip("front", "bumper-strip-front", 0.0, FZ(113), Y(388), Y(366), "rubber", RUBBER, depth=FRONT, facing=0.1),
        # Amber indicator in the bumper end: front view x 42–113 (divider x 60).
        box("front", "indicator-front", FZ(113), FZ(40), Y(386), Y(368), "lens", AMBER, depth=FRONT, facing=0.1),
        # Rubber lip on the nose along the bumper top edge (geometry.json 05 front).
        strip("front", "bumper-lip-front", 0.0, FZ(45), bf_top - 0.012, bf_top, "rubber", RUBBER, depth=FRONT, facing=0.1),
    ]
    if fog:
        decals.append(box("front", "fog-front", fog[0], fog[1], fog[2], fog[3], "lens", "#eef1e6", depth=FRONT, facing=0.25))
    if plate_front:
        decals.append(box("front", "plate-front", -0.1, 0.26, bf_bot + 0.005, bf_bot + 0.115, "satin", "#e9e9e6", depth=FRONT, facing=0.3))

    # Rear view: lamp units on the bumper top (x 887–985 → z 0.705–0.419), inboard→outboard
    # red / clear / amber (photo 20-rear, RoW); red reflector band with PORSCHE lettering
    # between them (y 973–1003); rubber rubbing strip; overriders flanking the plate.
    lamp_y0, lamp_y1 = RY(1000), RY(970)
    band_y0, band_y1 = RY(1003), RY(973)
    z_in, z_out = RZ(985), RZ(887)
    decals += [
        box("rear", "taillight", z_in, z_in + 0.112, lamp_y0, lamp_y1, "lens", RED, depth=REAR, facing=0.25),
        box("rear", "reverse-light", z_in + 0.112, z_in + 0.176, lamp_y0, lamp_y1, "lens", CLEAR, depth=REAR, facing=0.25),
        box("rear", "indicator-rear", z_in + 0.176, z_out, lamp_y0, lamp_y1, "lens", AMBER, depth=REAR, facing=0.25),
        box("rear", "reflector-band", -0.1, z_in, band_y0, band_y1, "lens", BAND_RED, depth=REAR, facing=0.25),
        # PORSCHE lettering (black) x 1022–1233, y 984–1000.
        box("rear", "badge-rear", -0.1, RZ(1022), RY(1000), RY(984), "satin", "#1a1a1a", depth=REAR, facing=0.25, stripes=[0.025, 0.4]),
        strip("rear", "bumper-strip-rear", RZ(1022), z_out, Y(STRIP_R[1]), Y(STRIP_R[0]), "rubber", RUBBER, depth=REAR, facing=0.3),
        box("rear", "plate-rear", -0.1, 0.26, 0.37, 0.48, "satin", "#e9e9e6", depth=REAR, facing=0.3),
    ]
    if guard:
        # Rubber overriders flanking the plate (rear view x 988–1022 → z 0.41–0.31; photo
        # 20-rear and the studio profile show them on RoW cars), bumper top to below it.
        decals.append(box("rear", "guard-rear", RZ(1022), RZ(988), 0.30, Y(BUMPER_R_TOP) + 0.005, "rubber", RUBBER, depth=REAR, facing=0.3))
    if rear_script:
        decals.append(rear_script)

    # Top view.
    screen_top = [[X(COWL_PX + 3), -0.1], [X(COWL_PX + 3), 0.605], [X(SCREEN_TOP_PX - 6), 0.54], [X(SCREEN_TOP_PX - 2), -0.1]]
    rear_top = [[X(985), -0.1], [X(985), 0.42], [X(1195), REAR_WINDOW_Z], [X(1197), -0.1]]
    gz = grille_z if grille_z is not None else RZ(983)
    decals += [
        {"id": "windscreen", "plane": "top", "kind": "fill", "points": even(screen_top, True, 0.15), "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
        {"id": "rear-window", "plane": "top", "kind": "fill", "points": even(rear_top, True, 0.15), "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.9, 2]},
        # Black slatted engine-lid grille (side view x 1205–1283; rear view half-width x 983).
        box("top", "engine-grille", X(1205), X(1283), -0.1, gz, "satin", "#1f2022", stripes=[0.02, 0.5], facing=0.3, depth=[0.8, 2], spacing=0.1),
        # Slatted cowl grille ahead of the windscreen (geometry.json 05 front.other).
        box("top", "cowl-grille", X(478), X(492), -0.1, 0.28, "satin", "#2b2b2b", facing=0.3, depth=[0.8, 2]),
        # Crest on the lid nose (front view y 945–962 ↔ lid height 0.63–0.68 m → x 0.24–0.27).
        box("top", "crest", 0.24, 0.27, 0.0, 0.022, "chrome", "#c9a24e", facing=0.3, depth=[0.5, 2]),
        # Filler flap on the left front wing: studio photo X 1.17–1.34 (centre 1.26), dd930
        # plan 0.16 × 0.09 m oval near the wing top.
        {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left", "points": ellipse(1.26, 0.645, 0.08, 0.045),
         "finish": "satin", "color": GAP, "facing": 0.3, "depth": [0.7, 2]},
        {"id": "hood-gap", "plane": "top", "kind": "line", "points": even([[0.15, 0.0], [0.155, HOOD_EDGE_Z_NOSE], [X(COWL_PX - 17), HOOD_EDGE_Z_COWL]], False, 0.2),
         "finish": "satin", "color": GAP, "facing": 0.3},
        {"id": "lid-gap", "plane": "top", "kind": "line", "points": even([[X(1195), 0.0], [X(1195), LID_EDGE_Z_TOP], [X(1382), LID_EDGE_Z], [X(1384), 0.0]], False, 0.15),
         "finish": "satin", "color": GAP, "facing": 0.3, "depth": [0.6, 2]},
    ]
    decals += list(extra)
    for d in decals:
        d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]
    return decals


def headlight(ring_color, ring_finish):
    r = LAMP_LENS_D / 2
    # Side view: lamp glass face from (130, 268) to (117, 340) → centre (123, 304), leaning
    # back 10° (atan 13/72).
    return {
        "centre": [X(123), Y(304), LAMP_Z],
        "outline": [[round(float(np.cos(a)) * r, 4), round(float(np.sin(a)) * r, 4)] for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)],
        "yaw": 3,
        "pitch": 10,
        "ring": round((LAMP_RING_D - LAMP_LENS_D) / 2, 4),
        "ringColor": ring_color,
        "ringFinish": ring_finish,
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    }


# Door mirror (front view: head x 565–610 / y 850–875, stalk base x 556 / y 880; side view
# head x 572–592): inner edge z 0.772, 0.133 wide, 0.077 tall, 0.06 long, centre y ≈ 0.91.
MIRROR_AT = [X(582), 0.91, FZ(565)]
MIRROR_SIZE = [0.06, 0.08, 0.133]
# Single tailpipe on the car's left (geometry.json 05): side view pipe end (1368, 435),
# rear view circle centre x 940, r ≈ 10 px.
EXHAUST = [X(EXHAUST_SIDE[0]), Y(EXHAUST_SIDE[1]), -RZ(940), 0.029]


def ref_end_view(stop, name, crop, lat_s, vert_s, centre_x, ground_y, path=SHEET, half_width=0.805):
    """Save an isotropically rescaled copy of an end view (vertical scale matched to the
    lateral one) for check_car.py; returns the calib entry."""
    g = cv2.imread(path) if not path.lower().endswith(".gif") else cv2.cvtColor(
        np.array(__import__("PIL.Image", fromlist=["Image"]).open(path).convert("RGB")), cv2.COLOR_RGB2BGR)
    x0, y0, x1, y1 = crop
    sub = g[y0:y1, x0:x1]
    k = vert_s / lat_s
    sub = cv2.resize(sub, (sub.shape[1], int(round(sub.shape[0] * k))), interpolation=cv2.INTER_LINEAR)
    out_dir = os.path.join(ROOT, "research", "traces", stop)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"ref-{name}.png")
    cv2.imwrite(dst, sub)
    return {"image": os.path.relpath(dst, ROOT), "centreX": centre_x - x0, "groundY": (ground_y - y0) * k,
            "left": centre_x - x0 - half_width / lat_s, "right": centre_x - x0 + half_width / lat_s, "width": 2 * half_width}


def ref_side_view(stop):
    """Copy of the side view with the region behind the rear arch compressed by K_REAR (the
    correction applied to the trace), so check-side.png compares like with like."""
    g = cv2.imread(SHEET)
    a = int(ARCH_R_PX)
    left, right = g[:, :a], g[:, a:1460]
    right = cv2.resize(right, (int(round(right.shape[1] * K_REAR)), right.shape[0]), interpolation=cv2.INTER_AREA)
    out = np.concatenate([left, right], axis=1)
    out_dir = os.path.join(ROOT, "research", "traces", stop)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "ref-side.png")
    cv2.imwrite(path, out)
    return os.path.relpath(path, ROOT)


def compress_rear(path, stop, name, arch_px, tail_px, k, vscale=1.0):
    """Copy of a side-view sheet for the check overlays: optional vertical rescale (sheets
    scanned with a non-square aspect) and the region behind the rear arch compressed by k
    (the G-series factory drawing and the drawings derived from it show the rear overhang
    ~4–5 % longer than the printed 42.8 in). Returns the relative path."""
    g = cv2.imread(path)
    if vscale != 1.0:
        g = cv2.resize(g, (g.shape[1], int(round(g.shape[0] * vscale))), interpolation=cv2.INTER_CUBIC)
    a = int(arch_px)
    left, right = g[:, :a], g[:, a:int(tail_px) + 20]
    right = cv2.resize(right, (int(round(right.shape[1] * k)), right.shape[0]), interpolation=cv2.INTER_AREA)
    out = np.concatenate([left, right], axis=1)
    out_dir = os.path.join(ROOT, "research", "traces", stop)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"ref-{name}.png")
    cv2.imwrite(dst, out)
    return os.path.relpath(dst, ROOT)


def write_outputs(stop, car, calib):
    out = os.path.join(ROOT, "src", "data", "cars", f"{stop}.json")
    with open(out, "w") as f:
        json.dump(car, f, indent=1)
    with open(os.path.join(ROOT, "research", "traces", f"{stop}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    print("wrote", os.path.relpath(out, ROOT), "length", car["length"], "axles", car["frontAxle"], car["rearAxle"])


# ------------------------------------------------------------------ 05 car
def main():
    side_z = plan_half_width(0.805, 0.805)   # 1610 mm at both axles (narrow body)
    body = gseries_body(side_z)
    decals = gseries_decals(trim="chrome", trim_color=CHROME, handle=("chrome", CHROME), grille_z=RZ(983),
                            # '911' script centred on the lid below the grille (photos 20-rear,
                            # 25-rear-34-right; rear view mark at y 922 → 0.75 m).
                            rear_script=lid_badge(body, 0.745, 0.765, 0.06, "chrome", CHROME))
    # Tyre 165 HR 15 (specs.json 05, base 911 on 5.5J x 15 steel). No 1974–77 side photo shows
    # this tyre (all show 185/70 on alloys), so the diameter measured for the same tyre on the
    # 1964–68 car's photos is used: 0.265 × 2211 mm ≈ 0.59–0.60 m (02 trace, TRACING.md).
    tyre_d = 0.60
    wheel = {"diameter": tyre_d, "width": 0.165, "rim": 0.381, "design": "steel-hubcap", "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None}
    car = {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.360,
        "trackRear": 1.342,
        "body": body,
        "decals": decals,
        "wheels": {"front": dict(wheel), "rear": dict(wheel)},
        "headlight": headlight("#e3e6e9", "chrome"),
        # geometry.json 05: chrome door mirror on the driver's door only.
        "mirror": {"at": MIRROR_AT, "size": MIRROR_SIZE, "shape": "flag", "color": CHROME, "finish": "chrome", "sides": "left"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        "exhausts": [EXHAUST],
    }
    wheel_y = GROUND_Y - tyre_d / 2 / S
    calib = {
        # Side sheet with the rear-overhang correction applied (ref-side.png, see K_REAR).
        "side": {"image": ref_side_view(STOP), "wheelF": [FA_PX, wheel_y], "wheelR": [RA_PX, wheel_y],
                 "tipF": FA_PX - FA / S, "crop": [0, 50, 1445, 560]},
        # Studio profile: hub centres from circle fits of the rims (79.6 / 74.2 px):
        # (564.5, 597.5) / (1425.5, 595.5); the car wears 185/70 VR 15 (r 0.32 m), so the
        # hub height is shifted to the 0.30 m axle of the traced car.
        "side_photo": {"image": os.path.relpath(PHOTO_SIDE, ROOT), "wheelF": [564.5, 597.5 + 0.02 / 0.0026377],
                       "wheelR": [1425.5, 595.5 + 0.02 / 0.0026377], "tipF": 564.5 - FA / 0.0026377, "crop": [200, 200, 1820, 760]},
        # Plan: no 1974–77 plan view exists; the SC vendor plan (same shell, rear wings
        # +21 mm/side, drawn ≈2 % wider than the official widths) is the overlay reference.
        "top": {"image": "research/blueprints/07-911-sc-1978/vec-30946_porsche-911sc_4view-dims-watermarked.jpg",
                "tipF": 84, "tipR": 806, "centreY": 629.0, "crop": [60, 440, 850, 810]},
        # End views: isotropic copies (vertical scale matched to the lateral one).
        "front": ref_end_view(STOP, "front", (0, 690, 640, 1250), F_S, F_VS, F_CX, F_GY),
        "rear": ref_end_view(STOP, "rear", (800, 690, 1460, 1250), R_S, R_VS, R_CX, R_GY),
    }
    write_outputs(STOP, car, calib)


def centre_plane_photo_check(stop, spec, hubs, tips_px, principal, name="side-photo-centre"):
    """Extra overlay of a side photo for centre-line features (roof, tips). A hub-calibrated
    overlay projects centre-line features a few % too large: the hubs are ~0.7 m nearer the
    camera than the centre plane. The ratio r of the two scales follows from the bumper tips
    (official length); the hubs are then projected onto the centre plane about the
    principal point (image centre). Arches / wheels do NOT line up in this overlay."""
    sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
    import check_car  # noqa: E402
    car, _ = check_car.load(stop)
    (fx, fy), (rx, ry) = hubs
    hub_scale = WB / (rx - fx)
    k = (tips_px[1] - tips_px[0]) * hub_scale / L      # centre-plane px per hub-plane px
    px, py = principal
    f2 = (px + (fx - px) * k, py + (fy - py) * k)
    r2 = (px + (rx - px) * k, py + (ry - py) * k)
    s2 = dict(spec, wheelF=list(f2), wheelR=list(r2), tipF=f2[0] - FA / (hub_scale / k))
    check_car.side_view(car, s2, stop, name)
    return k


if __name__ == "__main__":
    main()
    subprocess.run([sys.executable, os.path.join(ROOT, "research", "tools", "check_car.py"), STOP], check=True)
    # Studio photo: bumper tips (rubber nose x 237, rear guard x 1778) → k = 0.947 (camera
    # ≈ 12 m from the near hubs).
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json")) as f:
        sp = json.load(f)["side_photo"]
    ratio = centre_plane_photo_check(STOP, sp, ((564.5, 597.5 + 0.02 / 0.0026377), (1425.5, 595.5 + 0.02 / 0.0026377)),
                                     (237, 1778), (960, 507))
    print("centre-plane scale ratio", round(ratio, 4))
