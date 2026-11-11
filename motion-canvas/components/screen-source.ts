export interface ScreenSlot {
  asset: string | null;
  width: number;
  height: number;
  position: number[];
}

interface ScreenAsset {
  id: string;
  kind: string;
  file: string;
  width?: number;
  height?: number;
}

/** Fit the source inside its slot without cropping or stretching the real interface. */
export function screenSource(
  slot: Pick<ScreenSlot, "asset" | "width" | "height">,
  assets: ScreenAsset[],
) {
  if (slot.asset === null) return null;
  const asset = assets.find((item) => item.id === slot.asset);
  if (!asset) throw new Error(`Unknown screen asset: ${slot.asset}`);
  const { width, height } = asset;
  if (
    asset.kind !== "image" ||
    ![width, height, slot.width, slot.height].every(
      (value) => typeof value === "number" && Number.isFinite(value),
    ) ||
    !width ||
    !height ||
    width <= 0 ||
    height <= 0 ||
    slot.width <= 0 ||
    slot.height <= 0
  ) {
    throw new Error(
      "Screen assets require image dimensions and a positive slot size",
    );
  }
  const scale = Math.min(slot.width / width, slot.height / height);
  return {
    src: `/${asset.file}`,
    width: width * scale,
    height: height * scale,
  };
}
