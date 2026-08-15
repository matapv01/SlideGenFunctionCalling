export type XmlTransitionType =
  | "none"
  | "fade"
  | "push"
  | "wipe"
  | "split"
  | "cover"
  | "uncover"
  | "zoom"
  | "cut"
  | "random"
  | "wheel"
  | "strips"
  | "circle"
  | "diamond"
  | "plus";

export type XmlTransitionDirection = "l" | "r" | "u" | "d" | "in" | "out";
export type XmlTransitionAdvance = "click" | "after" | "both";

export interface XmlTransitionConfig {
  type: XmlTransitionType;
  direction: XmlTransitionDirection;
  duration: number;
  advance: XmlTransitionAdvance;
  delay: number;
}

export const XML_TRANSITION_OPTIONS: Array<{ value: XmlTransitionType; label: string; description: string }> = [
  { value: "none", label: "None", description: "Instant change" },
  { value: "fade", label: "Fade", description: "Soft dissolve" },
  { value: "push", label: "Push", description: "New slide pushes from an edge" },
  { value: "wipe", label: "Wipe", description: "Reveal from an edge" },
  { value: "split", label: "Split", description: "Open from the center" },
  { value: "cover", label: "Cover", description: "New slide covers the old one" },
  { value: "uncover", label: "Uncover", description: "Old slide pulls away" },
  { value: "zoom", label: "Zoom", description: "Zoom into the new slide" },
  { value: "cut", label: "Cut", description: "Instant cut" },
  { value: "random", label: "Random", description: "PowerPoint chooses an effect" },
  { value: "wheel", label: "Wheel", description: "Rotating spokes" },
  { value: "strips", label: "Strips", description: "Diagonal strips" },
  { value: "circle", label: "Circle", description: "Circular reveal" },
  { value: "diamond", label: "Diamond", description: "Diamond reveal" },
  { value: "plus", label: "Plus", description: "Plus-shaped reveal" },
];

export const XML_TRANSITION_DIRECTIONS: Array<{ value: XmlTransitionDirection; label: string }> = [
  { value: "l", label: "From left" },
  { value: "r", label: "From right" },
  { value: "u", label: "From top" },
  { value: "d", label: "From bottom" },
  { value: "in", label: "In" },
  { value: "out", label: "Out" },
];

const numberOr = (value: string | undefined, fallback: number) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const transitionTypes = new Set<XmlTransitionType>(XML_TRANSITION_OPTIONS.map((option) => option.value));
const transitionDirections = new Set<XmlTransitionDirection>(XML_TRANSITION_DIRECTIONS.map((option) => option.value));

export const readXmlTransition = (attrs: Record<string, string>): XmlTransitionConfig => {
  const rawType = attrs.transition?.trim().toLowerCase() as XmlTransitionType | undefined;
  const rawDirection = attrs.transition_direction?.trim().toLowerCase() as XmlTransitionDirection | undefined;
  const rawAdvance = attrs.transition_advance?.trim().toLowerCase() as XmlTransitionAdvance | undefined;
  return {
    type: rawType && transitionTypes.has(rawType) ? rawType : "none",
    direction: rawDirection && transitionDirections.has(rawDirection) ? rawDirection : "l",
    duration: Math.max(120, Math.min(3000, numberOr(attrs.transition_duration, 700))),
    advance: rawAdvance === "after" || rawAdvance === "both" ? rawAdvance : "click",
    delay: Math.max(500, Math.min(60000, numberOr(attrs.transition_delay, 3000))),
  };
};

export const transitionNeedsDirection = (type: XmlTransitionType) =>
  ["push", "wipe", "split", "cover", "uncover", "strips", "zoom"].includes(type);

export const transitionAnimationName = (
  type: XmlTransitionType,
  direction: XmlTransitionDirection,
) => {
  const sideDirection = ["l", "r", "u", "d"].includes(direction) ? direction : "l";
  if (type === "none" || type === "cut") return "none";
  if (type === "uncover") return "none";
  if (type === "fade" || type === "random" || type === "wheel") return "xml-present-fade";
  if (type === "zoom") return `xml-present-zoom-${direction === "out" ? "out" : "in"}`;
  if (type === "split") return `xml-present-split-${direction === "u" || direction === "d" ? "vertical" : "horizontal"}`;
  if (type === "wipe" || type === "strips") return `xml-present-wipe-${sideDirection}`;
  if (type === "circle") return "xml-present-circle";
  if (type === "diamond") return "xml-present-diamond";
  if (type === "plus") return "xml-present-plus";
  return `xml-present-push-${sideDirection}`;
};

export const transitionOutgoingAnimationName = (
  type: XmlTransitionType,
  direction: XmlTransitionDirection,
) => {
  const sideDirection = ["l", "r", "u", "d"].includes(direction) ? direction : "l";
  if (type === "push") return `xml-present-out-push-${sideDirection}`;
  if (type === "uncover") return `xml-present-out-uncover-${sideDirection}`;
  return "none";
};
