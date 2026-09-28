"""Trace: 11-996-1-1998 — 911 Carrera Coupé, type 996 first series (MY1998–2001).

Primary reference: the-blueprints.com #765 "Porsche 911 Carrera 4 (1998)" 4-view
line drawing (contributor Janne Kaasalainen), research/blueprints/11-996-1-1998/
tbp-765_porsche-911-carrera-4-1998_4view.gif (1320x1350 px): top view (nose left),
side view (car's left side, nose left), front and rear views. The Carrera 4 body is
the narrow Carrera body (research/geometry.json: "Carrera 4 ... body identical").
Cross-checks: vendor 4-view vec-1888 (same folder) and the photos in
research/photos/11-996-1-1998/ (01 Porsche AG studio side profile, 07/08 front,
10 rear, 13/14 front 3/4, 20 headlamp detail).

Official figures (research/specs.json → 11-996-1-1998.dimensions_mm / tyres):
  L 4430, W 1765, H 1305, WB 2350, tracks 1455 / 1500 mm,
  tyres 205/50 ZR 17 front, 255/40 ZR 17 rear, wheels 7J / 9J x 17.

Calibration (sheet pixels; every view calibrated on its own):
  The sheet's views are drawn ~2.5 % short in length relative to their widths and
  heights (the vendor 4-view vec-1888 shows the same: L/W 2.44 vs official 2.51),
  so each axis is calibrated separately against the official figures.
  SIDE  x: axle tick lines under the hubs at x = 328.0 / 989.0 px → 661 px = 2350 mm
           (3.555 mm/px). Bumper extremes (front plate excluded) 48.5 / 1282.0 px give
           4386 mm (-1.0 %); the 44 mm are spread over both overhangs (+2.2 %) so the
           official length and wheelbase both hold.
        y: tyre contact y = 942, roof top y = 566 → 376 px = 1305 mm (3.471 mm/px).
           Check: tyre outline radius 92 px → Ø 639 mm vs 637 mm for 205/50 R17.
  TOP   same x mapping (nose 49 / tail 1282 px agree with the side view); centre line
        per column (295.5 → 297.5 px); widths: max plan width 507 px = 1765 mm.
  FRONT centre x 418.5, body 165.5..672.5 px = 1765 mm (3.481 mm/px); ground 1321,
        roof 954 → 3.556 mm/px vertically. Check: lamp bottom 0.565 m vs 0.555 m in
        the side view.
  REAR  centre x 953, body 699..1207 px = 1765 mm (3.474 mm/px); vertical is fitted
        through ground 1326, the lamp-bottom/bumper line 1134 (0.659 m from the side
        view) and the roof 957 (1.305 m).
Heights of features visible in the side view are taken from the side view; the end
views supply z (half-widths) and front/rear-only features.

Run: <venv>/python research/traces/11-996-1-1998.py
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

STOP = "11-996-1-1998"
SHEET = os.path.join(ROOT, "research", "blueprints", STOP, "tbp-765_porsche-911-carrera-4-1998_4view.gif")
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------ official figures
L, W, H, WB = 4.430, 1.765, 1.305, 2.350          # specs.json dimensions_mm
TRACK_F, TRACK_R = 1.455, 1.500                    # specs.json track_front / track_rear
RIM = 17 * 0.0254                                  # 17-inch rims
TYRE_F = RIM + 2 * 0.205 * 0.50                    # 205/50 ZR 17 → 0.6368 m
TYRE_R = RIM + 2 * 0.255 * 0.40                    # 255/40 ZR 17 → 0.6358 m

# ------------------------------------------------------------------ side calibration
FA_PX, RA_PX = 328.0, 989.0        # axle tick lines (hub centres)
TIP_PX, TAIL_PX = 48.5, 1282.0     # bumper extremes, plate excluded
GROUND_PY, ROOF_PY = 942.0, 566.0  # tyre contact line, roof top
SX = WB / (RA_PX - FA_PX)                                   # m/px along the car
K_OH = (L - WB) / ((FA_PX - TIP_PX + TAIL_PX - RA_PX) * SX)  # overhang stretch (1.022)
FA = (FA_PX - TIP_PX) * SX * K_OH
RA = FA + WB
SY = H / (GROUND_PY - ROOF_PY)                               # m/px vertical


def X(px):
    """Sheet x (side/top views) → car x (m from the front tip)."""
    if px <= FA_PX:
        return round((px - TIP_PX) * SX * K_OH, 4)
    if px <= RA_PX:
        return round(FA + (px - FA_PX) * SX, 4)
    return round(RA + (px - RA_PX) * SX * K_OH, 4)


def X_inv(x):
    if x <= FA:
        return TIP_PX + x / (SX * K_OH)
    if x <= RA:
        return FA_PX + (x - FA) / SX
    return RA_PX + (x - RA) / (SX * K_OH)


def Y(py):
    """Side-view sheet y → height (m)."""
    return round((GROUND_PY - py) * SY, 4)


def pts(points):
    return [[X(px), Y(py)] for px, py in points]


# ------------------------------------------------------------------ top calibration
SZ = W / 507.0                      # m/px across the car (max plan width 507 px)


def top_centre(px):
    # Centre line of the plan view, fitted to column midpoints (295.5 px at x=100 →
    # 297.5 px at x=1100; the scan is tilted by 2 px).
    return 295.3 + (px - 100) * 0.0021


def Zt(px, py):
    """Top-view sheet point → half-width z (m)."""
    return round(abs(py - top_centre(px)) * SZ, 4)


# ------------------------------------------------------------------ front / rear calibration
F_CX, F_SZ, F_GROUND, F_SY = 418.5, W / 507.0, 1321.0, H / (1321.0 - 954.0)
R_CX, R_SZ = 953.0, W / 508.0
R_ANCH = [(957.0, H), (1134.0, 0.659), (1326.0, 0.0)]      # rear view py → height


def Zf(px):
    return round(abs(px - F_CX) * F_SZ, 4)


def Yf(py):
    return round((F_GROUND - py) * F_SY, 4)


def Zr(px):
    return round(abs(px - R_CX) * R_SZ, 4)


def Yr(py):
    ys = [a for a, _ in R_ANCH]
    hs = [b for _, b in R_ANCH]
    return round(float(np.interp(py, ys, hs)), 4)


# ------------------------------------------------------------------ side silhouette (auto)
from PIL import Image  # noqa: E402  (OpenCV cannot read GIF)

sheet_rgb = np.array(Image.open(SHEET).convert("RGB"))
gray = cv2.cvtColor(sheet_rgb, cv2.COLOR_RGB2GRAY)

side = silhouette_from_drawing(gray, (15, 562, 1300, 948), close=3, thresh=160)
prof = column_profile(side)
top_px = {x: t for x, (t, b) in prof.items() if TIP_PX <= x <= TAIL_PX}
# Wiper pivot on the cowl (x 436..468) pokes above the scuttle line: bridge it.
for a, b in ((436, 470),):
    ya, yb = top_px[a], top_px[b]
    for x in range(a, b + 1):
        top_px[x] = ya + (yb - ya) * (x - a) / (b - a)
silhouette_top = [[X(x), Y(v)] for x, v in sorted(top_px.items()) if x % 3 == 0]

# ------------------------------------------------------------------ plan half-width (auto)
plan = silhouette_from_drawing(gray, (20, 30, 1300, 562), close=3, thresh=160)
pprof = column_profile(plan)
half_px = {x: (b - t) / 2 for x, (t, b) in pprof.items() if TIP_PX <= x <= TAIL_PX}
# Door mirrors stick out at x 560..616: interpolate the body line under them.
for a, b in ((558, 620),):
    ha, hb = half_px[a], half_px[b]
    for x in range(a, b + 1):
        half_px[x] = ha + (hb - ha) * (x - a) / (b - a)
# The front plate (x < 49) is not body.
half_width = [[X(x), round(h * SZ, 4)] for x, h in sorted(half_px.items()) if x % 4 == 0 and x >= 50]


# ------------------------------------------------------------------ wheel arches (auto, radial)
def arch(cx, cy, a0, a1, skip=()):
    """Outer fender-lip line of a wheel arch: outermost dark line 100..124 px from the hub."""
    g = cv2.GaussianBlur(gray.astype(float), (3, 3), 0.7)
    out = []
    for a in np.arange(a0, a1 - 0.1, -2.0):
        if any(s0 <= a <= s1 for s0, s1 in skip):
            continue
        t = math.radians(a)
        best = None
        for r in np.arange(100, 124, 0.25):
            x = cx + r * math.cos(t)
            y = cy - r * math.sin(t)
            if g[int(round(y)), int(round(x))] < 200:
                best = r
        if best is not None:
            out.append((a, best))
    # median-smooth the radius
    rs = np.array([r for _, r in out])
    sm = [float(np.median(rs[max(0, i - 3):i + 4])) for i in range(len(rs))]
    return [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for (a, _), r in zip(out, sm)]


# 136..150° on the front arch hit the side marker, 46..54° on the rear arch the lid line.
ARCH_F = arch(FA_PX, 849, 186, -6, skip=((135, 151), (-12, -3)))
ARCH_R = arch(RA_PX, 849, 186, -6, skip=((46, 55), (182, 190)))

# ------------------------------------------------------------------ hand-read lines (side view px)
# Lower edge: nose → front apron → front arch → sill → rear arch → rear apron → tail.
BOTTOM = [(48.5, 822), (50, 838), (57, 846), (60, 856), (62, 864), (65, 873), (72, 880), (100, 883),
          (140, 887), (170, 891), (219, 892), (220, 872)] + ARCH_F + \
         [(447, 872), (448, 893), (600, 893), (760, 893), (872, 893), (873, 872)] + ARCH_R + \
         [(1106, 870), (1110, 875), (1150, 869), (1200, 861), (1220, 856), (1235, 847), (1250, 839),
          (1262, 832), (1271, 818), (1277, 800), (1282, 780)]
bottom = sorted(pts(BOTTOM))

# Windscreen side edge (A-pillar outer line, side view), cowl → roof.
APILLAR = [(498, 688), (506, 682), (515, 676), (523, 670), (531, 664), (542, 658), (548, 652), (557, 646),
           (567, 640), (576, 634), (586, 628), (595, 622), (603, 616), (610, 606), (614, 598)]
# Side glass (DLO): door glass, lowest-front point first, clockwise in the side view.
DLO_DOOR = [(527, 693), (532, 688), (541, 682), (552, 676), (564, 664), (575, 655), (587, 646), (598, 640),
            (608, 634), (617, 628), (626, 622), (635, 616), (647, 610), (665, 604), (680, 601), (695, 598),
            (725, 596), (755, 597), (785, 599), (815, 604), (828, 606), (822, 632), (815, 660), (808, 690)]
# (front edge taken at the door glass's rear edge: the B-pillar trim between the two
# windows is black and reads as part of the glasshouse)
DLO_QUARTER = [(808, 690), (828, 606), (851, 609), (875, 618), (905, 626), (935, 632), (965, 646), (995, 657), (1006, 664),
               (1008, 669), (1000, 675), (965, 677), (935, 678), (905, 680), (860, 683)]
BELT_CABIN = [(527, 693), (600, 692), (700, 692), (808, 691), (860, 682), (935, 678), (980, 676)]
RAIL_CABIN = [(614, 598), (650, 606), (680, 597), (725, 592), (785, 594), (830, 600), (875, 612), (935, 628),
              (995, 652), (1010, 664)]
# Door shut line (front edge down, sill, rear edge up to the belt).
DOOR = [(505, 696), (487.5, 712), (473.5, 728), (468.5, 744), (467.5, 768), (469.5, 800), (473.5, 824),
        (478.5, 848), (486, 855), (600, 856), (720, 856), (738, 848), (762.5, 832), (778, 816), (790.5, 800),
        (801.5, 784), (810.5, 768), (818.5, 752), (825, 736), (825.5, 720), (818.5, 704), (812, 696)]
HANDLE = [(760, 742), (758, 736), (765, 729), (790, 727), (812, 730), (814, 740), (808, 745), (770, 745)]
SHOULDER = [(215, 738), (300, 728), (400, 718), (480, 713), (600, 713), (800, 713), (900, 712), (1000, 714),
            (1100, 718), (1140, 722)]   # faint shoulder highlight line on wing, door and rear wing
REAR_HIP = [(960, 683), (1050, 690), (1140, 697)]   # rear wing top edge beside the engine lid
TAIL_SIDE = [(1148, 750), (1141, 735), (1146, 726), (1162, 719), (1190, 714), (1220, 712), (1240, 714),
             (1252, 728), (1260, 744), (1264, 752), (1200, 752)]   # wrap-around part of the tail lamp
SIDE_MARKER = [(205, 783), (205, 774), (255, 772), (258, 778), (255, 784)]   # amber marker/repeater in the bumper
MIRROR_PX = (552, 602, 661, 690)   # housing extent in the side view (x0, x1, y0, y1); base triangle 532..552
# Amber indicator band of the headlamp unit where it wraps round the wing (photo 01: x 0.20..0.34 m,
# y 0.56..0.60 m; drawing: lamp front-lower end (87..125, 770..784) px).
INDICATOR_SIDE = [(87, 784), (92, 774), (125, 766), (128, 772), (122, 779)]
# Porsche crest on the front lid (geometry.json 11: carried over from the 993); plan view emblem
# at x 115..132 px, 18 px across (≈ 0.06 m).
CREST_T = [(115, 296.4), (115, 287.5), (132, 287.5), (132, 296.4)]

# ------------------------------------------------------------------ hand-read lines (top view px)
WINDSCREEN_T = [(455, 296), (458, 196), (466, 136), (475, 100), (600, 125), (605, 196), (606, 296)]
REAR_WINDOW_T = [(918, 297), (918, 175), (925, 162), (960, 158), (1050, 160), (1090, 166), (1097, 180), (1098, 297)]
HOOD_EDGE_T = [(91, 296), (93, 260), (98, 225), (108, 192), (122, 192), (200, 178), (280, 156), (360, 126),
               (420, 106), (478, 96)]   # front lid shut line (centre front → windscreen corner)
LID_EDGE_T = [(1100, 297), (1100, 166), (1150, 171), (1200, 176), (1245, 180), (1247, 297)]
GRILLE_T = [(1162, 297), (1162, 187), (1222, 187), (1222, 297)]   # louvred engine-lid grille
LAMP_T = (93, 215)   # headlamp unit plan extent in x

# ------------------------------------------------------------------ hand-read lines (front / rear view px)
LAMP_F = [(218, 1122), (225, 1108), (235, 1101), (248, 1098), (262, 1100), (275, 1106), (287, 1113), (297, 1122),
          (306, 1130), (313, 1138), (318, 1146), (320, 1150)]   # unit above the indicator band (image-left lamp)
LAMP_F_BOTTOM = [(320, 1150), (226, 1150), (220, 1140), (217, 1130)]
# Front/rear outlines follow the point order used by every stop's boxes: start at the
# inner-bottom corner, go up, outward along the top, down, and back along the bottom.
INDICATOR_F = [(310, 1161), (320, 1153), (320, 1150), (226, 1150), (230, 1156), (240, 1160),
               (270, 1162)]   # amber indicator band along the bottom of the unit (MY1998)
# Intakes (drawing front view; photo 07 confirms the layout): upper outer openings, a
# body-colour blade, and a full-width lower opening. Split into the same three slots as the
# later stops: outer part (z ≥ 0.24 m), centre part, blade (photo 07: y 872–878 px → 0.355–
# 0.362 m with the lamp-span calibration described in 12-996-2-2002.py; drawing notch 1219–1224).
INTAKE_F = [(350, 1242), (350, 1224), (342, 1219), (344, 1212), (338, 1206), (255, 1205), (242, 1207), (238, 1215),
            (240, 1226), (250, 1236), (262, 1240)]
INTAKE_MID_F = [(418.5, 1242), (418.5, 1225), (350, 1224), (350, 1242)]
INTAKE_BAR_F = [(346, 1223), (346, 1219), (244, 1219), (240, 1223)]
# Tail lamp (rear view, drawing outline; segment layout from photos 01/22/23/10):
# upper indicator band, red lower band with a clear reversing square near mid-length.
TAIL_R = [(840, 1134), (839, 1100), (836, 1092), (820, 1094), (790, 1096), (760, 1099), (742, 1104), (733, 1115),
          (733, 1134)]


def tail_split(px):
    """Upper/lower band division: 50 % of the lamp height (photo 10), tilted with the lamp top."""
    return 1113 + (840 - px) * 8 / 107


REV = (778, 790)   # reversing-light square (drawing: clear square x 778..790 px)
TAIL_LOWER = [(840, 1134), (840, tail_split(840)), (REV[1], tail_split(REV[1])), (REV[1], 1131), (REV[0], 1131),
              (REV[0], tail_split(REV[0])), (733, tail_split(733)), (733, 1134)]
TAIL_UPPER = [(840, tail_split(840)), (839, 1100), (836, 1092), (820, 1094), (790, 1096), (760, 1099), (742, 1104),
              (733, 1115), (733, tail_split(733))]
REVERSE_R = [(REV[1], 1131), (REV[1], tail_split(REV[1])), (REV[0], tail_split(REV[0])), (REV[0], 1131)]
PLATE_R = [(953, 1211), (953, 1183), (886, 1183), (886, 1211)]   # plate in the apron recess (EU, as drawn)
PLATE_F = [(418.5, 1222), (418.5, 1188), (345, 1188), (345, 1222)]   # front plate below the lid (EU)
# "Carrera" script on the lid (drawing: x 916..990 px → 0.26 m wide; photo 10: ≈0.27 m, black):
# a thin band at the script's mid-height stands for the lettering at pixel-art scale.
BADGE_R = [(953, 1109), (953, 1104), (953 - 38, 1104), (953 - 38, 1109)]
EXHAUST_R = (808, 1239, 13)   # tailpipe centre + radius (px)

# ------------------------------------------------------------------ end-view section widths (m)
# Glasshouse half-widths from the front/rear view outlines (px → m):
#   front view y 970/1000/1040 → 1.248/1.141/1.000 m high, half-width 0.515/0.568/0.655
#   rear  view y 968/998/1028  → 1.27/1.16/1.05 m high,  half-width 0.500/0.583/0.643
ROOF_RAIL_Z = 0.505      # top of the side glass (plan view: glass top edge 137-140 px off centre)
BELT_Z = 0.700           # side-glass base (plan: glass outer edge 200 px off centre)
SHOULDER_Z = 0.80        # door shoulder under the glass
WINDSCREEN_BASE_Z = Zt(475, 100)   # 0.68
WINDSCREEN_TOP_Z = Zt(600, 125)    # 0.59
REAR_WINDOW_Z = Zt(960, 158)       # 0.485 (frame outer edge)
LID_EDGE_Z_FRONT = Zt(1100, 166)   # 0.458
LID_EDGE_Z_REAR = Zt(1245, 180)    # 0.41
HIP_CREST_Z = 0.78       # rear wing crest (rear view: 0.806 at 0.84 m, 0.842 at 0.81 m)

# ------------------------------------------------------------------ headlamp
# The 'fried egg' unit lies almost flat along the top of the wing. Its lens plane is
# fixed by three points identified in all three views (car coords, x rearward):
#   A inner-front corner   plan (92,196)   front (320,1150)
#   B outer-front corner   plan (125,105)  front (222,1145)   (z: mean of plan and front)
#   C top/rear of the round main lens  side (213,718)  front (248,1098)  plan (214,125)
LAMP_A = np.array([X(92), Yf(1150), (Zt(92, 196) + Zf(320)) / 2])
LAMP_B = np.array([X(125), Yf(1145), (Zt(125, 105) + Zf(222)) / 2])
LAMP_C = np.array([X(213), (Y(718) + Yf(1098)) / 2, (Zf(248) + Zt(214, 125)) / 2])
n = np.cross(LAMP_B - LAMP_A, LAMP_C - LAMP_A)
n = n / np.linalg.norm(n)
if n[1] < 0:
    n = -n
# n = (x rearward, up, outboard). Renderer axis: (cos yaw cos p fwd, sin p up, sin yaw cos p out).
PITCH = round(math.degrees(math.atan2(n[1], math.hypot(n[0], n[2]))), 1)
YAW = round(math.degrees(math.atan2(n[2], -n[0])), 1)
p_, y_ = math.radians(PITCH), math.radians(YAW)
U_HAT = np.array([-math.sin(y_), 0.0, -math.cos(y_)])                                  # fwd + inboard
V_HAT = np.array([math.sin(p_) * math.cos(y_), math.cos(p_), -math.sin(p_) * math.sin(y_)])  # up the slope


def on_lamp_plane(z, y):
    """3D point of the lamp plane seen at (z, y) in the front view."""
    x = LAMP_A[0] + (n[1] * (y - LAMP_A[1]) + n[2] * (z - LAMP_A[2])) / (-n[0])
    return np.array([x, y, z])


# Front-view outline of the unit above the amber indicator band (image-left lamp: u =
# image-right = inboard); lifted onto the plane and expressed in the lens plane, so the
# rendered lamp projects back onto the traced front-view outline.
lamp_poly = LAMP_F + LAMP_F_BOTTOM
lamp3 = np.array([on_lamp_plane(Zf(px), Yf(py)) for px, py in lamp_poly])
lamp_c = lamp3.mean(axis=0)
outline = [[round(float(np.dot(p - lamp_c, U_HAT)), 4), round(float(np.dot(p - lamp_c, V_HAT)), 4)]
           for p in lamp3]
lamp_x, cy, cz = (float(v) for v in lamp_c)
HEADLIGHT = {
    "centre": [round(lamp_x, 4), round(cy, 4), round(cz, 4)],
    "outline": outline,
    "yaw": YAW,
    "pitch": PITCH,
    # Clear lens edge / thin grey surround (photo 20: no chrome ring).
    "ring": 0.006,
    "ringColor": "#b9bfc4",
    "ringFinish": "satin",
    "lensColor": "#dfe6ea",
    "graphic": "projector",
}

# Lamp edges on the traced plane, sorted by x (lamp3 order: 0-2 outer rear, 3 top, 4-11 inner
# edge down to the inner-front corner, 12 corner, 13-15 outer front).
LAMP_INNER = sorted(lamp3[3:12].tolist())
LAMP_OUTER = sorted(lamp3[[13, 14, 15, 0, 1, 2, 3]].tolist())


# ------------------------------------------------------------------ assemble the section curves
FA_, RA_ = FA, RA
cowl_x = X(447)            # windscreen base on the centre line (side & plan)
roof_front_x = X(612)      # windscreen top / roof front
x_lid_front = X(91)        # front lid leading edge on the centre line (plan)


def sil(x):
    return float(np.interp(x, [p[0] for p in silhouette_top], [p[1] for p in silhouette_top]))


# Hood centre line: lid edge height from the front view (0.633 m at y 1143) matches the
# side silhouette at the lid edge; it rises to the scuttle (0.881 m, where the windscreen
# centre line meets the cowl in the side view; front view 0.885 m), staying below the
# wing crests (photos 13/14: the wings stand proud of the lid beside the lamps).
h_lid, h_cowl = sil(x_lid_front) + 0.015, sil(cowl_x)
hood = []
for t in np.linspace(0, 1, 12):
    x = x_lid_front + (cowl_x - x_lid_front) * t
    h = h_lid + (h_cowl - h_lid) * (1 - (1 - t) ** 1.45)
    if t < 0.95:
        h = min(h, sil(x) - 0.03 * (1 - t))
    hood.append([round(x, 4), round(h, 4)])
nose = [p for p in silhouette_top if p[0] < x_lid_front]
cabin_top = [p for p in silhouette_top if p[0] > cowl_x + 0.02]
top_y = nose + hood + cabin_top


def pw(x):
    """Plan half-width at x (m)."""
    return float(np.interp(x, [p[0] for p in half_width], [p[1] for p in half_width]))


# Nose (ahead of the lamps, x < 0.15 m): the bumper face is broad in plan (0.32 m half-
# width 35 mm behind the tip, 0.50 m at 0.1 m), so the upper section points are spread
# across it instead of converging on the centre line.
NOSE = [X(58), X(70), X(80)]

# Fender crest (P3). Front wing: the shoulder where the broad wing top turns down into
# the side. Plan view: a feature line 2–5 cm inside the outline, z 0.738 (x 0.45 m) →
# 0.766 (0.52) → 0.787 (0.88) → 0.81 (1.09) → 0.818 (1.31 m); side view: the matching
# shoulder highlight (SHOULDER, y 0.708 at x 0.62 → 0.795 at 1.57 m). Ahead of that the
# shoulder runs just outside the lamp's outer edge (3D lamp outline: (0.24, 0.608, 0.67),
# (0.32, 0.644, 0.69), (0.40, 0.679, 0.70), (0.46, 0.708, 0.70)) and round the bumper
# corner. Then the door shoulder, the rear-wing crest and down to the tail-lamp top.
FRONT_CREST = [  # (x m, z m, y m)
    (X(100) - 0.03, 0.57, 0.575), (0.24, 0.69, 0.597), (0.32, 0.715, 0.632), (0.40, 0.73, 0.664),
    (0.46, 0.742, 0.688), (0.52, 0.766, 0.70), (X(215), 0.775, Y(738)), (X(300), 0.787, Y(728)),
    (1.09, 0.81, 0.762), (X(400), 0.818, Y(718)), (X(480), 0.818, Y(713))]
crest = [[0.0, Y(822)]] + [[x, round(sil(x) - 0.03, 4)] for x in NOSE] + [[x, y] for x, _, y in FRONT_CREST]
crest += pts([(700, 713), (900, 712)]) + pts(REAR_HIP) + pts([(1200, 712), (1250, 725), (1275, 760), (1282, 780)])
# (capped 12 mm inside the plan outline: at x ≈ 0.24 m the lamp's outer-front corner is
# right at the outline, so the shoulder cannot sit outboard of it there)
crest_z = [[0.0, 0.0]] + [[x, round(0.87 * pw(x), 4)] for x in NOSE] + \
          [[x, round(min(z, pw(x) - 0.012), 4)] for x, z, _ in FRONT_CREST] + \
          [[X(700), 0.815], [X(900), 0.815], [X(960), HIP_CREST_Z],
           [X(1140), 0.75], [X(1230), 0.66], [X(1270), 0.45], [L, 0.0]]

# Belt: lid side edge ahead of the windscreen (a touch below the hood surface), side-glass
# base in the cabin, engine-lid side edge behind the rear window.
belt = [[0.0, Y(822)]] + [[x, round(sil(x) - 0.012, 4)] for x in NOSE]
# In the lamp zone the wing top follows the lamp plane: P4 rides on the lamp's inner edge
# (the lid shut line meets it there, photo 18), so the flat 'fried egg' lies on the loft.
LAMP_ZONE = (LAMP_INNER[1][0], LAMP_INNER[-2][0])   # x 0.19 .. 0.587 m
belt += [[x, round(y - 0.02, 4)] for x, y in hood if X(100) < x < LAMP_ZONE[0] - 0.02 or x > LAMP_ZONE[1] + 0.07]
belt += [[round(x, 4), round(y - 0.004, 4)] for x, y, z in LAMP_INNER[1:-1]]
belt += pts(BELT_CABIN)
belt += pts([(1060, 688), (1100, 686), (1150, 684), (1200, 686)]) + pts([(1250, 725), (1275, 760), (1282, 780)])
belt_z = [[0.0, 0.0]] + [[x, round(0.62 * pw(x), 4)] for x in NOSE] + \
         [[round(x, 4), round(z, 4)] for x, y, z in LAMP_INNER[1:-1]] + \
         [[X(px), Zt(px, py)] for px, py in HOOD_EDGE_T[5:] if X(px) > LAMP_ZONE[1] + 0.07] + \
         [[X(527), BELT_Z], [X(808), BELT_Z], [X(980), BELT_Z - 0.03], [X(1060), 0.55],
          [X(1100), LID_EDGE_Z_FRONT], [X(1245), LID_EDGE_Z_REAR], [X(1272), 0.3], [L, 0.0]]

# Roof rail: collapses onto the hood ahead of the screen, follows the A-pillar, the glass
# top, the rear-window side edge and collapses onto the engine lid.
rail = [[0.0, Y(822)]] + [[x, round(sil(x) - 0.004, 4)] for x in NOSE]
rail += [[x, round(y - 0.004, 4)] for x, y in hood if x > X(100)]
rail += pts(APILLAR) + pts(RAIL_CABIN)
rail += pts([(1060, 675), (1100, 682), (1150, 683), (1200, 687)]) + pts([(1250, 725), (1275, 760), (1282, 780)])
roof_z = [[0.0, 0.0]] + [[x, round(0.33 * pw(x), 4)] for x in NOSE] + \
         [[X(108), 0.2], [cowl_x, 0.36], [X(498), WINDSCREEN_BASE_Z - 0.03],
          [X(614), WINDSCREEN_TOP_Z - 0.06], [X(700), ROOF_RAIL_Z], [X(900), ROOF_RAIL_Z - 0.01],
          [X(1010), REAR_WINDOW_Z], [X(1100), LID_EDGE_Z_FRONT - 0.05], [X(1245), 0.3], [X(1272), 0.2], [L, 0.0]]

# Widest point height (front/rear views): bumper corners, wing at hub height, door,
# rear wing at the lamp-bottom line.
side_y = [[0.0, Y(822)], [X(60), 0.43], [X(140), 0.45], [FA_, 0.50], [X(470), 0.53], [X(800), 0.55],
          [RA_, 0.62], [X(1180), 0.63], [X(1250), 0.62], [L, Y(780)]]


def bot(x):
    return float(np.interp(x, [p[0] for p in bottom], [p[1] for p in bottom]))


# Underside on the centre line, ~0.12 m under the cabin (ground clearance 100–110 mm,
# geometry.json). At the nose (x < 0.085 m) and the tail (x > 4.30 m) the side
# silhouette's lower edge is the centre-line profile of the bumper faces curving under,
# so there floorY IS that edge and the rocker point P1 sits just above it and well inboard
# (the renderer paints the P0→P1 segment as underbody: kept to a thin dark strip, which
# is the black lower lip seen in photos 01/07). Elsewhere the floor stays 20–30 mm under
# the bumper/sill edge (photo 01: black lip under the body-colour apron).
NOSE_END, TAIL_START = X(72), X(1250)
floor_y = [[X(px), round(bot(X(px)), 4)] for px in (48.5, 50, 57, 60, 62, 65, 72)] + \
          [[X(100), round(bot(X(100)) - 0.025, 4)], [FA_ - 0.25, 0.17], [FA_, 0.15], [FA_ + 0.5, 0.12],
           [RA_ - 0.35, 0.12], [RA_, 0.14], [RA_ + 0.45, 0.2]] + \
          [[X(px), round(bot(X(px)) - 0.025, 4)] for px in (1150, 1200, 1235)] + \
          [[X(px), round(bot(X(px)), 4)] for px in (1250, 1262, 1271, 1277, 1282)]
bottom = [[x, round(y + 0.012, 4)] if (x <= NOSE_END or x >= TAIL_START) else [x, y] for x, y in bottom]


# Rocker / arch-edge z: under the arches the lip sits at the wing's outer surface; the
# sill tucks in ~45 mm below the door belly; at the nose/tail P1 moves inboard (see above).
def near_arch(x):
    return abs(x - FA_) < 0.40 or abs(x - RA_) < 0.42


def rocker_frac(x):
    """P1 as a fraction of the half-width where the bumper faces curve under (nose/tail):
    the bumper bottoms are flat across the width (photos 07/10), so P1 stays wide."""
    if x <= NOSE_END:
        return 0.8
    if x <= X(100):
        return 0.8 + 0.13 * ((x - NOSE_END) / (X(100) - NOSE_END))
    if x >= TAIL_START:
        return 0.8
    if x >= X(1235):
        return 0.93 - 0.13 * ((x - X(1235)) / (TAIL_START - X(1235)))
    return None


rocker_z = []
for x, z in half_width:
    f = rocker_frac(x)
    rocker_z.append([x, round(max(0.0, z * f if f is not None else z - (0.012 if near_arch(x) else 0.045)), 4)])

body = {
    "floorY": floor_y,
    "rockerY": simplify(bottom, 0.002),
    "rockerZ": simplify(rocker_z, 0.003),
    "sideY": side_y,
    "sideZ": simplify(half_width, 0.002),
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
        x = min(max(x, 0.0), L)
        if out and x <= out[-1][0] + 1e-4:
            out[-1][1] = round((out[-1][1] + v) / 2, 4)
        else:
            out.append([round(x, 4), round(v, 4)])
    body[k] = out

# Seat the wing on the flat lamp: over the lamp's length the section passes through the
# lamp's inner edge (belt) and outer edge (crest) on the lens plane, and the lid centre stays
# just above the inner edge — otherwise the renderer's raycast placement pushes the lamp out
# of the wing (see 11-996-1-1998.lampseat.py).
import importlib.util  # noqa: E402

_ls = importlib.util.spec_from_file_location("lampseat", os.path.join(HERE, f"{STOP}.lampseat.py"))
lampseat = importlib.util.module_from_spec(_ls)
_ls.loader.exec_module(lampseat)
LAMP_SEAT = lampseat.seat(body, HEADLIGHT)

# The Catmull-Rom section bulges beyond P2 (up to ~2 cm where the rocker/arch lip P1 sits
# close to P2 and the floor centre P0 pulls its tangent outward). Pull sideZ in so the
# lofted plan outline matches the traced one: iterate on the dense traced half-width
# (every 4 px ≈ 1.5 cm), then simplify and check the remaining error on a dense grid.
def pw_target(x):
    return float(np.interp(x, [p[0] for p in half_width], [p[1] for p in half_width]))


dense = [[x, z] for x, z in half_width if 0 < x < L]
body["sideZ"] = [[0.0, 0.0]] + dense + [[L, 0.0]]
for _ in range(4):
    body["sideZ"] = [[x, round(max(z - (max(p[0] for p in half_section(body, x)) - pw_target(x)), 0.0), 4)]
                     if 0 < x < L else [x, z] for x, z in body["sideZ"]]
body["sideZ"] = simplify(body["sideZ"], 0.0015)
for _ in range(2):
    body["sideZ"] = [[x, round(max(z - (max(p[0] for p in half_section(body, x)) - pw_target(x)), 0.0), 4)]
                     if 0 < x < L else [x, z] for x, z in body["sideZ"]]
WIDTH_ERR = max(abs(max(p[0] for p in half_section(body, x)) - pw_target(x)) for x in np.linspace(0.05, L - 0.05, 400))

# ------------------------------------------------------------------ decals
def side_decal(id_, points, finish, color, kind="fill", **kw):
    # Long outlines are thinned (Douglas-Peucker, 4 mm): a morph pair shares a 40-decal /
    # 1024-point budget and every slot is resampled to twice the larger point count.
    p = pts(points)
    if len(p) > 10:
        p = simplify(p, 0.004)
    d = {"id": id_, "plane": "side", "kind": kind, "points": p, "finish": finish, "color": color}
    d.update(kw)
    return d


def top_pts(points):
    return [[X(px), Zt(px, py)] for px, py in points]


def front_pts(points):
    return [[Zf(px), Yf(py)] for px, py in points]


def rear_pts(points):
    return [[Zr(px), Yr(py)] for px, py in points]


GLASS = "#1c232a"
TRIM = "#16181a"
LENS_RED = "#b3201a"
AMBER = "#e8962a"

# Black seal/trim along the top of the glasshouse (A-pillar edge → roof seal → quarter
# window tip).
TRIM_LINE = DLO_DOOR[:20] + [(851, 609), (905, 626), (965, 646), (1006, 664), (1008, 669)]
# Fuel filler flap: right front wing only. Plan view: an oval drawn on the right wing only,
# x 358..420 px (1.13..1.35 m), z 0.75..0.83 m. Photo 03 (right side, hubs 1343.4/669.3 px →
# 286.9 px/m): outline x 1247..1311, y 624..651 px → centre x = FA + 0.225 m, y 0.789 m,
# 0.223 m long, 0.094 m tall as seen from the side (the flap faces up-and-out).
FLAP_C, FLAP_A, FLAP_B = (round(FA + (1343.4 - 1279) / 286.9, 4), 0.789), 0.111, 0.047
FLAP = [[round(FLAP_C[0] - FLAP_A * math.cos(a), 4), round(FLAP_C[1] - FLAP_B * math.sin(a), 4)]
        for a in np.linspace(math.pi / 2, math.pi / 2 - 2 * math.pi, 13)[:-1]]

decals = [
    side_decal("side-glass", DLO_DOOR, "glass", GLASS, depth=[0.45, 2], facing=0.3),
    side_decal("quarter-glass", DLO_QUARTER, "glass", GLASS, depth=[0.45, 2], facing=0.3),
    side_decal("window-trim", TRIM_LINE, "satin", TRIM, kind="line", width=0.012, depth=[0.45, 2], facing=0.3),
    side_decal("door-gap", DOOR, "satin", "#2a2a2a", kind="line", depth=[0.6, 2]),
    side_decal("door-handle", HANDLE, "satin", "#2a2a2a", kind="line", depth=[0.6, 2]),
    side_decal("side-marker", SIDE_MARKER, "lens", AMBER, depth=[0.55, 2], facing=0.3),
    side_decal("indicator-side", INDICATOR_SIDE, "lens", AMBER, depth=[0.55, 2], facing=0.25),
    side_decal("taillight-side", TAIL_SIDE, "lens", LENS_RED, depth=[0.55, 2], facing=0.35),
    {"id": "fuel-flap", "plane": "side", "kind": "line", "points": FLAP, "finish": "satin", "color": "#2a2a2a",
     "depth": [0.6, 2], "side": "right"},
]
decals += [
    {"id": "windscreen", "plane": "top", "kind": "fill", "points": top_pts(WINDSCREEN_T), "finish": "glass",
     "color": GLASS, "facing": 0.15, "depth": [0.8, 2]},
    {"id": "rear-window", "plane": "top", "kind": "fill", "points": top_pts(REAR_WINDOW_T), "finish": "glass",
     "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    {"id": "crest", "plane": "top", "kind": "fill", "points": top_pts(CREST_T), "finish": "chrome",
     "color": "#c9a24e", "facing": 0.3, "depth": [0.5, 1.0]},
    {"id": "hood-gap", "plane": "top", "kind": "line", "points": top_pts(HOOD_EDGE_T), "finish": "satin",
     "color": "#2a2a2a", "facing": 0.3, "depth": [0.5, 1.0]},
    {"id": "lid-gap", "plane": "top", "kind": "line", "points": top_pts(LID_EDGE_T), "finish": "satin",
     "color": "#2a2a2a", "facing": 0.3, "depth": [0.6, 1.2]},
    {"id": "engine-grille", "plane": "top", "kind": "fill", "points": top_pts(GRILLE_T), "finish": "paint",
     "color": "paint", "stripes": [round(6.5 * SX * K_OH, 4), 0.3], "facing": 0.3, "depth": [0.7, 1.2]},
    # Body-colour bumper faces: where the aprons curve under at the nose (x < 0.085 m) and
    # tail (x > 4.30 m) the renderer's underbody band would show from the front/rear; the
    # photos show paint down to the black lip (front 0.235 m, photo 07) and down to the
    # dark diffuser area (rear 0.30 m, drawing rear view y 1235 px / photo 10).
    {"id": "bumper-front-face", "plane": "front", "kind": "fill",
     "points": [[0.0, 0.235], [0.0, 0.44], [0.8, 0.44], [0.8, 0.235]], "finish": "paint", "color": "paint",
     "depth": [-0.05, 0.12], "facing": 0.2},
    {"id": "bumper-rear-face", "plane": "rear", "kind": "fill",
     "points": [[0.0, 0.30], [0.0, 0.64], [0.85, 0.64], [0.85, 0.30]], "finish": "paint", "color": "paint",
     "depth": [L - 0.2, L + 0.05], "facing": 0.2},
    {"id": "indicator-front", "plane": "front", "kind": "fill", "points": front_pts(INDICATOR_F), "finish": "lens",
     "color": AMBER, "depth": [-0.05, 0.5], "facing": 0.2},
    {"id": "intake-front", "plane": "front", "kind": "fill", "points": front_pts(INTAKE_F), "finish": "satin",
     "color": "#141516", "stripes": [0.012, 0.35], "depth": [-0.05, 0.45], "facing": 0.3},
    {"id": "intake-bar-front", "plane": "front", "kind": "fill", "points": front_pts(INTAKE_BAR_F), "finish": "paint",
     "color": "paint", "depth": [-0.05, 0.45], "facing": 0.3},
    {"id": "intake-front-centre", "plane": "front", "kind": "fill", "points": front_pts(INTAKE_MID_F),
     "finish": "satin", "color": "#1b1c1e", "stripes": [0.012, 0.35], "depth": [-0.05, 0.45], "facing": 0.3},
    {"id": "taillight", "plane": "rear", "kind": "fill", "points": rear_pts(TAIL_LOWER), "finish": "lens",
     "color": LENS_RED, "depth": [L - 0.45, L + 0.05], "facing": 0.25},
    # MY1998: amber indicator lenses (geometry.json 12 "MY1998 996 had yellow (amber)
    # indicator lenses, smoked from MY1999"; press photo 01 shows the orange upper band).
    {"id": "indicator-rear", "plane": "rear", "kind": "fill", "points": rear_pts(TAIL_UPPER), "finish": "lens",
     "color": "#e0762a", "depth": [L - 0.45, L + 0.05], "facing": 0.25},
    {"id": "reverse-light", "plane": "rear", "kind": "fill", "points": rear_pts(REVERSE_R), "finish": "lens",
     "color": "#eef1f2", "depth": [L - 0.45, L + 0.05], "facing": 0.25},
    {"id": "plate-rear", "plane": "rear", "kind": "fill", "points": rear_pts(PLATE_R), "finish": "satin",
     "color": "#e4e4df", "depth": [L - 0.3, L + 0.05], "facing": 0.4},
    {"id": "plate-front", "plane": "front", "kind": "fill", "points": front_pts(PLATE_F), "finish": "satin",
     "color": "#e4e4df", "depth": [-0.05, 0.3], "facing": 0.4},
    {"id": "badge-rear", "plane": "rear", "kind": "fill", "points": rear_pts(BADGE_R), "finish": "satin",
     "color": "#1d1e20", "depth": [L - 0.45, L + 0.05], "facing": 0.3},
]



car = {
    "id": STOP,
    "length": L,
    "frontAxle": round(FA, 4),
    "rearAxle": round(RA, 4),
    "trackFront": TRACK_F,
    "trackRear": TRACK_R,
    "body": body,
    "decals": decals,
    "wheels": {
        "front": {"diameter": round(TYRE_F, 4), "width": 0.205, "rim": round(RIM, 4), "design": "twist",
                  "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
        "rear": {"diameter": round(TYRE_R, 4), "width": 0.255, "rim": round(RIM, 4), "design": "twist",
                 "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
    },
    "headlight": HEADLIGHT,
    "mirror": {"at": [X((MIRROR_PX[0] + MIRROR_PX[1]) / 2), Y((MIRROR_PX[2] + MIRROR_PX[3]) / 2), Zf(215)],
               "size": [round((MIRROR_PX[1] - MIRROR_PX[0]) * SX, 3), round((MIRROR_PX[3] - MIRROR_PX[2]) * SY, 3),
                        round((215 - 157) * F_SZ, 3)],
               "shape": "aero", "color": "paint", "finish": "paint"},
    "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
    # One (oval) tailpipe each side (geometry.json 12: "two oval tailpipes, one at each outer
    # corner"; photos 10/11 show the same on the 996.1): rear view centre 145 px off the
    # centre line, side view pipe end at x 1250 px, 0.285 m high. The mesh is 0.12 m long.
    "exhausts": [[round(X(1250) - 0.05, 4), Y(859), s * Zr(EXHAUST_R[0]), round(EXHAUST_R[2] * R_SZ, 3)]
                 for s in (1, -1)],
}

with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
    json.dump(car, f, indent=1)


# ------------------------------------------------------------------ calibrated reference images
# check_car.py uses isotropic calibrations; the sheet's views are not isotropic, so each
# view is resampled into car space (3.5 mm/px) with the calibration above.
S = 0.0035


def warp(fn_src, x_range, y_range, name):
    """fn_src(xs, ys) → (px, py) arrays on the sheet for car-space grids."""
    xs = np.arange(x_range[0], x_range[1], S)
    ys = np.arange(y_range[1], y_range[0], -S)
    gx, gy = np.meshgrid(xs, ys)
    px, py = fn_src(gx, gy)
    img = cv2.remap(sheet_rgb, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR,
                    borderValue=(255, 255, 255))
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return os.path.relpath(path, ROOT), xs, ys


xinv = np.vectorize(X_inv)
side_img, sxs, sys_ = warp(lambda gx, gy: (xinv(gx), GROUND_PY - gy / SY), (-0.15, L + 0.15), (-0.05, 1.45),
                           "ref-side.png")
top_img, txs, tzs = warp(lambda gx, gz: (xinv(gx), top_centre(xinv(gx)) - gz / SZ), (-0.15, L + 0.15), (-1.05, 1.05),
                         "ref-top.png")
front_img, fzs, fys = warp(lambda gz, gy: (F_CX - gz / F_SZ, F_GROUND - gy / F_SY), (-1.05, 1.05), (-0.05, 1.45),
                           "ref-front.png")
r_py = np.vectorize(lambda h: float(np.interp(-h, [-b for _, b in R_ANCH], [a for a, _ in R_ANCH])))
rear_img, rzs, rys = warp(lambda gz, gy: (R_CX + gz / R_SZ, r_py(gy)), (-1.05, 1.05), (-0.05, 1.45), "ref-rear.png")


def col(xs, v):
    return float((v - xs[0]) / S)


def row(ys, v):
    return float((ys[0] - v) / S)


calib = {
    "side": {"image": side_img, "wheelF": [col(sxs, FA), row(sys_, TYRE_F / 2)],
             "wheelR": [col(sxs, RA), row(sys_, TYRE_F / 2)], "tipF": col(sxs, 0.0)},
    "top": {"image": top_img, "tipF": col(txs, 0.0), "tipR": col(txs, L), "centreY": row(tzs, 0.0)},
    "front": {"image": front_img, "centreX": col(fzs, 0.0), "groundY": row(fys, 0.0), "left": col(fzs, -W / 2),
              "right": col(fzs, W / 2), "width": W},
    "rear": {"image": rear_img, "centreX": col(rzs, 0.0), "groundY": row(rys, 0.0), "left": col(rzs, -W / 2),
             "right": col(rzs, W / 2), "width": W},
    # Porsche AG studio profile (photo 01, car's left side, long lens). Hub centres from a
    # circle fit to the rim edges: (492.8, 542.8) / (1356.0, 548.2) px → 367.3 px/m.
    # tipF puts the model's axles on the hubs (492.8 − FA·367.3); the flat overlay then
    # shows the centre-line ends ~2 % short / roof slightly high from perspective — see
    # check-side-photo-persp-*.png for the perspective-correct comparison.
    "side_photo": {"image": "research/photos/11-996-1-1998/01-side-left.jpg", "wheelF": [492.8, 542.8],
                   "wheelR": [1356.0, 548.2], "tipF": round(492.8 - FA * 367.3, 1), "crop": [100, 170, 1780, 680]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)



# ------------------------------------------------------------------ lamp check (placement as the renderer does it)
def lamp_hit(centre):
    """model.ts placeLamp: cast from centre + 0.5·axis back along the axis onto the loft."""
    axis = np.array([-math.cos(y_) * math.cos(p_), math.sin(p_), math.sin(y_) * math.cos(p_)])  # car coords
    start = np.array(centre) + 0.5 * axis
    for t in np.arange(0.0, 1.2, 0.001):
        q = start - t * axis
        sec = np.array(half_section(body, float(q[0])), np.float32)
        ring = np.concatenate([sec, sec[::-1] * np.array([-1, 1], np.float32)])
        if cv2.pointPolygonTest(ring.reshape(-1, 1, 2), (float(q[2]), float(q[1])), False) >= 0:
            return q + 0.004 * axis
    return np.array(centre)


LAMP_ORIGIN = lamp_hit([lamp_x, cy, cz])
lamp_world = [LAMP_ORIGIN + u * U_HAT + v * V_HAT for u, v in outline]


def draw_lamp(img_path, to_px, pts, out_path, box):
    from PIL import ImageDraw
    im = Image.open(os.path.join(ROOT, img_path)).convert("RGB")
    d = ImageDraw.Draw(im)
    q = [to_px(p) for p in pts]
    d.line(q + [q[0]], fill=(255, 40, 40), width=2)
    return im.crop(box)


panels = [
    draw_lamp(side_img, lambda p: (col(sxs, p[0]), row(sys_, p[1])), lamp_world, None,
              (int(col(sxs, -0.05)), int(row(sys_, 1.0)), int(col(sxs, 0.9)), int(row(sys_, 0.3)))),
    draw_lamp(top_img, lambda p: (col(txs, p[0]), row(tzs, p[2])), lamp_world, None,
              (int(col(txs, -0.05)), int(row(tzs, 0.95)), int(col(txs, 0.9)), int(row(tzs, 0.1)))),
    draw_lamp(front_img, lambda p: (col(fzs, -p[2]), row(fys, p[1])), lamp_world, None,
              (int(col(fzs, -0.95)), int(row(fys, 1.0)), int(col(fzs, -0.1)), int(row(fys, 0.3)))),
]
wsum = sum(pn.width for pn in panels)
sheet = Image.new("RGB", (wsum + 20, max(pn.height for pn in panels)), "white")
xo = 0
for pn in panels:
    sheet.paste(pn, (xo, 0))
    xo += pn.width + 10
sheet = sheet.resize((sheet.width * 2, sheet.height * 2))
sheet.save(os.path.join(OUT_DIR, "check-lamp.png"))

# ------------------------------------------------------------------ perspective photo checks
# The lofted car projected through a fitted pinhole camera onto three side photos (see
# 11-996-1-1998.photofit.py). Hubs from rim-edge circle fits. Set PHOTOCHECK=0 to skip.
PHOTO_CHECKS = [
    # file, front hub, rear hub, car box, facing, ground row cut, camera distance grid (m), ends
    ("01-side-left.jpg", (492.8, 542.8), (1356.0, 548.2), (120, 185, 1760, 665), "left", 648, (20, 26, 32, 40, 50), None),
    # 02 is filed as "side-right" but shows the car's LEFT side (nose left, no filler flap).
    ("02-side-right.jpg", (627.1, 829.1), (1412.2, 839.8), (290, 505, 1745, 940), "left", 920, (6, 8, 10, 13, 16), None),
    # 03: dark green car against foliage → GrabCut is poor; the bumper ends (hand-read at
    # 1567 / 414 px against the road) also constrain the camera distance.
    ("03-side-right.jpg", (1343.4, 772.7), (669.3, 766.9), (405, 490, 1580, 862), "right", 846,
     (4.5, 5.5, 6.5, 8, 10), (1567, 414)),
]
if os.environ.get("PHOTOCHECK", "1") == "1":
    import importlib.util

    spec = importlib.util.spec_from_file_location("photofit", os.path.join(HERE, f"{STOP}.photofit.py"))
    photofit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(photofit)
    for fname, hf, hr, box, facing, ground, dgrid, ends in PHOTO_CHECKS:
        st = photofit.check(car, os.path.join(ROOT, "research", "photos", STOP, fname), hf, hr, box,
                            os.path.join(OUT_DIR, f"check-side-photo-persp-{fname[:2]}.png"), facing=facing,
                            ground_row=ground, D_grid=dgrid, Y_grid=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ends=ends)
        print("photo", fname, st)

print("plan half-width max error after compensation (m):", round(float(WIDTH_ERR), 4))
_push, _depths = lampseat.placement(body, HEADLIGHT, half_section)
print("lamp seated over x", [round(v, 3) for v in LAMP_SEAT], "renderer placement pushes the lens out by (mm)",
      round(_push * 1000), "probe depths (mm)", [None if d is None else round(d * 1000) for d in _depths])
print("wrote", STOP, "L", L, "axles", round(FA, 4), round(RA, 4), "K_OH", round(K_OH, 4),
      "SX", round(SX * 1000, 3), "SY", round(SY * 1000, 3), "lamp pitch/yaw", PITCH, YAW,
      "lamp centre", [round(v, 3) for v in lamp_c], "placed at", [round(float(v), 3) for v in LAMP_ORIGIN])
