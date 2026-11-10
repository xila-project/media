# ElevenLabs audio workflow

ElevenLabs supplies optional source assets. It is never called by local builds, tests or CI. Keep original downloads, prompts, model settings, generation identifiers, costs and transformations so an accepted sound can be reused without generating it again.

## Connect securely

Use the [official hosted MCP server](https://elevenlabs.io/docs/eleven-api/resources/mcp-server), which authenticates through OAuth. The older local `elevenlabs-mcp` package is archived; do not install it for a new connection.

```sh
# Codex
codex mcp add elevenlabs --url https://api.elevenlabs.io/v1/mcp
codex mcp login elevenlabs

# Claude Code
claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp
# Then use /mcp in Claude Code to authenticate.
```

Sign in, select the intended workspace and approve access in the provider's browser flow. No API keys belong in this repository. If a newly configured server is not visible in an already-running client, reconnect or reload its MCP tools after login.

## Generate a review candidate

Read the workspace's available node types and the selected model's schema and prompting guide. Create a node without running it, with the exact duration and instrumental settings. Estimate its cost with `creative_run_flow_nodes`, `estimate_only: true`, and an explicit `generations_count: 1`.

Only run after the maintainer approves a concrete candidate and a credit cap. Keep the same flow and node, turn off `estimate_only`, and run once. Costs scale with variation count; leaving the count unspecified can generate several variations. A pending request is not a reason to run it again: use `creative_get_flow_run_status` at the returned polling interval. Preserve completed downloads immediately because media links expire. Do not commit signed download URLs, workspace-switch codes or credentials.

The maintainer approved one initial startup candidate with a 5,000-credit cap. Candidate 001 uses Music v2.5 for a three-second instrumental sonic signature; the quote was 82.5 credits and the completed generation reported 44.99 credits. This approval does not authorize another take. Prompt, parameters, provenance and the stable flow link are in `productions/startup/candidates/001/`.

## Master and reuse offline

```sh
python3 scripts/audio.py process assets/audio/startup/candidate-001-source.mp3 --output output/startup/candidate-001 --rate 22050
python3 scripts/video.py soundtrack output/cinematic-opening/opening-bootsplash.mp4 output/startup/candidate-001/master.wav output/cinematic-opening/opening-startup-001.mp4 --offset 5
python3 scripts/video.py validate output/cinematic-opening/opening-startup-001.mp4 --width 960 --height 540 --fps 30 --duration 8
```

The shared soundtrack command places the cue at the requested time, pads silence and preserves video duration. It copies the H.264 stream and encodes the soundtrack to AAC; no animation frames need to be rendered again. The review places the same three-second signature at five seconds, as the cinematic camera settles and the bootsplash ripple starts.

The source for this first candidate is a 48 kHz stereo MP3 from ElevenLabs. The processing master is a 48 kHz PCM24 mono WAV derived from it; converting to WAV does not restore the fidelity of a lossless original. The embedded export is dithered PCM16 mono at 22,050 Hz. Preserve the original provider file and its hash.

## Human review and publication

Listen to the standalone signature before judging the trailer mix. Inspect level, attack, tail, small-speaker audibility and mono compatibility. The offline validator measures loudness and peaks; artistic acceptance requires listening review.

Candidate 001 is generated preview material, not approved Xila sonic branding. It remains available in the authorized ElevenLabs flow and locally under `assets/audio/startup/`; the source and output media are ignored by Git. Builds continue to use the free synthetic fixture until an accepted, licensed source is explicitly integrated. Before publication, confirm the originating workspace's rights, retain the applicable terms and determine how the accepted source will be distributed. Do not infer a commercial license merely because a file was generated.

## Embedded constraints

Generate the startup signature for limited playback hardware from the beginning: keep its essential pitches and harmonic motion audible in mono and the midrange, rather than depending on deep bass or phase-based stereo effects. Keep the normal PCM16 export, and additionally run `scripts/audio.py audition` for an 8-bit, 22050 Hz bandwidth-constrained listening check. This is a stress test; it does not replace listening on the intended DAC and speaker.

Candidate 002 was separately approved as one four-second take, capped at 125 credits. Its quote was 110 credits; completion reported approximately 59.99 credits. The richer harmonic draft includes mono and limited-bandwidth constraints, and both the normal master and constrained PCM8 listening file are ready for human review. The source, pipeline commands and exact reported cost are documented with that candidate.
