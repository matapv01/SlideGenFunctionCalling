import { CANVAS_HEIGHT, CANVAS_WIDTH } from "./constants";
import type { SlideElement } from "./types";

export type CanvasAlignment =
  | "left"
  | "horizontal-center"
  | "right"
  | "top"
  | "vertical-center"
  | "bottom";

export type ElementStyleUpdate = Partial<SlideElement> & { _filter?: string };

export interface ElementStylePreset {
  id: string;
  swatch: string;
  updates: ElementStyleUpdate;
}

const roundPosition = (value: number) => Math.round(value * 100) / 100;

export const getCanvasAlignmentUpdates = (
  element: Pick<SlideElement, "width" | "height">,
  alignment: CanvasAlignment,
): Partial<SlideElement> => {
  switch (alignment) {
    case "left":
      return { x: 0 };
    case "horizontal-center":
      return { x: roundPosition((CANVAS_WIDTH - element.width) / 2) };
    case "right":
      return { x: roundPosition(CANVAS_WIDTH - element.width) };
    case "top":
      return { y: 0 };
    case "vertical-center":
      return { y: roundPosition((CANVAS_HEIGHT - element.height) / 2) };
    case "bottom":
      return { y: roundPosition(CANVAS_HEIGHT - element.height) };
  }
};

export const buildElementFilter = (
  element: Pick<SlideElement, "blur" | "brightness" | "saturation">,
) => {
  const blur = element.blur ?? 0;
  const brightness = element.brightness ?? 100;
  const saturation = element.saturation ?? 100;

  return [
    blur > 0 ? `blur(${blur}px)` : "",
    brightness !== 100 ? `brightness(${brightness}%)` : "",
    saturation !== 100 ? `saturate(${saturation}%)` : "",
  ].filter(Boolean).join(" ") || "none";
};

export const getElementStylePresets = (type: SlideElement["type"]): ElementStylePreset[] => {
  if (type === "text") {
    return [
      {
        id: "text-modern",
        swatch: "#1d4ed8",
        updates: {
          color: "#172554",
          fontFamily: "'Be Vietnam Pro', sans-serif",
          fontWeight: "800",
          fontSize: 64,
          lineHeight: "1.15",
          letterSpacing: "-1px",
        },
      },
      {
        id: "text-editorial",
        swatch: "#9a3412",
        updates: {
          color: "#431407",
          fontFamily: "'Playfair Display', serif",
          fontWeight: "700",
          fontSize: 58,
          lineHeight: "1.2",
          letterSpacing: "0px",
        },
      },
      {
        id: "text-clean",
        swatch: "#0f172a",
        updates: {
          color: "#0f172a",
          fontFamily: "'Inter', sans-serif",
          fontWeight: "500",
          fontSize: 36,
          lineHeight: "1.45",
          letterSpacing: "0px",
        },
      },
    ];
  }

  if (type === "image" || type === "video") {
    return [
      {
        id: "media-soft",
        swatch: "#dbeafe",
        updates: {
          borderRadius: 28,
          shadow: "0 20px 45px rgba(15, 23, 42, 0.22)",
          saturation: 100,
          brightness: 100,
        },
      },
      {
        id: "media-mono",
        swatch: "#64748b",
        updates: {
          borderRadius: 0,
          shadow: "none",
          saturation: 0,
          brightness: 105,
        },
      },
      {
        id: "media-vivid",
        swatch: "#f97316",
        updates: {
          borderRadius: 16,
          shadow: "0 12px 30px rgba(249, 115, 22, 0.2)",
          saturation: 140,
          brightness: 105,
        },
      },
    ];
  }

  if (type === "equation" || type === "icon") {
    return [
      { id: "accent-blue", swatch: "#2563eb", updates: { color: "#2563eb", fontSize: 38 } },
      { id: "accent-violet", swatch: "#7c3aed", updates: { color: "#7c3aed", fontSize: 38 } },
      { id: "accent-ink", swatch: "#0f172a", updates: { color: "#0f172a", fontSize: 38 } },
    ];
  }

  return [
    {
      id: "shape-ocean",
      swatch: "#2563eb",
      updates: {
        fillColor: "#2563eb",
        strokeColor: "#1d4ed8",
        strokeWidth: 0,
        strokeStyle: "none",
        borderRadius: 24,
        shadow: "0 14px 32px rgba(37, 99, 235, 0.24)",
      },
    },
    {
      id: "shape-coral",
      swatch: "#f97316",
      updates: {
        fillColor: "#f97316",
        strokeColor: "#ea580c",
        strokeWidth: 0,
        strokeStyle: "none",
        borderRadius: 32,
        shadow: "0 14px 32px rgba(249, 115, 22, 0.22)",
      },
    },
    {
      id: "shape-outline",
      swatch: "#f8fafc",
      updates: {
        fillColor: "#f8fafc",
        strokeColor: "#0f172a",
        strokeWidth: 3,
        strokeStyle: "solid",
        borderRadius: 12,
        shadow: "none",
      },
    },
  ];
};
