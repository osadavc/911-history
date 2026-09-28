#!/bin/bash
# Filmstrip of the morph between consecutive stops: t = 0, .25, .5, .75, 1 from the 3/4 view.
# usage: research/tools/render_morphs.sh <out.png> <car-id> <car-id> [<car-id> ...]
set -e
OUT="$1"; shift
SCRATCH="/private/tmp/claude-501/-Users-osadavc-Documents-Projects-life-of-a-911/d71944a1-cbbb-45c9-a8de-7ebd6ff2edec/scratchpad"
SHOT="$SCRATCH/shot/shot.mjs"
TMP=$(mktemp -d)
ids=("$@")
rows=()
for ((k = 0; k < ${#ids[@]} - 1; k++)); do
  pair="${ids[$k]},${ids[$((k + 1))]}"
  frames=()
  for t in 0 0.25 0.5 0.75 1; do
    f="$TMP/$k-$t.png"
    node "$SHOT" "http://localhost:3000/lab?car=$pair&t=$t&px=2&az=0.7&el=0.2&d=10" "$f" --w 1400 --h 700 --wait 2200 >/dev/null 2>&1
    ffmpeg -v error -y -i "$f" -vf "crop=1300:560:750:120,scale=650:-1" "$f.c.png"
    frames+=("-i" "$f.c.png")
  done
  ffmpeg -v error -y "${frames[@]}" -filter_complex "hstack=5" "$TMP/row$k.png"
  rows+=("-i" "$TMP/row$k.png")
done
if [ ${#rows[@]} -gt 2 ]; then
  ffmpeg -v error -y "${rows[@]}" -filter_complex "vstack=$(( ${#rows[@]} / 2 ))" "$OUT"
else
  cp "$TMP/row0.png" "$OUT"
fi
rm -rf "$TMP"
echo "wrote $OUT"
