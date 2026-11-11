import { makeScene2D, Video } from "@motion-canvas/2d";
import { waitFor } from "@motion-canvas/core";
import { Logo, Text } from "../components/brand";
import { Screen } from "../components/screen";
import production from "../../productions/trailer/production.json";
export default makeScene2D(function* (view) {
  view.fill("#000000");
  const logo = Logo({ width: 64 });
  logo.position([-800, -400]);
  view.add(logo);
  view.add(Text({ text: "Xila in motion", fontSize: 44, y: -400 }));
  const slot = production.screens.main;
  if (production.footage) {
    const video = new Video({
      src: production.footage,
      width: slot.width,
      height: slot.height,
      x: slot.position[0],
      y: slot.position[1],
    });
    view.add(video);
    video.play();
  } else {
    view.add(Screen(slot));
  }
  const caption = production.footage
    ? "Recorded Xila session"
    : slot.asset
      ? "Captured Xila interface"
      : "Production test • no interface simulation";
  view.add(Text({ text: caption, fontSize: 22, fontWeight: 400, y: 450 }));
  yield* waitFor(2.5);
  yield* view.opacity(0, 0.5);
});
