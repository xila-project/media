import assert from "node:assert/strict";
import { test } from "node:test";
import take from "../productions/not-your-regular/takes/001/cues.json" with { type: "json" };
import {
  barPhase,
  barToSeconds,
  beatPulse,
  beatToSeconds,
  createCueLookup,
  event,
  hit,
  line,
  positionToSeconds,
  secondsToBar,
  secondsToBeat,
  sectionAt,
  withWordTimes,
  word,
} from "../motion-canvas/components/beat.ts";

function near(actual: number, expected: number, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) < tolerance, `${actual} ≈ ${expected}`);
}

test("score positions and fractional subdivisions map to seconds", () => {
  near(barToSeconds(5), 7.742, 0.001);
  near(positionToSeconds("5.1"), 7.742, 0.001);
  near(positionToSeconds("53.4e"), 102.21774193548387);
  near(positionToSeconds("2.3&"), 3.1451612903225805);
  near(positionToSeconds("2.3a"), 3.2661290322580645);
  for (const malformed of ["0.1", "1.0", "1.5", "1.1x", "5", "1.1\n"]) {
    assert.throws(() => positionToSeconds(malformed), RangeError);
  }
});

test("beat offsets and one-based bar positions round-trip", () => {
  near(secondsToBeat(beatToSeconds(6.5)), 6.5);
  near(secondsToBar(barToSeconds(17.5)), 17.5);
  near(barPhase(positionToSeconds("53.4e")), 0.8125);
  for (let bar = 1; bar <= 81; bar++) {
    assert.equal(barPhase(barToSeconds(bar)), 0);
  }
});

test("section boundaries belong to the section starting there", () => {
  assert.equal(sectionAt(barToSeconds(5) - 0.001)?.id, "intro");
  assert.equal(sectionAt(barToSeconds(5))?.id, "verse-1");
  assert.equal(sectionAt(barToSeconds(81) - 0.001)?.id, "outro");
  assert.equal(sectionAt(barToSeconds(81)), undefined);
  assert.equal(sectionAt(-0.001), undefined);
});

test("line, word and event lookup return absolute seconds", () => {
  near(line("intro-booth"), 2.903225806451613);
  near(word("intro-booth", 1), 3.1451612903225805);
  near(word("intro-booth", "Booth"), 3.3870967741935485);
  near(event("trap-mute"), 102.09677419354838);
  assert.throws(() => line("missing"), RangeError);
  assert.throws(() => word("intro-booth", 3), RangeError);
  assert.throws(() => event("missing"), RangeError);
});

test("beat pulse resets to 1 on every beat and decays exponentially in seconds", () => {
  for (let beat = 0; beat < 320; beat++) {
    assert.equal(beatPulse(beatToSeconds(beat), 0.1), 1);
  }
  near(beatPulse(0.1, 0.1), Math.exp(-1));
  assert.equal(beatPulse(-0.1, 0.1), 0);
});

test("hit ramps from onset through its attack and release", () => {
  assert.equal(hit(0.9, 1, 0.25, 0.5), 0);
  assert.equal(hit(1, 1, 0.25, 0.5), 0);
  assert.equal(hit(1.125, 1, 0.25, 0.5), 0.5);
  assert.equal(hit(1.25, 1, 0.25, 0.5), 1);
  assert.equal(hit(1.5, 1, 0.25, 0.5), 0.5);
  assert.equal(hit(1.75, 1, 0.25, 0.5), 0);
  assert.equal(hit(1, 1, 0, 0.5), 1);
  assert.equal(hit(1.25, 1, 0.25, 0), 0);
});

test("measured word timings replace grid cues for a line without mutating the default", () => {
  const measured = withWordTimes({
    lineId: "intro-booth",
    words: [
      { text: "Just", start: 2.95, end: 3.1 },
      { text: "the", start: 3.16, end: 3.26 },
      { text: "booth.", start: 3.45, end: 3.6 },
    ],
  });
  assert.equal(measured.word("intro-booth", "booth"), 3.45);
  assert.equal(measured.word("intro-booth", 1), 3.16);
  assert.equal(measured.word("led-answer", "file"), word("led-answer", "file"));
  near(word("intro-booth", "booth"), 3.3870967741935485);
});

test("a take lookup uses measured seconds and the take's grid", () => {
  const measured = createCueLookup(take);
  assert.equal(measured.line("section-1-intro-01"), 5.94);
  assert.equal(measured.word("section-1-intro-01", "day"), 6.36);
  assert.equal(measured.word("section-10-bridge-08", "xila"), 119.04);
  assert.equal(measured.positionToSeconds("2.1"), 1.875);
  assert.equal(measured.sectionAt(5.939), undefined);
  assert.equal(measured.sectionAt(5.94)?.id, "section-1-intro");
  assert.equal(measured.sectionAt(10), undefined);
  assert.throws(() => measured.line("section-1-intro-02"), RangeError);
  assert.equal(sectionAt(0)?.id, "intro");
});
