# Application handoff proof

Review 006 is a six-second 3D proof responding to review 005's disconnected flat style. The subject is a specific WebAssembly application reaching Xila and producing a visible result. A named `pixel_painter.wasm` artifact moves toward the official Xila mark, passes behind the runtime foundation, and a graphics-response route reaches a genuine captured application result. An oblique camera pullback and controlled graphite reflections restore the approved material language.

The artifact filename and WebAssembly header were checked against the signed bundle prepared for the earlier native session. `evidence.json` records its payload hash. The transfer, route and timings are conceptual artwork. The output image is the pinned, genuine Pixel Painter screenshot used in the architecture study. Updating to the latest guest UI and recording live action remain pending. This proof evaluates the connection to the subject and the material treatment.

The mark is imported directly from the official SVG. A black backing reserves more than one quarter of its width as clear space. The mark retains its source geometry and orientation. The camera and application artifact move around it.

Typography is prepared from the locked Montserrat WOFF2 using the existing Playwright browser renderer, then applied to a transparent surface in Blender. This avoids Blender's incorrect rendering of some contours from the variable TTF. The helper introduces no new package dependency. Generated label PNGs and videos stay under `output/`.

```sh
mise run render:application-handoff
python3 scripts/video.py validate output/application-handoff/review-006/application-handoff.mp4 --width 960 --height 540 --fps 30 --duration 6
```

The task resolves the brand assets, prepares the label, renders every frame and validates the assembled MP4. CUDA is selected when available; the CPU path for this scene remains unverified. Prepare the label before rendering selected zero-based frames directly:

```sh
python3 scripts/brand.py
node scripts/prepare-application-label.mjs
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup --python-exit-code 1 --python blender/scripts/application_handoff.py -- --device cuda --still 20 --still 100 --still 160
```

Production JSON owns the application name, source illustration, output settings and camera keys. Source imagery is replaceable through the shared screenshot importer. Keep the earlier review cuts for comparison. A full-timeline join and the revised 12-second execution passage follow review of this short proof.

## Verification

The complete 180-frame sequence rendered on the RTX 2060 SUPER using CUDA. H.264 decoding, 960×540 dimensions, 30 FPS and six-second duration passed validation. Encoded frames were inspected across the transfer and result reveal. The packed, versioned label reproduced a full-sequence frame within one RGB level. Repository checks passed with 9 TypeScript tests and 12 Python tests.
