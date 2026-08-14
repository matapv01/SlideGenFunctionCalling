import { describe, expect, it } from "vitest";
import {
  buildElementFilter,
  getCanvasAlignmentUpdates,
  getElementStylePresets,
} from "@/pages/SlideEditor/editorActions";

describe("slide editor actions", () => {
  it("aligns an element against all slide edges and centers", () => {
    const element = { width: 400, height: 200 };

    expect(getCanvasAlignmentUpdates(element, "left")).toEqual({ x: 0 });
    expect(getCanvasAlignmentUpdates(element, "horizontal-center")).toEqual({ x: 760 });
    expect(getCanvasAlignmentUpdates(element, "right")).toEqual({ x: 1520 });
    expect(getCanvasAlignmentUpdates(element, "top")).toEqual({ y: 0 });
    expect(getCanvasAlignmentUpdates(element, "vertical-center")).toEqual({ y: 440 });
    expect(getCanvasAlignmentUpdates(element, "bottom")).toEqual({ y: 880 });
  });

  it("builds a combined CSS filter and resets to none", () => {
    expect(buildElementFilter({ blur: 2, brightness: 110, saturation: 80 }))
      .toBe("blur(2px) brightness(110%) saturate(80%)");
    expect(buildElementFilter({ blur: 0, brightness: 100, saturation: 100 })).toBe("none");
  });

  it("returns presets suited to each element family", () => {
    expect(getElementStylePresets("text").map(preset => preset.id)).toContain("text-modern");
    expect(getElementStylePresets("image").map(preset => preset.id)).toContain("media-mono");
    expect(getElementStylePresets("shape").map(preset => preset.id)).toContain("shape-outline");
  });
});
