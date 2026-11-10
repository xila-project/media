import assert from "node:assert/strict";
import { test } from "node:test";
import { rippleKeyframes } from "../scripts/bootsplash-keyframes.mjs";

test("cinematic reminder follows Core clockwise pulse timing", () => {
  const frames = rippleKeyframes({
    fps: 30,
    duration: 8,
    bootsplashRipple: { start: 5.3 },
  });
  assert.equal(frames.length, 240);
  assert.deepEqual(
    frames[158].arms.map((arm) => [arm.x, arm.y, arm.opacity]),
    Array.from({ length: 4 }, () => [0, 0, 255]),
  );
  for (const [frame, index, x, y] of [
    [171, 0, -16, -16],
    [183, 3, 16, -16],
    [195, 2, 16, 16],
    [207, 1, -16, 16],
  ]) {
    assert.deepEqual(frames[frame].arms[index], { x, y, opacity: 180 });
  }
  assert.deepEqual(
    frames[239].arms.map((arm) => [arm.x, arm.y, arm.opacity]),
    Array.from({ length: 4 }, () => [0, 0, 255]),
  );
});
