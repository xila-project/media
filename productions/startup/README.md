# Xila startup sound

Produce a short standalone sonic signature for the OS boot sequence first; reuse that same signature in the trailer opening. The direction is majestic, restrained, authoritative and elegant: controlled low-frequency presence, subtle synthetic texture, minimal melodic movement and a dignified harmonic resolution. Avoid a cheerful commercial melody or an excessive cinematic impact.

The initial three-second ElevenLabs candidate is described in `candidates/001/prompt.txt`. Its request and generation provenance are kept beside the prompt. The maintainer approved one initial candidate with a maximum of 5,000 credits; that approval does not authorize automatic retries or further candidates.

Source audio is preserved under `assets/audio/startup/`, outside generated output. Source files are never overwritten by mastering. Generated masters and embedded exports live in ignored `output/startup/`. Until a generated candidate has been reviewed, the default task continues to use the synthetic technical fixture.

```sh
mise run render:startup
# After downloading an actual source:
python3 scripts/audio.py process assets/audio/startup/candidate-001-source.wav --output output/startup/candidate-001 --rate 22050
```

The offline processing pipeline downmixes before measuring, applies two-pass loudness normalization, writes a 48 kHz PCM24 mono master and exports dithered mono PCM16 at 22050, 44100 or 48000 Hz. It verifies loudness and peak levels and writes `validation.json`. Conversion cannot restore quality missing from a lossy provider source; keep its actual format and provenance.

No OS playback implementation is included. ElevenLabs is optional and is never called by builds, tests or CI. Imported audio must be licensed before publication; a generated preview is not automatically an approved or publishable Xila asset.

## Candidate 001 review

The single approved generation is complete: Music v2.5, three seconds, instrumental, 44.99 credits reported. Its original 48 kHz stereo MP3 is preserved locally at `assets/audio/startup/candidate-001-source.mp3`; the source hash and stable provider flow link are in `candidates/001/request.json`. The original asset and generated exports are ignored by Git and are not yet published or licensed for release.

Review `output/startup/candidate-001/master.wav` for the sound itself, then `output/cinematic-opening/opening-startup-001.mp4` for placement in the trailer. The default fixture task is unchanged. See [ElevenLabs integration](../../docs/elevenlabs.md) for connection, cost approval, mastering and reuse.

## Candidate 002 draft

Listening feedback on candidate 001: too simple, effectively one note. Candidate 002 proposes four seconds with three deliberate gestures: low foundation, a small ascending interval over suspended harmony, then a broad dark consonant resolution. The emphasis is stately grandeur and quiet arrogance through rich voicing and breathing space. Its prompt and quoted cost are saved in `candidates/002/`; it has not been generated and requires a separate credit approval.

## Limited-DAC listening check

The startup signature must retain its identity on a limited-quality DAC and a small speaker: use a lower-midrange body, clear audible harmonics, rounded attacks and mono-compatible voicing. Musical grandeur must come from harmonic structure and timbre rather than sub-bass level or stereo width. Candidate 002's draft includes these constraints.

The [classic ESP32 DAC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/dac.html) has 8-bit conversion. This does not describe every ESP32-family chip or an external DAC. The repository provides a deliberately constrained listening profile, separate from the PCM16 delivery export:

```sh
python3 scripts/audio.py audition output/startup/candidate-001/master.wav --output output/startup/candidate-001/dac-8bit.wav
```

The profile downmixes to mono, applies a 180–5000 Hz band limit, resamples to 22050 Hz and writes dithered unsigned PCM8. The accompanying JSON records the profile and explicitly marks it as a simulation with no hardware validation. These bandwidth limits are an engineering stress test, not a measured ESP32 output stage or speaker response. Original source audio and the normal master remain unchanged.

Review the normal and constrained versions at a sensible matched listening level, then test the actual DAC, amplifier and speaker before accepting the sound for release. No operating-system playback code or hardware support claim is introduced here.
