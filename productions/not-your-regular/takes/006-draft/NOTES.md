# Take 006 (draft): changes from take 005

These are draft inputs for ElevenLabs Music v2.5 (`prompt.txt`, `lyrics.txt`). Nothing has been generated and no credits have been spent. The same song is formatted for Suno in [SUNO.md](../../SUNO.md).

Each change below cites a measurement. The measurements come from Demucs stems and the timings in Aditazzz's repo. Data and tools are in `output/not-your-regular/reference/`.

## Changes and the measurements behind them

1. **Verses are chanted on one note with hard auto-tune.**
   - LWICD verse 2 sits entirely on one note (D4), and verse 1 spans about 5 semitones. Pitch error is 3.5–9 cents with almost no wobble, which means hard-tuned.
   - Data Center Fornicator's lead is also a hard-tuned monotone (F2).
   - Take 005's verses measure 20–29 cents of error with 17–30 cents of wobble. That is statistically untuned speech, which is why they read as talk-rap.
   - The melody now opens up only on the hook.
2. **The groove is simpler.**
   - LWICD has a four-on-the-floor kick, straight 8th hats (about 6–7 hits per bar) and almost no bass onsets.
   - Take 005 has 16th hats (10–12 per bar) and a rolling 16th bass (5–9 onsets per bar).
   - Its drive should come from the vocal density and the contrast between sections, not from a busy rhythm section.
3. **The bass is withheld.**
   - In LWICD the bass is absent in verse 1 (until its last 2 bars), verse 2, the bridge, the final chorus and the breakdown.
   - Its first full-weight entry (−4 dB) starts the drop, which is the loudest section.
   - In take 005 the bass plays almost everywhere, and verse 1 is as loud as the chorus.
4. **Total stops before choruses.**
   - LWICD stops dead for about 2 bars before chorus 1 ("Too late!") and chorus 2 ("Everything."), with drums near −67 dB.
   - The pre-chorus here ends in a 2-bar silence for "Where's the real computer?" and "Your pocket. Happy to see me?". The stop-time keeps its silence before chorus 2.
5. **The arrangement map now copies LWICD's contrasts, not its content.** In order:
   - the intro opens with no music at all, then a pad, then the beat;
   - the bridge has no drums or bass;
   - the breakdown keeps only one soft kick (ours is a heartbeat: the app crashes, the system keeps beating);
   - the final chorus has no bass;
   - the drop is the loudest part;
   - the outro is silent, then the beat returns for 2 bars.
6. **The hook is doubled.** LWICD repeats its hook twice back to back, one bar each, which fills 4 of 8 chorus lines. "Out of the loop!" now does the same. The "(O-S!)" echo moves to the chopped vocal motif.
7. **Verse lines are about 8 syllables, one bar each.** LWICD verse lines measure 7–10 syllables over about 1.85 s each. Several lines were tightened:
   - "poke registers";
   - "two-fifty-six K";
   - "Doorbell?" and "Toaster?" lose their "Your";
   - "Walked it. Twice." replaces ALIX's sung aside.
8. **ALIX only speaks in silences.** In LWICD the male voice (98–143 Hz, about G2–D3) has about 12 lines, all of them dialogue in gaps, and never sings. The draft gives ALIX:
   - no sung or chanted line;
   - no line over the beat except the breakdown, which has only a lone kick.

   This also keeps every ALIX line replaceable by the maintainer's voice clone in the edit.

9. **A different key and loop.**
   - The draft is in A minor, with chords changing every two beats and a major V for the lift.
   - LWICD measures G minor with Gm–Eb–Bb–D every two beats; that exact loop is not reused.
   - ElevenLabs ignored the requested key in take 005 (we asked for C minor and got F minor), so the key is a hint, not a guarantee.
10. **A dynamic mix.** LWICD measures −16.5 LUFS with an 8.4 LU loudness range. Take 005 measures −12.2 LUFS and 5.6 LU. The prompt asks for big contrast between the quiet verses and the loud hooks.

## Content cuts to stay near 3 minutes

- **Intro:** 8 lines instead of 10. "That's a microcontroller. / A microcontroller with an OS." is merged into "The chip in your hand. I have an OS."
- **Pre-chorus:** "(I ordered a real computer.)" is cut so the stop fits in 2 bars.
- **Verse 3:** halved to 4 lines (the "blob" and "lose in your meal" couplets are cut). It keeps the scepticism and the Rust library claim.
- **Boot log:** 4 bars. ALIX's "Build you in? So what's inside?" is cut because it would sit over the beat.
- **Bridge:** ALIX's three lines from v3, including "Is this an ad?", are back, now in the drumless gaps.

Claim honesty is unchanged from LYRICS-v3.md. "Plural!", "No watchdog reset?" and "Update the app! That's the plan!" remain roadmap lines, the gadget apps remain imagined, and "two-fifty-six K" is the Nano 33 BLE's 256 KiB of RAM.

## Estimated length

Count at 130 BPM, where one bar is 1.846 s:

| Section             |                    Bars |
| ------------------- | ----------------------: |
| Intro               |                       7 |
| Hook                |                       4 |
| Verse 1             |                       8 |
| Pre-chorus and stop |                       4 |
| Chorus              |                       8 |
| Post-chorus         |                       4 |
| Verse 2             |                       8 |
| Stop-time           |                       3 |
| Chorus 2            |                       8 |
| Verse 3             |                       4 |
| Boot log            |                       4 |
| Bridge              |                       8 |
| Breakdown           |                       3 |
| Final chorus        |                       8 |
| Drop                |                       4 |
| Outro               |                       4 |
| Beat return         |                       2 |
| **Total**           | **97 bars, about 2:59** |

Request `duration_seconds: 180`.
