"""Trace: 01-901-1963 — Porsche 901, the IAA Frankfurt show car (12 Sep 1963).

References (research/blueprints/01-901-1963/, see sources.json):
  SIDE  official_porsche_sketch_1963_side.jpg  (Porsche AG "Sketch, Porsche 911, 1963",
        3300x1860, orthographic, car facing left = its LEFT side, wheel-centre lines and
        ground line drawn).                                           -> primary side view
  FRONT official_porsche_sketch_1963_front.jpg (same set, 1100x620, ground line drawn,
        isotropic).                                                   -> front-view z / y
  HOOD  brochure_901_1963_phantom_side.png (901 brochure W 221 e, 9.63): the only
        drawing that shows the front-lid centre line (dashed, hidden behind the wing).
  PLAN / REAR: no 901 drawing exists (sources.json: "use the SWB 911 drawings; 901 ->
        911 body is near-identical in plan"): the 1967 factory body drawing
        research/blueprints/02-911-swb-1964/tbp-40868_... is used for plan-view widths and
        the rear-view horizontal positions, mapped onto the 901's own axles and tips.
Official 1963 figures (research/geometry.json 01, brochure 9.63): L 4135, W 1600, H 1273,
  WB 2204, tracks 1332 / 1312, ground clearance 118 mm, 165 x 15 tyres on 4 1/2 J x 15.
Show-car details (research/history.md + geometry.json 01): no bumper guards, no sill trim,
  body-colour bumpers with a chrome strip + black rubber insert, no fog lamps, round chrome
  mirror on the driver's (left) door, round fuel flap on top of the left front wing,
  chrome horn grilles + clear/amber corner lamps below the headlamps, chrome engine-lid grille.

Calibration (side sketch, isotropic):
  wheel-centre lines x = 925 / 2332 px (1407 px <-> WB 2204 mm -> 1.56645 mm/px),
  hub centres y = 1567 / 1565, ground line top edge y = 1762.
  The sketch draws bumper GUARDS (front guard to x = 335, rear "C" guard to 2997); the IAA
  car had none, so the tips are the bumper strip ends: x = 372 (front) and 2988 (rear).
  -> length 4.098 m, front overhang 0.866 m, rear 1.028 m. Cross-check: the 901 brochure
  phantom (no front guard, rear guard drawn) measures 4.134 m over its rear guard = the
  official 4135 mm, and 4.107-4.113 m to the rear bumper-strip end, so the official length
  includes a guard and the guard-less show car is ~4.10-4.11 m (this trace: -0.2..-0.4 %).
  Roof peak y = 956 -> 1.263 m (official 1273, -0.8 %).
  Tyres: measured 0.60 m (see TYRE_D); the sketch draws 0.617 m, so the model's wheel centre
  sits 3.5 px (5 mm) below the drawn hub.
Front sketch: body 321..764 px = 1600 mm (3.612 mm/px), centre x 542.5, ground y 491.5.

Run: <venv python> research/traces/01-901-1963.py
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
from trace_lib import column_profile, silhouette_from_drawing, simplify  # noqa: E402

STOP = "01-901-1963"
BP = os.path.join(ROOT, "research", "blueprints")
SIDE_IMG = os.path.join(BP, STOP, "official_porsche_sketch_1963_side.jpg")
FRONT_IMG = os.path.join(BP, STOP, "official_porsche_sketch_1963_front.jpg")
FACTORY = os.path.join(BP, "02-911-swb-1964", "tbp-40868_porsche-911-1967_factory-body-4view-mm.png")

# ------------------------------------------------------------------ side calibration
S = 2.204 / (2332 - 925)          # m per px (official WB 2204 over the wheel-centre lines)
TIP_X, TAIL_X = 372, 2988         # bumper-strip ends (guards excluded, see docstring)
GROUND_Y = 1762                   # top edge of the drawn ground line
FRONT_AXLE_X, REAR_AXLE_X = 925, 2332


def X(px):
    return round((px - TIP_X) * S, 4)


def Y(py):
    return round((GROUND_Y - py) * S, 4)


def curve(points):
    return [[X(px), Y(py)] for px, py in points]


L = X(TAIL_X)
FA, RA = X(FRONT_AXLE_X), X(REAR_AXLE_X)

# ------------------------------------------------------------------ front-view calibration
F_S = 1.600 / (764 - 321)         # m per px, official width 1600 over the body outline
F_CX, F_GY = 542.5, 491.5


def FZ(px):
    return round(abs(px - F_CX) * F_S, 4)


def FY(py):
    return round((F_GY - py) * F_S, 4)


# ------------------------------------------------------------------ side silhouette (top)
gray = cv2.imread(SIDE_IMG, cv2.IMREAD_GRAYSCALE)
blur = cv2.GaussianBlur(gray, (3, 3), 0)
top_px = {}
for x in range(410, 2950):                # x < 400 is the front bumper guard, x > 2950 the rear guard
    ys = np.nonzero(blur[900:1560, x] < 215)[0]
    if len(ys):
        top_px[x] = float(ys[0] + 900)


def despike(values, window=12, tol=6):
    xs = sorted(values)
    arr = np.array([values[x] for x in xs], float)
    out = arr.copy()
    for i in range(len(arr)):
        lo, hi = max(0, i - window), min(len(arr), i + window + 1)
        med = np.median(arr[lo:hi])
        if abs(arr[i] - med) > tol:
            out[i] = med
    return dict(zip(xs, out))


top_px = despike(top_px)
# The wiper pivot pokes above the cowl at x 1205-1265: bridge it on the cowl line.
for a, b in ((1195, 1250),):
    ya, yb = top_px[a], top_px[b]
    for x in range(a, b + 1):
        top_px[x] = ya + (yb - ya) * (x - a) / (b - a)
# Nose and tail behind the guards (hand-read from column scans): bumper top / strip end at
# the tips, the wing's nose line (x 408-415) and the rear wing corner above the lamp.
NOSE_TOP = [(372, 1492), (385, 1482), (398, 1476), (408, 1462)]
# Tail (4x zoom + column scans): the lid centre line reaches the rear corner at
# (2958, 1410); the tail's rear face then drops almost vertically to the bumper top at
# (2969, 1474); behind that only the bumper remains (strip end cap at x 2986, y 1505).
# Every upper line (crest, belt, rail, top) follows this common drop.
TAIL_DROP = [(2964, 1431), (2967, 1456), (2969, 1475), (2978, 1483), (2988, 1505)]
TAIL_TOP = [(2950, 1395), (2958, 1410)] + TAIL_DROP
# Fastback: the true centre-line silhouette is the faint upper line behind the roof step
# (column scans at threshold 232); the darker line below it is the rear-window frame.
FASTBACK = [(2150, 997), (2170, 1000.5), (2180, 1003), (2186, 1012), (2210, 1026.5), (2230, 1033.5),
            (2250, 1040), (2270, 1046.5), (2290, 1054), (2310, 1062), (2330, 1069), (2350, 1077),
            (2370, 1084.5), (2390, 1092), (2410, 1100.5), (2430, 1108), (2450, 1116), (2470, 1124),
            (2490, 1133), (2510, 1140.5), (2530, 1148.5), (2550, 1157.5), (2570, 1166), (2590, 1174),
            (2610, 1186.5)]
fb = dict(FASTBACK)
xs_fb = sorted(fb)
for x in range(xs_fb[0], xs_fb[-1] + 1):
    top_px[x] = float(np.interp(x, xs_fb, [fb[k] for k in xs_fb]))
for x, y in NOSE_TOP + TAIL_TOP:
    top_px[x] = y
silhouette_top = [[X(x), Y(v)] for x, v in sorted(top_px.items()) if x % 4 == 0 or x < 410 or x > 2948]

# ------------------------------------------------------------------ side silhouette (bottom)
# Hand-read lower edge; arches = outer edge of the dark wheel-well band (radial scan at
# the mid-grey threshold, see .md), sill line y 1603-1607, aprons from column scans.
BOTTOM = [
    (372, 1520), (385, 1533), (400, 1546), (415, 1564), (430, 1584), (445, 1595), (460, 1603),
    (490, 1610), (520, 1613), (560, 1617), (600, 1620), (640, 1620), (668, 1614), (678, 1600),
    # front arch
    (682, 1580), (684, 1565), (686, 1545), (696, 1520), (702, 1500), (711, 1472), (721, 1450),
    (735, 1429), (749, 1409), (767, 1392), (787, 1377), (808, 1364), (830, 1355), (853, 1347),
    (877, 1342), (901, 1339), (925, 1337), (949, 1337), (973, 1340), (997, 1344), (1021, 1352),
    (1043, 1362), (1064, 1376), (1083, 1391), (1101, 1408), (1116, 1428), (1129, 1449),
    (1140, 1471), (1148, 1494), (1155, 1518), (1163, 1542), (1169, 1567), (1176, 1590),
    (1195, 1604),
    # sill
    (1300, 1605), (1600, 1605), (1900, 1605), (2070, 1604),
    # rear arch
    (2092, 1590), (2096, 1565), (2100, 1541), (2106, 1517), (2114, 1494), (2124, 1472),
    (2135, 1452), (2150, 1433), (2166, 1416), (2185, 1402), (2204, 1389), (2225, 1379),
    (2246, 1372), (2268, 1367), (2300, 1363), (2332, 1363), (2370, 1366), (2396, 1369),
    (2417, 1374), (2438, 1381), (2459, 1390), (2479, 1402), (2497, 1416), (2514, 1432),
    (2530, 1451), (2544, 1471), (2552, 1480), (2558, 1500), (2566, 1520), (2577, 1540),
    (2578, 1560), (2583, 1582), (2595, 1601),
    # rear apron up to the bumper end
    (2700, 1601), (2800, 1599), (2870, 1599), (2905, 1594), (2930, 1575), (2948, 1552),
    (2965, 1538), (2980, 1525), (2988, 1508)]
silhouette_bot = curve(BOTTOM)

# ------------------------------------------------------------------ hood centre line
# Brochure phantom (901 brochure 9.63): dashed front-lid centre line, as a height offset
# below its own wing-crest line (brochure px, vertical scale 1.03 mm/px: roof 393 px to
# tyre contact 1635 px = 1273 mm). x mapped to the sketch by the front wheel centre
# (brochure 885 -> 925) and the scale ratio 1.0421/1.5665 (brochure WB 2115 px).
BRO_CREST = {400: 879, 500: 868.5, 600: 859.5, 700: 851.5, 800: 845, 850: 842.5, 950: 837.5}
BRO_HOOD = {400: 1002, 500: 966, 600: 934, 700: 906, 800: 880.5, 850: 868.5, 950: 846.5}


def bro_to_sketch(bx):
    return 925 + (bx - 885) * (1.0421 / 1.56645)


hood_pts = []
for bx in sorted(BRO_HOOD):
    sx = bro_to_sketch(bx)
    drop_m = (BRO_HOOD[bx] - BRO_CREST[bx]) * 1.03e-3       # hood below the wing crest
    crest_y = Y(top_px[int(round(sx))])
    hood_pts.append([X(sx), round(crest_y - drop_m, 4)])
# Front of the lid (hidden behind the wings in every side view): the lid is the same part as
# on the production car, so its nose shape is taken from the 1967 factory drawing's dashed
# hidden lid line (02 sheet px, as read in the 02 trace), measured from that car's bumper
# face at the centre line (plan row scan: x 1714 px), and shifted vertically onto the
# brochure's lid points (mean offset over the brochure points x < 0.5 m). At the tip the
# section closes on the bumper top (side sketch y 1476 -> 0.448 m; front sketch 0.453 m).
SWB_HOOD_PX = [(1705, 425), (1718, 408), (1750, 392), (1800, 370), (1850, 350), (1900, 332), (1950, 318)]
swb_hood = [((px - 1714) * 2.4567e-3, (644.3 - py) * 2.4567e-3) for px, py in SWB_HOOD_PX]
_sx, _sy = zip(*swb_hood)
offs = [y - float(np.interp(x, _sx, _sy)) for x, y in hood_pts if x < 0.5]
HOOD_OFFSET = round(float(np.mean(offs)), 4)
hood_nose = [[0.0, Y(1476)]] + [[round(x, 4), round(y + HOOD_OFFSET, 4)] for x, y in swb_hood
                                if 0.0 < x < hood_pts[0][0] - 0.02]
print("hood nose offset vs the 1967 lid line", HOOD_OFFSET, "from", [round(o, 4) for o in offs])
# Visible cowl (above the wing crest from x ~1000) to the windscreen base, then the
# windscreen / roof / fastback / lid / tail = side silhouette.
cowl = [[X(x), Y(top_px[x])] for x in range(1010, 1246, 8)]
SCREEN_BASE_X = 1245
top_y = hood_nose + hood_pts + cowl + [p for p in silhouette_top if p[0] > X(SCREEN_BASE_X)]

# ------------------------------------------------------------------ other side-view lines (px)
# Wing crest: silhouette from the headlamp back to x ~1000, then the lower line that runs
# on to the door (column scans: y 1233-1236), cabin shoulder just under the glass,
# rear hip highlight (faint line 2000..2600), tail lamp top at the corner.
CREST_CABIN = [(1250, 1238), (1500, 1238), (1800, 1240), (2000, 1242)]
CREST_REAR = [(2350, 1264), (2500, 1281), (2600, 1297), (2750, 1330), (2880, 1375),
              (2945, 1405), (2958, 1411)] + TAIL_DROP
BELT_CABIN = [(1420, 1232), (1600, 1231), (1800, 1233), (1950, 1235), (2050, 1227),
              (2300, 1225), (2380, 1218)]
# Engine-lid side edge (lower of the two tail lines).
LID_EDGE = [(2600, 1216), (2650, 1240), (2700, 1273), (2750, 1297), (2800, 1321),
            (2850, 1346), (2900, 1374), (2940, 1400), (2958, 1412)] + TAIL_DROP
# Drip rail (upper edge of the gutter), runs down the fastback as the "flyline".
RAIL_CABIN = [(1600, 1003), (1700, 1008), (1800, 1011), (1900, 1018),
              (2000, 1028), (2100, 1047), (2200, 1072), (2300, 1092), (2400, 1127),
              (2500, 1163), (2560, 1185)]
# Side glass: vent + door glass (one outline, lowest-front first, clockwise in this view),
# quarter glass. Inner edge of the chrome frames.
DLO_DOOR = [(1455, 1215), (1500, 1170), (1560, 1100), (1610, 1045), (1648, 1022),
            (1700, 1027), (1800, 1029), (1900, 1038), (1990, 1053), (2062, 1063),
            (1985, 1233), (1800, 1231), (1600, 1229)]
DLO_QUARTER = [(2010, 1229), (2088, 1066), (2150, 1075), (2200, 1093), (2250, 1115),
               (2300, 1141), (2345, 1170), (2375, 1195), (2380, 1212), (2360, 1222),
               (2200, 1225)]
WINDOW_TRIM = [(1440, 1216), (1500, 1160), (1560, 1092), (1640, 1012), (1700, 1016),
               (1800, 1019), (1900, 1026), (2000, 1038), (2100, 1056), (2200, 1082),
               (2300, 1117), (2350, 1150), (2385, 1185), (2390, 1215)]
DOOR = [(1395, 1240), (1300, 1243), (1275, 1255), (1262, 1275), (1255, 1310), (1250, 1400),
        (1252, 1480), (1257, 1545), (1265, 1553), (1840, 1553), (1870, 1540), (1900, 1500),
        (1930, 1430), (1960, 1350), (1980, 1285), (1990, 1240)]
HANDLE = [(1878, 1317), (1878, 1303), (1972, 1303), (1972, 1317)]   # pull handle + button, column scans
# Bumper chrome strips (rounded rectangles y 1493-1518; rubber insert 1500-1510).
STRIP_F = [(372, 1518), (372, 1494), (380, 1492), (735, 1492), (742, 1505), (735, 1518)]
STRIP_R = [(2575, 1518), (2572, 1505), (2578, 1492), (2982, 1492), (2988, 1505), (2982, 1518)]
# Corner lamp unit below the headlamp (side view, wraps the wing corner).
INDICATOR_SIDE = [(420, 1466), (447, 1430), (530, 1430), (547, 1468)]

# ------------------------------------------------------------------ plan view (factory 02 sheet)
# Half-widths from the 1967 factory plan (same method as the 02 trace), mapped onto the
# 901's axles/tips. The factory tips (1693 / 3387) are the bumper GUARDS; the bumper faces
# at the centre line are 1714 / 3364.5 px (row scans) -> those map to 0 and L here.
fgray = cv2.imread(FACTORY, cv2.IMREAD_GRAYSCALE)
F_SC = 2.4567e-3


def swb_to_901(px):
    """factory-drawing x (px) -> 901 x (m), piecewise linear through the landmarks."""
    marks = [(1714, 0.0), (2066, FA), (2966, RA), (3364.5, L)]
    for (a, xa), (b, xb) in zip(marks, marks[1:]):
        if px <= b or b == marks[-1][0]:
            return round(xa + (px - a) * (xb - xa) / (b - a), 4)
    return L


plan = silhouette_from_drawing(fgray, (1660, 670, 3420, 1340), close=3, thresh=150)
plan = cv2.morphologyEx(plan, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
pprof = column_profile(plan)
half_width = [[swb_to_901(x), round((b - t) / 2 * F_SC, 4)] for x, (t, b) in sorted(pprof.items())
              if 1860 <= x <= 3230 and x % 4 == 0]
# Nose and tail outlines hand-read by row scans (guards excluded): (x px, half-width px).
# (row y -> outline x; half-width = centre row 1012 (nose) / 1013 (tail) minus y)
NOSE_PLAN = [(1714, 0), (1714.5, 42), (1715, 62), (1716, 82), (1718, 102), (1718.5, 122),
             (1722.5, 142), (1726.5, 162), (1731.5, 182), (1737, 202), (1744.5, 222),
             (1756.5, 242), (1771.5, 262), (1794.5, 282), (1857.5, 302)]
TAIL_PLAN = [(3242.5, 283), (3293.5, 263), (3326.5, 243), (3340, 223), (3347.5, 203),
             (3352.5, 183), (3353.5, 163), (3358.5, 123), (3361, 103), (3363, 83),
             (3363.5, 63), (3364.5, 0)]
nose = [[swb_to_901(x), round(h * F_SC, 4)] for x, h in NOSE_PLAN]
tail = [[swb_to_901(x), round(h * F_SC, 4)] for x, h in TAIL_PLAN]
side_z = nose + [p for p in half_width if nose[-1][0] < p[0] < tail[0][0]] + tail

# ------------------------------------------------------------------ z of the section lines
# Front sketch (901): headlamp centres 374 / 712 px (z 0.609 / 0.612), y 306 -> 0.670;
# wing crest over the lamp tunnels at x ~365 (z 0.64); A-pillar/screen base corner
# x 362 (z 0.652), roof rail at the screen top x 390 (z 0.551).
# Front lid side edges (the gap between lid and wings): front sketch rows y 330-350 show
# them at x 431-432.5 / 653-655.5 (z 0.40) at the nose, rising to x 379.5 / 706 at y 260
# (z 0.59) at the cowl; the factory plan (02 sheet, halves of the upper/lower lid lines,
# x 1760 -> 2260 px) gives 0.388 -> 0.582. The lid's front edge is a transverse line
# 17 px (0.042 m) behind the bumper face (plan: solid line x 1731 behind the face at
# 1714), its corners at (1740, 858) px -> x 0.064 m, z 0.383 m.
# -> 0.39 at the nose (mean of plan 0.383 / front sketch 0.40), 0.585 at the cowl.
# Factory drawing (02 sheet, horizontal only): B-pillar section glass base 1300/2 = 0.65,
# roof 1076/2 = 0.538, rear window 1016/2 = 0.508, rear hip 0.657, lid edge 0.44 (same
# readings as the 02 trace).
LAMP_Z = round((FZ(374) + FZ(712)) / 2, 4)
LAMP_Y = FY(306)
LAMP_R_LENS = 27 * F_S          # lens radius 27 px
LAMP_R_RING = 33 * F_S          # chrome ring outer radius 33 px
CREST_Z_FRONT = FZ(365)
SCREEN_BASE_Z = FZ(362)
RAIL_Z_SCREEN_TOP = FZ(390)
HOOD_EDGE_Z_NOSE, HOOD_EDGE_Z_COWL, HOOD_CORNER_X, HOOD_FRONT_X = 0.39, 0.585, 0.064, 0.042
CABIN_BELT_Z, CABIN_RAIL_Z = 0.65, 0.538
REAR_WINDOW_Z, HIP_CREST_Z, LID_EDGE_Z = 0.508, 0.657, 0.44


def keys(pairs):
    return [[round(a, 4), round(b, 4)] for a, b in pairs]


# crest: nose (bumper top at the tip) -> wing nose -> lamp brow -> wing crest (silhouette).
crest = [[0.0, Y(1492)]] + [p for p in silhouette_top if X(400) <= p[0] <= X(1000)]
crest += [[X(x), Y(y)] for x, y in ((1050, 1235), (1150, 1235))] + curve(CREST_CABIN) + curve(CREST_REAR)
belt = [[0.0, Y(1492)]] + [[x, round(y - 0.03, 4)] for x, y in hood_nose[1:] + hood_pts]
belt += [[X(x), round(Y(top_px[x]) - 0.03, 4)] for x in range(1010, 1246, 24)]
belt += curve(BELT_CABIN) + curve(LID_EDGE)
rail = [[0.0, Y(1492)]] + [[x, round(y - 0.004, 4)] for x, y in hood_nose[1:] + hood_pts]
rail += [[X(x), round(Y(top_px[x]) - 0.004, 4)] for x in range(1010, 1246, 24)]
# Windscreen base curves back ~155 px from the centre (1245) to the A-pillar foot (1395), so
# the rail runs along the cowl to the pillar foot, then up the A-pillar outer line
# (column scans: y = 1098.5 - 1.01 (x - 1500)) to the drip rail.
A_PILLAR = [(1395, 1205), (1450, 1150), (1500, 1098.5), (1540, 1058), (1570, 1027), (1600, 1005)]
rail += curve([(1300, 1203), (1350, 1206)]) + curve(A_PILLAR)
rail += curve([p for p in RAIL_CABIN if p[0] > 1600])
# Behind the rear window the rail collapses onto the engine lid (just under its centre line).
rail += [[X(x), round(Y(top_px[x]) - 0.004, 4)] for x in list(range(2605, 2950, 25)) + [2950]]
rail += curve([(2958, 1413)] + TAIL_DROP)

side_y = keys([(0, Y(1505)), (X(430), Y(1480)), (FA, 0.53), (X(1300), 0.51), (X(1900), 0.505),
               (RA, 0.51), (X(2800), Y(1490)), (L, Y(1505))])
floor_y = keys([(0, Y(1530)), (X(420), Y(1575)), (X(560), Y(1622)), (FA, 0.19), (X(1200), 0.17),
                (X(2100), 0.17), (RA, 0.19), (X(2700), Y(1606)), (X(2930), Y(1580)), (L, Y(1515))])

rocker_z = [[x, round(max(0.0, z - (0.012 if (abs(x - FA) < 0.33 or abs(x - RA) < 0.36) else 0.04)), 4)]
            for x, z in side_z]
crest_z = keys([(0, 0), (X(390), 0.34), (X(470), CREST_Z_FRONT - 0.03), (X(560), CREST_Z_FRONT),
                (X(1245), 0.66), (X(1420), 0.70), (X(1990), 0.71), (X(2200), 0.69),
                (X(2450), HIP_CREST_Z), (X(2800), 0.6), (L - 0.03, 0.4), (L, 0)])
belt_z = keys([(0, 0), (HOOD_FRONT_X, 0.3), (HOOD_CORNER_X, HOOD_EDGE_Z_NOSE), (X(SCREEN_BASE_X), HOOD_EDGE_Z_COWL),
               (X(1420), CABIN_BELT_Z), (X(2380), CABIN_BELT_Z - 0.01), (X(2600), LID_EDGE_Z + 0.03),
               (X(2800), LID_EDGE_Z), (L - 0.03, 0.3), (L, 0)])
roof_z = keys([(0, 0), (X(400), 0.16), (X(SCREEN_BASE_X), 0.3), (X(1320), 0.5), (X(1395), 0.66), (X(1600), RAIL_Z_SCREEN_TOP),
               (X(2000), CABIN_RAIL_Z - 0.01), (X(2180), REAR_WINDOW_Z), (X(2590), REAR_WINDOW_Z - 0.02),
               (X(2615), 0.30), (X(2800), 0.2), (X(2940), 0.1), (L, 0)])

body = {
    "floorY": floor_y,
    "rockerY": simplify(silhouette_bot, 0.002),
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


# ------------------------------------------------------------------ decals
# Slot ids: TRACING.md table ids wherever the table defines the feature; the SWB example's
# extra slots (vent-divider, taillight-side, parking-front, reverse-light, indicator-rear,
# bumper-insert-*, plate-rear, cowl-grille, crest) where the 901 has the same part.
# NOTE the SWB example currently puts its SIDE-view bumper strip in "bumper-strip-front/
# rear" and re-uses those ids on the front/rear planes (duplicates: the app pairs only the
# first); TRACING.md defines bumper-strip-* as the front/rear-plane rubber strips. To avoid
# pairing a side decal with a front decal (in 02 or in the later table-following stops) this
# car uses bumper-front/-rear (side), bumper-front-face/-rear-face (front/rear chrome strip)
# and the SWB's bumper-insert-* (rubber insert). Change these constants if 02 is renamed.
ID_SIDE_BUMPER_F, ID_SIDE_BUMPER_R = "bumper-front", "bumper-rear"
ID_FACE_F, ID_FACE_R = "bumper-front-face", "bumper-rear-face"
ID_INSERT_F, ID_INSERT_R = "bumper-insert-front", "bumper-insert-rear"


def side_decal(id_, pts, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": curve(pts), "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, a0, a1, b0, b1, finish, color, **kw):
    """Axis-aligned rectangle: (a, b) = (x, y) side, (x, z) top, (z, y) front/rear (as in 02)."""
    d = {"id": id_, "plane": plane, "kind": "fill", "points": [[a0, b0], [a0, b1], [a1, b1], [a1, b0]],
         "finish": finish, "color": color}
    d.update(kw)
    return d


CHROME = "#dfe2e5"
RUBBER = "#1c1c1c"
GLASS = "#1d2329"
AMBER = "#e59a35"
GOLD = "#c9a24e"
FRONT = [-0.05, 0.45]          # x range where front decals apply (as in 02)
REAR = [L - 0.45, L + 0.05]

# Vent-window rear frame: the slanted chrome bar behind the A-pillar (sketch zoom: the
# bar's two edges run (1570, 1222)-(1650, 1022) and (1582, 1222)-(1660, 1025)).
VENT_BAR = [(1576, 1224), (1655, 1022)]
# Tail lamp housing seen from the side (it wraps round the corner): sketch zoom trapezoid.
TAIL_SIDE = [(2775, 1473), (2803, 1413), (2932, 1413), (2940, 1472)]

decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.35),
    side_decal("window-trim", WINDOW_TRIM, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("vent-divider", VENT_BAR, "chrome", CHROME, kind="line", depth=[0.45, 2], facing=0.3),
    side_decal("drip-rail", RAIL_CABIN, "chrome", CHROME, kind="line", depth=[0.4, 2], facing=0.2),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.55, 2]),
    side_decal("door-handle", HANDLE, "chrome", CHROME, depth=[0.6, 2]),
    # No sill trim on the IAA car (history.md: it "lacked the production car's ... sill
    # trim"; none drawn on the 1963 sketch, none on the 'TYP 901' photo) -> no rocker-trim.
    # Bumper ends from the side: the chrome strip (rubber insert inside) on the body-colour
    # bumper, running back to the wheel arches.
    side_decal(ID_SIDE_BUMPER_F, STRIP_F, "chrome", CHROME, depth=[0.0, 2], facing=0.2),
    side_decal(ID_SIDE_BUMPER_R, STRIP_R, "chrome", CHROME, depth=[0.0, 2], facing=0.2),
    # Corner lamps wrap round the wing corners: the amber section shows from the side
    # (No. 57 side photo), front unit below the headlamp, rear unit on the bumper.
    side_decal("indicator-side", INDICATOR_SIDE, "lens", AMBER, depth=[0.5, 2], facing=0.25),
    side_decal("taillight-side", TAIL_SIDE, "lens", AMBER, depth=[0.5, 2], facing=0.25),
]

# Front plane: the official 1963 front elevation (z, y both true scale, 3.612 mm/px).
#   chrome strip y 374.5-386 px (0.381-0.423 m; side sketch 0.382-0.423 m) to the
#   wrap-round at x 333 (z 0.757); rubber insert y 378-383; lamp/grille housing y 345-366
#   (0.453-0.529 m; side sketch lamp 0.460-0.520): horn grille x 652-700 mirrored
#   (z 0.396-0.569), lamp x 703-748 (z 0.580-0.742) split at x 722 (z 0.648);
#   plate x 471-614 (half 0.258), y 397-425 (0.240-0.341, 'TYP 901' photo: plate below
#   the bumper strip); crest at y 336-349 (0.51-0.56 m) on the lid nose.
#   Colours: amber OUTBOARD, clear INBOARD (901 No. 57 front photo, 'TYP 901' photo).
#   No bumper guards and no fog lamps on the 1963 show car (geometry.json 01).
LAMP_BOT, LAMP_TOP = FY(366), FY(345)
decals += [
    box("front", ID_FACE_F, 0.0, FZ(333), FY(386), FY(374.5), "chrome", CHROME, depth=FRONT, facing=0.3),
    box("front", ID_INSERT_F, 0.0, FZ(333), FY(383), FY(378), "rubber", RUBBER, depth=FRONT, facing=0.3),
    box("front", "horn-grille", FZ(652), FZ(700), LAMP_BOT, LAMP_TOP, "chrome", CHROME, depth=FRONT, facing=0.3,
        stripes=[0.012, 0.45]),
    box("front", "parking-front", FZ(703), FZ(722), LAMP_BOT, LAMP_TOP, "lens", "#eef1f2", depth=FRONT, facing=0.25),
    box("front", "indicator-front", FZ(722), FZ(748), LAMP_BOT, LAMP_TOP, "lens", AMBER, depth=FRONT, facing=0.25),
    box("front", "plate-front", 0.0, FZ(471), FY(425), FY(397), "satin", "#e9e9e6", depth=FRONT, facing=0.3),
]

# Rear plane: no 901 rear drawing. Heights from the 901 side sketch (lamp 1413-1473 px ->
# 0.453-0.547 m; strip as the front); lateral split from the production 901 No. 57 rear
# photo (research/photos/01-901-1963/03-rear.jpg, scale from its 520 mm plate = 382 px):
# red 0.444-0.563, clear 0.563-0.597, amber 0.597-0.666 (02 factory rear view:
# 0.43/0.56/0.61/0.686). Plate: from the strip bottom to 0.071 m above the strip top
# (No. 57 photo), half-width 0.26.
T_BOT, T_TOP = Y(1470), Y(1416)
decals += [
    box("rear", "taillight", 0.444, 0.563, T_BOT, T_TOP, "lens", "#b8231d", depth=REAR, facing=0.25),
    box("rear", "reverse-light", 0.563, 0.597, T_BOT, T_TOP, "lens", "#eef1f2", depth=REAR, facing=0.25),
    box("rear", "indicator-rear", 0.597, 0.666, T_BOT, T_TOP, "lens", AMBER, depth=REAR, facing=0.25),
    box("rear", ID_FACE_R, 0.0, 0.757, Y(1518), Y(1492), "chrome", CHROME, depth=REAR, facing=0.3),
    box("rear", ID_INSERT_R, 0.0, 0.757, Y(1510), Y(1500), "rubber", RUBBER, depth=REAR, facing=0.3),
    box("rear", "plate-rear", 0.0, 0.26, Y(1518) - 0.002, Y(1492) + 0.071, "satin", "#e9e9e6", depth=REAR, facing=0.3),
]

# Top plane.
SCREEN_TOP_X = 1555
RW_TOP_X, RW_BOT_X = 2180, 2590
GRILLE_X0, GRILLE_X1 = 2620, 2752       # sketch zoom: louvred patch on the lid
# Windscreen in plan: the base curves back from the centre (side sketch x 1245) to the
# A-pillar foot (x 1395, 0.235 m further back); its plan shape follows the factory plan's
# screen base (02 sheet: dx 0 / 0.007 / 0.022 / 0.054 / 0.091 / 0.140 / 0.201 m at
# z 0 / 0.23 / 0.38 / 0.50 / 0.57 / 0.62 / 0.668), scaled to the 901's 0.235 m sweep.
SCREEN_SWEEP = [(0.0, 0.0), (0.007, 0.23), (0.022, 0.38), (0.054, 0.50), (0.091, 0.57), (0.140, 0.62), (0.201, 0.668)]
k_sweep = (X(1395) - X(SCREEN_BASE_X)) / 0.201
screen_base = [[round(X(SCREEN_BASE_X) + dx * k_sweep, 4), round(z * (SCREEN_BASE_Z - 0.03) / 0.668, 4)] for dx, z in SCREEN_SWEEP]
# Cowl fresh-air slot at the lid's rear edge ('TYP 901' photo): lateral half-width 0.267
# (front sketch hatched band x 467-615) / 0.245 (No. 57 front photo) -> 0.26; fore-aft
# depth and gap to the screen base as the production part (02: 0.086 m, 0.03 m).
COWL_X1 = X(SCREEN_BASE_X) - 0.03
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill",
     "points": screen_base + [[X(SCREEN_TOP_X), RAIL_Z_SCREEN_TOP - 0.03], [X(SCREEN_TOP_X) + 0.01, 0.0]],
     "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.8, 2]},   # 901 screen base at 0.87 m
    {"id": "rear-window", "plane": "top", "kind": "fill",
     "points": [[X(RW_TOP_X), 0.0], [X(RW_TOP_X), REAR_WINDOW_Z - 0.04], [X(RW_BOT_X), REAR_WINDOW_Z - 0.05], [X(RW_BOT_X) + 0.005, 0.0]],
     "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.8, 2]},    # rear window base 0.92 m (centre)
    # Chrome grille, two halves each side of a centre bar: half-width 0.43 m (factory plan
    # 171-176 px; No. 57 rear photo 630 px / 2 at the plate scale), length from the sketch.
    # (the 901's lid is lower than the 911's: the grille spans y 0.77-0.86 m -> depth from 0.7)
    box("top", "engine-grille", X(GRILLE_X0), X(GRILLE_X1), 0.0, 0.43, "chrome", CHROME, stripes=[0.018, 0.5],
        facing=0.3, depth=[0.7, 2]),
    box("top", "cowl-grille", COWL_X1 - 0.086, COWL_X1, 0.0, 0.26, "satin", "#2b2b2b", stripes=[0.012, 0.5],
        facing=0.3, depth=[0.8, 2]),
    # Gold crest on the lid nose (geometry.json 01): front sketch 0.05 m shield at 0.51-0.56 m
    # height -> where the lid centre line passes that height, x 0.035-0.075 m.
    box("top", "crest", 0.035, 0.075, 0.0, 0.025, "chrome", GOLD, facing=0.3, depth=[0.45, 2]),
    # Filler flap on top of the LEFT front wing (geometry.json 01 body.fuel_filler).
    # Plan position: factory plan oval centre (2195, 1290) px -> x 1.182 m, z 0.678 m (the
    # 901 sketch flap centre x 1131 -> 1.189 m agrees). Size: 0.19-0.20 m long (No. 57
    # photo 79 px; 1963 sketch 130 px), 0.093 m across in plan (factory plan 38 px).
    {"id": "fuel-flap", "plane": "top", "kind": "line", "side": "left",
     "points": [[round(swb_to_901(2195) + 0.097 * math.cos(a), 4), round(0.678 + 0.0465 * math.sin(a), 4)]
                for a in np.linspace(0, 2 * math.pi, 13)],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3, "depth": [0.7, 2]},
    {"id": "hood-gap", "plane": "top", "kind": "line",
     "points": [[HOOD_FRONT_X, 0.0], [HOOD_FRONT_X + 0.002, 0.3], [HOOD_CORNER_X - 0.008, HOOD_EDGE_Z_NOSE - 0.012],
                [HOOD_CORNER_X, HOOD_EDGE_Z_NOSE], [X(SCREEN_BASE_X - 10), HOOD_EDGE_Z_COWL]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
    {"id": "lid-gap", "plane": "top", "kind": "line",
     "points": [[X(RW_BOT_X + 5), 0.0], [X(RW_BOT_X + 5), LID_EDGE_Z + 0.02], [X(2935), LID_EDGE_Z - 0.02], [X(2940), 0.0]],
     "finish": "satin", "color": "#2a2a2a", "facing": 0.3},
]
for d in decals:
    d["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in d["points"]]
assert len({d["id"] for d in decals}) == len(decals), "duplicate decal ids"

# ------------------------------------------------------------------ parts
# 165 x 15 has no aspect ratio in its size: measured instead (TRACING.md). 901 No. 57 studio
# side photo (research/photos/01-901-1963/01-side-left.jpg): tyre top y 652 -> ground contact
# 908 = 256 px over a hub-to-hub wheelbase of 943 px (x 440 -> 1383) = 0.2715 x WB -> 0.598 m
# at WB 2204. (Porsche's 1963 sketch draws r = 197 px = 0.617 m; brochure art ~0.29 x WB.)
TYRE_D = 0.60
car = {
    "id": STOP,
    "length": L,
    "frontAxle": FA,
    "rearAxle": RA,
    "trackFront": 1.332,                  # 901 brochure 9.63
    "trackRear": 1.312,
    "body": body,
    "decals": decals,
    "wheels": {
        "front": {"diameter": round(TYRE_D, 4), "width": 0.165, "rim": 0.381, "design": "steel-hubcap",
                  "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
        "rear": {"diameter": round(TYRE_D, 4), "width": 0.165, "rim": 0.381, "design": "steel-hubcap",
                 "face": "#c9ccd0", "lip": "#d7d9dc", "caliper": None},
    },
    "headlight": {
        # side sketch: chrome ring face from (517, 1410) to (583, 1262), centre ~ (553, 1336)
        "centre": [X(553), LAMP_Y, LAMP_Z],
        "outline": [[round(math.cos(a) * LAMP_R_LENS, 4), round(math.sin(a) * LAMP_R_LENS, 4)]
                    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)],
        "yaw": 4,
        "pitch": 24,                     # side sketch: ring face inclined atan(66/148) = 24 deg from vertical
        "ring": round(LAMP_R_RING - LAMP_R_LENS, 4),
        "ringColor": "#e3e6e9",
        "ringFinish": "chrome",
        "lensColor": "#e2e8ec",
        "graphic": "sealed",
    },
    # Round chrome mirror on the driver's (left) door only (geometry.json 01). Front sketch:
    # head = 22 px circle centred (763, 260) -> centre z 0.796 m, y 0.836 m, diameter 0.079 m
    # (stalk from the door top at z 0.731); side sketch: head at x ~1440 px, y ~1232 (0.830 m).
    "mirror": {"at": [X(1440), FY(260), round(FZ(763) - 0.0395, 4)], "size": [0.05, 0.079, 0.079], "shape": "round",
               "color": CHROME, "finish": "chrome", "sides": "left"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    # Tailpipe below the bumper on the near (left, -z) side: sketch (2905-2975, 1565-1595).
    # One tailpipe on the LEFT (-z): side sketch x 2905..2975, y 1565..1595 (r 0.024 m);
    # z from the No. 57 rear photo (pipe root ~374 px left of the centre at ~1.45 mm/px).
    # The IAA car is reported with twin tailpipes (history.md) but the second pipe's position
    # is undocumented, so only the drawn one is modelled.
    "exhausts": [[X(2945), Y(1580), -0.55, 0.024]],
}

out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
with open(out, "w") as f:
    json.dump(car, f, indent=1)

r_px = TYRE_D / 2 / S
calib = {
    "side": {"image": os.path.relpath(SIDE_IMG, ROOT), "wheelF": [FRONT_AXLE_X, GROUND_Y - r_px],
             "wheelR": [REAR_AXLE_X, GROUND_Y - r_px], "tipF": TIP_X, "crop": [300, 880, 3060, 1790]},
    "front": {"image": os.path.relpath(FRONT_IMG, ROOT), "centreX": F_CX, "groundY": F_GY,
              "left": 321, "right": 764, "width": 1.6, "crop": [280, 110, 810, 510]},
    # Studio profile of the production 901 No. 57 (Porsche press kit): rim-circle fits give
    # hub centres (439.0, 777.5) / (1390.4, 786.6). tipF is set so the car's own front axle
    # lands on the photo's hub (the photo's centre-line extremes are ~5 % foreshortened by
    # perspective: bumper centre ~0.8 m behind the hub plane at a ~15 m camera distance).
    "side_photo": {"image": "research/photos/01-901-1963/01-side-left.jpg", "wheelF": [439.0, 777.5],
                   "wheelR": [1390.4, 786.6], "tipF": round(439.0 - FA / (2.204 / 951.44), 1),
                   "crop": [40, 330, 1880, 940]},
    # Substitute plan: the 1967 factory plan (no 901 plan exists), bumper faces as tips.
    "top": {"image": os.path.relpath(FACTORY, ROOT), "tipF": 1714, "tipR": 3364.5, "centreY": 1014,
            "crop": [1650, 660, 3420, 1360]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)
print("wrote", os.path.relpath(out, ROOT), "length", L, "axles", FA, RA, "height",
      max(v for _, v in body["topY"]))
