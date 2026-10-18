---
name: vale-style
description: Vale Studio's locked video style for vertical short-form (Reels, TikTok, Shorts) — colour schemes, type, captions, card motion, split screens, UI cards, sound and what's rejected. Use before designing or reviewing any caption, title, card, animation, grade or sound for a Vale-style reel.
---

# Vale Studio video style

The full source of truth is `../vale-reel/kit/STYLE.md` (relative to this skill's folder). Read it before designing anything. Brand values are in `../vale-reel/kit/brand/BRAND.md` and `../vale-reel/kit/brand/tokens.json`.

If the project you're working in has its own `STYLE.md` (copied in by the vale-reel skill and possibly edited since), that copy wins.

## The short version

- **Feel:** premium but down to earth, educational. Business owners should think "this is for me, and these people know what they're doing" in the first second.
- **Two colour schemes, never mixed:**
  - Monochrome (dark): off-black `#151413`, warm white `#F2EEE8`, logo cream `#E6D8BC` on the key word, film grain.
  - Dusty blue (light): `#3C5182` on pale grey-white `#E4E4DF`, off-black body, blue key word (Caveat handwritten, or Helvetica with a hand-drawn underline).
  - Paper `#F3F1EC` only for the handwritten card (blue ink `#2B3E6E`, Caveat 128px).
- **Type:** Helvetica Neue Bold, lowercase, 150px, tracking -0.035em for big statements. Caveat for handwritten asides.
- **Captions:** Helvetica Neue Bold 96px lowercase, 2 words at a time, soft shadow (optionally one key word in cream), or sentence case Medium 72px, 3 to 4 words. No karaoke highlight.
- **Card motion:** hard cut, smooth rise (28px, 90 ms stagger, 520 ms, cubic-bezier(.2,.8,.2,1)), snappy mask (per word, 60 ms, 240 ms, cubic-bezier(.7,0,.2,1)), filmic focus (24px blur to 0, 104% to 100%, 800 ms).
- **Premium details, sparingly:** "VALE STUDIO" corner label, "01 / 04" index, hairline rule drawing on, the sun mark, film grain, soft shadows on rounded cards.
- **Sound:** soft click, paper slide, film click, short whoosh, breath of air. Big moment = hard cut to a card with a whoosh or film click. Never low thuds. Under -1 dB peak.
- **Grade:** `../vale-reel/kit/presets/look/Vale_Warm_Natural.cube` — warm, natural, soft contrast.
- **Never:** dark grid backgrounds, emoji, stock footage, bouncy pop-ups, glitch/RGB split, condensed uppercase poster type, karaoke captions, low hits.
- **Layout:** design to the tightest safe zone across Reels/TikTok/Shorts. On tight talking-head framing, titles go in the top band and captions in the bottom band, never together.
