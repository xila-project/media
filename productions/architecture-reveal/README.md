# Kinetic architecture study

Review 002 changes the trailer's emphasis to a moving, monochrome structure. Modules assemble around the official Xila mark, channels draw upward, white signals travel between levels, and the camera sweeps from a close material view to the complete structure. A brief Pixel Painter illustration appears within the upper level between 5.9 and 6.8 seconds. The passage runs seven seconds and is silent.

The forms are a conceptual visualization of a Rust core, WebAssembly execution and applications. Counts, dimensions, signal speeds and routes are artistic choices. They communicate motion and modularity. The complete SVG is imported from the pinned Brand repository, preserving every module, curve and gap. Its settled size reserves clear space within the foundation.

## Sources and reference use

The previous product study used Applications `7bf59dbb` and Core `cd211cc7`, which preceded the current activity, settings, terminal and drawer changes. This capture instead uses a clean archive of Platforms `e6ee588744e3c968696b74ead6d19f02f9d68dc6`. Its lockfile resolves Applications `5e2507e0` and Core `dab15367`. The archive was built in its own directory so Platforms' Cargo configuration was active. Working checkouts were preserved.

`capture.json` records the complete dependency pins and released Wasm bundle. Pixel Painter was launched through the current native session, and the three stepped paths were drawn through its actual input controls. Its source code is unchanged between the two Applications revisions. The screenshot's hash, author and licensing are in the shared asset catalog.

The Launchscene review covered the narrative structure of [Linear Releases](https://launchscene.app/v/linear-releases), its product-panel reveal and adjacent camera passage. Its sequence moves from a hook into a specific feature reveal and then a CTA. The narrative annotations have a human quick review; camera and audio measurements have no individual verification. Exact Bézier curves are unknown. Full-film playback remains unreviewed.

The inspected [Linear Agent architecture scene](https://launchscene.app/v/linear-agent?t=29.733) is AI-annotated and unverified. Its perspective, progressive focus and restrained lines served as visual reference only. The source frame was inspected through Launchscene. This study's assembling solids, vertical progression, paths, timings, camera and materials are original production choices. No source imagery, sound or proprietary models are included.

The GUI is a supporting illustration. The geometry, movement, controlled light and official mark carry the sequence. The earlier 14-second screen-focused cut is preserved as `output/review/xila-trailer-review-001.mp4`.

## Render

```sh
mise run render:architecture-reveal
python3 scripts/video.py concat \
  output/cinematic-opening/opening-bootsplash.mp4 \
  output/architecture-reveal/review-002/architecture-reveal.mp4 \
  -o output/review/xila-trailer-review-002.mp4
python3 scripts/video.py validate output/review/xila-trailer-review-002.mp4 \
  --width 960 --height 540 --fps 30 --duration 15
```

Configuration owns the camera keys, layer centers and arrival times, source screenshot, duration, frame rate, resolution and illustration window. Increment the numbered review before the next artistic revision. CUDA is selected when available. The CPU path for this study remains unverified.

For selected zero-based frames before a full render:

```sh
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup \
  --python-exit-code 1 --python blender/scripts/architecture_reveal.py -- \
  --device cuda --still 25 --still 85 --still 155 --still 188
```

Replace the supporting illustration through the common importer:

```sh
python3 scripts/screens.py import /path/to/capture.png \
  --production architecture-reveal --slot application \
  --origin 'SOURCE REVISION AND CAPTURE CONTEXT' \
  --author 'SOURCE AUTHOR; capture by YOUR NAME' --license 'SOURCE LICENSE'
```

The importer preserves animation settings. Verify the runtime's actual locked Core and Applications revisions before making a new capture. Record the guest release separately from the native host revision. See the shared [native capture workflow](../../docs/native-capture.md).

## Verification

Repository checks passed with 9 TypeScript and 12 Python tests. Extracting shared camera and Cycles helpers was checked against an earlier full-sequence product frame: only 12 of 1,555,200 decoded RGB channel values differed, each by one level. The source camera transform and scene composition match. The complete 210-frame passage and assembled 15-second cut passed H.264 decoding, dimension, duration and frame-rate validation. Encoded output and settled brand clear space were inspected.
