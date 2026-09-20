export interface XmlSlideElement {
  id: string;
  tag: string;
  attrs: Record<string, string>;
  text: string;
  children: XmlSlideElement[];
  /** Text before the first child; used to preserve mixed text/math XML. */
  leadingText?: string;
  /** Text after this child and before the next sibling. */
  tail?: string;
}

export interface XmlSlidePage {
  id: string;
  attrs: Record<string, string>;
  elements: XmlSlideElement[];
}

export interface XmlSlideDocument {
  presentationAttrs: Record<string, string>;
  width: number;
  height: number;
  slides: XmlSlidePage[];
}

const numberOr = (value: string | undefined, fallback: number) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

// XML slide generators historically used escaped HTML break markers inside
// textbox text (for example ``A&lt;br&gt;B``). They are data, not DOM elements,
// so normalize them at the parser boundary before layout/rendering.
export const normalizeXmlTextBreaks = (value: string) =>
  value.replace(/<br\s*\/?>/gi, "\n");

const attributesOf = (element: Element) => {
  const attrs: Record<string, string> = {};
  for (const attr of Array.from(element.attributes)) {
    attrs[attr.name] = attr.value;
  }
  return attrs;
};

const directElementChildren = (element: Element) =>
  Array.from(element.childNodes).filter(
    (node): node is Element => node.nodeType === Node.ELEMENT_NODE,
  );

const INLINE_LATEX_RE = /(?<!\\)(?:\$\$(.*?)\$\$|\$([^$\n]+?)\$|\\\((.*?)\\\)|\\\[(.*?)\\\])/gs;

export const normalizeLatexFormula = (value: string) =>
  value.replace(/\\_/g, "_");

const inlineMathSegments = (value: string) => {
  const segments: Array<{ type: "text" | "math"; value: string }> = [];
  let cursor = 0;
  for (const match of value.matchAll(INLINE_LATEX_RE)) {
    const formula = [match[1], match[2], match[3], match[4]]
      .find((candidate) => candidate !== undefined)
      ?.trim() || "";
    if (!formula) continue;
    const start = match.index ?? 0;
    if (start > cursor) segments.push({ type: "text", value: value.slice(cursor, start) });
    segments.push({ type: "math", value: normalizeLatexFormula(formula) });
    cursor = start + match[0].length;
  }
  if (cursor < value.length) segments.push({ type: "text", value: value.slice(cursor) });
  return segments;
};

const materializeInlineMathInXml = (document: XMLDocument) => {
  const textboxes = Array.from(document.querySelectorAll("textbox, text"));
  textboxes.forEach((textbox) => {
    Array.from(textbox.querySelectorAll("math-field")).forEach((field) => {
      field.textContent = normalizeLatexFormula(field.textContent || "");
    });
    Array.from(textbox.childNodes).forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE || node.nodeType === Node.CDATA_SECTION_NODE) {
        const value = node.nodeValue || "";
        const segments = inlineMathSegments(value);
        if (!segments.some((segment) => segment.type === "math")) return;
        const fragment = document.createDocumentFragment();
        segments.forEach((segment) => {
          if (segment.type === "math") {
            const field = document.createElement("math-field");
            field.textContent = segment.value;
            fragment.appendChild(field);
          } else if (segment.value) {
            fragment.appendChild(document.createTextNode(segment.value));
          }
        });
        node.replaceWith(fragment);
        return;
      }

      if (!(node instanceof Element) || node.tagName.toLowerCase() !== "run") return;
      const raw = node.textContent || "";
      const segments = inlineMathSegments(raw);
      if (!segments.some((segment) => segment.type === "math")) return;
      const fragment = document.createDocumentFragment();
      segments.forEach((segment) => {
        if (segment.type === "math") {
          const field = document.createElement("math-field");
          field.textContent = segment.value;
          fragment.appendChild(field);
          return;
        }
        if (!segment.value) return;
        const run = node.cloneNode(false) as Element;
        run.textContent = segment.value;
        fragment.appendChild(run);
      });
      node.replaceWith(fragment);
    });
  });
};

const parseElement = (element: Element, index: number): XmlSlideElement => {
  const attrs = attributesOf(element);
  const children: XmlSlideElement[] = [];
  let leadingText = "";
  for (const node of Array.from(element.childNodes)) {
    if (node.nodeType === Node.ELEMENT_NODE) {
      children.push(parseElement(node as Element, children.length));
      continue;
    }
    if (node.nodeType !== Node.TEXT_NODE && node.nodeType !== Node.CDATA_SECTION_NODE) continue;
    const value = normalizeXmlTextBreaks(node.nodeValue ?? "");
    if (!children.length) leadingText += value;
    else children[children.length - 1].tail = `${children[children.length - 1].tail || ""}${value}`;
  }
  const directTextValue = normalizeXmlTextBreaks(leadingText);
  const directText = element.tagName.toLowerCase() === "run"
    ? directTextValue
    : directTextValue.trim();
  const isRichTextbox = ["textbox", "text"].includes(element.tagName.toLowerCase())
    && children.some((child) => child.tag.toLowerCase() === "run");
  const text = isRichTextbox
    ? children
      .filter((child) => child.tag.toLowerCase() === "run")
      .map((child) => child.text)
      .join("")
    : directText;

  return {
    id: attrs.id || `xml-element-${index + 1}`,
    tag: element.tagName,
    attrs,
    text,
    children,
    leadingText,
  };
};

export const parseXmlSlide = (xml: string): XmlSlideDocument => {
  const parsed = new DOMParser().parseFromString(xml, "application/xml");
  const parserError = parsed.getElementsByTagName("parsererror")[0];
  if (parserError) {
    throw new Error(parserError.textContent || "Dữ liệu trình chiếu không hợp lệ");
  }

  // Older/generated XML can contain Markdown-style `$...$` math instead of
  // the canonical math-field node. Normalize it before the editor builds its
  // element model so stored slides render consistently too.
  materializeInlineMathInXml(parsed);

  const presentation = parsed.documentElement;
  if (!presentation || presentation.tagName !== "presentation") {
    throw new Error("Dữ liệu trình chiếu không hợp lệ");
  }

  const slides = directElementChildren(presentation).filter((child) => child.tagName === "slide");
  if (!slides.length) {
    throw new Error("Bản trình chiếu không có slide nào");
  }

  const presentationAttrs = attributesOf(presentation);
  const width = numberOr(presentationAttrs.width, 1600);
  const height = numberOr(presentationAttrs.height, 900);

  return {
    presentationAttrs,
    width,
    height,
    slides: slides.map((slide, slideIndex) => ({
      id: attributesOf(slide).id || `xml-slide-${slideIndex + 1}`,
      attrs: attributesOf(slide),
      elements: directElementChildren(slide).map((element, index) => parseElement(element, index)),
    })),
  };
};

const escapeXml = (value: string) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

const serializeAttrs = (attrs: Record<string, string>) =>
  Object.entries(attrs)
    .map(([key, value]) => ` ${key}="${escapeXml(String(value))}"`)
    .join("");

const serializeElement = (element: XmlSlideElement, depth: number) => {
  const indent = "  ".repeat(depth);
  const attrs = serializeAttrs(element.attrs);
  const children = element.children;
  const hasRichRuns = ["textbox", "text"].includes(element.tag.toLowerCase())
    && children.some((child) => child.tag.toLowerCase() === "run");

  if (!children.length && !element.text) {
    return `${indent}<${element.tag}${attrs} />`;
  }

  if (!children.length) {
    return `${indent}<${element.tag}${attrs}>${escapeXml(element.text)}</${element.tag}>`;
  }

  const childXml = children
    .map((child) => `${serializeElement(child, depth + 1)}${child.tail ? escapeXml(child.tail) : ""}`)
    .join("\n");
  // ``element.text`` mirrors the concatenated run text for editor/layout use.
  // Rich text must be serialized only through its children to avoid duplication.
  const text = !hasRichRuns
    ? escapeXml(element.leadingText ?? element.text)
    : "";
  return `${indent}<${element.tag}${attrs}>${text}\n${childXml}\n${indent}</${element.tag}>`;
};

export const serializeXmlSlide = (document: XmlSlideDocument) => {
  const presentationAttrs = serializeAttrs({
    ...document.presentationAttrs,
    width: String(document.width),
    height: String(document.height),
  });
  const slides = document.slides.map((slide) => {
    const slideAttrs = serializeAttrs(slide.attrs);
    const elements = slide.elements.map((element) => serializeElement(element, 2)).join("\n");
    return [
      `  <slide${slideAttrs}>`,
      elements,
      "  </slide>",
    ].filter(Boolean).join("\n");
  }).join("\n");

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    `<presentation${presentationAttrs}>`,
    slides,
    "</presentation>",
  ].filter(Boolean).join("\n");
};

export const updateXmlElement = (
  document: XmlSlideDocument,
  id: string,
  update: Partial<Pick<XmlSlideElement, "text" | "attrs" | "children">>,
  slideIndex = 0,
): XmlSlideDocument => ({
  ...document,
  slides: document.slides.map((slide, index) => index !== slideIndex ? slide : ({
    ...slide,
    elements: slide.elements.map((element) =>
      element.id === id
          ? {
            ...element,
            ...(update.text !== undefined ? { text: update.text } : {}),
            ...(update.children !== undefined ? { children: update.children } : {}),
            ...(update.text !== undefined && update.children === undefined && element.children.some(
              (child) => child.tag.toLowerCase() === "run",
            ) ? { children: [] } : {}),
            ...(update.attrs ? { attrs: { ...element.attrs, ...update.attrs } } : {}),
          }
        : element,
    ),
  })),
});

export const defaultXmlSlide = `<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900">
  <slide background="#F4F4F4">
    <image src="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=85&amp;w=1600&amp;auto=format&amp;fit=crop" x="515" y="0" width="1085" height="900" />
    <polygon points="0,0 965,0 595,900 0,900" fill="#23242B" line_color="none" />
    <polygon points="787.00,145.00 835.00,145.00 725.00,708.00 773.00,708.00" fill="#98F033" line_color="none" />
    <textbox x="78" y="210" width="620" height="290" font="Arial" size="64" color="#98F033" align="left" vertical_align="top">THIS IS YOUR PRESENTATION TITLE</textbox>
  </slide>
</presentation>`;
