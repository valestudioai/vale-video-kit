# Vale Studio video kit

A Claude Code plugin with Vale Studio's short-form video style and the editing pipeline behind it.

It has two skills:

- **vale-style**: the locked look. Colour schemes, type, captions, card motion, split screens, UI cards, sound, and what's been rejected.
- **vale-reel**: the pipeline. It transcribes with WhisperX, builds a tight cut, storyboards every beat for approval, renders graphics, captions and sound in the Vale style, then assembles the edit in Adobe Premiere Pro over MCP.

The kit also includes the brand files and fonts, the LUT, the audio and export presets, the graphics generator, the render scripts and a worked example storyboard.

## Install

In Claude Code:

```
/plugin marketplace add valestudioai/vale-video-kit
/plugin install vale-video@vale-studio
```

Then open an empty project folder in Claude Code and paste in [SETUP-PROMPT.md](SETUP-PROMPT.md). Claude sets up the kit, checks your tools, builds your own house style from your references into `STYLE.md` over a few Style Lab rounds, and then edits your first video.

## Requirements

- macOS (built and tested on Apple Silicon).
- ffmpeg and ffprobe.
- Python 3.11 with a WhisperX venv, for transcription.
- Node 22+ and Google Chrome, for animation renders.
- Adobe Premiere Pro 2025 or 2026, for the Premiere step (optional).

See `skills/vale-reel/SKILL.md` and `skills/vale-reel/PREMIERE.md` for details.

## Licences

- Fonts in `skills/vale-reel/kit/brand/fonts/` (Newsreader, Hanken Grotesk, DM Mono, Caveat) are licensed under the SIL Open Font License 1.1.
- The Premiere connector isn't bundled. It's [hetpatel-11/Adobe_Premiere_Pro_MCP](https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP) (MIT).
- The reference reels listed in `references/NOTES.md` belong to their creators. The kit only describes them and includes none of their footage or assets.
