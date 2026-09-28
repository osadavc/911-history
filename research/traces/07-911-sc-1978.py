"""Trace: 07-911-sc-1978 — 911 SC 3.0 Coupé, MY1978 (RoW, standard spec).

Spec car (specs.json 07, geometry.json 07 reference_variant, history.md): MY1978 911 SC
Coupé — chrome window surrounds, door handles and headlight rings (MY1978 only), 15-in ATS
cast wheels (6J / 7J x 15, 185/70 VR 15 / 215/60 VR 15), no spoilers, no side repeaters.
Official figures: L 4291, WB 2272, H 1320, width 1652 at the rear axle / 1610 at the front
axle (FISA B-207 via geometry.json 07), overhangs 932 / 1087 mm, tracks 1369 / 1379 mm
(specs.json 07; Porsche 1981 technical data).

The SC shares the G-series shell with 05 (geometry.json 07: "same wider bodyshell as the
911 Carrera"; 1981 US dimension drawing = the same Porsche drawing as the 1975 one). This
script therefore imports the G-series body model of 05 and applies the documented
differences only:
  * rear wings widened by 21 mm per side (1610 → 1652 mm at the rear axle; the plan shape
    of the widening comes from the SC / Carrera 3.2 plan views, see 05 `plan_half_width`),
  * tracks 1369 / 1379 mm, tyres 185/70 VR 15 (0.640 m) / 215/60 VR 15 (0.639 m) on
    6J / 7J x 15 ATS cast wheels (RIM_DESIGNS `ats`),
  * MY1978 details: chrome headlamp rings / window frames / door handles, one
    body-colour electric flag mirror on the driver's door, "911SC" lid script, single
    tailpipe on the left, no fog lamps, no side repeaters.

References checked (research/blueprints/07-911-sc-1978/, research/photos/07-911-sc-1978/):
  SIDE  brochure_1981_911sc_us_techdata_side_dimension_drawing.png (official; the scan is
        squashed vertically: k = 1.0345 from the official height, cross-checked by the rim
        ellipses 55.8 × 58.4 px) — axles at the 36.6 in / 89.5 in extension lines
        x 255.65 / 633.15 → 6.0185 mm/px; ground y 879.
  3VIEW tbp-25361_porsche-911sc-1979_3view.gif — side (wheels 170.5 / 546.5, ground 227.5),
        front / rear views (end-view overlays).
  PLAN  vec-30946 (SC vendor 4-view) — the plan composite input and the top overlay.
  PHOTO 01-side-left.jpg ("tracing": side) — white SC; 05-side-left.jpg — 1981 US SC,
        clean distant profile (hubs from the polished 16-in rim lips); 08-front.jpg,
        18-rear.jpg (details).

Run: research/tools/venv python research/traces/07-911-sc-1978.py
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

STOP = "07-911-sc-1978"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)

L, FA, RA = G.L, G.FA, G.RA
# geometry.json 07 / FISA B-207: wheelbase 2272 (05: 2271). The 1 mm is carried by the
# rear axle position only; the shell is the same.
WB = 2.272
RA = round(FA + WB, 4)

# ------------------------------------------------------------------ body
# Rear wings +21 mm/side (1652 mm at the rear axle); front unchanged (1610 mm).
SIDE_Z = G.plan_half_width(0.805, 0.826)


BODY = G.gseries_body(SIDE_Z)


def body():
    return BODY


# ------------------------------------------------------------------ parts
TYRE_F = round(0.381 + 2 * 0.185 * 0.70, 4)   # 185/70 VR 15 → 0.640
TYRE_R = round(0.381 + 2 * 0.215 * 0.60, 4)   # 215/60 VR 15 → 0.639
ATS_FACE = "#c3c6c9"      # silver-painted cast face (photo 31-detail-wheel)
ATS_LIP = "#d9dbdd"       # polished rim edge

# Door mirror (MY1978: electrically adjustable, body colour, driver's door only — the
# museum SC (08-front) and the 1979 US brochure photo show one). Photo 05-side-left
# (hubs 449.5 / 1396.5 px → 2.3992 mm/px, hub height 0.32 m at y 840): head centre
# (760, 585) → x 1.677, y 0.932; head ≈ 50 × 50 px → 0.12 m. Front photo 08: head
# ≈ 105 × 70 px at ≈ 1.71 mm/px → 0.18 × 0.12 m. Outer edge 0.934 m from the centre line:
# printed on the official dd930 front view for the same electric door mirror (06).
MIRROR = {"at": [1.68, 0.93, 0.77], "size": [0.08, 0.115, 0.165], "shape": "flag", "color": "paint", "finish": "paint",
          "sides": "left"}


def decals():
    # "911SC" script on the lid just below the grille (photos 18-rear, 28/30-detail): in
    # 18-rear it spans x 858–1070 px with the reflector strip (2 × 0.419 m) spanning
    # x 592–1335 → 1.128 mm/px → 0.239 m wide; 13 px below the grille bottom (0.809 m) → centre 0.795 m.
    script = G.lid_badge(BODY, 0.785, 0.805, 0.12, "chrome", G.CHROME)
    return G.gseries_decals(trim="chrome", trim_color=G.CHROME, handle=("chrome", G.CHROME), grille_z=G.RZ(983),
                            rear_script=script)


def car():
    # ATS cast wheel: dished disc with five petal-shaped openings (RIM_DESIGNS `ats`).
    wf = {"diameter": TYRE_F, "width": 0.185, "rim": 0.381, "design": "ats", "face": ATS_FACE, "lip": ATS_LIP, "caliper": None}
    wr = dict(wf, diameter=TYRE_R, width=0.215)
    return {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.369,
        "trackRear": 1.379,
        "body": body(),
        "decals": decals(),
        "wheels": {"front": wf, "rear": wr},
        # MY1978: chrome-plated headlight rings (geometry.json 07 headlights.surround_ring).
        "headlight": G.headlight("#e3e6e9", "chrome"),
        "mirror": MIRROR,
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # Single tailpipe on the car's left (photo 18-rear; same outlet as 05).
        "exhausts": [G.EXHAUST],
    }


# ------------------------------------------------------------------ check references
def gif_to_png(path, name):
    dst = os.path.join(OUT_DIR, f"src-{name}.png")
    Image.open(path).convert("RGB").save(dst)
    return dst


def calib(c):
    tyre_r = c["wheels"]["front"]["diameter"] / 2
    out = {}
    # Official 1981 drawing: isotropic + rear overhang compressed onto the printed 42.8 in.
    sheet = os.path.join(BP, "brochure_1981_911sc_us_techdata_side_dimension_drawing.png")
    k = (1.320 / (879 - 667)) / (WB / (633.15 - 255.65))     # vertical stretch 1.0345
    s = WB / (633.15 - 255.65)                                # 6.0185 mm/px
    arch_px = 633.15 + 0.378 / s                              # rear arch rear leg (as 05)
    tail_px = 819.95                                          # rear extension line
    k_rear = (L - RA - 0.378) / ((tail_px - arch_px) * s)     # 0.950
    img = G.compress_rear(sheet, STOP, "side", arch_px, tail_px, k_rear, vscale=k)
    gy = 879 * k
    out["side"] = {"image": img, "wheelF": [255.65, gy - tyre_r / s], "wheelR": [633.15, gy - tyre_r / s],
                   "tipF": 255.65 - FA / s, "crop": [60, 600, 880, 960]}
    # Photo 05-side-left (1981 US SC on 16-in Fuchs): hubs from the polished rim-lip circle
    # fits (449.5, 838.5) / (1396.5, 841.5), r 84.3 / 81.7 px. Hub-aligned: the body rides on
    # the hubs (the loaded tyre puts the photo's hubs 0.29 m above its ground).
    ps = WB / (1396.5 - 449.5)
    out["side_photo"] = {"image": os.path.relpath(os.path.join(PH, "05-side-left.jpg"), ROOT),
                         "wheelF": [449.5, 838.5], "wheelR": [1396.5, 841.5],
                         "tipF": 449.5 - FA / ps, "crop": [80, 400, 1860, 1000]}
    out["top"] = {"image": "research/blueprints/07-911-sc-1978/vec-30946_porsche-911sc_4view-dims-watermarked.jpg",
                  "tipF": 84, "tipR": 806, "centreY": 629.0, "crop": [60, 440, 850, 810]}
    # SC 3-view end views: front — outline x 24–297 (1610 mm, front wings) → 5.897 mm/px,
    # centre 160.5, roof y 241 / ground y 457 ↔ 1.32 m; rear — outline x 438–714 (1652 mm)
    # → 5.986 mm/px, centre 576, roof 241 / ground 459.
    g3 = gif_to_png(os.path.join(BP, "tbp-25361_porsche-911sc-1979_3view.gif"), "3view")
    out["front"] = G.ref_end_view(STOP, "front", (0, 230, 330, 467), 1.610 / 273, 1.320 / (457 - 241), 160.5, 457,
                                  path=g3, half_width=0.805)
    out["rear"] = G.ref_end_view(STOP, "rear", (415, 230, 743, 467), 1.652 / 276, 1.320 / (459 - 241), 576.0, 459,
                                 path=g3, half_width=0.826)
    return out


def main():
    c = car()
    G.write_outputs(STOP, c, calib(c))


if __name__ == "__main__":
    main()
    subprocess.run([sys.executable, os.path.join(ROOT, "research", "tools", "check_car.py"), STOP], check=True)
    # Centre-plane overlay of photo 05-side-left: bumper tips x 115 (bumper rubber end) / 1815 (rear
    # guard) → k; principal point = image centre (960, 640).
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json")) as f:
        sp = json.load(f)["side_photo"]
    k = G.centre_plane_photo_check(STOP, sp, (tuple(sp["wheelF"]), tuple(sp["wheelR"])), (115, 1815), (960, 640))
    print("centre-plane scale ratio", round(k, 4))
