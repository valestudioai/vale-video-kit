# Vale Studio brand for video

Read this before adding any on-screen text, graphic, grade or sound to a Vale Studio edit. Machine-readable values are in `brand/tokens.json`. Same values in both files.

Vale Studio is a content marketing agency. Every video should feel **premium, warm and considered**. It must never look like AI slop or a generic creative agency.

## Rules that decide most choices

1. **The talking is the content.** Graphics support what is said and never compete with it. If a graphic doesn't add information, cut it.
2. **Warmth comes from material, not effects.** Use warm neutrals, natural light and real footage. No gradients, glows, emoji, stickers, 3D text or animated backgrounds.
3. **Restraint reads as premium.** Use one text treatment at a time, hard cuts and few effects. When unsure, leave it out.
4. **Be specific.** On-screen text uses real numbers, names and dates, never vague adjectives.

## Colour

| Name | Hex | Use on video |
|---|---|---|
| Ink | `#141313` | Title card backgrounds, lower-third plates, caption shadow |
| Paper | `#FFFFFF` | Caption text, text on Ink |
| Umber | `#5A504A` | Plates and cards on light backgrounds, end-card button |
| Stone | `#9C8979` | Thin rules, progress bars, accent marks. Never for small text over footage |
| Paper warm | `#F4F0EC` | Text on Ink when pure white is too bright (title cards) |
| Stone light | `#BBAEA2` | Secondary text on Ink (roles, dates, sources) |

- Every fill is a single colour. No gradients.
- Green `#8FC1A0` and red `#E8968A` (on Ink) are only for showing a real change in a number, such as "+12.4%" or "−3".

## Type

| Role | Font | Weight | Notes |
|---|---|---|---|
| Captions | Hanken Grotesk | SemiBold 600 | The workhorse |
| Emphasis word in a caption | Newsreader | Italic 400 | At most one word per caption, only when spoken with emphasis |
| Titles, hooks, title cards | Newsreader | Regular 400 / Medium 500 | Sentence case, tight tracking (−1.5%) |
| Labels, roles, sources | DM Mono | Medium 500 | UPPERCASE, +8% tracking |

All three are free on Google Fonts. They must be installed on the Mac before Premiere can use them (see Known gaps).

## Captions

| | Vertical 1080×1920 | Horizontal 1920×1080 |
|---|---|---|
| Font size | 64 px | 52 px |
| Max per line | 24 characters | 42 characters |
| Max lines | 2 | 2 |
| Position | Centred, baseline at y = 1340 | Centred, baseline at y = 940 |
| Safe box | x 90–990, y 260–1500 | Inside 90% title safe |

- **Default (matched to reference 3):** Newsreader Regular at 54 px, sentence case, on one tight plate (16 px left and right padding, 10 px top and bottom, 3 px corners). The phrase is 3 to 5 words.
- **Karaoke:** words already spoken are cream `#F4F0EC`, and upcoming words in the same phrase are dim `#C2B5A6`. The phrase advances word by word as it's spoken.
- **Plate:** Umber `#5A504A`. It reads on both the pale backdrop and the black tee. The alternative "forest" palette from the reference uses `#183429`.
- **Position:** centred, plate top at y 1470 on tight vertical framing, below the shirt logo.
- Keep the speaker's words. Drop filler words and false starts. Never paraphrase.
- Break phrases at natural boundaries, never after "a", "the", "to" or "and".
- Captions change on the phrase, with no animation. No word-by-word bouncing, pop-in scaling or colour-cycling.

## Keyword titles and title stacks (from reference 3)

- **Keyword title:** one huge word in Newsreader Regular, uppercase or title case, Paper warm `#F4F0EC`, 220 to 320 px on vertical, centred in the upper half of the frame. Use it on a key beat (the hook, the offer, the payoff) for 0.8 to 1.5 s, at most once every 6 to 8 seconds. Cut in and cut out.
- **Title stack:** line 1 in Hanken Grotesk ExtraBold uppercase, 92 px, cream. Line 2 in Newsreader Italic, 96 px, in the accent colour `#E6D5BC`, ending with a full stop. For example "YOUR BUSINESS / is better." Each line sits on its own Umber plate, left-aligned at x = 90, in the top band.
- **Pill label:** a white rounded pill with Hanken SemiBold ink text and one ExtraBold span in Umber. For example "**1 day** of filming".
- **Note card:** a cream rounded card (28 px radius) with a DM Mono label, one Hanken line and a round Umber button with an up arrow. For example "VALE STUDIO / One full day, every four weeks."
- **Date and label line:** DM Mono uppercase, +20% tracking, separated by " · ", in Paper warm at 70% opacity. For example "16 · OCTOBER 2026 · SUNSHINE COAST". Put it above a keyword title or title stack.

## Split screen (from references 1 and 2)

- For screen recordings, B-roll of the work, or a stat: the graphic or B-roll fills the top half (1080×960), and the speaker reframed to the bottom half (1080×960, face in the upper third of that half).
- The seam is a hard edge with no border. Captions sit on the seam, centred.

## Lower thirds (name and role)

- Line 1: name in Newsreader Medium, 60 px vertical / 48 px horizontal, Paper.
- Line 2: role in DM Mono Medium uppercase, 24 px / 20 px, Paper warm at 80%.
- Use an Umber `#5A504A` plate at 100% (Ink on light footage), 2 px corner radius, 24 px side padding and 16 px top and bottom padding. A 4 px Stone rule sits on the plate's left edge, full height.
- Left-aligned at x = 90 (vertical) or x = 96 (horizontal), in the bottom graphics band (y 1470 on tight vertical framing). Hide captions while it is up.
- Show it once, the first time the person speaks, for 4 seconds.
- Motion: fade in with an 8 px rise over 200 ms, ease cubic-bezier(0.2, 0, 0, 1). Fade out over 120 ms, ease cubic-bezier(0.4, 0, 1, 1).

## Title and hook cards

- Use them only when the edit needs a chapter break or an opening hook that the footage doesn't carry.
- Ink `#141313` background with Paper warm `#F4F0EC` text in Newsreader Regular. Vertical: 88 px, max 3 lines, left-aligned at x = 90. Horizontal: 96 px, max 2 lines.
- One word may be set in italic. No other decoration.
- Optional small label above it in DM Mono uppercase, Stone light, for example "PART 2" or "THE COST".
- Hold for 1.5 to 2.5 seconds. Cut in and cut out, with no transition.

## Numbers and data on screen

- Big numeral in Newsreader (120 px vertical), label below in DM Mono uppercase.
- A change sits beside it in Hanken Grotesk SemiBold, green or red as above, signed (+12.4%, −3).
- A progress or comparison bar is a 6 px Stone bar on a `#2E2A28` track, drawn to scale.
- Always say what the number is and the period: "Organic sessions, September 2026".

## End card

- Ink background. "Vale Studio" in Newsreader Medium, Paper warm.
- One line of call to action in Hanken Grotesk, for example "Book a strategy call at valestudio.com.au".
- 3 seconds. No logo animation, no music sting.

## Edit feel

- **Cuts:** hard cuts. No whooshes, zoom transitions, glitches, spins or flashes.
- **Punch-ins:** a cut to 110–115% framing to mark a key line, no more than once every 20 seconds. Cut, don't animate the zoom.
- **Pace:** tight but human. Remove dead air and restarts, and keep natural pauses before an important line.
- **B-roll:** real footage of real work, people and places. No stock handshakes, no AI-generated people, no abstract motion backgrounds.

## Colour grade

There is no LUT yet. This is the direction:
- Natural and warm. White balance slightly warm of neutral. Skin tones true, never orange.
- Blacks lifted very slightly and pulled toward umber, never crushed blue-black. Highlights soft, never clipped.
- Greens and blues slightly desaturated so the warm neutrals lead.
- Never use teal-and-orange, heavy film grain, faded "vintage" looks or high-contrast "cinematic" crushes.

## Audio

- Dialogue: −14 LUFS integrated, −1 dBTP true peak for social. High-pass at 80 Hz, gentle de-ess, light compression.
- Music, if any, sits 20 to 24 LU under the voice and is warm and acoustic or minimal. No stock "corporate uplifting" tracks.
- No sound effects on text or cuts.

## On-screen writing

- Australian English (colour, organise, enquiry). Sentence case.
- No exclamation marks, no emoji, no hashtags burned into the video.
- Numerals for 10 and up. Write dates as "22 October 2026", and currency as "$4,800 + GST".
- Avoid: elevate, unlock, leverage, game-changer, seamless, synergy, "in today's fast-paced world".

## Known gaps

- **Text behind the speaker** (reference 3's "CLAUDE" and "HUGE") needs a subject matte. That isn't set up yet.

- **No logo supplied.** "Vale Studio" set in Newsreader Medium stands in. Replace it when a logo exists.
- **Fonts may not be installed.** Newsreader, Hanken Grotesk and DM Mono need to be installed on the Mac (free from Google Fonts) before Premiere can use them.
- **No LUT.** The grade is described in words only.
- **No reference images or videos.** Send examples of edits you like and the caption, lower-third and grade specs can be locked to them.
- **"Considered" was added as the third feel word** because the brief gave two. Change it if it is wrong.
- **Sizes are starting points.** Check them against the platform UI on a real upload once, then lock them here.
