"""Align a Scribe word transcript to SONG.md and emit a measured cue sheet.

Seconds drive playback. Grid stamps round to the nearest sixteenth at the
supplied BPM. Lines without transcript evidence carry no timing, and sections
span only the available lyric times.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import cache, lru_cache
import json
import math
from pathlib import Path
import re
import unicodedata

METER = 4
SUBDIVISIONS = ("", "e", "&", "a")
MAX_PAUSE = 1.75  # Seconds of silence allowed between transcript words in one line.
MIN_CONFIDENCE = 0.45
LOW_CONFIDENCE = 0.85
SECTION = re.compile(r"\*\*\[([^\]]+)\]\*\*")
LYRIC = re.compile(r"(ALIX|XILA|BOTH):\s*(.+)")
WORD = re.compile(r"[^\W_]+(?:['’.-][^\W_]+)*")
SMALL_NUMBERS = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
).split()
TENS = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()


@dataclass(frozen=True)
class LyricWord:
    text: str
    optional: bool


@dataclass(frozen=True)
class LyricLine:
    speaker: str
    text: str
    words: tuple[LyricWord, ...]


@dataclass(frozen=True)
class TranscriptWord:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class Match:
    lyric: int
    lyric_count: int
    transcript: int
    transcript_count: int
    similarity: float

    @property
    def stop(self):
        return self.transcript + self.transcript_count


@dataclass(frozen=True)
class Candidate:
    score: float
    confidence: float
    matches: tuple[Match, ...]


def parse_lyrics(markdown):
    source = [line.strip() for line in markdown.splitlines()]
    if "## Lyrics" in source:
        source = source[source.index("## Lyrics") + 1:]
    sections = []
    for line in source:
        if sections and line.startswith(("## ", "# ")):
            break
        heading = SECTION.fullmatch(line)
        lyric = LYRIC.fullmatch(line)
        if heading:
            sections.append((heading[1], []))
        elif lyric:
            words = tuple(
                LyricWord(word.group(), part.startswith("("))
                for part in re.findall(r"\([^)]*\)|[^()]+", lyric[2])
                for word in WORD.finditer(part)
            )
            if not sections or not words:
                raise ValueError(f"Lyric requires a section and words: {line}")
            sections[-1][1].append(LyricLine(lyric[1], lyric[2], words))
    if not sections or any(not lines for _, lines in sections):
        raise ValueError("Expected non-empty **[Section]** lyric blocks")
    return sections


def parse_transcript(data, duration):
    entries = data["words"] if isinstance(data, dict) else data
    words = []
    for entry in entries:
        if entry.get("type", "word") != "word" or not WORD.search(entry["text"]):
            continue
        word = TranscriptWord(entry["text"], entry["start"], entry["end"])
        if (not 0 <= word.start <= word.end <= duration
                or words and (word.start < words[-1].start or word.end < words[-1].end)):
            raise ValueError(f"Invalid or unordered Scribe timing: {entry}")
        words.append(word)
    return words


def number_name(value):
    if value < 20:
        return SMALL_NUMBERS[value]
    if value < 100:
        tens, ones = divmod(value, 10)
        return TENS[tens] + (SMALL_NUMBERS[ones] if ones else "")
    hundreds, remainder = divmod(value, 100)
    return SMALL_NUMBERS[hundreds] + "hundred" + (number_name(remainder) if remainder else "")


@cache
def spellings(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = " ".join(WORD.findall(text))
    if re.fullmatch(r"[0-9]{1,3}", text):
        value = int(text)
        names = {number_name(value)}
        if value >= 100 and value % 100:
            # Both "two hundred fifty-six" and the sung "two fifty-six".
            names.add(SMALL_NUMBERS[value // 100] + number_name(value % 100))
        return frozenset(names)
    compact = "".join(character for character in text if character.isalnum())
    if re.fullmatch(r"\w{2,}\.\w{2,}", text):
        return frozenset({compact, text.replace(".", "dot")})
    return frozenset({compact})


@lru_cache(maxsize=65_536)
def similarity(left, right):
    """Levenshtein similarity scaled to the longer spelling."""
    if left == right:
        return 1.0
    length = max(len(left), len(right))
    if min(len(left), len(right)) < 3 or abs(len(left) - len(right)) > length * 0.4:
        return 0.0
    previous = list(range(len(right) + 1))
    for row, a in enumerate(left, 1):
        current = [row]
        for column, b in enumerate(right, 1):
            current.append(min(
                current[-1] + 1, previous[column] + 1,
                previous[column - 1] + (a != b),
            ))
        previous = current
    return 1 - previous[-1] / length


def groups(words):
    """Precompute compact spellings for one word and split/merged compounds."""
    result = []
    for index in range(len(words)):
        variants = {""}
        row = []
        for word in words[index:index + 4]:
            variants = {prefix + suffix for prefix in variants for suffix in spellings(word.text)}
            row.append(variants)
        result.append(row)
    return result


def match_options(lyric, transcript):
    """Allow one-to-many in either direction for split/merged Scribe words."""
    options = {}
    for i, lyric_groups in enumerate(lyric):
        for j, transcript_groups in enumerate(transcript):
            matches = []
            for a, b in ((1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 1)):
                if a > len(lyric_groups) or b > len(transcript_groups):
                    continue
                quality = max(similarity(left, right)
                              for left in lyric_groups[a - 1]
                              for right in transcript_groups[b - 1])
                threshold = 0.60 if a == b else 0.80
                if quality >= threshold:
                    matches.append(Match(i, a, j, b, quality))
            if matches:
                options[i, j] = matches
    return options


def line_candidates(line, transcript_groups, phrase_end):
    """Find plausible local edit alignments, each anchored at both ends."""
    size = len(line.words)
    required = [not word.optional for word in line.words]
    if not any(required):
        required = [True] * size
    required_count = sum(required)
    options = match_options(groups(line.words), transcript_groups)
    for start in sorted({j for _, j in options}):
        stop = min(phrase_end[start], start + size * 2 + 3)
        states = {}
        best = {}

        def extend(score, evidence, matches, match):
            lyric_end = match.lyric + match.lyric_count
            count = sum(required[match.lyric:lyric_end])
            evidence += count * match.similarity
            # Missing mandatory words forgo their reward. Optional words carry
            # a small reward so shouts can attach without stealing core lyrics.
            score += count * (match.similarity + 0.6)
            score += (match.lyric_count - count) * match.similarity * 0.35
            score -= 0.08 * (match.lyric_count + match.transcript_count - 2)
            matches += (match,)
            save(lyric_end, match.stop, (score, evidence, matches))
            confidence = evidence / required_count
            if confidence < MIN_CONFIDENCE or score < 1.0:
                return
            candidate = Candidate(score, confidence, matches)
            if match.stop not in best or score > best[match.stop].score:
                best[match.stop] = candidate

        def save(i, j, state):
            if (i, j) not in states or state[0] > states[i, j][0]:
                states[i, j] = state

        for i in range(size):
            for j in range(start, stop):
                state = states.get((i, j))
                if state:
                    score, evidence, matches = state
                    save(i + 1, j, state)  # Lyric word absent from transcript.
                    save(i, j + 1, (score - 0.45, evidence, matches))  # Extra Scribe word.
                elif j != start:
                    continue
                else:
                    score, evidence, matches = 0.0, 0.0, ()
                for match in options.get((i, j), ()):
                    if match.stop <= stop:
                        extend(score, evidence, matches, match)
        yield from best.values()


def align(lines, transcript):
    """Select the best non-overlapping path through line candidates and skips."""
    size = len(transcript)
    transcript_groups = groups(transcript)
    phrase_end = [size] * size
    for j in range(size - 2, -1, -1):
        phrase_end[j] = (j + 1 if transcript[j + 1].start - transcript[j].end > MAX_PAUSE
                         else phrase_end[j + 1])

    # A state represents words consumed. Prefix maxima allow any number of
    # unused transcript words between lines. A skipped line keeps that state.
    scores = [0.0] + [-math.inf] * size
    history = []
    for line in lines:
        prefix = []
        best = 0
        for j, score in enumerate(scores):
            if score > scores[best] + 1e-9:
                best = j
            prefix.append(best)
        next_scores = scores.copy()
        trace = {}
        for candidate in line_candidates(line, transcript_groups, phrase_end):
            start = prefix[candidate.matches[0].transcript]
            end = candidate.matches[-1].stop
            score = scores[start] + candidate.score
            if score > next_scores[end] + 1e-9:
                next_scores[end] = score
                trace[end] = (start, candidate)
        history.append(trace)
        scores = next_scores

    cursor = max(range(size + 1), key=lambda j: round(scores[j], 9))
    result = []
    for trace in reversed(history):
        cursor, candidate = trace.get(cursor, (cursor, None))
        result.append(candidate)
    return list(reversed(result))


def position(seconds, bpm):
    """Nearest sixteenth-note position in the existing bar.beat notation."""
    subdivisions = math.floor(seconds * bpm / 60 * len(SUBDIVISIONS) + 0.5)
    beats, suffix = divmod(subdivisions, len(SUBDIVISIONS))
    bar, beat = divmod(beats, METER)
    return f"{bar + 1}.{beat + 1}{SUBDIVISIONS[suffix]}"


def span(start, end, bpm):
    return {"start": start, "end": end, "at": position(start, bpm), "endAt": position(end, bpm)}


def divide_span(start, end, count):
    edges = [round(start + (end - start) * i / count, 9) for i in range(count + 1)]
    edges[0], edges[-1] = start, end
    return zip(edges, edges[1:])


def time_words(line, transcript, candidate, bpm):
    timings = [None] * len(line.words)
    for match in candidate.matches:
        start = transcript[match.transcript].start
        end = transcript[match.stop - 1].end
        for i, (a, b) in enumerate(divide_span(start, end, match.lyric_count), match.lyric):
            timings[i] = (a, b, match.lyric_count > 1)

    first = next(timing[0] for timing in timings if timing)
    previous = first
    i = 0
    while i < len(timings):
        if timings[i]:
            previous = timings[i][1]
            i += 1
            continue
        j = i + 1
        while j < len(timings) and timings[j] is None:
            j += 1
        # When there is no measured interval (e.g. an unsung closing
        # shout), use a point cue at the nearest edge of the measured line.
        end = timings[j][0] if j < len(timings) else previous
        for index, (a, b) in enumerate(divide_span(min(previous, end), end, j - i), i):
            timings[index] = (a, b, True)
        i = j

    words = []
    for word, (start, end, interpolated) in zip(line.words, timings, strict=True):
        cue = {"text": word.text, **span(start, end, bpm)}
        if word.optional:
            cue["optional"] = True
        if interpolated:
            cue["interpolated"] = True
        words.append(cue)
    return words


def make_cues(sections, transcript, bpm, duration):
    candidates = iter(align([line for _, lines in sections for line in lines], transcript))
    ids = Counter()
    cues = {
        "timing": "measured",
        "bpm": bpm,
        "beatsPerBar": METER,
        "bars": duration * bpm / (METER * 60),
        "duration": duration,
        "sections": [],
        "lines": [],
        "events": [],
    }
    for name, lines in sections:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "section"
        ids[slug] += 1
        section_id = f"section-{len(cues['sections']) + 1}-{slug}"
        label = f"{name} ({ids[slug]})" if ids[slug] > 1 else name
        section = {"id": section_id, "name": label}
        matched = []
        for index, line in enumerate(lines, 1):
            candidate = next(candidates)
            cue = {
                "id": f"{section_id}-{index:02}",
                "sectionId": section_id,
                "speaker": line.speaker,
                "delivery": "spoken" if slug in {"stop-time", "breakdown", "outro"} else "sung",
                "text": line.text,
                "words": [],
            }
            if candidate is None:
                cue["missing"] = True
            else:
                words = time_words(line, transcript, candidate, bpm)
                cue.update(span(words[0]["start"], words[-1]["end"], bpm))
                cue.update(words=words, confidence=round(candidate.confidence, 4))
                if cue["confidence"] < LOW_CONFIDENCE:
                    cue["low_confidence"] = True
                matched.append(cue)
            cues["lines"].append(cue)
        if matched:
            start, end = matched[0]["start"], matched[-1]["end"]
            section.update(span(start, end, bpm))
            section.update(startBar=1 + start * bpm / (METER * 60), bars=(end - start) * bpm / (METER * 60))
        else:
            section["missing"] = True
        cues["sections"].append(section)
    return cues


def alignment_report(cues):
    report = [
        f"Lyric alignment at {cues['bpm']} BPM | {cues['duration']:.3f} s",
        "Coverage estimates from the transcript.",
        "",
    ]
    for section in cues["sections"]:
        lines = [line for line in cues["lines"] if line["sectionId"] == section["id"]]
        missing = sum(line.get("missing", False) for line in lines)
        weak = sum(line.get("low_confidence", False) for line in lines)
        report.append(f"{section['name']}: {len(lines) - missing}/{len(lines)} matched, {weak} low-confidence")
    total = len(cues["lines"])
    missing = [line for line in cues["lines"] if line.get("missing")]
    weak = [line for line in cues["lines"] if line.get("low_confidence")]
    report += [f"Total: {total - len(missing)}/{total} matched, {len(weak)} low-confidence", "", "Missing lines"]
    report += [f"  {line['id']} {line['speaker']}: {line['text']}" for line in missing] or ["  None"]
    report += ["", "Low-confidence lines"]
    report += [
        f"  {line['start']:.3f}–{line['end']:.3f} s ({line['confidence']:.0%}) "
        f"{line['id']} {line['speaker']}: {line['text']}"
        for line in weak
    ] or ["  None"]
    return "\n".join(report) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lyrics", type=Path, required=True)
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--bpm", type=int, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.bpm <= 0 or not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("BPM and duration must be positive and finite")
    try:
        sections = parse_lyrics(args.lyrics.read_text(encoding="utf-8"))
        transcript = parse_transcript(json.loads(args.words.read_text(encoding="utf-8")), args.duration)
        cues = make_cues(sections, transcript, args.bpm, args.duration)
        args.out.write_text(json.dumps(cues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.error(str(error))
    print(alignment_report(cues), end="")


if __name__ == "__main__":
    main()
