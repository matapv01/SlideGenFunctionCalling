// Utility: convert computed RGB color strings to hex (#RRGGBB)
export function rgbToHex(color) {
    if (!color || color === 'transparent') return '#000000';
    if (color.startsWith('#')) return color;

    const nums = color.match(/\d+/g);
    if (!nums || nums.length < 3) return '#000000';

    const r = parseInt(nums[0]).toString(16).padStart(2, '0');
    const g = parseInt(nums[1]).toString(16).padStart(2, '0');
    const b = parseInt(nums[2]).toString(16).padStart(2, '0');

    return `#${r}${g}${b}`;
}
