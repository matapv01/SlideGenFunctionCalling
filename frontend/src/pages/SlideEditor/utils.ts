// --- Helper: Convert px string to number ---
export const pxToNum = (val: string | null): number =>
  val ? parseFloat(val.replace("px", "")) : 0;
