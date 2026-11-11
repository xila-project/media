# Launch film

The two-minute Xila launch film, produced as one continuous world under the art direction recorded in [the execution study](../application-handoff/README.md#art-direction). Review 001 is a full-length **previz**: every passage of [the scenario](../trailer/SCENARIO.md) is staged, lit, timed and rendered at 960×540 with low samples, so the direction and pacing can be judged as a whole before passages are refined.

## Structure

`production.json` owns the look, copy, screens and shot list. A shot names a **set**, the set time it starts at (`offset`), its duration and camera keys in set time. The escalation montage reuses the other sets with new cameras, so geometry and timing exist once.

| Shot                | Set          | Scenario passage                                                           |
| ------------------- | ------------ | -------------------------------------------------------------------------- |
| 01-recognition      | recognition  | Extruded official mark under a moving strip; ignites, Core ripple at 5.3 s |
| 02-foundation       | foundation   | Floor slabs arrive into alignment; three routes leave the mark             |
| 03-operating-system | field        | Ordered field locks in rows; “An operating system.” / “Built in Rust.”     |
| 04-execution        | execution    | Light follows the measured Pixel Painter strokes into the result surface   |
| 05-proof-of-life    | proof        | Genuine captures fill the surface; the stroke continues as a route         |
| 06-embedded         | embedded     | Compact board under a macro camera; output surfaces open around it         |
| 07-coherent-system  | namespace    | One request, a junction, Files / Devices / Pipes respond                   |
| 08-open-source      | opensource   | Slabs separate over a seam of light; “Open source.”                        |
| 09a–09f-escalation  | (reused)     | Six cuts: pulse, slabs, overhead, sweep, capture, convergence              |
| 10-controlled-power | power        | Lights drain back to the mark; a final pulse; top-down on the mark         |
| identity            | final-reveal | Official flat lockup, description and URL (Motion Canvas, 12 s)            |

Code: `blender/scripts/film_world.py` (shared world, materials, routes, mark, surfaces, copy, camera, finishing) and `blender/scripts/launch_film.py` (sets). `scripts/prepare-copy.mjs` renders every line from the locked Montserrat and fails if the browser falls back to another face. `scripts/render_film.py` renders, renumbers, assembles and validates each shot, then concatenates the film.

```sh
mise run render:launch-film                                    # everything
python3 scripts/render_film.py --device cuda --shots 04-execution --keep   # one shot, reuse the rest
```

Quick stills in set-time frames:

```sh
node scripts/prepare-copy.mjs launch-film
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup --python-exit-code 1 \
  --python blender/scripts/launch_film.py -- --shot 06-embedded --device cuda --samples 8 --still 100
```

## Sources and honesty

- The mark is the official SVG, extruded perpendicular to its paths only in the recognition close-ups; it is flat, white and on a quarter-width black clear-space plate elsewhere. Rotation belongs to the camera.
- The recognition ripple comes from the shared Core bootsplash timeline (`scripts/bootsplash-keyframes.mjs`); no Python timing model exists.
- The execution routes are the measured stroke centerlines of the pinned Pixel Painter capture. Speeds, pauses, counts and the route into each surface are artwork.
- Screens show genuine material only: the pinned Pixel Painter and drawer captures, and three native recordings (`native-003`: drawer launch, drawing, activity) recorded at Platforms `b655fe2a` with locked Core `f2978da3` and Applications `a8ed9a4b`, guest Pixel Painter 0.1.0 (see `capture.json`). They are imported under `assets/footage` with per-frame hashes.
- The recordings were sampled at about 5.5 fps by `xila-debug screenshot`. `scripts/footage.py retime` holds the latest real frame at each 30 FPS output time; nothing is interpolated or invented. The drawer launch plays at 1.2× and the drawing at **3×** real time (the escalation shows its last second, 15.8–18.8 s, at 3×). The activity view plays in real time; its memory values include screenshot-capture overhead.
- The output surfaces in the embedded and execution passages are blank glows, deliberately not interfaces. No hardware, board or performance claim is made.
- Files, Devices and Pipes illustrate the VFS's shared namespace (see the [content evidence](../trailer/CONTENT-EVIDENCE.md)); the forms are abstract.
- There is no sound. Music, the startup signature and sound design need a separate review and, for ElevenLabs, an approved budget.
