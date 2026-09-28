"""Draw polylines/points (pixel coords of the original image) over an image for verification.
usage: overlay.py in.jpg shapes.json out.png [--crop x0 y0 x1 y1] [--zoom z]
shapes.json: {"lines": [{"pts": [[x,y],...], "color": "#ff0000", "closed": false}], "points": [[x,y,"label"],...], "circles": [[cx,cy,r,"#00ff00"]]}"""
import sys, json, argparse
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("shapes"); ap.add_argument("out")
ap.add_argument("--crop", nargs=4, type=int)
ap.add_argument("--zoom", type=float, default=1.0)
a = ap.parse_args()
im = Image.open(a.inp).convert("RGB")
x0 = y0 = 0
if a.crop:
    x0, y0, x1, y1 = a.crop
    im = im.crop((x0, y0, x1, y1))
z = a.zoom
if z != 1.0:
    im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(im, "RGBA")
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
S = json.load(open(a.shapes))
T = lambda p: ((p[0] - x0) * z, (p[1] - y0) * z)
for ln in S.get("lines", []):
    pts = [T(p) for p in ln["pts"]]
    if ln.get("closed"): pts = pts + [pts[0]]
    d.line(pts, fill=ln.get("color", "#ff0000"), width=ln.get("width", 2))
for c in S.get("circles", []):
    cx, cy = T(c[:2]); r = c[2] * z
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c[3] if len(c) > 3 else "#00ff00", width=2)
for p in S.get("points", []):
    X, Y = T(p[:2])
    d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill="#ffea00", outline="#000000")
    if len(p) > 2: d.text((X + 5, Y - 6), str(p[2]), fill="#ffea00", font=font, stroke_width=2, stroke_fill="#000")
im.save(a.out)
print(im.size)
