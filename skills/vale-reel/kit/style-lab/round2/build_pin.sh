#!/usr/bin/env bash
# Pinterest section. Modes:
#   bw      clip in black and white with grain, overlay on top
#   frame   clip shown through the print border (overlay page is the border)
#   overlay clip with overlay on top
#   full    full-screen page, no clip; voice from the clip under it
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p out frames
SRC=footage/img9225_6455.mp4
for p in pin_pages/${ONLY:-*}.html; do
  id=$(basename "$p" .html)
  mode=$(python3 -c "import json;print([c.get('mode') for c in json.load(open('manifest.json'))['cards'] if c['id']=='$id'][0])")
  if [ "$mode" = "full" ]; then node ../render/render.mjs "$p" "frames/$id" 30 >/dev/null
  else node ../render/render.mjs "$p" "frames/$id" 30 1080 1920 --transparent >/dev/null; fi
  case "$mode" in
    bw)    V="[0:v]hue=s=0,eq=contrast=1.18:brightness=-0.02,noise=alls=22:allf=t[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]" ;;
    full)  V="[1:v]format=yuv420p[v]" ;;
    *)     V="[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]" ;;
  esac
  ffmpeg -v error -y -i "$SRC" -framerate 30 -i "frames/$id/%05d.png" -i "audio/${id}_sfx.wav" \
    -filter_complex "$V;[0:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
    -map "[v]" -map "[a]" -frames:v 87 -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -movflags +faststart "out/${id}_full.mp4"
  ffmpeg -v error -y -i "out/${id}_full.mp4" -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset slow -crf 30 -an \
    -movflags +faststart "out/${id}_preview.mp4"
  echo "$id done ($(du -k "out/${id}_preview.mp4" | cut -f1) KB preview)"
done
