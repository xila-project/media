# Product reveal study

This six-second passage follows the reviewed cinematic opening. A close oblique view of Xila's actual calculator resolves into two floating screenshot surfaces, with the real file manager behind it. A continuous camera pullback creates parallax before a restrained final drift. The review is silent.

The sources were captured from `native_example` through Xila's own `xila-debug` screenshot operation, at 1280×800. The calculator result was entered through its real controls. These are still captures animated in 3D. No interface behavior is simulated. `capture.json` records the native revision, existing local changes, dependency sources and lockfile hashes. Each imported PNG has its own provenance and hash in `assets/catalog.json`.

## Render and review

```sh
mise run render:product-reveal
python3 scripts/video.py concat \
  output/cinematic-opening/opening-bootsplash.mp4 \
  output/product-reveal/review-001/product-reveal.mp4 \
  -o output/review/xila-trailer-review-001.mp4
python3 scripts/video.py validate output/review/xila-trailer-review-001.mp4 \
  --width 960 --height 540 --fps 30 --duration 14
```

The render task reads dimensions, frame rate, duration, review number and sample count from `production.json`. It regenerates the full frame sequence and validates the resulting H.264 video. CUDA is selected when available, with a CPU fallback for other machines. The render manifest records the actual device. To require either backend explicitly, run the script inside the pinned Blender environment.

```sh
mise exec aqua:blender/blender@4.5.15 -- python3 scripts/render_product.py --device cuda
mise exec aqua:blender/blender@4.5.15 -- python3 scripts/render_product.py --device cpu
```

For composition checks before a full render, select zero-based frames.

```sh
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup \
  --python-exit-code 1 --python blender/scripts/product_reveal.py -- \
  --device auto --still 24 --still 90 --still 165
```

The output lives in `output/product-reveal/review-001/`. Increment the three-digit `review` value before an artistic revision to preserve earlier rendered cuts. Change the production dimensions for a final-resolution render, and render the opening at the same dimensions before assembling both sections.

## Replace a capture

The `screens` entries own source asset IDs and the logical aspect ratio. The `panels` entries own world-space width, placement, orientation and reveal timing. The camera keys live separately. Replacing an asset preserves those animation choices, and fits the new image inside its slot without stretching it.

```sh
python3 scripts/screens.py import /path/to/new-calculator.png \
  --production product-reveal --slot calculator \
  --origin 'YOUR SOURCE URL OR NATIVE CAPTURE REVISION' \
  --author 'SOURCE AUTHOR; capture by YOUR NAME' \
  --license 'SOURCE LICENSE'
python3 scripts/validate.py
mise run render:product-reveal
```

Use `--slot files` for the rear surface. Commit the PNG, catalog and production JSON together. See the shared [screen workflow](../../docs/screens.md) and [native capture commands](../../docs/native-capture.md).

## Reference and creative decisions

`REFERENCE.md` preserves Launchscene's returned brief for Linear Releases scene 4 unchanged. Its source window is 0.75 seconds. The inspected reference frame shows dark product panels in perspective on black. Its overall annotation has a human quick review, while the camera, OCR and audio tracks lack individual verification. Exact trajectories, fonts and Bézier curves are unknown.

The Xila shot uses original camera keys, a six-second pacing choice, clamped Blender Bézier interpolation, staged exposure and genuine Xila screenshots. Those are production choices. No reference imagery, text, interface, music or animation curve is imported. The source frame was inspected through `get_frames`; full-film playback remains unreviewed.

Review 001 rendered all 180 frames with Blender 4.5.15 and CUDA on an NVIDIA GeForce RTX 2060 SUPER. The six-second section and the assembled 14-second, 420-frame review passed H.264 decoding, dimensions, duration and frame-rate validation. Encoded frames were inspected across the cut and camera move. Repository checks passed with 9 TypeScript tests and 12 Python tests. The CPU rendering path remains unverified for this passage.

This is a composition review. Typography, the architecture passage, sound and the full-film ending remain to be developed after review of this stage.
