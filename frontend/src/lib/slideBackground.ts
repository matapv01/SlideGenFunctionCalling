type SlideDesignSettings = {
  backgroundColor?: string;
  backgroundImage?: string;
  defs?: string;
  [key: string]: unknown;
};

type SlideBackground = {
  backgroundColor?: string;
  backgroundImage?: string;
};

const WHITE_LIKE_VALUES = new Set([
  '#fff',
  '#ffffff',
  'white',
  'rgb(255,255,255)',
  'rgb(255, 255, 255)',
  'rgba(255,255,255,1)',
  'rgba(255, 255, 255, 1)',
]);

const COLOR_TOKEN_REGEX = /(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\)|var\(--[^)]+\)|\b(?:transparent|white|black|red|green|blue|yellow|orange|gray|grey|brown|cyan|magenta)\b)/i;

const BACKGROUND_SELECTORS = [
  'body',
  '.slide-bg-wrapper',
  '.slide-container',
  '.content-wrapper',
  '.outer-wrapper',
  'html',
];

export const parseSlideDesignSettings = (value: unknown): SlideDesignSettings | null => {
  if (!value) return null;
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed === 'object' ? (parsed as SlideDesignSettings) : null;
    } catch {
      return null;
    }
  }
  return typeof value === 'object' ? (value as SlideDesignSettings) : null;
};

const parseStyleText = (styleText: string): Record<string, string> => {
  const result: Record<string, string> = {};
  for (const entry of styleText.split(';')) {
    const trimmed = entry.trim();
    if (!trimmed) continue;
    const separatorIndex = trimmed.indexOf(':');
    if (separatorIndex <= 0) continue;
    const key = trimmed.slice(0, separatorIndex).trim().toLowerCase();
    const value = trimmed.slice(separatorIndex + 1).trim();
    if (!key || !value) continue;
    result[key] = value.replace(/\s*!important\s*$/i, '').trim();
  }
  return result;
};

const extractFromStyleText = (styleText: string): SlideBackground => {
  const declarations = parseStyleText(styleText);
  let backgroundColor = declarations['background-color'];
  let backgroundImage = declarations['background-image'];

  const shorthand = declarations.background;
  if (shorthand) {
    if (!backgroundColor) {
      const colorMatch = shorthand.match(COLOR_TOKEN_REGEX);
      if (colorMatch) {
        backgroundColor = colorMatch[1];
      }
    }
    if (!backgroundImage && /(url\(|gradient\()/i.test(shorthand)) {
      backgroundImage = shorthand;
    }
  }

  if (backgroundImage && /^none$/i.test(backgroundImage)) {
    backgroundImage = undefined;
  }

  return { backgroundColor, backgroundImage };
};

const selectorMatches = (selector: string, target: string): boolean => {
  const normalized = selector.trim().toLowerCase();
  const normalizedTarget = target.toLowerCase();
  if (normalizedTarget.startsWith('.')) {
    return normalized.includes(normalizedTarget);
  }
  return new RegExp(`\\b${normalizedTarget}\\b`).test(normalized);
};

const getHtmlBackground = (htmlContent?: string): SlideBackground => {
  if (!htmlContent) return {};

  let doc: Document;
  try {
    doc = new DOMParser().parseFromString(htmlContent, 'text/html');
  } catch {
    return {};
  }

  let colorFromCss: string | undefined;
  let imageFromCss: string | undefined;
  const styleBlocks = Array.from(doc.querySelectorAll('style')).map((styleNode) => styleNode.textContent || '');

  for (const cssText of styleBlocks) {
    const ruleRegex = /([^{}]+)\{([^{}]+)\}/g;
    let match: RegExpExecArray | null;
    while ((match = ruleRegex.exec(cssText)) !== null) {
      const selectorList = match[1];
      const declarations = match[2];
      const selectors = selectorList.split(',').map((selector) => selector.trim());
      const matched = BACKGROUND_SELECTORS.some((target) =>
        selectors.some((selector) => selectorMatches(selector, target))
      );
      if (!matched) continue;

      const extracted = extractFromStyleText(declarations);
      if (extracted.backgroundColor) colorFromCss = extracted.backgroundColor;
      if (extracted.backgroundImage) imageFromCss = extracted.backgroundImage;
    }
  }

  let colorFromInline: string | undefined;
  let imageFromInline: string | undefined;
  for (const selector of BACKGROUND_SELECTORS) {
    const target = selector === 'body'
      ? doc.body
      : selector === 'html'
      ? doc.documentElement
      : doc.querySelector(selector);
    if (!target) continue;
    const style = target.getAttribute('style');
    if (!style) continue;
    const extracted = extractFromStyleText(style);
    if (extracted.backgroundColor) colorFromInline = extracted.backgroundColor;
    if (extracted.backgroundImage) imageFromInline = extracted.backgroundImage;
  }

  return {
    backgroundColor: colorFromInline || colorFromCss,
    backgroundImage: imageFromInline || imageFromCss,
  };
};

const isWhiteLikeBackground = (value?: string): boolean => {
  if (!value) return false;
  return WHITE_LIKE_VALUES.has(value.trim().toLowerCase());
};

export const resolveSlideBackground = (
  designSettings: unknown,
  htmlContent?: string,
  defaultBackgroundColor = '#ffffff'
): SlideBackground => {
  const parsedSettings = parseSlideDesignSettings(designSettings);
  const htmlFallback = getHtmlBackground(htmlContent);

  const designBackgroundColor = parsedSettings?.backgroundColor;
  const designBackgroundImage = parsedSettings?.backgroundImage;
  const htmlBackgroundColor = htmlFallback.backgroundColor;
  const htmlBackgroundImage = htmlFallback.backgroundImage;

  // Streaming preview renders html_content directly; when design_settings carries a stale
  // default white value, prefer html-derived background to avoid whitewashing slides.
  const shouldPreferHtmlBackground =
    isWhiteLikeBackground(designBackgroundColor) &&
    (!!htmlBackgroundImage || (!!htmlBackgroundColor && !isWhiteLikeBackground(htmlBackgroundColor)));

  const backgroundColor = shouldPreferHtmlBackground
    ? (htmlBackgroundColor || designBackgroundColor || defaultBackgroundColor)
    : (designBackgroundColor || htmlBackgroundColor || defaultBackgroundColor);

  const backgroundImage = designBackgroundImage || htmlBackgroundImage;

  return { backgroundColor, backgroundImage };
};
