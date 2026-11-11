import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import {
  CLOCKWISE_RANK,
  DIRECTION,
  PERIOD,
  loopArm,
} from "../motion-canvas/components/bootsplash-timeline.ts";

// The Blender scene consumes the same tested Core timeline as Motion Canvas.
// Finish the last arm's pulse before holding, rather than starting a second lap.
export function rippleKeyframes(config) {
  return Array.from(
    { length: Math.round(config.duration * config.fps) },
    (_, frame) => {
      const time = Math.round(
        (frame / config.fps - config.bootsplashRipple.start) * 1000,
      );
      const arms = CLOCKWISE_RANK.map((rank, index) => {
        const state =
          time < 0 || time >= (rank * PERIOD) / 4 + PERIOD / 2
            ? { offset: 0, opacity: 255 }
            : loopArm(index, time, 320, true);
        return {
          x: DIRECTION[index][0] * state.offset || 0,
          y: DIRECTION[index][1] * state.offset || 0,
          opacity: state.opacity,
        };
      });
      return { frame, arms };
    },
  );
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  // Optional: --duration <s> --fps <n> --start <s> for other productions' shots.
  const args = Object.fromEntries(
    process.argv
      .slice(2)
      .flatMap((value, index, list) =>
        value.startsWith("--")
          ? [[value.slice(2), Number(list[index + 1])]]
          : [],
      ),
  );
  const config =
    args.start === undefined
      ? JSON.parse(
          readFileSync(
            new URL(
              "../productions/cinematic-opening/production.json",
              import.meta.url,
            ),
            "utf8",
          ),
        )
      : {
          duration: args.duration,
          fps: args.fps,
          bootsplashRipple: { start: args.start },
        };
  process.stdout.write(JSON.stringify(rippleKeyframes(config)));
}
