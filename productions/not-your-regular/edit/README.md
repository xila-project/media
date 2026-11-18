# Out of the Loop: audio edit

`build_edit.py` assembles the review edit from take 005 and two TTS dialogue takes. It runs inside `output/not-your-regular/edit-001/` and expects these inputs there, all ignored by Git:

- `t5.wav`: `assets/audio/not-your-regular/take-005-source.mp3` decoded to 48 kHz stereo.
- `alix.wav`: ALIX's dialogue lines, from ElevenLabs TTS `eleven_v4` with the library voice "Stray - Deep and Grounded" (`DT7zBOa8kCzTWHNN60AC`), generation `Kqgj4jUwpUeWqv7GigWR`. This is a stand-in until the maintainer's voice clone exists.
- `xila.wav`: XILA's dialogue lines, from ElevenLabs TTS `eleven_v4` with the library voice "Therese" (`yX1d4od5qd09pvOQx88H`), generation `DVk4b05BpQrayIJJEMVf`.

Line boundaries were measured with FFmpeg `silencedetect`. Bar times assume 130 BPM from the start of take 005 (see `takes/005/transcript-words.json`).

| Edit     | Changes                                                                                                                                                                                                                                  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| edit-001 | First assembly: TTS intro, stop-time and outro; chorus 2 replaced by chorus 1.                                                                                                                                                           |
| edit-002 | Gemini QA fixes: tighter dialogue gaps, a C-minor pad and a riser into the beat, the stop-time cut from 7 to 6 bars with the tail left to decay, longer crossfades, room and air on the TTS voices, quieter whispers over the song tail. |
