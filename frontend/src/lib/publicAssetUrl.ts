/**
 * Resolve public files from the document base. The document base is the
 * single /slidegen mount point, so assets remain relative to the FE.
 */
export function publicAssetUrl(assetPath: string): string {
  const asset = assetPath.replace(/^\/+/, "");
  return new URL(`./${asset}`, document.baseURI).toString();
}
