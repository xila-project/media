import assert from "node:assert/strict";
import { test } from "node:test";
import { screenSource } from "../motion-canvas/components/screen-source.ts";

test("screen slots resolve catalog IDs while preserving image proportions", () => {
  const slot = {
    asset: "desktop",
    width: 1200,
    height: 600,
    position: [10, 20],
  };
  const assets = [
    {
      id: "desktop",
      kind: "image",
      file: "assets/images/desktop.png",
      width: 800,
      height: 600,
    },
  ];
  assert.deepEqual(screenSource(slot, assets), {
    src: "/assets/images/desktop.png",
    width: 800,
    height: 600,
  });
  assert.deepEqual(screenSource({ ...slot, height: 300 }, assets), {
    src: "/assets/images/desktop.png",
    width: 400,
    height: 300,
  });
  assert.equal(screenSource({ ...slot, asset: null }, assets), null);
  assert.throws(
    () => screenSource({ ...slot, width: NaN }, assets),
    /dimensions/,
  );
});

test("unknown assets and invalid dimensions fail before rendering", () => {
  const slot = { asset: "missing", width: 1200, height: 600 };
  assert.throws(() => screenSource(slot, []), /Unknown screen asset/);
  assert.throws(
    () =>
      screenSource(slot, [
        {
          id: "missing",
          kind: "image",
          file: "assets/a.png",
          width: 0,
          height: 10,
        },
      ]),
    /dimensions/,
  );
});
