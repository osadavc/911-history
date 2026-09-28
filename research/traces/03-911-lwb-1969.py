"""Trace: 03-911-lwb-1969 — 911 T 2.0 Coupé, B-series (MY1969), long wheelbase.

What changed from the 1964-68 car (research/history.md, geometry.json 03, specs.json 03):
  * wheelbase +57 mm, 2211 -> 2268 mm: "the rear wheels moved back on longer semi-trailing
    arms without lengthening the body"; "the wheel openings were adapted" / re-cut;
    "Wheelarches got a subtle flare design and the indicators were a bit bigger too".
  * 911 T: 165 HR 15 on 5 1/2 J x 15, tracks 1362 / 1343 mm, L 4163 / W 1610 / H 1320
    (specs.json 03 = the spec panel of this stop).
So the body shell (doors, glass, roof, lids, bumpers) is the same pressing as the 1964-68
car and is traced from the same factory body drawing as stop 02; the LWB-specific parts come
from the LWB references:

References
  SHELL  research/blueprints/02-911-swb-1964/tbp-40868_porsche-911-1967_factory-body-4view-mm.png
         (factory body drawing, side + plan, 2.4567 mm/px; same calibration as the 02 trace:
         front axle "Plan 0" x 2066, ground y 644.3). Readings marked "02" are the 02 trace's
         hand-read lines of this sheet (checked on an overlay); the nose, lid line and plan
         nose were re-read here.
  LWB    research/blueprints/03-911-lwb-1969/tbp-68304_porsche-911e-1968_autocar-top-side-dims.png
         (Autocar-type side + plan of a LWB 911, printed WB 7 ft 5.5 in; hub centres by rim-circle
         fits (268.9, 1149.6) / (905.9, 1148.1) -> 637 px = 2268 mm, 3.5604 mm/px, ground y 1230):
         rear arch centred on the moved rear hub (arch centre 907.5 vs hub 905.9), arch-to-bumper
         gap ~5 cm, double arch line (flare lip), bumper strip band, grille position.
  LWB    research/blueprints/03-911-lwb-1969/tbp-68305_porsche-911s-1970_rally-3view-colour.png
         (front/rear views, horizontal positions only - vertical scale ~6 % short).
  PHOTOS research/photos/03-911-lwb-1969/: 22 (July-1969 911 T 2.0 = this stop's car: Fuchs,
         no front guards, no fog lamps, chrome sill strip, rubber bumper strip), 01 (1973 T 2.4
         true profile: lamp extents near the wheel plane; this car sits ~7 cm low on its wheels,
         so it is not used for heights), 04 (911 E rear: lamp split, guards, reflectors,
         tailpipe on the left), 08/09/11 (1970-71 T: rear guards, rubber strips), 06 (1969 911 S).

Front tip: the 1969 T has no front bumper guards (photo 22; geometry.json 03 "omit on the
  model"), so x = 0 is the front bumper face at the centre line (factory side view strip end
  x 1712, plan row scan 1714 -> 1713); the 02 trace's tip (1693) is the guard. The rear guards
  are fitted (photos 04/08/11/23/24, geometry.json rear bumper) -> rear tip = guard tip 3387, as 02.
  -> L = 4.115 m; + the 44 mm front guard of the drawing = 4.159 (official 4163 incl. guards).

Run: <venv python> research/traces/03-911-lwb-1969.py
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
from trace_lib import column_profile, half_section, silhouette_from_drawing, simplify  # noqa: E402

STOP = "03-911-lwb-1969"
BP = os.path.join(ROOT, "research", "blueprints")
SHEET = os.path.join(BP, "02-911-swb-1964", "tbp-40868_porsche-911-1967_factory-body-4view-mm.png")
AUTOCAR = os.path.join(BP, STOP, "tbp-68304_porsche-911e-1968_autocar-top-side-dims.png")
RALLY = os.path.join(BP, STOP, "tbp-68305_porsche-911s-1970_rally-3view-colour.png")
PHOTO_SIDE = os.path.join(ROOT, "research", "photos", STOP, "01-side-right.jpg")

# ------------------------------------------------------------------ calibration (factory sheet)
S = 2.4567 / 1000                 # m/px (02: 900 px between the axle marks = 2211 mm)
TIP_X, TAIL_X = 1713, 3387        # bumper face (no front guard) / rear guard tip
GROUND_Y = 644.3                  # 02: roof peak y 107 + official 1320 mm
FRONT_AXLE_X = 2066               # "Plan 0" vertical
WB = 2.268                        # Porsche press release S18_3621 (MY1969 B-series)
SWB_REAR_AXLE_X = 2966
REAR_AXLE_X = FRONT_AXLE_X + WB / S          # 2989.2 px
SHIFT = REAR_AXLE_X - SWB_REAR_AXLE_X        # 23.2 px = 57 mm: the rear wheel opening moves with it


def X(px):
    return round((px - TIP_X) * S, 4)


def Y(py):
    return round((GROUND_Y - py) * S, 4)


def curve(points):
    return [[X(px), Y(py)] for px, py in points]


L = X(TAIL_X)
FA, RA = X(FRONT_AXLE_X), round(X(FRONT_AXLE_X) + WB, 4)

# ------------------------------------------------------------------ side silhouette (top), as 02
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

# ------------------------------------------------------------------ lower edge (rocker line)
# 02's hand-read lower edge with (a) the guard-less nose re-read (column scans x 1712-1740:
# bumper face 1712-1716, apron 1741+), (b) the rear wheel opening moved back by SHIFT
# (Autocar LWB side: rear arch centred on the moved hub; its rear foot ends ~5 cm ahead of
# the bumper, here 3144 vs bumper 3160 px = 3.9 cm), (c) the sill run extended to it.
NOSE_BOT = [(1713, 458), (1714, 470), (1716, 480), (1722, 490)]
FRONT_BOT = [(1741, 501), (1765, 518), (1789, 525), (1837, 523), (1897, 521), (1914, 514), (1924, 505),
             (1932, 480), (1945, 440), (1965, 405), (1990, 380), (2020, 360), (2060, 351), (2100, 353),
             (2140, 370), (2170, 400), (2190, 440), (2205, 490), (2215, 520), (2232, 530), (2300, 530)]
SWB_REAR_ARCH = [(2800, 527), (2809, 520), (2821, 479), (2833, 444), (2845, 422), (2857, 405), (2869, 394),
                 (2881, 386), (2905, 378), (2929, 374), (2953, 373), (2980, 375), (3013, 379), (3037, 388),
                 (3061, 403), (3073, 416), (3085, 434), (3097, 460), (3109, 493), (3121, 509), (3133, 517)]
REAR_ARCH = [(x + SHIFT, y) for x, y in SWB_REAR_ARCH]
TAIL_BOT = [(3169, 520), (3229, 517), (3289, 515), (3337, 512), (3349, 503), (3361, 502), (3373, 496),
            (3383, 478), (3387, 460)]
BOTTOM = NOSE_BOT + FRONT_BOT + [(2790 + SHIFT, 530)] + REAR_ARCH + TAIL_BOT
silhouette_bot = curve(BOTTOM)

# ------------------------------------------------------------------ plan (factory sheet)
plan = silhouette_from_drawing(gray, (1660, 670, 3420, 1340), close=3, thresh=150)
plan = cv2.morphologyEx(plan, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
pprof = column_profile(plan)
half_width = [[X(x), round((b - t) / 2 * S, 4)] for x, (t, b) in sorted(pprof.items())
              if 1860 <= x and x % 4 == 0]
# Nose without the guards: bumper-face outline by row scans (half-width px = 1012 - row).
NOSE_PLAN = [(1713, 0), (1714.5, 42), (1715, 62), (1716, 82), (1718, 102), (1718.5, 122),
             (1722.5, 142), (1726.5, 162), (1731.5, 182), (1737, 202), (1744.5, 222),
             (1756.5, 242), (1771.5, 262), (1794.5, 282), (1857.5, 302)]
side_z = [[X(x), round(h * S, 4)] for x, h in NOSE_PLAN] + half_width   # tail incl. rear guards (as 02)

# ------------------------------------------------------------------ centre line (topY)
# Nose re-read (column scans of the factory side view): bumper face -> bumper top corner
# (1716-1724) -> lid nose (solid line, 1728-1830) -> dashed hidden lid line (centres,
# 1850-2075) -> 02's cowl readings (2100-2255) -> windscreen (02) -> roof/fastback silhouette.
NOSE_TOP = [(1713, 458), (1714, 450), (1716, 442.5), (1720, 440), (1724, 438.5), (1728, 435), (1732, 426),
            (1736, 419), (1740, 414.5), (1744, 410), (1752, 404.5), (1760, 398.5), (1768, 393.5),
            (1776, 388.5), (1784, 384.5), (1792, 381), (1800, 377), (1808, 373.5), (1816, 369.5), (1830, 362)]
LID = [(1850, 356), (1875, 346), (1900, 337), (1925, 329.5), (1950, 323), (1975, 316), (2000, 309.5),
       (2025, 303), (2050, 298), (2075, 293)]
COWL = [(2100, 292), (2150, 287), (2200, 283), (2255, 279)]                    # 02
SCREEN = [(2262, 262), (2300, 234), (2350, 198), (2400, 162), (2440, 133), (2470, 114)]  # 02
hood = curve(NOSE_TOP + LID + COWL)
screen = curve(SCREEN)
top_y = hood + screen[1:] + [p for p in silhouette_top if p[0] > screen[-1][0]]

# ------------------------------------------------------------------ crest / belt / rail (as 02)
DLO_DOOR = [(2342, 265), (2400, 207), (2452, 160), (2478, 148), (2520, 143), (2600, 142), (2700, 146),
            (2790, 158), (2750, 270), (2600, 269), (2450, 267)]
DLO_QUARTER = [(2758, 270), (2796, 159), (2880, 175), (2950, 206), (2988, 236), (2996, 254),
               (2982, 264), (2900, 268)]
BELT_CABIN = [(2342, 265), (2450, 267), (2600, 269), (2750, 270), (2900, 268), (2990, 263)]
RAIL_CABIN = [(2478, 146), (2520, 140), (2600, 139), (2700, 143), (2790, 154), (2880, 172),
              (2950, 202), (2990, 232)]
DOOR = [(2296, 283), (2296, 515), (2730, 515), (2752, 300), (2750, 270)]

crest = [[0.0, Y(458)], [X(1716), Y(440)], [X(1745), Y(410)], [X(1812), Y(392)], [X(1840), Y(318)]]
crest += [p for p in silhouette_top if X(1850) <= p[0] <= X(2255)]
crest += curve([(2300, 272), (2500, 274), (2750, 276), (2950, 272), (3050, 262), (3150, 272),
                (3250, 318), (3330, 364), (3387, 446)])
belt = [[0.0, Y(458)], [X(1716), Y(441)]] + [[x, round(y - 0.03, 4)] for x, y in hood[7:]]
belt += curve(BELT_CABIN) + curve([(3050, 252), (3110, 247), (3200, 290), (3300, 345), (3387, 446)])
rail = [[0.0, Y(458)], [X(1716), Y(441)]] + [[x, round(y - 0.004, 4)] for x, y in hood[7:]]
rail += screen[1:-1] + curve(RAIL_CABIN)
rail += curve([(3040, 228), (3110, 244), (3200, 288), (3300, 342), (3387, 446)])


def keys(pairs):
    return [[round(a, 4), round(b, 4)] for a, b in pairs]


side_y = keys([(0, Y(458)), (X(1760), Y(430)), (FA, 0.56), (X(2300), 0.54), (X(2750), 0.535),
               (RA, 0.54), (X(3300), Y(470)), (L, Y(452))])
floor_y = keys([(0, Y(478)), (X(1750), Y(512)), (X(1900), 0.25), (FA, 0.2), (X(2300), 0.181),
                (X(2800), 0.181), (RA, 0.21), (X(3200), 0.28), (L, Y(478))])

# z of the section lines (02 readings of the factory end views / B-pillar section; the lid
# edges at the nose re-read on the plan: lid front edge 0.042 m behind the bumper face,
# corners x 0.064 / z 0.383; cowl 0.582 - see the 901 trace).
CREST_Z_FRONT, CREST_Z_COWL = 0.56, 0.64
HOOD_EDGE_Z_NOSE, HOOD_EDGE_Z_COWL, HOOD_CORNER_X, HOOD_FRONT_X = 0.383, 0.582, 0.064, 0.042
CABIN_BELT_Z, CABIN_RAIL_Z, REAR_WINDOW_Z, HIP_CREST_Z, LID_EDGE_Z = 0.646, 0.538, 0.495, 0.657, 0.44

# Flares: "subtle flare (lip)" on both openings (Autocar: double arch line ~5 cm wide; photos
# 01/22 show a rolled lip). The lip is modelled by taking the arch edge 7 mm further out than
# 02 (5 mm inside the plan width instead of 12 mm; flush would bulge the loft past the
# unchanged 1610 mm body width). Flare size is not published (geometry.json).
rocker_z = [[x, round(max(0.0, z - (0.005 if (abs(x - FA) < 0.33 or abs(x - RA) < 0.36) else 0.04)), 4)]
            for x, z in side_z]
crest_z = keys([(0, 0), (X(1716), 0.3), (X(1745), 0.4), (X(1812), CREST_Z_FRONT - 0.03), (X(1850), CREST_Z_FRONT),
                (X(2255), CREST_Z_COWL), (X(2342), 0.70), (X(2750), 0.71), (X(2990), 0.69),
                (X(3100), HIP_CREST_Z), (X(3300), 0.6), (L - 0.03, 0.4), (L, 0)])
belt_z = keys([(0, 0), (HOOD_FRONT_X, 0.3), (HOOD_CORNER_X, HOOD_EDGE_Z_NOSE), (X(2255), HOOD_EDGE_Z_COWL),
               (X(2342), CABIN_BELT_Z), (X(2990), CABIN_BELT_Z - 0.01), (X(3100), LID_EDGE_Z + 0.03),
               (X(3300), LID_EDGE_Z), (L - 0.03, 0.3), (L, 0)])
roof_z = keys([(0, 0), (HOOD_CORNER_X, 0.16), (X(2255), 0.3), (X(2300), 0.44), (X(2470), CABIN_RAIL_Z),
               (X(2857), CABIN_RAIL_Z - 0.01), (X(2990), REAR_WINDOW_Z), (X(3110), REAR_WINDOW_Z - 0.02),
               (X(3300), 0.26), (L, 0)])

body = {
    "floorY": floor_y,
    "rockerY": silhouette_bot,
    "rockerZ": simplify(rocker_z, 0.003),
    "sideY": side_y,
    "sideZ": simplify(side_z, 0.002),
    "crestY": simplify(sorted(crest), 0.003),
    "crestZ": crest_z,
    "beltY": simplify(sorted(belt), 0.003),
    "beltZ": belt_z,
    "roofY": simplify(sorted(rail), 0.003),
    "roofZ": roof_z,
    "topY": simplify(sorted(top_y), 0.003),
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
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([x, v])
    body[k] = out


def body_half_width(x, y):
    """Outer z of the lofted section at x, at height y (for rear-view proportions)."""
    sec = half_section(body, x)
    best = 0.0
    for (z0, y0), (z1, y1) in zip(sec, sec[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            best = max(best, z0 + (z1 - z0) * (y - y0) / (y1 - y0))
    return best


# ------------------------------------------------------------------ decals
# Slot ids as the 01 trace (see its .md for why bumper-front/-rear + bumper-*-face are used
# instead of 02's duplicated bumper-strip-*), plus 02's extra slots for shared parts.
def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": curve(pts), "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, **kw):
    d = {"id": id_, "plane": plane, "kind": "fill", "points": [[a0, b0], [a0, b1], [a1, b1], [a1, b0]],
         "finish": finish, "color": color}
    d.update(kw)
    return d


CHROME = "#dfe2e5"
RUBBER = "#1c1c1c"
GLASS = "#1d2329"
AMBER = "#e59a35"
GOLD = "#c9a24e"
FRONT = [-0.05, 0.45]
REAR = [L - 0.45, L + 0.05]

# Bumpers (Autocar LWB side view, rear bumper columns x 1030-1110, front x 100-160): blade top
# y 1093 (0.488 m), rubber profile strip 1100-1111 (0.423-0.463 m), bottom 1150-1155; the
# strip sits at 0.70-0.88 of the blade height (photo 01: 0.75-0.88). Black rubber profile
# with thin bright edges (geometry.json 03 "rubber profile strips"; photos 01/08/09/22).
STRIP_BOT, STRIP_TOP = 0.423, 0.463
# Front lamp wrap-round seen from the side (photo 01 amber lens, near the wheel plane): 0.45-0.62 m
# ahead of the front axle, 0.016-0.073 m above the bumper top (factory bumper top y 438 = 0.507).
IND_X0, IND_X1 = FA - 0.62, FA - 0.45
IND_Y0, IND_Y1 = Y(438) + 0.016, Y(438) + 0.073
# Rear lamp wrap-round from the side (photo 01, trapezoid): bottom 0.664-0.848 m / top
# 0.710-0.840 m behind the rear axle, 0.014-0.111 m above the bumper top (factory 0.502).
REAR_TOP = Y(440)
TAIL_SIDE = [[RA + 0.664, REAR_TOP + 0.014], [RA + 0.710, REAR_TOP + 0.111], [RA + 0.840, REAR_TOP + 0.111],
             [RA + 0.848, REAR_TOP + 0.014]]

decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("window-trim", DLO_DOOR[:7] + [(2790, 158)] + DLO_QUARTER[2:6], "chrome", CHROME, kind="line",
               depth=[0.45, 2], facing=0.3),
    side_decal("vent-divider", [(2415, 266), (2452, 162)], "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", RAIL_CABIN + [(3040, 228)], "chrome", CHROME, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.55, 2]),
    # Push-button pull handle: the concealed lever only came with the C series (MY1970).
    side_decal("door-handle", [(2690, 300), (2745, 300), (2745, 309), (2690, 309)], "chrome", CHROME, depth=[0.6, 2]),
    # Chrome sill strip between the arches (photo 22, 1969 T; photo 01), to the moved rear arch.
    side_decal("rocker-trim", [(2240, 505), (2800 + SHIFT, 505), (2800 + SHIFT, 520), (2240, 520)], "chrome", CHROME,
               depth=[0.6, 2]),
    {"id": "bumper-front", "plane": "side", "kind": "fill", "finish": "rubber", "color": RUBBER,
     "points": [[0.0, STRIP_BOT], [0.0, STRIP_TOP], [X(1925), STRIP_TOP], [X(1925), STRIP_BOT]],
     "depth": [0.0, 2], "facing": 0.2},
    {"id": "bumper-rear", "plane": "side", "kind": "fill", "finish": "rubber", "color": RUBBER,
     "points": [[X(3160), STRIP_BOT], [X(3160), STRIP_TOP], [L, STRIP_TOP], [L, STRIP_BOT]],
     "depth": [0.0, 2], "facing": 0.2},
    box("side", "indicator-side", IND_X0, IND_X1, IND_Y0, IND_Y1, "lens", AMBER, depth=[0.5, 2], facing=0.25),
    {"id": "taillight-side", "plane": "side", "kind": "fill", "points": TAIL_SIDE, "finish": "lens", "color": AMBER,
     "depth": [0.5, 2], "facing": 0.25},
]

# Front plane (same front end as 02/01; lamp heights = factory housing y 405-437 -> 0.507-0.586).
#   Inboard -> outboard (photo 22, 1969 T): chrome horn grille, clear parking lens, amber
#   indicator wrapping round (lateral split from the 1963 front elevation, as 01: 0.396 /
#   0.569 / 0.580 / 0.648 / 0.742). No front guards, no fog lamps (photo 22).
LAMP_B, LAMP_T = Y(437), Y(405)
decals += [
    box("front", "bumper-front-face", 0.0, 0.77, STRIP_BOT - 0.004, STRIP_TOP + 0.004, "chrome", CHROME, depth=FRONT, facing=0.3),
    box("front", "bumper-insert-front", 0.0, 0.77, STRIP_BOT + 0.004, STRIP_TOP - 0.004, "rubber", RUBBER, depth=FRONT, facing=0.3),
    box("front", "horn-grille", 0.396, 0.569, LAMP_B, LAMP_T, "chrome", CHROME, depth=FRONT, facing=0.3, stripes=[0.012, 0.45]),
    box("front", "parking-front", 0.580, 0.648, LAMP_B, LAMP_T, "lens", "#eef1f2", depth=FRONT, facing=0.25),
    box("front", "indicator-front", 0.648, 0.742, LAMP_B, LAMP_T, "lens", AMBER, depth=FRONT, facing=0.25),
    # Plate on the bumper below the strip (photo 22: 520 x 110 mm plate, lower half of the blade).
    box("front", "plate-front", 0.0, 0.26, 0.30, 0.41, "satin", "#e9e9e6", depth=FRONT, facing=0.3),
]

# Rear plane. Lamp units sit on the bumper (photo 01: 0.014-0.111 m above the bumper top).
# Lateral split from photo 04 (911 E, straight rear), as fractions of the body half-width at
# lamp height: amber 0.96-0.855, clear 0.855-0.80, red 0.80-0.684 (flush parts - protruding
# guards/reflectors are magnified by the close camera and are placed as 02 instead).
T_BOT, T_TOP = REAR_TOP + 0.014, REAR_TOP + 0.111
ZB = body_half_width(RA + 0.78, (T_BOT + T_TOP) / 2)
decals += [
    box("rear", "taillight", round(0.684 * ZB, 4), round(0.80 * ZB, 4), T_BOT, T_TOP, "lens", "#b8231d", depth=REAR, facing=0.25),
    box("rear", "reverse-light", round(0.80 * ZB, 4), round(0.855 * ZB, 4), T_BOT, T_TOP, "lens", "#eef1f2", depth=REAR, facing=0.25),
    box("rear", "indicator-rear", round(0.855 * ZB, 4), round(0.96 * ZB, 4), T_BOT, T_TOP, "lens", AMBER, depth=REAR, facing=0.25),
    box("rear", "bumper-rear-face", 0.0, 0.8, STRIP_BOT - 0.004, STRIP_TOP + 0.004, "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", "bumper-insert-rear", 0.0, 0.8, STRIP_BOT + 0.004, STRIP_TOP - 0.004, "rubber", RUBBER, depth=REAR, facing=0.3),
    # Rear guards: chrome with black rubber faces (photos 04, 11, 01); z as the 02 rear view.
    box("rear", "guard-rear", 0.36, 0.43, 0.33, 0.56, "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", "guard-pad-rear", 0.372, 0.418, 0.345, 0.545, "rubber", RUBBER, depth=REAR, facing=0.3),
    # Red reflectors on the bumper below the lamps (photos 04, 23, 24), below the strip.
    box("rear", "reflector-rear", round(0.70 * ZB, 4), round(0.90 * ZB, 4), STRIP_BOT - 0.055, STRIP_BOT - 0.01,
        "lens", "#a51d1a", depth=REAR, facing=0.3),
    box("rear", "plate-rear", 0.0, 0.26, 0.40, 0.52, "satin", "#e9e9e6", depth=REAR, facing=0.3),
    # 'PORSCHE' in widely spaced letters low on the lid, gold to MY1972 (geometry.json 03);
    # photo 04: 0.33 m half-span, ~0.045 m above the lamp tops.
    box("rear", "badge-rear", 0.0, 0.33, T_TOP + 0.035, T_TOP + 0.055, "chrome", GOLD, depth=REAR, facing=0.2),
]

# Top plane.
screen_top = [[X(2262), 0.0], [X(2262), 0.60], [X(2470), 0.5], [X(2478), 0.0]]       # 02
rear_top = [[X(2862), 0.0], [X(2862), 0.47], [X(3100), 0.46], [X(3105), 0.0]]        # 02
# Engine-lid grille: factory plan x 3150-3232 (Autocar LWB plan: 0.41-0.62 m behind its rear
# hub = x 3.55-3.76 here, vs 3.53-3.73: same part); half-width 0.44 (factory 0.43, Autocar 0.45).
GRILLE_X0, GRILLE_X1 = X(3150), X(3232)
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": screen_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.85, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": rear_top, "finish": "glass", "color": GLASS,
     "facing": 0.15, "depth": [0.9, 2]},
    box("top", "engine-grille", GRILLE_X0, GRILLE_X1, 0.0, 0.44, "chrome", CHROME, stripes=[0.016, 0.5],
        facing=0.3, depth=[0.8, 2]),
    # '911 T' script centred just below the grille (geometry.json 03 badging; photo 04 layout).
    box("top", "badge-model", GRILLE_X1 + 0.03, GRILLE_X1 + 0.05, 0.0, 0.063, "chrome", GOLD, facing=0.3, depth=[0.7, 2]),
    # Cowl air slot (photo 22) ahead of the screen, 0.086 m deep as 02, half-width 0.25.
    box("top", "cowl-grille", X(2215), X(2250), 0.0, 0.25, "satin", "#2b2b2b", stripes=[0.012, 0.5], facing=0.3,
        depth=[0.8, 2]),
    # Crest on the lid nose (geometry.json 03 "near its leading edge"), right behind the lid front.
    box("top", "crest", HOOD_FRONT_X + 0.012, HOOD_FRONT_X + 0.052, 0.0, 0.022, "chrome", GOLD, facing=0.3, depth=[0.45, 2]),
    # Filler flap on the LEFT front wing (geometry.json 03; factory plan oval (2195, 1290) px,
    # 0.19 x 0.093 m).
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left",
     "points": [[round(X(2195) + 0.097 * math.cos(a), 4), round(0.678 + 0.0465 * math.sin(a), 4)]
                for a in np.linspace(0, 2 * math.pi, 13)],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3, "depth": [0.7, 2]},
    {"id": "hood-gap", "plane": "top", "kind": "line",
     "points": [[HOOD_FRONT_X, 0.0], [HOOD_FRONT_X + 0.002, 0.3], [HOOD_CORNER_X - 0.008, HOOD_EDGE_Z_NOSE - 0.012],
                [HOOD_CORNER_X, HOOD_EDGE_Z_NOSE], [X(2250), HOOD_EDGE_Z_COWL]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
    {"id": "lid-gap", "plane": "top", "kind": "line",
     "points": [[X(3110), 0.0], [X(3110), LID_EDGE_Z + 0.02], [X(3370), LID_EDGE_Z - 0.02], [X(3372), 0.0]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]
assert len({d["id"] for d in decals}) == len(decals), "duplicate decal ids"

# ------------------------------------------------------------------ parts
# 165 HR 15 (specs.json 03): the same tyre as stop 02, whose diameter was measured in two side
# photos at 0.265-0.2675 x WB(2211) = 0.59-0.60 m (TRACING.md) -> 0.60 m. (Photo 01's car runs
# unknown tyres and sits low; the Autocar drawing draws 0.625 m on the 911 E.)
TYRE_D = 0.60
car = {
    "id": STOP,
    "length": L,
    "frontAxle": FA,
    "rearAxle": RA,
    "trackFront": 1.362,            # specs.json 03 (911 T, 5 1/2 J)
    "trackRear": 1.343,
    "body": body,
    "decals": decals,
    "wheels": {
        # Fuchs forged 5-spoke: every LWB 911 T in the research photos (01, 08, 09-11, 16, 22 = July
        # 1969 T, 23) and both LWB drawings show Fuchs; polished spokes on a black star (geometry.json 03).
        "front": {"diameter": TYRE_D, "width": 0.165, "rim": 0.381, "design": "fuchs",
                  "face": "#c9cdd1", "lip": "#d9dcdf", "caliper": None},
        "rear": {"diameter": TYRE_D, "width": 0.165, "rim": 0.381, "design": "fuchs",
                 "face": "#c9cdd1", "lip": "#d9dcdf", "caliper": None},
    },
    # Same headlamp as 02 (unchanged part: 1963 front elevation z 0.614, ring 0.238 m).
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
    # Single round chrome mirror forward on the driver's door (geometry.json 03), as 02.
    "mirror": {"at": [X(2335), 0.885, 0.76], "size": [0.05, 0.09, 0.09], "shape": "round", "color": CHROME,
               "finish": "chrome", "sides": "left"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    # Single tailpipe below the bumper on the car's LEFT (geometry.json 03; photo 04), z from
    # photo 04 (1.4 x the guard offset), height as 02.
    "exhausts": [[round(L - 0.02, 4), Y(500), -0.55, 0.03]],
}

out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
with open(out, "w") as f:
    json.dump(car, f, indent=1)

# ------------------------------------------------------------------ calibration for the checks
AC_S = WB / 637.0
calib = {
    # Autocar LWB side view: hubs from rim-circle fits; tipF places the car's own front axle on
    # the drawn hub (the drawing's bumper face is at x ~28, its front guard at 18).
    "side": {"image": os.path.relpath(AUTOCAR, ROOT), "wheelF": [268.9, 1149.6], "wheelR": [905.9, 1148.1],
             "tipF": round(268.9 - FA / AC_S, 1), "crop": [0, 820, 1203, 1251]},
    # 1973 911 T 2.4 profile (car facing right): rim-circle hubs; tipF from the front axle.
    "side_photo": {"image": os.path.relpath(PHOTO_SIDE, ROOT), "wheelF": [1466.3, 976.4], "wheelR": [629.1, 982.5],
                   "tipF": round(1466.3 + FA / (WB / 837.2), 1), "crop": [230, 560, 1900, 1110]},
    # Autocar LWB plan (isotropic assumption; its width reads ~2.6 % wide).
    "top": {"image": os.path.relpath(AUTOCAR, ROOT), "tipF": round(268.9 - FA / AC_S, 1),
            "tipR": round(268.9 - FA / AC_S + L / AC_S, 1), "centreY": 514, "crop": [0, 250, 1203, 780]},
    # Rally 3-view: front x 6-262 at the widest (1610 mm), rear 375-632; ground at the tyres' foot.
    "front": {"image": os.path.relpath(RALLY, ROOT), "centreX": 134.0, "groundY": 199, "left": 6, "right": 262,
              "width": 1.61, "crop": [0, 0, 300, 205]},
    "rear": {"image": os.path.relpath(RALLY, ROOT), "centreX": 503.5, "groundY": 204, "left": 375, "right": 632,
             "width": 1.61, "crop": [340, 0, 637, 210]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)
print("wrote", os.path.relpath(out, ROOT), "length", L, "axles", FA, RA, "WB", round(RA - FA, 4),
      "lamp ZB", round(ZB, 3))
