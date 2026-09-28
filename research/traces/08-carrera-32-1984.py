"""Trace: 08-carrera-32-1984 — 911 Carrera 3.2 Coupé, MY1984 (RoW, no spoiler).

Spec car (specs.json 08, coordinator): MY1984 Carrera 3.2 Coupé on forged Fuchs, fog lamps
set into the front apron. Official figures: L 4291, WB 2272, H 1320, width 1652 at the rear
axle / 1610 at the front axle (FIA/FISA B-282 via geometry.json 08), overhangs 932 / 1087 mm,
tracks 1372 / 1380 mm (specs.json 08, MY1984–86), tyres 185/70 VR 15 / 215/60 VR 15 on
6J / 7J x 15 forged Fuchs (specs.json 08).

The Carrera 3.2 body is the SC body (geometry.json 08: "same as SC"; B-282 widths 1610 /
1652), so the shell is the 07 shell (G-series model of 05 with the SC rear wings). The
documented differences from the MY1978 SC reference (geometry.json changes_from_previous_stop):
  * fog lamps built into the front apron (06-front, 26-other, Targa 3-view front view),
  * amber side repeaters on the front wings (MY1984),
  * black anodised window frames / drip rail / handles, body-colour headlamp rings,
  * forged Fuchs wheels (black star, polished lip on the MY1984/85 cars in photos 09 / 13),
  * "Carrera" script on the lid, tracks 1372 / 1380,
  * body-colour electric flag mirrors on both doors (photos of 1984/85 cars 09 and 13 and
    of later cars all show two).

References checked (research/blueprints/08-carrera-32-1984/, research/photos/08-carrera-32-1984/):
  SIDE  vec-1941 vendor 4-view "911 Carrera (1985)" with printed 2272 / 4291 dims: wheels
        (230.5, 280.5) / (622.5, 280.5) = 392 px → 5.796 mm/px; the 4291 dimension spans
        x 70–810 (5.799 mm/px) and gives overhangs 0.931 / 1.088 m (official 0.932 / 1.087).
  PLAN  vec-1941 plan view (tips x 68 / 797, centre row 628.5).
  FRONT tbp-68298 Targa 3-view front view (fog lamps in the apron; lateral 1610 mm over the
        wing outline x 83–500, vertical roof 10 / ground 338 ↔ 1.32 m).
  REAR  vec-1941 rear view (printed 1652 mm width).
  PHOTO 03-side-left (red 3.2 against a plain wall, ~12 m camera distance): hub-aligned
        overlay + centre-plane overlay. The "tracing" photo 01-side-right has strong
        perspective (front rim lip 168 × 184 px, rear 225 × 228 px: the camera is much nearer
        the rear wheel) and 02-side-left is a panned oblique shot (front overhang 0.31 × WB
        vs official 0.41) — neither is used for geometry.

Run: research/tools/venv python research/traces/08-carrera-32-1984.py
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("g05", os.path.join(HERE, "05-g-series-1974.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

STOP = "08-carrera-32-1984"
BP = os.path.join(ROOT, "research", "blueprints", STOP)
PH = os.path.join(ROOT, "research", "photos", STOP)
OUT_DIR = os.path.join(ROOT, "research", "traces", STOP)
os.makedirs(OUT_DIR, exist_ok=True)

L, FA = G.L, G.FA
WB = 2.272                    # geometry.json 08 / B-282
RA = round(FA + WB, 4)
SIDE_Z = G.plan_half_width(0.805, 0.826)   # 1610 / 1652 mm (B-282 items 204a / 204b)
BODY = G.gseries_body(SIDE_Z)

BLACK = "#1b1c1e"             # anodised black trim (rubber finish: satin *lines* render as panel gaps)
FUCHS_FACE = "#2a2b2d"        # black-painted star (photos 09 / 13, 1984–85 cars)
FUCHS_LIP = "#d8dadc"         # polished rim lip

# Fog lamps in the apron below the bumper, outboard under the indicators.
#  photo 06-front (1987 US; wing width 1035 px ↔ 1.610 m → 1.556 mm/px, centre x 903):
#    lamps x 503–600 / 1203–1307 → z 0.47–0.63, ×0.94 for the lamps standing ~0.6 m ahead
#    of the widest wing section (perspective) → 0.44–0.59; heights: bumper bottom y 864
#    (0.398 m), apron bottom y 957 (≈ 0.28 m) → lamp y 883–933 → 0.310–0.374 m.
#  Targa 3-view front view (3.861 mm/px lateral, 4.02 mm/px vertical): x 138.5–181.5,
#    y 241.5–266.5 → z 0.425–0.591, y 0.287–0.388.
FOG = (0.43, 0.59, 0.31, 0.374)
# Side repeater on the front wing just ahead of the door gap, about level with the arch top:
#  Targa 3-view (3.924 mm/px): (343.8, 513) → x 1.326, y 0.679; photo 02-side-left: x 1.288,
#  y 0.678; 1989 French brochure photo: x 1.383, y 0.656 → x 1.30–1.355, y 0.66–0.69.
REPEATER = (1.30, 1.355, 0.66, 0.69)


def decals():
    # "Carrera" script (photo 17-rear: centred, 0.256 m wide, 27 % of the way down the lid
    # from the grille to the reflector strip → centre 0.752 m).
    script = G.lid_badge(BODY, 0.738, 0.766, 0.128, "rubber", BLACK)
    return G.gseries_decals(trim="rubber", trim_color=BLACK, handle=("rubber", BLACK), grille_z=G.RZ(983),
                            rear_script=script, side_repeater=REPEATER, fog=FOG)


def car():
    wf = {"diameter": round(0.381 + 2 * 0.185 * 0.70, 4), "width": 0.185, "rim": 0.381, "design": "fuchs",
          "face": FUCHS_FACE, "lip": FUCHS_LIP, "caliper": None}
    wr = dict(wf, diameter=round(0.381 + 2 * 0.215 * 0.60, 4), width=0.215)
    return {
        "id": STOP,
        "length": L,
        "frontAxle": FA,
        "rearAxle": RA,
        "trackFront": 1.372,
        "trackRear": 1.380,
        "body": BODY,
        "decals": decals(),
        "wheels": {"front": wf, "rear": wr},
        # geometry.json 08: headlight rings in vehicle colour.
        "headlight": G.headlight("paint", "paint"),
        # Body-colour flag mirrors on both doors (photos 09, 13 (1984–85), 06, 16); same
        # housing as the SC (07), outer edge 0.934 m (dd930 front view, printed).
        "mirror": {"at": [1.68, 0.93, 0.77], "size": [0.08, 0.115, 0.165], "shape": "flag", "color": "paint", "finish": "paint"},
        "wing": {"kind": "none", "x0": 0, "x1": 0, "y": 0, "halfSpan": 0, "lip": "#111111"},
        # Single tailpipe on the car's left (photo 17-rear).
        "exhausts": [G.EXHAUST],
    }


def calib(c):
    tyre_r = c["wheels"]["front"]["diameter"] / 2
    s = WB / (622.5 - 230.5)
    ps = WB / (1409.0 - 740.5)
    t3 = os.path.join(BP, "tbp-68298_porsche-911-carrera-targa-1989_3view-colour.png")
    vec = os.path.join(BP, "vec-1941_porsche-911-carrera-1985_4view-dims-watermarked.jpg")
    return {
        "side": {"image": os.path.relpath(vec, ROOT), "wheelF": [230.5, 280.5], "wheelR": [622.5, 280.5],
                 "tipF": 230.5 - FA / s, "crop": [55, 90, 830, 345]},
        # Photo 03-side-left (red 3.2 against a plain wall; its optional whale tail is not
        # modelled): hubs = centres of the polished rim lips read on 10 px grids,
        # (740.5, 653.5) / (1409, 654.5), lip r 64.5 px. Hub-aligned (the body sits on
        # the hubs; the photo car's loaded 16-in tyres give a 0.29 m hub height).
        "side_photo": {"image": os.path.relpath(os.path.join(PH, "03-side-left.jpg"), ROOT),
                       "wheelF": [740.5, 653.5], "wheelR": [1409.0, 654.5],
                       "tipF": 740.5 - FA / ps, "crop": [470, 330, 1760, 760]},
        "top": {"image": os.path.relpath(vec, ROOT), "tipF": 68, "tipR": 797, "centreY": 628.5, "crop": [50, 440, 830, 810]},
        "front": G.ref_end_view(STOP, "front", (60, 0, 530, 345), 1.610 / 417, 1.320 / 328, 291.5, 338, path=t3, half_width=0.805),
        # vec-1941 rear view: widest outline x 910–1196 (printed 1652 mm) → centre 1053,
        # 5.776 mm/px; roof y 531, tyre bottoms y 746 ↔ 1.32 m.
        "rear": G.ref_end_view(STOP, "rear", (880, 520, 1230, 760), 1.652 / 286, 1.320 / (746 - 531), 1053.0, 746,
                               path=vec, half_width=0.826),
    }


def main():
    c = car()
    G.write_outputs(STOP, c, calib(c))


if __name__ == "__main__":
    main()
    subprocess.run([sys.executable, os.path.join(ROOT, "research", "tools", "check_car.py"), STOP], check=True)
    # Centre-plane overlay of photo 03 (see 05 centre_plane_photo_check): bumper tips at
    # x 515 / 1700 give k = 0.939; the principal point x = 1259 follows from both tips (the
    # photo is a crop), y = image centre 445.
    import json
    with open(os.path.join(ROOT, "research", "traces", f"{STOP}.calib.json")) as f:
        sp = json.load(f)["side_photo"]
    k = G.centre_plane_photo_check(STOP, sp, (tuple(sp["wheelF"]), tuple(sp["wheelR"])), (515, 1700), (1259, 445))
    print("centre-plane scale ratio", round(k, 4))
