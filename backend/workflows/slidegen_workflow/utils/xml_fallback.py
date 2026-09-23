"""Small deterministic XML fallback used at the workflow safety boundary."""

from __future__ import annotations

import re
from xml.sax.saxutils import escape


def fallback_xml_for_failed_tool(
    tool_call: dict,
    reason: str,
    source_content: str = "",
) -> str:
    """Return a readable no-image slide when a tool cannot be regenerated."""
    del tool_call, reason
    raw_lines = [
        re.sub(r"^\s*[-+*]\s*", "", line).strip()
        for line in str(source_content or "").splitlines()
        if line.strip()
    ]
    if raw_lines and raw_lines[0].isdigit():
        raw_lines.pop(0)
    title = raw_lines.pop(0) if raw_lines else "Nội dung slide"
    body_lines = []
    for line in raw_lines:
        if line == title or line in body_lines:
            continue
        body_lines.append(line)
    body = "\n".join(body_lines[:10]) or "Nội dung đang được tổng hợp."
    safe_title = escape(title[:180])
    safe_body = escape(body[:1400])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#F8FAFC">
    <shape type="rect" x="0" y="0" width="1600" height="900" fill="#F8FAFC" line_color="none" />
    <shape type="rect" x="120" y="118" width="12" height="126" fill="#0D9488" line_color="none" />
    <textbox x="170" y="110" width="1310" height="150" font="Arial" size="42" bold="true" color="#0F172A" align="left" vertical_align="middle" overflow="shrink">{safe_title}</textbox>
    <textbox x="170" y="300" width="1260" height="470" font="Arial" size="24" color="#334155" align="left" vertical_align="top" overflow="shrink">{safe_body}</textbox>
  </slide>
</presentation>'''
