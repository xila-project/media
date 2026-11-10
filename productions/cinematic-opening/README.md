# Cinematic opening study

A six-second visual-direction review, rendered at 960×540 and 30 FPS. It establishes material, lighting, camera movement and reveal pacing before committing to the full launch-film edit. It is silent; no music, effects, voice generation or paid services are used.

The camera starts inside a tight oblique detail of the monogram and pulls back to the complete symbol. Physical strip lights progressively reveal its five modules. The last part settles into a frontal composition with clear space. The logo itself never rotates or changes its planar geometry. A shallow perpendicular extrusion is a cinematic material treatment explicitly requested for this film; the flat official SVG remains the brand master. There are no particles, invented hardware, fake interfaces or product claims.

```sh
mise run render:cinematic-opening
```

Outputs are ignored under `output/cinematic-opening/`: the Blender scene, PNG frames, a render manifest and `opening.mp4`.

For a fast lighting check, render selected zero-based frames:

```sh
mise exec aqua:blender/blender@4.5.15 -- blender --background --factory-startup --python-exit-code 1 --python blender/scripts/cinematic_opening.py -- --still 15 --still 75 --still 179
```

The production JSON owns the camera keys, dimensions, sample count, material and brand pin. `--resolution 1920x1080` renders final-resolution frames; assemble and validate them with `scripts/video.py` using the matching dimensions. The Mise review task intentionally uses the 960×540 default.

The previously reviewed Motion Canvas bootsplash remains available through `mise run render:logo`. It will be integrated into the revised trailer after this shot's visual direction is reviewed. The existing 15-second trailer is the earlier pipeline proof of concept, not the finished cinematic direction.

## References and access limits

- [Apple Mac Pro teaser](https://www.youtube.com/watch?v=SQl2FjaKCAQ): the supplied YouTube video was unavailable to the downloader. A [three-second reveal segment from Apple's media server](https://www.apple.com/media/us/mac-pro/2013/16C1b6b5-1d91-4fef-891e-ff2fc1c1bb58/videos/macpro_intro_desktop.mp4) was downloaded only into the ignored research cache and inspected as sequential frames. Observed: a near-black shell, restrained reflected light, and a partial reveal becoming readable. This is not a claim to have viewed the full teaser.
- [PS5 hardware reveal](https://www.youtube.com/watch?v=RkC0l4iekYo): page title verified, but video playback/download was unavailable in this environment. Scale and escalation are taken from the user's supplied direction; no shot-by-shot analysis is claimed.
- [Linear Releases](https://launchscene.app/v/linear-releases): the public scene breakdown was read. It describes camera movement and depth of field connecting abstract geometry to product views. The film itself was not viewed. The [MCP endpoint](https://launchscene.app/api/mcp) requires OAuth; no authenticated connection was available during this study.
- [Nothing launch presentation](https://nothing.community/d/35792-phone-3-and-headphone-1-are-here): the official post points to its launch video. No particular film was viewed; identity and restraint follow the user's brief.

These are references for creative principles. No source video, soundtrack, model, proprietary shot or reference frame is included in the repository or the Xila render. The actual motion, camera, lighting and scene are original procedural work.
