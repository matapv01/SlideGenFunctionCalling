import { Fragment, useMemo, type ReactNode } from "react";
import { convertLatexToMarkup } from "mathlive";
import "mathlive/static.css";

type MarkdownBlock =
  | { type: "paragraph"; lines: string[] }
  | { type: "heading"; level: number; text: string }
  | { type: "unordered-list"; items: string[] }
  | { type: "ordered-list"; items: string[] }
  | { type: "quote"; lines: string[] }
  | { type: "code"; language: string; lines: string[] }
  | { type: "math"; value: string }
  | { type: "rule" };

const blockStart = (line: string) => {
  return (
    /^\s{0,3}#{1,6}\s+/.test(line)
    || /^\s{0,3}[-*+]\s+/.test(line)
    || /^\s{0,3}\d+[.)]\s+/.test(line)
    || /^\s{0,3}>\s?/.test(line)
    || /^\s*```/.test(line)
    || /^\s*(?:\$\$|\\\[|\\begin\{(?:equation\*?|align\*?|gather\*?)\})\s*$/.test(line)
    || /^\s*(?:---+|___+|\*\s*\*\s*\*+)\s*$/.test(line)
  );
};

function parseBlocks(value: string): MarkdownBlock[] {
  const lines = String(value || "").replace(/\r\n?/g, "\n").split("\n");
  const blocks: MarkdownBlock[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const codeStart = line.match(/^\s*```\s*([\w-]*)\s*$/);
    if (codeStart) {
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      blocks.push({ type: "code", language: codeStart[1] || "", lines: codeLines });
      continue;
    }

    const displayMathStart = line.match(/^\s*(\$\$|\\\[)\s*$/);
    if (displayMathStart) {
      const closingToken = displayMathStart[1] === "$$" ? "$$" : "\\]";
      const mathLines: string[] = [];
      index += 1;
      while (index < lines.length && lines[index].trim() !== closingToken) {
        mathLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      blocks.push({ type: "math", value: mathLines.join("\n").trim() });
      continue;
    }

    const equationStart = line.match(/^\s*\\begin\{(equation\*?|align\*?|gather\*?)\}\s*$/);
    if (equationStart) {
      const closingToken = `\\end{${equationStart[1]}}`;
      const mathLines: string[] = [];
      index += 1;
      while (index < lines.length && lines[index].trim() !== closingToken) {
        mathLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      blocks.push({ type: "math", value: mathLines.join("\n").trim() });
      continue;
    }

    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (heading) {
      blocks.push({ type: "heading", level: heading[1].length, text: heading[2] });
      index += 1;
      continue;
    }

    if (/^\s*(?:---+|___+|\*\s*\*\s*\*+)\s*$/.test(line)) {
      blocks.push({ type: "rule" });
      index += 1;
      continue;
    }

    const unordered = line.match(/^\s{0,3}[-*+]\s+(.+)$/);
    if (unordered) {
      const items = [unordered[1]];
      index += 1;
      while (index < lines.length) {
        const next = lines[index].match(/^\s{0,3}[-*+]\s+(.+)$/);
        if (next) {
          items.push(next[1]);
          index += 1;
          continue;
        }
        if (lines[index].trim() && /^\s{2,}\S/.test(lines[index])) {
          items[items.length - 1] += ` ${lines[index].trim()}`;
          index += 1;
          continue;
        }
        break;
      }
      blocks.push({ type: "unordered-list", items });
      continue;
    }

    const ordered = line.match(/^\s{0,3}\d+[.)]\s+(.+)$/);
    if (ordered) {
      const items = [ordered[1]];
      index += 1;
      while (index < lines.length) {
        const next = lines[index].match(/^\s{0,3}\d+[.)]\s+(.+)$/);
        if (next) {
          items.push(next[1]);
          index += 1;
          continue;
        }
        if (lines[index].trim() && /^\s{2,}\S/.test(lines[index])) {
          items[items.length - 1] += ` ${lines[index].trim()}`;
          index += 1;
          continue;
        }
        break;
      }
      blocks.push({ type: "ordered-list", items });
      continue;
    }

    const quote = line.match(/^\s{0,3}>\s?(.*)$/);
    if (quote) {
      const quoteLines = [quote[1]];
      index += 1;
      while (index < lines.length) {
        const next = lines[index].match(/^\s{0,3}>\s?(.*)$/);
        if (!next) break;
        quoteLines.push(next[1]);
        index += 1;
      }
      blocks.push({ type: "quote", lines: quoteLines });
      continue;
    }

    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && lines[index].trim() && !blockStart(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push({ type: "paragraph", lines: paragraph });
  }

  return blocks;
}

const inlineToken = /(`[^`\n]+`|\$\$[^$\n]+\$\$|\$[^$\n]+\$|\\\([^\n]+?\\\)|\*\*[^*\n]+\*\*|__[^_\n]+__|~~[^~\n]+~~|\[[^\]\n]+\]\(https?:\/\/[^\s)]+\)|\[(?:Source|Nguồn)\s+\d+\]|\*[^*\n]+\*|_[^_\n]+_)/g;

type CitationClickHandler = (sourceIndex: number) => void;

function LatexMath({ value, display = false }: { value: string; display?: boolean }) {
  const latex = value.trim();
  const markup = useMemo(() => {
    if (!latex) return "";
    try {
      return convertLatexToMarkup(latex);
    } catch {
      return "";
    }
  }, [latex]);

  if (!markup) {
    return <code className={display ? "chat-math-fallback is-block" : "chat-math-fallback"}>{latex}</code>;
  }

  return (
    <span
      className={display ? "chat-math chat-math-block" : "chat-math chat-math-inline"}
      role="math"
      aria-label={latex}
      dangerouslySetInnerHTML={{ __html: markup }}
    />
  );
}

function mathTokenValue(token: string) {
  if (token.startsWith("$$") && token.endsWith("$$")) return token.slice(2, -2);
  if (token.startsWith("$") && token.endsWith("$")) return token.slice(1, -1);
  if (token.startsWith("\\(") && token.endsWith("\\)")) return token.slice(2, -2);
  return token;
}

function renderInline(value: string, onCitationClick?: CitationClickHandler): ReactNode[] {
  const result: ReactNode[] = [];
  let lastIndex = 0;
  let tokenIndex = 0;

  for (const match of value.matchAll(inlineToken)) {
    const token = match[0];
    const index = match.index ?? 0;
    if (index > lastIndex) {
      result.push(<Fragment key={`text-${tokenIndex++}`}>{value.slice(lastIndex, index)}</Fragment>);
    }

    if (token.startsWith("`") && token.endsWith("`")) {
      result.push(<code key={`code-${tokenIndex++}`}>{token.slice(1, -1)}</code>);
    } else if (
      (token.startsWith("$") && token.endsWith("$"))
      || (token.startsWith("\\(") && token.endsWith("\\)"))
    ) {
      result.push(<LatexMath key={`math-${tokenIndex++}`} value={mathTokenValue(token)} />);
    } else if ((token.startsWith("**") && token.endsWith("**")) || (token.startsWith("__") && token.endsWith("__"))) {
      result.push(<strong key={`strong-${tokenIndex++}`}>{renderInline(token.slice(2, -2), onCitationClick)}</strong>);
    } else if (token.startsWith("~~") && token.endsWith("~~")) {
      result.push(<del key={`del-${tokenIndex++}`}>{token.slice(2, -2)}</del>);
    } else if (token.startsWith("[") && token.includes("](") && token.endsWith(")")) {
      const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/);
      if (link) {
        result.push(
          <a key={`link-${tokenIndex++}`} href={link[2]} target="_blank" rel="noreferrer">
            {link[1]}
          </a>,
        );
      } else {
        result.push(<Fragment key={`token-${tokenIndex++}`}>{token}</Fragment>);
      }
    } else if (/^\[(?:Source|Nguồn)\s+\d+\]$/.test(token)) {
      const citation = token.match(/^\[(?:Source|Nguồn)\s+(\d+)\]$/);
      const sourceIndex = citation ? Number(citation[1]) : 0;
      const label = token.slice(1, -1);
      result.push(
        onCitationClick && sourceIndex > 0 ? (
          <button
            className="chat-citation"
            key={`citation-${tokenIndex++}`}
            type="button"
            onClick={() => onCitationClick(sourceIndex)}
            aria-label={`Open ${label}`}
          >
            {label}
          </button>
        ) : (
          <span className="chat-citation" key={`citation-${tokenIndex++}`}>{label}</span>
        ),
      );
    } else if (token.startsWith("*") || token.startsWith("_")) {
      result.push(<em key={`em-${tokenIndex++}`}>{renderInline(token.slice(1, -1), onCitationClick)}</em>);
    } else {
      result.push(<Fragment key={`token-${tokenIndex++}`}>{token}</Fragment>);
    }
    lastIndex = index + token.length;
  }

  if (lastIndex < value.length) {
    result.push(<Fragment key={`text-${tokenIndex}`}>{value.slice(lastIndex)}</Fragment>);
  }
  return result;
}

function renderTextLines(lines: string[], onCitationClick?: CitationClickHandler) {
  return lines.map((line, index) => (
    <Fragment key={`line-${index}`}>
      {index > 0 && <br />}
      {renderInline(line, onCitationClick)}
    </Fragment>
  ));
}

export default function ChatMarkdown({
  content,
  onCitationClick,
}: {
  content: string;
  onCitationClick?: CitationClickHandler;
}) {
  return (
    <div className="chat-markdown">
      {parseBlocks(content).map((block, index) => {
        const key = `block-${index}`;
        if (block.type === "heading") {
          const Heading = `h${Math.min(block.level, 4)}` as keyof JSX.IntrinsicElements;
          return <Heading key={key}>{renderInline(block.text, onCitationClick)}</Heading>;
        }
        if (block.type === "unordered-list") {
          return <ul key={key}>{block.items.map((item, itemIndex) => <li key={`${key}-${itemIndex}`}>{renderInline(item, onCitationClick)}</li>)}</ul>;
        }
        if (block.type === "ordered-list") {
          return <ol key={key}>{block.items.map((item, itemIndex) => <li key={`${key}-${itemIndex}`}>{renderInline(item, onCitationClick)}</li>)}</ol>;
        }
        if (block.type === "quote") return <blockquote key={key}>{renderTextLines(block.lines, onCitationClick)}</blockquote>;
        if (block.type === "code") return <pre key={key}><code>{block.lines.join("\n")}</code></pre>;
        if (block.type === "math") return <LatexMath key={key} value={block.value} display />;
        if (block.type === "rule") return <hr key={key} />;
        return <p key={key}>{renderInline(block.lines.join(" "), onCitationClick)}</p>;
      })}
    </div>
  );
}
