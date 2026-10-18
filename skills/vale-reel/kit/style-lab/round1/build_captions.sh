#!/usr/bin/env bash
# Render caption pages transparent at the footage rate and composite them over the graded BETTER clip.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p out frames
for p in cap_pages/*.html; do
  id=$(basename "$p" .html)
  node ../render/render.mjs "$p" "frames/$id" 23.976 1080 1920 --transparent >/dev/null
  ffmpeg -v error -y -i footage/better_0_29.mp4 -framerate 24000/1001 -i "frames/$id/%05d.png" \
    -filter_complex "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]" -map "[v]" -map 0:a \
    -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -movflags +faststart "out/${id}_full.mp4"
  ffmpeg -v error -y -i "out/${id}_full.mp4" -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset slow -crf 30 -an \
    -movflags +faststart "out/${id}_preview.mp4"
  echo "$id done ($(du -k "out/${id}_preview.mp4" | cut -f1) KB preview)"
done
