"""Trace: 12-996-2-2002 — 911 Carrera Coupé, type 996 second series (MY2002–2004).

The 996.2 is a facelift of the 996.1 narrow body (research/geometry.json 12; coordinator
brief: keep the narrow-body Carrera envelope from the 996.1 trace — the only 996.2 drawing,
tbp-68297, is the wide-body Carrera 4S with the Turbo front apron). The body curves are
therefore the 996.1 trace (src/data/cars/11-996-1-1998.json, written by
research/traces/11-996-1-1998.py); this script applies the documented facelift changes,
each measured on the 996.2 photos (research/photos/12-996-2-2002/):

  * Headlamps: "911 Turbo headlamps, rounded off at the bottom" (geometry.json 12). The lamp
    outline is segmented in photo 07 (straight-on front) and mapped into the 996.1 drawing's
    front view through the 996.1 photo 07 of stop 11 (same framing): the two cars' lamp
    spans agree (inner/outer span ratio 0.514 vs 0.517), so the 996.2 contour is scaled by
    the span ratio (isotropic, anchored on the lamp tops; check: the lid front edge then
    lands within 2 px of the 996.1's), and the 996.1 photo contour is fitted to the 996.1
    drawing outline (4 parameters, rms 1.8 drawing px ≈ 6 mm). Same wing opening and
    mounting → the lamp is lifted onto the 996.1 lamp plane (pitch 64.2°, yaw 14°).
  * Front apron: "completely reshaped, larger intakes" — upper outer openings, a body-colour
    blade and a full-width lower opening, read on photo 07 (calibration below).
  * Rear: "extended rear end panel … a raised section runs from wheel arch to wheel arch
    below the licence-plate recess" and "redesigned oval tailpipes" (photos 11, 12).
  * Clear indicator lenses (geometry.json 12: amber only on MY1998): no amber band under the
    lamp, clear side marker, clear upper tail-lamp band (photos 11, 23, 24, 28).
  * Width 1770 mm (+5 mm, "widened rear quarter panels"), front track 1465 mm (specs.json 12).
  * Wheels: standard 17-inch "Carrera II" (slim curved five-spoke; photo 24), same tyres.

Verified unchanged on photo 01 (studio side profile): perspective fit of the 996.1 body
IoU 0.94 with the ends on the photo within 1 px (D 6 m); arch-lip radii measured the same
way on 996.1 and 996.2 photos agree within 0.5 cm; glasshouse, door, handle, marker, tail
lamp land on the photo (check-side-photo-persp-01.png).

Photo 07 calibration (front, long lens): lamp inner span 541 px ↔ 2 × 0.343 m (996.1 drawing
lamp inner ends) → 789 px/m at the lamp tips (x ≈ 0.16 m); at the bumper face (x ≈ 0.05 m,
camera ≈ 5 m from the nose, estimated from the lamp spans) 806 px/m; centre line x 984;
lid front edge y 665 ↔ 0.608 m (996.1 drawing). Validated on the 996.1 photo 07 with the
same method: intake top 0.410 m (drawing 0.412), bottom 0.289 (0.281), outer end 0.598 (0.614).

Run: <venv>/python research/traces/12-996-2-2002.py   (PHOTOCHECK=0 skips the photo fit)
"""
import importlib.util
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import half_section, simplify  # noqa: E402

STOP = "12-996-2-2002"
BASE = "11-996-1-1998"
PH = os.path.join(ROOT, "research", "photos", STOP)
PH11 = os.path.join(ROOT, "research", "photos", BASE)
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)
PHOTOCHECK = os.environ.get("PHOTOCHECK", "1") == "1"

base = json.load(open(os.path.join(ROOT, "src", "data", "cars", f"{BASE}.json")))
L = base["length"]                      # 4430 (specs.json 12: unchanged)
FA, RA = base["frontAxle"], base["rearAxle"]
W = 1.770                               # specs.json 12 width
TRACK_F, TRACK_R = 1.465, 1.500         # specs.json 12 tracks

# ------------------------------------------------------------------ 996.1 drawing calibrations (11-996-1-1998.py)
F_CX, F_SZ, F_GROUND, F_SY = 418.5, 1.765 / 507.0, 1321.0, 1.305 / (1321.0 - 954.0)


def Zf(px):
    return abs(px - F_CX) * F_SZ


def Yf(py):
    return (F_GROUND - py) * F_SY


# 996.1 drawing front-view lamp unit outline (image-left lamp), as traced for stop 11.
LAMP11_F = [(218, 1122), (225, 1108), (235, 1101), (248, 1098), (262, 1100), (275, 1106), (287, 1113), (297, 1122),
            (306, 1130), (313, 1138), (318, 1146), (320, 1150), (320, 1153), (318, 1158), (310, 1161), (270, 1162),
            (240, 1160), (230, 1156), (220, 1140), (217, 1130), (218, 1122)]


# ------------------------------------------------------------------ body: 996.1 + widened rear quarters
body = json.loads(json.dumps(base["body"]))
# +2.5 mm per side on the rear quarters (width 1765 → 1770), blended in behind the doors.
X_BLEND0, X_BLEND1 = 2.70, 2.95
for key in ("sideZ", "rockerZ", "crestZ"):
    out = []
    for x, z in body[key]:
        w = float(np.clip((x - X_BLEND0) / (X_BLEND1 - X_BLEND0), 0, 1))
        if 0 < x < L and z > 0:
            z = z + 0.0025 * w
        out.append([x, round(z, 4)])
    body[key] = out


# ------------------------------------------------------------------ headlamp (photo 07 of both stops)
def lamp_contour(photo, box, seed, mode):
    """Headlamp outline in a straight-on front photo (image-left lamp)."""
    im = cv2.imread(photo)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    x0, y0, x1, y1 = box
    if mode == "bright":      # clear lens: low saturation, bright (+ amber bulb area)
        m = ((S < 70) & (V > 150)) | ((H >= 5) & (H <= 25) & (V > 150))
        k = 7
    else:                     # red car: everything that is not red paint
        m = ~(((H <= 12) | (H >= 160)) & (S > 110) & (V > 60))
        k = 5
    sub = np.zeros(H.shape, np.uint8)
    sub[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    if mode != "bright":
        sub = cv2.morphologyEx(sub, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    sub = cv2.morphologyEx(sub, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(sub)
    cnt, _ = cv2.findContours((lab == lab[seed[1], seed[0]]).astype(np.uint8) * 255, cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_NONE)
    return max(cnt, key=cv2.contourArea)[:, 0, :].astype(float)


P07 = os.path.join(PH, "07-front.jpg")
C12 = lamp_contour(P07, (430, 500, 740, 720), (560, 600), "bright")
C11 = lamp_contour(os.path.join(PH11, "07-front.jpg"), (400, 500, 730, 730), (560, 600), "red")
# Lamp spans (both lamps segmented the same way): 996.1 photo outer 1061 / inner 549 px,
# centre 956.5; 996.2 photo outer 1053 / inner 541 px, centre 986.5 (ratios 0.517 / 0.514).
SPAN11, SPAN12, CX11, CX12 = 1061.0, 1053.0, 956.5, 986.5
TOP11, TOP12 = C11[:, 1].min(), C12[:, 1].min()
S21 = SPAN11 / SPAN12
m12 = np.c_[CX11 + (C12[:, 0] - CX12) * S21, TOP11 + (C12[:, 1] - TOP12) * S21]   # 996.2 → 996.1 photo


def dense(poly, step=0.5):
    out = []
    for (a, b), (c, d) in zip(poly[:-1], poly[1:]):
        n = max(2, int(math.hypot(c - a, d - b) / step))
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append((a + (c - a) * t, b + (d - b) * t))
    out.append(poly[-1])
    return np.array(out)


UNIT = dense(LAMP11_F)


def nearest(q, ref):
    return np.sqrt(((q[:, None, :] - ref[None, :, :]) ** 2).sum(2)).min(1)


def r_t1(p):
    q = np.c_[C11[:, 0] * p[0] + p[2], C11[:, 1] * p[1] + p[3]]
    inv = np.c_[(UNIT[:, 0] - p[2]) / p[0], (UNIT[:, 1] - p[3]) / p[1]]
    return np.r_[nearest(q, UNIT), nearest(inv, C11) * p[0]]


p0 = [103 / np.ptp(C11[:, 0]), 64 / np.ptp(C11[:, 1]), 0.0, 0.0]
p0[2] = 217 - C11[:, 0].min() * p0[0]
p0[3] = 1098 - C11[:, 1].min() * p0[1]
T1 = least_squares(r_t1, p0, loss="soft_l1", f_scale=1.0).x          # 996.1 photo → 996.1 drawing
T1_RMS = float(np.sqrt(np.mean(r_t1(T1) ** 2)))
lamp_draw = np.c_[m12[:, 0] * T1[0] + T1[2], m12[:, 1] * T1[1] + T1[3]]  # 996.2 lamp in drawing px
lamp_draw = np.array(simplify([[float(a), float(b)] for a, b in lamp_draw], 0.6))

# Lamp split. The upper part of the 996.2 (Turbo) lamp fills the 996.1 wing opening — its top
# and outer outline coincide with the 996.1 unit (check-lamp.png) — while its lower lobe
# ("rounded off at the bottom") turns down into the new bumper (photo 01, side: the lamp
# sliver bends down at x ≈ 0.36 and ends at x 0.324, y 0.566; photo 22). A flat lens cannot
# follow that bend: on the 996.1 plane the lobe would sit 10 cm in front of the nose. So,
# as on the 996.1 (whose lower amber band is the `indicator-front` decal), the part of the
# lamp above the 996.1 unit's bottom line (drawing y 1150 px → 0.608 m) is the 3D lamp on
# the 996.1 lens plane (pitch 64.2°, yaw 14°), and the lobe below it is the
# `indicator-front` front decal (clear lens: the 996.2 indicators are clear, geometry.json 12).
SPLIT_PY = 1150.0
h11 = base["headlight"]
Y_ = math.radians(h11["yaw"])
P_ = math.radians(h11["pitch"])
PITCH12 = h11["pitch"]
N = np.array([-math.cos(Y_) * math.cos(P_), math.sin(P_), math.sin(Y_) * math.cos(P_)])   # car coords
C0 = np.array(h11["centre"], float)
U_HAT = np.array([-math.sin(Y_), 0.0, -math.cos(Y_)])
V_HAT = np.array([math.sin(P_) * math.cos(Y_), math.cos(P_), -math.sin(P_) * math.sin(Y_)])


def lift(z, y):
    return np.array([C0[0] + (N[1] * (y - C0[1]) + N[2] * (z - C0[2])) / (-N[0]), y, z])


def clip_y(poly, y_cut, keep_above):
    """Clip a closed polygon (drawing px, y down) by the horizontal line y = y_cut."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina = (a[1] <= y_cut) == keep_above
        inb = (b[1] <= y_cut) == keep_above
        if ina:
            out.append(tuple(a))
        if ina != inb:
            t = (y_cut - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), y_cut))
    return out


LAMP_UPPER = clip_y([tuple(p) for p in lamp_draw], SPLIT_PY, True)
LAMP_LOBE = clip_y([tuple(p) for p in lamp_draw], SPLIT_PY, False)
lamp3 = np.array([lift(Zf(px), Yf(py)) for px, py in LAMP_UPPER])
lamp_c = lamp3.mean(axis=0)
lamp_outline = [[round(float(np.dot(p - lamp_c, U_HAT)), 4), round(float(np.dot(p - lamp_c, V_HAT)), 4)]
                for p in lamp3]
# Lobe decal in the front plane [z, y], ordered like the other front boxes: inner-bottom,
# up the inner side, outward along the top (the split line), down the outer side, back.
_lobe = [[round(Zf(px), 4), round(Yf(py), 4)] for px, py in LAMP_LOBE]
_ymin = min(p[1] for p in _lobe)
_i0 = min((i for i in range(len(_lobe)) if _lobe[i][1] <= _ymin + 0.003), key=lambda i: _lobe[i][0])
LOBE_F = _lobe[_i0:] + _lobe[:_i0]
if LOBE_F[1][0] > LOBE_F[0][0]:        # must head inboard (up the inner side) first
    LOBE_F = [LOBE_F[0]] + LOBE_F[1:][::-1]

# ------------------------------------------------------------------ front apron (photo 07)
K07, CX07, LID07 = 806.0, 984.0, 665.0


def fz(u):
    return round(abs(u - CX07) / K07, 4)


def fy(v):
    return round(0.608 - (v - LID07) / K07, 4)


def fpts(points):
    return [[fz(u), fy(v)] for u, v in points]


# Order: inner-bottom corner, up, outward along the top, down, back along the bottom.
INTAKE_OUT = [(775, 934), (775, 870), (778, 850), (775, 838), (760, 826), (720, 821), (650, 820), (550, 821),
              (500, 825), (488, 840), (495, 856), (512, 872), (525, 900), (540, 915), (560, 922), (620, 928),
              (700, 932)]
INTAKE_BAR = [(770, 869), (770, 858), (700, 858), (600, 857), (520, 856), (500, 859), (505, 866), (520, 869)]
INTAKE_MID = [(984, 936), (984, 868), (775, 868), (775, 934)]
# No front plate: the tracing front photo (07) has none (photo 08 carries a US plate on a
# holder); plate-front of the 996.1 drawing dissolves in the 11 → 12 morph.

# ------------------------------------------------------------------ rear (photos 11, 12)
# Photo 12 (standard oval tailpipes): tail-lamp inner edges x 560 / 1372 px ↔ z ±0.393 m
# (996.1 drawing, lamps carried over) → 1033 px/m, centre 966; lamp bottom y 765 ↔ 0.659 m.
# Oval tips centred x 487 / 1447 → z 0.465 m; ×1.043 (the same measurement on the 996.1 photo
# 10 gives 0.483 m where the drawing has 0.504 m) → 0.485 m. Height as the 996.1 (drawing).
# Tip 0.115 × 0.06 m → round equivalent r 0.042 m.
EXHAUST_Z, EXHAUST_R = 0.485, 0.042
# Raised arch-to-arch brace below the plate recess: its lower edge crease at y ≈ 1050 px in
# photo 12 → 0.383 m, running out to the arches (|z| ≤ 0.80 m).
BRACE = [[0.0, 0.383], [0.40, 0.384], [0.62, 0.39], [0.76, 0.40], [0.80, 0.41]]

# ------------------------------------------------------------------ decals
DROP = {"indicator-side", "indicator-front"}   # amber bands gone (clear lamps); the lobe re-adds indicator-front
decals = []
for d in base["decals"]:
    if d["id"] in DROP:
        continue
    d = json.loads(json.dumps(d))
    if d["id"] == "side-marker":
        d["color"] = "#dfe3e6"                 # clear lens (photos 24, 28)
    if d["id"] == "indicator-rear":
        d["color"] = "#cfd3d6"                 # clear upper band (photos 11, 23)
    if d["id"] == "badge-rear":
        # "Carrera" script sits lower on the 996.2 lid, level with the lamps' lower band
        # (photo 12: centre y 738 px → 0.685 m, x 845–1085 px → ±0.116 m; photo 11 agrees),
        # the 996.1's is level with the lamp tops (photo 10, drawing).
        d["points"] = [[0.0, 0.678], [0.0, 0.692], [0.116, 0.692], [0.116, 0.678]]
    if d["id"] in ("intake-front", "plate-front", "intake-front-centre", "intake-bar-front"):
        continue
    decals.append(d)
FRONT = [-0.05, 0.45]
decals += [
    {"id": "intake-front", "plane": "front", "kind": "fill", "points": fpts(INTAKE_OUT), "finish": "satin",
     "color": "#141516", "stripes": [0.012, 0.35], "depth": FRONT, "facing": 0.3},
    {"id": "intake-bar-front", "plane": "front", "kind": "fill", "points": fpts(INTAKE_BAR), "finish": "paint",
     "color": "paint", "depth": FRONT, "facing": 0.3},
    {"id": "intake-front-centre", "plane": "front", "kind": "fill", "points": fpts(INTAKE_MID), "finish": "satin",
     "color": "#1b1c1e", "depth": FRONT, "facing": 0.3},
    {"id": "rear-brace", "plane": "rear", "kind": "line", "points": BRACE, "finish": "satin", "color": "#2a2a2a",
     "depth": [L - 0.25, L + 0.05], "facing": 0.3},
    {"id": "indicator-front", "plane": "front", "kind": "fill", "points": LOBE_F, "finish": "lens", "color": "#e3e8eb",
     "depth": [-0.05, 0.5], "facing": 0.2},
]

HEADLIGHT = {
    "centre": [round(float(v), 4) for v in lamp_c],
    "outline": lamp_outline,
    "yaw": h11["yaw"],
    "pitch": round(PITCH12, 1),
    "ring": 0.006,
    "ringColor": "#b9bfc4",
    "ringFinish": "satin",
    "lensColor": "#e4eaee",
    "graphic": "projector",
}
# Re-seat the wing on the 996.2 lamp (its lower edge dips further than the 996.1's), as in
# 11-996-1-1998.py (see 11-996-1-1998.lampseat.py).
_ls = importlib.util.spec_from_file_location("lampseat", os.path.join(HERE, f"{BASE}.lampseat.py"))
lampseat = importlib.util.module_from_spec(_ls)
_ls.loader.exec_module(lampseat)
LAMP_SEAT = lampseat.seat(body, HEADLIGHT)
_push, _depths = lampseat.placement(body, HEADLIGHT, half_section)

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
        # 17-inch Carrera II (geometry.json 12), 205/50 ZR 17 / 255/40 ZR 17 (specs.json 12):
        # slim curved five spokes (photo 24) → closest RIM_DESIGNS entry "twist".
        "front": dict(base["wheels"]["front"], design="twist"),
        "rear": dict(base["wheels"]["rear"], design="twist"),
    },
    "headlight": HEADLIGHT,
    "mirror": base["mirror"],
    "wing": base["wing"],
    "exhausts": [[base["exhausts"][0][0], base["exhausts"][0][1], s * EXHAUST_Z, EXHAUST_R] for s in (1, -1)],
}
with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
    json.dump(car, f, indent=1)

# ------------------------------------------------------------------ calibration for check_car
REF11 = os.path.join("research", "traces", BASE)
cal11 = json.load(open(os.path.join(ROOT, "research", "traces", f"{BASE}.calib.json")))
P01 = os.path.join("research", "photos", STOP, "01-side-left.jpg")
K01 = 1017.2 / 2.35
calib = {
    # 996.1 drawing views (same body; the only 996.2 drawing is the wide C4S): side & plan.
    "side": cal11["side"],
    "top": cal11["top"],
    # Photo 01 (studio side), hubs from rim-edge circle fits; flat hub calibration.
    "side_photo": {"image": P01, "wheelF": [434.5, 973.7], "wheelR": [1451.7, 973.6],
                   "tipF": round(434.5 - FA * K01, 1), "crop": [30, 520, 1900, 1120]},
    # Front / rear: the 996.1 drawing views (same body). The facelift decals are checked on the
    # 996.2 photos separately (check-front-photo.png, check-rear-photo.png): a close-range photo
    # cannot be overlaid orthographically (roof and bumper are at very different distances).
    "front": cal11["front"],
    "rear": cal11["rear"],
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)

# ------------------------------------------------------------------ lamp check: 996.1 vs 996.2 outline
ref_front = Image.open(os.path.join(ROOT, REF11, "ref-front.png")).convert("RGB")
cf = cal11["front"]
sc = 0.0035


def to_ref(z, y):
    return (cf["centreX"] - z / sc, cf["groundY"] - y / sc)


dr = ImageDraw.Draw(ref_front)
for poly, col in ((LAMP11_F, (0, 0, 0)), ([tuple(p) for p in lamp_draw] + [tuple(lamp_draw[0])], (40, 80, 255))):
    dr.line([to_ref(Zf(px), Yf(py)) for px, py in poly], fill=col, width=2)
box = [int(v) for v in (*to_ref(0.85, 0.85), *to_ref(0.25, 0.45))]
lamp_img = ref_front.crop((box[0], box[1], box[2], box[3])).resize(((box[2] - box[0]) * 3, (box[3] - box[1]) * 3))
lamp_img.save(os.path.join(OUT_DIR, "check-lamp.png"))

# ------------------------------------------------------------------ facelift decals on the 996.2 photos
def overlay_photo(photo, plane, to_px, out, crop):
    im = Image.open(photo).convert("RGB")
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.3)
    d = ImageDraw.Draw(im)
    for dec in decals:
        if dec["plane"] != plane:
            continue
        for sgn in (1, -1):
            q = [to_px(sgn * z, y) for z, y in dec["points"]]
            if dec["kind"] != "line":
                q.append(q[0])
            d.line(q, fill=(255, 190, 0), width=2)
    im.crop(crop).save(out)


# Front: photo 07, bumper-face calibration (fz / fy above).
overlay_photo(P07, "front", lambda z, y: (CX07 - z * K07, LID07 + (0.608 - y) * K07),
              os.path.join(OUT_DIR, "check-front-photo.png"), (380, 480, 1600, 1000))
# Rear: photo 12, tail-lamp face calibration (valid near the centre; the lamps' outer ends
# wrap round the corners and appear compressed).
K12, CX12R, LAMPB12 = 1033.0, 966.0, 765.0
overlay_photo(os.path.join(PH, "12-rear.jpg"), "rear", lambda z, y: (CX12R - z * K12, LAMPB12 + (0.659 - y) * K12),
              os.path.join(OUT_DIR, "check-rear-photo.png"), (200, 560, 1720, 1200))

# ------------------------------------------------------------------ photo check
if PHOTOCHECK:
    _spec = importlib.util.spec_from_file_location("photofit", os.path.join(HERE, f"{BASE}.photofit.py"))
    photofit = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(photofit)
    st = photofit.check(car, os.path.join(ROOT, P01), (434.5, 973.7), (1451.7, 973.6), (40, 530, 1880, 1112),
                        os.path.join(OUT_DIR, "check-side-photo-persp-01.png"), facing="left", ground_row=1000,
                        D_grid=(5, 6, 7), Y_grid=[0.7, 0.9, 1.1, 1.3], hub_height=0.303, ends=(80, 1864),
                        U0_grid=(760, 860, 960, 1060, 1160))
    print("photo 01-side-left.jpg", st)

zmax = max(max(p[0] for p in half_section(body, x)) for x in np.linspace(0, L, 700))
print("lamp pitch", round(PITCH12, 1), "3D part x extent", round(float(lamp3[:, 0].min()), 3),
      round(float(lamp3[:, 0].max()), 3), "(photo 01 whole lamp: 0.324–0.631); lobe decal pts", len(LOBE_F))
print("lamp seated over x", [round(v, 3) for v in LAMP_SEAT], "renderer placement pushes the lens out by (mm)",
      round(_push * 1000), "probe depths (mm)", [None if d is None else round(d * 1000) for d in _depths])
print("wrote", STOP, "width", round(2 * zmax, 4), "T1 rms (drawing px)", round(T1_RMS, 2),
      "lamp centre", [round(float(v), 3) for v in lamp_c], "lamp drawing y", round(float(lamp_draw[:, 1].min()), 1),
      round(float(lamp_draw[:, 1].max()), 1))
