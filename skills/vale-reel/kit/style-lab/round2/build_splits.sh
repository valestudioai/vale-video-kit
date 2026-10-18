#!/usr/bin/env bash
# Split screens: render each animated panel transparent at the footage rate, then composite it over BETTER.
#   shift  = speaker moved down 760 px under a hard 940 px panel (black above the shifted shot is covered by the panel)
#   blurbg = same shift, but the top is filled with a blurred, dimmed copy of the shot and the panel floats as a card
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p out frames
SRC=${SRC:-footage/img9225_6455.mp4}
RATE=${RATE:-30}
SHIFT=${SHIFT:-700}
for p in split_pages/*.html; do
  id=$(basename "$p" .html)
  mode=$(python3 -c "import json;print([c.get('mode') for c in json.load(open('manifest.json'))['cards'] if c['id']=='$id'][0])")
  node ../render/render.mjs "$p" "frames/$id" "$RATE" 1080 1920 --transparent >/dev/null
  if [ "$mode" = "blurbg" ]; then
    BASE="[0:v]split[a][b];[a]scale=1242:2208,crop=1080:1920,boxblur=28:2,eq=brightness=-0.18:saturation=0.7[bg];[b]crop=1080:$((1920-SHIFT)):0:0[sh];[bg][sh]overlay=0:$SHIFT[base]"
  else
    BASE="[0:v]crop=1080:$((1920-SHIFT)):0:0,pad=1080:1920:0:$SHIFT:black[base]"
  fi
  ffmpeg -v error -y -i "$SRC" -framerate "$RATE" -i "frames/$id/%05d.png" \
    -filter_complex "$BASE;[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]" -map "[v]" -map 0:a \
    -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -movflags +faststart "out/${id}_full.mp4"
  ffmpeg -v error -y -i "out/${id}_full.mp4" -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset slow -crf 30 -an \
    -movflags +faststart "out/${id}_preview.mp4"
  echo "$id done ($(du -k "out/${id}_preview.mp4" | cut -f1) KB preview)"
done
