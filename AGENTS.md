# Working in Xila Media

## Collaboration and delivery

- Work in small, reviewable stages. The maintainer requests a rendered review at each creative stage before expanding the edit.
- Implement directly; do not introduce a separate planning or permission phase for work already authorized.
- Commit working increments regularly and push them to `origin/main`. Do not leave completed work only on a feature branch or open a pull request unless requested. Never force-push or overwrite another contributor's work.
- State what actually passed and what remains unverified. The repository is still being bootstrapped; do not describe incomplete CI or documentation as finished.

## Brand and creative direction

- `xila-project/brand` is the single source of truth. Resolve the immutable commit and hashes in `assets/brand/lock.json` with `python3 scripts/brand.py`.
- Do not edit the ignored upstream cache or copy path coordinates into animation code. Use the exact official SVGs, Montserrat and the upstream legal notices.
- Preserve the five-part monogram, original curves, proportions and gaps. Provide at least one quarter of the symbol width as clear space in settled compositions. Use the correct black or white variant for its background.
- The trailer direction is monumental, minimal, authoritative and restrained. Use deliberate camera motion, controlled monochrome lighting and progressive reveals. Avoid slide-like sequences, decorative effects, fake interfaces and unsupported product or hardware claims.
- The reviewed cinematic material treatment permits shallow perpendicular extrusion of the official curves; it does not replace the flat identity master. Do not bevel, redraw or rotate the mark itself.
- Keep the connection to the existing Core bootsplash. Its pinned timeline is shared by Motion Canvas and the Blender keyframe generator; do not maintain another timing model.

## Architecture and commands

- Use Motion Canvas and TypeScript for 2D scenes and typography, Blender `bpy` for optional 3D work, and the shared FFmpeg scripts for assembly and audio processing.
- Keep production settings and brand/reference pins in `productions/*/production.json`. Put reusable components in `motion-canvas/components` and reusable scene scripts in `blender/scripts`.
- Use the exact versions in `mise.toml` and `package-lock.json`. Blender must remain optional for purely 2D work. Python scripts currently need only the standard library.
- Preview with `mise run preview`. Render the bootsplash with `mise run render:logo`; render the opening with `mise run render:cinematic-opening` and the current kinetic passage with `mise run render:architecture-reveal`.
- `productions/cinematic-opening/README.md` records the current visual review and reference-access limitations. The earlier trailer is a pipeline proof of concept, not the completed cinematic launch film.
- Prefer existing helpers and focused functions. Add dependencies only for a demonstrated need; do not introduce Docker or duplicate FFmpeg commands.

## Verification

- Run `npm test`, `npm run typecheck`, `npm run lint` and `python3 scripts/validate.py` for relevant code changes. Use `npm run format:check` when checking formatting; fix failures rather than claiming the aggregate check passed.
- Exercise real FFmpeg output for media-processing changes. Verify duration, dimensions, frame rate, codec and decoding with `scripts/video.py validate`.
- Inspect actual rendered frames and the encoded output before reporting a visual change complete. Preserve earlier review cuts when making artistic revisions.
- Reuse earlier frames only when their settings and visual result are unchanged and the handoff is verified. Otherwise render the full sequence.
- Document unavailable capabilities and inaccessible reference films honestly. Launchscene annotations are references, not original animation curves; respect their verification and missing-data labels.

## Assets, licensing and credentials

- Record imported source provenance, author, license, origin and hash in `assets/catalog.json`. For native captures, verify the actual locked Core and Applications revisions and record the guest bundle release separately from the host revision. Mark missing footage as a visible placeholder. Never invent a functioning Xila interface.
- Keep source recordings and original audio outside generated-output directories. Generated frames, Blender files, WAV exports and videos belong under ignored `output/` and are not committed.
- Code is Apache-2.0. Preserve upstream brand notices and Montserrat's SIL OFL notice; imported media retains its own license.
- ElevenLabs is optional and must not be required by local builds or CI. Never consume credits without explicit approval and a budget. The synthetic startup fixture is a technical test, not approved sonic branding.
- Never commit or print API keys, tokens, OAuth credentials or private configuration. Use existing authenticated tools or the host's secure credential flow.
- Do not modify sibling Xila repositories without explicit authorization. Read their current upstream revisions when local checkouts are stale.
