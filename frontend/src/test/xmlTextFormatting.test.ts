import { describe, expect, it } from "vitest";
import type { XmlSlideElement } from "@/lib/xmlSlide";
import { applyXmlTextFormatting, replaceXmlTextContent } from "@/lib/xmlTextFormatting";

const textbox = (text = "Hello world"): XmlSlideElement => ({
  id: "title",
  tag: "textbox",
  attrs: { color: "#111111", size: "30" },
  text,
  children: [],
});

describe("XML inline text formatting", () => {
  it("formats only the selected substring", () => {
    const runs = applyXmlTextFormatting(textbox(), { start: 6, end: 11 }, { color: "#ef4444", highlight: "#fef08a", bold: true });
    expect(runs.map((run) => run.text)).toEqual(["Hello ", "world"]);
    expect(runs[0].attrs.color).toBeUndefined();
    expect(runs[1].attrs).toMatchObject({ color: "#ef4444", highlight: "#fef08a", bold: "true", font_weight: "700" });
  });

  it("toggles style based on the selected runs", () => {
    const source = textbox();
    source.children = applyXmlTextFormatting(source, { start: 0, end: 5 }, { bold: true });
    source.text = "Hello world";
    const toggled = applyXmlTextFormatting(source, { start: 0, end: 5 }, { bold: "toggle" });
    expect(toggled[0].attrs.bold).toBe("false");
  });

  it("keeps formatting when edited text is replaced", () => {
    const source = textbox();
    source.children = applyXmlTextFormatting(source, { start: 6, end: 11 }, { italic: true });
    const next = replaceXmlTextContent({ ...source, text: "Hello world" }, "Hello Canva");
    expect(next.map((run) => run.text)).toEqual(["Hello ", "Canva"]);
    expect(next[1].attrs.italic).toBe("true");
  });
});
