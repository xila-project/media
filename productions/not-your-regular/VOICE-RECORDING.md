# Maintainer voice recording

ALIX, the dry, low, deadpan firmware developer, never sings. He only speaks in the silences (see REFERENCE-ANALYSIS.md and takes/006-draft). His lines are generated with TTS and then converted to the maintainer's voice:

- **Instant Voice Clone** made from this recording, then used for TTS or the Voice Changer (`eleven_multilingual_sts_v2`).
- **Direct use.** Raw reads of the lines may be used directly when they sound better than the clone.

## Setup

- A phone is fine. Hold it 15–20 cm from the mouth, slightly to the side to avoid plosives.
- Record in a quiet, soft room (a wardrobe full of clothes is ideal), with no fan, music or echo.
- Use WAV, or m4a at the highest quality. Do not apply noise reduction or other effects.
- Start with **5 seconds of silence**.
- Keep normal levels: the loudest syllables must not clip.
- Put the files in `assets/audio/not-your-regular/voice/`. The folder is git-ignored and is never committed or uploaded without the maintainer's consent.

## What to record (about 3 min, one or several files)

1. **French, natural (~60 s).** Talk calmly about anything, for example what Xila is. This gives the clone your timbre.
2. **English, natural (~45 s).** Read a paragraph of the Xila README, slowly. The accent is fine.
3. **ALIX lines (~60 s).** Use a low, calm voice without forcing it, close to the mic and late-night intimate: dry, blasé, unimpressed. Read each line **twice**, the second time even flatter, with 2 seconds of silence between lines.
   - Big day. I made the LED blink.
   - Who said that?
   - That's a microcontroller.
   - Chips run a loop. While true.
   - So what are you?
   - Can it run apps? / With files? / So where's the real computer?
   - Wait. A cat flap with apps?
   - And the OS? That small?
   - An OS? On that? Get real.
   - Forty customers. Forty firmware forks.
   - One tiny fix. Reflash the whole fleet.
   - Is this an ad?
   - Trap. / Did we just crash? / No watchdog reset?
4. **Monotone (~20 s).** Say these lines on one held note, like a robot announcer. They may be hard-tuned, as Data Center Fornicator does with its male voice:
   - Out of the loop.
   - Memory: mapped. Tasks: named. Shell: ready.
5. **Whispered (~15 s).** Whisper close to the mic, twice:
   - So... do I flash you?
   - Shh. We're in a library.

## Next steps (Claude)

1. Create the Instant Voice Clone from parts 1–2 with the maintainer's consent. This uses a voice slot, not credits.
2. Generate ALIX's lines with the clone, or convert the stand-in TTS lines with the Voice Changer.
3. A/B them against the raw reads from parts 3–5, and keep whichever sounds best per line.
