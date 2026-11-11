# Replaceable screens

Production JSON owns the screen slots. The asset catalog owns source provenance. Reusable `Screen` nodes resolve a slot's asset ID and fit the image inside the configured rectangle while preserving its aspect ratio. Animate the returned node to move, scale or fade the screen independently of its content.

The initial slot is `screens.main` in `productions/trailer/production.json`. Its width, height and position use the Motion Canvas logical 1920×1080 coordinate system. A null asset produces a visible placeholder. The existing `footage` option continues to accept a cataloged recording.

## Import or replace a screenshot

Capture the actual Xila interface. Keep browser chrome, debug overlays, private data and authentication secrets out of the capture. Use the source's actual author and license in the command below.

```sh
python3 scripts/screens.py import /path/to/desktop.png \
  --production trailer --slot main \
  --origin 'https://platforms.xila.dev/demonstrations/wasm/en/' \
  --author 'Xila contributors; capture by YOUR NAME' \
  --license 'Apache-2.0'
python3 scripts/validate.py
npm run render -- --production trailer --scene footage --resolution 960x540 --fps 30
```

The importer checks the PNG/JPEG encoding and decoding, stores a content-addressed source under `assets/images/screens/`, records its hash and dimensions in `assets/catalog.json`, and updates only the selected slot's asset ID. Running it again with a different screenshot preserves the slot's framing and animation. An identical source reuses its existing catalog entry and provenance.

Review the resulting `output/trailer/footage/footage.mp4`, then commit the production JSON, catalog and source image together. Previous sources remain available for earlier revisions. A failed import preserves the previous slot. Import operations serialize on an ignored advisory lock file on Linux/macOS.

The current trailer is the earlier pipeline proof of concept. Its footage scene exercises this reusable component. The cinematic product passage is still in development.

## Create another slot

Add an entry alongside `main` with an `asset` ID or null, a positive `width` and `height`, and a two-number `position`. Use it in a scene with `view.add(Screen(production.screens.secondary))`. Both the importer and renderer resolve the slot at build time, so each updated source requires a new render of its scene.

## Assemble reviewed sections

Render each section independently at matching dimensions, pixel format, frame rate and stream time base. The shared assembler can join H.264 sections through stream copy. Its review output contains video only.

```sh
python3 scripts/video.py concat \
  output/cinematic-opening/opening-bootsplash.mp4 \
  output/trailer/footage/footage.mp4 \
  -o output/review/assembly.mp4
python3 scripts/video.py validate output/review/assembly.mp4 \
  --width 960 --height 540 --fps 30 --duration 11
```

This example is a technical assembly check. Review the edit and add an approved soundtrack separately with `scripts/video.py soundtrack`. Generated media stays under ignored `output/`.
