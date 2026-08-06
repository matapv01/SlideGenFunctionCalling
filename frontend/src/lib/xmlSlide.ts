export interface XmlSlideElement {
  id: string;
  tag: string;
  attrs: Record<string, string>;
  text: string;
  children: XmlSlideElement[];
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

const parseElement = (element: Element, index: number): XmlSlideElement => {
  const attrs = attributesOf(element);
  const text = Array.from(element.childNodes)
    .filter((node) => node.nodeType === Node.TEXT_NODE || node.nodeType === Node.CDATA_SECTION_NODE)
    .map((node) => node.nodeValue ?? "")
    .join("")
    .trim();

  return {
    id: attrs.id || `xml-element-${index + 1}`,
    tag: element.tagName,
    attrs,
    text,
    children: directElementChildren(element).map((child, childIndex) =>
      parseElement(child, childIndex),
    ),
  };
};

export const parseXmlSlide = (xml: string): XmlSlideDocument => {
  const parsed = new DOMParser().parseFromString(xml, "application/xml");
  const parserError = parsed.getElementsByTagName("parsererror")[0];
  if (parserError) {
    throw new Error(parserError.textContent || "Dữ liệu trình chiếu không hợp lệ");
  }

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

  if (!children.length && !element.text) {
    return `${indent}<${element.tag}${attrs} />`;
  }

  if (!children.length) {
    return `${indent}<${element.tag}${attrs}>${escapeXml(element.text)}</${element.tag}>`;
  }

  const childXml = children.map((child) => serializeElement(child, depth + 1)).join("\n");
  const text = element.text ? escapeXml(element.text) : "";
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
  update: Partial<Pick<XmlSlideElement, "text" | "attrs">>,
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
