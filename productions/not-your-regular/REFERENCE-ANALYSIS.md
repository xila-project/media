# Reference analysis: measured, not guessed

Measured on 2026-11-18. This document replaces earlier listening-only claims (LISTENING-REPORT.md and LWICD-BLUEPRINT.md) wherever they disagree with it. It covers two references, _Look What I Can Do_ (LWICD, Aditazzz) and _Data Center Fornicator_ (DCF, Private Island TV), and our take 005 as the comparison point.

This is analysis only. We take structure, arrangement and production technique from it. We never copy melodies, lyrics or the exact chord loop.

## Sources and method

**Sources**

- **LWICD:** `output/not-your-regular/listen/lwicd.mp3`, aligned with Aditazzz's timing data from github.com/aditazzz/Suno-YouTube-aditazzz-Music, commit `5f78bb8`, `songs/look-what-i-can-do/build/`:
  - `timed.json`: word-level timings for every line;
  - `sections.json`;
  - `beats.json`.

  The song starts at 0 s in the video audio, so the two line up. Its README states that the track was made with Suno.

- **DCF:** the full 1:45 track from the official "Private Island TV - Topic" YouTube upload. The original clip has been removed from YouTube. The maintainer's local copy is a 29 s ringtone excerpt.
- **Take 005:** `output/not-your-regular/listen/take-005.mp3`.

**Method**

1. **Stems.** Each track was split into vocals, drums, bass and other with Demucs `htdemucs`.
2. **Rhythm.** Onsets were detected per band (kick below 120 Hz, snare/clap 180–3500 Hz, hats above 7 kHz, bass stem, vocal stem). They were folded onto a 16-step grid over a constant tempo fitted to the kick onsets.
3. **Arrangement.** Each stem's RMS was measured per bar, in dB relative to that stem's loudest bar.
4. **Vocal pitch.** pYIN supplied the voicing decision and YIN the continuous f0. From these:
   - **deviation** is the median distance from the nearest semitone, after removing the global tuning offset;
   - **wobble** is the median standard deviation inside a held note;
   - **span** is the distance between the 5th and 95th percentiles.
5. **Chords.** Chroma templates on bass + other, two beats at a time, with the bass-stem chroma giving the root.
6. **Loudness.** FFmpeg `ebur128` (integrated loudness, LRA, true peak).
7. **DCF lyrics.** Transcribed from the vocal stem with faster-whisper `medium.en`.

**Tooling.** All of it is optional and lives outside the repo, so it is not a build dependency:

- a uv venv with Python 3.12, librosa 0.11, Demucs, PyTorch CPU and faster-whisper;
- scripts in `output/not-your-regular/reference/tools/` (`analyze.py`, `rhythm.py`);
- raw results in `output/not-your-regular/reference/data/`;
- stems in `output/not-your-regular/reference/stems/htdemucs/`.

All of these are ignored local outputs.

**Limits**

- Stems are estimates, so every per-stem figure is approximate.
- Chord labels are approximate. A maj7 template can absorb a minor triad a third below, so read roots and functions rather than extensions.
- Bass onset counts are unreliable for legato or sustained bass.
- We make no swing claims. The measured offsets were inconsistent.
- Pitch statistics need sung or tuned material. Spoken lines give large deviations by nature.

## Corrections to the earlier listening reports

| Claim (Gemini / Argon)                   | Measured                                                                                                                                                                                                      |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 129.2 BPM                                | **≈131.1–131.4 BPM**, from linear fits to Aditazzz's own beat times (residual 8–17 ms). The 129.2 in `beats.json` is a librosa tempo bin (the median beat interval), not the real tempo.                      |
| C minor, Eb relative-major chorus        | **G minor.** The pitch-class profile peaks on G, D, Eb, Bb and A. The bass roots give a 2-bar **Gm–Eb–Bb–D** loop, i–VI–III–V with a major V: **one chord every two beats**, used in the verses and the hook. |
| 16th-note hats with off-beat open hats   | **Straight 8th hats**, about 6–7 hits per bar.                                                                                                                                                                |
| Staccato FM bass with an octave bounce   | **Bass is absent from the verses**. Where it plays, it is sparse or sustained (0.1–0.5 detected onsets per bar), with no 16th pattern.                                                                        |
| Kick out only for the Q&A; intro on beat | **No music at all for the first 6.8 s.** A pad enters at 6.8 s and the beat only at 12.3 s.                                                                                                                   |

## LWICD: arrangement timeline

Each stem's level is given in dB relative to its loudest bar. Section names come from `sections.json`.

| Time (s)    | Event                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 0–6.8       | Dialogue completely dry: drums, bass and other all below −44 dB.                                                                 |
| 6.8         | A pad/synth enters under the dialogue (other −7 to −10 dB).                                                                      |
| 12.3        | Drums enter, right after "Close enough".                                                                                         |
| 14.2        | Bass enters. A 4-bar instrumental hook with the vocal-chop motif follows.                                                        |
| 19.8–30.7   | V1: drums and synths, **bass out** (−51 to −61 dB). Bass returns at 30.7 s for the last two bars as a lift.                      |
| 34.4–39.9   | Pre-chorus: drums thin out (−11, −14 dB). Bass out again from 38.1 s.                                                            |
| 39.9–43.6   | **About 2 bars of total stop.** Drums at −67 dB and other down to −49 dB. "Too late!" lands in silence.                          |
| 43.6        | CH1 slams in at full level (drums −5, bass −12, other −12 dB).                                                                   |
| 56.4–65.5   | Post-chorus chant, full, with one dip bar at 60.0 s.                                                                             |
| 65.5–80.0   | V2: drums at −10 dB, **no bass at all**.                                                                                         |
| 81.9–85.5   | BREAK: drums fade, then silence. The question-and-answer runs a cappella.                                                        |
| 85.5        | CH2 at full level.                                                                                                               |
| 98.4–105.6  | V3, first half: bass present, other filtered down (−28 to −37 dB).                                                               |
| 105.6–122   | V3, second half: **texture switch**. Bass out, synths full.                                                                      |
| 122–136.5   | BRIDGE: **no drums, no bass.** A keynote pad builds to 0 dB at 131 s.                                                            |
| 136.5–143.8 | FINAL chorus: drums full, **no bass**, pads at −37 to −43 dB for 4 bars. Pads come up from 143.8 s.                              |
| 151–158     | BREAKDOWN: dialogue **over drums only** (−7 to −12 dB). Bass and pads out.                                                       |
| 158.3       | **Bass slam** on "I knew it!" The drop (160–169 s) is the loudest part of the song: drums −3, bass −4.4, other −5 dB.            |
| 169.2       | Beat cut. The outro dialogue (171–176.7 s) sits in near silence.                                                                 |
| 176.7–186   | After the last line, the **full beat returns at maximum for about 5 bars with no vocal**. The twist ending restarts the machine. |

Loudness is **−16.5 LUFS integrated, LRA 8.4 LU, true peak −3.6 dBFS**. This is not a brickwalled master: the energy comes from contrast.

## LWICD: vocals

**Lead**

- Female, median **D4 (294 Hz)**: a mid-low chest register, not a bright high voice.
- Hook lines reach about C5–D5.
- The drop has the highest median of the song, about Bb4 (467 Hz).

**Verses are hard-tuned near-monotone**

| Section | Median | Span (st) | Deviation (c) | Wobble (c) | Within 15 c |
| ------- | ------ | --------: | ------------: | ---------: | ----------: |
| V1      | D4     |       5.0 |           3.5 |        4.7 |         79% |
| V2      | D4     |       3.0 |           9.1 |        9.9 |         63% |
| V3      | D4     |      17.8 |           5.5 |       14.7 |         74% |
| CH1     | D4     |      18.7 |           8.7 |        8.8 |         65% |
| DROP    | A#4    |      17.3 |           6.0 |        6.2 |         77% |

V2 is effectively one note. Median pitch per word for the first lines:

| Line | Words → pitch                                               |
| ---- | ----------------------------------------------------------- |
| 1    | I'm D4 · a D4 · Senior D4 · Slopcore D4 · Architect D4      |
| 2    | Chief D4 · Executive D4 · of D4 · What's D4 · Next D4       |
| 3    | VP D4 · of D4 · Things D4 · That D4 · Look D4 · Complete D4 |
| 6    | Chief D4 · of D4 · Artificial D4 · Me D4                    |

D is the fifth of G minor. It is a common tone of Gm, Bb and D, and the maj7 over Eb, so a single recited note sits over the moving loop. That is the "elegant, not rap" quality: speech rhythm on a quantised, robot-flat pitch. The melody only opens on the hook, which spans about 13–19 semitones up to C5–D5.

**Male voice**

- 98–143 Hz (G2–D3).
- About 12 lines, **only in dialogue**: intro, break, bridge, breakdown and outro. He never sings.
- He answers in the gaps the band leaves.

**Line lengths**

- **Verse:** one line per bar, about 8 syllables per line (V1: 8, 7, 8, 8, 8, 8, 8, 10).
- **Hook:** 5 syllables in one bar, sung **twice back to back**. The hook takes 4 of the 8 chorus lines, alternating with 8-syllable lines.

| Section   | Bars | Syllables | Syllables/s | Syllables/beat |
| --------- | ---: | --------: | ----------: | -------------: |
| INTRO     | 10.5 |        41 |        2.11 |           0.98 |
| V1        |  7.9 |        65 |        4.44 |           2.06 |
| PRE       |  3.9 |        25 |        3.45 |           1.60 |
| CH1       |  7.9 |        48 |        3.26 |           1.51 |
| POST      |  4.9 |        35 |        3.83 |           1.78 |
| V2        |  7.8 |        63 |        4.34 |           2.02 |
| BREAK     |  1.9 |        20 |        5.56 |           2.58 |
| CH2       |  8.9 |        48 |        2.91 |           1.35 |
| V3        | 11.8 |        88 |        4.03 |           1.87 |
| BRIDGE    |  7.8 |        49 |        3.37 |           1.56 |
| FINAL     |  7.8 |        51 |        3.51 |           1.63 |
| BREAKDOWN |  5.9 |        20 |        1.83 |           0.85 |
| DROP      |  4.9 |        20 |        2.20 |           1.02 |
| OUTRO     |  8.3 |        17 |        1.11 |           0.51 |

Bar counts use the 129.2 BPM grid from `sections.json`. Syllables are estimated with a vowel-group heuristic. The verses are the densest sung parts, at about 2 syllables per beat, which is eighth notes. The hook relaxes to about 1.5 syllables per beat.

**Groove**

- Four-on-the-floor kick.
- Snare/clap-band energy on every beat: the kick transient plus a clap on 2 and 4 cannot be separated.
- Straight 8th hats.
- No rolling bass.

## DCF: measured profile

**Tempo, key and level**

- **129.8 BPM**, 1:45.
- **F minor, one-chord drone.** It vamps on Fm almost throughout, with chromatic neighbours (E, F#/Gb) for menace.
- **−12.6 LUFS, LRA 3.5 LU**: a constant, compressed club level, unlike LWICD's dynamics.

**Groove.** Four-on-the-floor kick, dense claps, 8th hats, and an **off-beat house bass** that hits on the 8th-note offbeats.

**Vocals**

- **Lead:** a deep male voice, hard-tuned and monotone **on the tonic F2 (about 87 Hz)**. In the chorus, deviation is 7.1 c and wobble 3.3 c, so it is clearly quantised.
- **Female hook:** "Ram it in, hot and wet, plug it in", also monotone, on Bb3/B3 with a half-step wiggle.
- The chant section (61–74 s) is the only melodic, call-and-response part.

**Lyrics**

- The chorus is a list of four job titles, all ending in "-ator" ("…incubator / …accelerator / … / a data center fornicator").
- Call-and-response: "We're coming for your land / Put your hands up".
- A spoken "Wait what?"
- A tonal flip in the bridge ("Oh my god we screwed the planet"), then an outro chant loop.
- The sensuality comes from **deadpan tech double-entendre delivered flat**, never from breathy singing.

## Take 005 against the references

| Measure                 | LWICD                                  | DCF                    | Take 005                                                |
| ----------------------- | -------------------------------------- | ---------------------- | ------------------------------------------------------- |
| Tempo                   | ≈131                                   | 129.8                  | 130.0                                                   |
| Key                     | G minor                                | F minor (drone)        | F minor (the prompt asked for C minor: key is ignored)  |
| Harmonic rhythm         | a chord every 2 beats                  | static drone           | mostly static, one chord per bar or less                |
| Hats                    | straight 8ths (~6/bar)                 | 8ths                   | **16ths, 10–12/bar**                                    |
| Bass                    | absent in verses, sparse elsewhere     | off-beat 8ths, 3–5/bar | **rolling 16ths, 5–9 onsets/bar, everywhere**           |
| Verse drums             | −7 to −10 dB (lighter than the chorus) | constant               | **−1.0 dB in V1, the loudest section**                  |
| Loudness / LRA          | −16.5 LUFS / 8.4 LU                    | −12.6 / 3.5            | −12.2 / 5.6                                             |
| Verse vocal tuning      | deviation 3.5 c, wobble 4.7 c          | 7–10 c in the chorus   | **deviation 23 c, wobble 30 c**                         |
| Stops before the chorus | 2-bar total stops, twice               | none                   | one stop-time (85–92 s); the pre-chorus stop is partial |

Deviation needs a reference point. An untuned voice lands at random relative to the semitone grid, which gives a median deviation of about 25 c. Take 005's verses, at 23 c, are therefore **statistically untuned**. That is the measurable reason they read as talk-rap: a narrow, speech-like pitch without quantisation. LWICD uses the same narrow range, but hard-tuned.

The boot log and bridge show a male median of about 105–109 Hz, which confirms the role swap reported in `takes/005/REVIEW.md`.

## What makes the "3 a.m." feeling

Both references put **a flat, hard-tuned recitation over a plain four-on-the-floor groove at about 130 BPM**, and save the melody for one sticky hook. LWICD then adds drive through **contrast**: instruments are withheld, the band stops dead before the chorus, and the bass is held back until the drop. DCF does the opposite and sustains one relentless level. Take 005 got its drive from a busy rhythm section, with 16th hats and rolling bass, so every section sounds the same and the voice has nowhere to land.

## Production rules for our track

1. **Verses:** hard-tuned near-monotone (zero retune speed) on one chord tone, usually the fifth, with speech rhythm at about 8 syllables per bar. The melody opens only on the hook.
2. **Groove:** four-on-the-floor kick, claps on 2 and 4, straight 8th hats. **No rolling 16th bass.**
3. **Bass:** withheld in the verses, brought in for the pre-chorus and chorus, and **first heard at full level at the drop**.
4. **Harmony:** a fast harmonic rhythm, one chord every two beats, in minor with a major V for the lift. **Use a different loop from LWICD's Gm–Eb–Bb–D.**
5. **Stops:** a 2-bar a cappella stop before each chorus, and a cold slam back in.
6. **Bridge and late sections:** a drumless bridge; a final chorus without bass that builds into the drop; a breakdown over drums only.
7. **Drop:** the loudest part of the song.
8. **Outro:** dialogue in silence, then the beat comes back alone for the button.
9. **Master:** about −14 to −16 LUFS integrated with an LRA of about 8 LU. Energy should come from contrast, not limiting.
10. **Male voice (ALIX):** speaks only in the gaps, low (100–140 Hz), and never sings over the beat. DCF shows that a deep, hard-tuned monotone line is also an option for one moment.
11. **Hook:** about 5 syllables in one bar, sung twice back to back, taking half of the chorus lines.
12. **Sensuality:** deadpan double-entendre delivered flat, kept to a wink.
13. **Never copy** the melodies, the lyrics or the exact chord loop.

## Production paths now open

- **Remix take 005 from its local stems.** The Demucs stems mean the ElevenLabs API is no longer needed for this. We can:
  - mute the bass in the verses and lower the drums there;
  - fix the breakdown, where the drums return early;
  - build real 2-bar stops;
  - hard-tune the vocal stem toward a monotone chord tone.

  Demucs artefacts on AI-generated audio still need to be checked by ear.

- **Regenerate** with ElevenLabs or Suno, writing the rules above into the prompt explicitly: one-note hard-tuned verses, 8th hats, no bass in the verses, stops before the choruses, a bass-less final chorus and the drop as the peak.
