# WebAssembly execution motion study

A twelve-second 2D motion and typography treatment for scenario 00:28–00:40. Abstract modules approach a runtime threshold, pause and advance through it. A pointer-like signal enters a module, an abstract drawing stroke develops, and a response travels outward. The camera treatment pushes into the action before a brief, genuine native drawer illustration at 11.2 seconds prepares the next recorded launch shot.

The larger headline is `Built to be built upon.` Supporting typography identifies `WebAssembly applications.` The source relationships are documented in [content evidence](../trailer/CONTENT-EVIDENCE.md). Timings, channels and module counts are editorial choices. The graphics illustrate execution and the guest graphics round trip. The actual native capture is a fixed screenshot from the session pinned in `../architecture-reveal/capture.json`, imported with its own catalog hash.

```sh
mise run render:wasm-execution
npm run render -- --production wasm-execution --resolution 960x540
python3 scripts/video.py concat output/rust-core/rust-core.mp4 output/wasm-execution/wasm-execution.mp4 -o output/review/rust-wasm-study-005.mp4
python3 scripts/video.py validate output/review/rust-wasm-study-005.mp4 --width 960 --height 540 --fps 30 --duration 22
```

This review covers the revised Rust and execution passages as a standalone 22-second study. Its 2D treatment still needs a composition review alongside the approved 3D opening and kinetic material. The additional bridge before scenario 00:18, the live GUI recording after 00:40 and sound remain pending.

Production JSON owns the copy, output defaults and replaceable drawer slot. Replace that source through `scripts/screens.py import --production wasm-execution --slot drawer` with the required source provenance arguments.
