import { makeScene2D } from "@motion-canvas/2d";
import { linear } from "@motion-canvas/core";
import { Bootsplash } from "../components/bootsplash";
export default makeScene2D(function* (view) {
  view.fill("#000000");
  const splash = Bootsplash();
  view.add(splash.node);
  // Core intro (900 ms) followed by its clockwise ripple. No trailer-only caption.
  yield* splash.time(2500, 2.5, linear);
  yield* view.opacity(0, 0.5);
});
