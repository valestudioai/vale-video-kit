# Vale Studio presets

The brand rules behind these are in `brand/BRAND.md`.

## Audio: `audio/vale_voice.sh`

Voice clean-up and mastering for talking-head social video:
1. 80 Hz high-pass
2. Gentle denoise
3. De-ess
4. 2.5:1 compression
5. Two-pass loudness to **-14 LUFS, -1 dBTP**

```bash
presets/audio/vale_voice.sh raw/BETTER.mp4 transcript/BETTER_voice.wav
```

Tested on BETTER.mp4: the raw clip measured -22.1 LUFS and the output measures -14.2 LUFS with a -1.0 dBTP peak.

In Premiere, without the script, get the same result like this:
- **Essential Sound > Dialogue:** Reduce Noise 3, De-ess 3, Dynamics on with Auto Gain.
- **Export > Effects > Loudness Normalization:** ITU BS.1770-3, Target Loudness -14 LUFS, True Peak -1 dBTP.

## Export: `export/Vale - Social H.264 16 Mbps.epr`

- H.264 Match Source, so frame size and rate follow the sequence. Works for vertical Reels, TikTok and Shorts, and for horizontal YouTube.
- VBR 2-pass, 16 Mbps target and 20 Mbps max.
- AAC 320 kbps at 48 kHz.
- Maximum render quality on.

The preset is already copied to `~/Documents/Adobe/Adobe Media Encoder/25.0/Presets/`. If it doesn't appear in Premiere's Export preset list, import it from the Preset menu (the "..." next to Preset), choose Import Preset, and pick this file.

## Look: `look/Vale_Warm_Natural.cube`

- Warm and natural with soft contrast. Blacks lift slightly toward umber, highlights roll off, and cyans, blues and greens are pulled back. Skin is left alone.
- Built from reference reel 3 (see `references/NOTES.md`).
- Installed in `~/Library/Application Support/Adobe/Common/LUTs/Creative/`, so it appears in **Lumetri Color > Creative > Look**. Fix exposure and white balance in Basic Correction first.
- To change it, edit the strengths at the top of `look/make_lut.py` and rerun it.
- Before and after: `previews/lut_before_after_12s.png`.

## Graphics: `graphics/vale_graphics.py`

Full-frame transparent PNG overlays at 1080×1920. Lay them on V2 or above.

| Function | What it makes | Default position |
|---|---|---|
| `caption(text, emphasis)` | 2 to 4 word phrase on an Umber plate, optional Newsreader Italic word | y 1470, centred (below the shirt logo) |
| `keyword(word)` | One huge Newsreader word in Ink | Top band, y 110 |
| `date_line(parts)` | DM Mono spaced label | y 70, above the keyword |
| `title_stack(line1, line2)` | HANKEN BOLD CAPS over a Newsreader italic line ending in a full stop | Top band, left at x 106 |
| `lower_third(name, role)` | Newsreader name, mono role, Umber plate with a Stone rule | y 1470, left |

For tight talking-head framing like BETTER.mp4, the face, cap and shirt logo fill the middle of the frame. Titles go in the top band and captions and the lower third go in the bottom band, never together. Pass `color=` or `plate_color=` for dark or light footage.

Preview: `previews/graphics_preview.png`. Demos: `graphics/demo/`.
