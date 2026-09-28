"""Overlay a labeled pixel grid on an image (optionally cropped/zoomed) for reading coordinates.
usage: grid.py in.jpg out.png [--crop x0 y0 x1 y1] [--step 50] [--zoom 1.0]
Labels always show ORIGINAL image pixel coordinates."""
import sys, argparse
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--crop", nargs=4, type=int)
ap.add_argument("--step", type=int, default=50)
ap.add_argument("--zoom", type=float, default=1.0)
a = ap.parse_args()
im = Image.open(a.inp).convert("RGB")
x0, y0 = 0, 0
if a.crop:
    x0, y0, x1, y1 = a.crop
    im = im.crop((x0, y0, x1, y1))
if a.zoom != 1.0:
    im = im.resize((int(im.width * a.zoom), int(im.height * a.zoom)), Image.LANCZOS)
d = ImageDraw.Draw(im, "RGBA")
try:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
except Exception:
    font = ImageFont.load_default()
z = a.zoom
step = a.step
minor = step / 5
# minor lines
gx = (x0 // minor) * minor
while gx < x0 + im.width / z:
    X = (gx - x0) * z
    major = abs(gx % step) < 1e-6
    d.line([(X, 0), (X, im.height)], fill=(255, 0, 255, 150) if major else (0, 255, 255, 55), width=1)
    if major:
        d.text((X + 2, 2), str(int(gx)), fill=(255, 0, 255, 255), font=font)
        d.text((X + 2, im.height - 14), str(int(gx)), fill=(255, 0, 255, 255), font=font)
    gx += minor
gy = (y0 // minor) * minor
while gy < y0 + im.height / z:
    Y = (gy - y0) * z
    major = abs(gy % step) < 1e-6
    d.line([(0, Y), (im.width, Y)], fill=(255, 0, 255, 150) if major else (0, 255, 255, 55), width=1)
    if major:
        d.text((2, Y + 1), str(int(gy)), fill=(255, 0, 255, 255), font=font)
        d.text((im.width - 34, Y + 1), str(int(gy)), fill=(255, 0, 255, 255), font=font)
    gy += minor
im.save(a.out)
print(im.size)
