"""Trace: 14-997-2-2009 — 911 Carrera Coupé, type 997 second series (MY2009–2012).

The 997.2 is a facelift of the 997.1 (research/geometry.json 14; coordinator brief: derive it
from the 997.1 trace plus the documented differences — no clean 997.2 Carrera 4-view exists).
The body is the 997.1 trace (src/data/cars/13-997-1-2005.json; run 13 first); this script
applies the documented changes, each measured on the 997.2 photos (research/photos/14-997-2-2009/)
against the matching 997.1 photos with the same method, so shared errors cancel:

  * Length 4427 → 4435 mm (specs.json 14; width/height/wheelbase/tracks unchanged). The
    +8 mm come from the revised aprons; no source splits them, so each overhang grows 4 mm.
  * Front: LED daytime-running/position/indicator units replace the 997.1 indicator/fog
    units; larger intakes, the outer ones black with two horizontal struts (geometry.json 14,
    photos 08, 24, 25). Measured on photo 08 (tracing: front) with the same front camera as
    the 997.1 photo 08 (13-997-1-2005.frontcam.py): lamps (ellipse fits 428.4 / 1499.6 px),
    front tyres' outer edges (299 / 1623 px) → D 11.4 m; lid front edge check 0.638 m
    (drawing 0.623; the 997.1 photo gives 0.609 — ±1.5 cm).
  * Rear: LED tail lamps "drawn right into the wing, tapering off to the outside", red with a
    silver-transparent bar; black trim along the bottom of the rear apron; tailpipes integrated
    in it (geometry.json 14, photos 12, 26). Photo 12 is mapped onto the 997.1 photo 11 through
    features the facelift did not change — the lamp inner edges (they abut the same engine lid)
    and the lid's lower shut line: scale 1.0771, centre 950 → 911 px, lid line 659.5 → 589.5 px
    — and then into the 997.1 rear-lamp decal frame (photo 11 lamp inner edge x 520 ↔ z 0.428,
    outer end x 282 ↔ z 0.803; inner top y 497 ↔ 0.779, inner bottom y 603 ↔ 0.646).
    Tailpipes: same size and position as the 997.1 (both photos: centres ±0.439 m).
  * Side: tail lamp (side part) and front light unit from photo 06 (square-on side profile:
    rims 86.6 / 87.2 px), hub calibration (1403.1, 1039.0) / (614.4, 1040.0) px, loaded hub
    height 0.311 m. Side marker, flap, door, glass as the 997.1 (photo 06/01 agree within 1 cm).
  * Mirrors: "larger" (geometry.json 14). Photo 06: housing x 1.774–2.010 m, y 0.902–0.995 m;
    photo 08 (front camera at x 1.9 m): z 0.673–0.844 m, height 0.082 m. (The owner's-manual
    width across mirrors, 1952 mm, would put the tips at ±0.976 m — outside the front-wing
    silhouette in photo 08 where they are clearly inside; the photo is used.)
  * Wheels: standard 18-inch "Carrera IV" twin-blade five-spoke (geometry.json 14 → twin-spoke),
    same tyres 235/40 ZR18 / 265/40 ZR18.
  * Headlamps: shape unchanged (Bi-Xenon, geometry.json 14).

Run: <venv>/python research/traces/14-997-2-2009.py   (PHOTOCHECK=0 skips the photo fit)
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
from trace_lib import half_section  # noqa: E402

STOP = "14-997-2-2009"
BASE = "13-997-1-2005"
PH = os.path.join(ROOT, "research", "photos", STOP)
PH13 = os.path.join(ROOT, "research", "photos", BASE)
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)
PHOTOCHECK = os.environ.get("PHOTOCHECK", "1") == "1"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


frontcam = load_module("frontcam", os.path.join(HERE, "13-997-1-2005.frontcam.py"))
photofit = load_module("photofit", os.path.join(HERE, "11-996-1-1998.photofit.py"))
lampseat = load_module("lampseat", os.path.join(HERE, "11-996-1-1998.lampseat.py"))

base = json.load(open(os.path.join(ROOT, "src", "data", "cars", f"{BASE}.json")))

# ------------------------------------------------------------------ length: +4 mm on each overhang
L13, FA13, RA13 = base["length"], base["frontAxle"], base["rearAxle"]
L = 4.435                       # specs.json 14
DELTA = (L - L13) / 2           # 0.004
FA, RA = FA13 + DELTA, RA13 + DELTA
TRACK_F, TRACK_R = 1.486, 1.534
RIM = 18 * 0.0254
TYRE_F = RIM + 2 * 0.235 * 0.40
TYRE_R = RIM + 2 * 0.265 * 0.40


def sx(x):
    """997.1 car x → 997.2 car x (front overhang ×(FA+δ)/FA, middle +δ, rear overhang stretched)."""
    if x <= FA13:
        return x * FA / FA13
    if x <= RA13:
        return x + DELTA
    return RA + (x - RA13) * (L - RA) / (L13 - RA13)


def r4(pts):
    return [[round(float(a), 4), round(float(b), 4)] for a, b in pts]


body = {k: [[round(sx(x), 4), v] for x, v in c] for k, c in base["body"].items()}

# ------------------------------------------------------------------ front (photo 08 of both stops)
LAMP14 = [round(sx(base["headlight"]["centre"][0]), 4), base["headlight"]["centre"][1],
          base["headlight"]["centre"][2]]
CAM14 = frontcam.FrontCam((428.4, 1499.6), LAMP14[2], LAMP14[0], (299.0, 1623.0), (TRACK_F + 0.235) / 2, FA,
                          (647.7 + 641.9) / 2, LAMP14[1], 1125.5, 0.0)
DEPTH = frontcam.section_depth(body, half_section)
# Image-left half (car's right side), read on zoomed contrast-stretched grids of photo 08.
UNIT_P08 = [(330, 815), (345, 800), (400, 801), (470, 804), (495, 812), (515, 826), (522, 840), (512, 866),
            (450, 869), (380, 869), (340, 866), (328, 850)]
DRL_P08 = [(334, 845), (400, 846), (470, 848), (512, 850), (510, 864), (450, 867), (380, 867), (338, 862)]
INTAKE_OUT_P08 = [(334, 875), (536, 875), (552, 916), (573, 962), (584, 1007), (560, 1016), (450, 1016),
                  (368, 1014), (345, 975), (334, 930)]
STRUT1_P08 = [(338, 913), (552, 913), (556, 922), (340, 922)]
STRUT2_P08 = [(343, 962), (573, 962), (576, 970), (346, 970)]
INTAKE_CTR_P08 = [(633, 932), (962.5, 932), (962.5, 1038), (700, 1037), (665, 1025), (642, 994), (630, 950)]
F08 = {k: frontcam.photo_outline(CAM14, v, DEPTH) for k, v in
       (("unit", UNIT_P08), ("drl", DRL_P08), ("intake_out", INTAKE_OUT_P08), ("strut1", STRUT1_P08),
        ("strut2", STRUT2_P08), ("intake_ctr", INTAKE_CTR_P08))}
LID_EDGE_CHECK = CAM14.hc - (712 - CAM14.v_off) / (CAM14.f / (CAM14.D + 0.161))

# ------------------------------------------------------------------ rear (photo 12 → photo 11 → 997.1 decal frame)
S12, C12, C11, LID12, LID11 = 1.0771, 950.0, 911.0, 659.5, 589.5


def p12_to_p11(u, v):
    return C11 + (u - C12) * S12, LID11 + (v - LID12) * S12


def p11_to_decal(u, v):
    """Photo-11 frame (image-left lamp) → the 997.1 rear-lamp decal frame (vec-1030 based)."""
    z = 0.428 + (520.0 - u) * (0.803 - 0.428) / (520.0 - 282.0)
    y = 0.779 - (v - 497.0) * (0.779 - 0.646) / (603.0 - 497.0)
    return z, y


def rear_outline(pts12):
    out = [p11_to_decal(*p12_to_p11(u, v)) for u, v in pts12]
    return frontcam.order_front(r4(out))


# Photo 12, image-left lamp (car's right): outline and the silver-transparent bar.
TAIL_P12 = [(587, 562), (450, 563), (380, 566), (362, 575), (358, 600), (362, 630), (375, 655), (420, 680),
            (480, 688), (540, 687), (580, 672), (587, 660)]
BAR_P12 = [(565, 595), (390, 596), (378, 604), (376, 616), (382, 628), (395, 634), (565, 635)]
TAIL = rear_outline(TAIL_P12)
BAR = rear_outline(BAR_P12)
# Black lower apron (photo 12: band top y 935 px, 27 px above the tailpipe tops; out to the
# tailpipe surrounds, x 495–1410 px → |z| ≤ 0.54 m), anchored on the tailpipe height (0.23 m).
EX = base["exhausts"][0]
BAND_TOP = round(EX[1] + 0.033 + 27 * S12 / 913.6, 3)
BAND = [[0.0, 0.17], [0.0, BAND_TOP], [0.50, BAND_TOP], [0.54, BAND_TOP - 0.02], [0.555, 0.20], [0.53, 0.17]]

# ------------------------------------------------------------------ side (photo 06, square-on)
K06, HF06, HR06, HUB06 = 788.7 / 2.35, (1403.1, 1039.0), (614.4, 1040.0), 0.311


def p06(u, v):
    return FA + (HF06[0] - u) / K06, HUB06 + (HF06[1] - v) / K06


TAIL_SIDE_P06 = [(440, 905), (430, 910), (400, 916), (370, 920), (340, 924), (322, 924), (318, 918), (322, 900),
                 (335, 885), (350, 878), (380, 885), (410, 893)]
UNIT_SIDE_P06 = [(1640, 997), (1642, 985), (1650, 975), (1680, 973), (1692, 980), (1690, 992), (1670, 998)]


def side_order(poly):
    """Lowest-front point first, clockwise as seen in the side view of a nose-left car."""
    p = [list(v) for v in poly]
    area = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))
    if area > 0:
        p.reverse()
    xs, ys = [v[0] for v in p], [v[1] for v in p]
    i0 = min(range(len(p)), key=lambda i: (p[i][0] - min(xs)) / (np.ptp(xs) or 1) + (p[i][1] - min(ys)) /
             (np.ptp(ys) or 1))
    return p[i0:] + p[:i0]


TAIL_SIDE = side_order(r4([p06(u, v) for u, v in TAIL_SIDE_P06]))
UNIT_SIDE = side_order(r4([p06(u, v) for u, v in UNIT_SIDE_P06]))
MIRROR_X = (p06(1142, 841)[0], p06(1063, 810)[0])
MIRROR_Y = (p06(1142, 841)[1], p06(1063, 810)[1])

# ------------------------------------------------------------------ decals
decals = []
for d in base["decals"]:
    d = json.loads(json.dumps(d))
    if d["plane"] in ("side", "top"):
        d["points"] = r4([[sx(x), v] for x, v in d["points"]])
    if d.get("depth") and d["plane"] in ("front", "rear"):
        d["depth"] = [round(sx(v), 4) if 0 <= v <= L13 + 0.1 else round(v + (2 * DELTA if v > L13 / 2 else 0), 4)
                      for v in d["depth"]]
    decals.append(d)
by_id = {d["id"]: d for d in decals}

FRONT = [-0.05, 0.45]
REAR = [round(L - 0.45, 4), round(L + 0.05, 4)]
CLEAR = "#e4e8ea"
by_id["indicator-front"].update(points=F08["unit"], color=CLEAR)
by_id["intake-front"].update(points=F08["intake_out"], color="#121314")
by_id["intake-front-centre"].update(points=F08["intake_ctr"], color="#121314")
# The body-colour bar becomes the upper black strut (dark grey so it reads against the opening).
by_id["intake-bar-front"].update(points=F08["strut1"], finish="satin", color="#2e3033")
by_id["indicator-side"].update(points=UNIT_SIDE, color=CLEAR)
by_id["taillight-side"].update(points=TAIL_SIDE)
by_id["taillight"].update(points=TAIL)
by_id["indicator-rear"].update(points=BAR, color="#d9dde0")
# Plate and "Carrera" script: photo 12 mapped onto photo 11 and its face scale (see 13):
# plate x 826–1070, y 812–928 px → z ±0.144, y 0.348–0.484; script centre y 616 → 0.715.
def p12_face(u, v):
    u11, v11 = p12_to_p11(u, v)
    return round(abs(u11 - C11) / 913.6, 4), round(0.646 + (606.0 - v11) / 913.6, 4)


by_id["plate-rear"].update(points=[p12_face(950, 928), p12_face(950, 812), p12_face(1070, 812),
                                   p12_face(1070, 928)])
by_id["badge-rear"].update(points=[p12_face(950, 621), p12_face(950, 610), p12_face(1055, 610),
                                   p12_face(1055, 621)])
decals += [
    {"id": "intake-strut-front", "plane": "front", "kind": "fill", "points": F08["strut2"], "finish": "satin",
     "color": "#2e3033", "depth": FRONT, "facing": 0.3},
    # LED daytime running / position lights along the lower part of the front units.
    {"id": "drl-front", "plane": "front", "kind": "fill", "points": F08["drl"], "finish": "emissive",
     "color": "#f4f7fa", "depth": FRONT, "facing": 0.2},
    {"id": "bumper-strip-rear", "plane": "rear", "kind": "fill", "points": r4(BAND), "finish": "satin",
     "color": "#151617", "depth": [round(L - 0.25, 4), round(L + 0.05, 4)], "facing": 0.25},
]

# ------------------------------------------------------------------ headlight, mirror, exhausts
headlight = json.loads(json.dumps(base["headlight"]))
headlight["centre"] = LAMP14
# Seat check (the lamp and the wing are the 997.1's, shifted with the front overhang).
push, depths = lampseat.placement(body, headlight, half_section)

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
        "front": {"diameter": round(TYRE_F, 4), "width": 0.235, "rim": round(RIM, 4), "design": "twin-spoke",
                  "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
        "rear": {"diameter": round(TYRE_R, 4), "width": 0.265, "rim": round(RIM, 4), "design": "twin-spoke",
                 "face": "#c9ccd0", "lip": "#d6d9dc", "caliper": "#202020"},
    },
    "headlight": headlight,
    "mirror": {"at": [round(sum(MIRROR_X) / 2, 4), round(sum(MIRROR_Y) / 2, 4), 0.673],
               "size": [round(abs(MIRROR_X[1] - MIRROR_X[0]), 3), 0.087, 0.171],
               "shape": "aero", "color": "paint", "finish": "paint"},
    "wing": base["wing"],
    "exhausts": [[round(sx(e[0]), 4), e[1], e[2], e[3]] for e in base["exhausts"]],
}
with open(os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json"), "w") as f:
    json.dump(car, f, indent=1)

# ------------------------------------------------------------------ calibration for check_car
V838 = os.path.join("research", "blueprints", STOP, "vec-838_porsche-911-carrera-997-2010_side-top-dims-watermarked.jpg")
K838 = (624.5 - 220.5) / 2.35
calib = {
    # The 997.2 vendor drawing, hubs aligned (its nose then sits 5 cm ahead of the model's:
    # the vendor side views put the wheels ~5 cm too far back, see 13-997-1-2005.md).
    "side": {"image": V838, "wheelF": [220.5, 268.0], "wheelR": [624.5, 268.0],
             "tipF": round(220.5 - FA * K838, 1), "crop": [20, 80, 830, 340]},
    "top": {"image": V838, "tipF": 40.0, "tipR": 804.0, "centreY": 629.0, "crop": [20, 450, 830, 810]},
    # Photo 06 (square-on side profile), flat hub calibration.
    "side_photo": {"image": os.path.join("research", "photos", STOP, "06-side-right.jpg"),
                   "wheelF": list(HF06), "wheelR": list(HR06), "tipF": round(HF06[0] + FA * K06, 1),
                   "crop": [240, 760, 1760, 1160]},
}
with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
    json.dump(calib, f, indent=1)

# ------------------------------------------------------------------ photo overlays of the facelift decals
def overlay(photo, to_px, planes, out, crop):
    im = Image.open(photo).convert("RGB")
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.3)
    d = ImageDraw.Draw(im)
    for dec in decals:
        if dec["plane"] not in planes:
            continue
        for sgn in (1, -1):
            q = [to_px(sgn * a, b, dec) for a, b in dec["points"]]
            if dec["kind"] != "line":
                q.append(q[0])
            d.line(q, fill=(255, 190, 0), width=2)
    im.crop(crop).save(out)


def front_px(z, y, dec):
    x = DEPTH(abs(z), y)
    u, v = CAM14.project(x, y, z)
    return (2 * CAM14.u0 - u, v)      # image-left = car's right (+z)


overlay(os.path.join(PH, "08-front.jpg"), front_px, ("front",), os.path.join(OUT_DIR, "check-front-photo.png"),
        (250, 380, 1700, 1100))


def rear_px(z, y, dec):
    # inverse of p11_to_decal ∘ p12_to_p11 (image-left lamp = car's right, +z)
    u11 = 520.0 - (abs(z) - 0.428) * (520.0 - 282.0) / (0.803 - 0.428)
    v11 = 497.0 + (0.779 - y) * (603.0 - 497.0) / (0.779 - 0.646)
    u12 = C12 + (u11 - C11) / S12
    v12 = LID12 + (v11 - LID11) / S12
    return (u12 if z >= 0 else 2 * C12 - u12, v12)


overlay(os.path.join(PH, "12-rear.jpg"), rear_px, ("rear",), os.path.join(OUT_DIR, "check-rear-photo.png"),
        (250, 400, 1700, 1080))

# ------------------------------------------------------------------ perspective side-photo check
if PHOTOCHECK:
    st = photofit.check(car, os.path.join(PH, "06-side-right.jpg"), HF06, HR06, (250, 770, 1740, 1150),
                        os.path.join(OUT_DIR, "check-side-photo-persp-06.png"), facing="right", ground_row=1143,
                        D_grid=(6, 8, 10, 13, 16, 20), Y_grid=[0.4, 0.6, 0.8, 1.0, 1.2], hub_height=HUB06)
    print("photo 06-side-right.jpg", st)

print("front camera D %.2f m, lid front edge %.3f m (drawing 0.623)" % (CAM14.D, LID_EDGE_CHECK))
print("renderer lamp placement push (mm)", round(push * 1000))
print("wrote", STOP, "L", L, "axles", round(FA, 4), round(RA, 4), "tail lamp z %.3f–%.3f y %.3f–%.3f" % (
    min(p[0] for p in TAIL), max(p[0] for p in TAIL), min(p[1] for p in TAIL), max(p[1] for p in TAIL)))
