"""Trace: 13-997-1-2005 — 911 Carrera Coupé, type 997 first series (MY2005–2008).

References (research/blueprints/13-997-1-2005/, research/photos/13-997-1-2005/):
  SIDE   tbp-8809_porsche-911-carrera-s-2005_cutaway-side.gif (1085x337, Dr Dan Saranga):
         997.1 Carrera S — the same narrow shell as the Carrera. Orthographic side view
         (nose RIGHT); WB/L 567.5/1066 = 0.532 vs official 2350/4427 = 0.531, and circles of
         the official 235/40 R18 / 265/40 R18 tyres sit on its drawn tyres (ref-cutaway-cal.png).
         Used for the top silhouette (nose, wings, screen, roof, lid, tail), the nose/tail
         lower edges and the sill. The vendor 4-view vec-1030 puts the wheels ~5 cm too far
         back (overhangs 1.05/1.05 m vs 0.99/1.08 m here); photos 02 and 07 agree with the
         cutaway (see the .md).
  PHOTO  02-side-right.jpg (tracing: side; 2008 Carrera, long lens): arches, sill, door gap,
         side glass, handle, filler flap, marker, front light unit, head/tail-lamp side
         outlines — all within a few cm of the near wheel plane, mapped with the flat hub
         calibration. A camera fitted to the photo (research/traces/11-996-1-1998.photofit.py)
         is used only for the perspective check overlay.
  WINGS  07-side-right.jpg (Porsche Museum 997.1 C4S, long lens; same front body): front-
         wing crest heights (the cutaway's silhouette near the cowl is the centre cowl).
  PLAN   vec-1030 plan view: half-width outline, headlamp and tail-lamp plan extents, front
         lid shut line, engine-lid grille.
  FRONT  vec-1030 front view (+ photos 08, 21, 22 for shapes): lamp, light units, intakes.
  REAR   vec-1030 rear view (+ photos 11, 23): tail lamps, plate recess, tailpipes.
  ROOF   Porsche: "apart from the roof, every visible body part of the 997 is new"
         (geometry.json 13 body.roofline): the glasshouse z-values (windscreen, roof rail,
         side-glass base, rear window) are carried over from the 996.1 trace. (The vendor
         4-views disagree by ±4 cm on glass widths even between the 996.1 and 996 Turbo,
         which share that roof, so they are not used for it.)
Official figures (research/specs.json 13): L 4427, W 1808, H 1310, WB 2350, tracks
  1486/1534 mm, tyres 235/40 ZR 18 / 265/40 ZR 18 on 8J / 10J x 18.

Calibration (each view on its own):
  CUTAWAY hubs x 834.0 (front) / 266.5 (rear) → 567.5 px = 2350 mm (4.141 mm/px); body
          ends (line centres) 1073 / 7 → 4414 mm (−0.3 %): overhangs ×1.006 to hit 4427.
          Ground (tyre contact line) y 331, roof (line centre) y 12 → 1310 mm (4.107 mm/px).
  PLAN    tips x 34 / 803 → L (5.757 mm/px); centre row 629; half-width 156 px = 904 mm.
  FRONT   centre x 1055; 151 px each side = 904 mm (5.987 mm/px); ground y 330, roof y 100
          → 1310 mm (5.696 mm/px). Check: lid front edge 0.623 m vs 0.616 m in the side view.
  REAR    centre x 1053; 152 px = 904 mm (5.947 mm/px); ground 748, roof 521 (5.771 mm/px).
  PHOTO02 hub centres (1467.0, 713.3) / (464.6, 691.3) from rim-edge circle fits (426.6
          px/m); loaded front hub height 0.313 m (hub → tyre contact 133.5 px).

Run: <venv>/python research/traces/13-997-1-2005.py   (PHOTOCHECK=0 skips the photo check)
"""
import importlib.util
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import column_profile, half_section, silhouette_from_drawing, simplify  # noqa: E402

STOP = "13-997-1-2005"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
CUT = os.path.join(BP, "tbp-8809_porsche-911-carrera-s-2005_cutaway-side.gif")
VEC = os.path.join(BP, "vec-1030_porsche-911-carrera-2-997_4view-dims-watermarked.jpg")
P02 = os.path.join(PH, "02-side-right.jpg")
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)
PHOTOCHECK = os.environ.get("PHOTOCHECK", "1") == "1"

_spec = importlib.util.spec_from_file_location("photofit", os.path.join(HERE, "11-996-1-1998.photofit.py"))
photofit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(photofit)
_ls = importlib.util.spec_from_file_location("lampseat", os.path.join(HERE, "11-996-1-1998.lampseat.py"))
lampseat = importlib.util.module_from_spec(_ls)
_ls.loader.exec_module(lampseat)
_fc = importlib.util.spec_from_file_location("frontcam", os.path.join(HERE, "13-997-1-2005.frontcam.py"))
frontcam = importlib.util.module_from_spec(_fc)
_fc.loader.exec_module(frontcam)

# ------------------------------------------------------------------ official figures
L, W, H, WB = 4.427, 1.808, 1.310, 2.350
TRACK_F, TRACK_R = 1.486, 1.534
RIM = 18 * 0.0254                                  # 0.4572 m
TYRE_F = RIM + 2 * 0.235 * 0.40                    # 235/40 ZR 18 → 0.6452 m
TYRE_R = RIM + 2 * 0.265 * 0.40                    # 265/40 ZR 18 → 0.6692 m

# ------------------------------------------------------------------ cutaway (side) calibration
FA_PX, RA_PX = 834.0, 266.5
TIP_PX, TAIL_PX = 1073.0, 7.0
GROUND_PY, ROOF_PY = 331.0, 12.0
SX = WB / (FA_PX - RA_PX)
K_OH = (L - WB) / ((TIP_PX - FA_PX + RA_PX - TAIL_PX) * SX)
FA = (TIP_PX - FA_PX) * SX * K_OH
RA = FA + WB
SY = H / (GROUND_PY - ROOF_PY)


def X(px):
    """Cutaway x (nose right) → car x (m from the front tip)."""
    if px >= FA_PX:
        return round((TIP_PX - px) * SX * K_OH, 4)
    if px >= RA_PX:
        return round(FA + (FA_PX - px) * SX, 4)
    return round(RA + (RA_PX - px) * SX * K_OH, 4)


def X_inv(x):
    if x <= FA:
        return TIP_PX - x / (SX * K_OH)
    if x <= RA:
        return FA_PX - (x - FA) / SX
    return RA_PX - (x - RA) / (SX * K_OH)


def Y(py):
    return round((GROUND_PY - py) * SY, 4)


def pts(points):
    return [[X(px), Y(py)] for px, py in points]


# ------------------------------------------------------------------ vec-1030 calibrations
T_TIP, T_TAIL, T_CY = 34.0, 803.0, 629.0
T_SX = L / (T_TAIL - T_TIP)
T_SZ = (W / 2) / 156.0


def Xt(px):
    return round((px - T_TIP) * T_SX, 4)


def Zt(py):
    return round(abs(T_CY - py) * T_SZ, 4)


F_CX, F_SZ, F_GROUND, F_SY = 1055.0, (W / 2) / 151.0, 330.0, H / (330.0 - 100.0)
R_CX, R_SZ, R_GROUND, R_SY = 1053.0, (W / 2) / 152.0, 748.0, H / (748.0 - 521.0)


def Zf(px):
    return round(abs(px - F_CX) * F_SZ, 4)


def Yf(py):
    return round((F_GROUND - py) * F_SY, 4)


def Zr(px):
    return round(abs(px - R_CX) * R_SZ, 4)


def Yr(py):
    return round((R_GROUND - py) * R_SY, 4)


# ------------------------------------------------------------------ carried-over roof (996.1 trace)
BELT_Z = 0.70             # side-glass base
ROOF_RAIL_Z = 0.505       # top of the side glass
REAR_WINDOW_Z = 0.485     # rear-window frame half-width
WINDSCREEN_BASE_Z = 0.68  # windscreen base corners
WINDSCREEN_TOP_Z = 0.59   # windscreen top corners

# ------------------------------------------------------------------ cutaway silhouettes (auto)
cut_rgb = np.array(Image.open(CUT).convert("RGB"))
cut_gray = cv2.cvtColor(cut_rgb, cv2.COLOR_RGB2GRAY)
sil = silhouette_from_drawing(cut_gray, (0, 0, cut_gray.shape[1], cut_gray.shape[0]), close=3, thresh=160)
# The outline is drawn ~5 px thick: erode 2 px so the edge sits on the line centre.
sil = cv2.erode(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
prof = column_profile(sil)
top_px = {x: float(t) for x, (t, b) in prof.items() if TAIL_PX <= x <= TIP_PX}
# Wiper spindle on the cowl (x 726..772) pokes above the scuttle: bridge it.
for a, b in ((726, 772),):
    ya, yb = top_px[a], top_px[b]
    for x in range(a, b + 1):
        top_px[x] = ya + (yb - ya) * (x - a) / (b - a)
# Engine lid: the black louvre/spoiler detail makes the outline jagged (x < 330): median.
xs_ = sorted(top_px)
arr_ = np.array([top_px[x] for x in xs_])
for i, x in enumerate(xs_):
    if x < 330:
        top_px[x] = float(np.median(arr_[max(0, i - 6):i + 7]))
silhouette_top = sorted([[X(x), Y(v)] for x, v in top_px.items() if int(x) % 3 == 0])


def sil_top(x):
    return float(np.interp(x, [p[0] for p in silhouette_top], [p[1] for p in silhouette_top]))


# ------------------------------------------------------------------ plan outline (vec-1030, auto)
vec = cv2.imread(VEC)
vec_rgb = cv2.cvtColor(vec, cv2.COLOR_BGR2RGB)
_hsv = cv2.cvtColor(vec, cv2.COLOR_BGR2HSV).astype(int)
vH, vS, vV = _hsv[:, :, 0], _hsv[:, :, 1], _hsv[:, :, 2]
v_body = ((vS > 90) & (vH > 95) & (vH < 115)) | ((vS < 60) & (vV < 130)) | (((vH < 8) | (vH > 170)) & (vS > 120))
_tb = cv2.morphologyEx(v_body[450:810, 20:830].astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
_n, _lab, _st, _ = cv2.connectedComponentsWithStats(_tb)
_tb = _lab == 1 + np.argmax(_st[1:, cv2.CC_STAT_AREA])
half_px = {}
for c in range(_tb.shape[1]):
    ys = np.nonzero(_tb[:, c])[0]
    if len(ys):
        half_px[c + 20] = (ys[-1] - ys[0]) / 2
# Mirrors (x 310..402) stick out: bridge the body line under them.
for a, b in ((310, 402),):
    ha, hb = half_px[a], half_px[b]
    for x in range(a, b + 1):
        half_px[x] = ha + (hb - ha) * (x - a) / (b - a)
half_width = [[Xt(x), round(h * T_SZ, 4)] for x, h in sorted(half_px.items()) if x % 3 == 0 and T_TIP < x < T_TAIL]


def pw(x):
    return float(np.interp(x, [p[0] for p in half_width], [p[1] for p in half_width]))


# ------------------------------------------------------------------ lower body
# The cutaway's lowest lines (sill y 301 → 0.12 m, chin 0.10–0.19 m) are the underbody:
# both side photos put the painted sill bottom at 0.195 m (02: v 750 at u 700, 0.125 m
# under the hub line; 07 museum C4S: v 828, 0.104 m under a 0.298 m hub). So the body's
# lower edge (rockerY) comes from photo 02's paint edge (sill, aprons, arches) and the
# cutaway's underbody line gives floorY (0.12 m; ground clearance 104 mm, geometry.json).
SILL_Y = 0.195
FLOOR_Y = Y(301)
# Ends of the lower edge, measured relative to the car's own tips (the bumpers are far from
# the hub plane in x, so flat photo x-positions would be compressed by perspective; the US
# car in photo 02 also has 34 mm longer bumpers):
#  * nose paint edge — photo 02, distance from the nose tip (u 1811) at 426.7 px/m, height
#    from the hub line (near-plane features: the bumper's lower corners):
NOSE_PAINT = [(0.0, 0.418), (0.007, 0.305), (0.035, 0.249), (0.063, 0.240), (0.091, 0.229), (0.12, 0.216),
              (0.148, 0.211), (0.20, 0.199), (0.26, 0.190), (0.40, 0.187), (0.47, 0.184)]
#  * black front lip / chin (floorY) — vec-1030 side view lower outline (nose tip x 34 px,
#    768 px = L, ground y 330.5, 5.683 mm/px): px 38/62/86/106/138 → y 294/302/302/304/306:
NOSE_LIP = [(0.0, 0.40), (0.023, 0.207), (0.161, 0.162), (0.300, 0.162), (0.415, 0.151), (0.60, 0.139)]
#  * tail lower edge — vec-1030, distance from the tail tip (x 802 px): px 690/710/730/750/
#    770/778/782/786/790/798 → y 291/288/285/283/283/279/276/270/264/264 (photo 02 agrees
#    within 2 cm: 0.218/0.234/0.255/0.273/0.29/0.35 at 0.53/0.42/0.28/0.21/0.14/0.035 m):
TAIL_EDGE = [(0.646, 0.225), (0.530, 0.242), (0.415, 0.259), (0.300, 0.270), (0.184, 0.270), (0.138, 0.293),
             (0.115, 0.310), (0.092, 0.344), (0.069, 0.378), (0.023, 0.400), (0.0, 0.42)]
# The rear face is near-vertical from 0.38 to 0.62 m in both drawings (vec-1030 x 798–802 px,
# cutaway x 7–13 px): at x = L the section's points are spread over that face (floor 0.40 →
# top 0.62) instead of collapsing to one height, so the last strip stays rear-facing.
TIP_Y = {"floor": 0.40, "rocker": 0.42, "side": 0.50, "crest": 0.58, "belt": 0.60, "rail": 0.61}
TIP_Y_TAIL = TIP_Y["side"]
# A-pillar outer edge (windscreen side edge seen from the side): roof corner → cowl.
APILLAR = [(583, 30), (600, 38), (620, 48), (640, 57), (660, 67), (680, 77), (700, 87), (720, 98), (740, 110)]
COWL_PX = 740

# ------------------------------------------------------------------ photo 02 (right side, nose right)
P02_HF, P02_HR = (1467.0, 713.3), (464.6, 691.3)
P02_HUB_H = 0.313
P02_RECT = (60, 280, 1830, 860)
P02_GROUND = 847
p2 = cv2.imread(P02)
_p2hsv = cv2.cvtColor(p2, cv2.COLOR_BGR2HSV).astype(int)
# Speed Yellow paint: hue 18–30 (grass/foliage are ≥ 33), bright.
YEL = (_p2hsv[:, :, 0] >= 14) & (_p2hsv[:, :, 0] <= 31) & (_p2hsv[:, :, 1] > 70) & (_p2hsv[:, :, 2] > 140)


def p2_body_mask():
    """Car silhouette in photo 02: the yellow paint (closed) plus the wheels."""
    m = YEL.astype(np.uint8)
    m[:250] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == lab[600, 1000]).astype(np.uint8) * 255      # the component holding the door
    for (cx, cy), r in ((P02_HF, 134), (P02_HR, 139)):
        cv2.circle(m, (int(cx), int(cy)), r, 255, -1)
    # A-pillar / windscreen edge seen from the side (dark, not paint): between the side
    # glass's front edge and the A-pillar's outer edge line (1025,316) → (1270,468).
    cv2.fillPoly(m, [np.array([(980, 325), (1025, 316), (1270, 468), (1180, 476)], np.int32)], 255)
    m[:, 1812:] = 0                                            # grass beyond the nose tip
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = np.zeros_like(m)
    cv2.drawContours(out, cnt, -1, 255, -1)
    out[P02_GROUND:, :] = 0
    return out


def arch_px(hub, a0=-12, a1=193, step=3.0):
    """Arch lip: first solid run of paint going outward from the hub centre."""
    cx, cy = hub
    out = []
    for a in np.arange(a0, a1, step):
        t = math.radians(a)
        for r in np.arange(120, 260, 0.5):
            x, y = int(round(cx + r * math.cos(t))), int(round(cy - r * math.sin(t)))
            if YEL[y, x] and all(YEL[int(round(cy - (r + d) * math.sin(t))), int(round(cx + (r + d) * math.cos(t)))]
                                 for d in (1, 2, 3, 4)):
                out.append((cx + r * math.cos(t), cy - r * math.sin(t)))
                break
    return out


ARCH_F_PX = arch_px(P02_HF)
ARCH_R_PX = arch_px(P02_HR)

# Door gap: dark-line detector on the paint (row scans for the front/rear edges, column
# scans for the bottom), top corners read on a zoomed grid.
DOOR_P2 = [(1222, 478), (1233, 494), (1242.5, 510), (1254, 530), (1257.5, 550), (1259.5, 570), (1259.5, 590),
           (1259, 610), (1257.5, 630), (1256, 650), (1254, 670), (1251.5, 690), (1249, 710), (1240, 724),
           (1200, 722.5), (1160, 721), (1120, 719), (1080, 718), (1040, 716), (1000, 714.5), (960, 713),
           (920, 711.5), (880, 709.5), (840, 703.5), (830.5, 700), (803, 680), (785, 660), (769.5, 640),
           (756, 620), (743.5, 600), (732.5, 580), (723, 560), (715.5, 540), (709.5, 520), (708, 500),
           (716, 480), (730, 468), (745, 462)]
HANDLE_P2 = [(740, 551), (733, 540), (734, 522), (745, 513), (800, 512), (822, 518), (826, 532), (818, 548),
             (790, 552)]
FLAP_P2 = (1377.0, 512.0, 47.0, 21.0)          # round filler flap: centre u, v and semi-axes (px)
MARKER_P2 = [(1590, 616), (1585, 604), (1592, 598), (1655, 600), (1662, 606), (1658, 616)]
UNIT_P2 = [(1740, 668), (1733, 656), (1738, 644), (1790, 641), (1802, 648), (1802, 663), (1790, 670)]
TAIL_P2 = [(254, 507), (240, 518), (225, 530), (210, 537), (190, 539), (170, 538), (150, 536), (111, 533),
           (115, 522), (125, 510), (140, 495), (160, 481), (200, 492), (230, 500)]
TAIL_SPLIT_P2 = 509.0                           # clear upper band / red lower band boundary (v)
HEADLAMP_P2 = ((1730.0, 601.0), (1625.0, 517.0))  # lamp sliver: lower-front tip, upper-rear tip
MIRROR_P2 = (1045, 1150, 418, 476)              # housing box (u0, u1, v0, v1)
B_PILLAR_P2 = ((731.0, 322.0), (763.0, 452.0))  # door-glass rear edge (thin dark line)


def dlo_contour():
    """Side-glass region (glass + black seals) in photo 02; the mirror box is filled in and
    the belt below it continued straight."""
    x0, y0, x1, y1 = 440, 300, 1300, 500
    roi = (~YEL[y0:y1, x0:x1]).astype(np.uint8)
    roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    full = np.zeros(YEL.shape, np.uint8)
    full[y0:y1, x0:x1] = roi
    for c in range(x0, x1):
        ys = np.nonzero(YEL[250:500, c])[0]
        if len(ys):
            full[:ys[0] + 250 + 3, c] = 0
    u0, u1, v0, v1 = MIRROR_P2
    full[v0:v1, u0:u1] = 1
    # Nothing ahead of the glass's front edge (A-pillar): line (980, 325) → (1180, 470).
    for v in range(y0, y1):
        ue = 980 + (v - 325) * 200 / 145
        full[v, int(round(ue)) + 3:] = 0
    for u in range(u0 - 12, u1 + 40):
        vb = 468.5 + (u - 1100) * 0.056          # glass base through the mirror (straight)
        full[int(round(vb)) + 1:, u] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(full)
    m = (lab == lab[390, 900]).astype(np.uint8) * 255
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnt, key=cv2.contourArea)[:, 0, :].astype(float)
    return c[::6]


DLO_P2 = dlo_contour()


def clip_halfplane(poly, a, b, keep_positive):
    """Sutherland–Hodgman: keep the part of a polygon on one side of the line a→b."""
    def side(p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        sp, sq = side(p), side(q)
        inp, inq = (sp >= 0) == keep_positive, (sq >= 0) == keep_positive
        if inp:
            out.append(tuple(p))
        if inp != inq:
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def clockwise_from_lowest_front(poly):
    """Closed outline in car side coords (x rearward, y up) → start at the lowest-front
    point, clockwise as seen in the side view of a nose-left car (front edge upward first)."""
    p = [list(v) for v in poly]
    area = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))
    if area > 0:        # counter-clockwise in (x, y) = anticlockwise on screen → reverse
        p.reverse()
    xs = [v[0] for v in p]
    ys = [v[1] for v in p]
    span_x, span_y = (max(xs) - min(xs)) or 1, (max(ys) - min(ys)) or 1
    i0 = min(range(len(p)), key=lambda i: (p[i][0] - min(xs)) / span_x + (p[i][1] - min(ys)) / span_y)
    return p[i0:] + p[:i0]


# ------------------------------------------------------------------ hand-read: vec-1030 plan (px)
HOOD_EDGE_T = [(62, 629), (63, 600), (68, 575), (78, 556), (95, 548), (140, 536), (200, 521), (260, 505),
               (280, 499)]                           # front-lid shut line, centre front → windscreen corner
GRILLE_T = [(714, 629), (714, 566), (771, 566), (771, 629)]   # engine-lid louvres (dark slats)
LID_EDGE_T = [(705, 629), (705, 560), (740, 556), (790, 560), (793, 629)]
TAIL_T = (713, 791)                                  # tail-lamp plan x-extent (red)
CREST_T = [(66, 629), (66, 622), (78, 622), (78, 629)]   # lid crest emblem

# ------------------------------------------------------------------ hand-read: vec-1030 front / rear (px)
# Front: lamp (image-left = car's right lamp) from a light-region segmentation: x 924..963,
# y 191..229; indicator/fog unit x 921..970, y 242..253; outer intake x 935..999, y 260..287
# (body-colour bar across it, photos 08/22); centre intake x 1000..1111, y 262..290.
LAMP_F = [(943.5, 191), (953, 193), (960, 199), (963, 210), (960, 221), (953, 227), (943.5, 229), (934, 227),
          (927, 221), (924, 210), (927, 199), (934, 193)]
UNIT_F = [(970, 253), (970, 243), (930, 242), (922, 245), (921, 250), (925, 253)]
INTAKE_OUT_F = [(999, 287), (999, 261), (945, 260), (936, 266), (935, 281), (940, 287)]
INTAKE_BAR_F = [(999, 276), (999, 270), (936, 270), (935, 276)]   # body-colour bar across it
INTAKE_MID_F = [(1055, 291), (1055, 263), (1004, 262), (1002, 272), (1006, 291)]
# Photo 08 (straight-on front, tracing: front) — details read on zoomed grids (image-left half):
# light unit, outer intake (two openings), the body-colour bar between them, centre intake.
# Converted with the front camera fitted to the headlamp centres (ellipse fits 432.6 / 1449.2
# px at the lamp centre x 0.484, z ±0.6675, y 0.6835) and the front tyres' outer edges
# (323 / 1547 px at x = FA, z ±0.8605, contact v 1002): D 6.76 m. Check: the lid front edge
# (v 609 on the centre line) → 0.609 m (drawing 0.623). vec-1030 draws the light unit too thin
# (aspect 0.22 vs 0.37 in the photo), so the photo is used for these details.
P08_LAMPS_U, P08_LAMP_V, P08_TYRES_U, P08_GROUND_V = (432.6, 1449.2), 535.5, (323.0, 1547.0), 1002.0
UNIT_P08 = [(304, 748), (303, 700), (306, 685), (340, 686), (400, 690), (450, 694), (490, 705), (508, 718),
            (518, 740), (522, 758), (515, 766), (480, 764), (430, 760), (380, 756), (340, 752)]
INTAKE_OUT_P08 = [(362, 790), (400, 790), (500, 793), (590, 795), (604, 800), (606, 845), (620, 868), (624, 890),
                  (618, 910), (600, 915), (500, 914), (420, 910), (375, 902), (358, 880), (356, 830)]
INTAKE_BAR_P08 = [(358, 845), (612, 845), (612, 868), (358, 868)]
INTAKE_CTR_P08 = [(658, 836), (940, 836), (940, 922), (700, 921), (680, 912), (665, 890), (660, 860)]

# Rear: tail lamps (red) x 918..981, y 613..636; plate recess x 997..1109, y 652..685
# (photo 11: 0.53 m wide recess with a plate); one tailpipe each side (photo 11).
TAIL_R = [(981, 636), (981, 613), (930, 613), (921, 617), (918, 625), (921, 633), (930, 636)]
TAIL_R_SPLIT = 620.0                                  # clear upper band / red lower band (photo 11: top 30 %)
# Rear details on photo 11 (straight-on rear): face scale 913.6 px/m from the lamp inner edges
# (±0.428 m, vec-1030), confirmed by the US plate (276 px → 0.302 m, actual 0.305); centre
# x 911; heights referenced to the lamp's inner-bottom corner (v 606 ↔ 0.646 m, vec-1030).
# vec-1030's rear view puts the "Carrera" script below the lamps (0.60 m) — in the photos it
# sits between them (v 522–555 → 0.72 m).
P11_K, P11_C, P11_V0, P11_Y0 = 913.6, 911.0, 606.0, 0.646


def p11(u, v):
    return round(abs(u - P11_C) / P11_K, 4), round(P11_Y0 + (P11_V0 - v) / P11_K, 4)


PLATE_R = [p11(911, 878), p11(911, 735), p11(1048, 735), p11(1048, 878)]   # plate (US 12 x 6 in)
BADGE_R = [p11(911, 544), p11(911, 533), p11(1025, 533), p11(1025, 544)]   # script mid-band
EXHAUST_R = (962.0, 706.0, 8.0)                      # tailpipe centre (px) and radius (px)

# ------------------------------------------------------------------ fixed section curves
cowl_x = X(COWL_PX)          # windscreen base on the centre line
roof_front_x = X(583)        # windscreen top / roof front
x_lid_front = Xt(62)         # front lid leading edge (plan)
h_lid = Yf(220.7)            # lid front edge height (front view) 0.623 m
h_cowl = sil_top(cowl_x)

# Photo 02 is a close shot (camera fitted to the loft: D ≈ 5 m, height ≈ 1.0 m — see
# check-side-photo-persp-02.png). Near the nose its silhouette is the near-side lamp and wing,
# while the higher lid centre (z = 0, 0.74 m further away) is hidden by perspective; the
# orthographic drawings (cutaway, vec-1030 side — agreeing within 1.5 cm) show that lid centre.
# The museum photo 07 (longer range) lies in between. So: lid centre = drawing silhouette;
# near-side wing crest, nose corner and lamp = photo 02, back-projected at their own depth.
P02_CAM = photofit.Camera({"frontAxle": FA, "rearAxle": RA, "trackFront": TRACK_F,
                           "wheels": {"front": {"diameter": TYRE_F}, "rear": {"diameter": TYRE_R}}},
                          P02_HF, P02_HR, 1920, 5.0, 1.0, "right", P02_HUB_H)


def p02_top_profile(u0, u1, z, step=6):
    """Photo 02 top edge (paint or clear lamp against the foliage) back-projected at depth z."""
    img = cv2.imread(P02)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(int)
    H_, S_, V_ = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    carpx = ((H_ >= 14) & (H_ <= 31) & (S_ > 70) & (V_ > 140)) | ((S_ < 60) & (V_ > 150))
    out = []
    for u in range(u0, u1, step):
        col = carpx[430:760, u]
        run = 0
        for i, c in enumerate(col):
            run = run + 1 if c else 0
            if run >= 4:
                x, y = P02_CAM.backproject(u, 430 + i - 3, z)
                out.append((round(float(x), 4), round(float(y), 4)))
                break
    return sorted(out)


# Wing crest behind the lamp (near side, z ≈ 0.70): x 0.60 → 1.45 m.
WING_02 = [p for p in p02_top_profile(1110, 1640, 0.70, 12) if 0.60 <= p[0] <= 1.45]
# Nose corner in front of the lamp (z ≈ 0.72): x 0.27 → 0.34 m.
CORNER_02 = [p for p in p02_top_profile(1745, 1790, 0.72, 5) if 0.27 <= p[0] <= 0.345]


def wing(x):
    return float(np.interp(x, [p[0] for p in WING_02], [p[1] for p in WING_02]))


# Lid centre line: lid front edge (front view 0.623 m at x 0.161) then the drawing silhouette
# up to the cowl (the silhouette there is higher than the photo-02 wing, so it is the lid).
hood = [[round(x_lid_front, 4), round(h_lid, 4)]] + \
    [[round(x, 4), round(sil_top(x) - 0.003, 4)] for x in np.linspace(x_lid_front + 0.06, cowl_x, 18)]
nose = [p for p in silhouette_top if p[0] < x_lid_front]
cabin_top = [p for p in silhouette_top if p[0] > cowl_x + 0.02]
# Rear-window base (x 3.15–3.85 m): the cutaway draws the rear glass as a thick band and its
# silhouette there sits 2–3.5 cm below both vec-1030 (tip-relative: 1.174/1.117/1.117/1.088/
# 1.054/1.026/0.997 at x 3.2…3.8) and the 996.1 trace of the same carried-over roof
# (1.183/1.157/1.127/1.102/1.070/1.031/0.993); their mean is used there.
REAR_GLASS_TOP = [(3.15, 1.2035), (3.20, 1.1785), (3.30, 1.137), (3.40, 1.122), (3.50, 1.095), (3.60, 1.062),
                  (3.70, 1.0285), (3.80, 0.995), (3.85, 0.99)]
cabin_top = [p for p in cabin_top if not (3.14 <= p[0] <= 3.86)] + [list(p) for p in REAR_GLASS_TOP]
TOP_Y = sorted(nose + hood + cabin_top)
NOSE = [X(1066), X(1058), X(1050)]


# Rear deck. The roof and rear window are carried over from the 996 and the engine lid is a
# near-flat deck like the 996's: the lid-edge (P4) and rear-window-edge (P5) drops below the
# centre line are taken from the 996.1 trace at the same distance from the tail (top − belt
# 0.20/0.13/0.088/0.038/0/0 m at L−0.9/0.7/0.55/0.4/0.3/0.2; top − rail 0.15/0.111/0.082/
# 0.037/0/0.007 m). Plan z: rear window 0.485 m (996.1), lid side edge 0.45 → 0.40 m (vec-1030
# plan: lid shut line), converging to the tail.
LID_EDGE_DROP = [(1.1, 0.23), (0.9, 0.20), (0.7, 0.13), (0.55, 0.088), (0.4, 0.038), (0.3, 0.0), (0.2, 0.003),
                 (0.12, 0.012), (0.06, 0.03)]
RAIL_DROP = [(1.1, 0.16), (0.9, 0.15), (0.7, 0.111), (0.55, 0.082), (0.4, 0.037), (0.3, 0.0), (0.2, 0.007),
             (0.12, 0.012), (0.06, 0.03)]
LID_EDGE_Z = [(3.60, 0.55), (Xt(700), 0.46), (4.10, 0.44), (4.30, 0.40), (L - 0.06, 0.30), (L - 0.03, 0.20)]
RAIL_Z_REAR = [(3.60, 0.48), (Xt(699), 0.46), (4.10, 0.40), (4.30, 0.35), (L - 0.06, 0.24), (L - 0.03, 0.16)]
# Rear hips (P3): tail-lamp top edge 0.79 m at L−0.25 (photo 02: v 481 at u 160) with the hip
# crest 2–4 cm above it; rear view (vec-1030): shoulder 0.85–0.87 m at z ≈ 0.85 m.
HIP_CREST = [(1.1, 0.885), (0.9, 0.875), (0.7, 0.862), (0.55, 0.85), (0.4, 0.835), (0.3, 0.82), (0.2, 0.795),
             (0.12, 0.76), (0.06, 0.70), (0.03, 0.645)]
HIP_CREST_Z = [(1.1, 0.857), (0.9, 0.857), (0.7, 0.842), (0.55, 0.823), (0.4, 0.78), (0.3, 0.738), (0.2, 0.674),
               (0.12, 0.586), (0.06, 0.45), (0.03, 0.30)]


def top_at(x):
    return float(np.interp(x, [p[0] for p in TOP_Y], [p[1] for p in TOP_Y]))


def build(F):
    """Assemble the body curves. F: photo-derived features in car coordinates."""
    arch_f, arch_r = F["arch_f"], F["arch_r"]
    fx1 = max(p[0] for p in arch_f)
    rx0 = min(p[0] for p in arch_r)
    ax0 = min(q[0] for q in arch_f)
    ax1 = max(q[0] for q in arch_r)
    nose_b = [[x, y] for x, y in NOSE_PAINT if x < ax0 - 0.02]
    tail_b = [[L - d, y] for d, y in TAIL_EDGE if L - d > ax1 + 0.02]
    bottom = nose_b + [list(p) for p in arch_f] + \
        [[x, SILL_Y] for x in np.linspace(fx1 + 0.03, rx0 - 0.03, 6)] + [list(p) for p in arch_r] + tail_b
    bottom = sorted(bottom)

    # Crest (P3): front wings = the side silhouette from behind the nose to the cowl (front
    # view: silhouette half-width 0.796 m at 0.866 m — the wing crest near the axle); door
    # shoulder under the glass; rear hips (rear view: widest 0.904 m at 0.65–0.75 m, crest
    # ~0.86 m inboard of the lamp tops); down to the tail-lamp top.
    crest = [[0.0, Y(229)]] + [[x, round(sil_top(x) - 0.03, 4)] for x in NOSE] + \
        [list(p) for p in CORNER_02] + [list(p) for p in WING_02]
    crest += [[F["belt"][0][0], F["belt"][0][1] - 0.02], [F["belt"][-1][0] - 0.3, F["belt"][-1][1] - 0.04]]
    crest += [[L - d, y] for d, y in HIP_CREST] + [[L, TIP_Y["crest"]]]
    # z: nose 0.85 × plan half-width; the nose corner; over the lamp the seat puts P3 on the
    # lamp's outer edge; behind it the wing crest runs back from the lamp top (z 0.66) at
    # ≈ 0.70 m (the filler flap, drawn in the plan at z 0.765–0.852 and seen from the side at
    # y 0.73–0.79, sits on the shoulder outboard of the crest); ≥ 3 cm inside the plan outline.
    crest_z = [[0.0, 0.0]] + [[x, round(0.85 * pw(x), 4)] for x in NOSE] + \
        [[x, round(min(z, pw(x) - 0.03), 4)] for x, z in ((X(1040), 0.62), (0.30, 0.72), (0.65, 0.69),
                                                          (0.80, 0.70), (FA, 0.71), (1.26, 0.72))] + \
        [[cowl_x, 0.74], [F["belt"][0][0], 0.82],
         [F["belt"][-1][0] - 0.3, 0.84]] + [[L - d, z] for d, z in HIP_CREST_Z] + [[L, 0.0]]

    # Belt (P4): lid shut line ahead of the screen (plan HOOD_EDGE_T, just under the hood),
    # side-glass base (photo 02 DLO), engine-lid side edge behind.
    belt = [[0.0, Y(229)]] + [[x, round(sil_top(x) - 0.012, 4)] for x in NOSE]
    belt += [[x, round(min(y - 0.02, wing(x) + 0.005 if x >= WING_02[0][0] else y - 0.02), 4)]
             for x, y in hood if Xt(95) < x < F["belt"][0][0] - 0.08]
    belt += [list(p) for p in F["belt"]]
    belt += [[L - d, round(top_at(L - d) - dy, 4)] for d, dy in LID_EDGE_DROP if L - d > F["belt"][-1][0] + 0.05]
    belt += [[L, TIP_Y["belt"]]]
    belt_z = [[0.0, 0.0]] + [[x, round(0.6 * pw(x), 4)] for x in NOSE] + \
        [[Xt(px), Zt(py)] for px, py in HOOD_EDGE_T[4:]] + \
        [[F["belt"][0][0], BELT_Z], [F["belt"][-1][0], BELT_Z - 0.02]] + \
        [[x, z] for x, z in LID_EDGE_Z if x > F["belt"][-1][0] + 0.05] + [[L, 0.0]]

    # Roof rail (P5): hood → A-pillar outer edge → side-glass top → rear-window edge → lid.
    rail = [[0.0, Y(229)]] + [[x, round(sil_top(x) - 0.004, 4)] for x in NOSE]
    rail += [[x, round(y - 0.004, 4)] for x, y in hood if Xt(95) < x < cowl_x - 0.01]
    rail += pts(APILLAR) + [list(p) for p in F["rail"] if p[0] > X(583) + 0.05]
    q_end = F["rail"][-1][0]
    rail += [[L - d, round(top_at(L - d) - dy, 4)] for d, dy in RAIL_DROP if L - d > q_end + 0.05]
    rail += [[L, TIP_Y["rail"]]]
    roof_z = [[0.0, 0.0]] + [[x, round(0.3 * pw(x), 4)] for x in NOSE] + \
        [[Xt(95), 0.2], [cowl_x, 0.36], [X(740), WINDSCREEN_BASE_Z - 0.03], [X(583), WINDSCREEN_TOP_Z - 0.06],
         [X(500), ROOF_RAIL_Z], [X(400), ROOF_RAIL_Z - 0.01], [q_end, REAR_WINDOW_Z]] + \
        [[x, z] for x, z in RAIL_Z_REAR if x > q_end + 0.05] + [[L, 0.0]]

    # Widest-point height: bumper corners, front wing at hub height, door, rear hips at the
    # tail-lamp bottom line (rear view: full width 0.65–0.75 m).
    side_y = [[0.0, Y(229)], [X(1058), 0.42], [X(1000), 0.46], [FA, 0.52], [X(700), 0.55], [X(400), 0.60],
              [RA, 0.66], [X(150), 0.66], [X(60), 0.58], [L, TIP_Y_TAIL]]

    # Underside on the centre line: the black front lip (vec-1030 chin line, 3–4 cm under the
    # paint edge, photo 02), the underbody line (0.12 m) between the axles, and the black rear
    # diffuser round the tailpipes, down to 0.165 m (photo 11: black surround v 885–980 with the
    # ground at v ≈ 1095 under the rear face, 704 px/m) — the renderer paints P0→P1 dark.
    def bot(x):
        return float(np.interp(x, [p[0] for p in bottom], [p[1] for p in bottom]))

    floor_y = [list(p) for p in NOSE_LIP] + \
        [[FA - 0.25, 0.14], [FA, 0.13], [FA + 0.5, FLOOR_Y], [RA - 0.35, FLOOR_Y], [RA, 0.15], [RA + 0.45, 0.2]] + \
        [[L - 0.30, 0.17], [L - 0.15, 0.165], [L - 0.09, 0.175], [L - 0.05, 0.25], [L - 0.02, 0.36]] + \
        [[L, TIP_Y["floor"]]]

    def near_arch(x):
        return abs(x - FA) < 0.42 or abs(x - RA) < 0.45

    # P1 at the ends: bumper lower corners — rear 0.95 × half-width (vec-1030 rear view: full
    # 0.90 m half-width down to 0.33 m), front 0.9 (photo 08: lip nearly full width).
    rocker_z = []
    for x, z in half_width:
        f = 0.9 if x < X(1040) else (0.95 if x > X(150) else None)
        rocker_z.append([x, round(max(0.0, z * f if f else z - (0.012 if near_arch(x) else 0.04)), 4)])

    body = {
        "floorY": floor_y,
        "rockerY": simplify(bottom, 0.002),
        "rockerZ": simplify(rocker_z, 0.003),
        "sideY": side_y,
        "sideZ": [[0.0, 0.0]] + [list(p) for p in half_width] + [[L, 0.0]],
        "crestY": simplify(sorted(crest), 0.003),
        "crestZ": sorted(crest_z),
        "beltY": simplify(sorted(belt), 0.003),
        "beltZ": sorted(belt_z),
        "roofY": simplify(sorted(rail), 0.003),
        "roofZ": sorted(roof_z),
        "topY": simplify(sorted(TOP_Y), 0.002),
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
            x = min(max(float(x), 0.0), L)
            if out and x <= out[-1][0] + 1e-4:
                out[-1][1] = round((out[-1][1] + v) / 2, 4)
            else:
                out.append([round(x, 4), round(float(v), 4)])
        body[k] = out
    # Seat the wing on the flat headlamp (belt on its inner edge, crest on its outer edge, lid
    # below the inner edge) so the renderer's raycast leaves the lamp in the wing (see
    # 11-996-1-1998.lampseat.py; without it the lamp was pushed 7.6 cm out of the wing).
    hl = headlamp(F)
    u_in = max(u for u, _ in hl["outline"])
    body["_seat"] = lampseat.seat(body, hl, full=True, ends=0.015, cap_top=False,
                                  inboard=lampseat.probe_radius(hl) - u_in)
    seat_range = body.pop("_seat")
    print("lamp seated over x", [round(v, 3) for v in seat_range])
    # Pull sideZ in against the Catmull-Rom bulge so the lofted plan matches the traced one.
    for it in range(6):
        body["sideZ"] = [[x, round(max(z - (max(p[0] for p in half_section(body, x)) - pw(x)), 0.0), 4)]
                         if 0 < x < L else [x, z] for x, z in body["sideZ"]]
        if it == 3:
            body["sideZ"] = simplify(body["sideZ"], 0.0015)
    # Sanity: P2 must stay close to the plan outline (a large pull means another control point
    # sticks out of the plan and must be fixed instead).
    bad = [(x, z, pw(x)) for x, z in body["sideZ"] if 0.02 < x < L - 0.02 and pw(x) - z > 0.04
           and abs(x - FA) > 0.45 and abs(x - RA) > 0.47]   # at the arches P1 (lip) is outboard by design
    if bad:
        print("WARNING sideZ pulled > 4 cm inside the plan outline at", [(round(a, 3), round(b, 3), round(c, 3))
                                                                        for a, b, c in bad[:8]])
    return body


# ------------------------------------------------------------------ photo → car mappings
def flat_p2(u, v):
    """Pass 1: photo 02 px → car (x, y), flat hub calibration (right side, nose right)."""
    hf, hr = np.array(P02_HF), np.array(P02_HR)
    d = hr - hf
    k = np.linalg.norm(d) / math.hypot(WB, (TYRE_R - TYRE_F) / 2)
    ang = math.atan2(-d[1], -d[0]) - math.atan2((TYRE_R - TYRE_F) / 2, WB)
    c, s = math.cos(-ang), math.sin(-ang)
    du, dv = u - hf[0], v - hf[1]
    ru, rv = c * du - s * dv, s * du + c * dv
    return FA - ru / k, P02_HUB_H - rv / k


def photo_features(mapper):
    """Car-space features from photo 02 through mapper(u, v) → (x, y)."""
    F = {}
    F["arch_f"] = sorted([mapper(u, v) for u, v in ARCH_F_PX])
    F["arch_r"] = sorted([mapper(u, v) for u, v in ARCH_R_PX])
    dlo = [mapper(u, v) for u, v in DLO_P2]
    (bu0, bv0), (bu1, bv1) = B_PILLAR_P2
    a, b = mapper(bu0, bv0), mapper(bu1, bv1)
    # extend the B-pillar line beyond the glass so it cuts cleanly
    dx, dy = b[0] - a[0], b[1] - a[1]
    a2, b2 = (a[0] - dx, a[1] - dy), (b[0] + dx, b[1] + dy)
    door = clip_halfplane(dlo, a2, b2, keep_positive=True)
    quarter = clip_halfplane(dlo, a2, b2, keep_positive=False)
    if np.mean([p[0] for p in door]) > np.mean([p[0] for p in quarter]):
        door, quarter = quarter, door
    F["door_glass"] = clockwise_from_lowest_front(door)
    F["quarter_glass"] = clockwise_from_lowest_front(quarter)
    # Glass base (belt) and glass top (rail) sampled along the DLO outline.
    xs = np.linspace(min(p[0] for p in dlo) + 0.02, max(p[0] for p in dlo) - 0.02, 18)
    arr = np.array(dlo)
    belt_line, rail_line = [], []
    for x in xs:
        near = arr[np.abs(arr[:, 0] - x) < 0.03]
        if len(near):
            belt_line.append([round(float(x), 4), round(float(near[:, 1].min()), 4)])
            rail_line.append([round(float(x), 4), round(float(near[:, 1].max()), 4)])
    F["belt"], F["rail"] = belt_line, rail_line
    F["door"] = [mapper(u, v) for u, v in DOOR_P2]
    F["handle"] = [mapper(u, v) for u, v in HANDLE_P2]
    cu, cv, au, av = FLAP_P2
    F["flap"] = [mapper(cu - au * math.cos(t), cv + av * math.sin(t))
                 for t in np.linspace(math.pi / 2, math.pi / 2 - 2 * math.pi, 13)[:-1]]
    F["marker"] = [mapper(u, v) for u, v in MARKER_P2]
    # The light unit wraps round the bumper corner (z ≈ 0.72), where the flat photo mapping
    # would put it ahead of the nose: back-project it through the fitted photo-02 camera.
    F["unit"] = [tuple(P02_CAM.backproject(u, v, 0.72)) for u, v in UNIT_P2]
    F["tail"] = [mapper(u, v) for u, v in TAIL_P2]
    F["tail_split_y"] = mapper(180, TAIL_SPLIT_P2)[1]
    F["headlamp"] = [mapper(u, v) for u, v in HEADLAMP_P2]
    u0, u1, v0, v1 = MIRROR_P2
    F["mirror"] = [mapper(u0, v1), mapper(u1, v0)]
    return F


# ------------------------------------------------------------------ decals & parts
GLASS = "#1c232a"
TRIM = "#16181a"
GAP = "#2a2a2a"
LENS_RED = "#b3201a"
CLEAR = "#e4e8ea"
AMBER = "#e8962a"
FRONT = [-0.05, 0.45]
REAR = [L - 0.45, L + 0.05]


def r4(points):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in points]


def thin(points, tol=0.004):
    p = r4(points)
    return simplify(p, tol) if len(p) > 10 else p


def side(id_, points, finish, color, kind="fill", **kw):
    d = {"id": id_, "plane": "side", "kind": kind, "points": thin(points), "finish": finish, "color": color}
    d.update(kw)
    return d


def box(plane, id_, pts_, finish, color, **kw):
    d = {"id": id_, "plane": plane, "kind": "fill", "points": r4(pts_), "finish": finish, "color": color}
    d.update(kw)
    return d


def front_pts(points):
    return [[Zf(px), Yf(py)] for px, py in points]


def rear_pts(points):
    return [[Zr(px), Yr(py)] for px, py in points]


def front_details(body):
    """Photo 08 details → car [z, y] (see the P08 constants); each point is back-projected
    onto the lofted body at its own height (section depth)."""
    lamp = LAMP_REF
    cam = frontcam.FrontCam(P08_LAMPS_U, lamp[2], lamp[0], P08_TYRES_U, (TRACK_F + 0.235) / 2, FA,
                            P08_LAMP_V, lamp[1], P08_GROUND_V, 0.0)
    depth = frontcam.section_depth(body, half_section)
    return {k: frontcam.photo_outline(cam, v, depth) for k, v in
            (("unit", UNIT_P08), ("intake_out", INTAKE_OUT_P08), ("bar", INTAKE_BAR_P08),
             ("intake_ctr", INTAKE_CTR_P08))}, cam


def make_decals(F):
    F08 = F["front08"]
    tail = F["tail"]
    split = F["tail_split_y"]
    tail_lo = [p for p in tail if p[1] <= split + 1e-6]
    tail_up = [p for p in tail if p[1] >= split - 1e-6]
    xs_lo = [p[0] for p in tail_lo]
    # side tail lamp: whole lamp red (lower band) + clear upper band
    decals = [
        side("side-glass", F["door_glass"], "glass", GLASS, depth=[0.45, 2], facing=0.3),
        side("quarter-glass", F["quarter_glass"], "glass", GLASS, depth=[0.45, 2], facing=0.3),
        side("window-trim", F["rail"], "satin", TRIM, kind="line", width=0.012, depth=[0.45, 2], facing=0.3),
        side("door-gap", F["door"], "satin", GAP, kind="line", depth=[0.6, 2]),
        side("door-handle", F["handle"], "satin", GAP, kind="line", depth=[0.6, 2]),
        # Amber side marker in the front bumper flank (photo 02/24; US-market car).
        side("side-marker", F["marker"], "lens", AMBER, depth=[0.55, 2], facing=0.3),
        # Clear indicator/fog unit wrapping round the bumper corner.
        side("indicator-side", F["unit"], "lens", CLEAR, depth=[0.4, 2], facing=0.25),
        side("taillight-side", clockwise_from_lowest_front(tail), "lens", LENS_RED, depth=[0.5, 2], facing=0.3),
        {"id": "fuel-flap", "plane": "side", "kind": "line", "points": r4(F["flap"]), "finish": "satin",
         "color": GAP, "depth": [0.6, 2], "side": "right"},
    ]
    # Windscreen / rear window in plan: the roof and glass are carried over from the 996
    # (geometry.json 13), so the 996.1 traced outlines are reused, re-mapped in x: windscreen
    # from 3 cm behind the cowl to 2 cm ahead of the roof front (as on the 996.1 trace);
    # rear window over the vec-1030 plan glass extent x 573..699 px (3.103..3.828 m).
    c11 = json.load(open(os.path.join(ROOT, "src", "data", "cars", "11-996-1-1998.json")))
    g11 = {d["id"]: d for d in c11["decals"]}

    def remap(points, a0, a1, b0, b1):
        return [[b0 + (x - a0) * (b1 - b0) / (a1 - a0), z] for x, z in points]

    ws = g11["windscreen"]["points"]
    rw = g11["rear-window"]["points"]
    decals += [
        {"id": "windscreen", "plane": "top", "kind": "fill",
         "points": r4(remap(ws, min(p[0] for p in ws), max(p[0] for p in ws), cowl_x + 0.029, roof_front_x - 0.021)),
         "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.8, 2]},
        {"id": "rear-window", "plane": "top", "kind": "fill",
         "points": r4(remap(rw, min(p[0] for p in rw), max(p[0] for p in rw), Xt(573), Xt(699))),
         "finish": "glass", "color": GLASS, "facing": 0.15, "depth": [0.85, 2]},
    ]
    decals += [
        {"id": "hood-gap", "plane": "top", "kind": "line", "points": r4([[Xt(px), Zt(py)] for px, py in HOOD_EDGE_T]),
         "finish": "satin", "color": GAP, "facing": 0.3, "depth": [0.5, 1.0]},
        {"id": "lid-gap", "plane": "top", "kind": "line", "points": r4([[Xt(px), Zt(py)] for px, py in LID_EDGE_T]),
         "finish": "satin", "color": GAP, "facing": 0.3, "depth": [0.6, 1.2]},
        {"id": "engine-grille", "plane": "top", "kind": "fill", "points": r4([[Xt(px), Zt(py)] for px, py in GRILLE_T]),
         "finish": "paint", "color": "paint", "stripes": [0.035, 0.3], "facing": 0.3, "depth": [0.7, 1.2]},
        {"id": "crest", "plane": "top", "kind": "fill", "points": r4([[Xt(px), Zt(py)] for px, py in CREST_T]),
         "finish": "chrome", "color": "#c9a24e", "facing": 0.3, "depth": [0.5, 1.0]},
        box("front", "bumper-front-face", [[0.0, 0.22], [0.0, 0.46], [0.86, 0.46], [0.86, 0.22]], "paint", "paint",
            depth=[-0.05, 0.12], facing=0.2),
        box("rear", "bumper-rear-face", [[0.0, 0.33], [0.0, 0.62], [0.88, 0.62], [0.88, 0.33]], "paint", "paint",
            depth=[L - 0.2, L + 0.05], facing=0.2),
        box("front", "indicator-front", F08["unit"], "lens", CLEAR, depth=FRONT, facing=0.2),
        # Three intakes (geometry.json 13; photo 08): outer radiator intakes split by a
        # body-colour bar, wide centre intake.
        box("front", "intake-front", F08["intake_out"], "satin", "#141516", depth=FRONT, facing=0.3),
        box("front", "intake-bar-front", F08["bar"], "paint", "paint", depth=FRONT, facing=0.3),
        box("front", "intake-front-centre", F08["intake_ctr"], "satin", "#141516", depth=FRONT, facing=0.3),
        box("rear", "taillight", rear_pts([(981, 636), (981, TAIL_R_SPLIT), (920, TAIL_R_SPLIT), (918, 625),
                                           (921, 633), (930, 636)]), "lens", LENS_RED, depth=REAR, facing=0.25),
        box("rear", "indicator-rear", rear_pts([(981, TAIL_R_SPLIT), (981, 613), (930, 613), (921, 617),
                                                (920, TAIL_R_SPLIT)]), "lens", CLEAR, depth=REAR, facing=0.25),
        box("rear", "plate-rear", PLATE_R, "satin", "#e4e4df", depth=[L - 0.3, L + 0.05], facing=0.4),
        box("rear", "badge-rear", BADGE_R, "chrome", "#c5c8cc", depth=REAR, facing=0.3),
    ]
    return decals


# Headlamp: lens plane from the side-view sliver (photo 02: lower-front tip → upper-rear
# tip) and the front-view outline (vec-1030). Pitch = atan(Δx / Δy) of that sliver with the
# front-view heights; yaw from the plan view (the outer edge sits ~3 cm behind the inner).
def headlamp(F):
    # Photo 02 sliver back-projected at the lamp's depth (lower-front tip z 0.68, upper-rear
    # tip z 0.657): x 0.361 → 0.607 (the flat hub mapping put it 2.5 cm further back).
    (xa, ya) = P02_CAM.backproject(*HEADLAMP_P2[0], 0.68)
    (xb, yb) = P02_CAM.backproject(*HEADLAMP_P2[1], 0.657)
    lz = np.array([Zf(px) for px, _ in LAMP_F])
    ly = np.array([Yf(py) for _, py in LAMP_F])
    y_lo, y_hi = ly.min(), ly.max()
    pitch = math.degrees(math.atan2(xb - xa, y_hi - y_lo))
    yaw = 5.0
    p_, w_ = math.radians(pitch), math.radians(yaw)
    cz, cy = float((lz.max() + lz.min()) / 2), float((y_hi + y_lo) / 2)
    cx = (xa + xb) / 2
    outline = [[round(float((cz - z) / math.cos(w_)), 4), round(float((y - cy) / math.cos(p_)), 4)]
               for z, y in zip(lz, ly)]
    return {
        "centre": [round(cx, 4), round(cy, 4), round(cz, 4)],
        "outline": outline,
        "yaw": round(yaw, 1),
        "pitch": round(pitch, 1),
        # Dark gasket round the clear lens (photos 08/20); projector main beam inside.
        "ring": 0.008,
        "ringColor": "#2b2d30",
        "ringFinish": "satin",
        "lensColor": "#dde5ea",
        "graphic": "projector",
    }


def make_car(F):
    body = build(F)
    (mx0, my0), (mx1, my1) = F["mirror"]
    car = {
        "id": STOP,
        "length": L,
        "frontAxle": round(FA, 4),
        "rearAxle": round(RA, 4),
        "trackFront": TRACK_F,
        "trackRear": TRACK_R,
        "body": body,
        "decals": make_decals(F),
        "wheels": {
            # 18-inch 'Carrera' five-spoke (geometry.json 13; photo 02/24), silver.
            "front": {"diameter": round(TYRE_F, 4), "width": 0.235, "rim": round(RIM, 4), "design": "five-spoke",
                      "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
            "rear": {"diameter": round(TYRE_R, 4), "width": 0.265, "rim": round(RIM, 4), "design": "five-spoke",
                     "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
        },
        "headlight": headlamp(F),
        # Double-arm door mirror on the mirror triangle (geometry.json 13), body colour; housing
        # box from photo 02; out to the front-view mirror tip (x 890 px → 0.99 m).
        # Mirror housing (the renderer centres the ellipsoid on at[0], at[1] and z + size/2):
        # fore-aft extent from photo 02 (x 1.739–1.985); lateral extent from photo 08 through the
        # front camera (13-997-1-2005.frontcam.py; housing u 394–490 px at x 1.9 → z 0.704–0.855,
        # height 58 px → 0.091 m). The vec-1030 front view reads the tip 13 cm further out
        # (0.988) — the photo shows the housing inside the front-wing silhouette.
        "mirror": {"at": [round((mx0 + mx1) / 2, 4), round((my0 + my1) / 2, 4), 0.704],
                   "size": [round(abs(mx1 - mx0), 3), 0.091, 0.151],
                   "shape": "aero", "color": "paint", "finish": "paint"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # One oval tailpipe each side (geometry.json 13 "a pair of oval-shaped tailpipes"). Photo 11
        # (rear): tips x 430–580 / 1232–1382 px; the rear-face scale 913.6 px/m comes from the lamp
        # inner edges (±0.428 m, vec-1030) and is confirmed by the US plate (276 px → 0.302 m,
        # actual 0.305) → centres ±0.439 m, oval 0.164 × 0.066 m (round equivalent r 0.052).
        # (vec-1030's rear view puts a dark diffuser region at ±0.54 m, which I had first taken
        # for the tip.) Height: photo 11 tip centres v 940/950 → 0.275 m (vec-1030: 0.24); the
        # pipe ends ~0.09 m ahead of the tail tip.
        "exhausts": [[round(L - 0.09, 4), 0.275, s * 0.439, 0.052]
                     for s in (1, -1)],
    }
    with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
        json.dump(car, f, indent=1)
    push, depths = lampseat.placement(body, car["headlight"], half_section)
    print("renderer placement pushes the lens out by (mm)", round(push * 1000), "probe depths (mm)",
          [None if d is None else round(d * 1000) for d in depths])
    return car


# ------------------------------------------------------------------ photo features
# All side features read on photo 02 (arches, door gap, side glass, handle, flap, marker,
# light unit, lamp outlines) lie within a few cm of the near wheel plane, where the flat
# hub calibration is exact (a feature 0.24 m inside that plane, e.g. the glass top, moves by
# ≈1 cm). A camera fitted to the photo (photofit) is used only for the check overlay: at
# 5–6 m it back-projects points near the tips badly (e.g. the front light unit landed
# 8 cm ahead of the nose).
F = photo_features(flat_p2)
LAMP_REF = headlamp(F)["centre"]
F["front08"] = {k: [[0.0, 0.0], [0.0, 0.01], [0.01, 0.01]] for k in ("unit", "intake_out", "bar", "intake_ctr")}
_body0 = make_car(F)["body"]            # the body does not depend on the front decals
F["front08"], FRONT_CAM = front_details(_body0)
print("photo 08 front camera: D %.2f m, f %.0f px, lid front edge %.3f m (drawing %.3f)" % (
    FRONT_CAM.D, FRONT_CAM.f,
    FRONT_CAM.hc - (609 - FRONT_CAM.v_off) / (FRONT_CAM.f / (FRONT_CAM.D + x_lid_front)), h_lid))
car = make_car(F)
PHOTO_MASK = p2_body_mask()

# ------------------------------------------------------------------ calibrated reference images
S = 0.0035


def warp(src_rgb, fn_src, x_range, y_range, name):
    xs = np.arange(x_range[0], x_range[1], S)
    ys = np.arange(y_range[1], y_range[0], -S)
    gx, gy = np.meshgrid(xs, ys)
    px, py = fn_src(gx, gy)
    img = cv2.remap(src_rgb, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR,
                    borderValue=(255, 255, 255))
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return os.path.relpath(path, ROOT), xs, ys


xinv = np.vectorize(X_inv)
side_img, sxs, sys_ = warp(cut_rgb, lambda gx, gy: (xinv(gx), GROUND_PY - gy / SY), (-0.15, L + 0.15),
                           (-0.05, 1.45), "ref-side.png")
top_img, txs, tzs = warp(vec_rgb, lambda gx, gz: (T_TIP + gx / T_SX, T_CY - gz / T_SZ), (-0.15, L + 0.15),
                         (-1.05, 1.05), "ref-top.png")
front_img, fzs, fys = warp(vec_rgb, lambda gz, gy: (F_CX - gz / F_SZ, F_GROUND - gy / F_SY), (-1.05, 1.05),
                           (-0.05, 1.45), "ref-front.png")
rear_img, rzs, rys = warp(vec_rgb, lambda gz, gy: (R_CX + gz / R_SZ, R_GROUND - gy / R_SY), (-1.05, 1.05),
                          (-0.05, 1.45), "ref-rear.png")


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
    # Photo 02 (car's right side, nose right), flat hub calibration; the perspective-correct
    # comparison is check-side-photo-persp-02.png.
    "side_photo": {"image": os.path.relpath(P02, ROOT), "wheelF": list(P02_HF), "wheelR": list(P02_HR),
                   "tipF": round(P02_HF[0] + FA * 426.6, 1), "crop": [40, 260, 1880, 880]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)

# Cutaway calibration check: tyre circles of the official sizes on the drawing.
cal = Image.fromarray(cut_rgb).convert("RGB")
d = ImageDraw.Draw(cal)
for hx, r in ((FA_PX, TYRE_F / 2), (RA_PX, TYRE_R / 2)):
    rp = r / SX
    cy_ = GROUND_PY - r / SY
    d.ellipse([hx - rp, cy_ - rp, hx + rp, cy_ + rp], outline=(255, 0, 0), width=1)
d.line([(0, GROUND_PY), (cal.width, GROUND_PY)], fill=(0, 0, 255))
d.line([(0, ROOF_PY), (cal.width, ROOF_PY)], fill=(0, 0, 255))
cal.save(os.path.join(OUT_DIR, "ref-cutaway-cal.png"))

# ------------------------------------------------------------------ photo checks
if PHOTOCHECK:
    st = photofit.check(car, P02, P02_HF, P02_HR, P02_RECT, os.path.join(OUT_DIR, "check-side-photo-persp-02.png"),
                        facing="right", ground_row=P02_GROUND, D_grid=(4, 5, 6, 7, 8, 10, 12, 15),
                        Y_grid=[0.6, 0.8, 1.0, 1.2, 1.4, 1.6], mask=PHOTO_MASK.copy(), hub_height=P02_HUB_H)
    print("photo 02-side-right.jpg", st)

print("wrote", STOP, "L", L, "axles", round(FA, 4), round(RA, 4), "SX", round(SX * 1000, 3), "SY", round(SY * 1000, 3),
      "lamp", car["headlight"]["centre"], "pitch", car["headlight"]["pitch"])
