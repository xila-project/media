import { Img, Rect } from "@motion-canvas/2d";
import catalog from "../../assets/catalog.json";
import { Text } from "./brand";
import { screenSource, type ScreenSlot } from "./screen-source";

/** A replaceable screenshot surface. Animate the returned node independently of its content. */
export function Screen(slot: ScreenSlot) {
  const source = screenSource(slot, catalog.assets);
  const panel = new Rect({
    width: slot.width,
    height: slot.height,
    x: slot.position[0],
    y: slot.position[1],
  });
  if (source) {
    panel.add(new Img(source));
  } else {
    panel.stroke("#555555");
    panel.lineWidth(2);
    panel.add(Text({ text: "SCREENSHOT PLACEHOLDER", fontSize: 40 }));
    panel.add(
      Text({
        text: "Replace with a verified Xila capture",
        fontSize: 24,
        fontWeight: 400,
        y: 75,
      }),
    );
  }
  return panel;
}
