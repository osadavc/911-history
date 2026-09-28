"""Trace: 18-992-2-2024 — 911 Carrera Coupé, type 992 second phase (992.2), 2024-today.

No official 992.2 drawing exists, and the vendor 5-view in research/blueprints/18-992-2-2024
prints the 992.1 length (4,519) and measures WB/L 1.6 % off, so it is used only for
proportions of the new aprons. The body is the 992.1 trace (research/traces/17-992-1-2019.py:
`trace_992_shell`, the same shell: "Proven roof designs adopted unchanged", carry-over
wings, doors, glass and bonnet) placed at the official 992.2 dimensions, with the
documented facelift differences (research/geometry.json 18-992-2-2024, history.md) taken
from the 992.2 photos in research/photos/18-992-2-2024:
  - front: apron lights deleted (all functions in the Matrix-LED lamps), larger horizontal
    intakes with two blades, plate on a new holder with a high-gloss sensor panel below
    (P15 official straight front, P17 street front with EU plate, vendor front view);
  - rear: redesigned light strip with the 'PORSCHE' lettering integrated in it, higher
    number plate above a black lower section, oval tailpipes in the diffuser fins, grille
    with five fins per side (P19 official straight rear, P20, P36, vendor rear view);
  - unchanged: glasshouse, doors, flush handles, fuel flap (P04), mirrors, lamp housings.

Official dimensions (research/specs.json: Porsche press kit / EU spec sheet MY S 05/2024):
  L 4,542  W 1,852  H 1,302  WB 2,450  tracks 1,597 / 1,551 mm,
  tyres 235/40 ZR 19 on 8.5J / 295/35 ZR 20 on 11.5J.
Placement of the 992.1 shell:
  length: 4,542 mm = 992.1's 4,519 + 23 mm "from new front and rear aprons" (geometry.json);
      the split is not published and could not be measured (the profile photos' unknown
      principal point moves a photo-derived overhang by 1-3 cm per 100 px): 11.5 mm each.
  height: 1,302 mm (EU) vs 1,298 -> RIDE = +0.004 m.

Run: <venv>/bin/python research/traces/18-992-2-2024.py
"""
import importlib.util
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("t17", os.path.join(HERE, "17-992-1-2019.py"))
t17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t17)
t15 = t17.t15

STOP = "18-992-2-2024"
RIDE = 0.004
D_FRONT = D_REAR = t17.D_FRONT - 0.0115     # each overhang 11.5 mm longer than the 992.1's

# P19 (official straight rear, 992.2 GTS: body, light strip, lid and plate position shared
# with the Carrera): EU plate 922-1175 px = 520 mm -> 2.055 mm/px, centre line u 1048.5;
# heights relative to the red strip line (v 467), placed at the 992.1 bar height (both vendor
# drawings put the bar at 0.77 m; the profile photos scatter +-2.5 cm) plus RIDE.
P19_S, P19_CX, P19_RED_V = 0.002055, 1048.5, 467.0
RED_Y = t17.BAR_Y + RIDE


def p19(u, v):
    return [round(abs(u - P19_CX) * P19_S, 3), round(RED_Y - (v - P19_RED_V) * P19_S, 3)]


# New aprons in plan: the vendor 992.2 plan view (tips 45 / 813 px, centre row 806) against the
# vendor 992.1 plan (tips 50.5 / 826.5, centre 628), each normalised to its own half-width
# 0.45 m behind the tip, gives the 992.2's nose and tail narrower near the tips (more rounded
# corners around the larger intakes): ratio at 0.03 / 0.06 / 0.10 / 0.15 / 0.20 / 0.30 m from
# the tip = nose 0.88 / 0.93 / 0.96 / 0.935 / 0.93 / 0.986, tail 0.85 / 0.925 / 0.97 / 0.914 /
# 0.93 / 0.965 (+-1.2 % reading noise). Smoothed factors applied to every z curve:
NOSE_F = [(0.0, 0.90), (0.10, 0.94), (0.20, 0.935), (0.30, 0.975), (0.45, 1.0)]
TAIL_F = [(0.0, 0.87), (0.10, 0.94), (0.20, 0.93), (0.30, 0.965), (0.45, 1.0)]
Z_KEYS = ("rockerZ", "sideZ", "crestZ", "beltZ", "roofZ")


def apron_plan(body, L):
    def factor(x):
        if x < 0.45:
            return float(np.interp(x, [a for a, _ in NOSE_F], [b for _, b in NOSE_F]))
        if x > L - 0.45:
            return float(np.interp(L - x, [a for a, _ in TAIL_F], [b for _, b in TAIL_F]))
        return 1.0
    for k in Z_KEYS:
        keys = sorted(set([p[0] for p in body[k]] + [round(v, 4) for v in np.linspace(0, 0.45, 10)] +
                          [round(L - v, 4) for v in np.linspace(0, 0.45, 10)]))
        body[k] = [[x, round(t17.mono(body[k], x) * factor(x), 4)] for x in keys]


def build():
    shell = t17.trace_992_shell()
    c = t17.Ctx(shell, RIDE, D_FRONT, D_REAR)
    L, FA, RA = c.L, c.FA, c.RA
    apron_plan(c.body, L)
    sx, sy, sxt, plane = c.sx, c.sy, c.sxt, c.plane
    t17.shell_decals(c)

    # 992.1 car-space x (photo-derived details) -> 992.2 car space.
    L17 = round(t15.remap_overhangs(shell["L"], shell, t17.D_FRONT, t17.D_REAR), 4)
    FA17 = round(t15.remap_overhangs(shell["FA"], shell, t17.D_FRONT, t17.D_REAR), 4)
    RA17 = round(t15.remap_overhangs(shell["RA"], shell, t17.D_FRONT, t17.D_REAR), 4)

    def from17(x):
        if x <= FA17:
            return round(x * FA / FA17, 4)
        if x <= RA17:
            return round(x - FA17 + FA, 4)
        return round(RA + (x - RA17) * (L - RA) / (L17 - RA17), 4)

    # ---- side ----------------------------------------------------------------------------
    # Fuel flap on the right front wing (P04 official profile shows it on the carry-over wing).
    fcx, fcy = FA + 0.345, 0.815 + RIDE
    c.decals.append({"id": "fuel-flap", "plane": "side", "kind": "line", "side": "right",
                     "points": [[round(fcx + 0.09 * math.cos(a), 4), round(fcy + 0.052 * math.sin(a), 4)]
                                for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 17)],
                     "finish": "satin", "color": "#2a2a2a", "depth": [0.6, 2]})
    # Light strip wrapping into the flank: same wing, same outline as the 992.1 (P04: housing
    # 0.765-0.826 m, P02 0.68-0.76 m: within the photos' +-2.5 cm scatter of the 992.1 values).
    plane("taillight-side", "side", [[from17(a), round(b + RIDE, 4)] for a, b in t17.LIGHT_SIDE_M], "lens",
          "#8e1814", depth=[0.5, 2], facing=0.3)
    # No apron light strip any more (indicator-side / indicator-front dissolve).

    # ---- top: rear grille with five fins per side + centre brake light, a graphic unit with
    # the rear window (geometry.json; P20, P29, P33): same black field as the 992.1.
    plane("engine-grille", "top", [[sxt(705), 0.0], [sxt(705), 0.40], [sxt(770), 0.42], [sxt(770), 0.0]],
          "satin", "#34373b", facing=0.3, depth=[0.85, 2],
          # Lengthwise louvres (geometry.json: "vertical/longitudinal louvres"; 992: nine
          # slats per side). Pitch ≈ 3 cm read from the lid close-ups (16/25, 17/27) and the
          # 992.1 studio plan view (17/22-top). Slats dark grey, gaps near-black.
          stripes=[0.03, 0.45], stripeAxis="b")

    # ---- front (lowest point first, clockwise in the [z, y] plot) ------------------------------
    # Heights from the vendor 992.2 front view (roof y 80 = 1.302 m, 5.936 mm/px; its lamp centre
    # y 180 = 0.708 m matches the 992.1's 0.704) cross-checked on P17 (EU plate 110 mm = 62 px,
    # camera about lamp height) and P15; widths from the vendor view and P15 (lamp spacing).
    fd = [-0.05, 0.62]
    # Larger outer intakes with two horizontal blades (vendor x 905-975 / y 230-268 px ->
    # z 0.40-0.82, 0.19-0.41 m; P17 0.20-0.425 m; P15 z 0.39-0.81).
    plane("intake-front", "front", [[0.40, 0.195], [0.40, 0.415], [0.60, 0.418], [0.80, 0.415], [0.82, 0.35],
                                    [0.815, 0.24], [0.78, 0.198]], "satin", "#1f2123", stripes=[0.073, 0.15],
          depth=fd, facing=0.2)
    # High-gloss black sensor panel below the plate (geometry.json; P15 x 820-1045 -> z +-0.31;
    # vendor: two round sensors at 0.24-0.35 m).
    plane("intake-front-centre", "front", [[0.0, 0.19], [0.0, 0.305], [0.30, 0.305], [0.31, 0.19]], "glass",
          "#141517", depth=fd, facing=0.2)
    # Licence plate on the new holder: top level with the intakes' top (P17), EU 520 x 110 mm.
    plane("plate-front", "front", [[0.0, 0.305], [0.0, 0.415], [0.26, 0.415], [0.26, 0.305]],
          "satin", "#d9dcdf", depth=fd, facing=0.2)
    # Black lower lip (vendor rows 268-280 -> 0.115-0.186 m).
    plane("bumper-front-face", "front", [[0.0, 0.115], [0.0, 0.188], [0.80, 0.188], [0.84, 0.16], [0.80, 0.115]],
          "satin", "#1b1c1e", depth=[-0.05, 0.45], facing=0.2)

    # ---- rear (P19 via p19(); lowest point first, clockwise) -----------------------------------
    rd = [L - 0.75, L + 0.05]
    # Dark carrier of the light strip with the integrated 'PORSCHE' lettering (P19 carrier
    # v 457-497, lettering v 480-491 over u 908-1189 -> z +-0.29): drawn below the red line.
    plane("badge-rear", "rear", [[0.0, p19(0, 497)[1]], [0.0, p19(0, 471)[1]], [0.62, p19(0, 471)[1]],
                                 [0.62, p19(0, 497)[1]]], "satin", "#2e3033", depth=rd, facing=0.2)
    # Full-width red strip line (reflector-band slot): P19 v 464-470, to u 713 (z 0.69).
    plane("reflector-band", "rear", [[0.0, p19(0, 470)[1]], [0.0, p19(0, 464)[1]], [0.69, p19(0, 464)[1]],
                                     [0.69, p19(0, 470)[1]]], "lens", "#b3201a", depth=rd, facing=0.15)
    # End units with the integrated light arc (P19 u 681-713 inward to the body edge, v 457-497).
    plane("taillight", "rear", [p19(700, 497), p19(713, 488), p19(713, 462), p19(700, 457), p19(640, 458),
                                p19(626, 470), p19(628, 486), p19(650, 496)], "lens", "#8e1814",
          depth=rd, facing=0.15)
    # Higher number plate above the black lower section (P19 v 568.6-621 px -> 0.46-0.57 m).
    plane("plate-rear", "rear", [[0.0, p19(0, 621)[1]], [0.0, p19(0, 568.6)[1]], [0.26, p19(0, 568.6)[1]],
                                 [0.26, p19(0, 621)[1]]], "satin", "#d9dcdf", depth=rd, facing=0.2)
    # Red reflectors at the outer corners of the black lower section (P19 u 662-749, v 632-648;
    # vendor rear view 0.39-0.46 m).
    plane("reflector-rear", "rear", [p19(749, 648), p19(749, 632), p19(662, 632), p19(662, 648)], "lens",
          "#a51d18", depth=rd, facing=0.2)
    # Black lower rear section with the diffuser fins (P19 top edge v 650 -> 0.40 m).
    top_black = p19(0, 650)[1]
    plane("bumper-rear-face", "rear", [[0.0, 0.13], [0.0, top_black], [0.84, top_black], [0.90, 0.36],
                                       [0.90, 0.20], [0.84, 0.13]], "satin", "#1c1d1f",
          depth=[L - 0.45, L + 0.05], facing=0.2)

    car = {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.597,
        "trackRear": 1.551,
        "body": c.body,
        "decals": c.decals,
        # Same tyre sizes as the 992.1 (0.671 / 0.7145 m); the standard 'Carrera' wheel on the
        # official US-gallery Carrera (P01) and the street car P17 has ten spokes in five pairs
        # -> twin-spoke, silver (the media-drive car P04/P34 wears an optional 5-spoke design).
        "wheels": {
            "front": {"diameter": round(0.4826 + 2 * 0.235 * 0.40, 4), "width": 0.235, "rim": 0.4826,
                      "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
            "rear": {"diameter": round(0.508 + 2 * 0.295 * 0.35, 4), "width": 0.295, "rim": 0.508,
                     "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
        },
        # Matrix-LED lamp with the four-point signature and all light functions (geometry.json;
        # P15, P30) in the carry-over round housing.
        "headlight": None,
        "mirror": None,
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # One large oval tailpipe each side set into the diffuser fins (geometry.json; P20, P36):
        # z +-0.42 (P20), 0.30 m (P19 diffuser pipe centres v 695).
        "exhausts": [[round(L - 0.05, 4), p19(0, 695)[1], 0.42, 0.05], [round(L - 0.05, 4), p19(0, 695)[1], -0.42, 0.05]],
    }
    ref17, _ = t17.build()
    lamp = dict(ref17["headlight"])
    lamp["centre"] = [round(from17(lamp["centre"][0]), 4), round(lamp["centre"][1] + RIDE, 4), lamp["centre"][2]]
    lamp["lensColor"] = "#d0d9e1"
    car["headlight"] = lamp
    mirror = dict(ref17["mirror"])
    mirror["at"] = [round(from17(mirror["at"][0]), 4), round(mirror["at"][1] + RIDE, 4), mirror["at"][2]]
    car["mirror"] = mirror
    return car


def main():
    car = build()
    out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
    with open(out, "w") as f:
        json.dump(car, f, indent=1)
    vend = os.path.join(ROOT, "research", "blueprints", STOP,
                        "vec-30945_porsche-911-carrera-s-2025_5view-dims-watermarked.jpg")
    rel = os.path.relpath(vend, ROOT)
    tyre_r = car["wheels"]["front"]["diameter"] / 2
    # Vendor 992.2 5-view, used for checks only: upper side view hubs (rim-lip circle fits)
    # 222.28/240.70 and 631.64/240.49; its length scale is off (see docstring), so check-side
    # shows the proportion differences. Front / rear views: centre 1043, sides 887-1199 px.
    s_v = 2.450 / (631.64 - 222.28)
    calib = {
        "side": {"image": rel, "wheelF": [222.28, 240.70], "wheelR": [631.64, 240.49],
                 "tipF": 222.28 - car["frontAxle"] / s_v, "crop": [30, 70, 850, 310]},
        "top": {"image": rel, "tipF": 45.0, "tipR": 813.0, "centreY": 806.0, "crop": [30, 620, 850, 990]},
        "front": {"image": rel, "centreX": 1043.0, "groundY": 80 + 1.302 / (1.852 / 312), "left": 887,
                  "right": 1199, "width": 1.852, "crop": [860, 70, 1230, 310]},
        "rear": {"image": rel, "centreX": 1043.0, "groundY": 373 + 1.302 / (1.852 / 312), "left": 887,
                 "right": 1199, "width": 1.852, "crop": [860, 365, 1230, 600]},
    }
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    print("wrote", os.path.relpath(out, ROOT), "length", car["length"], "axles", car["frontAxle"], car["rearAxle"])
    # Photo check on the official 992.2 Carrera profile P04 (nose right; rim-lip circle fits
    # 1248.91/1011.71 and 597.28/1005.66; camera at about hub height per sources.json).
    t15.perspective_side_check(car, os.path.join(ROOT, "research", "photos", STOP, "04-side-right.jpg"),
                               (1248.91, 1011.71, 597.28, 1005.66), 14.0,
                               os.path.join(ROOT, "research", "traces", STOP, "check-photo-side.png"),
                               crop=[300, 720, 1520, 1120], flip=True, u0=923.1, v0=1008.7)


if __name__ == "__main__":
    main()
