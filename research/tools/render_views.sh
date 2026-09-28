#!/bin/bash
# Render a traced car (or a morph between cars) from five angles into one contact sheet.
# usage: research/tools/render_views.sh <car-id[,car-id2]> <out.png> [t] [paint-hex]
# Needs `bun run dev` on :3000 (serves /lab and /lab/car?id=...).
set -e
CARS="$1"; OUT="$2"; T="${3:-0}"; PAINT="${4:-c8102e}"
SCRATCH="/private/tmp/claude-501/-Users-osadavc-Documents-Projects-life-of-a-911/d71944a1-cbbb-45c9-a8de-7ebd6ff2edec/scratchpad"
SHOT="$SCRATCH/shot/shot.mjs"
TMP=$(mktemp -d)
i=0
for v in "34:0.7:0.2" "side:1.5708:0.03" "rear34:2.45:0.22" "front:0.0:0.08" "rear:3.1416:0.1" "top:1.5708:1.45"; do
  n=${v%%:*}; r=${v#*:}; az=${r%%:*}; el=${r#*:}
  node "$SHOT" "http://localhost:3000/lab?car=$CARS&t=$T&px=2&az=$az&el=$el&d=10&paint=%23$PAINT" "$TMP/$i.png" --w 1400 --h 700 --wait 2500 >/dev/null 2>&1
  i=$((i+1))
done
ffmpeg -v error -y -i "$TMP/0.png" -i "$TMP/1.png" -i "$TMP/2.png" -i "$TMP/3.png" -i "$TMP/4.png" -i "$TMP/5.png" \
  -filter_complex "[0]crop=1400:600:700:100[a];[1]crop=1400:600:700:100[b];[2]crop=1400:600:700:100[c];[3]crop=1400:600:700:100[d];[4]crop=1400:600:700:100[e];[5]crop=1400:600:700:100[f];[a][b][c]hstack=3[t];[d][e][f]hstack=3[u];[t][u]vstack" "$OUT"
rm -rf "$TMP"
echo "wrote $OUT"
