import { describe, expect, it } from "vitest";

import {
  parseXmlSlide,
  serializeXmlSlide,
  updateXmlElement,
} from "@/lib/xmlSlide";


const richXml = `<?xml version="1.0" encoding="UTF-8"?>
<presentation width="1600" height="900">
  <slide background="#FFFFFF">
    <textbox id="headline" x="100" y="100" width="900" height="100" color="#111111">
      <run>AI giúp </run>
      <run emphasis="highlight" color="#2563EB" bold="true">tăng 40%</run>
    </textbox>
  </slide>
</presentation>`;


describe("XML slide rich text", () => {
  it("parses run text for layout while preserving run styles", () => {
    const document = parseXmlSlide(richXml);
    const textbox = document.slides[0].elements[0];

    expect(textbox.text).toBe("AI giúp tăng 40%");
    expect(textbox.children).toHaveLength(2);
    expect(textbox.children[1].attrs.highlight).toBeUndefined();
    expect(textbox.children[1].attrs.color).toBe("#2563EB");
  });

  it("round-trips rich runs without duplicating visible textbox text", () => {
    const serialized = serializeXmlSlide(parseXmlSlide(richXml));
    const reparsed = parseXmlSlide(serialized);
    const textbox = reparsed.slides[0].elements[0];

    expect(textbox.text).toBe("AI giúp tăng 40%");
    expect(textbox.children).toHaveLength(2);
    expect((serialized.match(/AI giúp/g) || [])).toHaveLength(1);
    expect((serialized.match(/tăng 40%/g) || [])).toHaveLength(1);
  });

  it("flattens rich runs when the user edits textbox text", () => {
    const document = parseXmlSlide(richXml);
    const updated = updateXmlElement(
      document,
      "headline",
      { text: "Edited plain text" },
    );
    const textbox = updated.slides[0].elements[0];

    expect(textbox.text).toBe("Edited plain text");
    expect(textbox.children).toEqual([]);
    expect(serializeXmlSlide(updated)).toContain(
      "<textbox id=\"headline\"",
    );
    expect(serializeXmlSlide(updated)).toContain(
      ">Edited plain text</textbox>",
    );
  });
});
