#!/usr/bin/env bash
# Render every page in pages/ to out/<id>_preview.mp4 (540x960 muted loop, small) and out/<id>_full.mp4 (1080x1920).
# If audio/<id>.wav exists it's muxed into the full version.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p out frames
for p in pages/*.html; do
  id=$(basename "$p" .html)
  [ -n "${ONLY:-}" ] && [[ "$id" != $ONLY ]] && continue
  node ../render/render.mjs "$p" "frames/$id" 30 >/dev/null
  ffmpeg -v error -y -framerate 30 -i "frames/$id/%05d.png" -vf "scale=540:960:flags=lanczos,format=yuv420p" \
    -c:v libx264 -preset slow -crf 30 -an -movflags +faststart "out/${id}_preview.mp4"
  if [ -f "audio/$id.wav" ]; then
    ffmpeg -v error -y -framerate 30 -i "frames/$id/%05d.png" -i "audio/$id.wav" -map 0:v -map 1:a -shortest \
      -vf "format=yuv420p" -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -movflags +faststart "out/${id}_full.mp4"
  else
    ffmpeg -v error -y -framerate 30 -i "frames/$id/%05d.png" -vf "format=yuv420p" -c:v libx264 -preset slow -crf 17 -an \
      -movflags +faststart "out/${id}_full.mp4"
  fi
  echo "$id done ($(du -k "out/${id}_preview.mp4" | cut -f1) KB preview)"
done
