"""Trace: 06-930-turbo-1975 — 911 Turbo 3.0 Coupé (type 930), MY1975, whale tail.

Spec car (specs.json 06, coordinator: "the 1975 Turbo 3.0 with the whale tail, not the later
3.3 tea tray"): L 4291, WB 2272, H 1320 (specs.json 06; Excellence 1976–77), width 1775 mm
at the rear axle and 1700 mm at the front axle (FIA hom. 645 / FISA B-208 items 203 / 204a,
geometry.json 06), overhangs 932 / 1087 mm (B-208), tracks 1432 / 1501 mm, MY1975 tyres
185/70 VR 15 / 215/60 VR 15 on 7J / 8J x 15 forged Fuchs (specs.json 06; geometry.json 06
tyre_front / tyre_rear "MY1975–76 … Porsche 1976 US technical data").

The Turbo is the G-series shell with flared wings, a deep front spoiler and the whale-tail
wing on a GRP engine lid (geometry.json 06). This script imports the G-series model of
05-g-series-1974.py and applies the documented Turbo differences:
  * plan: front wings 850 mm, rear wings 887.5 mm half-width, flare shapes read off the
    official dd930 plan view (research/blueprints/06…/dd_911-turbo-1986_4view-mm-dims.jpg,
    3.6395 mm/px from its tips 87 / 1266 px), nose and tail from the G-series composite;
  * rear arch lip 4 % larger (dd930 side view: arch top 0.361 m above the axle vs 0.346 m
    on the narrow car's official drawing);
  * deep matt-black front spoiler (dd930 and the Polish 930 plan: lower edge 0.20 m from
    x 0.13 m back to the front arch; Polish "matowy czarny" = matt black);
  * whale-tail wing (tbp-77242 "911 Turbo 930 1977" 4-view and the Polish 930 plan):
    flat top 0.98 m above the ground from where it leaves the lid (x ≈ 3.56 m) to the
    trailing edge 0.066 m ahead of the tail; half-span 0.64 m (tbp-77242 rear view);
  * MY1975 details: black anodised trim, body-colour headlamp rings and mirror (driver's
    door only until MY1988), rectangular fog lamps in the spoiler (photo 08-front), twin
    tailpipes on the left (tbp-77242 rear view), "turbo" script on the lid, black Fuchs.

Run: research/tools/venv python research/traces/06-930-turbo-1975.py
"""
import importlib.util
import json
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("g05", os.path.join(HERE, "05-g-series-1974.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
sys.path.insert(0, os.path.join(ROOT, "research", "tools"))
from trace_lib import silhouette_from_drawing  # noqa: E402

STOP = "06-930-turbo-1975"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)
DD = os.path.join(BP, "dd_911-turbo-1986_4view-mm-dims.jpg")

L, FA = G.L, G.FA
WB = 2.272
RA = round(FA + WB, 4)
HALF_F, HALF_R = 0.850, 0.8875      # 1700 / 1775 mm (hom. 645 item 204a, width)


# ------------------------------------------------------------------ plan
def dd930_plan():
    """Half-width of the official dd930 plan view (x in metres from the tip, h in metres,
    3.6395 mm/px isotropic: tips 87 / 1266 px = 4.291 m; centre row 1213.5). The mean of
    both halves; the door mirrors (x 1.40–1.75 m) and the 1775 mm dimension's extension
    lines (x > 3.30 m) are excluded."""
    g = cv2.imread(DD, cv2.IMREAD_GRAYSCALE)
    g[964:976, 1060:1400] = 255
    m = silhouette_from_drawing(g, (70, 955, 1290, 1470), close=3, thresh=150)
    s = L / (1266 - 87)
    xs, hs = [], []
    for px in range(87, 1267):
        ys = np.nonzero(m[:, px])[0]
        if not len(ys):
            continue
        x = (px - 87) * s
        if 1.40 <= x <= 1.75 or x > 3.30:
            continue
        xs.append(x)
        hs.append(((1213.5 - ys[0]) + (ys[-1] - 1213.5)) / 2 * s)
    return np.array(xs), np.array(hs)


# Rear end of the rear flare (dd930 plan zoom, 10 px grid; outline rows at px 1000 / 1060 /
# 1080 / 1100 → x 3.323 / 3.541 / 3.614 / 3.687 m).
FLARE_TAIL = [(3.323, (1213.5 - 970) * 3.6395e-3), (3.541, (1213.5 - 978) * 3.6395e-3),
              (3.614, (1213.5 - 988) * 3.6395e-3), (3.687, (1213.5 - 1003) * 3.6395e-3)]


def turbo_half_width():
    grid = np.linspace(0, 1, 431)
    xs_g = grid * L
    sc = G.plan_shape(grid)
    nose_tail = np.where(xs_g < 2.0, sc * 0.805, sc * 0.826)   # G-series nose (05) / SC tail (07)
    xs, hs = dd930_plan()
    xs = np.concatenate([xs, [p[0] for p in FLARE_TAIL]])
    hs = np.concatenate([hs, [p[1] for p in FLARE_TAIL]])
    order = np.argsort(xs)
    xs, hs = xs[order], hs[order]
    # scale the drawing to the official axle widths (0.992 front / 0.993 rear)
    k_f = HALF_F / np.interp(FA, xs, hs)
    k_r = HALF_R / np.interp(RA, xs, hs)
    k = np.interp(xs, [FA, RA], [k_f, k_r])
    dd = np.interp(xs_g, xs, hs * k)
    # blend: G-series nose until x 0.20, dd930 0.25–3.60, SC tail beyond 3.72
    w = G.smoothstep(0.20, 0.30, xs_g) * (1 - G.smoothstep(3.62, 3.74, xs_g))
    z = nose_tail + w * (dd - nose_tail)
    z = G.savgol_filter(z, 9, 2)
    return [[round(float(x), 4), round(float(v), 4)] for x, v in zip(xs_g, z)]


# ------------------------------------------------------------------ lower edge
def turbo_bottom():
    """05 lower edge with (a) the deep front spoiler and (b) the rear arch lip scaled 1.04
    about the rear wheel centre (flared arch)."""
    out = []
    rc = (RA, 0.32)
    for x, y in G.SILHOUETTE_BOT:
        if 0.10 < x < 0.54:
            continue
        if RA - 0.40 < x < RA + 0.40 and y > 0.25:
            dx, dy = x - rc[0], y - rc[1]
            x, y = rc[0] + dx * 1.04, rc[1] + dy * 1.04
        out.append([round(x, 4), round(y, 4)])
    # Spoiler: bumper bottom (0.40 m) to x 0.125, vertical front face at x 0.13 (dd930 x 237 px,
    # 3.561 mm/px), lower edge 0.20 m (dd930 y 2290 px; Polish plan y 381 px → 0.205 m)
    # back to x 0.50, rising into the front arch leg (0.536 m, 0.256 m).
    spoiler = [[0.10, 0.40], [0.125, 0.395], [0.135, 0.205], [0.15, 0.200], [0.30, 0.200], [0.45, 0.202],
               [0.50, 0.215], [0.525, 0.24]]
    out += spoiler
    out.sort()
    return out


# ------------------------------------------------------------------ parts
BLACK = "#1b1c1e"
FUCHS_FACE = "#2a2b2d"
FUCHS_LIP = "#d8dadc"
# Fog lamps in the spoiler (photo 08-front, Turbo 3.3 straight front: headlamp centres
# 859 px apart = 2 × 0.628 m → 1.462 mm/px; lamps x 192–308 / 867–983 px, y 925–983 px vs
# the headlamp centre row 678 (0.706 m); the lamps stand ~0.35 m nearer the camera than the
# headlamps → offsets from the image centre ÷ 1.035) → z 0.40–0.56, y 0.28–0.36. The dd930
# front view gives z 0.38–0.55, y 0.31–0.39; the 3.0s in photos 21/22/28 show the same lamps.
FOG = (0.40, 0.56, 0.28, 0.36)
# Whale tail, side profile (WingDef: top surface from (x0, y) to (x1, y + rise), slab
# `thickness`, black rubber lip `lipHeight` standing on the trailing edge):
#  tbp-77242 side view (5.968 mm/px from its 4291 mm length, ground y 229, front axle
#   x 167.6): the top leaves the lid at (600, 67) → x 3.513, y 0.967; flat top to the
#   trailing edge (715, 64) → y 0.985 (rise 0.018 m), lip tip (720, 62) → 0.997; underside
#   at the trailing edge y 76 → thickness 0.072 m; trailing edge 11 px ahead of the tail.
#  Polish 930 plan (3.87 mm/px, ground y 435): flat top 0.983 m, lip ≈ 0.99 m, trailing
#   thickness ≈ 0.058 m, trailing edge 0.071 m ahead of the tail.
#  Press photo 01-side-left: the black rubber border curls up ≈ 0.04 m over the last 0.39 m.
# → x0 3.56 (where the lid centre reaches the wing top), x1 = L − 0.066, y 0.967, rise 0.018,
#   thickness 0.065 (mean trailing thickness of the two drawings), lipHeight 0.025 (between
#   the drawings' ≈ 0.015 and the photo's ≈ 0.04). Half-span 0.64 m: tbp-77242 rear view,
#   wing x 848–1062 px at 5.956 mm/px (1775 mm over x 795–1093).
WING = {"kind": "whale", "x0": 3.56, "x1": round(L - 0.066, 4), "y": 0.967, "halfSpan": 0.64, "lip": "#141414",
        "thickness": 0.065, "rise": 0.018, "lipHeight": 0.025}

BODY = G.gseries_body(turbo_half_width(), bottom=turbo_bottom(), apron=False)


def decals():
    # "turbo" script centred on the lid below the wing (tbp-77242 rear view; photos 12, 16).
    script = G.lid_badge(BODY, 0.68, 0.70, 0.10, "rubber", BLACK)
    d = G.gseries_decals(trim="rubber", trim_color=BLACK, handle=("rubber", BLACK), grille_z=G.RZ(983),
                         rear_script=script, fog=FOG)
    # Matt-black spoiler (Polish plan "matowy czarny"): side face below the bumper and the
    # front face; inserted before the fog lamps so the lenses stay on top.
    spoiler = [
        G.box("side", "spoiler-front", 0.12, 0.54, 0.19, 0.395, "rubber", "#161718", depth=[0.3, 2], facing=0.3),
        G.box("front", "spoiler-front-face", -0.1, 0.80, 0.19, 0.395, "rubber", "#161718", depth=[-0.05, 0.6], facing=0.3),
    ]
    idx = next(i for i, x in enumerate(d) if x["id"] == "fog-front")
    for s in reversed(spoiler):
        s["points"] = [[round(float(a), 4), round(float(b), 4)] for a, b in s["points"]]
        d.insert(idx, s)
    return d


def car():
    wf = {"diameter": round(0.381 + 2 * 0.185 * 0.70, 4), "width": 0.185, "rim": 0.381, "design": "fuchs",
          "face": FUCHS_FACE, "lip": FUCHS_LIP, "caliper": None}
    wr = dict(wf, diameter=round(0.381 + 2 * 0.215 * 0.60, 4), width=0.215)
    return {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.432,
        "trackRear": 1.501,
        "body": BODY,
        "decals": decals(),
        "wheels": {"front": wf, "rear": wr},
        "headlight": G.headlight("paint", "paint"),
        # Body-colour flag mirror on the driver's door (passenger mirror standard from MY1988).
        # dd930 front view: mirror outer edge 934 mm from the centre line (printed).
        "mirror": {"at": [1.68, 0.93, 0.77], "size": [0.08, 0.115, 0.165], "shape": "flag", "color": "paint", "finish": "paint",
                   "sides": "left"},
        "wing": WING,
        # Twin tailpipes on the car's left below the bumper (tbp-77242 rear view pipes at
        # z 0.59 / 0.66; heights as the G-series outlet).
        "exhausts": [[G.EXHAUST[0], G.EXHAUST[1], -0.59, 0.028], [G.EXHAUST[0], G.EXHAUST[1], -0.66, 0.028]],
    }


def calib(c):
    tyre_r = c["wheels"]["front"]["diameter"] / 2
    s_dd = WB / (1100.5 - 462.5)
    # tbp-77242 (1977 3.0 with the whale tail): side wheels at (167.6, 173) / (548.3, 172.2)
    src = os.path.join(OUT_DIR, "src-77242.png")
    Image.open(os.path.join(BP, "tbp-77242_porsche-911-turbo-930-1977_4view.png")).convert("RGB").save(src)
    s77 = L / (734 - 15)
    ps = WB / (1375.5 - 462.9)
    return {
        # Official dd930 side view (3.3 tea tray; body, arches and spoiler as the 3.0).
        "side": {"image": os.path.relpath(DD, ROOT), "wheelF": [462.5, 2349.8 - tyre_r / s_dd],
                 "wheelR": [1100.5, 2349.8 - tyre_r / s_dd], "tipF": 462.5 - FA / s_dd, "crop": [150, 1880, 1480, 2380]},
        # Official press photo of a Turbo 3.0 (green, sky background): hubs = rim-lip fits.
        "side_photo": {"image": os.path.relpath(os.path.join(PH, "01-side-left.jpg"), ROOT),
                       "wheelF": [462.9, 975.6], "wheelR": [1375.5, 974.0], "tipF": 462.9 - FA / ps,
                       "crop": [60, 540, 1880, 1120]},
        "top": {"image": os.path.relpath(DD, ROOT), "tipF": 87, "tipR": 1266, "centreY": 1213.5, "crop": [60, 940, 1300, 1490]},
        # dd930 end views: lateral on the body widths (front 1700 over x 989–1460, rear 1775
        # over x 32–506), vertical from the printed 1310 (roof 31.5 → ground 401).
        "front": G.ref_end_view(STOP, "front", (960, 0, 1500, 420), 1.700 / 471, 1.310 / (402.5 - 37), 1226.0, 402.5,
                                path=DD, half_width=0.85),
        "rear": G.ref_end_view(STOP, "rear", (0, 0, 560, 420), 1.775 / 474, 1.310 / (401 - 31.5), 269.75, 401.0,
                               path=DD, half_width=0.8875),
        "side_77242": {"image": os.path.relpath(src, ROOT), "wheelF": [548.3 - WB / s77, 229 - tyre_r / s77],
                       "wheelR": [548.3, 229 - tyre_r / s77], "tipF": 15, "crop": [0, 0, 750, 240]},
    }


def main():
    c = car()
    cal = calib(c)
    extra = cal.pop("side_77242")
    G.write_outputs(STOP, c, cal)
    return extra


def draw_wing(name, spec, c):
    """check_car.py does not draw the wing: add its side profile (slab + rubber lip) to an
    overlay, the same shape the app extrudes."""
    from PIL import ImageDraw
    from trace_lib import SideCalib
    path = os.path.join(OUT_DIR, f"check-{name}.png")
    im = Image.open(path).convert("RGB")
    cal = SideCalib(spec["wheelF"], spec["wheelR"], c["rearAxle"] - c["frontAxle"], c["wheels"]["front"]["diameter"] / 2, spec["tipF"])
    x0c, y0c = (spec.get("crop") or [0, 0])[:2]
    w = c["wing"]
    th, rise, lip = w.get("thickness", 0.05), w.get("rise", 0.0), w.get("lipHeight", 0.0)
    slab = [(w["x0"], w["y"] - th), (w["x0"], w["y"]), (w["x1"], w["y"] + rise), (w["x1"], w["y"] + rise - th)]
    depth = min(0.04, abs(w["x1"] - w["x0"]) * 0.2)
    lipbox = [(w["x1"] - depth, w["y"] + rise), (w["x1"] - depth, w["y"] + rise + lip), (w["x1"], w["y"] + rise + lip),
              (w["x1"], w["y"] + rise)]
    d = ImageDraw.Draw(im)
    for poly, col in ((slab, "#ff00ff"), (lipbox, "#00ff00")):
        pts = [cal.to_px(x, y) for x, y in poly]
        pts = [(x - x0c, y - y0c) for x, y in pts]
        d.line(pts + [pts[0]], fill=col, width=2)
    im.save(path)


if __name__ == "__main__":
    extra = main()
    subprocess.run([sys.executable, os.path.join(ROOT, "research", "tools", "check_car.py"), STOP], check=True)
    import check_car  # noqa: E402
    car_def, _ = check_car.load(STOP)
    check_car.side_view(car_def, extra, STOP, "side-77242")
    draw_wing("side-77242", extra, car_def)
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json")) as f:
        sp = json.load(f)["side_photo"]
    # Centre-plane overlay of the press photo: bumper tips x 117 / 1811 px, image centre.
    k = G.centre_plane_photo_check(STOP, sp, (tuple(sp["wheelF"]), tuple(sp["wheelR"])), (117, 1811), (960, 717))
    print("centre-plane scale ratio", round(k, 4))
    draw_wing("side-photo", sp, car_def)
