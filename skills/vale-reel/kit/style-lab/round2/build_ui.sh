#!/usr/bin/env bash
# UI cards: render transparent at the footage rate, composite over the graded BETTER clip, mix the click under the voice.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p out frames
SRC=${SRC:-footage/img9225_6455.mp4}
RATE=${RATE:-30}
SHIFT=${SHIFT:-700}
for p in ui_pages/*.html; do
  id=$(basename "$p" .html)
  node ../render/render.mjs "$p" "frames/$id" "$RATE" 1080 1920 --transparent >/dev/null
  ffmpeg -v error -y -i "$SRC" -framerate "$RATE" -i "frames/$id/%05d.png" -i "audio/${id}_sfx.wav" \
    -filter_complex "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v];[0:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -movflags +faststart "out/${id}_full.mp4"
  ffmpeg -v error -y -i "out/${id}_full.mp4" -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset slow -crf 30 -an \
    -movflags +faststart "out/${id}_preview.mp4"
  echo "$id done ($(du -k "out/${id}_preview.mp4" | cut -f1) KB preview)"
done
