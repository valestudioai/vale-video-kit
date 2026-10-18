# Vale Studio video style

Built round by round in Style Lab (`style-lab.html`, published as your own Claude artifact).
This file is the source of truth. The older style experiments in `presets/styles/` are reference only.

## The brief

Agreed 2026-10-17.

1. **What it's for:** Instagram Reels for Vale Studio's own account.
2. **Where and what shape:** vertical 9:16 on every short-form platform (Reels, TikTok, YouTube Shorts, LinkedIn). Designed to the tightest safe zone across those apps.
3. **Who's watching and what they feel:** business owners. The videos feel premium but down to earth, and educational. In the first second the viewer should think "this is for me, and these people clearly know what they're doing" (suggested by Claude; confirm or change).
4. **References** (details in `references/NOTES.md`):
   - **Tom Noske** (reel DeSo34eBhvZ): the cut scenes, a plain background with text over the top; his caption style; the Helvetica look.
   - **Gannon Meyer** (reel DeK5cgNskkb): the animation style on a plain background (charts drawing on, floating avatars, stat cards); the 50/50 split with animation; his captions.
   - **Jason Cooperson** (reel DdovWa7D35X): the split-screen elements and the animations. Not his dark grid backgrounds, and not his captions.
   - **RPN** (reel DecWaVFJC4v): the split-screen elements and the animations.
   - **justyn.ai** (reel DeUUFJQu8cw), added after round 1 as an "elite reference". Seen in it:
     - serif captions on a deep green plate with the spoken word lit
     - huge serif keyword titles
     - "BOLD CAPS / italic serif." title stacks
     - a spaced mono date line, UI cards, and a warm natural grade

     What the user loves about it:
     - **The UI cards and prompt-bar graphics.**
     - **The overall polish, warmth and pacing.**

     Not its serif type or the karaoke caption plate (Helvetica was kept and karaoke dropped in round 1).
   - **Pinterest** (valeharrison01; VALE, BRAND and Creative boards): black-and-white cinematic photography, handwritten notes, tall condensed type, 90s analog film, retro print on cream and kraft, and sun motifs.
5. **Never:** dark grid backgrounds, emoji, stock footage, bouncy pop-ups, or anything that feels cheap.
6. **Always:** small premium design details, used sparingly: fine hairline rules and thin borders, small corner labels ("VALE STUDIO · 01", dates), the sun mark from the logo as a tiny accent, subtle film grain on plain backgrounds, soft shadows on rounded cards, numbered sections or progress markers.
7. **What we have:**
   - **Name:** Vale Studio.
   - **Logo:** the cream "VALE ☀ STUDIO" mark on black. Using the profile picture until there's a logo file.
   - **Font:** Helvetica Neue (on this Mac) for text and captions. Also testing a tall condensed face for big statements and a handwritten note style.
   - **Colours:** undecided. Testing three pairings from the Pinterest boards:
     - Monochrome: off-black, warm white and the logo cream, with grain.
     - Analog paper: cream or kraft with off-black and one ochre or brick-red accent.
     - Dusty blue on pale grey-white.
   - The earlier brand colours (#5A504A, #9C8979, #FFFFFF, #141313) are available but not required.
8. **Motion:** educational first. The base is clear and smooth so the teaching is easy to follow. Snappy, filmic, physical or glitchy accents go on key moments, so the graphics feel cool. Never bouncy.
9. **Sound:** subtle clicks and soft whooshes under animations, and punchier hits on big moments. There's no sound library, so sounds are made with AI (the Higgsfield audio generator, unless told otherwise), trimmed, faded and kept under -1 dB peak.
10. **Build order:**
    - Round 1: text cards and colour, captions, sounds.
    - Round 2: split screens and animations, once the look is set.

## Working method: storyboard first

Every new video gets a storyboard before anything renders, following justyn.ai (reel DeUUFJQu8cw): "before rendering, it gives me a complete storyboard so I can see what Claude is thinking", and changes come back as one sentence ("tighter cut, bigger captions").
- **Where:** the Storyboard page, `storyboard/storyboard.html`, published as your own Claude artifact.
- **Each beat shows:** its edit timecode and length, the shot type, the spoken line, what happens, labelled rows (card, sound, captions, UI), and a graded raw frame next to mock frames in the locked style.
- **Changes:** one sentence on the page, plus notes on single beats. Each round of changes becomes a new version.
- **Rendering:** happens only after Approve.

## Locked

### Round 1 keeps (2026-10-17)

- **Colour:**
  - Monochrome: warm off-black `#151413`, warm white `#F2EEE8`, logo cream `#E6D8BC` on the key word, film grain. "I like this."
  - Dusty blue: `#3C5182` on pale grey-white `#E4E4DF`.
- **Card motion (all four kept; the default is still to be picked):**
  - Hard cut: one frame, Tom's cut scene.
  - Smooth rise: 28px, 90 ms stagger, 520 ms, cubic-bezier(.2,.8,.2,1).
  - Snappy mask: per word, 60 ms stagger, 240 ms, cubic-bezier(.7,0,.2,1).
  - Filmic focus: 24px blur to 0, 104% to 100%, 800 ms, plus a slow drift.
- **Big-statement type:**
  - Helvetica Neue Bold, lowercase, 150px, tracking -0.035em.
  - Helvetica Bold plus a handwritten aside (Caveat 74px, logo cream, rotated -6°) and a hand-drawn underline. "I like this."
- **Captions:**
  - Tom: Helvetica Neue Bold 96px, lowercase, white, 2 words at a time, soft shadow.
  - Tom plus one key word in logo cream.
  - Sentence case: Helvetica Neue Medium 72px, 3 to 4 words.
- **Premium details on cards:** a "VALE STUDIO" corner label, a "01 / 04" index, a hairline rule that draws on, the sun mark, and film grain (all present in every kept card).
- **Sounds (synthesised):** soft click (card cuts, UI), paper slide (cards landing), film click (filmic reveals).

### Round 2 keeps (2026-10-17, shot on the IMG_9225 walk-and-talk)

- **Split screens (all three kept):**
  - Hard split at 940px, warm off-black panel, a line chart that draws on (stroke-dash, 1.3 s) while the number counts to 30.
  - The same split on a pale grey-white panel `#E4E4DF` with a dusty blue `#3C5182` line.
  - Floating card: rounded 30px card with a deep shadow over a blurred, dimmed copy of the shot (Gannon).
- **Animations on a plain background (all four kept):**
  - Chart draws on, with a soft click as the end dot lands.
  - Stat cards stack in (1 / 30 / 0), each landing with a paper slide.
  - Handwritten note and arrow draw on after a hard-cut statement, with a film click. Note: "Arrow is going over safe zone".
  - Numbered list (plan, film, edit, post) with hairlines; each step lights up with a soft click.
- **UI cards over footage (from justyn.ai):** prompt bar light (cream bar, dark send button), prompt bar dark (cream send button), notification card ("New enquiry"). All land in the top band at 0.8 s with the soft click.
- **Sounds:** the whoosh is back in two forms. Short and soft: 320 ms with a 1.4 kHz peak, on the snappy mask. A breath of air: 700 ms with a 900 Hz peak, on the smooth rise.
- **Ideas kept, execution not:**
  - Repeated stack: "I like the idea but don't like the effect" (rows hard-cutting in, growing).
  - Handwritten card (blue ink on paper, no footage): "Don't like animation but idea is great" (left-to-right wipe).

### Round 3 keeps (2026-10-17). "I am happy so far."

- **Handwritten card** (blue ink `#2B3E6E`, Caveat 128px on paper `#F3F1EC`, "— vale studio" sign-off): all four motions kept (hard cut, line by line, pulls into focus, word by word). The wipe is gone.
- **Light scheme:** pale grey-white `#E4E4DF` (not warm paper), off-black type, with the dusty blue key word in one of two forms. Either handwritten in Caveat blue, or Helvetica blue with a hand-drawn blue underline that draws on.
- **Repeated stack:** kept in dusty blue on pale grey, with rows rising in (smooth rise, 90 ms apart) and the breath of air.
- **Big moments:** short whoosh into the cut, breath of air into the cut, and film click on the cut were all kept. A big moment is a hard cut to a card with one of these, never a low hit.
- **Split screens:** number with a progress line, bar chart growing, prompt bar typing inside the panel, and the floating card in the light scheme (dusty blue line).
- **Animations:** handwritten note with the arrow inside the safe zone, before and after (4 vs 30), a month calendar filling in, and weekly reach bars.
- **UI cards:** the prompt bar that turns into its answer, a cursor clicking send, and the "This week" schedule card ticking off.

## Rejected

Round 1. No reasons were given, so these are inferred from the pattern of keeps and drops.

- **Glitch accent** (RGB split): too loud and cheap for Vale.
- **Helvetica Medium for big statements:** too quiet at that size. It's fine as a caption.
- **Condensed uppercase poster type:** too shouty.
- **Captions with spoken words lit (karaoke):** dropped.
- **Punchy hit** (50 Hz thump with shake): too heavy.
- **Not rated, so treated as not wanted for now:** Analog cream, Kraft and brick, tiny Gannon captions.

Round 2. Reasons are inferred unless quoted.

- **Dusty blue mixed into monochrome:** blue key word on black, blue-black ground and blue details on black were all dropped. Keep the two schemes separate; don't mix them.
- **Softer big moment** (70 Hz thud plus paper tap): dropped like the punchy hit. Low thuds aren't Vale.
- **Pinterest analog treatments:** the B&W cinematic look with timecode, the printed photo border and the retro sticker were all dropped. The Pinterest boards set the mood, not literal effects. What survives from them is the handwriting and dusty blue.
- **Not rated:** the pill label UI card. Treated as not wanted for now.

Round 3.

- **Warm paper ground for the light scheme:** dropped. The light scheme stays pale grey-white; paper is only for the handwritten card.
- **Whole stack pulling into focus** (filmic, monochrome): dropped.

## Open questions

- Is the first-second feeling right?
- Is there a logo file (SVG or PNG)?
- **Colour:** settled in round 2 as two separate schemes: Monochrome (dark) and Dusty blue (light), never mixed. Settled in round 3: off-black body with a blue key word, handwritten or underlined.
- **Big moments:** both low hits (punchy, then softer) were dropped, but the whooshes were kept. Is a big moment marked by a whoosh into a hard cut, by silence, or by no sound at all? (Round 3 tests these.)
- **Captions:** three styles kept (Tom, Tom plus cream word, sentence case). Which is the default?
- Which motion feel is the default, and which are accents (rounds 1 and 2)?
- **Sound source:** Higgsfield's audio tool only makes speech (it declines sound effects), so round 1's sounds were synthesised from scratch in code (`style-lab/round1/gen_sounds.py`). Connect an AI SFX generator such as ElevenLabs to replace them, or keep the synthesised ones if they work.
- **Round 2 wasn't submitted.** It was read from the per-card notes (24 of 25 rated).
- **Round 3 Maybes:**
  - The repeated stack in dark monochrome ("Still doesn't fit", on both the rise and the mask versions). It only works in dusty blue so far.
  - Silence as a big moment.
  - Stat cards inside the split panel.
  - The notification stack.
- **Captions on a white tee:** white captions vanish on it. The storyboard test puts them at y 1060 with a deep shadow. Is the cream key word still readable there?
