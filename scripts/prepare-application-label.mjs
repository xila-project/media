import { readFile, mkdir, writeFile } from "node:fs/promises";
import { chromium } from "playwright";
const root = new URL("../", import.meta.url);
const config = JSON.parse(
  await readFile(
    new URL("productions/application-handoff/production.json", root),
    "utf8",
  ),
);
if (!/^[0-9]{3}$/.test(config.review)) throw new Error("Invalid review number");
const output = new URL(
  `output/application-handoff/review-${config.review}/`,
  root,
);
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
  const png = await page.evaluate(
    async ({ font, name }) => {
      const face = new FontFace(
        "Montserrat",
        `url(data:font/woff2;base64,${font})`,
        { weight: "100 900" },
      );
      document.fonts.add(await face.load());
      const canvas = document.createElement("canvas");
      // A single engraved filename: supporting detail, not a headline.
      canvas.width = 2048;
      canvas.height = 256;
      const context = canvas.getContext("2d");
      context.fillStyle = "#ffffff";
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.letterSpacing = "12px";
      context.font = "500 120px Montserrat";
      context.fillText(name, 1024, 128);
      return canvas.toDataURL("image/png").split(",")[1];
    },
    { font, name: config.application },
  );
  await mkdir(output, {
    recursive: true,
  });
  await writeFile(
    new URL("application-label.png", output),
    Buffer.from(png, "base64"),
  );
} finally {
  await browser.close();
}
