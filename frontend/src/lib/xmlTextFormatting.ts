import type { XmlSlideElement } from "./xmlSlide";

export interface XmlTextSelection {
  start: number;
  end: number;
  /** Current editable text, when the selection came from a live contentEditable. */
  text?: string;
}

export type XmlTextFormatValue = boolean | "toggle";

export interface XmlTextFormat {
  color?: string;
  highlight?: string;
  bold?: XmlTextFormatValue;
  italic?: XmlTextFormatValue;
  underline?: XmlTextFormatValue;
  strike?: XmlTextFormatValue;
}

const isRun = (element: XmlSlideElement) => element.tag.toLowerCase() === "run";

const formatKeys: Array<keyof Pick<XmlTextFormat, "bold" | "italic" | "underline" | "strike">> = [
  "bold",
  "italic",
  "underline",
  "strike",
];

const formatIsActive = (
  attrs: Record<string, string>,
  inherited: Record<string, string>,
  key: keyof Pick<XmlTextFormat, "bold" | "italic" | "underline" | "strike">,
) => {
  const value = attrs[key] ?? inherited[key];
  if (key === "bold") {
    return value === "true" || Number(value) >= 600;
  }
  return value === "true";
};

const applyFormatAttrs = (
  attrs: Record<string, string>,
  format: XmlTextFormat,
  toggledValues: Partial<Record<keyof XmlTextFormat, boolean>>,
) => {
  const next = { ...attrs };
  if (format.color !== undefined) next.color = format.color;
  if (format.highlight !== undefined) next.highlight = format.highlight;

  formatKeys.forEach((key) => {
    const value = format[key];
    if (value === undefined) return;
    const enabled = value === "toggle" ? Boolean(toggledValues[key]) : value;
    next[key] = String(enabled);
    if (key === "bold") next.font_weight = enabled ? "700" : "400";
  });
  return next;
};

const makeRun = (element: XmlSlideElement, text: string, attrs: Record<string, string>, index: number): XmlSlideElement => ({
  id: `${element.id}-run-${index}`,
  tag: "run",
  attrs,
  text,
  children: [],
});

interface TextSegment {
  text: string;
  attrs: Record<string, string>;
  start: number;
  end: number;
}

const sourceSegments = (element: XmlSlideElement): TextSegment[] => {
  const runs = element.children.filter(isRun);
  if (!runs.length) {
    const text = element.text || "";
    return [{ text, attrs: {}, start: 0, end: text.length }];
  }

  let offset = 0;
  const fullText = element.text || "";
  return runs.map((run, index) => {
    const oldLength = (run.text || "").length;
    const text = index === runs.length - 1
      ? fullText.slice(offset)
      : fullText.slice(offset, offset + oldLength);
    const segment = { text, attrs: { ...run.attrs }, start: offset, end: offset + text.length };
    offset += text.length;
    return segment;
  });
};

export const applyXmlTextFormatting = (
  element: XmlSlideElement,
  selection: XmlTextSelection,
  format: XmlTextFormat,
) => {
  const textLength = (element.text || "").length;
  const start = Math.max(0, Math.min(textLength, Math.min(selection.start, selection.end)));
  const end = Math.max(start, Math.min(textLength, Math.max(selection.start, selection.end)));
  if (start === end || textLength === 0) return element.children;

  const segments = sourceSegments(element);
  const selectedSegments = segments.filter((segment) => segment.end > start && segment.start < end);
  const toggledValues: Partial<Record<keyof XmlTextFormat, boolean>> = {};
  formatKeys.forEach((key) => {
    if (format[key] !== "toggle") return;
    const allActive = selectedSegments.length > 0 && selectedSegments.every((segment) => (
      formatIsActive(segment.attrs, element.attrs, key)
    ));
    toggledValues[key] = !allActive;
  });

  const nextRuns: XmlSlideElement[] = [];
  let runIndex = 0;
  segments.forEach((segment) => {
    if (!segment.text) return;
    const boundaries = [0];
    if (start > segment.start && start < segment.end) boundaries.push(start - segment.start);
    if (end > segment.start && end < segment.end) boundaries.push(end - segment.start);
    boundaries.push(segment.text.length);

    boundaries.forEach((boundary, index) => {
      if (index === boundaries.length - 1) return;
      const chunkStart = boundaries[index];
      const chunkEnd = boundaries[index + 1];
      const absoluteStart = segment.start + chunkStart;
      const absoluteEnd = segment.start + chunkEnd;
      const selected = absoluteStart < end && absoluteEnd > start;
      const attrs = selected
        ? applyFormatAttrs(segment.attrs, format, toggledValues)
        : { ...segment.attrs };
      nextRuns.push(makeRun(element, segment.text.slice(chunkStart, chunkEnd), attrs, runIndex));
      runIndex += 1;
    });
  });
  return nextRuns;
};

/** Keep existing per-run formatting when the user edits the text itself. */
export const replaceXmlTextContent = (element: XmlSlideElement, text: string) => {
  const runs = element.children.filter(isRun);
  if (!runs.length) return [];

  let cursor = 0;
  return runs.map((run, index) => {
    const oldLength = (run.text || "").length;
    const isLast = index === runs.length - 1;
    const nextText = isLast ? text.slice(cursor) : text.slice(cursor, cursor + oldLength);
    cursor += oldLength;
    return makeRun(element, nextText, { ...run.attrs }, index);
  }).filter((run) => run.text.length > 0);
};
