"""Trace: 02-911-swb-1964 — 911 2.0 Coupé, short wheelbase (1964–1968).

Primary reference: factory body drawing of the 1967 911 (side, plan, front,
rear and B-pillar section views with printed dimensions), the-blueprints.com
preview "porsche-911-1967" (research/blueprints/02-911-swb-1964/).
Official dimensions: research/specs.json → L 4163, W 1610, H 1320, WB 2211,
tracks 1337/1317 mm, tyres 165 HR 15.

Calibration (side + plan views share one scale):
  front tip x = 1693 px, rear tip x = 3387 px (1694 px ↔ 4163 mm)
  front axle x = 2066 px ("Plan 0" vertical), rear axle x = 2966 px
  (900 px ↔ 2211 mm → 2.4567 mm/px; both arch centres agree)
  roof peak y = 107 px; with the official 1320 mm height the ground is y = 644.3 px.
  Printed dimensions check: 830 → 848, 572 → 575, 753 → 759, 1413 → 1422 mm (<2.5 %).
  Plan view max width 648 px → 1592 mm (drawing label: 1595).
End views (front/rear/B-pillar section) are used for horizontal positions only:
their vertical scale is foreshortened on this sheet.

Run: research/tools/venv python research/traces/02-911-swb-1964.py
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import column_profile, silhouette_from_drawing, simplify  # noqa: E402

STOP = "02-911-swb-1964"
SHEET = os.environ.get("SHEET", os.path.join(ROOT, "research", "blueprints", STOP, "tbp-40868_porsche-911-1967_factory-body-4view-mm.png"))

S = 2.4567 / 1000  # metres per pixel
TIP_X, TAIL_X = 1693, 3387
GROUND_Y = 644.3
FRONT_AXLE_X, REAR_AXLE_X = 2066, 2966
PLAN_CENTRE_ROW = None  # per-column centre is used (the scan is tilted ~4 px)


def X(px):
    return round((px - TIP_X) * S, 4)


def Y(py):
    return round((GROUND_Y - py) * S, 4)


def curve(points):
    return [[X(px), Y(py)] for px, py in points]


# ------------------------------------------------------------------ side view
gray = cv2.imread(SHEET, cv2.IMREAD_GRAYSCALE)
side = silhouette_from_drawing(gray, (1680, 90, 3400, 545), close=3, thresh=150)
side = cv2.morphologyEx(side, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
prof = column_profile(side)


def clean(values, window=9, tol=10):
    """Replace spikes (dimension lines leaking into the fill) with the local median."""
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
# Dimension/leader lines that touch the roofline: bridge them linearly.
for a, b in ((2036, 2080), (2160, 2186), (2368, 2388), (3004, 3022)):
    ya, yb = top_px[a], top_px[b]
    for x in range(a, b + 1):
        top_px[x] = ya + (yb - ya) * (x - a) / (b - a)

# Lower edge, read by hand from the zoomed side view (arches are crossed by
# dimension lines, so the automatic fill is unreliable there).
BOTTOM = [(1693, 460), (1705, 479), (1717, 490), (1741, 501), (1765, 518), (1789, 525), (1837, 523),
          (1897, 521), (1914, 514), (1924, 505), (1932, 480), (1945, 440), (1965, 405), (1990, 380),
          (2020, 360), (2060, 351), (2100, 353), (2140, 370), (2170, 400), (2190, 440), (2205, 490),
          (2215, 520), (2232, 530), (2300, 530), (2790, 530), (2800, 527), (2809, 520), (2821, 479),
          (2833, 444), (2845, 422), (2857, 405), (2869, 394), (2881, 386), (2905, 378), (2929, 374),
          (2953, 373), (2980, 375), (3013, 379), (3037, 388), (3061, 403), (3073, 416), (3085, 434),
          (3097, 460), (3109, 493), (3121, 509), (3133, 517), (3169, 520), (3229, 517), (3289, 515),
          (3337, 512), (3349, 503), (3361, 502), (3373, 496), (3383, 478), (3387, 460)]
bot_px = dict(BOTTOM)

# Silhouette top in car space. Ahead of the windscreen this is the fender crest.
silhouette_top = [[X(x), Y(v)] for x, v in sorted(top_px.items()) if x % 4 == 0]
silhouette_bot = [[X(x), Y(v)] for x, v in sorted(bot_px.items())]

# ------------------------------------------------------------------ plan view
plan = silhouette_from_drawing(gray, (1660, 670, 3420, 1340), close=3, thresh=150)
plan = cv2.morphologyEx(plan, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
pprof = column_profile(plan)
half_width = [[X(x), round((b - t) / 2 * S, 4)] for x, (t, b) in sorted(pprof.items()) if x % 4 == 0]

# ------------------------------------------------------------------ hand-read lines (px)
# Hood centre line (dashed hidden line behind the fender, side view).
HOOD = [(1693, 446), (1705, 425), (1718, 408), (1750, 392), (1800, 370), (1850, 350), (1900, 332),
        (1950, 318), (2000, 306), (2050, 298), (2100, 292), (2150, 287), (2200, 283), (2255, 279)]
# Windscreen centre (side view A-pillar outer line from cowl to roof front).
SCREEN = [(2262, 262), (2300, 234), (2350, 198), (2400, 162), (2440, 133), (2470, 114)]
# Side glass (DLO) inner outline, starting lowest-front, clockwise in side view.
DLO_DOOR = [(2342, 265), (2400, 207), (2452, 160), (2478, 148), (2520, 143), (2600, 142), (2700, 146),
            (2790, 158), (2750, 270), (2600, 269), (2450, 267)]
DLO_QUARTER = [(2758, 270), (2796, 159), (2880, 175), (2950, 206), (2988, 236), (2996, 254),
               (2982, 264), (2900, 268)]
# Belt (glass sill) and roof rail (glass top + drip rail) across the cabin.
BELT_CABIN = [(2342, 265), (2450, 267), (2600, 269), (2750, 270), (2900, 268), (2990, 263)]
RAIL_CABIN = [(2478, 146), (2520, 140), (2600, 139), (2700, 143), (2790, 154), (2880, 172),
              (2950, 202), (2990, 232)]
# Door shut lines (front edge vertical at the A-pillar, rear edge slanted with the B-pillar).
DOOR = [(2296, 283), (2296, 515), (2730, 515), (2752, 300), (2750, 270)]
# Front bumper blade (side view) and its indicator housing.
BUMPER_F = [(1693, 446), (1700, 438), (1925, 438), (1925, 478), (1700, 478), (1693, 468)]
BUMPER_R = [(3160, 438), (3380, 438), (3387, 452), (3380, 478), (3160, 478)]
INDICATOR_F = [(1745, 432), (1760, 400), (1850, 400), (1868, 432)]

# ------------------------------------------------------------------ end views (horizontal only)
# Front view: centre x 371, 2.446 mm/px (1595 label). Rear view: centre 1180, 2.39 mm/px (1016 label).
# B-pillar section: centre 1179, 2.44 mm/px (1300/1076/1578 labels).
# Headlamps: official Porsche 1963 front elevation (true projection, ground line drawn):
# centres 170 px from the centre line at 3.61 mm/px → 0.614 m; chrome ring 66 px → 0.238 m;
# centre 186 px above ground → 0.671 m on the 901, which sat 45 mm lower than the 911.
LAMP_Z = 0.614
LAMP_RING_D = 0.238
LAMP_Y = 0.671 + 0.045
FENDER_CREST_Z_FRONT = 0.56
FENDER_CREST_Z_COWL = 0.64
HOOD_EDGE_Z_NOSE = 0.314   # plan view: front lid side edge at the nose
HOOD_EDGE_Z_COWL = 0.548   # plan view: front lid side edge at the windscreen
CABIN_BELT_Z = 0.646       # section: glass base (1300 wide at the door top)
CABIN_RAIL_Z = 0.538       # section: roof rail (1076 label)
REAR_WINDOW_Z = 0.495      # rear view: rear window half-width (1016 label)
HIP_CREST_Z = 0.657        # rear view: rear fender shoulder
LID_EDGE_Z = 0.44          # rear view: engine lid side edge

L = X(TAIL_X)
FA, RA = X(FRONT_AXLE_X), X(REAR_AXLE_X)


def lerp_keys(pairs):
    return [[round(a, 4), round(b, 4)] for a, b in pairs]


hood = curve(HOOD)
screen = curve(SCREEN)
roof_top = [p for p in silhouette_top if X(2470) <= p[0]]
top_y = hood + screen[1:] + [p for p in roof_top if p[0] > screen[-1][0]]

# Fender crest = side silhouette ahead of the cowl, door shoulder in the cabin,
# rear hip crest behind (a little below the fastback silhouette).
crest = [p for p in silhouette_top if X(1850) <= p[0] <= X(2255)]
crest = [[0.0, Y(446)], [X(1745), Y(410)], [X(1812), Y(392)], [X(1840), Y(318)]] + crest
crest += curve([(2300, 272), (2500, 274), (2750, 276), (2950, 272), (3050, 262), (3150, 272),
                (3250, 318), (3330, 364), (3387, 446)])

belt = [[0.0, Y(446)]] + [[x, round(y - 0.03, 4)] for x, y in hood[2:]]
belt += curve(BELT_CABIN)
belt += curve([(3050, 252), (3110, 247), (3200, 290), (3300, 345), (3387, 446)])

rail = [[0.0, Y(446)]] + [[x, round(y - 0.004, 4)] for x, y in hood[2:]]
rail += screen[1:-1] + curve(RAIL_CABIN)
rail += curve([(3040, 228), (3110, 244), (3200, 288), (3300, 342), (3387, 446)])

side_y = lerp_keys([(0, Y(452)), (X(1760), Y(430)), (FA, 0.56), (X(2300), 0.54), (X(2750), 0.535),
                    (RA, 0.54), (X(3300), Y(470)), (L, Y(452))])

floor_y = lerp_keys([(0, Y(470)), (X(1750), Y(512)), (X(1900), 0.25), (FA, 0.2), (X(2300), 0.181),
                     (X(2800), 0.181), (RA, 0.21), (X(3200), 0.28), (L, Y(478))])

# z curves
sz = half_width
rocker_z = [[x, round(max(0.0, z - (0.012 if (abs(x - FA) < 0.33 or abs(x - RA) < 0.36) else 0.04)), 4)] for x, z in sz]
crest_z = lerp_keys([(0, 0), (X(1712), 0.34), (X(1812), FENDER_CREST_Z_FRONT - 0.03), (X(1850), FENDER_CREST_Z_FRONT),
                     (X(2255), FENDER_CREST_Z_COWL), (X(2342), 0.70), (X(2750), 0.71), (X(2990), 0.69),
                     (X(3100), HIP_CREST_Z), (X(3300), 0.6), (L - 0.03, 0.4), (L, 0)])
belt_z = lerp_keys([(0, 0), (X(1718), HOOD_EDGE_Z_NOSE), (X(2255), HOOD_EDGE_Z_COWL), (X(2342), CABIN_BELT_Z),
                    (X(2990), CABIN_BELT_Z - 0.01), (X(3100), LID_EDGE_Z + 0.03), (X(3300), LID_EDGE_Z),
                    (L - 0.03, 0.3), (L, 0)])
roof_z = lerp_keys([(0, 0), (X(1718), 0.16), (X(2255), 0.3), (X(2300), 0.44), (X(2470), CABIN_RAIL_Z),
                    (X(2857), CABIN_RAIL_Z - 0.01), (X(2990), REAR_WINDOW_Z), (X(3110), REAR_WINDOW_Z - 0.02),
                    (X(3300), 0.26), (L, 0)])

body = {
    "floorY": floor_y,
    "rockerY": silhouette_bot,
    "rockerZ": simplify(rocker_z, 0.003),
    "sideY": side_y,
    "sideZ": simplify(sz, 0.002),
    "crestY": simplify(sorted(crest), 0.003),
    "crestZ": crest_z,
    "beltY": simplify(sorted(belt), 0.003),
    "beltZ": belt_z,
    "roofY": simplify(sorted(rail), 0.003),
    "roofZ": roof_z,
    "topY": simplify(sorted(top_y), 0.003),
}

# The section must close to a line at both tips.
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

# Deduplicate x keys (monotone cubic needs strictly increasing x).
for k, c in body.items():
    out = []
    for x, v in c:
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([x, v])
    body[k] = out


def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": curve(pts), "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, **kw):
    """Axis-aligned rectangle decal: (a, b) = (x, y) side, (x, z) top, (z, y) front/rear."""
    pts = [[a0, b0], [a0, b1], [a1, b1], [a1, b0]]
    d = {"id": id_, "plane": plane, "kind": "fill", "points": pts, "finish": finish, "color": color}
    d.update(kw)
    return d


CHROME = "#dfe2e5"
RUBBER = "#1c1c1c"
GLASS = "#1d2329"
GOLD = "#c9a24e"
FRONT = [-0.05, 0.45]          # x range where front decals apply
REAR = [L - 0.45, L + 0.05]

# geometry.json 02: bumpers are body-colour steel with a full-width chrome strip and a
# black rubber insert, plus two vertical chrome guards; the side view gives the band
# 0.408–0.508 m (factory drawing y 478–438 px).
BUMPER_TOP, BUMPER_BOT = Y(438), Y(478)
STRIP_TOP, STRIP_BOT = Y(452), Y(462)

decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    # Chrome window frames (geometry.json: chrome-framed door glass, chrome quarter frame).
    side_decal("window-trim", DLO_DOOR[:7] + [(2790, 158)] + DLO_QUARTER[2:6], "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    # Pivoting front vent window: its rear frame is the slanted bar behind the A-pillar.
    side_decal("vent-divider", [(2415, 266), (2452, 162)], "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", RAIL_CABIN + [(3040, 228)], "chrome", CHROME, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.55, 2]),
    side_decal("door-handle", [(2690, 300), (2745, 300), (2745, 309), (2690, 309)], "chrome", CHROME, depth=[0.6, 2]),
    side_decal("rocker-trim", [(2240, 505), (2800, 505), (2800, 520), (2240, 520)], "chrome", CHROME, depth=[0.6, 2]),
    # Bumper ends seen from the side: chrome strip on the body-colour bumper.
    side_decal("bumper-strip-front", [(1693, 452), (1925, 452), (1925, 462), (1693, 462)], "chrome", CHROME, depth=[0.0, 2], facing=0.2),
    side_decal("bumper-strip-rear", [(3160, 452), (3387, 452), (3387, 462), (3160, 462)], "chrome", CHROME, depth=[0.0, 2], facing=0.2),
    # Lamp unit wrapping round the wing corner (amber indicator), visible from the side.
    side_decal("indicator-side", [(1745, 432), (1760, 404), (1840, 404), (1850, 432)], "lens", "#e59a35", depth=[0.5, 2], facing=0.25),
    # Tail lamp housings sit on the bumper and wrap round the rear corners.
    side_decal("taillight-side", [(3290, 437), (3290, 412), (3370, 420), (3380, 437)], "lens", "#e59a35", depth=[0.5, 2], facing=0.25),
]

# Front view (official 1963 elevation for lateral positions; +45 mm ride height for
# the production 911 per geometry.json 02 "ground clearance +32, height +47").
decals += [
    box("front", "bumper-strip-front", 0.0, 0.8, STRIP_BOT, STRIP_TOP, "chrome", CHROME, depth=FRONT, facing=0.3),
    box("front", "bumper-insert-front", 0.0, 0.8, STRIP_BOT + 0.003, STRIP_TOP - 0.003, "rubber", RUBBER, depth=FRONT, facing=0.3),
    box("front", "guard-front", 0.316, 0.392, 0.38, 0.56, "chrome", CHROME, depth=FRONT, facing=0.3),
    box("front", "horn-grille", 0.392, 0.572, 0.505, 0.575, "chrome", CHROME, depth=FRONT, facing=0.3, stripes=[0.012, 0.45]),
    box("front", "indicator-front", 0.572, 0.66, 0.505, 0.575, "lens", "#e59a35", depth=FRONT, facing=0.25),
    box("front", "parking-front", 0.66, 0.753, 0.505, 0.575, "lens", "#eef1f2", depth=FRONT, facing=0.25),
    box("front", "fog-front", 0.19, 0.3, 0.33, 0.37, "lens", "#e8d9a0", depth=FRONT, facing=0.3),
    box("front", "plate-front", 0.0, 0.26, 0.37, 0.41, "satin", "#e9e9e6", depth=FRONT, facing=0.3),
]

# Rear view: lamp units on the bumper top, inboard→outboard red / clear / amber
# (geometry.json 02, European version); z from the factory rear view (1016 label).
decals += [
    box("rear", "taillight", 0.43, 0.56, BUMPER_TOP, BUMPER_TOP + 0.065, "lens", "#b8231d", depth=REAR, facing=0.25),
    box("rear", "reverse-light", 0.56, 0.61, BUMPER_TOP, BUMPER_TOP + 0.065, "lens", "#eef1f2", depth=REAR, facing=0.25),
    box("rear", "indicator-rear", 0.61, 0.686, BUMPER_TOP, BUMPER_TOP + 0.065, "lens", "#e59a35", depth=REAR, facing=0.25),
    box("rear", "bumper-strip-rear", 0.0, 0.8, STRIP_BOT, STRIP_TOP, "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", "bumper-insert-rear", 0.0, 0.8, STRIP_BOT + 0.003, STRIP_TOP - 0.003, "rubber", RUBBER, depth=REAR, facing=0.3),
    box("rear", "guard-rear", 0.36, 0.43, 0.33, 0.56, "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", "plate-rear", 0.0, 0.25, 0.38, 0.46, "satin", "#e9e9e6", depth=REAR, facing=0.3),
    box("rear", "badge-rear", 0.0, 0.13, 0.735, 0.748, "chrome", GOLD, depth=REAR, facing=0.2),
]

screen_top = [[X(2262), 0.0], [X(2262), 0.60], [X(2470), 0.5], [X(2478), 0.0]]
rear_top = [[X(2862), 0.0], [X(2862), 0.47], [X(3100), 0.46], [X(3105), 0.0]]
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rear_top, "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.9, 2]},
    # geometry.json 02: wide chrome grille of horizontal bars at the top of the engine lid.
    box("top", "engine-grille", X(3150), X(3232), 0.0, 0.3, "chrome", CHROME, stripes=[0.018, 0.5], facing=0.3, depth=[0.8, 2]),
    # Fresh-air slot at the rear edge of the front lid, ahead of the windscreen.
    box("top", "cowl-grille", X(2215), X(2250), 0.0, 0.2, "satin", "#2b2b2b", stripes=[0.012, 0.5], facing=0.3, depth=[0.8, 2]),
    # Gold crest on the lid nose.
    box("top", "crest", X(1735), X(1752), 0.0, 0.022, "chrome", GOLD, facing=0.3, depth=[0.5, 2]),
    # Round filler flap on top of the left front wing (released from inside).
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left",
     "points": [[X(2150) + 0.045 * np.cos(a), 0.62 + 0.045 * np.sin(a)] for a in np.linspace(0, 2 * np.pi, 13)],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3, "depth": [0.7, 2]},
    {"id": "hood-gap", "plane": "top", "kind": "line", "points": [[X(1725), 0.0], [X(1735), HOOD_EDGE_Z_NOSE], [X(2250), HOOD_EDGE_Z_COWL]], "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
    {"id": "lid-gap", "plane": "top", "kind": "line", "points": [[X(3110), 0.0], [X(3110), LID_EDGE_Z + 0.02], [X(3370), LID_EDGE_Z - 0.02], [X(3372), 0.0]], "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]

# Tyre 165 HR 15 (specs.json). Its overall diameter is measured, not assumed: in two
# independent side photos (photos/02…/01-side-left.jpg, 09-side-left.jpg) the tyre is
# 0.265–0.2675 × the wheelbase → ≈ 0.59 m; hub-to-floor (loaded radius) in 01 is
# 107 px × 2.638 mm/px ≈ 0.28 m. The arch top there sits ≈ 0.71 m above the floor,
# matching the drawing-based body (0.713 m).
tyre_d = 0.60
car = {
    "id": STOP,
    "length": L,
    "frontAxle": FA,
    "rearAxle": RA,
    "trackFront": 1.337,
    "trackRear": 1.317,
    "body": body,
    "decals": decals,
    "wheels": {
        "front": {"diameter": round(tyre_d, 4), "width": 0.165, "rim": 0.381, "design": "steel-hubcap", "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
        "rear": {"diameter": round(tyre_d, 4), "width": 0.165, "rim": 0.381, "design": "steel-hubcap", "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
    },
    "headlight": {
        "centre": [X(1832), LAMP_Y, LAMP_Z],
        "outline": [[round(float(np.cos(a)) * (LAMP_RING_D / 2 - 0.024), 4), round(float(np.sin(a)) * (LAMP_RING_D / 2 - 0.024), 4)] for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)],
        "yaw": 3,
        "pitch": 15,
        "ring": 0.024,
        "ringColor": "#e3e6e9",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    },
    # geometry.json 02: one round chrome mirror on the front of the driver's door;
    # official front elevation: head ≈ 0.09 m, 0.79 m out, ≈ 0.84 m high (+45 mm for the 911).
    "mirror": {"at": [X(2335), 0.885, 0.76], "size": [0.05, 0.09, 0.09], "shape": "round", "color": "#dfe2e5", "finish": "chrome", "sides": "left"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    "exhausts": [[L - 0.02, Y(500), 0.3, 0.03]],
}

out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
with open(out, "w") as f:
    json.dump(car, f, indent=1)
calib = {
    "side": {"image": os.path.relpath(SHEET, ROOT), "wheelF": [FRONT_AXLE_X, GROUND_Y - tyre_d / 2 / S],
             "wheelR": [REAR_AXLE_X, GROUND_Y - tyre_d / 2 / S], "tipF": TIP_X, "crop": [1650, 60, 3420, 680]},
    "top": {"image": os.path.relpath(SHEET, ROOT), "tipF": TIP_X, "tipR": TAIL_X, "centreY": 1014, "crop": [1650, 660, 3420, 1360]},
    # Porsche studio profile of a 1965 911 2.0: hub centres read from a zoomed grid.
    "side_photo": {"image": "research/photos/02-911-swb-1964/01-side-left.jpg", "wheelF": [575, 693],
                   "wheelR": [1418, 693], "tipF": 280, "crop": [240, 280, 1820, 840]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)
print("wrote", os.path.relpath(out, ROOT), "length", L, "axles", FA, RA)
