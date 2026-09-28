"""Trace: 15-991-1-2012 — 911 Carrera Coupé, type 991 first phase (991.1), MY2012–2015.

The 991.1 and 991.2 share one body shell: research/geometry.json lists only apron,
lamp, lid-grille, door-handle and ride-height changes for the facelift (length
4,491 -> 4,499 mm, height 1,303 -> 1,294 mm from the 10 mm lower PASM ride height).
The only official orthographic drawing of that shell is Porsche's own 991.2
Carrera S dimension sheet (research/blueprints/16-991-2-2016/dd_porsche-official_
911-carrera-s-2016_front-rear-side-mm.gif: side, front and rear views with printed
dimensions), so the shell is traced from it here; the 991.1 specifics come from
the 991.1 references (vendor 4-view vec-4101 and research/photos/15-991-1-2012).
Stop 16 imports `trace_991_shell()` / `shell_to_body()` from this file and applies
the 991.2 details from the official drawing.

Official dimensions (research/specs.json: Porsche spec PDF / porsche.com 2012):
  991.1 Carrera: L 4,491  W 1,808  H 1,303  WB 2,450  tracks 1,532 / 1,518 mm,
  tyres 235/40 ZR 19 on 8.5J / 285/35 ZR 19 on 11J.

--- Calibration --------------------------------------------------------------
OS  official side view (px of the .gif):
    axle extension lines of the printed "2.450 mm" at x = 504.5 / 1215.5
    -> 711 px = 2,450 mm -> 3.44585 mm/px; both drawn wheels are centred on
    these lines (tyre white area 408..601 wide, 995..1188 tall -> centre y
    1091.75, radius 97 px = 334 mm ~ 235/40 R19 = 335.3 mm).
    Length extension lines x = 216.5 / 1521.5 -> 4,496.8 mm (printed 4,499, -0.05 %).
    Ground = wheel centre + 335.3 mm = y 1189.06 (drawn ground line top edge 1189).
    Roof stroke centre y 812 -> 1,299 mm (printed 1,294-1,298, +0.2 %).
    Outlines are ~4.5 px strokes; readings are stroke centres (the printed
    dimension lines reference stroke centres too).
OF/OR official front / rear views: centre lines x 369 / 1357.5 (symmetry of the
    body outline and of both lamps); ground line top y 470. Across: official
    1,808 mm width over the outer body edges (536 px) = 3.373 mm/px; up: the roof
    stroke centre (y 83) at the side view's 1.299 m -> 3.357 mm/px (0.5 % from
    square). The printed track lines sit ~25 mm inboard of the official tracks
    and are not used.
VT  vendor 991.1 top view (vec-4101): tips x 49 / 818 (769 px = 4,491 mm),
    centre row 629.5. Its max plan width is 1,845 mm at the length scale (2 %
    over the official 1,808; the 991.2 vendor top view agrees to 6 mm), so plan
    half-widths are scaled to the official width (5.74 mm/px across).
VF/VR vendor 991.1 front / rear views: centres 1055.5 / 1060, 1,808 mm over
    314 / 313 px; up 5.904 mm/px from the printed 1,293 mm height (ground 327 /
    748). Used only for 991.1-specific apron and lamp details.
Ride height: the drawing is a 991.2 (1,299 mm measured). The 991.1 Carrera is
    1,303 mm (non-PASM, 9 mm above the 991.2's 1,294): RIDE = +0.004 m here,
    -0.005 m for stop 16.
Length: the 8 mm facelift difference (4,491 vs 4,499) is not split by any
    source; each overhang takes half (remap_overhangs()).

Run: <venv>/bin/python research/traces/15-991-1-2012.py
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import simplify  # noqa: E402

STOP = "15-991-1-2012"
OFFICIAL = os.path.join(ROOT, "research", "blueprints", "16-991-2-2016",
                        "dd_porsche-official_911-carrera-s-2016_front-rear-side-mm.gif")
VENDOR = os.path.join(ROOT, "research", "blueprints", STOP,
                      "vec-4101_porsche-911-carrera-s-991-2012_4view-dims-watermarked.jpg")

# ------------------------------------------------------------------ OS calibration
S = 2.450 / 711
TIP_X, TAIL_X = 216.5, 1521.5
FA_X, RA_X = 504.5, 1215.5
WHEEL_Y = 1091.75
GROUND_Y = WHEEL_Y + 0.3353 / S


def X(px):
    return (px - TIP_X) * S


def Y(py):
    return (GROUND_Y - py) * S


# ------------------------------------------------------------------ OF / OR calibration
OF_CX, OR_CX, END_GROUND = 369.0, 1357.5, 470.0
END_H = 1.808 / 536
END_V = 1.299 / 387       # roof stroke centre (y 83) at the side view's 1.299 m


def FZ(px, cx=OF_CX):
    return abs(px - cx) * END_H


def FY(py):
    return (END_GROUND - py) * END_V


# ------------------------------------------------------------------ VT / VF / VR calibration
VT_TIP, VT_TAIL, VT_CY = 49, 818, 629.5
VT_SX = 4.491 / (VT_TAIL - VT_TIP)
VT_SZ = 0.904 / 157.5
# Vendor front / rear views: roof-top stroke edge 107 / 525, tyre bottoms 330 / 747 (223 /
# 222 px for the printed 1,293 mm), body sides 313 px for 1,808 mm; centre lines 1055.5 /
# 1060.5. The vendor car (Carrera S, 1,293-1,295 mm) sits 8 mm lower than the 991.1
# Carrera (1,303 mm): VENDOR_RIDE is added to its heights.
VF_CX, VF_GROUND, VF_S = 1055.5, 330.0, 0.00579
VR_CX, VR_GROUND, VR_S = 1060.5, 747.0, 0.00580
VENDOR_RIDE = 0.008


def vf(px, py):
    return [round(abs(px - VF_CX) * VF_S, 3), round((VF_GROUND - py) * VF_S + VENDOR_RIDE, 3)]


def vr(px, py):
    return [round(abs(px - VR_CX) * VR_S, 3), round((VR_GROUND - py) * VR_S + VENDOR_RIDE, 3)]


# ================================================================== side view readings
# Lower edge (stroke centres / wheel-well band edges), 4x gridded zooms + column runs.
BOTTOM = [
    (216.5, 1117), (218, 1122), (222, 1128), (225, 1133), (230, 1138), (260, 1138), (300, 1137.5),
    (340, 1141), (380, 1143.5), (393.5, 1143),
    # front arch: outer edge of the dark wheel-well band, ray-cast from the hub (504.5, 1091.75)
    (393.2, 1111.4), (393.0, 1091.8), (395.2, 1072.5), (400.2, 1053.8), (408.4, 1036.2), (419.5, 1020.4),
    (432.2, 1005.6), (448.2, 994.3), (466.0, 986.0), (484.9, 980.5), (504.5, 978.2), (524.1, 980.5),
    (543.3, 985.1), (561.2, 993.5), (577.8, 1004.4), (591.8, 1018.5), (603.7, 1034.5), (612.6, 1052.4),
    (617.8, 1071.8), (619.5, 1091.8), (618.7, 1111.9), (620.5, 1146),
    # sill (rocker bottom)
    (700, 1147), (800, 1146.5), (900, 1146), (1000, 1146), (1085, 1146), (1101.5, 1146),
    # rear arch (hub 1215.5, 1091.75)
    (1102.2, 1111.7), (1102.5, 1091.8), (1104.2, 1072.1), (1109.3, 1053.1), (1116.3, 1034.5),
    (1127.4, 1017.8), (1141.3, 1003.3), (1158.0, 992.2), (1176.3, 984.2), (1195.7, 979.5),
    (1215.5, 978.2), (1235.3, 979.5), (1255.0, 983.2), (1273.5, 991.3), (1290.7, 1002.1),
    (1305.5, 1016.2), (1316.8, 1033.2), (1324.5, 1052.1), (1329.7, 1071.6), (1333.0, 1091.8),
    (1333.7, 1112.6), (1334, 1135),
    # rear apron bottom and tail
    (1360, 1133), (1400, 1129), (1440, 1124), (1480, 1123.5), (1500, 1123), (1508, 1119),
    (1515, 1108), (1520, 1095), (1521.5, 1088),
]

# Greenhouse lines (stroke centres), column runs every 5-20 px.
# DLO_TOP = outer frame of the side-glass opening (L3); GLASS_TOP = glass edge (L4);
# BELT1 = glass base (sill); BELT2 = door top edge, continuing forward as the fender
# crease that leaves the silhouette at x 522 (0.870 m = the front view's fender peak).
DLO_TOP = [(820, 859), (840, 850), (860, 843.5), (880, 839.5), (900, 837.5), (920, 836.5), (940, 837),
           (960, 838), (980, 839.5), (1000, 842), (1020, 844.5), (1040, 847.5), (1060, 851.5), (1080, 856),
           (1100, 861), (1120, 866.5), (1140, 872.5), (1160, 879.5), (1180, 887), (1200, 896.5), (1206, 905)]
GLASS_TOP = [(820, 865), (840, 856), (860, 849), (880, 844.5), (900, 842.5), (920, 842), (940, 842.5),
             (960, 843.5), (980, 845), (1000, 847), (1020, 849.5)]
BELT1 = [(716, 933), (760, 932.5), (800, 933.5), (840, 932.5), (880, 931.5), (920, 930.5), (960, 929.5),
         (1000, 928), (1040, 926), (1080, 923.5), (1120, 920.5), (1160, 916.5), (1200, 909.5), (1206, 905)]
BELT2 = [(522, 938.5), (572, 936.5), (612, 935.5), (660, 934.5), (700, 937), (760, 936), (800, 937),
         (840, 936.5), (880, 935.5), (920, 935), (960, 933.5), (1000, 932.5), (1040, 931), (1080, 928.5),
         (1120, 926), (1160, 921.5), (1200, 915)]
# A-pillar: L_a = screen side edge / pillar outer edge from the screen corner (675, 935) to
# the roof corner (815, 848) and (810, 835); the silhouette above it is the screen centre
# (front view: screen top edge y 100 = 1.242 m on the centre line, reached by the silhouette
# at x 803).
A_PILLAR = [(675, 935), (685, 932), (700, 921), (720, 907), (740, 894), (760, 881), (780, 868.5), (800, 857),
            (810, 851), (815, 848)]
# A-pillar rear edge L_b = front edge of the side-glass frame, rising off the belt at x 702 and
# running into DLO_TOP at x 820.
A_PILLAR_REAR = [(702, 936), (720, 923), (740, 908), (760, 894), (780, 881), (800, 869), (815, 861)]
# Deck edge (line L2): roof side edge -> C-pillar / rear-window side edge -> engine-lid side
# edge -> spoiler trailing corner (1455, 958).
DECK_EDGE = [(812, 833), (840, 832), (860, 827.5), (880, 824.5), (900, 823), (920, 822.5), (960, 823),
             (1000, 826), (1040, 831), (1080, 837.5), (1120, 845), (1160, 857), (1200, 867), (1250, 881.5),
             (1300, 897), (1320, 904.5), (1330, 913), (1340, 921), (1350, 928), (1360, 933), (1380, 939.5),
             (1400, 943), (1420, 949.5), (1440, 955), (1455, 958)]
# Rear-wing shoulder crease (upper edge of the taillight zone): 1270,985 -> 1460,961.
SHOULDER = [(1270, 985), (1300, 981), (1340, 976), (1380, 971), (1420, 966), (1460, 961), (1478, 959)]
# Screen and rear window along the centre line (silhouette x): screen base 612 (cowl),
# screen top 803 (1.242 m, front view); rear-window top 1122 (rear view y 108.5 = 1.213 m),
# bottom 1325 just ahead of the lid's leading lip (1330-1342).
SCREEN_BASE_X, SCREEN_TOP_X, REAR_TOP_X, REAR_BOT_X = 612, 803, 1122, 1318

# Side glass outlines — lowest-front point first, clockwise in the side view (nose left):
# up the glass front edge (L_c), along the glass top (L4), down the B-pillar, back along the sill.
DLO_DOOR = [(718, 931), (730, 922), (760, 902), (780, 887), (800, 875), (820, 865), (860, 849), (900, 842.5),
            (940, 842.5), (980, 845), (1010, 848.5), (1025, 851), (1004, 926), (960, 928.5), (880, 930.5)]
DLO_QUARTER = [(1013, 926), (1034, 855), (1060, 856.5), (1100, 866), (1140, 877.5), (1180, 892), (1198, 902),
               (1201, 907), (1180, 913.5), (1120, 919.5), (1060, 923.5)]
# Door shut line (front edge x 655, rear edge curving to the sill), os_b/os_c zooms.
DOOR = [(700, 936), (668, 950), (657, 975), (655, 1020), (656, 1100), (900, 1100), (940, 1095), (990, 1060),
        (1020, 1000), (1026, 960), (1005, 928)]
# Headlight lens in the side view: front-bottom (300,1020) to top-rear (410,951).
LAMP_SIDE = (300, 1020, 410, 951)
# Front side-marker lens (clear, below/behind the lamp): 355..432 x 1003..1023.
SIDE_MARKER = [(372, 1022), (357, 1005), (432, 1003), (430, 1010), (412, 1022)]


def side_silhouette_top():
    """Top edge of the side view (first dark pixel + 2 px = stroke centre)."""
    g = np.array(Image.open(OFFICIAL).convert("L"))
    top = {}
    for x in range(217, 1522):
        ys = np.nonzero(g[790:1150, x] < 150)[0]
        if len(ys):
            top[x] = ys[0] + 790 + 2.0
    # Wiper arms stand above the cowl at x 592-613: bridge the cowl to the screen base.
    a, b = 590, 614
    for x in range(a, b + 1):
        top[x] = top[a] + (top[b] - top[a]) * (x - a) / (b - a)
    return top


def plan_half_width(length):
    """VT plan outline -> {car x: half-width}; x spread over `length` (the OS drawing's), mirrors
    (VT x 352-402) bridged."""
    im = np.asarray(Image.open(VENDOR).convert("RGB")).astype(int)
    mx, mn = im.max(axis=2), im.min(axis=2)
    car = (((mx - mn) > 60) | (mx < 120)).astype(np.uint8)
    reg = car[440:830, 30:840].copy()
    import cv2
    h, w = reg.shape
    ff = reg.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 2)
    filled = ff != 2
    out = {}
    for x in range(VT_TIP, VT_TAIL + 1):
        ys = np.nonzero(filled[:, x - 30])[0]
        if len(ys):
            out[x] = (ys[-1] - ys[0] + 1) / 2
    a, b = 352, 402
    for x in range(a, b + 1):
        out[x] = out[a] + (out[b] - out[a]) * (x - a) / (b - a)
    return {round((x - VT_TIP) / (VT_TAIL - VT_TIP) * length, 4): v * VT_SZ for x, v in sorted(out.items())}


def dedupe(curve):
    out = []
    for x, v in sorted(curve):
        x, v = float(x), float(v)
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([round(x, 4), round(v, 4)])
    return out


def keys(pairs):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pairs]


# ================================================================== shell
# Lid-centre depth under the lamp-top fender bump (m) and the lid shut line's depth below
# the lid centre (m): set from the front-3/4 photo check (see .md).
LAMP_TOP_DIP = 0.012
LID_EDGE_DROP = 0.02
# Lens centre line on the side view (midway between the lens edges B and C).
LENS_MID = [(300, 1021), (320, 1012), (340, 1000), (360, 986), (380, 972), (400, 959), (410, 952)]


def screen_base_z(px):
    """Plan position of the screen's lower edge: centre at x 612, corners (z 0.70) at x 675
    (A-pillar base on the side view); parabolic in plan (VT: corners ~0.2 m behind the centre)."""
    t = min(1.0, max(0.0, (px - SCREEN_BASE_X) / (675 - SCREEN_BASE_X)))
    return 0.70 * math.sqrt(t)


def trace_991_shell():
    """991 shell curves in car space (x from the front tip, drawing ride height/length)."""
    top_px = side_silhouette_top()
    L = X(TAIL_X)
    xs_sorted = sorted(top_px)

    def silY(px):
        return Y(float(np.interp(px, xs_sorted, [top_px[k] for k in xs_sorted])))

    def line(pts, lo=-1e9, hi=1e9):
        return [(X(a), Y(b)) for a, b in pts if lo <= a <= hi]

    # ---- topY (centre line) -------------------------------------------------------
    # The whole side silhouette is the centre line: ahead of x 258 px the rounded nose, then
    # the front lid (its leading edge, 0.62 m on the centre line in the front view, meets
    # the silhouette at x 258 = 0.144 m), the cowl, screen, roof, rear window, lid and tail.
    # The only place where the fender rises to the silhouette is the lamp's top-rear corner
    # (410, 951; plan: lamp oval 0.24-0.65 m); there the lid centre sits LAMP_TOP_DIP below.
    nose = [(0.0, Y(1112)), (X(219), Y(1046)), (X(221), Y(1039))]
    nose += [(X(x), silY(x)) for x in range(224, 259, 6)]
    hood = []
    for x in [258, 290, 320, 350, 380, 410, 440, 470, 500, 522]:
        t = min(1.0, abs(x - 430) / 110)
        hood.append((X(x), silY(x) - LAMP_TOP_DIP * (1 - t * t)))
    body_top = [(X(x), silY(x)) for x in range(528, 1522, 6)]
    top_y = dedupe(nose + hood + body_top + [(L, Y(1004))])

    # ---- crestY / crestZ (P3) -----------------------------------------------------
    # Front fender: the headlamp lies on the fender's front slope, so ahead of the lamp's
    # top-rear corner the fender top at the lamp's z follows the lens centre line (midway
    # between the lens edges B and C on the side view: 0.57 m at x 285 px rising at 32 deg
    # to 0.834 m at 410); from there to x 516 it is the silhouette, then the crease BELT2
    # (0.870 m) to the door. Cabin: door shoulder 1.5 cm under BELT2 (door top). Rear: hip
    # crest (rear view: shoulder 0.873 m at z 0.78) closing onto the tail's upper edge.
    crest = [(0.0, Y(1112)), (X(222), Y(1062)), (X(250), Y(1036)), (X(285), Y(1022))]
    crest += [(X(x), Y(v)) for x, v in LENS_MID]
    crest += [(X(x), silY(x)) for x in range(420, 517, 12)]
    crest += [(X(x), Y(v) - (0.015 if x >= 700 else 0.0)) for x, v in BELT2]
    crest += [(X(1250), FY(208)), (X(1320), FY(208)), (X(1390), FY(208) - 0.012),
              (X(1440), Y(962)), (X(1480), Y(968)), (X(1505), Y(992)), (L, Y(1010))]
    crest_y = dedupe(crest)
    crest_z = keys([(0, 0), (X(222), 0.36), (X(250), 0.56), (X(285), 0.66), (X(320), 0.68), (X(410), 0.685),
                    (X(470), 0.675), (X(522), 0.665), (X(612), 0.67), (X(680), 0.755),
                    (X(900), 0.775), (X(1100), 0.775), (X(1200), 0.785), (X(1300), 0.79), (X(1390), 0.78),
                    (X(1440), 0.74), (X(1480), 0.66), (X(1505), 0.5), (L, 0)])

    # ---- beltY / beltZ (P4) -------------------------------------------------------
    # Ahead of the screen: front-lid shut line, LID_EDGE_DROP under the lid centre; z from
    # the VT lid line (0.485 at 0.27 m, 0.571 at 0.71 m) and the front view's valley line
    # (z 0.38 at 0.626 m ... 0.536 at 0.776 m), meeting the screen corner at the A-pillar
    # base (675, 935). Cabin: glass base BELT1 (front-view greenhouse outline z 0.737 at
    # 0.89 m). Behind the quarter window: the C-pillar foot, sweeping onto the foot of the
    # raised rear deck's side face (DECK_EDGE from x 1330: rear view z 0.53-0.55 at 0.80-
    # 0.87 m) down to the spoiler's trailing corner (1455, 958).
    belt = [(0.0, Y(1112)), (X(222), Y(1054)), (X(240), Y(1036))]
    belt += [(x, y - LID_EDGE_DROP) for x, y in hood if x <= X(500)]
    belt += [(X(560), Y(932)), (X(612), Y(933)), (X(660), Y(934.5))]
    belt += line(BELT1)
    belt += [(X(1240), Y(907)), (X(1290), Y(910))]
    belt += line(DECK_EDGE, 1330)
    belt += [(X(1490), Y(975)), (L, Y(1010))]
    belt_y = dedupe(belt)
    belt_z = keys([(0, 0), (X(222), 0.22), (X(240), 0.34), (X(258), 0.40), (X(300), 0.46), (X(352), 0.52),
                   (X(410), 0.555), (X(470), 0.575), (X(522), 0.60), (X(612), 0.66), (X(675), 0.725),
                   (X(716), 0.737), (X(1000), 0.735), (X(1206), 0.715), (X(1260), 0.66), (X(1330), 0.56),
                   (X(1400), 0.545), (X(1455), 0.53), (X(1490), 0.44), (L, 0)])

    # ---- roofY / roofZ (P5) -------------------------------------------------------
    # Ahead of the screen: just under the lid centre, near the centre line; then the screen's
    # lower edge in plan (screen_base_z) at cowl height. A-pillar: the pillar's outer edge
    # rear edge (A_PILLAR_REAR = front edge of the side-glass frame) with z from the plan
    # (VT side-glass strip inner edge 0.669 at 2.08 m, the windscreen edge 0.06 m further in;
    # front view: pillar outer edge z 0.66 at 1.074 m). Cabin: the top edge of the side-glass
    # opening (DLO_TOP) with z 0.628 (2.25 m) -> 0.606 (2.43) -> 0.600 (2.6) -> 0.588 (3.04)
    # (VT; front/rear-view greenhouse outline z 0.59 at 1.215 m). Over the rear quarter the
    # rail blends onto the rear-window side edge on the C-pillar (DECK_EDGE, rear view z
    # 0.49-0.50) and follows it down; behind the rear window: the top edge of the raised
    # engine-lid deck (rear view: lid top corners z 0.47 at 0.98 m) 1.2 cm under the centre.
    roof = [(0.0, Y(1112))]
    roof += [(x, y - 0.004) for x, y in nose[1:] + hood]
    roof += [(X(x), silY(x) - 0.004) for x in (540, 570, 600)]
    roof += [(X(x), silY(x) - 0.006) for x in (630, 650)]
    roof += line(A_PILLAR_REAR)
    roof += line(DLO_TOP, 820, 1100)
    roof += [(X(1150), Y(855)), (X(1200), Y(867))]
    roof += line(DECK_EDGE, 1250, 1320)
    roof += [(X(x), silY(x) - 0.012) for x in (1345, 1380, 1420, 1450, 1475)]
    roof += [(X(1495), Y(975)), (L, Y(1010))]
    roof_y = dedupe(roof)
    roof_z = keys([(0, 0), (X(222), 0.08), (X(258), 0.14), (X(352), 0.20), (X(522), 0.26), (X(600), 0.30),
                   (X(630), screen_base_z(630)), (X(650), screen_base_z(650)), (X(675), 0.72), (X(702), 0.737),
                   (X(720), 0.72), (X(760), 0.705), (X(780), 0.69), (X(800), 0.68), (X(815), 0.67), (X(840), 0.645),
                   (X(880), 0.62), (X(920), 0.606), (X(1000), 0.60), (X(1100), 0.588), (X(1150), 0.54), (X(1200), 0.50),
                   (X(1250), 0.495), (X(1320), 0.485), (X(1345), 0.475), (X(1420), 0.47),
                   (X(1475), 0.46), (X(1495), 0.40), (L, 0)])

    # ---- rockerY / floorY ---------------------------------------------------------
    rocker_y = dedupe([(X(a), Y(b)) for a, b in BOTTOM])
    floor_y = dedupe([(0.0, Y(1117)), (X(230), Y(1139)), (X(330), Y(1147)), (X(420), 0.128),
                      (X(1340), 0.128), (X(1440), Y(1127)), (X(1500), Y(1124)), (L, Y(1090))])

    # ---- sideZ / sideY / rockerZ --------------------------------------------------
    plan = plan_half_width(L)
    side_z = [[x, round(z, 4)] for x, z in plan.items()]
    side_z = simplify([p for i, p in enumerate(side_z) if i % 3 == 0], 0.002)
    # Height of the widest point: front/rear views show vertical body sides (z 0.90) from
    # 0.23 to 0.77 m; the apron corners are widest ~0.5 m, the doors ~0.5 m. Over the
    # wheels the widest point is the flared lip just above the arch cut, so there sideY is
    # kept 3.5 cm above rockerY (otherwise the section would hang a skirt over the tyre).
    base_side = [(0, Y(1114)), (X(250), 0.47), (X(393), 0.50), (X(620), 0.50), (X(900), 0.50),
                 (X(1100), 0.52), (X(1334), 0.55), (X(1450), 0.52), (L, Y(1060))]
    rock = dedupe([(X(a), Y(b)) for a, b in BOTTOM])
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
        near_arch = abs(x - X(FA_X)) < 0.33 or abs(x - X(RA_X)) < 0.36
        rocker_z.append((x, max(0.0, zside(x) - (0.012 if near_arch else 0.05))))
    rocker_z = simplify(keys(rocker_z), 0.003)

    curves = {"floorY": floor_y, "rockerY": rocker_y, "rockerZ": rocker_z, "sideY": side_y, "sideZ": side_z,
              "crestY": crest_y, "crestZ": crest_z, "beltY": belt_y, "beltZ": belt_z, "roofY": roof_y,
              "roofZ": roof_z, "topY": top_y}
    correct_overshoots(curves, plan, silY, L)

    return {
        "L": L, "FA": X(FA_X), "RA": X(RA_X), "silY": silY,
        **curves,
    }


def correct_overshoots(curves, plan, silY, L, iters=8):
    """The loft passes a Catmull-Rom spline through P0..P6, which bulges past P2 (sideZ) and,
    where P5 sits steeply below P6, above the centre line. Pull the keys back so that the
    lofted section's maximum half-width equals the traced plan half-width (VT) and its
    maximum height equals the traced side silhouette. In the cabin the rail is the traced
    DLO top and is left alone (no bulge there once P5 is the glass top)."""
    from trace_lib import half_section
    px = sorted(plan)
    pz = [plan[k] for k in px]

    def target_z(x):
        return float(np.interp(x, px, pz))

    def sil_target(x):
        return silY(TIP_X + x / S)

    cab0, cab1 = X(700), X(1130)
    for _ in range(iters):
        sz = []
        for x, z in curves["sideZ"]:
            if 0.02 < x < L - 0.02:
                zmax = max(p[0] for p in half_section(curves, x))
                z = z - (zmax - target_z(x))
            sz.append([x, round(z, 4)])
        curves["sideZ"] = sz
        ry = []
        for x, y in curves["roofY"]:
            if 0.05 < x < L - 0.03 and not cab0 <= x <= cab1:
                ymax = max(p[1] for p in half_section(curves, x))
                excess = ymax - sil_target(x)
                if excess > 0.0005:
                    y = y - 1.5 * excess
            ry.append([x, round(y, 4)])
        curves["roofY"] = ry


BODY_KEYS = ["floorY", "rockerY", "rockerZ", "sideY", "sideZ", "crestY", "crestZ", "beltY", "beltZ",
             "roofY", "roofZ", "topY"]
Y_KEYS = {"floorY", "rockerY", "sideY", "crestY", "beltY", "roofY", "topY"}


def remap_overhangs(x, shell, d_front, d_rear):
    """Shorten the front / rear overhang by d_front / d_rear metres, wheelbase unchanged."""
    fa, ra, L = shell["FA"], shell["RA"], shell["L"]
    if x <= fa:
        return x * (fa - d_front) / fa
    if x <= ra:
        return x - d_front
    return (ra - d_front) + (x - ra) * (L - ra - d_rear) / (L - ra)


def shell_to_body(shell, ride, d_front, d_rear):
    """Body curves for a stop: ride-height offset and overhang remap applied."""
    body = {}
    for k in BODY_KEYS:
        c = []
        for x, v in shell[k]:
            xx = remap_overhangs(x, shell, d_front, d_rear)
            vv = v + ride if k in Y_KEYS else v
            c.append([round(xx, 4), round(vv, 4)])
        body[k] = dedupe(c)
    L = round(remap_overhangs(shell["L"], shell, d_front, d_rear), 4)
    for k in ("sideZ", "rockerZ", "crestZ", "beltZ", "roofZ"):
        c = body[k]
        c[0] = [0.0, 0.0] if c[0][0] <= 1e-6 else c[0]
        if c[0][0] > 0:
            c.insert(0, [0.0, 0.0])
        if c[-1][0] < L - 1e-6:
            c.append([L, 0.0])
        else:
            c[-1] = [L, 0.0]
    return body, L


# ================================================================== 991.1 specifics
RIDE = 0.004              # 1,303 mm (991.1 Carrera) vs the drawing's 1,299 mm
D_FRONT = D_REAR = 0.003  # 4,491 mm vs the drawing's 4,496.8 mm, split equally

# Front / rear details are placed with the orthographic vendor 991.1 views (vf/vr); their
# shapes follow the straight front / rear photos P10 / P12 (see .md for the readings).


class Ctx:
    """A 991 shell placed for one stop (ride height, overhang remap) plus decal helpers."""

    def __init__(self, ride, d_front, d_rear):
        self.ride = ride
        self.shell = shell = trace_991_shell()
        self.body, self.L = shell_to_body(shell, ride, d_front, d_rear)
        self.FA = round(remap_overhangs(shell["FA"], shell, d_front, d_rear), 4)
        self.RA = round(remap_overhangs(shell["RA"], shell, d_front, d_rear), 4)
        self._df, self._dr = d_front, d_rear
        self.decals = []

    def sx(self, px):
        return round(remap_overhangs(X(px), self.shell, self._df, self._dr), 4)

    def sy(self, py):
        return round(Y(py) + self.ride, 4)

    def side(self, id_, pts, finish, color, kind="fill", **kw):
        d = {"id": id_, "plane": "side", "kind": kind, "points": [[self.sx(a), self.sy(b)] for a, b in pts],
             "finish": finish, "color": color}
        d.update(kw)
        self.decals.append(d)

    def plane(self, id_, pl, pts, finish, color, kind="fill", **kw):
        d = {"id": id_, "plane": pl, "kind": kind, "points": [[round(a, 4), round(b, 4)] for a, b in pts],
             "finish": finish, "color": color}
        d.update(kw)
        self.decals.append(d)


# Wheels: geometry.json 15 documents the standard 19-in Carrera wheel as "10 slim spokes
# grouped in 5 pairs (five twin-spoke)"; several photo cars wear optional wheels.

def shell_decals(c):
    """Decals of the shared 991 shell (glass, shut lines), traced on the official drawing."""
    sx = c.sx
    c.side("side-glass", DLO_DOOR, "glass", "#1c2127", depth=[0.5, 2], facing=0.3)
    c.side("quarter-glass", DLO_QUARTER, "glass", "#1c2127", depth=[0.5, 2], facing=0.3)
    # Black window surround (photos): the outer frame line (A-pillar rear edge, DLO_TOP) as a band.
    c.side("window-trim", A_PILLAR_REAR[1:] + DLO_TOP, "satin", "#15171a", kind="line", width=0.014,
           depth=[0.5, 2], facing=0.25)
    c.side("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.6, 2])
    # Windscreen: centre from the cowl (612) to the header (803); lower edge curving back to
    # the corners at the A-pillar base (675, z 0.70); side edge along the pillar's front edge
    # L_a with the VT glass width (0.70 at 1.64-1.73 m, 0.65 at 1.82, 0.634 at 1.90, 0.611 at
    # 1.99) to the top corner (810, z 0.60); nearly straight header (VT).
    scr = [[sx(SCREEN_BASE_X), 0.0]]
    scr += [[sx(x), round(screen_base_z(x), 4)] for x in (620, 632, 645, 660, 675)]
    scr += [[sx(720), 0.685], [sx(760), 0.655], [sx(780), 0.635], [sx(800), 0.615], [sx(810), 0.60],
            [sx(808), 0.30], [sx(SCREEN_TOP_X), 0.0]]
    c.plane("windscreen", "top", scr, "glass", "#1c2127", facing=0.2, depth=[0.86, 2])
    # Rear window: top 1122 at the centre, bottom 1318; half-width 0.485 (VT) with rounded
    # lower corners (VT: ~0.06 m radius).
    rear = [[sx(REAR_TOP_X), 0.0], [sx(REAR_TOP_X + 8), 0.485], [sx(1250), 0.485], [sx(1300), 0.475],
            [sx(1312), 0.44], [sx(1317), 0.30], [sx(REAR_BOT_X), 0.0]]
    c.plane("rear-window", "top", rear, "glass", "#1c2127", facing=0.15, depth=[0.95, 2])
    # Front-lid shut line in plan: leading edge (x 0.144 m) to the corner inboard of the lamp,
    # then along the fender valley to the screen corner (VT lid line; front-view valley).
    c.plane("hood-gap", "top", [[sx(258), 0.0], [sx(262), 0.30], [sx(280), 0.40], [sx(352), 0.515],
                                [sx(470), 0.575], [sx(560), 0.62], [sx(660), 0.70]],
            "satin", "#2a2a2a", kind="line", facing=0.3)
    # Engine lid in plan: from behind the rear window (1332) to the spoiler's trailing edge
    # (1478); sides along the raised deck's top edge (rear view z 0.47-0.50).
    c.plane("lid-gap", "top", [[sx(1332), 0.0], [sx(1332), 0.47], [sx(1476), 0.50], [sx(1478), 0.0]],
            "satin", "#2a2a2a", kind="line", facing=0.3)


def build():
    c = Ctx(RIDE, D_FRONT, D_REAR)
    shell, body, L, FA, RA = c.shell, c.body, c.L, c.FA, c.RA
    sx, sy, side, plane, decals = c.sx, c.sy, c.side, c.plane, c.decals
    shell_decals(c)

    # ---- side ------------------------------------------------------------------------
    # 991.1 door handle: body-colour pull handle in a recessed grip shell (geometry.json;
    # photos 01-03): the shell's outline is drawn as a dark rim band around the handle
    # pressing of the official drawing (x 938..1015, y 973..995).
    side("door-handle", [(938, 993), (939, 976), (975, 971.5), (1016, 975), (1017, 989), (978, 995.5)], "satin",
         "#1d1e20", kind="band", width=0.009, depth=[0.6, 2], facing=0.3)
    # Clear side-marker lens behind the lamp (P01: x 0.561-0.724 m, y 0.578-0.619 m).
    # Apron DRL/indicator unit wrapping the front corner, seen from the side (P01 hi-res: x 262-330 px,
    # y 615-645 px -> x 0.136-0.334 m, y 0.42-0.51 m).
    plane("indicator-side", "side", [[0.14, 0.43], [0.136, 0.47], [0.15, 0.505], [0.26, 0.508], [0.334, 0.44],
                                     [0.25, 0.425]], "lens", "#e9edf0", depth=[0.4, 2], facing=0.25)
    # Slim wrap-around tail lamp, side part (P01 hi-res: tip u 1555 / v 540, top edge to u 1690 / v 522,
    # bottom v 548 -> x 3.93-4.35 m with 1 % perspective correction, y 0.70-0.78 m).
    plane("taillight-side", "side", [[3.95, 0.705], [3.925, 0.727], [4.15, 0.757], [4.345, 0.779],
                                     [4.35, 0.742], [4.345, 0.704], [4.15, 0.703]],
          "lens", "#9c1a16", depth=[0.5, 2], facing=0.3)
    plane("side-marker", "side", [[0.575, 0.578], [0.561, 0.60], [0.64, 0.619], [0.724, 0.612], [0.70, 0.584]],
          "lens", "#e8e3d6", depth=[0.6, 2], facing=0.3)
    # Front corner light (DRL/indicator strip seen from the side, P01: x 0.135-0.334,
    # y 0.42-0.50) is part of indicator-front on the front plane (it wraps the corner).
    # Fuel flap: right front wing ahead of the door (geometry.json; photo 04: 0.315 m behind
    # the front axle, 0.78 m high, diameter ~0.13 m).
    fcx, fcy, fr = FA + 0.315, 0.78, 0.063
    decals.append({"id": "fuel-flap", "plane": "side", "kind": "line", "side": "right",
                   "points": [[round(fcx + fr * math.cos(a), 4), round(fcy + fr * math.sin(a), 4)]
                              for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 17)],
                   "finish": "satin", "color": "#2a2a2a", "depth": [0.6, 2]})

    # ---- top (plan) ------------------------------------------------------------------
    # Porsche crest on the front lid (geometry.json): VT blob x 84-93 px, row 626-634 -> x 0.204-0.257 m,
    # z +-0.026 m (VT scales), just behind the lid's leading edge (VT x 77.5 px).
    plane("crest", "top", [[0.204, 0.0], [0.204, 0.026], [0.257, 0.026], [0.257, 0.0]], "chrome", "#c9a24e",
          facing=0.3, depth=[0.5, 1.0])
    # 991.1 lid grille: three transverse slats with the third brake light (geometry.json;
    # photos 12, 19, 22). P12: grille 520..870 px wide -> +-0.40 m at the lid; on the lid top
    # between x 1345 and 1462 px (the 991.2 drawing's louvre field, same lid).
    # P22: three dark transverse slots between four painted bars -> period 0.10 m, slot 30 %.
    plane("engine-grille", "top", [[sx(1345), 0.0], [sx(1345), 0.40], [sx(1462), 0.41], [sx(1462), 0.0]],
          "paint", "paint", stripes=[0.10, 0.3], facing=0.3, depth=[0.85, 2])

    # ---- front (VF positions, P10 shapes) ----------------------------------------------
    # Point order (front/rear planes): lowest point first (innermost if tied), then
    # clockwise in the [z, y] plot, i.e. up the inner edge first (as in the 1964 trace).
    front_depth = [-0.05, 0.62]
    # LED DRL / indicator strip over each outer intake (991.1 layout, geometry.json): P10 inner
    # tip 465 px (z 0.45), outer end 195 px (z 0.74 at the plate's scale, ~0.83 corrected for
    # the corner lying 0.2 m further back), 20-35 px (0.02-0.035 m) tall; VF height 0.46-0.51.
    plane("indicator-front", "front", [[0.44, 0.462], [0.46, 0.474], [0.60, 0.497], [0.845, 0.522], [0.855, 0.505],
                                       [0.83, 0.488], [0.62, 0.474]],
          "lens", "#e9edf0", depth=front_depth, facing=0.2)
    # Outer cooling intakes with two horizontal slats (P10): VF dark area 928..995 x 257..292,
    # rounded outer-lower corner (P10: 234..300 x 1062..1074).
    plane("intake-front", "front", [vf(995, 292), vf(995, 257), vf(960, 256), vf(930, 257), vf(927, 270),
                                    vf(931, 285), vf(942, 292)],
          "satin", "#232528", stripes=[0.045, 0.3], depth=front_depth, facing=0.2)
    # Central intake below the plate (VF 1003..1108 x 270..290).
    plane("intake-front-centre", "front", [[0.0, vf(0, 290)[1]], [0.0, vf(0, 271)[1]], [0.30, vf(0, 271)[1]],
                                     [0.305, vf(0, 280)[1]], [0.295, vf(0, 290)[1]]],
          "satin", "#1f2123", depth=front_depth, facing=0.2)
    # Licence plate (EU 520 x 110 mm) on the central intake's top edge (P10: plate bottom =
    # intake top, 1045 px).
    py0 = vf(0, 271)[1]
    plane("plate-front", "front", [[0.0, py0], [0.0, py0 + 0.11], [0.26, py0 + 0.11], [0.26, py0]],
          "satin", "#d9dcdf", depth=front_depth, facing=0.2)
    # Black lower lip (P01, P06, P10): full width below 0.215 m (OF lip line 0.187-0.233 on
    # the 991.2; P01 nose bottom 0.22 m).
    plane("bumper-front-face", "front", [[0.0, 0.14], [0.0, 0.215], [0.60, 0.215], [0.72, 0.23], [0.74, 0.19],
                                         [0.70, 0.14]],
          "satin", "#1b1c1e", depth=[-0.05, 0.45], facing=0.2)

    # ---- rear (VR positions, P12 shapes) -----------------------------------------------
    rear_depth = [L - 0.75, L + 0.05]
    # Slim wrap-around LED taillights (991.1): VR lens 917..988 x 612..631; P12 shape (flat
    # top, full height at the inner end, tapering outward where it wraps the corner).
    plane("taillight", "rear", [vr(975, 631), vr(988, 626), vr(990, 618), vr(985, 612), vr(950, 612),
                                vr(918, 614), vr(914, 619), vr(925, 625), vr(945, 630)],
          "lens", "#9c1a16", depth=rear_depth, facing=0.15)
    # "PORSCHE" lettering between the lamps (P12: 0.733-0.754 m, z +-0.265).
    plane("badge-rear", "rear", [[0.0, 0.733], [0.0, 0.754], [0.265, 0.754], [0.265, 0.733]],
          "satin", "#3b3d40", depth=rear_depth, facing=0.2)
    # Rear plate in the bumper bay (P12: 0.414-0.524 m; EU 520 mm wide).
    plane("plate-rear", "rear", [[0.0, 0.414], [0.0, 0.524], [0.26, 0.524], [0.26, 0.414]],
          "satin", "#d9dcdf", depth=rear_depth, facing=0.2)
    # Small red reflectors low in the bumper either side of the plate bay (geometry.json;
    # VR 943..978 x 675..680, P12 0.395-0.425 m).
    plane("reflector-rear", "rear", [vr(978, 681), vr(978, 675), vr(943, 675), vr(943, 681)],
          "lens", "#a51d18", depth=rear_depth, facing=0.2)
    # Black lower rear section around the tailpipes (P12: below 0.34 m, z < 0.58; VR 690).
    plane("bumper-rear-face", "rear", [[0.0, 0.17], [0.0, vr(0, 690)[1]], [0.52, vr(0, 690)[1]],
                                       [0.60, 0.30], [0.62, 0.20], [0.58, 0.17]],
          "satin", "#1c1d1f", depth=[L - 0.45, L + 0.05], facing=0.2)

    # One oval tailpipe each side (base Carrera, P12): centre z 0.457, y 0.288.
    tail = (0.457, 0.288)
    car = {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.532,
        "trackRear": 1.518,
        "body": body,
        "decals": decals,
        "wheels": {
            "front": {"diameter": round(0.4826 + 2 * 0.235 * 0.40, 4), "width": 0.235, "rim": 0.4826,
                      "design": "twin-spoke", "face": "#c6c9cc", "lip": "#b7babd", "caliper": "#1b1b1b"},
            "rear": {"diameter": round(0.4826 + 2 * 0.285 * 0.35, 4), "width": 0.285, "rim": 0.4826,
                     "design": "twin-spoke", "face": "#c6c9cc", "lip": "#b7babd", "caliper": "#1b1b1b"},
        },
        # Lens: front view 0.261 x 0.228 m (OF), side view 0.38 x 0.24 m along a 32 deg slope
        # (OS), plan 0.41 x 0.23 m (VT) -> a 0.26 x 0.44 m ellipse pitched 58 deg back.
        # Centre: P01 (0.51, 0.707) and OS (0.478, 0.703) -> 0.49 m; z 0.682 (OF).
        "headlight": {
            "centre": [round(0.49 - D_FRONT, 4), round(0.705 + RIDE, 4), 0.682],
            "outline": [[round(0.13 * math.cos(a), 4), round(0.22 * math.sin(a), 4)]
                        for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)],
            "yaw": 8, "pitch": 58, "ring": 0.014, "ringColor": "#c9ced3", "ringFinish": "chrome",
            "lensColor": "#dde6ee", "graphic": "projector",
        },
        # Door-top mirror (geometry.json): housing OS 725..795 x 900..935, OF z 0.80..0.985.
        "mirror": {"at": [sx(760), sy(918), 0.80], "size": [0.24, 0.12, 0.185], "shape": "aero",
                   "color": "paint", "finish": "paint"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        "exhausts": [[round(L - 0.04, 4), tail[1], tail[0], 0.042], [round(L - 0.04, 4), tail[1], -tail[0], 0.042]],
    }
    return car, shell


def photo_silhouette_top(photo, x0, x1, y0=250, y1=800, thresh=45):
    """Top edge of the car against a plain studio background (per-row background colour from
    the image borders)."""
    im = np.asarray(Image.open(photo).convert("RGB")).astype(float)
    bg = np.median(np.concatenate([im[:, :150], im[:, -150:]], axis=1), axis=1)
    car = np.abs(im - bg[:, None, :]).sum(axis=2) > thresh
    prof = {}
    for x in range(x0, x1):
        ys = np.nonzero(car[y0:y1, x])[0]
        if len(ys):
            prof[x] = ys[0] + y0
    return prof


def perspective_side_check(car, photo, hubs, dist, out, crop=None, z_wheel=0.85, flip=False, roof_span=None,
                           u0=None, v0=None):
    """Draw `car` over a side photo with a pinhole camera (no yaw) `dist` m from the centre
    plane, principal point at the image centre, scale and position fixed by the two hub
    centres (at the wheel-face depth z_wheel). Centre-line features then sit where the
    perspective puts them, so the silhouette can be judged against the photo."""
    from PIL import ImageDraw
    sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
    from trace_lib import half_section, mono
    im = Image.open(photo).convert("RGB")
    W, H = im.size
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.35)
    d = ImageDraw.Draw(im)
    fx, fy, rx, ry = hubs
    sgn = -1 if flip else 1
    dw = dist - z_wheel
    f = abs(rx - fx) / (car["rearAxle"] - car["frontAxle"]) * dw
    u0 = W / 2 if u0 is None else u0
    v0 = H / 2 if v0 is None else v0
    xc = car["frontAxle"] - sgn * (fx - u0) * dw / f
    hc = car["wheels"]["front"]["diameter"] / 2 + ((fy + ry) / 2 - v0) * dw / f

    def P(x, y, z):
        dep = dist - z
        return (u0 + sgn * f * (x - xc) / dep, v0 - f * (y - hc) / dep)

    body, L = car["body"], car["length"]
    xs = np.linspace(0, L, 1400)
    top = {}
    umin, umax = 1e9, -1e9
    for x in xs:
        for z, y in half_section(body, x):
            u, v = P(x, y, z)
            k = int(u // 4)
            top[k] = min(top.get(k, 1e9), v)
            umin, umax = min(umin, u), max(umax, u)
    d.line([(k * 4 + 2, top[k]) for k in sorted(top)], fill="#ff2d55", width=2)
    if roof_span:
        prof = photo_silhouette_top(photo, *roof_span)
        err = [top[x // 4] - prof[x] for x in range(roof_span[0], roof_span[1], 10) if x in prof and x // 4 in top]
        err = np.array(err)
        print(f"  roof profile vs photo: mean {err.mean():+.1f} px, rms {np.sqrt((err ** 2).mean()):.1f} px; "
              f"model tips at u {umin:.0f} / {umax:.0f}")
    for key, zkey, col in (("rockerY", "rockerZ", "#ff9500"), ("crestY", "crestZ", "#34c759"),
                           ("beltY", "beltZ", "#007aff"), ("roofY", "roofZ", "#af52de")):
        d.line([P(x, mono(body[key], x), mono(body[zkey], x)) for x in xs], fill=col, width=1)
    for dec in car["decals"]:
        if dec["plane"] != "side" or dec.get("side") == ("right" if not flip else "left"):
            continue
        pp = [P(x, y, 0.8) for x, y in dec["points"]]
        if dec["kind"] != "line":
            pp.append(pp[0])
        d.line(pp, fill="#ffcc00", width=1)
    for ax, key, tr in ((car["frontAxle"], "front", car["trackFront"]), (car["rearAxle"], "rear", car["trackRear"])):
        w = car["wheels"][key]
        zt = tr / 2 + w["width"] / 2
        for rr, wd in ((w["diameter"] / 2, 2), (w["rim"] / 2, 1)):
            d.line([P(ax + rr * math.cos(t), w["diameter"] / 2 + rr * math.sin(t), zt)
                    for t in np.linspace(0, 2 * math.pi, 60)], fill="#00c7be", width=wd)
    if crop:
        im = im.crop(tuple(crop))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)
    print("wrote", os.path.relpath(out, ROOT), f"(camera {dist} m, f {f:.0f} px, height {hc:.2f} m)")


def main():
    car, shell = build()
    out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
    with open(out, "w") as f:
        json.dump(car, f, indent=1)
    tyre_r = car["wheels"]["front"]["diameter"] / 2
    calib = {
        "side": {"image": os.path.relpath(OFFICIAL, ROOT),
                 "wheelF": [FA_X, GROUND_Y - (tyre_r + RIDE) / S], "wheelR": [RA_X, GROUND_Y - (tyre_r + RIDE) / S],
                 "tipF": TIP_X + D_FRONT / S, "crop": [180, 780, 1560, 1200]},
        "top": {"image": os.path.relpath(VENDOR, ROOT), "tipF": VT_TIP, "tipR": VT_TAIL, "centreY": VT_CY,
                "crop": [20, 440, 850, 820]},
        "front": {"image": os.path.relpath(OFFICIAL, ROOT), "centreX": OF_CX, "groundY": END_GROUND - RIDE / END_V,
                  "left": 101, "right": 637, "width": 1.808, "crop": [40, 60, 700, 490]},
        "rear": {"image": os.path.relpath(OFFICIAL, ROOT), "centreX": OR_CX, "groundY": END_GROUND - RIDE / END_V,
                 "left": 1090, "right": 1625, "width": 1.808, "crop": [1030, 60, 1690, 490]},
    }
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    print("wrote", os.path.relpath(out, ROOT), "length", car["length"], "axles", car["frontAxle"], car["rearAxle"])
    # Photo check: official studio profile P01 (hubs read on 2.5x gridded zooms; the body is
    # placed relative to the hubs, so the photo car's optional 20-inch wheels - rim lips 188 px
    # = 0.548 m - do not matter). The camera distance is the only free parameter: 15-22 m
    # bracket the roof profile (x 720-1650 px) and the tips; 18 m is used (see .md).
    perspective_side_check(car, os.path.join(ROOT, "research", "photos", STOP, "01-side-left.jpg"),
                           (555, 673.5, 1396, 674), 18.0,
                           os.path.join(ROOT, "research", "traces", STOP, "check-photo-side.png"),
                           crop=[200, 300, 1780, 820], roof_span=(720, 1650))


if __name__ == "__main__":
    main()
