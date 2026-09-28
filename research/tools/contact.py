"""Contact sheet of every image in a folder: python contact.py <dir> <out.png> [cols] [thumb_w]"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

folder, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 360
th = int(tw * 2 / 3)
files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")))
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 16)), "white")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
for i, f in enumerate(files):
    im = Image.open(os.path.join(folder, f)).convert("RGB")
    im.thumbnail((tw - 4, th - 4))
    x, y = (i % cols) * tw, (i // cols) * (th + 16)
    sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
    draw.text((x + 4, y + th + 1), f[:48], fill="black", font=font)
sheet.save(out)
print(out, len(files), "images")
