import { Img, Node } from "@motion-canvas/2d";
import { createSignal } from "@motion-canvas/core";
import officialSymbol from "../../assets/brand/upstream/assets/symbol/xila-symbol-white.svg?raw";
import {
  DIRECTION,
  INTRO,
  PERIOD,
  introArm,
  loopArm,
  squareOpacity,
} from "./bootsplash-timeline";

/** Isolate an official module without rewriting its path, rect, or transform. */
function moduleSource(index: number) {
  const document = new DOMParser().parseFromString(
    officialSymbol,
    "image/svg+xml",
  );
  const group = document.querySelector("g");
  if (!group || group.children.length !== 5)
    throw new Error(
      "Unexpected official symbol structure; review brand update",
    );
  Array.from(group.children).forEach((child, i) => {
    if (i !== index) child.remove();
  });
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(document))}`;
}

export function Bootsplash({ width = 320 } = {}) {
  const time = createSignal(0);
  const node = new Node({});
  // Upstream order: center, BR, TR, TL, BL. Core order: TL, BL, BR, TR.
  const sourceIndex = [3, 4, 1, 2];
  node.add(
    new Img({
      src: moduleSource(0),
      width,
      opacity: () => squareOpacity(time()) / 255,
    }),
  );
  sourceIndex.forEach((source, index) => {
    const state = () =>
      time() < INTRO
        ? introArm(index, time(), width)
        : loopArm(index, time() - INTRO, width, time() < INTRO + PERIOD);
    node.add(
      new Img({
        src: moduleSource(source),
        width,
        opacity: () => state().opacity / 255,
        x: () => DIRECTION[index][0] * state().offset,
        y: () => DIRECTION[index][1] * state().offset,
      }),
    );
  });
  return { node, time };
}
