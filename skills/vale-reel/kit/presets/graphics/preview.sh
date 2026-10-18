#!/usr/bin/env bash
# Render a contact sheet of the graphics demos over graded frames of a clip, one row per palette.
# Usage: presets/graphics/preview.sh raw/BETTER.mp4 presets/previews/graphics_preview.png
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/../.."
clip="$1"; out="$2"
lut=presets/look/Vale_Warm_Natural.cube
times=(1 2 18 11)
rows=()
for pal in vale forest; do
  demos=(presets/graphics/demo/$pal/1_keyword.png presets/graphics/demo/$pal/2_title_stack.png presets/graphics/demo/$pal/3_note_card.png presets/graphics/demo/$pal/4_lower_third.png)
  args=(); fc=""
  for i in 0 1 2 3; do args+=(-ss "${times[$i]}" -i "$clip"); done
  for i in 0 1 2 3; do args+=(-i "${demos[$i]}"); done
  for i in 0 1 2 3; do fc+="[$i:v]trim=end_frame=1,lut3d=file=$lut[g$i];[g$i][$((i+4)):v]overlay[o$i];"; done
  fc+="[o0][o1][o2][o3]hstack=4,scale=1440:-1"
  ffmpeg -v error -y "${args[@]}" -filter_complex "$fc" -frames:v 1 "/tmp/vale_row_$pal.png"
  rows+=(-i "/tmp/vale_row_$pal.png")
done
ffmpeg -v error -y "${rows[@]}" -filter_complex "vstack=2" -frames:v 1 "$out"
rm -f /tmp/vale_row_*.png
echo "Wrote $out"
