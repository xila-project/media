# Xila Media

Reproducible multimedia production for [Xila](https://www.xila.dev/), using Motion Canvas, optional Blender and FFmpeg. Official identity assets remain owned by [xila-project/brand](https://github.com/xila-project/brand); this repository resolves a hash-verified, immutable snapshot.

**Work in progress:** the tooling, bootsplash adaptation and audio processing work locally. The first trailer was a pipeline proof of concept; the cinematic opening is now under creative review. CI, contributor documentation and the final trailer edit are still being completed.

## Local use

Install [Mise](https://mise.jdx.dev/), then:

```sh
mise trust
mise install
mise run deps:install
mise run preview
```

Node 24.22.0, Python 3.13.18 and FFmpeg 7.1.1 are pinned. Blender 4.5.15 is activated only by Blender tasks. Python scripts use the standard library; there is no Python package environment to install.

```sh
mise run render:logo                 # Reviewed Core bootsplash adaptation
mise run render:trailer              # Earlier 15-second pipeline proof of concept
mise run render:cinematic-opening    # Eight-second camera, material and bootsplash study
mise run render:product-reveal       # Earlier screen-focused study
mise run render:architecture-reveal  # Current kinetic study with a brief application illustration
mise run render:startup              # Synthetic fixture and normalized WAV exports
npm test
npm run typecheck
npm run lint
```

Individual scenes can be rendered with `npm run render -- --scene architecture --resolution 1280x720 --fps 30`. Video outputs are H.264 MP4; source frame sequences and generated media stay under ignored `output/`.

The [kinetic architecture study](productions/architecture-reveal/README.md) develops the current motion direction, with a brief capture from a current native session.

See the [replaceable screen workflow](docs/screens.md) for importing screenshots, preserving framing and assembling independent sections.

See the [bootsplash reference](docs/bootsplash.md) and [cinematic study notes](productions/cinematic-opening/README.md). The startup fixture is a technical test, not approved sonic branding. [ElevenLabs startup candidates](productions/startup/README.md) are available for listening review; see the [optional audio workflow](docs/elevenlabs.md). No ElevenLabs access or paid generation is required for any build.

## Source and licensing

Code is Apache-2.0. Brand assets retain the upstream Apache-2.0 notices; Montserrat retains SIL OFL 1.1. Resolve them with `npm run brand:sync` or `python3 scripts/brand.py --local ../brand`. Imported recordings and audio need explicit provenance in `assets/catalog.json`; native screenshot sources are bundled for the product study; moving screen recordings remain to be captured. Never commit credentials or generated renders.
