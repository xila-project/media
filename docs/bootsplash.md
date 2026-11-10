# Bootsplash reference

The logo introduction follows [Core's bootsplash timeline](https://github.com/xila-project/core/blob/dab153676f7d2c02cbee57fa49211ed5db7660cf/libraries/bootsplash/src/lib.rs), pinned at `dab153676f7d2c02cbee57fa49211ed5db7660cf`. The adjacent local Core checkout predates this animation; it is not the reference for this production.

`motion-canvas/components/bootsplash-timeline.ts` ports Core's fixed-point arithmetic and timing:

- Center square fades in over 240 ms.
- Arms begin at 150 ms, staggered clockwise every 100 ms, each lasting 450 ms with cubic ease-out. Assembly ends at 900 ms.
- The initial outward offset is one fifth of the symbol width.
- The ripple period is 1600 ms; each arm pulses for 800 ms, with the next arm starting halfway through. Peak travel is one twentieth of the symbol width, with opacity falling to 180/255.
- The first ripple leaves arms at rest until their first turn. Later cycles wrap continuously.

`bootsplash.tsx` isolates the four paths and center rectangle directly from the hash-verified official SVG. It preserves each element's geometry, the upstream group transform, and their common viewBox. No path coordinates are copied into animation source. The settled pose reproduces the official symbol; the moving poses follow the existing Core bootsplash treatment. Modules never rotate, stretch, or change color.

The trailer uses a 320 px symbol on the 1920×1080 logical canvas. Its three-second introduction contains the assembly and one full ripple, followed by a trailer-specific half-second fade to black. This is a media adaptation of the runtime animation, not a recording of the operating system. It does not reproduce LVGL's resolution-specific pixel snapping.

Run `npm run render -- --production logo` for the isolated introduction. `npm test` checks assembly endpoints, clockwise order, ripple extrema and first-cycle behavior against Core's timeline contract. When updating the animation, review the pinned Core implementation, update its provenance in `productions/trailer/production.json`, and inspect the actual render.
