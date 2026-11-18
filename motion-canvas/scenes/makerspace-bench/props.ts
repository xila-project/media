import {
  Circle,
  Gradient,
  Img,
  Line,
  Node,
  Path,
  Rect,
} from "@motion-canvas/2d";
import type { RectProps, TxtProps } from "@motion-canvas/2d";
import { Text } from "../../components/brand";
import nanoImage from "../../../assets/images/makerspace-bench/nano-33-ble.jpg";

export const ink = "#101632";
export const cobalt = "#264ded";
export const coral = "#ff685e";
export const paper = "#fff0da";
const silver = "#bdc7dd";

export function word(text: TxtProps["text"], size: number, fill = paper) {
  return Text({
    text,
    fontSize: size,
    fontWeight: 850,
    letterSpacing: -size * 0.025,
    fill,
  });
}

export function tape(
  text: TxtProps["text"],
  width: number,
  props: RectProps = {},
  size = 53,
  colour = coral,
) {
  return new Rect({
    width,
    height: size * 1.52,
    radius: 4,
    fill: colour,
    shadowColor: "#070c3777",
    shadowBlur: 13,
    shadowOffset: [4, 8],
    ...props,
    children: [
      new Rect({
        width: width - 8,
        height: size * 1.42,
        stroke: colour === cobalt ? "#b9c9ff65" : "#fff0da6b",
        lineWidth: 2,
        radius: 3,
      }),
      word(text, size, colour === cobalt ? paper : ink),
    ],
  });
}

export function plate(src: string, scale = 1.01, y = 0, x = 0) {
  return new Img({ src, width: 1920, height: 1080, scale, x, y });
}

function nano() {
  // The unaltered Arduino photograph is clipped to its PCB and USB silhouette.
  // The D13 LED glow lives in a separate layer and never changes the source image.
  return new Node({
    children: [
      new Rect({
        width: 378,
        height: 158,
        x: 6,
        radius: 4,
        fill: "#070d23",
        shadowBlur: 23,
        shadowOffset: [12, 18],
        shadowColor: "#070d23dd",
      }),
      new Path({
        data: "M -181 -79 H 202 V 79 H -181 V 35 H -196 V -40 H -181 Z",
        clip: true,
      }),
    ],
  });
}

export function board(lit: () => number) {
  const body = nano();
  const mask = body.children()[1];
  mask.add(new Img({ src: nanoImage, width: 520, height: 330 }));
  body.add(
    new Circle({
      x: -172,
      y: 52,
      size: 56,
      opacity: () => lit() * 0.85,
      fill: new Gradient({
        type: "radial",
        from: [0, 0],
        fromRadius: 4,
        to: [0, 0],
        toRadius: 28,
        stops: [
          { offset: 0, color: "#fff8e5" },
          { offset: 0.28, color: "#ffd8c1bf" },
          { offset: 1, color: "#ff685e00" },
        ],
      }),
    }),
  );
  body.add(
    new Rect({
      x: -172,
      y: 52,
      width: 12,
      height: 7,
      rotation: 3,
      radius: 2,
      fill: "#fff3c9",
      opacity: lit,
    }),
  );
  return body;
}

export function chip() {
  const body = new Node({});
  for (const side of [-1, 1]) {
    for (let i = 0; i < 12; i++) {
      body.add(
        new Rect({
          x: -438 + i * 79,
          y: side * 339,
          width: 41,
          height: 165,
          radius: 6,
          fill: silver,
          stroke: "#e8e6ed",
          lineWidth: 3,
        }),
      );
      body.add(
        new Rect({
          x: side * 519,
          y: -274 + i * 50,
          width: 135,
          height: 25,
          radius: 4,
          fill: silver,
        }),
      );
    }
  }
  body.add(
    new Rect({
      size: [970, 632],
      radius: 34,
      fill: new Gradient({
        type: "linear",
        from: [-500, -300],
        to: [480, 310],
        stops: [
          { offset: 0, color: "#393d62" },
          { offset: 0.4, color: "#171b37" },
          { offset: 1, color: "#090c23" },
        ],
      }),
      stroke: "#64698b",
      lineWidth: 4,
      shadowOffset: [18, 32],
      shadowBlur: 40,
      shadowColor: "#060b30b0",
    }),
  );
  body.add(
    new Circle({
      size: 42,
      x: -416,
      y: -231,
      fill: "#0b112d",
      stroke: "#5e6480",
      lineWidth: 3,
    }),
  );
  return body;
}

export function traces() {
  const panel = new Rect({ size: [2200, 1360], fill: "#1b39a0" });
  for (let row = -8; row <= 8; row++) {
    for (const side of [-1, 1]) {
      const y = row * 76;
      const elbow = side * (660 + Math.abs(row) * 38);
      const end = side * 1100;
      panel.add(
        new Line({
          points: [
            [side * 250, y * 0.68],
            [elbow - side * 74, y * 0.68],
            [elbow, y],
            [end, y],
          ],
          stroke: row % 3 ? "#4f72dc" : "#ff837699",
          lineWidth: 4,
        }),
      );
      panel.add(
        new Circle({
          x: elbow,
          y,
          size: 14,
          stroke: "#a8bafc",
          fill: "#1b39a0",
          lineWidth: 3,
        }),
      );
    }
  }
  return panel;
}

export function scope() {
  const housing = new Rect({
    size: [1510, 865],
    fill: "#d6cccb",
    radius: 45,
    stroke: "#fff0da",
    lineWidth: 5,
    shadowColor: "#080a20",
    shadowOffset: [30, 35],
    shadowBlur: 50,
  });
  const glass = new Rect({
    x: -154,
    size: [1100, 727],
    radius: 55,
    fill: "#081632",
    stroke: "#283b6b",
    lineWidth: 18,
    clip: true,
  });
  for (let i = -6; i <= 6; i++) {
    glass.add(
      new Rect({ width: 2, height: 727, x: i * 86, fill: "#32528799" }),
    );
  }
  for (let i = -4; i <= 4; i++) {
    glass.add(
      new Rect({ width: 1100, height: 2, y: i * 80, fill: "#32528799" }),
    );
  }
  housing.add(glass);
  for (const y of [-260, -85, 90, 265]) {
    housing.add(
      new Circle({
        x: 572,
        y,
        size: 115,
        fill: "#333452",
        stroke: "#b7b7ce",
        lineWidth: 5,
        shadowColor: "#15152d99",
        shadowOffset: [6, 10],
        shadowBlur: 15,
      }),
    );
    housing.add(
      new Rect({
        x: 572,
        y: y - 33,
        width: 6,
        height: 25,
        radius: 3,
        fill: coral,
        rotation: 25,
      }),
    );
  }
  return { housing, glass };
}
