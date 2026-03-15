/**
 * Convert an RGB/RGBA CSS color string to a hex color string.
 * Examples:
 *   rgbToHex("rgb(255, 128, 0)")   → "#ff8000"
 *   rgbToHex("rgba(0, 0, 0, 0)")   → "#000000"
 *   rgbToHex("#aabbcc")            → "#aabbcc"  (passthrough)
 *   rgbToHex("transparent")        → "transparent"
 */
export function rgbToHex(color) {
  if (!color) return '#000000';
  if (color.startsWith('#')) return color;
  if (color === 'transparent' || color === 'rgba(0, 0, 0, 0)') return 'transparent';

  const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (!match) return color;

  const r = parseInt(match[1], 10).toString(16).padStart(2, '0');
  const g = parseInt(match[2], 10).toString(16).padStart(2, '0');
  const b = parseInt(match[3], 10).toString(16).padStart(2, '0');
  return `#${r}${g}${b}`;
}
