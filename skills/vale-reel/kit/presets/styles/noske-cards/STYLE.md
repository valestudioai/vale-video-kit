# noske-cards (the main style to replicate)

Learned from Tom Noske (instagram.com/reel/Defg87-BF9r and instagram.com/reel/DeXygzfBUta). Rebuilt in Vale colours.

**Feel:** calm, confident and minimal. The words do the punching. Lots of space, one idea on screen at a time.

## Measured from his reels

| | Tom Noske | Vale version |
|---|---|---|
| Caption | Bold lowercase sans, 1 to 2 words, about 95–100 px, centred at 58–64% height. Warm peach `#E0C0AC` on one reel, warm white on the other | Hanken Grotesk 700, lowercase, 96 px, cream `#F1E4D6`, soft Ink shadow, 1 to 2 words |
| Dark word card | Full-screen `#141B1E` with bold white word | Ink `#141313` with cream `#F4F0EC` word |
| Light word card | Full-screen `#F5F7FD` with deep teal `#1C3838` word | Paper warm `#F4F0EC` with Umber `#5A504A` word |
| Kinetic card | Earlier words small and faded above the bold current word | Same: the ghost line at about 48% size and 60% opacity |
| Quote card | Light card, big pale grey quote marks | Same, quote marks in `#C9BFB5` |
| Cameras | Two angles, cut on each sentence | One camera, so alternating framing (100% / 118%, biased to the face) on every sentence-sized phrase |
| Grade | Dark, moody, warm practicals | Vale Warm Natural |
| Extras | Screen recordings and image grids, a speaker picture-in-picture on a light card | Not built yet (see Gaps) |

## Rules

- **Card rhythm:** a card on a key word about every 4 to 6 s. Hold it at least 12 frames (0.5 s). The audio keeps running underneath, and captions hide while a card is up.
- **Card choice:** light cards for the positive or the subject ("better", "quality"), dark cards for weight and endings ("queensland", "the rest."). Use a kinetic card when the lead-in words matter ("does not reflect the" → "quality"). Use a quote card for a phrase the viewer should remember.
- **Captions:** lowercase, no full stops except on cards, and no plate. On BETTER's tight framing they sit at y 1035, between the chin and the shirt logo. Over B-roll they sit at y 1170.
- **Framing:** alternate 100% and 118% on each new sentence. Never animate the zoom.
- **No transitions.** Every change is a hard cut.

## Gaps

- **Picture-in-picture hook** (a speaker clip in a rounded rectangle on a light card, with a peach line above): needs a masked overlay. It can be done in the preview renderer, but not yet in Premiere.
- **Screen-recording inserts** need recordings from you.
