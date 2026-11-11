import {
  Renderer,
  RendererResult,
  Vector2,
  type Project,
  type RendererSettings,
} from "@motion-canvas/core";
import "./global.css";
import trailerProject from "./projects/trailer?project";
import logoProject from "./projects/logo?project";
import finalProject from "./projects/final-reveal?project";
import rustProject from "./projects/rust-core?project";
declare global {
  interface Window {
    saveFrame: (frame: number, data: string) => Promise<void>;
    runRender: (options: {
      production: string;
      scene?: string;
      fps: number;
      width: number;
      height: number;
      duration: number;
    }) => Promise<void>;
  }
}
window.runRender = async ({
  production,
  scene,
  fps,
  width,
  height,
  duration,
}) => {
  const projects: Record<string, Project> = {
    trailer: trailerProject,
    logo: logoProject,
    "final-reveal": finalProject,
    "rust-core": rustProject,
  };
  const project = { ...projects[production] };
  if (scene)
    project.scenes = project.scenes.filter(
      (description) => description.name === scene,
    );
  if (project.scenes.length === 0) throw new Error(`Scene not found: ${scene}`);
  await document.fonts.load("600 64px Montserrat");
  await document.fonts.load("400 24px Montserrat");
  await document.fonts.ready;
  if (!document.fonts.check("600 64px Montserrat"))
    throw new Error("Montserrat did not load");
  project.meta.rendering.exporter.exporters.push({
    id: "xila-png",
    displayName: "Xila PNG sequence",
    meta: () => {
      throw new Error("CLI exporter has no editor options");
    },
    create: async () => ({
      handleFrame: async (canvas, frame) => {
        // Renderer includes the end frame; deliver exactly duration*fps frames.
        if (frame < Math.round(duration * fps))
          await window.saveFrame(frame, canvas.toDataURL("image/png"));
      },
    }),
  });
  const renderer = new Renderer(project);
  const outcome = { result: RendererResult.Error as RendererResult };
  renderer.onFinished.subscribe((value) => {
    outcome.result = value;
  });
  const errors: unknown[] = [];
  project.logger.onLogged.subscribe((entry) => {
    if (entry.level === "error") errors.push(entry);
  });
  const settings: RendererSettings = {
    name: production,
    size: new Vector2(1920, 1080),
    resolutionScale: width / 1920,
    background: "#000000",
    colorSpace: "srgb",
    fps,
    range: [0, duration],
    exporter: { name: "xila-png", options: {} },
  };
  if (height !== (width * 9) / 16) throw new Error("Only 16:9 is supported");
  await renderer.render(settings);
  if (outcome.result !== RendererResult.Success || errors.length)
    throw new Error(JSON.stringify(errors));
};
