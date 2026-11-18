"""Render the Everything Is a File animatic guide from a house cue sheet."""

import argparse
from array import array
from contextlib import ExitStack
from dataclasses import dataclass
import json
from math import cos, exp, isfinite, pi, sin, sqrt, sumprod, tau
from pathlib import Path
from random import Random
import re
import sys
from tempfile import TemporaryDirectory
import wave

from audio import measure

RATE = 48000
PRODUCTION = "house-everything-is-a-file"
DEFAULT_CUES = Path("productions") / PRODUCTION / "cues.json"
DEFAULT_OUTPUT = Path("output") / PRODUCTION
SUBDIVISION = {"": 0, "e": 0.25, "&": 0.5, "a": 0.75}
# A minor 9, C major 7, D dominant 9, E minor 7, voiced above the bass.
CHORDS = (
    (33, (57, 60, 64, 67, 71)),
    (36, (55, 59, 60, 64)),
    (38, (57, 60, 64, 66)),
    (40, (55, 59, 62, 64)),
)
VOWELS = {
    "a": (730, 1190, 2500),
    "e": (510, 1850, 2550),
    "i": (330, 2220, 3000),
    "o": (470, 930, 2550),
    "u": (350, 810, 2400),
}
WAVE_SIZE = 2048


@dataclass(frozen=True)
class Grid:
    bpm: float
    beats: int
    frames: int

    @classmethod
    def from_cues(cls, cues):
        if cues["beatsPerBar"] != 4:
            raise ValueError("The house arrangement requires four beats per bar")
        if not isfinite(cues["bpm"]) or cues["bpm"] <= 0:
            raise ValueError("Tempo must be positive and finite")
        frames = round(cues["duration"] * RATE)
        if frames <= 0 or cues["bars"] <= 0:
            raise ValueError("Cue sheet must have a positive duration and bar count")
        return cls(cues["bpm"], cues["bars"] * 4, frames)

    @property
    def beat_seconds(self):
        return 60 / self.bpm

    def frame(self, beat):
        return round(beat * 60 * RATE / self.bpm)

    def beat_at(self, position):
        match = re.fullmatch(r"([1-9]\d*)\.([1-4])([e&a]?)", position)
        if match is None:
            raise ValueError(f"Invalid cue position {position!r}")
        bar, beat, suffix = match.groups()
        offset = (int(bar) - 1) * 4 + int(beat) - 1 + SUBDIVISION[suffix]
        if offset >= self.beats:
            raise ValueError(f"Cue position {position!r} is past the last bar")
        return offset


def zeros(length):
    return array("f", [0]) * length


def frequency(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def release(t, duration, attack=0.004, tail=0.012):
    return min(1, t / attack, (duration - t) / tail)


def lowpass(hz):
    return 1 - exp(-tau * hz / RATE)


def drums():
    rng = Random(124)
    kick, hat, clap, rim, ride = (array("f") for _ in range(5))
    for n in range(round(0.30 * RATE)):
        t = n / RATE
        # Integral of a 52 Hz body plus a fast, exponentially dropping pitch.
        phase = tau * (52 * t + 2.4 * (1 - exp(-t / 0.018)))
        click = sin(tau * 1850 * t) * exp(-t / 0.0022)
        envelope = release(t, 0.30, attack=0.001)
        kick.append(envelope * (0.64 * sin(phase) * exp(-t / 0.065) + 0.10 * click))

    previous = 0
    for n in range(round(0.24 * RATE)):
        t = n / RATE
        noise = rng.uniform(-1, 1)
        bright = (noise - previous) * 0.5
        previous = noise
        if t < 0.072:
            hat.append(0.158 * bright * exp(-t / 0.018) * release(t, 0.072, 0.001))
        if t < 0.14:
            # Three short bursts into a single tail give the clap its attack.
            burst = sum(exp(-(t - hit) / 0.009) for hit in (0, 0.008, 0.016) if hit <= t)
            clap.append(0.19 * bright * burst * release(t, 0.14, 0.001))
        if t < 0.08:
            ring = sin(tau * 825 * t) + 0.55 * sin(tau * 1430 * t)
            rim.append((0.135 * ring + 0.17 * bright) * exp(-t / 0.012) * release(t, 0.08, 0.001))
        metal = sin(tau * 4829 * t) * sin(tau * 1361 * t)
        ride.append(0.07 * (bright + metal) * exp(-t / 0.075) * release(t, 0.24, 0.001))
    return kick, hat, clap, rim, ride


def saw_table():
    # Band-limited carrier shared by the detuned chord and guide vocoder.
    return [
        -2 / pi * sum(sin(tau * i * h / WAVE_SIZE) / h for h in range(1, 25))
        for i in range(WAVE_SIZE)
    ]


def chord_clips(notes, beat_seconds, saw, alternate):
    length = round(beat_seconds * RATE) + 1
    left, right = zeros(length), zeros(length)
    stabs = ((0.18, 0.66, 0.21), (0.77, 0.21, 0.115))
    if alternate:
        stabs = ((0.49, 0.42, 0.235),)
    for start, span, level in stabs:
        offset = round(start * beat_seconds * RATE)
        duration = span * beat_seconds
        size = min(length - offset, round(duration * RATE))
        for voice, note in enumerate(notes):
            # Spread the same voicing using opposing detunes and phase offsets.
            step = frequency(note) * WAVE_SIZE / RATE
            phase = WAVE_SIZE * (voice + 1) / (len(notes) + 1)
            drift = 2 ** ((4 if voice % 2 else -6) / 1200)
            for n in range(size):
                t = n / RATE
                envelope = level * release(t, duration, 0.007, 0.035) * exp(-t / 0.18)
                dry = 0.40 * saw[int(phase + n * step) % WAVE_SIZE]
                left[offset + n] += envelope * (dry + 0.60 * saw[int(n * step * drift) % WAVE_SIZE])
                right[offset + n] += envelope * (dry + 0.60 * saw[int(n * step / drift) % WAVE_SIZE])
    return left, right


def bass_clip(root, beat_seconds, alternate):
    bass = zeros(round(beat_seconds * RATE) + 1)
    # A short root on the kick and an octave response on the swung offbeat.
    for start, span, octave, level in ((0, 0.40, 0, 0.28), (0.58, 0.33, 12, 0.24)):
        offset = round(start * beat_seconds * RATE)
        duration = span * beat_seconds
        note = root + octave - (12 if alternate and octave else 0)
        angular = tau * frequency(note)
        for n in range(min(len(bass) - offset, round(duration * RATE))):
            t = n / RATE
            phase = angular * t
            body = sin(phase) + 0.30 * sin(2 * phase) + 0.12 * sin(3 * phase)
            duck = 1 - 0.86 * exp(-(t + start * beat_seconds) / 0.10)
            bass[offset + n] = level * body * duck * release(t, duration, 0.006)
    return bass


def riser(frames):
    rng = Random(48)
    samples = array("f")
    filtered = phase = 0
    for n in range(frames):
        position = n / frames
        noise = rng.uniform(-1, 1)
        filtered += (0.035 + position * 0.38) * (noise - filtered)
        phase += tau * (135 + position ** 3 * 380) / RATE
        envelope = position ** 2 * min(1, (1 - position) * 75)
        samples.append(envelope * (0.32 * (noise - filtered) + 0.055 * sin(phase)))
    return samples


def chord_cutoff(bar, beat):
    if bar <= 4:
        return 235 + 35 * bar
    if (bar, beat) in {(12, 3), (13, 0)}:
        return 190
    if bar < 17:
        return 820
    if bar < 24:
        return 880 + 95 * (bar - 17)
    if bar == 24:
        return (1600, 2100, 2900, 4200)[beat]
    if bar <= 32:
        return 5200
    if bar <= 40:
        return 2500
    if bar <= 48:
        return 430
    return 7100 if bar < 54 else 9700


def overlay(destination, source, offset=0, gain=1):
    for n in range(min(len(destination) - offset, len(source))):
        destination[offset + n] += gain * source[n]


def fade_before_mute(samples, start):
    # De-click just before the edit. Keep the mute itself an exact hard zero.
    width = min(round(0.003 * RATE), start)
    for n in range(width):
        samples[start - width + n] *= (width - n - 1) / width


def render_music(grid, mutes, saw):
    left, right = zeros(grid.frames), zeros(grid.frames)
    kick, hat, clap, rim, ride = drums()
    seconds = grid.beat_seconds
    chords = [tuple(chord_clips(notes, seconds, saw, alt) for alt in (False, True)) for _, notes in CHORDS]
    basses = [tuple(bass_clip(root, seconds, alt) for alt in (False, True)) for root, _ in CHORDS]
    pump = [1 - 0.83 * exp(-n / (RATE * 0.13)) for n in range(round(seconds * RATE) + 1)]
    swell = riser(grid.frame(4))
    chord_l1 = chord_l2 = chord_r1 = chord_r2 = drum_l = drum_r = 0
    hat_offset = round(0.58 * seconds * RATE)
    for index in range(grid.beats):
        start = grid.frame(index)
        stop = min(grid.frame(index + 1), grid.frames)
        if start >= stop:
            break
        bar, beat = divmod(index, 4)
        chord_index = bar % len(CHORDS)
        bar += 1
        is_break = 41 <= bar <= 48
        has_kick = not is_break and (bar, beat) != (13, 0)
        cutoff = lowpass(chord_cutoff(bar, beat))
        cutoff_step = 0
        if bar == 24:
            next_hz = chord_cutoff(24, beat + 1) if beat < 3 else chord_cutoff(25, 0)
            cutoff_step = (lowpass(next_hz) - cutoff) / (stop - start)
        size = stop - start
        drum = zeros(size)
        if has_kick:
            overlay(drum, kick)
        if is_break or (bar, beat) == (14, 3):
            overlay(drum, rim, gain=0.72 if is_break else 1)
        if 25 <= bar <= 72 and not is_break and beat in (1, 3):
            overlay(drum, clap)
        cymbal = zeros(size)
        if not is_break:
            overlay(cymbal, hat, hat_offset, gain=0.8 if beat % 2 == 0 else 1)
        if bar == 48:
            overlay(cymbal, hat, gain=0.35 + 0.18 * beat)
        if 62 <= bar <= 64:
            overlay(cymbal, ride, hat_offset)
        chord_l, chord_r = chords[chord_index][beat % 2]
        bass = basses[chord_index][beat == 3] if 9 <= bar <= 72 and not is_break else None
        chord_level = 0.44 if is_break else 1.15 if bar >= 49 else 0.95
        intro_filter = lowpass(340 + 25 * bar) if bar <= 4 else 1
        swell_start = start - grid.frame(47 * 4) if bar == 48 else 0
        for n in range(size):
            chord_l1 += cutoff * (chord_l[n] - chord_l1)
            chord_l2 += cutoff * (chord_l1 - chord_l2)
            chord_r1 += cutoff * (chord_r[n] - chord_r1)
            chord_r2 += cutoff * (chord_r1 - chord_r2)
            cutoff += cutoff_step
            drum_l += intro_filter * (drum[n] + cymbal[n] * 0.75 - drum_l)
            drum_r += intro_filter * (drum[n] + cymbal[n] - drum_r)
            chord_gain = chord_level * (pump[n] if has_kick else 1) if bar <= 72 else 0
            center = bass[n] if bass is not None else 0
            if bar == 48:
                center += swell[min(swell_start + n, len(swell) - 1)]
            left[start + n] = drum_l + chord_l2 * chord_gain + center
            right[start + n] = drum_r + chord_r2 * chord_gain + center

    for mute_start, mute_end in mutes:
        start = min(grid.frames, grid.frame(mute_start))
        stop = min(grid.frames, grid.frame(mute_end))
        if stop > start:
            for channel in (left, right):
                fade_before_mute(channel, start)
                channel[start:stop] = zeros(stop - start)
    return left, right


def bandpass(hz, q):
    # Constant 0 dB peak band-pass biquad, in transposed direct form II.
    angle = tau * hz / RATE
    alpha = sin(angle) / (2 * q)
    divisor = 1 + alpha
    return alpha / divisor, -2 * cos(angle) / divisor, (1 - alpha) / divisor


def syllable(text, pitch, spoken, length, saw, rng):
    vowels = re.findall(r"[aeiou]", text.lower()) or ["e"]
    formants = VOWELS[vowels[0]]
    filters = [bandpass(hz, q) for hz, q in zip(formants, (3, 5, 7))]
    states = [[0, 0] for _ in filters]
    duration = length / RATE
    last_sample = (length - 1) / RATE
    onset = min(0.025, duration * 0.28)
    edge = rng.uniform(-1, 1)
    base_pitch = 119 + edge * 12 if spoken else frequency(57 + pitch)
    phase = 0
    output = array("f")
    for n in range(length):
        t = n / RATE
        progress = n / length
        phase += base_pitch * (1.09 - 0.28 * progress if spoken else 1) * WAVE_SIZE / RATE
        buzz = saw[int(phase) % WAVE_SIZE]
        noise = rng.uniform(-1, 1)
        consonant = max(0, 1 - t / onset)
        if spoken:
            carrier = 0.63 * buzz + (0.22 + 0.47 * consonant) * noise
            shape = 0.98 - 0.42 * progress + 0.11 * sin(tau * (len(vowels) * 0.5) * progress)
        else:
            carrier = 0.90 * buzz + 0.27 * consonant * noise
            shape = 0.90 + 0.10 * sin(tau * 4.6 * t)
        voice = carrier * 0.18
        for (b0, a1, a2), state, weight in zip(filters, states, (1.0, 0.86, 0.50)):
            filtered = b0 * carrier + state[0]
            state[0] = state[1] - a1 * filtered
            state[1] = -b0 * carrier - a2 * filtered
            voice += weight * filtered
        output.append(voice * shape * release(t, last_sample, 0.007, 0.023))
    return output


def render_vocals(grid, lines, mutes, syllable_beats, saw):
    vocals = zeros(grid.frames)
    rng = Random(220)
    words = sorted(
        ((grid.beat_at(word["at"]), line, word) for line in lines for word in line["words"]),
        key=lambda item: item[0],
    )
    power = active_frames = 0
    for index, (beat, line, word) in enumerate(words):
        text = word["text"]
        spoken = line["speaker"] == "ALIX" or line["delivery"] == "spoken"
        next_beat, next_line, _ = words[index + 1] if index + 1 < len(words) else (grid.beats, None, None)
        if spoken:
            span = min(0.32, 0.085 + 0.019 * len(text)) / grid.beat_seconds
        elif next_line is line:
            span = next_beat - beat
        elif line["text"].lower().rstrip(".!?") == "everything is a file":
            span = 2  # The hook's last note carries across beats 3 and 4.
        else:
            span = 1 if "pitch" in word else 0.52

        end = min(beat + span, next_beat)
        for mute_start, mute_end in mutes:
            if mute_start <= beat < mute_end:
                end = min(end, mute_end)

        pulses = [(beat, end, text)]
        if beat in syllable_beats:
            # The count-in spells one cue word across four eighth-note hits.
            hits = sorted(mark for mark in syllable_beats if beat <= mark < next_beat)
            pieces = ("Two", "fif", "ty", "six") if text.lower() == "two-fifty-six" else ()
            pulses = [
                (hit, min(hit + 0.5, next_hit), pieces[n] if n < len(pieces) else text)
                for n, (hit, next_hit) in enumerate(zip(hits, hits[1:] + [next_beat]))
            ]
        for onset, release_at, piece in pulses:
            start = grid.frame(onset)
            stop = min(grid.frames, grid.frame(release_at))
            if stop <= start:
                continue
            samples = syllable(piece, word.get("pitch", 0), spoken, stop - start, saw, rng)
            vocals[start:stop] = samples
            power += sumprod(samples, samples)
            active_frames += len(samples)
    return vocals, sqrt(power / active_frames) if active_frames else 0


def pcm_bytes(samples):
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


def write_waves(paths, left, right, vocals, music_gain, voice_gain):
    with ExitStack() as stack:
        outputs = [stack.enter_context(wave.open(str(path), "wb")) for path in paths]
        for output in outputs:
            output.setparams((2, 2, RATE, len(left), "NONE", "not compressed"))
        for start in range(0, len(left), RATE):
            stop = start + RATE
            mix, music, voice = array("h"), array("h"), array("h")
            for l, r, v in zip(left[start:stop], right[start:stop], vocals[start:stop]):
                l = round(l * music_gain)
                r = round(r * music_gain)
                v = round(v * voice_gain)
                mix.extend((l + v, r + v))
                if len(outputs) > 1:
                    music.extend((l, r))
                    voice.extend((v, v))
            for output, samples in zip(outputs, (mix, music, voice)):
                output.writeframesraw(pcm_bytes(samples))


def render(cues, output):
    grid = Grid.from_cues(cues)
    mutes = []
    syllable_beats = set()
    for event in cues["events"]:
        if event["kind"] == "mute":
            start = grid.beat_at(event["at"])
            mutes.append((start, start + event["beats"]))
        elif event["kind"] == "syllable":
            syllable_beats.add(grid.beat_at(event["at"]))
    saw = saw_table()
    left, right = render_music(grid, mutes, saw)
    vocals, voice_rms = render_vocals(grid, cues["lines"], mutes, syllable_beats, saw)
    music_rms = sqrt((sumprod(left, left) + sumprod(right, right)) / (2 * grid.frames))
    voice_balance = 10 ** (3 / 20) * music_rms / voice_rms if voice_rms else 0
    music_peak = max(max(map(abs, left)), max(map(abs, right)))
    voice_peak = max(map(abs, vocals)) * voice_balance
    if music_peak + voice_peak == 0:
        raise ValueError("Guide mix is silent")

    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".guide-", dir=output) as directory:
        stage = Path(directory)
        reference_gain = min(1, 0.9 / (music_peak + voice_peak)) * 32767
        reference = stage / "reference.wav"
        write_waves((reference,), left, right, vocals, reference_gain, reference_gain * voice_balance)
        levels = measure(reference)
        # The startup helper measures integrated loudness and true peak. Use
        # one linear gain so both stems still sum to the mix, with exact zeros.
        integrated, peak = float(levels["input_i"]), float(levels["input_tp"])
        gain_db = min(-20 - integrated, -2.05 - peak)
        gain = min(reference_gain * 10 ** (gain_db / 20), 32700 / max(music_peak, voice_peak))
        paths = [stage / name for name in ("guide.wav", "guide-music.wav", "guide-vocals.wav")]
        write_waves(paths, left, right, vocals, gain, gain * voice_balance)
        for path in paths:
            path.replace(output / path.name)
    print(f"Rendered {grid.frames} samples per channel at {RATE} Hz to {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cues", type=Path, nargs="?", default=DEFAULT_CUES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        render(json.loads(args.cues.read_text(encoding="utf-8")), args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
