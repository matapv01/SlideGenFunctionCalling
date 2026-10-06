"""RL-facing adapter for the XML-only SlideGen pipeline.

Compatibility stays here instead of re-introducing the removed HTML API into
backend, which remains aligned with minh_dep.
"""

from __future__ import annotations

import json

from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT,
    execute_tool as _execute_xml_tool,
)
from backend.workflows.slidegen_workflow.utils.prompts import (
    HUMAN_PROMPT_TEMPLATE,
    MATH_EQUATION_RULES,
    XML_CONTENT_PROMPT,
)


def execute_tool(tool_call: dict) -> str:
    """Strictly validate one RL tool call before passing it to the permissive executor.

    The production workflow accepts legacy/coercible arguments for compatibility.
    GRPO previews and rewards must instead render only arguments that satisfy the
    selected tool's declared schema; otherwise a malformed JSON string can be
    silently converted into a one-item list and look like an accepted rollout.
    """
    if not isinstance(tool_call, dict) or set(tool_call) != {"name", "arguments"}:
        raise ValueError("RL tool call must contain exactly name and arguments")

    name = tool_call.get("name")
    arguments = tool_call.get("arguments")
    if not isinstance(name, str) or not isinstance(arguments, dict):
        raise ValueError("RL tool call name and arguments have invalid types")

    tool = next(
        (
            candidate
            for category_tools in TOOLS_DICT.values()
            for candidate in category_tools
            if candidate.name == name
        ),
        None,
    )
    if tool is None:
        raise ValueError(f"Unknown RL XML tool: {name}")

    schema = getattr(tool, "args_schema", None)
    fields = getattr(schema, "model_fields", None)
    if schema is None or fields is None or set(arguments) - set(fields):
        raise ValueError(f"Arguments do not match the schema for {name}")
    try:
        validated_arguments = schema.model_validate(arguments).model_dump(
            exclude_unset=True
        )
    except Exception as exc:
        raise ValueError(f"Invalid arguments for {name}: {exc}") from exc

    return _execute_xml_tool(
        {"name": name, "arguments": validated_arguments},
        raise_on_error=True,
    )


_DOM_METRICS_SCRIPT = r"""() => {
  const canvas = document.querySelector('[data-xml-slide-canvas="true"]');
  if (!canvas) throw new Error("XML slide canvas was not found in frontend preview");
  const canvasRect = canvas.getBoundingClientRect();
  const logicalWidth = canvas.offsetWidth || canvasRect.width || 1;
  const logicalHeight = canvas.offsetHeight || canvasRect.height || 1;
  const scaleX = canvasRect.width / logicalWidth || 1;
  const scaleY = canvasRect.height / logicalHeight || 1;
  const toX = value => value / scaleX;
  const toY = value => value / scaleY;
  const tolerance = 1.5;
  const union = rects => rects.length ? rects.reduce((result, rect) => ({
    left: Math.min(result.left, rect.left), top: Math.min(result.top, rect.top),
    right: Math.max(result.right, rect.right), bottom: Math.max(result.bottom, rect.bottom),
  }), {left: rects[0].left, top: rects[0].top,
      right: rects[0].right, bottom: rects[0].bottom}) : null;
  const lineCount = rects => {
    const tops = [];
    for (const rect of rects) {
      if (!tops.some(top => Math.abs(top - rect.top) <= 2)) tops.push(rect.top);
    }
    return tops.length;
  };
  const boxes = Array.from(document.querySelectorAll('[data-xml-textbox="true"]'))
    .map(box => {
      const content = box.querySelector('[data-xml-text-content="true"]');
      if (!content || !content.textContent?.trim()) return null;
      const rect = box.getBoundingClientRect();
      const textRects = [];
      const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();
      while (node) {
        if (node.textContent?.trim()) {
          const range = document.createRange();
          range.selectNodeContents(node);
          textRects.push(...Array.from(range.getClientRects()));
        }
        node = walker.nextNode();
      }
      const visibleRects = textRects.filter(item => item.width > 0 && item.height > 0);
      const textRect = union(visibleRects);
      // Line boxes are ~1.2x the font size; inset them to approximate visible glyph ink.
      const inkRects = visibleRects.map(item => {
        const inset = item.height * 0.15;
        return {left: item.left, right: item.right, width: item.width,
                top: item.top + inset, bottom: item.bottom - inset, height: item.height - 2 * inset};
      });
      const collisionRects = [
        ...inkRects,
        ...Array.from(content.querySelectorAll('math-field, math-span'))
          .map(field => field.getBoundingClientRect())
          .filter(rect => rect.width > 0 && rect.height > 0),
      ].map(item => ({
        x: toX(item.left - canvasRect.left),
        y: toY(item.top - canvasRect.top),
        width: toX(item.width),
        height: toY(item.height),
      }));
      const reasons = [];
      if (rect.left < canvasRect.left - tolerance || rect.top < canvasRect.top - tolerance ||
          rect.right > canvasRect.right + tolerance || rect.bottom > canvasRect.bottom + tolerance) {
        reasons.push('slide_boundary');
      }
      if (textRect && (textRect.left < rect.left - tolerance || textRect.right > rect.right + tolerance)) {
        reasons.push('text_width');
      }
      // Flag only when a line loses more than a third of its box, i.e. glyphs are visibly clipped.
      if (visibleRects.some(item => Math.max(rect.top - item.top, item.bottom - rect.bottom) >
                                    Math.max(tolerance, item.height * 0.35))) {
        reasons.push('text_height');
      }
      const maxLinesValue = box.getAttribute('data-xml-max-lines');
      const maxLines = maxLinesValue ? Number(maxLinesValue) : null;
      const lines = lineCount(visibleRects);
      if (maxLines && lines > maxLines) reasons.push('max_lines');
      return {
        id: box.getAttribute('data-xml-element-id') || 'textbox',
        text: content.innerText || content.textContent || '',
        x: toX(rect.left - canvasRect.left), y: toY(rect.top - canvasRect.top),
        width: toX(rect.width), height: toY(rect.height), reasons,
        collision_rects: collisionRects,
      };
    }).filter(Boolean);
  const issues = boxes.flatMap(box => box.reasons.map(type => ({type, textbox: box.id})));
  const accessibleText = Array.from(
    document.querySelectorAll('[role="img"][aria-label], math-span[aria-label]')
  ).map(node => node.getAttribute('aria-label') || '').filter(Boolean);
  const imageStatus = Array.from(canvas.querySelectorAll('img')).map(image => ({
    src: image.currentSrc || image.src,
    loaded: image.complete && image.naturalWidth > 0,
  }));
  return {
    visible_text: [...boxes.map(box => box.text).filter(Boolean), ...accessibleText].join(' '),
    issues,
    image_status: imageStatus,
    collision_boxes: boxes.map(box => ({id: box.id, rects: box.collision_rects})),
  };
}"""


def _attach_bbox_collision_issues(metrics: dict) -> dict:
    """Score visible glyph/math bounds, not the frontend's expanded hitboxes."""
    boxes = metrics.pop("collision_boxes", [])
    issues = metrics.setdefault("issues", [])

    def visibly_overlaps(first: dict, second: dict) -> bool:
        width = min(
            first["x"] + first["width"], second["x"] + second["width"]
        ) - max(first["x"], second["x"])
        height = min(
            first["y"] + first["height"], second["y"] + second["height"]
        ) - max(first["y"], second["y"])
        smaller_area = min(
            first["width"] * first["height"],
            second["width"] * second["height"],
        )
        return (
            width > 1.5
            and height > 1.5
            and smaller_area > 0
            and width * height / smaller_area > 0.05
        )

    for index, first in enumerate(boxes):
        for second in boxes[index + 1 :]:
            if any(
                visibly_overlaps(first_rect, second_rect)
                for first_rect in first.get("rects", [])
                for second_rect in second.get("rects", [])
            ):
                issues.append({
                    "type": "bbox_collision",
                    "textbox": first.get("id", "textbox"),
                    "other": second.get("id", "textbox"),
                })
    return metrics


def render_xml_batch_to_png(
    xml_contents: list[str],
    output_paths: list[str],
    max_concurrency: int = 4,
) -> list[dict]:
    """Render and measure slides through the same frontend route used by BE."""
    if len(xml_contents) != len(output_paths):
        raise ValueError("xml_contents and output_paths must have equal length")
    if not xml_contents:
        return []

    from rl.render_runtime import render_batch
    results = render_batch(xml_contents, output_paths, _DOM_METRICS_SCRIPT, max_concurrency)
    return [_attach_bbox_collision_issues(result) for result in results]


def render_xml_to_png(xml_content: str, output_path: str) -> None:
    """Render one slide using the production frontend XML preview."""
    render_xml_batch_to_png([xml_content], [output_path], max_concurrency=1)


def format_tool_for_qwen(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args_schema.model_json_schema(),
        },
    }


QWEN_GENERATOR_SYSTEM_PROMPT = (
    MATH_EQUATION_RULES
    + "\n\n"
    + XML_CONTENT_PROMPT
    + """

RL SERIALIZATION CONTRACT:
- Return exactly one serialized Qwen native call to the supplied XML tool, using
  <tool_call><function=TOOL_NAME> ... </function></tool_call>.
- Inside it, emit one <parameter=FIELD_NAME>VALUE</parameter> for each argument.
  Use the exact tool name and parameter names from the supplied schema.
- For a scalar text parameter, VALUE is the text itself. For an array or object
  parameter, VALUE must be valid JSON of the declared type; escape quotes inside
  JSON strings. Never stringify an array/object as ordinary prose or leave its
  inner quotation marks unescaped. When slide text quotes a phrase, prefer the
  typographic marks “ ” over a raw " so the JSON stays valid; never put a
  backslash before an apostrophe (\' is not valid JSON).
- Write every visible slide text in the same language as SLIDE CONTENT, even
  when the slide plan, topic, or design instruction is written in English.
- Do not add prose, markdown, image-search calls, or raw XML. Emit one complete
  call only; do not append a second tool call or end-of-turn text.
"""
)


def build_generator_human_prompt(
    *,
    deck_style_contract: str,
    slide_topic: str,
    slide_plan: str,
    design_instruction: str,
    slide_content: str,
    assigned_tool_name: str,
    slide_index: int,
    deck_length: int,
    image_mode: str = "none",
    approved_images: list[dict] | None = None,
) -> str:
    """Mirror production prompt semantics; only the tool transport differs."""
    return HUMAN_PROMPT_TEMPLATE.format(
        slide_context_map="Offline GRPO corpus sample.",
        deck_style_contract=deck_style_contract,
        slide_topic=slide_topic,
        presentation_instruction="",
        image_mode=image_mode,
        visual_layout_request=design_instruction,
        approved_images=(
            json.dumps(approved_images or [], ensure_ascii=False)
            if image_mode == "semantic"
            else "None — use a layout with no image fields."
        ),
        recent_tools=(
            f"Use only the assigned XML layout tool: {assigned_tool_name}"
        ),
        slide_plan=slide_plan,
        design_instruction=design_instruction,
        slide_index=slide_index + 1,
        length_slide_chunks=deck_length,
        slide_content=slide_content,
        previous_function_call="None — this is the first attempt for this slide.",
        previous_evaluation="None — this is the first attempt for this slide.",
    ) + f"""

RL OUTPUT FORMAT:
Return one Qwen native call to the assigned tool `{assigned_tool_name}`. Use
<tool_call><function={assigned_tool_name}> with one parameter tag per schema
field, then </function></tool_call>. List and object parameter values must be
valid JSON of the schema-declared type, with quotes inside JSON strings escaped.
Return no prose, second call, or trailing text.
"""
