// Render a production's editorial copy with the locked Montserrat to tight,
// transparent PNGs for 3D placement. Usage: node scripts/prepare-copy.mjs <production>
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { chromium } from "playwright";

const root = new URL("../", import.meta.url);
const name = process.argv[2];
if (!/^[a-z0-9-]+$/.test(name ?? ""))
  throw new Error("Usage: prepare-copy.mjs <production>");
const config = JSON.parse(
  await readFile(new URL(`productions/${name}/production.json`, root), "utf8"),
);
const output = new URL(`output/${name}/copy/`, root);
const font = (
  await readFile(
    new URL(
      "assets/brand/upstream/assets/typography/Montserrat-normal.woff2",
      root,
    ),
  )
).toString("base64");
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROMIUM_PATH
    ? { executablePath: process.env.CHROMIUM_PATH }
    : {}),
});
try {
  const page = await browser.newPage();
  // Load the locked face once and prove it is used: fonts.check() is true
  // for unregistered families, so compare against the serif fallback instead.
  const loaded = await page.evaluate(async (font) => {
    const face = new FontFace(
      "Montserrat",
      `url(data:font/woff2;base64,${font})`,
      {
        weight: "100 900",
      },
    );
    document.fonts.add(await face.load());
    const context = document.createElement("canvas").getContext("2d");
    const width = (family) => {
      context.font = `600 100px ${family}`;
      return context.measureText("An operating system.").width;
    };
    return width("Montserrat") !== width("serif");
  }, font);
  if (!loaded) throw new Error("Montserrat did not load");
  await mkdir(output, { recursive: true });
  const manifest = {};
  for (const [id, copy] of Object.entries(config.copy)) {
    const { png, width, height } = await page.evaluate(
      async ({ copy }) => {
        const size = 160;
        const spec = `${copy.weight} ${size}px Montserrat`;
        const canvas = document.createElement("canvas");
        let context = canvas.getContext("2d");
        context.font = spec;
        context.letterSpacing = `${copy.tracking ?? 0}px`;
        const pad = Math.round(size * 0.25);
        canvas.width =
          Math.ceil(context.measureText(copy.text).width) + pad * 2;
        canvas.height = Math.round(size * 1.5);
        context = canvas.getContext("2d");
        context.font = spec;
        context.letterSpacing = `${copy.tracking ?? 0}px`;
        context.fillStyle = "#ffffff";
        context.textBaseline = "middle";
        context.fillText(copy.text, pad, canvas.height / 2);
        return {
          png: canvas.toDataURL("image/png").split(",")[1],
          width: canvas.width,
          height: canvas.height,
        };
      },
      { copy },
    );
    await writeFile(new URL(`${id}.png`, output), Buffer.from(png, "base64"));
    manifest[id] = { text: copy.text, width, height };
  }
  await writeFile(
    new URL("copy.json", output),
    JSON.stringify(manifest, null, 2) + "\n",
  );
} finally {
  await browser.close();
}
