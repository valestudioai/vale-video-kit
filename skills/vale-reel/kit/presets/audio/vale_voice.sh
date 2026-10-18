#!/usr/bin/env bash
# Vale Studio voice chain (brand/BRAND.md > Audio): clean up and master a talking-head voice for social.
#   high-pass 80 Hz -> gentle denoise -> de-ess -> light compression -> two-pass loudness to -14 LUFS / -1 dBTP
# Usage: presets/audio/vale_voice.sh input.(mp4|wav) output.wav
# Video is untouched; this writes a 48 kHz WAV to lay under the cut, or to mux back in with ffmpeg.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
in="$1"; out="$2"

# afftdn delays the audio by 25 ms; the atrim/apad pair pulls it back so it stays in sync with picture.
CHAIN="highpass=f=80:poles=2,afftdn=nr=8:nf=-50:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.025,deesser=i=0.35:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2dB:knee=4"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")

# Pass 1: measure after the chain.
stats=$(ffmpeg -hide_banner -nostats -i "$in" -vn -af "$CHAIN,loudnorm=I=-14:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$stats" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }

# Pass 2: apply with the measured values (linear mode keeps the voice's natural dynamics).
ffmpeg -hide_banner -v error -y -i "$in" -vn \
  -af "$CHAIN,loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true" \
  -t "$dur" -ar 48000 -c:a pcm_s24le "$out"

ffmpeg -hide_banner -nostats -i "$out" -af "ebur128=peak=true" -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:" | sed 's/^ */  /'
