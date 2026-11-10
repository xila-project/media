import assert from "node:assert/strict";
import { test } from "node:test";
import {
  INTRO,
  PERIOD,
  introArm,
  loopArm,
  squareOpacity,
} from "../motion-canvas/components/bootsplash-timeline.ts";

test("intro starts hidden and ends on the exact symbol", () => {
  assert.equal(INTRO, 900);
  assert.equal(squareOpacity(0), 0);
  assert.equal(squareOpacity(INTRO), 255);
  for (let i = 0; i < 4; i++) {
    assert.deepEqual(introArm(i, 0, 320), { offset: 64, opacity: 0 });
    assert.deepEqual(introArm(i, INTRO, 320), { offset: 0, opacity: 255 });
  }
});
test("arms assemble clockwise: top-left, top-right, bottom-right, bottom-left", () => {
  const time = 300;
  assert.ok(introArm(0, time, 320).opacity > introArm(3, time, 320).opacity);
  assert.ok(introArm(3, time, 320).opacity > introArm(2, time, 320).opacity);
  assert.equal(introArm(2, time, 320).opacity, 0);
  assert.equal(introArm(1, time, 320).opacity, 0);
});
test("ripple respects Core offsets, opacity and first-cycle behavior", () => {
  assert.equal(PERIOD, 1600);
  assert.deepEqual(loopArm(0, 400, 320, true), { offset: 16, opacity: 180 });
  assert.deepEqual(loopArm(3, 800, 320, true), { offset: 16, opacity: 180 });
  assert.deepEqual(loopArm(1, 200, 320, true), { offset: 0, opacity: 255 });
  assert.notDeepEqual(loopArm(1, 200, 320, false), { offset: 0, opacity: 255 });
  for (let t = 0; t < PERIOD * 2; t += 10)
    for (let i = 0; i < 4; i++) {
      const state = loopArm(i, t, 320, false);
      assert.ok(state.offset >= 0 && state.offset <= 16);
      assert.ok(state.opacity >= 180 && state.opacity <= 255);
    }
});
