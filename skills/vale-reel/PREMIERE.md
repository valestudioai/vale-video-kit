# Premiere Pro over MCP

Uses the open-source Premiere MCP connector by hetpatel-11 (MIT): https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP. Tested at v1.2.3 (commit 12684e3) with Premiere 25.6 and 26.5.

## Setup (run on the Mac, not in a VM)

1. `git clone https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP vendor/premiere-mcp` inside the project, then follow its README to build and run its `setup:mac` script (installs the CEP panel).
2. Add it to the project's `.mcp.json`, with the absolute path to your clone:

   ```json
   {
     "mcpServers": {
       "premiere-pro": {
         "command": "node",
         "args": ["<absolute path>/vendor/premiere-mcp/dist/index.js"],
         "env": { "PREMIERE_TEMP_DIR": "/tmp/premiere-mcp-bridge", "PREMIERE_MCP_TELEMETRY": "0" },
         "timeout": 600000
       }
     }
   }
   ```
3. Open Premiere, open the MCP panel (Window > Extensions), restart Claude Code, and check with `verify_premiere_connection`.

## Quirks and workarounds

- Tools whose schema shows no properties (e.g. `create_sequence_from_clips`, `execute_extendscript`, `set_sequence_frame_rate`) get their arguments stripped and fail. Instead: `create_sequence` with the "Social Media Portrait 9x16 30 fps" preset, then `set_sequence_settings` (frameRate 23.976 if needed).
- `import_folder` fails. Use `import_media` per file.
- `add_adjustment_layer` only makes a transparent PNG. Apply the LUT per clip with `apply_lut` (fine in parallel).
- `export_frame` ignores its time and exports the playhead frame. Verify with `list_sequence_tracks` and `get_clip_properties`.
- `add_to_timeline_batch` sets source in/out with `setInPoint(seconds)`, which rounds down: pass mid-frame times `(frame + 0.5) / fps`. Timeline positions at exact frame boundaries are fine.
- Stills placed with `add_to_timeline_batch` can come in one frame short. Fix with `trim_clip` duration = exact frames / fps.
- For ~150 captions, render one transparent QuickTime Animation layer (`scripts/render_caption_layer.py`) instead of importing stills.
- Full-screen cards: ProRes 422 HQ (QuickTime Animation bloats with grain). Alpha layers: QuickTime Animation.

## Presets

- Export: `presets/export/Vale - Social H.264 16 Mbps.epr` → copy to `~/Documents/Adobe/Adobe Media Encoder/<version>/Presets/` or import from Export > Preset > Import Preset.
- Look: `presets/look/Vale_Warm_Natural.cube` → copy to `~/Library/Application Support/Adobe/Common/LUTs/Creative/` so it shows in Lumetri > Creative > Look.
