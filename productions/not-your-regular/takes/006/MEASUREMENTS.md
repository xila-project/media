# Take 006: measurements

Take 006 was generated on 2026-11-18 from `composition-plan.json` (19 chunks, 91 bars, 168.0 s) with `music_v2_5` over the REST API. It cost 2,310 credits.

The measurements use the same method as REFERENCE-ANALYSIS.md:

- Demucs `htdemucs` stems.
- `analyze.py` for stem levels per bar and per section.
- `rhythm.py` for onsets per bar on a fitted grid and for vocal tuning.
- ebur128 for loudness.
- A faster-whisper transcript of the vocal stem (`transcript-whisper.json`) to check which lines were actually performed.

Sections come from the planned chunk durations. The chunk boundaries line up with the measured level changes (for example, the stop is silent from 80.7 to 84.4 s against the planned 79.4 to 84.9 s), so the API respected the section timing.

Take 006 is the first take whose sung verses are measurably near-monotone and hard-tuned, with a simple groove. However, every line meant to be spoken in a silence came back as silence with no voice, and verse 1 was never sung.

## Rules

| Rule                                                           | LWICD                              | Take 005                               | Take 006                                                                               | Result                                    |
| -------------------------------------------------------------- | ---------------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------- |
| Tempo about 130 BPM                                            | 131.1                              | 130.0                                  | 129.0                                                                                  | Pass                                      |
| Key hint (asked A minor)                                       | G minor                            | F minor (asked C minor)                | F major profile, r = 0.73                                                              | Fail (key is still ignored)               |
| Verses near-monotone and hard-tuned: deviation / wobble / span | V1 3.5 c / 4.7 c / 5.0 st          | V1 23.1 c / 29.9 c; V2 25.2 c / 23.7 c | V2 11.9 c / 21.2 c / 5.0 st; V3 8.1 c / 6.0 c; boot log 8.5 c / 2.0 st; all on F4      | Mostly pass (V2 is less tight than LWICD) |
| Straight 8th hats in verses (onsets per bar)                   | 5.9–7.3                            | up to 11–12                            | 6.4–7.3                                                                                | Pass                                      |
| No rolling bass (bass onsets per bar in verses)                | about 0.1                          | 5.5–9.1                                | 1.1–2.8                                                                                | Pass                                      |
| Bass withheld in verses (level vs the loudest bar)             | V1 −32 dB, V2 −62 dB               | V1 −5.5 dB, V2 −7.6 dB                 | V1 −20.5 dB, V2 −13.2 dB, V3 −8.2 dB                                                   | Partial (verse 1 only)                    |
| No bass in the final chorus                                    | −62 dB                             | n/a                                    | −3.5 dB                                                                                | Fail                                      |
| Drop is the loudest part                                       | drums −4.3, bass −5.9, the maximum | not the loudest                        | drums −0.3, bass −1.0                                                                  | Marginal pass (chorus 2 is close)         |
| Silence before chorus 1                                        | drums −67 dB                       | 2 bars with a riser                    | drums −0.7 dB: the beat keeps playing                                                  | Fail                                      |
| Silent stop-time before chorus 2                               | drums −67 dB                       | silent                                 | drums −36 to −68 dB, bass −54 dB                                                       | Pass (silent)                             |
| Drumless bridge                                                | drums −25 to −72 dB                | not drumless                           | drums −53 to −58 dB                                                                    | Pass                                      |
| Breakdown with a lone kick                                     | drums only                         | beat comes back early                  | total silence, about −63 dB                                                            | Partial (silent, no kick)                 |
| Outro silent, then the beat comes back                         | yes                                | n/a                                    | the beat plays under the whisper slot (drums −9 dB); the planned beat return is silent | Fail (reversed)                           |
| Spoken dialogue in the silences                                | performed                          | partly, with role swaps                | intro, stop 1, stop 2, breakdown and outro all absent                                  | Fail                                      |
| ALIX only speaks, low voice                                    | 98–143 Hz                          | voice swaps                            | bridge median 105 Hz; "Forty customers…" and "Is this an ad?" are performed            | Pass where present                        |
| Loudness and dynamic range                                     | −16.5 LUFS, LRA 8.4                | −12.2 LUFS, LRA 5.6                    | −12.6 LUFS, LRA 5.8                                                                    | Fail                                      |

## Missing or broken lyrics (from the transcript)

- **Never performed:**
  - all eight intro lines;
  - verse 1, an instrumental groove from 19 to 34 s;
  - "Where's the real computer? / Your pocket. Happy to see me?";
  - the four stop-time lines;
  - "One tiny fix. Reflash the whole fleet.";
  - the breakdown dialogue;
  - the outro whispers.
- **Truncated:** the boot log stops after "Users: checked." ("Drivers… Your move." is missing).
- **Chorus 2:** opens without its "Out of the loop! ×2" lines.

The API's `words_timestamps` list every planned line, including the ones never performed: they are an alignment of the plan, not a transcript.

## What this means

- **The silences are usable slots.** With `music_v2_5`, a chunk styled as "total silence, spoken dialogue" comes back as clean, on-grid silence without the voice. The intro (0–12 s), stop 2 and the breakdown are therefore exact slots for the TTS dialogue and the voice clone in the edit. This confirms the hybrid method: dialogue is placed in the edit, not generated by the music model.
- **Repairs rather than a full regeneration.**
  - The song was stored for inpainting (`song_id` in provenance.json).
  - `music_v2_5` accepts `AudioRefChunk`s from a stored song, so verse 1, stop 1 and the final chorus bass can be regenerated while the good chunks are kept.
  - Alternatively, the edit can use the Demucs stems: mute the bass in the final chorus, duck the drums under stop 1.
- **What to try next.**
  - Write the pre-chorus stop as an instrumental or silent chunk, without lines.
  - For the dialogue chunks, keep the "total silence" style but drop the lines and supply them in the edit.
