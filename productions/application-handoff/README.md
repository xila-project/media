# Execution study

Review 007 replaces review 006, whose labelled card, thin diagram line and small late result read as a slide, and whose overall art direction was judged too weak. It is an eight-second, single-shot study for the scenario's 00:28–00:40 execution passage.

## Story in one shot

Light leaves the official Xila mark, inlaid in a polished black floor. It travels along three stepped routes in metered stages, pausing at each boundary before resuming. The routes reach a monolithic surface, which lights up with the genuine Pixel Painter capture. The floor routes are the capture's own three strokes, so the viewer recognises the drawing on the screen as the path the light just travelled. Xila → execution → application result, without explanatory copy.

## Art direction

This brief applies to the remaining 3D passages unless a review supersedes it.

- **One grounded world.** A continuous polished black floor with faint architectural joints and light haze. Objects stand on it, reflect in it and have a readable scale. Avoid floating cards and objects in a void.
- **Light is the actor.** Signals are light inlaid in dark glass channels, not drawn lines. Pauses and stages carry meaning; decoration does not.
- **Geometry from the subject.** Shapes come from real sources: the official mark and measured application output. Do not invent diagrams.
- **Deep blacks, controlled highlights.** AgX Medium High Contrast, low haze, one broad backlight and a low rim. Restrained bloom and vignette in the compositor.
- **Camera.** Start low and long with a shallow depth of field, then crane to a composed wide view that holds the whole relationship. Rotation belongs to the camera; the mark keeps its orientation.

## Source fidelity and scope

- Stroke centerlines in `production.json` were measured from the pinned capture (`screen-ad6d…`, 30 px strokes) and mapped to the floor at 12.6 mm per pixel. The final step of each route into the surface base is an artwork extension.
- The result surface shows the existing pinned native screenshot without modification. It is not a live recording; refreshing to the latest guest UI and recording the actual drawing action remain pending.
- Advance speed, pauses and stagger illustrate Wasmi fuel-sliced cooperative execution editorially. They carry no measured timing.
- The mark is imported from the official SVG and lies flat on a black plate reserving more than a quarter of its width as clear space. The camera views it obliquely; its geometry and orientation are unchanged.
- `pixel_painter.wasm` is engraved on the floor as supporting detail, using the locked Montserrat rendered through the existing Playwright helper.
- The floor roughness comes from ambientCG `SurfaceImperfections015` (CC0 1.0), catalogued with its hash in `assets/catalog.json`.

## Render

```sh
mise run render:application-handoff
python3 scripts/video.py validate output/application-handoff/review-007/application-handoff.mp4 --width 960 --height 540 --fps 30 --duration 8
```

Quick look checks of selected zero-based frames at reduced samples:

```sh
python3 scripts/brand.py
node scripts/prepare-application-label.mjs
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup --python-exit-code 1 --python blender/scripts/application_handoff.py -- --device cuda --samples 32 --still 10 --still 160 --still 230
```

Each frame takes about 3–4 s at 48 samples on the RTX 2060 SUPER with CUDA. The CPU path for this scene is unverified. Generated frames, label PNGs and videos stay under `output/`; earlier review cuts remain in `output/review`.

## Verification

The complete 240-frame sequence rendered on CUDA at 48 samples. The assembled MP4 passed validation as H.264, 960×540, 30 FPS and eight seconds. Encoded frames were inspected at half-second intervals across the mark opening, staged light travel, crane and result reveal. Repository tests, type checks, lint, formatting and `scripts/validate.py` passed. Sound, the full 12-second passage timing and the live drawing recording remain to be produced.
