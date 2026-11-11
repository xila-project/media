import { Line, Node, Rect, makeScene2D } from "@motion-canvas/2d";
import {
  clamp,
  createSignal,
  easeInOutCubic,
  easeOutCubic,
  tween,
} from "@motion-canvas/core";
import { Logo, Text } from "../components/brand";
import { Screen } from "../components/screen";
import production from "../../productions/wasm-execution/production.json";

export default makeScene2D(function* (view) {
  view.fill("#000000");
  const time = createSignal(0);
  const ramp = (start: number, duration: number) =>
    clamp(0, 1, (time() - start) / duration);
  const stage = new Node({ y: 100 });
  view.add(stage);
  stage.scale(
    () =>
      1.8 -
      0.55 * easeOutCubic(ramp(0, 3)) +
      2.1 * easeInOutCubic(ramp(8, 3.2)),
  );
  stage.rotation(() => -10 * (1 - ramp(0, 3)) - 7 * ramp(8, 3.2));
  stage.x(() => -220 * easeInOutCubic(ramp(8, 3.2)));
  stage.opacity(() => 1 - ramp(11.05, 0.15));
  const track = new Line({
    points: [
      [-1500, 0],
      [-320, 0],
      [-320, -170],
      [320, -170],
      [320, 0],
      [1500, 0],
    ],
    stroke: "#555555",
    lineWidth: 2,
  });
  track.end(() => ramp(0, 1.4));
  stage.add(track);
  const gate = new Rect({
    width: 640,
    height: 460,
    stroke: "#888888",
    lineWidth: 2,
    radius: 3,
    fill: "#080808",
  });
  gate.opacity(() => ramp(0.4, 0.7));
  stage.add(gate);
  for (let i = 0; i < 5; i++) {
    const bar = new Line({
      points: [
        [-240 + i * 120, -170],
        [-240 + i * 120, 170],
      ],
      stroke: "#333333",
      lineWidth: 2,
    });
    bar.end(() => ramp(0.8 + i * 0.1, 0.6));
    stage.add(bar);
  }
  for (let i = 0; i < 3; i++) {
    const module = new Rect({
      width: 96,
      height: 96,
      fill: "#181818",
      stroke: "#eeeeee",
      lineWidth: 2,
    });
    const t = () => time() - i * 0.65;
    module.x(
      () =>
        -1350 +
        1050 * easeOutCubic(clamp(0, 1, t() / 1.5)) +
        600 * easeInOutCubic(clamp(0, 1, (t() - 2) / 1.2)) +
        1000 * easeInOutCubic(clamp(0, 1, (t() - 3.6) / 1.2)),
    );
    module.y(() => -70 * Math.sin(Math.PI * clamp(0, 1, (t() - 2) / 1.2)));
    module.opacity(() => 1 - ramp(5.8, 0.4));
    stage.add(module);
  }
  const primary = Text({ text: production.copy, fontSize: 88, y: -365 });
  const secondary = Text({
    text: production.supportingCopy,
    fontSize: 36,
    fontWeight: 400,
    y: -265,
  });
  primary.opacity(() => ramp(4, 0.4) * (1 - ramp(7, 0.4)));
  secondary.opacity(() => ramp(4.2, 0.4) * (1 - ramp(7, 0.4)));
  view.add([primary, secondary]);
  const pointer = new Line({
    points: [
      [-1400, 160],
      [-200, 160],
      [-200, 0],
      [0, 0],
    ],
    stroke: "#ffffff",
    lineWidth: 5,
  });
  pointer.end(() => ramp(7, 0.7));
  pointer.start(() => Math.max(0, ramp(7, 0.7) - 0.16));
  stage.add(pointer);
  const surface = new Rect({
    width: 270,
    height: 170,
    fill: "#111111",
    stroke: "#aaaaaa",
    lineWidth: 2,
  });
  surface.opacity(() => ramp(7.65, 0.25));
  stage.add(surface);
  const stroke = new Line({
    points: [
      [-100, 40],
      [-40, 40],
      [-40, -35],
      [100, -35],
    ],
    stroke: "#ffffff",
    lineWidth: 7,
  });
  stroke.end(() => ramp(7.9, 0.9));
  stage.add(stroke);
  const reply = new Line({
    points: [
      [0, 0],
      [200, 0],
      [200, -160],
      [1500, -160],
    ],
    stroke: "#ffffff",
    lineWidth: 5,
  });
  reply.end(() => ramp(8.9, 1.2));
  reply.start(() => Math.max(0, ramp(8.9, 1.2) - 0.12));
  stage.add(reply);
  const drawer = Screen(production.screens.drawer);
  drawer.opacity(() => ramp(11.2, 0.12));
  view.add(drawer);
  const logo = Logo({ width: 72 });
  logo.position([790, -390]);
  logo.opacity(() => 1 - ramp(3, 0.5));
  view.add(logo);
  yield* tween(production.duration, (value) =>
    time(value * production.duration),
  );
});
