import cues from "../../productions/house-everything-is-a-file/cues.json" with { type: "json" };

type Section = Readonly<{
  id: string;
  name: string;
  startBar: number;
  bars: number;
}>;

type WordCue = Readonly<{
  text: string;
  at: string;
  pitch?: number;
  start?: number;
}>;

type LineCue = Readonly<{
  id: string;
  at?: string;
  start?: number;
  missing?: boolean;
  speaker: string;
  delivery: string;
  text: string;
  words: readonly WordCue[];
}>;

type EventCue = Readonly<{
  id: string;
  at: string;
  kind: string;
  beats?: number;
}>;

export const cueSheet: Readonly<{
  bpm: number;
  beatsPerBar: number;
  bars: number;
  duration: number;
  sections: readonly Section[];
  lines: readonly (LineCue & { at: string })[];
  events: readonly EventCue[];
}> = cues;

export type WordTimingOverride = Readonly<{
  lineId: string;
  words: readonly Readonly<{ text: string; start: number; end: number }>[];
}>;

const { bpm, beatsPerBar } = cueSheet;
const secondsPerBeat = 60 / bpm;
const subdivisions: Readonly<Record<string, number>> = {
  "": 0,
  e: 0.25,
  "&": 0.5,
  a: 0.75,
};

// Beat offsets are zero-based. Bar positions are one-based and may be fractional.
export function beatToSeconds(beatOffset: number): number {
  return beatOffset * secondsPerBeat;
}

export function secondsToBeat(time: number): number {
  const beat = time / secondsPerBeat;
  const nearest = Math.round(beat);
  // Correct arithmetic drift at beat boundaries before calculating a phase.
  return Math.abs(beat - nearest) < 1e-10 ? nearest : beat;
}

export function barToSeconds(bar: number): number {
  return beatToSeconds((bar - 1) * beatsPerBar);
}

export function secondsToBar(time: number): number {
  return 1 + secondsToBeat(time) / beatsPerBar;
}

function gridSeconds(
  position: string,
  bpm: number,
  beatsPerBar: number,
): number {
  const match = /^([1-9]\d*)\.([1-9]\d*)([e&a]?)$/.exec(position);
  if (!match || match[0] !== position) {
    throw new RangeError(`Invalid score position: ${position}`);
  }
  const bar = Number(match[1]);
  const beat = Number(match[2]);
  if (!Number.isSafeInteger(bar) || beat > beatsPerBar) {
    throw new RangeError(`Invalid score position: ${position}`);
  }
  return (
    ((bar - 1) * beatsPerBar + beat - 1 + subdivisions[match[3]]) * (60 / bpm)
  );
}

function normalizeWord(text: string): string {
  return text
    .toLowerCase()
    .replace(/’/g, "'")
    .replace(/^\p{P}+|\p{P}+$/gu, "");
}

function findWord<T extends { text: string }>(
  words: readonly T[],
  id: string,
  indexOrText: number | string,
): T {
  const text = typeof indexOrText === "string" && normalizeWord(indexOrText);
  const cue =
    typeof indexOrText === "number"
      ? words[indexOrText]
      : words.find((word) => normalizeWord(word.text) === text);
  if (!cue) throw new RangeError(`Unknown word in ${id}: ${indexOrText}`);
  return cue;
}

type PlaybackSection = Readonly<
  Pick<Section, "id" | "name"> &
    Partial<Pick<Section, "startBar" | "bars">> & {
      start?: number;
      end?: number;
      missing?: boolean;
    }
>;

/** Read cues at their own tempo, preferring absolute seconds when supplied. */
export function createCueLookup<S extends PlaybackSection>(
  sheet: Readonly<
    Pick<typeof cueSheet, "bpm" | "beatsPerBar" | "events"> & {
      sections: readonly S[];
      lines: readonly LineCue[];
    }
  >,
) {
  const { bpm, beatsPerBar } = sheet;
  const lines = new Map(sheet.lines.map((cue) => [cue.id, cue]));
  const events = new Map(sheet.events.map((cue) => [cue.id, cue]));
  const positionToSeconds = (position: string) =>
    gridSeconds(position, bpm, beatsPerBar);
  const barStart = (bar: number) => (bar - 1) * beatsPerBar * (60 / bpm);

  function timedLine(id: string) {
    const cue = lines.get(id);
    if (!cue) throw new RangeError(`Unknown line: ${id}`);
    if (cue.missing || cue.at === undefined) {
      throw new RangeError(`Line has no timing: ${id}`);
    }
    return { cue, at: cue.at };
  }

  return {
    positionToSeconds,
    sectionAt(time: number): S | undefined {
      return sheet.sections.find(({ start, end, startBar, bars, missing }) => {
        if (missing) return false;
        if (start !== undefined && end !== undefined) {
          return time >= start && time < end;
        }
        if (startBar === undefined || bars === undefined) return false;
        return time >= barStart(startBar) && time < barStart(startBar + bars);
      });
    },
    line(id: string): number {
      const { cue, at } = timedLine(id);
      return cue.start ?? positionToSeconds(at);
    },
    event(id: string): number {
      const cue = events.get(id);
      if (!cue) throw new RangeError(`Unknown event: ${id}`);
      return positionToSeconds(cue.at);
    },
    /** Numeric word indices start at zero. Text selects the first match. */
    word(lineId: string, indexOrText: number | string): number {
      const { cue } = timedLine(lineId);
      const word = findWord(cue.words, lineId, indexOrText);
      return word.start ?? positionToSeconds(word.at);
    },
  };
}

export const { positionToSeconds, sectionAt, line, event, word } =
  createCueLookup(cueSheet);

/** Build a word lookup with measured absolute seconds for the supplied lines. */
export function withWordTimes(...overrides: readonly WordTimingOverride[]): {
  word: typeof word;
} {
  const measured = new Map<
    string,
    readonly { text: string; start: number }[]
  >();
  for (const { lineId, words } of overrides) {
    line(lineId);
    if (words.length === 0 || measured.has(lineId)) {
      throw new RangeError(`Invalid word timing override for ${lineId}`);
    }
    let previousStart = -1;
    measured.set(
      lineId,
      words.map(({ text, start, end }) => {
        if (
          !normalizeWord(text) ||
          !Number.isFinite(start) ||
          !Number.isFinite(end) ||
          start < 0 ||
          end <= start ||
          start <= previousStart
        ) {
          throw new RangeError(
            `Invalid measured word timing in ${lineId}: ${text}`,
          );
        }
        previousStart = start;
        return { text, start };
      }),
    );
  }
  return {
    word(lineId, indexOrText) {
      const words = measured.get(lineId);
      return words
        ? findWord(words, lineId, indexOrText).start
        : word(lineId, indexOrText);
    },
  };
}

/** Attack on each beat with an exponential time constant in seconds. */
export function beatPulse(time: number, decay: number): number {
  const beat = secondsToBeat(time);
  if (time < 0) return 0;
  const age = beatToSeconds(beat - Math.floor(beat));
  return decay > 0 ? Math.exp(-age / decay) : Number(age === 0);
}

export function barPhase(time: number): number {
  const bar = secondsToBar(time);
  return bar - Math.floor(bar);
}

/** Linear attack and release in seconds, with an instantaneous zero-length attack. */
export function hit(
  time: number,
  onset: number,
  attack: number,
  release: number,
): number {
  const age = time - onset;
  if (age < 0) return 0;
  if (age < attack) return age / attack;
  return release > 0 ? Math.max(0, 1 - (age - attack) / release) : 0;
}
