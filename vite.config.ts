import { defineConfig } from "vite";
import { createRequire } from "node:module";
const motionCanvas: typeof import("@motion-canvas/vite-plugin").default =
  createRequire(import.meta.url)("@motion-canvas/vite-plugin").default;
export default defineConfig({
  optimizeDeps: {
    noDiscovery: true,
    include: ["@motion-canvas/core", "@motion-canvas/2d"],
  },
  plugins: [
    motionCanvas({
      project: [
        "./motion-canvas/projects/trailer.ts",
        "./motion-canvas/projects/logo.ts",
        "./motion-canvas/projects/final-reveal.ts",
        "./motion-canvas/projects/rust-core.ts",
        "./motion-canvas/projects/wasm-execution.ts",
      ],
    }),
  ],
});
