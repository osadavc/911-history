"""Overlay a traced car definition on its reference images.

usage: python research/tools/check_car.py <stop-id>
reads   src/data/cars/<stop-id>.json          (the car definition)
        research/traces/<stop-id>.calib.json  (how each reference view is calibrated)
writes  research/traces/<stop-id>/check-<view>.png

calib.json:
{
  "side":  {"image": "...", "wheelF": [x,y], "wheelR": [x,y], "tipF": x, "crop": [x0,y0,x1,y1]},
  "top":   {"image": "...", "tipF": x, "tipR": x, "centreY": y, "crop": [...]},
  "front": {"image": "...", "centreX": x, "groundY": y, "left": x, "right": x, "width": m, "crop": [...]},
  "rear":  {"image": "...", "centreX": x, "groundY": y, "left": x, "right": x, "width": m, "crop": [...]}
}
Side calibration uses the car's own wheelbase and front tyre radius.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from trace_lib import FrontCalib, SideCalib, TopCalib, half_section, mono  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

COL = {
    "top": "#ff2d55",
    "bottom": "#ff9500",
    "crest": "#34c759",
    "belt": "#007aff",
    "roof": "#af52de",
    "side": "#5ac8fa",
    "decal": "#ffcc00",
    "wheel": "#00c7be",
    "lamp": "#ff3b30",
}


def load(stop):
    with open(os.path.join(ROOT, "src", "data", "cars", f"{stop}.json")) as f:
        car = json.load(f)
    with open(os.path.join(ROOT, "research", "traces", f"{stop}.calib.json")) as f:
        calib = json.load(f)
    return car, calib


def open_view(spec):
    im = Image.open(os.path.join(ROOT, spec["image"])).convert("RGB")
    # Fade the reference so overlays read clearly.
    im = Image.blend(im, Image.new("RGB", im.size, "white"), 0.35)
    return im


def save(im, spec, stop, view):
    if spec.get("crop"):
        im = im.crop(tuple(spec["crop"]))
    out_dir = os.path.join(ROOT, "research", "traces", stop)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"check-{view}.png")
    im.save(path)
    print("wrote", os.path.relpath(path, ROOT), im.size)


def stations(car, n=220):
    L = car["length"]
    return [L * i / (n - 1) for i in range(n)]


def side_view(car, spec, stop, name="side"):
    body = car["body"]
    tyre_r = car["wheels"]["front"]["diameter"] / 2
    cal = SideCalib(spec["wheelF"], spec["wheelR"], car["rearAxle"] - car["frontAxle"], tyre_r, spec["tipF"])
    # Shift so the car's own frontAxle is honoured (tipF defines x = 0).
    im = open_view(spec)
    d = ImageDraw.Draw(im)
    P = lambda x, y: cal.to_px(x, y)
    xs = stations(car)
    tops, bots = [], []
    lines = {k: [] for k in ("rocker", "crest", "belt", "roof", "top")}
    for x in xs:
        sec = half_section(body, x)
        ys = [p[1] for p in sec]
        tops.append(P(x, max(ys)))
        bots.append(P(x, min(ys)))
        lines["rocker"].append(P(x, mono(body["rockerY"], x)))
        lines["crest"].append(P(x, mono(body["crestY"], x)))
        lines["belt"].append(P(x, mono(body["beltY"], x)))
        lines["roof"].append(P(x, mono(body["roofY"], x)))
        lines["top"].append(P(x, mono(body["topY"], x)))
    d.line(tops, fill=COL["top"], width=2)
    d.line(lines["rocker"], fill=COL["bottom"], width=2)
    d.line(lines["crest"], fill=COL["crest"], width=1)
    d.line(lines["belt"], fill=COL["belt"], width=1)
    d.line(lines["roof"], fill=COL["roof"], width=1)
    d.line(lines["top"], fill=COL["top"], width=1)
    for axle, key in ((car["frontAxle"], "front"), (car["rearAxle"], "rear")):
        r = car["wheels"][key]["diameter"] / 2
        cx, cy = P(axle, r)
        rp = r / cal.scale
        d.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], outline=COL["wheel"], width=2)
        rr = car["wheels"][key]["rim"] / 2 / cal.scale
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=COL["wheel"], width=1)
    for dec in car["decals"]:
        if dec["plane"] != "side":
            continue
        pts = [P(x, y) for x, y in dec["points"]]
        if dec["kind"] != "line":
            pts.append(pts[0])
        d.line(pts, fill=COL["decal"], width=1)
    hx, hy, _ = car["headlight"]["centre"]
    X, Y = P(hx, hy)
    d.ellipse([X - 4, Y - 4, X + 4, Y + 4], outline=COL["lamp"], width=2)
    save(im, spec, stop, name)


def top_view(car, spec, stop):
    body = car["body"]
    cal = TopCalib(spec["tipF"], spec["tipR"], spec["centreY"], car["length"])
    im = open_view(spec)
    d = ImageDraw.Draw(im)
    xs = stations(car)
    for side in (1, -1):
        outline = []
        for x in xs:
            sec = half_section(body, x)
            outline.append(cal.to_px(x, max(p[0] for p in sec), side))
        d.line(outline, fill=COL["side"], width=2)
        for key, col in (("crestZ", COL["crest"]), ("beltZ", COL["belt"]), ("roofZ", COL["roof"])):
            d.line([cal.to_px(x, mono(body[key], x), side) for x in xs], fill=col, width=1)
        for dec in car["decals"]:
            if dec["plane"] != "top":
                continue
            pts = [cal.to_px(x, z, side) for x, z in dec["points"]]
            if dec["kind"] != "line":
                pts.append(pts[0])
            d.line(pts, fill=COL["decal"], width=1)
        # wheels as rectangles
        for axle, key, track in ((car["frontAxle"], "front", car["trackFront"]), (car["rearAxle"], "rear", car["trackRear"])):
            w = car["wheels"][key]
            r = w["diameter"] / 2
            z0 = track / 2 - w["width"] / 2
            z1 = track / 2 + w["width"] / 2
            a = cal.to_px(axle - r, z0, side)
            b = cal.to_px(axle + r, z1, side)
            d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], outline=COL["wheel"], width=1)
    save(im, spec, stop, "top")


def end_view(car, spec, stop, view):
    body = car["body"]
    cal = FrontCalib(spec["centreX"], spec["groundY"], spec["left"], spec["right"], spec["width"])
    im = open_view(spec)
    d = ImageDraw.Draw(im)
    L = car["length"]
    # Silhouette of the half of the car nearest the viewer, plus key sections.
    if view == "front":
        rng = [x for x in stations(car, 300) if x <= L * 0.62]
        keys = [car["frontAxle"] * 0.35, car["frontAxle"], car["frontAxle"] + 0.55]
    else:
        rng = [x for x in stations(car, 300) if x >= L * 0.38]
        keys = [L - 0.25, car["rearAxle"], car["rearAxle"] - 0.6]
    pts = []
    for x in rng:
        pts.extend(half_section(body, x))
    by_y = {}
    for z, y in pts:
        k = round(y / 0.01)
        by_y[k] = max(by_y.get(k, 0.0), z)
    sil = sorted((k * 0.01, z) for k, z in by_y.items())
    for side in (1, -1):
        d.line([cal.to_px(side * z, y) for y, z in sil], fill=COL["side"], width=2)
        for x, col in zip(keys, (COL["crest"], COL["belt"], COL["roof"])):
            sec = half_section(body, x)
            d.line([cal.to_px(side * z, y) for z, y in sec], fill=col, width=1)
        for dec in car["decals"]:
            if dec["plane"] != view:
                continue
            p = [cal.to_px(side * z, y) for z, y in dec["points"]]
            if dec["kind"] != "line":
                p.append(p[0])
            d.line(p, fill=COL["decal"], width=1)
        track = car["trackFront"] if view == "front" else car["trackRear"]
        w = car["wheels"]["front" if view == "front" else "rear"]
        a = cal.to_px(side * (track / 2 - w["width"] / 2), 0)
        b = cal.to_px(side * (track / 2 + w["width"] / 2), w["diameter"])
        d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], outline=COL["wheel"], width=1)
    if view == "front":
        lamp = car["headlight"]
        _, ly, lz = lamp["centre"]
        for side in (1, -1):
            # Outline u is image-right for the image-left lamp; mirrored for the other.
            outline = [cal.to_px(side * lz - side * u, ly + v) for u, v in lamp["outline"]]
            outline.append(outline[0])
            d.line(outline, fill=COL["lamp"], width=2)
    save(im, spec, stop, view)


def main():
    stop = sys.argv[1]
    car, calib = load(stop)
    if "side" in calib:
        side_view(car, calib["side"], stop)
    if "side_photo" in calib:
        side_view(car, calib["side_photo"], stop, "side-photo")
    if "top" in calib:
        top_view(car, calib["top"], stop)
    for view in ("front", "rear"):
        if view in calib:
            end_view(car, calib[view], stop, view)


if __name__ == "__main__":
    main()
