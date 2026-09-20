export const PROJECT_NAME_MAX_LENGTH = 40;

function cleanProjectName(value: string | null | undefined, fallback = "Untitled project") {
  const name = String(value ?? "").replace(/\s+/g, " ").trim();
  return name || fallback;
}

/** Keep project labels compact without changing the full value used for tooltips. */
export function truncateProjectName(value: string | null | undefined, fallback = "Untitled project") {
  const name = cleanProjectName(value, fallback);
  if (name.length <= PROJECT_NAME_MAX_LENGTH) return name;
  return `${name.slice(0, PROJECT_NAME_MAX_LENGTH - 1).trimEnd()}…`;
}

export function projectNameForInput(value: string | null | undefined, fallback = "Untitled project") {
  return cleanProjectName(value, fallback).slice(0, PROJECT_NAME_MAX_LENGTH);
}
