"""Trace: 16-991-2-2016 — 911 Carrera Coupé, type 991 second phase (991.2), MY2016–2019.

Same body shell as the 991.1 (research/geometry.json: the facelift changed aprons, lamps,
lid grille, door handles, ride height and wheels only), traced from Porsche's own 991.2
Carrera S dimension drawing in research/traces/15-991-1-2012.py (`trace_991_shell`). This
stop re-uses that shell with the 991.2 ride height and length, and takes the facelift
details directly from the same official drawing (it *is* a 991.2): front apron with the
narrowed light strips and active-flap intakes, 3D taillights, plus the 991.2 photos in
research/photos/16-991-2-2016 (P10 front, P12/P14/P16 rear, P01 side, P05/P16 wheels).

Official dimensions (research/specs.json: porsche.com 2015, PCNA 2017 spec sheet):
  L 4,499  W 1,808  H 1,294  WB 2,450  tracks 1,541 / 1,518 mm,
  tyres 235/40 ZR 19 on 8.5J / 295/35 ZR 19 on 11.5J.
Placement on the drawing (calibration in the stop-15 script):
  ride height: 1,294 mm official vs 1,299 mm measured on the drawing -> RIDE = -0.005 m;
  length: 4,499 vs 4,496.8 mm -> each overhang +1.1 mm (split not published).

Run: <venv>/bin/python research/traces/16-991-2-2016.py
"""
import importlib.util
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("t15", os.path.join(HERE, "15-991-1-2012.py"))
t15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t15)
FZ, FY, X, Y, S = t15.FZ, t15.FY, t15.X, t15.Y, t15.S

STOP = "16-991-2-2016"
RIDE = -0.005
D_FRONT = D_REAR = -0.0011


def of(px, py):
    """Official front view (px) -> [z, y] at the 991.2 ride height."""
    return [round(FZ(px), 3), round(FY(py) + RIDE, 3)]


def orr(px, py):
    """Official rear view (px) -> [z, y] at the 991.2 ride height."""
    return [round(FZ(px, t15.OR_CX), 3), round(FY(py) + RIDE, 3)]


# P12 (Carrera T, straight rear, 1920 px): EU plate 520 mm over 251 px -> 2.07 mm/px across
# and up; anchored on the lamps' inner top (437 px) = the drawing's 0.782 m (OR y 237).
P12_CX, P12_S, P12_TOP = 882.0, 0.00207, 437.0


def p12(px, py):
    return [round(abs(px - P12_CX) * P12_S, 3), round(0.782 + RIDE - (py - P12_TOP) * P12_S, 3)]


def build():
    c = t15.Ctx(RIDE, D_FRONT, D_REAR)
    L, FA, RA = c.L, c.FA, c.RA
    sx, plane = c.sx, c.plane
    t15.shell_decals(c)

    # ---- side ------------------------------------------------------------------------
    # 991.2 door handle: no recess cover (geometry.json; photos 01, 05, 16): only the handle's
    # own outline (the drawing's handle, x 938..1015, y 973..995) as a thin dark rim.
    c.side("door-handle", [(940, 992), (941, 977), (975, 973), (1014, 976), (1015, 988), (978, 994)], "satin",
           "#1d1e20", kind="band", width=0.005, depth=[0.6, 2], facing=0.3)
    # Clear side-marker lens behind the lamp (drawing: 355..432 x 1003..1023).
    c.side("side-marker", [(372, 1022), (357, 1005), (432, 1003), (430, 1010), (412, 1022)], "lens", "#e8e3d6",
           depth=[0.6, 2], facing=0.3)
    # Narrow position/indicator strip wrapping the front corner, side view of the official drawing
    # (rounded bar x 245-300 px, y 1040-1052 px).
    c.side("indicator-side", [(250, 1052), (244, 1046), (250, 1041), (298, 1038), (301, 1046), (295, 1051)], "lens",
           "#e9edf0", depth=[0.4, 2], facing=0.25)
    # 3D tail lamp, side part (official drawing: tip 1355/976, top edge along the shoulder to 1470/960,
    # rear edge x 1478-1480, bottom 1385-1470/988).
    c.side("taillight-side", [(1362, 983), (1355, 976), (1400, 970), (1440, 965), (1470, 961), (1479, 964),
                              (1480, 976), (1476, 987), (1440, 989), (1390, 988)],
           "lens", "#9c1a16", depth=[0.5, 2], facing=0.3)
    # Fuel flap: right front wing, carry-over (geometry.json; drawing/photos show the same wing).
    fcx, fcy, fr = FA + 0.315, 0.78 + RIDE - 0.004, 0.063
    c.decals.append({"id": "fuel-flap", "plane": "side", "kind": "line", "side": "right",
                     "points": [[round(fcx + fr * math.cos(a), 4), round(fcy + fr * math.sin(a), 4)]
                                for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 17)],
                     "finish": "satin", "color": "#2a2a2a", "depth": [0.6, 2]})

    # ---- top -------------------------------------------------------------------------
    # 991.2 lid grille: vertical louvres in high-gloss black (geometry.json; P12, P14, P16,
    # P23) over the lid top, drawing louvre field x 1345..1462 px, P12 width 0.82 m. The body
    # material's stripes only run across the car, so the lengthwise louvres are shown as a
    # black grille field (no stripes).
    plane("engine-grille", "top", [[sx(1345), 0.0], [sx(1345), 0.40], [sx(1462), 0.41], [sx(1462), 0.0]],
          "satin", "#34373b", facing=0.3, depth=[0.85, 2],
          # Lengthwise louvres (geometry.json: "vertical/longitudinal louvres"; 992: nine
          # slats per side). Pitch ≈ 3 cm read from the lid close-ups (16/25, 17/27) and the
          # 992.1 studio plan view (17/22-top). Slats dark grey, gaps near-black.
          stripes=[0.03, 0.45], stripeAxis="b")

    # Porsche crest on the front lid (carry-over lid; position as stop 15, VT of the 991.1).
    plane("crest", "top", [[0.204, 0.0], [0.204, 0.026], [0.257, 0.026], [0.257, 0.0]], "chrome", "#c9a24e",
          facing=0.3, depth=[0.5, 1.0])

    # ---- front (official front view OF; point order: lowest point first, then clockwise
    # in the [z, y] plot) ---------------------------------------------------------------
    front_depth = [-0.05, 0.62]
    # Narrowed position/indicator strip on top of each outer intake (geometry.json): OF band
    # 140..232 px x 313..326 px with a rounded inner end.
    plane("indicator-front", "front", [of(228, 327), of(233, 322), of(228, 316), of(190, 314), of(150, 313),
                                       of(139, 318), of(143, 325), of(185, 327)],
          "lens", "#e9edf0", depth=front_depth, facing=0.2)
    # Outer intakes with active cooling-air flaps (four slats, OF 340/350/362/374 px): frame
    # 137..262 px x 322..386 px, inner edge slanting down to the central opening.
    plane("intake-front", "front", [of(262, 385), of(246, 360), of(230, 330), of(180, 328), of(137, 324),
                                    of(137, 350), of(150, 376), of(180, 386)],
          "satin", "#232528", stripes=[0.038, 0.25], depth=front_depth, facing=0.2)
    # Central intake with two horizontal vanes (OF 280..458 px x 357..386 px).
    plane("intake-front-centre", "front", [[0.0, of(0, 386)[1]], [0.0, of(0, 357)[1]], [0.30, of(0, 357)[1]],
                                     [0.305, of(0, 372)[1]], [0.295, of(0, 386)[1]]],
          "satin", "#1f2123", stripes=[0.048, 0.2], depth=front_depth, facing=0.2)
    # Licence plate (EU 520 x 110 mm) directly above the central intake (P10).
    py0 = of(0, 357)[1]
    plane("plate-front", "front", [[0.0, py0], [0.0, py0 + 0.11], [0.26, py0 + 0.11], [0.26, py0]],
          "satin", "#d9dcdf", depth=front_depth, facing=0.2)
    # Black lower lip (P10; OF lip 400..414 px).
    plane("bumper-front-face", "front", [[0.0, 0.14], [0.0, of(0, 400)[1]], [0.62, of(0, 400)[1]],
                                         [0.74, of(0, 396)[1]], [0.76, 0.19], [0.70, 0.14]],
          "satin", "#1b1c1e", depth=[-0.05, 0.45], facing=0.2)

    # ---- rear (official rear view OR + P12/P14/P16) ------------------------------------
    rear_depth = [L - 0.75, L + 0.05]
    # 3D taillights with the four-point brake light (geometry.json): OR outline 1110..1242 px,
    # top 237 (inner) -> 249 (outer), bottom 262..268 px.
    plane("taillight", "rear", [orr(1180, 268), orr(1236, 266), orr(1242, 250), orr(1238, 237), orr(1180, 242),
                                orr(1120, 248), orr(1110, 256), orr(1118, 263), orr(1150, 268)],
          "lens", "#9c1a16", depth=rear_depth, facing=0.15)
    # "PORSCHE" lettering (P12: 748..1010 px, 2 cm below the lamps' inner top, 3.1 cm tall).
    ly1 = p12(0, 447)[1]
    plane("badge-rear", "rear", [[0.0, ly1 - 0.022], [0.0, ly1], [0.27, ly1], [0.27, ly1 - 0.022]],
          "satin", "#3b3d40", depth=rear_depth, facing=0.2)
    # Rear plate, carry-over position (P12: plate top 118 px below the lamps' inner top).
    pt = p12(0, 555)[1]
    plane("plate-rear", "rear", [[0.0, pt - 0.11], [0.0, pt], [0.26, pt], [0.26, pt - 0.11]],
          "satin", "#d9dcdf", depth=rear_depth, facing=0.2)
    # Low red reflectors with the edge above them (OR 1130..1190 px x 340..350 px; P12 z
    # 0.58-0.80, 0.39-0.42 m).
    plane("reflector-rear", "rear", [orr(1190, 350), orr(1190, 341), orr(1130, 339), orr(1130, 349)],
          "lens", "#a51d18", depth=rear_depth, facing=0.2)
    # Intercooler outlets at the lower corners of the rear fascia (geometry.json; P12, P14:
    # z 0.79-0.87, 0.24-0.33 m).
    plane("vent-rear", "rear", [[0.79, 0.24], [0.79, 0.33], [0.86, 0.33], [0.87, 0.24]],
          "satin", "#141516", depth=[L - 0.45, L + 0.05], facing=0.1)
    # Black lower rear section (P12: z +-0.62, 0.23-0.34 m).
    plane("bumper-rear-face", "rear", [[0.0, 0.17], [0.0, p12(0, 650)[1]], [0.56, p12(0, 650)[1]],
                                       [0.62, 0.30], [0.63, 0.20], [0.58, 0.17]],
          "satin", "#1c1d1f", depth=[L - 0.45, L + 0.05], facing=0.2)

    car = {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.541,
        "trackRear": 1.518,
        "body": c.body,
        "decals": c.decals,
        # 235/40 ZR 19 -> 0.671 m, 295/35 ZR 19 -> 0.689 m; standard 19-inch "Carrera" wheel
        # with five slim twin spokes (geometry.json; photos 05, 16).
        "wheels": {
            "front": {"diameter": round(0.4826 + 2 * 0.235 * 0.40, 4), "width": 0.235, "rim": 0.4826,
                      "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
            "rear": {"diameter": round(0.4826 + 2 * 0.295 * 0.35, 4), "width": 0.295, "rim": 0.4826,
                     "design": "twin-spoke", "face": "#c4c7ca", "lip": "#b9bcbf", "caliper": "#1b1b1b"},
        },
        # Same lamp housing as the 991.1 (drawing); Bi-Xenon with the integrated four-point LED
        # daytime running lights (geometry.json; P10, P21) -> "led4".
        "headlight": {
            "centre": [round(0.49 + 0.0011, 4), round(0.705 + RIDE, 4), 0.682],
            "outline": [[round(0.13 * math.cos(a), 4), round(0.22 * math.sin(a), 4)]
                        for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)],
            "yaw": 8, "pitch": 58, "ring": 0.014, "ringColor": "#c9ced3", "ringFinish": "chrome",
            "lensColor": "#d5dde4", "graphic": "led4",
        },
        "mirror": {"at": [sx(760), c.sy(918), 0.80], "size": [0.24, 0.12, 0.185], "shape": "aero",
                   "color": "paint", "finish": "paint"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # Base Carrera: one oval tailpipe each side (geometry.json; P16).
        "exhausts": [[round(L - 0.04, 4), 0.283, 0.46, 0.042], [round(L - 0.04, 4), 0.283, -0.46, 0.042]],
    }
    return car


def main():
    car = build()
    out = os.path.join(ROOT, "src", "data", "cars", f"{STOP}.json")
    with open(out, "w") as f:
        json.dump(car, f, indent=1)
    tyre_r = car["wheels"]["front"]["diameter"] / 2
    off = os.path.relpath(t15.OFFICIAL, ROOT)
    calib = {
        "side": {"image": off, "wheelF": [t15.FA_X, t15.GROUND_Y - (tyre_r + RIDE) / S],
                 "wheelR": [t15.RA_X, t15.GROUND_Y - (tyre_r + RIDE) / S], "tipF": t15.TIP_X + D_FRONT / S,
                 "crop": [180, 780, 1560, 1200]},
        "top": {"image": os.path.relpath(os.path.join(ROOT, "research", "blueprints", STOP,
                                                      "vec-12233_porsche-911-carrera-s-991-2-2016_4view-dims-watermarked.jpg"), ROOT),
                "tipF": 40, "tipR": 808, "centreY": 627.0, "crop": [10, 440, 840, 820]},
        "front": {"image": off, "centreX": t15.OF_CX, "groundY": t15.END_GROUND - RIDE / t15.END_V,
                  "left": 101, "right": 637, "width": 1.808, "crop": [40, 60, 700, 490]},
        "rear": {"image": off, "centreX": t15.OR_CX, "groundY": t15.END_GROUND - RIDE / t15.END_V,
                 "left": 1090, "right": 1625, "width": 1.808, "crop": [1030, 60, 1690, 490]},
    }
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json"), "w") as f:
        json.dump(calib, f, indent=1)
    print("wrote", os.path.relpath(out, ROOT), "length", car["length"], "axles", car["frontAxle"], car["rearAxle"])
    # Photo check: 991.2 Carrera, left profile P01 (street, close range; hub centres = the
    # wheel crests, read on 2.5x zooms). Of 5 / 7 / 10 m, a 5 m camera distance puts roof,
    # tail and nose on the photo (a close-range shot: the tips shrink towards the centre).
    t15.perspective_side_check(car, os.path.join(ROOT, "research", "photos", STOP, "01-side-left.jpg"),
                               (404, 893, 1462, 892), 5.0,
                               os.path.join(ROOT, "research", "traces", STOP, "check-photo-side.png"),
                               crop=[40, 440, 1880, 1060])


if __name__ == "__main__":
    main()
