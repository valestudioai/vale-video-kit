#!/usr/bin/env bash
# Resumable downloads of the WhisperX models with curl (Hugging Face's own downloader stalls on this connection).
#   faster-whisper large-v3-turbo -> ~/.cache/video-editor/models/faster-whisper-large-v3-turbo
#   English alignment (torchaudio WAV2VEC2_ASR_BASE_960H) -> ~/.cache/torch/hub/checkpoints
set -u
export PATH="$HOME/.local/bin:$PATH"

fetch() {  # url dest: retry until curl finishes, resuming each time
  local url="$1" dest="$2" n=0
  mkdir -p "$(dirname "$dest")"
  until curl -fL --retry 5 --retry-delay 3 --speed-limit 20000 --speed-time 30 -C - -o "$dest.part" "$url"; do
    n=$((n + 1))
    [ "$n" -ge 40 ] && { echo "Giving up on $url"; return 1; }
    echo "Retrying $url ($n)"; sleep 3
  done
  mv "$dest.part" "$dest"
}

M="$HOME/.cache/video-editor/models/faster-whisper-large-v3-turbo"
HF="https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo/resolve/main"
for f in config.json preprocessor_config.json tokenizer.json vocabulary.json model.bin; do
  [ -s "$M/$f" ] || fetch "$HF/$f" "$M/$f" || exit 1
done

A="$HOME/.cache/torch/hub/checkpoints/wav2vec2_fairseq_base_ls960_asr_ls960.pth"
[ -s "$A" ] || fetch "https://download.pytorch.org/torchaudio/models/wav2vec2_fairseq_base_ls960_asr_ls960.pth" "$A" || exit 1

ls -la "$M" "$A"
echo "Models ready."
