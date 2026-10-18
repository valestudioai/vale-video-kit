# Finishing in other apps

The render step always produces the same layers, whichever app you finish in:
- **Cut pieces:** the kept pieces of the raw clip, as frame-snapped in/out points from `transcript/<clip>/frames.json`.
- **Graphics:** one clip per card or animation, with alpha.
- **Captions:** one timeline-length transparent layer.
- **Sound effects:** `sfx.wav`.
- **Grade:** `presets/look/Vale_Warm_Natural.cube` (or your own LUT).
- **Finished MP4:** the composited `<clip>_v<N>.mp4`.

Only the last step changes per app. Premiere is in `PREMIERE.md`.

| App | Method | Status |
|---|---|---|
| Premiere Pro | Live, over the Premiere MCP connector | Tested |
| DaVinci Resolve Studio 21.1+ | Live, over Resolve's built-in AI connector | **Untested** |
| DaVinci Resolve (free) | Layered handoff | **Untested** |
| Final Cut Pro | FCPXML that opens as a new library | **Untested** |
| CapCut | Layered handoff | **Untested** |
| No app | Finished MP4 | Tested |

For untested routes, tell the user this is the first run through, check every result against `frames.json`, and write anything you learn into the project's CLAUDE.md.

## Alpha layers for other apps

- Encode graphics and captions as **ProRes 4444 with alpha**: `-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -alpha_bits 16`. Resolve, Final Cut and recent CapCut desktop builds all read it.
- QuickTime Animation also carries alpha, but it bloats badly with film grain.
- Full-screen cards with no transparency can go to ProRes 422 HQ.

## DaVinci Resolve Studio 21.1+ (live, untested)

### Connect
1. In Resolve, open File > Setup AI Assistants and let it register its built-in connector for Claude Code. Nothing to install.
2. Restart Claude Code with Resolve and a NEW, empty, saved project open.
3. Never write into a project that holds other work. Saving an "Untitled Project" hangs on Resolve's name dialog.
4. The connector runs Python against Resolve's scripting API through `run_script`. Look up calls with its API reference tools.
5. Its sandbox can't read files, so compute frame lists outside Resolve and paste them into the script as literals (or use `run_script_unsafe`).
6. Prove the connection: add a marker "Claude was here" on a test timeline, read it back, and delete the test timeline.

### Build the timeline
1. **Frame rate:** set the project's `timelineFrameRate` to the timeline rate before importing (30 for variable-frame-rate phone clips, otherwise the footage's own rate). A script can't set the playback frame rate, so ask the user to set Playback frame rate in Project Settings to the same number.
2. **Import:** bring the master and every layer file into the media pool. Read each clip's FPS back from Resolve and do all frame math at that rate.
3. **Create the timeline:** `CreateEmptyTimeline("<clip> v<N>")`, then add tracks with `timeline.AddTrack("video")` and `timeline.AddTrack("audio")` until V3 and A2 exist.
4. **Lay V1:** use ONE `AppendToTimeline` call with a list of clip infos (`mediaPoolItem`, `startFrame`, `endFrame`, end exclusive) and no `recordFrame`, so the pieces land back to back. Don't use `CreateTimelineFromClips`: when every piece comes from one file, it silently lays only the first.
5. **Lay the layers:** append graphics (V2), captions (V3) and sound effects (A2) with clip infos that set `trackIndex`, `mediaType` (1 video, 2 audio) and `recordFrame`.
6. **Apply the LUT:** copy the .cube into Resolve's LUT folder (`/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/` on macOS) and refresh LUTs. Then call `SetLUT(1, <path>)` on every V1 item.
7. **Split screens:** set `Pan`/`ZoomY`/`Tilt` with `SetProperty` on the V1 items that need the speaker shifted.
8. **Check and save:** read the timeline back and compare clip count, each clip's length and the total against `frames.json`, frame for frame. Then save through the Project Manager.

## DaVinci Resolve free (layered handoff, untested)

Blackmagic's connector is Studio-only, and 21.1 removed scripting from the free version, so build the [Layered handoff](#layered-handoff) below. Free Resolve can also import the Final Cut FCPXML (File > Import > Timeline), which gives trimmable cuts. Offer it as an extra, also untested.

## Final Cut Pro (FCPXML, untested)

### Version and validation
1. Write the newest FCPXML version this Final Cut ships a DTD for: `Contents/Frameworks/Interchange.framework/Versions/A/Resources/FCPXMLv1_*.dtd` inside the app.
2. Copy the DTD to a path with no spaces, and validate with `xmllint --dtdvalid`.

### Structure
- **Resources:**
  - one `format` matching the timeline (1080x1920, frameDuration such as `1001/30000s` or `100/3000s`)
  - one `asset` for the master
  - one `asset` per graphics clip, the captions layer and sfx.wav
- **Library tree:** `library > event > project > sequence > spine`.
- **Spine:** one `asset-clip` per kept piece, each with `offset`, `start` and `duration`. Keep the dialogue on the video clip, never as a separate audio element.
- **Graphics and captions:** connected clips inside the spine clip they sit over, with `lane="1"` (graphics) and `lane="2"` (captions), positioned by `offset` in the parent's time.
- **Sound effects:** a connected clip with `lane="-1"`.

### Times and timecode
- Times are rational fractions on the frame grid, such as `1001/30000s`, never long decimals.
- If the footage has embedded timecode, the asset starts at that timecode and every `start` counts from it. A clip written from 0s on timecoded media is silently dropped.

### Grade and import
- **LUT:** Final Cut can't apply a .cube through FCPXML reliably. Tell the user to add Custom LUT (Effects > Color) to one clip, pick the .cube, then copy and paste attributes to the rest. Alternatively, bake the LUT into a graded master before writing the XML (ffmpeg `lut3d`, ProRes 422 HQ). Ask which they prefer.
- **Import options:** add an `import-options` block with library location set to a new .fcpbundle in the project folder, copy assets 0 and suppress warnings 1, so Final Cut creates a fresh library.
- **Open it:** double-click the file, or use File > Import > XML.

## Layered handoff (CapCut, Resolve free; untested)

### What to write
Write `deliver/<clip>_v<N>/` with:
- `00_final.mp4`: the finished composite, ready to post.
- `01_cut_graded.mov`: the cut with the LUT baked in, no graphics (H.264 high bitrate, or ProRes 422 HQ).
- `02_graphics.mov`: every card and animation on one timeline-length ProRes 4444 alpha layer.
- `03_captions.mov`: the captions on a timeline-length ProRes 4444 alpha layer.
- `04_sfx.wav`.
- `HOW-TO-STACK.md`: new project at the same frame size and rate, then each file dropped at 0:00 in this order (cut at the bottom, then graphics, then captions, then the sfx track). Include the frame rate and duration so they can check nothing drifted.

### Check and caveats
- All four layers must be exactly the same length. Check every file with ffprobe.
- In CapCut, alpha playback depends on the build. If the graphics show a black background, the user should report it, and you fall back to delivering `00_final.mp4` plus the graded cut.
- The handoff cut is one continuous clip, not separate trimmable edits. Say so.
