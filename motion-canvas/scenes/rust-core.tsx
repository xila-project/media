import { Line, Node, Rect, makeScene2D } from "@motion-canvas/2d";
import {
  clamp,
  createSignal,
  easeInOutCubic,
  easeOutCubic,
  tween,
} from "@motion-canvas/core";
import { Logo, Text } from "../components/brand";
import production from "../../productions/rust-core/production.json";

export default makeScene2D(function* (view) {
  view.fill("#000000");
  const time = createSignal(0);
  const ramp = (start: number, duration: number) =>
    clamp(0, 1, (time() - start) / duration);
  const field = new Node({ y: 110 });
  view.add(field);
  field.scale(
    () =>
      1.65 -
      0.65 * easeOutCubic(ramp(0, 3)) +
      0.75 * easeInOutCubic(ramp(7, 3)),
  );
  field.x(() => -650 * easeInOutCubic(ramp(7, 3)));
  for (let row = 0; row < 4; row++) {
    for (let column = 0; column < 8; column++) {
      const start = 0.08 * column + 0.12 * row;
      const tile = new Rect({
        width: 104,
        height: 104,
        radius: 2,
        fill: "#111111",
        stroke: "#555555",
        lineWidth: 1,
      });
      tile.x(
        () =>
          (column - 3.5) * 116 - 1100 * (1 - easeOutCubic(ramp(start, 1.35))),
      );
      tile.y(
        () => (row - 1.5) * 116 + 280 * (1 - easeOutCubic(ramp(start, 1.35))),
      );
      tile.opacity(() => ramp(start, 0.35));
      field.add(tile);
    }
  }
  for (let row = 0; row < 4; row++) {
    const y = (row - 1.5) * 116;
    const route = new Line({
      points: [
        [-1300, y],
        [-470, y],
        [-470, y + 36],
        [470, y + 36],
        [470, y],
        [1500, y],
      ],
      stroke: "#bfbfbf",
      lineWidth: 2,
    });
    route.end(() => ramp(1.6 + row * 0.15, 1.2));
    field.add(route);
    const pulse = new Line({
      points: route.points()!,
      stroke: "#ffffff",
      lineWidth: 5,
    });
    const progress = () => ramp(2.4 + row * 0.16, 1.8);
    pulse.start(() => Math.max(0, progress() - 0.08));
    pulse.end(progress);
    pulse.opacity(() => 1 - ramp(4.2 + row * 0.16, 0.2));
    field.add(pulse);
  }
  const shade = new Rect({
    width: 1920,
    height: 420,
    y: -330,
    fill: "#000000",
  });
  view.add(shade);
  const heading = Text({ text: production.copy, fontSize: 96, y: -300 });
  heading.opacity(() => ramp(1, 0.45) * (1 - ramp(6, 0.45)));
  heading.x(() => -90 + 90 * easeOutCubic(ramp(1, 0.7)));
  view.add(heading);
  const supporting = Text({
    text: production.supportingCopy,
    fontSize: 36,
    fontWeight: 400,
    y: -205,
  });
  supporting.opacity(() => ramp(3, 0.4) * (1 - ramp(6, 0.45)));
  view.add(supporting);
  const logo = Logo({ width: 72 });
  logo.position([790, -390]);
  logo.opacity(() => 1 - ramp(2, 0.5));
  view.add(logo);
  const exit = new Line({
    points: [
      [-900, 110],
      [0, 110],
      [0, -40],
      [1600, -40],
    ],
    stroke: "#ffffff",
    lineWidth: 6,
  });
  exit.end(() => ramp(7.4, 2.2));
  exit.start(() => Math.max(0, ramp(7.4, 2.2) - 0.13));
  exit.opacity(() => ramp(7.3, 0.1));
  view.add(exit);
  yield* tween(production.duration, (value) =>
    time(value * production.duration),
  );
});
