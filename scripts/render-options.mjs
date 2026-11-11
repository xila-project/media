import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";
const config = JSON.parse(
  readFileSync(
    new URL("../productions/trailer/production.json", import.meta.url),
    "utf8",
  ),
);
export function renderOptions(args) {
  const { values } = parseArgs({
    args,
    options: {
      production: { type: "string", default: "trailer" },
      scene: { type: "string" },
      resolution: {
        type: "string",
        default: `${config.width}x${config.height}`,
      },
      fps: { type: "string", default: String(config.fps) },
      preset: { type: "string", default: "medium" },
    },
  });
  const { production, preset, scene } = values;
  if (
    !["trailer", "logo"].includes(production) ||
    !["1920x1080", "1280x720", "960x540"].includes(values.resolution) ||
    ![24, 30, 60].includes(Number(values.fps)) ||
    !["fast", "medium", "slow"].includes(preset)
  )
    throw new Error("Invalid production, resolution, FPS or preset");
  const selected = config.scenes.find((item) => item.name === scene);
  if (scene && (!selected || production !== "trailer"))
    throw new Error(
      "Select a trailer scene: intro, typography, footage, architecture, outro",
    );
  const [width, height] = values.resolution.split("x").map(Number);
  return {
    production,
    preset,
    scene,
    width,
    height,
    fps: Number(values.fps),
    duration:
      production === "logo"
        ? config.scenes[0].duration
        : (selected?.duration ?? config.duration),
    outputName: scene ?? production,
  };
}
