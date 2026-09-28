"""GrabCut car segmentation. usage: segment.py in.jpg out_prefix x0 y0 x1 y1 [iters]
Writes <prefix>_mask.png, <prefix>_cut.png (car on magenta) and <prefix>_profile.json with per-column top/bottom rows."""
import sys, json
import numpy as np, cv2
inp, pre = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
iters = int(sys.argv[7]) if len(sys.argv) > 7 else 6
img = cv2.imread(inp)
mask = np.zeros(img.shape[:2], np.uint8)
bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
cv2.grabCut(img, mask, (x0, y0, x1 - x0, y1 - y0), bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
# keep largest component
n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
if n > 1:
    k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]); m = np.where(lab == k, 255, 0).astype(np.uint8)
cv2.imwrite(pre + "_mask.png", m)
cut = img.copy(); cut[m == 0] = (255, 0, 255)
cv2.imwrite(pre + "_cut.png", cut)
prof = {}
for x in range(m.shape[1]):
    ys = np.nonzero(m[:, x])[0]
    if len(ys): prof[x] = [int(ys[0]), int(ys[-1])]
json.dump(prof, open(pre + "_profile.json", "w"))
print("cols", len(prof))
