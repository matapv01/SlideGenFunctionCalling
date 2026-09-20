import { describe, expect, it } from "vitest";

import {
  normalizeXmlTextBreaks,
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
  it("turns escaped br markers into real line breaks", () => {
    const document = parseXmlSlide(`
      <presentation width="1600" height="900">
        <slide>
          <textbox id="body" x="0" y="0" width="500" height="200">A&lt;br&gt;B&lt;br/&gt;C</textbox>
        </slide>
      </presentation>
    `);
    const textbox = document.slides[0].elements[0];

    expect(normalizeXmlTextBreaks("A<br>B")).toBe("A\nB");
    expect(textbox.text).toBe("A\nB\nC");
    expect(serializeXmlSlide(document)).not.toContain("&lt;br&gt;");
  });

  it("parses run text for layout while preserving run styles", () => {
    const document = parseXmlSlide(richXml);
    const textbox = document.slides[0].elements[0];

    expect(textbox.text).toBe("AI giúp tăng 40%");
    expect(textbox.children).toHaveLength(2);
    expect(textbox.children[1].attrs.highlight).toBeUndefined();
    expect(textbox.children[1].attrs.color).toBe("#2563EB");
  });

  it("materializes all supported inline LaTeX delimiters", () => {
    const document = parseXmlSlide(`
      <presentation width="1600" height="900">
        <slide>
          <textbox id="formula" x="0" y="0" width="500" height="200">
            Probability $P(A)$ and $$\\frac{a}{b}$$ plus \\(x^2\\) and \\[\\alpha+\\beta\\]
          </textbox>
        </slide>
      </presentation>
    `);
    const textbox = document.slides[0].elements[0];

    expect(textbox.children.map((child) => child.tag)).toEqual([
      "math-field",
      "math-field",
      "math-field",
      "math-field",
    ]);
    expect(textbox.children.map((child) => child.text)).toEqual([
      "P(A)",
      "\\frac{a}{b}",
      "x^2",
      "\\alpha+\\beta",
    ]);
    expect(textbox.leadingText?.trim()).toBe("Probability");
  });

  it("repairs Markdown-escaped subscripts inside math", () => {
    const document = parseXmlSlide(`
      <presentation width="1600" height="900">
        <slide>
          <textbox id="formula" x="0" y="0" width="500" height="200">
            Mean $\\bar{x}=\\frac{1}{n}\\sum\\_{i=1}^{n}x\\_i$
          </textbox>
        </slide>
      </presentation>
    `);
    const textbox = document.slides[0].elements[0];

    expect(textbox.children[0].text).toBe(
      "\\bar{x}=\\frac{1}{n}\\sum_{i=1}^{n}x_i",
    );
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

  it("round-trips chart, table, and connector element attributes", () => {
    const document = parseXmlSlide(`
      <presentation width="1600" height="900">
        <slide>
          <barchart x="10" y="20" width="400" height="240" data="10,20,30" />
          <line x1="30" y1="40" x2="300" y2="160" arrow_end="true" />
          <table x="80" y="100" width="600" height="300" data="Metric|Q1;Revenue|120" />
        </slide>
      </presentation>
    `);
    const [chart, connector, table] = document.slides[0].elements;

    expect(chart.tag).toBe("barchart");
    expect(chart.attrs.data).toBe("10,20,30");
    expect(connector.attrs.arrow_end).toBe("true");
    expect(table.tag).toBe("table");
    expect(serializeXmlSlide(document)).toContain("data=\"Metric|Q1;Revenue|120\"");
  });
});
