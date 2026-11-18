import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import cues from "../productions/house-everything-is-a-file/cues.json" with { type: "json" };
import { positionToSeconds } from "../motion-canvas/components/beat.ts";

const concept = readFileSync(
  new URL(
    "../productions/house-everything-is-a-file/CONCEPT.md",
    import.meta.url,
  ),
  "utf8",
);

test("the score spans 80 contiguous bars at 124 BPM", () => {
  assert.equal(cues.bpm, 124);
  assert.equal(cues.beatsPerBar, 4);
  assert.equal(cues.bars, 80);
  let nextBar = 1;
  for (const section of cues.sections) {
    assert.equal(section.startBar, nextBar);
    nextBar += section.bars;
  }
  assert.equal(nextBar, 81);
  assert.ok(Math.abs(cues.duration - 154.839) < 0.001);
  assert.ok(Math.abs(positionToSeconds("81.1") - cues.duration) < 0.001);
});

test("the cue sheet carries every lyric at its arrangement stamp and every word in order", () => {
  const lyrics = [
    ...concept.matchAll(
      /^\| (\d+\.\d[e&a]?)\s*\| \*\*(ALIX|XILA) \(([^)]+)\)\*\* “([^”]+)”/gm,
    ),
  ];
  assert.deepEqual(
    cues.lines.map(({ at, speaker, delivery, text }) => [
      at,
      speaker,
      delivery,
      text,
    ]),
    lyrics.map(([, at, speaker, delivery, text]) => [
      at,
      speaker,
      delivery === "vocoder/sung" ? "sung" : delivery,
      text,
    ]),
  );
  for (const [index, line] of cues.lines.entries()) {
    assert.deepEqual(
      line.words.map(({ text }) => text),
      line.text.replace(/[.,?…]/g, "").split(" "),
    );
    assert.equal(line.words[0].at, line.at);
    const next = cues.lines[index + 1];
    let previous = -1;
    for (const word of line.words) {
      const time = positionToSeconds(word.at);
      assert.ok(time > previous, `${line.id}: ${word.text}`);
      assert.ok(
        time < (next ? positionToSeconds(next.at) : cues.duration),
        line.id,
      );
      previous = time;
    }
  }
});

test("explicit word stamps and hook light cues follow the concept", () => {
  function cue(id: string, text: string) {
    return cues.lines
      .find((line) => line.id === id)
      ?.words.find((word) => word.text === text);
  }
  assert.equal(cue("intro-booth", "the")?.at, "2.3&");
  assert.equal(cue("intro-memory", "Plenty")?.at, "4.3");
  assert.equal(cue("intro-memory", "Plenty")?.pitch, 3);
  assert.equal(cue("led-answer", "file")?.at, "6.3");
  assert.equal(cue("digits-question", "handwriting")?.at, "11.4");
  assert.equal(cue("digits-answer", "file")?.at, "13.4");
  assert.equal(cue("system-alive", "system")?.at, "53.4e");
  assert.ok(
    positionToSeconds(cue("system-alive", "alive")!.at) <
      positionToSeconds("54.1"),
  );

  const hookWords = ["Everything", "is", "a", "file"];
  const hookIds = [
    ["hook-25", "25.1", "25.2", "25.2&", "25.3"],
    ["hook-27", "27.1", "27.2", "27.2&", "27.3"],
    ["hook-30", "30.1", "30.2", "30.2&", "30.3"],
    ["hook-31", "31.1", "31.2", "31.2&", "31.3"],
    ["hook-49", "49.1", "49.2", "49.2&", "49.3"],
    ["hook-59", "59.1", "59.2", "59.2&", "59.3"],
    ["hook-61", "61.1", "61.2", "61.2&", "61.3"],
    ["hook-65", "65.1", "65.2", "65.2&", "65.3"],
    ["hook-67", "67.1", "67.2", "67.2&", "67.3"],
    ["hook-71", "71.3", "71.4", "71.4&", "72.1"],
  ];
  for (const [id, ...positions] of hookIds) {
    assert.deepEqual(
      hookWords.map((text) => cue(id, text)?.at),
      positions,
    );
    assert.equal(cue(id, "file")?.pitch, -3);
    for (const [index, text] of hookWords.entries()) {
      assert.equal(
        cues.events.find((event) => event.id === `${id}-${text.toLowerCase()}`)
          ?.at,
        positions[index],
      );
    }
  }
});

test("the trap mutes one beat, and room doubling is cued on every beat of bars 70 and 71", () => {
  assert.deepEqual(
    cues.events.find(({ id }) => id === "trap-mute"),
    {
      id: "trap-mute",
      at: "53.4",
      beats: 1,
      kind: "mute",
    },
  );
  assert.equal(cues.events.find(({ id }) => id === "drop-restart")?.at, "54.1");
  assert.deepEqual(
    cues.events
      .filter(({ kind }) => kind === "room-double")
      .map(({ at }) => at),
    ["70.1", "70.2", "70.3", "70.4", "71.1", "71.2", "71.3", "71.4"],
  );
});

test("timed edit and instrumental cues stay on the score grid", () => {
  const events = new Map(cues.events.map(({ id, at }) => [id, at]));
  assert.deepEqual(
    ["two", "fif", "ty", "six"].map((part) =>
      events.get(`memory-syllable-${part}`),
    ),
    ["3.4", "3.4&", "4.1", "4.1&"],
  );
  for (const [id, at] of [
    ["led-click", "6.3"],
    ["card-enter", "11.4"],
    ["card-stall", "12.4"],
    ["card-drop", "13.4"],
    ["digits-rimshot", "14.4"],
    ["digits-card-wipe", "16.4"],
    ["hook-projector-reveal", "32.4"],
    ["native-drawer-launch", "34.1"],
    ["drawing-route-corner", "40.4"],
    ["drop-shutter-open", "49.1"],
    ["browser-capture-match", "73.1"],
  ]) {
    assert.equal(events.get(id), at, id);
  }
  for (const beat of [1, 2, 3, 4]) {
    assert.equal(events.get(`pre-shutter-${beat}`), `24.${beat}`);
    assert.equal(events.get(`break-hat-${beat}`), `48.${beat}`);
  }
  let previous = -1;
  for (const { id, at } of cues.events) {
    const time = positionToSeconds(at);
    assert.ok(time >= previous && time < positionToSeconds("81.1"), id);
    previous = time;
  }
});
