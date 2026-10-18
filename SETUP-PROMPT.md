Set up my AI video editor in this folder using the vale-video plugin I just installed. You are my editor: I film raw talking-head footage, and you cut it, style it and put it in front of me in the app I finish in. Before we edit anything, we build MY house style together from my references and lock it into STYLE.md. The Vale Studio style that ships with the plugin is only an example of how detailed STYLE.md should be. Never use it as my style.

Keep everything in this folder:
- raw/: my clips
- references/: reference reels and screenshots
- transcript/: transcripts and cut lists
- storyboard/: storyboards
- renders/: renders
- style-lab/: style tests
- scripts/: scripts
- vendor/: cloned connectors

## 1. Set up the kit
Load the vale-reel skill and follow its step 0. Copy its kit/ folder into this folder, without overwriting anything I already have, and make the folders above. Then:
- Rename CLAUDE.template.md to CLAUDE.md.
- Rename the kit's STYLE.md to references/EXAMPLE-STYLE-vale.md, and do the same with brand/BRAND.md (to references/EXAMPLE-BRAND-vale.md) and brand/tokens.json (to references/EXAMPLE-tokens-vale.json). My own versions get written later.

## 2. Check my machine
This kit is built for macOS. Check for:
- ffmpeg and ffprobe
- git
- uv, and Python 3.11 as uv sees it (`uv python find 3.11`)
- Node 22 or newer
- Google Chrome in /Applications

Tell me what's missing and the command to install it. Don't install anything without asking me first.

## 3. Ask where I finish
Ask whether I use Adobe Premiere Pro, or want a finished MP4 instead.

For Premiere:
- Follow the vale-reel skill's PREMIERE.md to clone, build and register the connector.
- Tell me to create a NEW, empty project, save it under a real name, keep it open, and start the MCP Bridge panel. Then tell me to restart Claude Code.
- Prove the connection inside that project: add a marker called "Claude was here", read it back, then remove it.
- Never write into a project that holds other work.

## 4. Write my brief
Ask me these questions in one message. Short answers are fine, and anything I skip goes under Open questions.
1. What are the videos for?
2. Which platforms, and what shape? (Default: vertical 9:16, designed to the tightest safe zone across Reels, TikTok and Shorts.)
3. Who's watching? What should they feel in the first second?
4. References: 2 to 5 creators or reels I love. For each one, what exactly do I like (captions, cards, cuts, grade, pacing, animations, sound) and what don't I want from it?
5. Never: things my videos must never do or look like.
6. Always: small details that should run through everything.
7. What I already have: name, logo file, fonts, colours.
8. Motion: calm and educational, snappy, filmic, playful? Where should the accents go?
9. Sound: subtle clicks and whooshes, punchier hits, music, or none?
10. A test clip of me talking, put in raw/, that we can design on.

## 5. Study my references
Ask me to drop the reels (downloaded videos or screen recordings) and any screenshots or mood boards into references/. Don't download anything from social platforms yourself.

For each reel:
- Extract frames with ffmpeg: one every 0.5 s, plus every scene change.
- Study the captions (font, size, case, words per line, position, plate or shadow), the cards and titles, the transitions and motion timing, the grade, the layout and safe zones, and the sound.

Write references/NOTES.md with a table: link, creator, what to take, what not to take. Describe the references, never copy their assets, music or exact layouts. Show me the notes and check you've read my taste right.

## 6. Write STYLE.md
Write STYLE.md in this folder. Use the same structure as references/EXAMPLE-STYLE-vale.md:
- **The brief:** my answers from step 4.
- **Working method:** storyboard first, render only after I approve.
- **Locked:** empty for now.
- **Rejected:** empty for now.
- **Open questions:** everything still undecided.

This file is the source of truth for every video from now on. It overrides the vale-style skill.

## 7. Style Lab: lock the look in rounds
Each round, make 15 to 25 short test renders (2 to 4 s each) in style-lab/round<N>/. Build them as HTML/CSS animations and capture them with style-lab/render/render.mjs, using the round scripts in style-lab/ as a starting point.
- **Round 1:** colour pairings, big-statement type, card motion (try a hard cut, a smooth rise, a snappy mask and a filmic focus), premium details, 3 to 4 caption styles, and 3 to 5 synthesised sounds.
- **Round 2:** on my test clip. Captions over my footage, split screens, animations on a plain background, and UI or graphic cards. Use only what survived round 1.
- **Round 3 and on:** fix the ideas I liked whose execution I didn't, and try the leftover open questions.

Show each round in a page where I can mark every test keep, maybe or drop, and add a note:
- If you can publish Claude artifacts, publish style-lab.html as my Style Lab page and reuse it every round.
- Otherwise, make a local HTML contact sheet I open in the browser, and I'll reply in chat.

After each round:
- Write keeps into Locked with exact values: hex codes, font, weight, size, tracking, easing curves, durations, positions, and sound length and frequency peak.
- Write drops into Rejected with the reason. Quote me where I gave one, and say "inferred" where I didn't.
- Update Open questions.

Keep going until I say the style is locked. Then write brand/BRAND.md and brand/tokens.json to match it, and check every font is installed.

## 8. Make my first video
Run the vale-reel pipeline on a real clip, with all looks taken from my STYLE.md:
1. Transcribe.
2. Cut. Show me the kept text and stop until I approve it.
3. Storyboard every beat. Stop until I approve it.
4. Render.
5. Build it in Premiere (or deliver the MP4).

Adapt the kit's scripts (scripts/storyboard.py, presets/graphics/vale_graphics.py, the render and premiere example scripts in storyboard/) to my style instead of Vale's colours and fonts. Every cut must be a real edit point I can trim. Check what landed against the cut list, frame for frame.

When the video is done, tell me plainly what still needs a human: cut points that clip a word, captions that collide with my face, anything you couldn't verify.

## How to work
- Just do it. Don't ask permission to create folders, write scripts or run commands. Execute, then report.
- Be concise.
- You need me for:
  - my brief answers
  - my reference files
  - rating each Style Lab round
  - approving the cut and the storyboard
  - any click in Premiere
- If something fails twice, stop and tell me.
- When you learn something non-obvious about my footage, setup or taste, write it in this folder's CLAUDE.md. Style decisions go in STYLE.md.

Start with step 1.
