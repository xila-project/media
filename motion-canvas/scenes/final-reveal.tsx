import { Line, makeScene2D } from "@motion-canvas/2d";
import { clamp, createSignal, easeOutExpo, tween } from "@motion-canvas/core";
import { Logo, Text } from "../components/brand";
import production from "../../productions/final-reveal/production.json";

export default makeScene2D(function* (view) {
  view.fill("#000000");
  const paths = [-1, 1].map(
    (direction) =>
      new Line({
        points: [
          [direction * 1400, 280],
          [direction * 460, 280],
          [direction * 460, 0],
          [0, 0],
        ],
        stroke: "#ffffff",
        lineWidth: 3,
        end: 0,
      }),
  );
  view.add(paths);
  const mark = Logo({ lockup: true, width: production.lockupWidth });
  mark.scale(2.6);
  mark.opacity(0);
  mark.y(-70);
  const description = Text({
    text: production.description,
    fontSize: 36,
    fontWeight: 400,
    y: 200,
    opacity: 0,
  });
  const url = Text({
    text: production.url,
    fontSize: 32,
    fontWeight: 400,
    y: 310,
    opacity: 0,
  });
  view.add([mark, description, url]);
  const time = createSignal(0);
  const ramp = (start: number, duration: number) =>
    clamp(0, 1, (time() - start) / duration);
  const fade = () => 1 - ramp(production.duration - 0.55, 0.55);
  for (const path of paths) {
    path.end(() => ramp(0, 0.55));
    path.start(() => ramp(0.55, 0.45));
  }
  mark.opacity(() => ramp(0.55, 0.3) * fade());
  mark.scale(() => 2.6 - 1.6 * easeOutExpo(ramp(0.55, 1.05)));
  description.opacity(() => ramp(1.6, 0.4) * fade());
  description.y(() => 200 - 20 * ramp(1.6, 0.4));
  url.opacity(() => ramp(2, 0.4) * fade());
  yield* tween(production.duration, (value) =>
    time(value * production.duration),
  );
});
