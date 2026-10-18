---
name: vale-reel
description: Edit a vertical talking-head clip into a Vale Studio reel — set up the project kit, transcribe with WhisperX, build a tight cut, storyboard every beat for approval, render graphics/captions/sound in the Vale style, and finish in Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro or CapCut (or as a finished MP4). Use when the user wants to edit, cut, storyboard, caption or render a reel, or set up a new Vale video project.
---

# Vale reel pipeline

Everything this skill needs ships in `kit/` next to this file. The look itself is defined by the **vale-style** skill; read it (and `kit/STYLE.md`) before designing anything on screen.

## 0. Set up the project (once per project folder)

The scripts expect to live inside the project, with `raw/`, `transcript/`, `renders/` and `storyboard/` beside them. If the current project has no `scripts/` folder yet:

1. Copy everything inside `kit/` into the project root (don't overwrite files the user already has; ask first).
2. Rename `CLAUDE.template.md` to `CLAUDE.md` (or merge it into an existing one) and fill in the machine notes at the top.
3. Make `raw/`, `transcript/`, `renders/`, `references/`.
4. Check the tools (see "Requirements" below) and tell the user what's missing. Don't install system packages without asking.
5. Install the fonts in `brand/fonts/` (macOS: copy to `~/Library/Fonts`). Helvetica Neue ships with macOS.
6. Ask where the user finishes. Premiere: follow `PREMIERE.md`. DaVinci Resolve (Studio or free), Final Cut Pro or CapCut: follow `FINISHING.md`. No app: the finished MP4 from step 5 is the deliverable.

## Pipeline for a new clip

Put the clip in `raw/<clip>.<ext>`. All commands run from the project root.

1. **Transcribe:** `<whisperx-venv>/bin/python scripts/transcribe.py raw/<clip>.mp4` → `transcript/<clip>/words.json`. First run `scripts/download_models.sh` (large-v3-turbo + English alignment, resumable curl).
2. **Cut:** add the clip's false starts and stutters to the `DROP` dict in `scripts/make_cuts.py`, then `python3 scripts/make_cuts.py <clip>` → `cuts.json` and `frames.json`. Show the user the kept text and **get approval**.
3. **Storyboard before anything renders:**
   1. Write `storyboard/<clip>/plan.json`: direction, look, and beats in raw seconds, each with shot, what happens, rows (card, sound, captions, UI) and mock frames. `kit/storyboard/IMG_9225/plan.json` is a worked example.
   2. `python3 scripts/storyboard.py <clip>` builds `storyboard/<clip>/v<N>/` (edit times from the cut, kept words, a graded raw frame and mock frames per beat). Mock-frame kinds: card, caption, prompt, note, split, hand, calendar; add a kind in `scripts/storyboard.py` when a plan needs one.
   3. Show it to the user. If you can publish Claude artifacts, publish `storyboard/storyboard.html` as their Storyboard page (it reads beats from the artifact database and frames from its asset store). Otherwise show the frames directly.
   4. The user replies with one sentence plus notes on single beats. Redraw as v<N+1>.
   5. **Render only after the user approves.**
4. **Voice:** `presets/audio/vale_voice.sh raw/<clip>.mp4 <out.wav>` (80 Hz HPF, denoise, de-ess, 2.5:1, -14 LUFS / -1 dBTP), then mux into `renders/<clip>_master.*`.
5. **Render:** write `storyboard/<clip>/render_v<N>.py` from the example in `kit/storyboard/IMG_9225/render_v1.py`. It builds `base.mp4` (cut + LUT + any split shift), one transparent `timeline.html` overlay captured frame by frame with `style-lab/render/render.mjs` (headless Chrome over CDP), and `sfx.wav` from the synthesised sounds in `style-lab/round*/`. Composite at constant frame rate (`-fps_mode cfr`; without it frames drop at card cuts) and finish at -14 LUFS.
6. **Finish in the user's app.** Other apps: follow `FINISHING.md` (Resolve Studio live, Final Cut via FCPXML, CapCut and free Resolve via a layered handoff; all untested so far). Premiere: write `storyboard/<clip>/premiere_v<N>.py` from `kit/storyboard/IMG_9225/premiere_v1.py` (render → encode → plan), then build the sequence with the connector as described in `PREMIERE.md`. V1 speaker, V2 graphics, V3 captions, A2 sfx, then `apply_lut` per V1 clip.

Older single-pass styles (`scripts/render_style.py <style> <clip>`, `presets/styles/*`) still work but are reference only; `STYLE.md` wins.

## Frame-accuracy rules

- Snap every cut to the clip's frame grid (`frames.json` does this). Variable-frame-rate phone clips go on a 30 fps timeline by seconds.
- Some MP4s carry an edit list that shifts frame 0; check with ffprobe if ffmpeg and Premiere disagree by one frame.
- When setting source in/out in Premiere, pass mid-frame times `(frame + 0.5) / fps`; Premiere rounds down.

## Requirements

- macOS, Apple Silicon tested. ffmpeg/ffprobe on PATH. Python 3.11 (uv works well) with a WhisperX venv for transcription; numpy for the render scripts.
- Google Chrome at `/Applications/Google Chrome.app` and Node 22+ (built-in WebSocket) for `render.mjs`. No npm installs.
- For step 6, one of: Adobe Premiere Pro 2025/2026 (tested), DaVinci Resolve Studio 21.1+ or free, Final Cut Pro, CapCut (untested), or none.
- Reference videos for study go in `references/`; extract frames to study them, never copy their assets. `kit/references/NOTES.md` lists the reels the style was built from.
