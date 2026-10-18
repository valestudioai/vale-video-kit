# Vale editing styles

Each style is a full editing look learned from one creator's reel and rebuilt in Vale Studio's brand: our colours, our fonts and our grade. We take their structure and pacing, not their assets.

| Style | Learned from | In one line | Best for |
|---|---|---|---|
| [noske-cards](noske-cards/STYLE.md) | Tom Noske, reels Defg87-BF9r and DeXygzfBUta | Minimal: 1 to 2 word bold lowercase cream captions, full-screen Ink and Paper word cards, kinetic and quote cards, alternating framing | **Main style to replicate.** Talking-head reels |
| [justyn-editorial](justyn-editorial/STYLE.md) | justyn.ai, reel DeUUFJQu8cw | Magazine feel: serif karaoke captions on Umber plates, huge serif keyword, bold-caps-over-italic title stacks, note cards | Founder stories, brand pieces |
| [cooperson-split](cooperson-split/STYLE.md) | jasoncooperson, reel DdovWa7D35X | Split screen: Ink graphics panel on top, speaker below, spaced mono captions on the seam | Explainers, offers, anything with a list or a product |
| [herk-bold](herk-bold/STYLE.md) | nateherkai, reel DdT_OwyFeoj | Punchy: 1 to 3 word heavy uppercase captions on Ink blocks, punch-ins on key lines, numbered beats | Tips, listicles, fast hooks |

All three share:
- The Vale Warm Natural LUT (`presets/look/Vale_Warm_Natural.cube`).
- The -14 LUFS voice chain (`presets/audio/vale_voice.sh`).
- The export preset (`presets/export/`).

Render any style onto a cut:

```bash
~/.cache/video-editor/whisperx-venv/bin/python scripts/render_style.py noske-cards
```

This writes `renders/<style>/overlays/*.png`, `placements.json`, and a preview at `renders/<style>/BETTER_<style>.mp4`.
