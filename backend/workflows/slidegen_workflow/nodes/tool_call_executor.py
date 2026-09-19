# File: backend/workflows/slidegen_workflow/nodes/tool_call_executor.py

"""
Executor / Validator Node for SlideGen Workflow.

Performs rule-based validation on generated tool calls BEFORE rendering.
Checks for: missing required params, None values, type mismatches,
empty strings, invalid color codes, invalid URLs, placeholder text, etc.

If validation passes → state["executor_decision"] = "pass"
If validation fails  → state["executor_decision"] = "fail" + feedback
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional

try:
    from langchain_core.runnables import RunnableConfig
except ImportError:
    RunnableConfig = None  # Allow standalone usage without LangGraph

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT as XML_TOOLS_DICT,
    canonical_tool_name,
    execute_tool as execute_xml_tool,
    execute_tool_plan as execute_xml_tool_plan,
    normalize_tool_arguments,
    normalize_tool_call,
)
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    NoApprovedImageError,
)
from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.utils.xml_transitions import (
    apply_random_slide_transitions,
)
from backend.workflows.slidegen_workflow.utils.xml_fallback import (
    fallback_xml_for_failed_tool as _fallback_xml_for_failed_tool,
)

logger = logging.getLogger(__name__)


def _store_xml_with_random_transitions(state: State, xml_content: str) -> None:
    """Attach one random PowerPoint transition to each generated XML slide."""
    transitioned_xml, transitions = apply_random_slide_transitions(xml_content)
    state["current_xml_content"] = transitioned_xml
    state["current_transitions"] = transitions

    if transitions:
        details = ", ".join(
            f"{item['type']}" + (f"/{item['direction']}" if item.get("direction") else "")
            for item in transitions
        )
        print(f"  Transition ngẫu nhiên: {details}")


def _store_best_available_fallback(
    state: State,
    active_execute_tool,
    tool_call: dict,
    reason: str,
) -> None:
    """Keep the last valid slide when a later regeneration response is broken."""
    previous_xml = str(state.get("last_valid_xml_content") or "").strip()
    previous_call = state.get("last_valid_tool_call") or {}
    if previous_xml and previous_call:
        print("  ⚠️ Reusing the last valid XML after regeneration failed.")
        state["current_tool_call"] = previous_call
        state["current_tool_plan"] = [previous_call]
        state["current_search_history"] = []
        state["current_xml_content"] = previous_xml
        return

    fallback_content = active_execute_tool(
        tool_call,
        source_content=state.get("current_slide_text", ""),
    )
    if not fallback_content:
        fallback_content = _fallback_xml_for_failed_tool(
            tool_call,
            reason,
            source_content=state.get("current_slide_text", ""),
        )
    fallback_call = {"name": "default_fallback", "arguments": {}}
    state["current_tool_call"] = fallback_call
    state["current_tool_plan"] = [fallback_call]
    state["current_search_history"] = []
    _store_xml_with_random_transitions(state, fallback_content)

# ─── Regex patterns ───────────────────────────────────────────────────
HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
RGBA_COLOR_RE = re.compile(r"^rgba?\(\s*\d+")  # loose check for rgba(...)
URL_RE = re.compile(r"^https?://")

# Fields that are typically color parameters
COLOR_FIELD_NAMES = {
    "bg_color", "bg_gradient_to", "text_color", "accent_color", "theme_color",
    "highlight_color", "background_color", "title_color", "subtitle_color",
    "headline_color", "number_color", "main_title_color", "subtitle_color",
    "divider_color", "border_color", "card_bg_color", "panel_bg_color",
    "panel_text_color", "number_bg_color", "number_text_color",
    "accent_bar_color", "line_color", "underline_color", "stripe_color",
    "sky_top_color", "sky_mid_color", "sky_bottom_color",
    "light_text_color", "dark_text_color", "text_color_title",
    "text_color_subtitle", "text_color_top", "icon_color", "shadow_color",
    "decoration_color", "decoration_color_start", "decoration_color_end",
    "bg_left_color", "bg_right_color", "bg_color_left", "bg_color_right",
    "left_bg_color", "right_bg_color", "bg_pattern_color",
    "circle_color", "circle_color_1", "circle_color_2", "circle_color_3",
    "circle_color_4", "curve_color", "grid_dot_color",
    "notebook_bg", "top_circle_color", "bottom_circle_color",
    "accent_line_color", "gradient_color_1", "gradient_color_2",
    "gradient_color_3", "bg_gradient_from", "bg_gradient_to",
    "chart_panel_background_color", "insight_box_background_color",
    "insight_text_color", "main_title_color",
}

# Placeholder / generic text that indicates the model didn't fill real content
PLACEHOLDER_PATTERNS = [
    "lorem ipsum", "your title here", "your text here", "placeholder",
    "default text", "sample text", "title here", "add your",
    "insert text", "type here", "enter text", "[title]", "[content]",
]


def _build_tool_schema_lookup(tools_dict: Dict) -> Dict[str, Dict]:
    """Build a lookup: tool_name -> schema metadata for one output format."""
    lookup = {}
    for _category, tools_list in tools_dict.items():
        for tool in tools_list:
            schema = tool.args  # Pydantic schema dict
            required = set()
            field_info = {}
            for field_name, field_schema in schema.items():
                field_info[field_name] = field_schema
                # Fields without 'default' are required
                if "default" not in field_schema:
                    required.add(field_name)
            lookup[tool.name] = {
                "required_fields": required,
                "field_info": field_info,
                "tool_ref": tool,
            }
    return lookup


def _build_schema_hint(tool_name: str, schema_lookup: Dict) -> str:
    """Return a concise, human-readable schema for *tool_name* to inject into
    retry feedback so the model knows the EXACT valid parameter names."""
    entry = schema_lookup.get(tool_name)
    if not entry:
        return ""
    field_info = entry["field_info"]
    required_fields = entry["required_fields"]
    lines = [
        f"\n--- CORRECT SCHEMA FOR '{tool_name}' ---",
        f"Use ONLY these exact parameter names (do NOT invent others):",
    ]
    for fname, fspec in field_info.items():
        ftype = fspec.get("type", "any")
        req_tag = " (REQUIRED)" if fname in required_fields else " (optional)"
        if ftype == "array":
            item_spec = fspec.get("items", {})
            if item_spec.get("type") == "object":
                item_keys = list(item_spec.get("properties", {}).keys())
                lines.append(f"  - {fname}: List[dict with keys {item_keys}]{req_tag}")
            else:
                lines.append(f"  - {fname}: List[{item_spec.get('type', 'any')}]{req_tag}")
        else:
            lines.append(f"  - {fname}: {ftype}{req_tag}")
    lines.append("--- END SCHEMA ---")
    return "\n".join(lines)


# Module-level cache
_TOOL_SCHEMA_LOOKUPS: Dict[str, Dict] = {}


def _get_schema_lookup(tools_dict: Dict = XML_TOOLS_DICT, cache_key: str = "xml") -> Dict:
    if cache_key not in _TOOL_SCHEMA_LOOKUPS:
        _TOOL_SCHEMA_LOOKUPS[cache_key] = _build_tool_schema_lookup(tools_dict)
    return _TOOL_SCHEMA_LOOKUPS[cache_key]


def _normalize_plan_for_execution(tool_plan: list, tool_lookup: Dict) -> list:
    """Normalize and schema-filter the calls that will actually be executed."""
    if not isinstance(tool_plan, list):
        return tool_plan

    normalized_plan = []
    for call in tool_plan:
        if not isinstance(call, dict):
            normalized_plan.append(call)
            continue
        normalized_call = normalize_tool_call(call)
        tool_name = normalized_call.get("name")
        schema_tool = tool_lookup.get(tool_name)
        if schema_tool is not None:
            known_fields = set(schema_tool.args.keys())
            arguments = normalized_call.get("arguments", {})
            if isinstance(arguments, dict):
                normalized_call["arguments"] = {
                    key: value
                    for key, value in arguments.items()
                    if key in known_fields
                }
        normalized_plan.append(normalized_call)
    return normalized_plan


def validate_tool_call(
    tool_call: dict,
    available_tool_names: List[str] = None,
    tools_dict: Dict = XML_TOOLS_DICT,
    format_name: str = "xml",
) -> Tuple[bool, List[str]]:
    """
    Validate a tool call dict against known schemas.
    
    Returns:
        (is_valid, list_of_error_messages)
    """
    errors: List[str] = []
    
    if not tool_call or not isinstance(tool_call, dict):
        return False, ["Tool call is empty or not a dict."]
    
    # Preserve parser diagnostics before normalizing aliases or arguments.
    if tool_call.get("_parse_error"):
        return False, [tool_call["_parse_error"]]

    raw_tool_name = tool_call.get("name")
    tool_name = canonical_tool_name(raw_tool_name)
    arguments = normalize_tool_arguments(
        tool_name,
        tool_call.get("arguments", {}),
    )
    
    # ── 1. Tool name checks ──────────────────────────────────────────
    if not tool_name or tool_name in ("PARSE_ERROR", "default_fallback"):
        errors.append("MISSING_TOOL_CALL: No valid tool was generated. Pick a valid tool from available tools.")
        return False, errors
    
    if not isinstance(tool_name, str):
        errors.append(f"INVALID_TOOL_NAME_TYPE: 'name' should be string, got {type(tool_name).__name__}.")
        return False, errors
    
    schema_lookup = _get_schema_lookup(tools_dict, format_name)

    # Check if tool exists in available tools (if provided) or in global registry
    available_tool_names = (
        [canonical_tool_name(name) for name in available_tool_names]
        if available_tool_names
        else available_tool_names
    )
    is_known_alias = isinstance(raw_tool_name, str) and raw_tool_name != tool_name
    if available_tool_names and tool_name not in available_tool_names and not is_known_alias:
        errors.append(
            f"UNKNOWN_TOOL: '{tool_name}' is not in the available tools: {available_tool_names}. "
            f"Choose one of the available tools."
        )
        return False, errors
    # Check if available tools is empty
    if tool_name not in schema_lookup:
        errors.append(
            f"UNREGISTERED_TOOL: '{tool_name}' is not a registered tool in the system."
        )
        return False, errors

    # ── 2. Arguments basic check ─────────────────────────────────────
    if not isinstance(arguments, dict):
        errors.append(f"INVALID_ARGUMENTS_TYPE: 'arguments' should be a dict, got {type(arguments).__name__}.")
        return False, errors

    # ── 2b. Auto-strip extra arguments NOT in schema ──────────────────
    # The model sometimes hallucinates parameters not defined in the tool schema.
    # Strip them silently here so we don't burn retry budget on EXTRA_ARGUMENT errors.
    tool_schema_pre = schema_lookup[tool_name]
    known_fields = set(tool_schema_pre["field_info"].keys())
    extra_keys = [k for k in arguments if k not in known_fields]
    if extra_keys:
        print(
            f"  ⚠️ [executor] Auto-stripping hallucinated argument(s) for '{tool_name}': {extra_keys}"
        )
        arguments = {k: v for k, v in arguments.items() if k in known_fields}
        # Propagate stripped arguments back so downstream checks use the clean dict
        tool_call = {**tool_call, "arguments": arguments}


    tool_schema = schema_lookup[tool_name]
    required_fields = tool_schema["required_fields"]
    field_info = tool_schema["field_info"]
    
    # ── 3. Required field checks ─────────────────────────────────────
    for req_field in required_fields:
        if req_field not in arguments:
            errors.append(
                f"MISSING_REQUIRED_PARAM: '{req_field}' is required for tool '{tool_name}' but was not provided."
            )
        elif arguments[req_field] is None:
            errors.append(
                f"NULL_VALUE: '{req_field}' is required but has value None/null."
            )
        elif isinstance(arguments[req_field], str) and arguments[req_field].strip() == "":
            errors.append(
                f"EMPTY_STRING: '{req_field}' is required but has an empty string value."
            )
    
    # ── 4. Type checks for all provided arguments ────────────────────
    for arg_name, arg_value in arguments.items():
        if arg_value is None:
            # None for optional field is OK, skip further checks
            if arg_name not in required_fields:
                continue
            # None for required field already caught above
            continue
        
        if arg_name not in field_info:
            errors.append(
                f"EXTRA_ARGUMENT: '{arg_name}' is not a valid parameter for tool '{tool_name}'. "
                f"Do NOT invent extra parameters! Valid parameters for '{tool_name}' are: {list(field_info.keys())}."
            )
            continue
        
        expected_type = field_info[arg_name].get("type", "")
        
        # Check list types
        if expected_type == "array":
            if not isinstance(arg_value, list):
                errors.append(
                    f"TYPE_MISMATCH: '{arg_name}' should be a list/array, got {type(arg_value).__name__}: {str(arg_value)[:100]}"
                )
            else:
                items_spec = field_info[arg_name].get("items", {})
                expected_item_type = items_spec.get("type", "")
                
                # Deep check list items
                if expected_item_type == "object":
                    for i, item in enumerate(arg_value):
                        if not isinstance(item, dict):
                            errors.append(
                                f"ITEM_TYPE_MISMATCH: '{arg_name}[{i}]' should be an object/dict, got {type(item).__name__}: '{str(item)[:50]}'. "
                                f"Provide a list of structured dictionaries."
                            )
                elif expected_item_type == "string":
                    for i, item in enumerate(arg_value):
                        if not isinstance(item, str):
                            errors.append(
                                f"ITEM_TYPE_MISMATCH: '{arg_name}[{i}]' should be a string, got {type(item).__name__}: '{str(item)[:50]}'."
                            )
        
        # Check string types
        if expected_type == "string" and not isinstance(arg_value, str):
            errors.append(
                f"TYPE_MISMATCH: '{arg_name}' should be a string, got {type(arg_value).__name__}: {str(arg_value)[:100]}"
            )
        
        # Check boolean types
        if expected_type == "boolean" and not isinstance(arg_value, bool):
            errors.append(
                f"TYPE_MISMATCH: '{arg_name}' should be a boolean, got {type(arg_value).__name__}: {str(arg_value)[:50]}"
            )
    
    # ── 5. Color value validation ────────────────────────────────────
    for arg_name, arg_value in arguments.items():
        if arg_name in COLOR_FIELD_NAMES and isinstance(arg_value, str):
            val = arg_value.strip()
            if val and not HEX_COLOR_RE.match(val) and not RGBA_COLOR_RE.match(val):
                errors.append(
                    f"INVALID_COLOR: '{arg_name}' = '{val}' is not a valid hex color code. "
                    f"Use format like '#2563EB' or '#FFF'."
                )
    
    # ── 6. Placeholder / generic text detection ──────────────────────
    text_fields = {"main_title", "subtitle", "title", "headline", "header_text",
                   "content_text", "description_text", "description"}
    for arg_name in text_fields:
        if arg_name in arguments and isinstance(arguments[arg_name], str):
            lower_val = arguments[arg_name].strip().lower()
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern in lower_val:
                    errors.append(
                        f"PLACEHOLDER_TEXT: '{arg_name}' contains placeholder text '{pattern}'. "
                        f"Use actual content from the slide."
                    )
                    break
    
    # ── 7. Empty list check for required list fields ─────────────────
    for arg_name, arg_value in arguments.items():
        if arg_name in required_fields and isinstance(arg_value, list) and len(arg_value) == 0:
            errors.append(
                f"EMPTY_LIST: '{arg_name}' is required but the list is empty."
            )

    # ── 8. Deep schema validation ───────────────────────────────────
    # The checks above intentionally produce concise feedback, but array
    # element types also need validation before StructuredTool invocation.
    # Otherwise a list[str] vs list[dict] mismatch passes here and only fails
    # during execution, where it becomes a generic safe-fallback slide.
    if not errors:
        args_schema = getattr(tool_schema["tool_ref"], "args_schema", None)
        if args_schema is not None:
            try:
                if hasattr(args_schema, "model_validate"):
                    args_schema.model_validate(arguments)
                else:
                    args_schema.parse_obj(arguments)
            except Exception as exc:
                errors.append(
                    f"SCHEMA_VALIDATION_ERROR: arguments for '{tool_name}' do not match "
                    f"the nested tool schema: {str(exc)[:700]}"
                )
    
    # ── 8. Strict Pydantic schema-level validation ───────────────────
    tool_ref = tool_schema.get("tool_ref")
    if tool_ref and hasattr(tool_ref, "args_schema") and tool_ref.args_schema:
        try:
            if hasattr(tool_ref.args_schema, "model_validate"):
                tool_ref.args_schema.model_validate(arguments)
            else:
                tool_ref.args_schema(**arguments)
        except Exception as pydantic_err:
            errors.append(f"SCHEMA_VALIDATION_ERROR for '{tool_name}':\n{pydantic_err}")

    is_valid = len(errors) == 0
    return is_valid, errors


def tool_call_executor(state: State, config: RunnableConfig) -> State:
    """
    Executor / Validator Node.
    
    Validates the tool call generated by slide_generator before passing
    to render_xml. If validation fails, sets executor_decision="fail"
    with feedback so the graph can route back to generate_slide.
    """
    idx = state.get('current_slide_index', 0)
    retry_count = int(state.get('executor_retry_count', 0))
    
    print(f"\n{'='*60}")
    print(f"  🔍 EXECUTOR VALIDATOR — Slide {idx + 1}, Attempt {retry_count + 1}/{EXECUTOR_MAX_RETRIES}")
    print(f"{'='*60}")
    
    tool_call = state.get('current_tool_call')
    
    # Edge case: no tool call at all
    if not tool_call:
        print("  ❌ No tool call found in state.")
        state['executor_decision'] = 'fail'
        state['executor_feedback'] = "CRITICAL: No tool call was generated. You must output a valid function call."
        state['executor_retry_count'] = retry_count + 1
        state['retry_count'] = int(state.get('retry_count', 0)) + 1
        if state['executor_retry_count'] >= EXECUTOR_MAX_RETRIES:
            _store_best_available_fallback(
                state,
                execute_xml_tool,
                {"name": "PARSE_ERROR", "arguments": {}},
                state['executor_feedback'],
            )
        return state
    
    configurable = config.get("configurable", {}) if config else {}
    requested_output_format = str(
        configurable.get("output_format")
        or state.get("output_format")
        or "xml"
    ).lower()
    if requested_output_format != "xml":
        raise ValueError("This workflow is XML-only; output_format must be 'xml'.")
    active_tools_dict = XML_TOOLS_DICT
    active_execute_tool = execute_xml_tool
    active_execute_tool_plan = execute_xml_tool_plan

    tool_name = tool_call.get('name', '???')
    print(f"  Tool: {tool_name}")
    print(f"  Args keys: {list(tool_call.get('arguments', {}).keys())}")
    
    # Get list of available tool names from candidate_tools in state (if available)
    candidate_tools = state.get('candidate_tools', [])
    available_names = [t.name for t in candidate_tools] if candidate_tools else None
    
    # Run validation
    is_valid, errors = validate_tool_call(
        tool_call,
        available_names,
        tools_dict=active_tools_dict,
        format_name="xml",
    )
    
    if is_valid:
        print(f"  ✅ PASS — Tool call is valid!")
        state['executor_decision'] = 'pass'
        state['executor_feedback'] = ''
        state['executor_retry_count'] = 0
        tool_lookup = {
            tool.name: tool
            for tools in active_tools_dict.values()
            for tool in tools
        }
        tool_plan = _normalize_plan_for_execution(
            state.get("current_tool_plan") or [tool_call],
            tool_lookup,
        )
        if isinstance(tool_plan, list) and tool_plan and isinstance(tool_plan[0], dict):
            tool_call = tool_plan[0]
            state["current_tool_call"] = tool_call
            state["current_tool_plan"] = tool_plan
        try:
            slide_options = state.get("slide_options") or {}
            current_index = int(state.get("current_slide_index", -1))
            approved_images = list(state.get("current_approved_images") or [])
            if not approved_images:
                approved_images = [
                    image
                    for image in slide_options.get("approved_image_assignments", []) or []
                    if isinstance(image, dict)
                    and int(image.get("slide_index", -1)) == current_index
                ]
            slide_content, final_tool_call, search_history = active_execute_tool_plan(
                tool_plan,
                tool_lookup=tool_lookup,
                source_content=state.get("current_slide_text", ""),
                approved_images=approved_images,
                asset_dir=configurable.get("output_folder"),
            )
            if not slide_content:
                raise ValueError(f"Tool '{tool_name}' returned empty XML content.")
        except NoApprovedImageError as e:
            # A verifier rejection is a quality decision, not a rendering
            # failure. Keep the same slide content but ask the generator to
            # call again with a layout that has no image slots.
            print(f"  IMAGE VERIFICATION: {e}")
            state["force_no_image_layout"] = True
            state["executor_decision"] = "fail"
            state["executor_feedback"] = (
                f"{e}\n"
                "Regenerate this slide with an XML layout that has no image "
                "parameters. Do not request or invent an image on this retry. "
                "Preserve the slide's content, hierarchy, and visual intent "
                "using typography, shapes, tables, or charts instead."
            )
            state["executor_retry_count"] = retry_count + 1
            state["retry_count"] = int(state.get("retry_count", 0)) + 1
            if state["executor_retry_count"] >= EXECUTOR_MAX_RETRIES:
                fallback_call = {"name": "default_fallback", "arguments": {}}
                state["current_tool_call"] = fallback_call
                state["current_tool_plan"] = [fallback_call]
                state["current_search_history"] = []
                fallback_content = _fallback_xml_for_failed_tool(
                    tool_call,
                    str(e),
                    source_content=state.get("current_slide_text", ""),
                )
                _store_xml_with_random_transitions(state, fallback_content)
                state["last_valid_tool_call"] = fallback_call
                state["last_valid_xml_content"] = state["current_xml_content"]
            return state
        except Exception as e:
            print(f"  FAIL - Tool plan execution failed: {e}")
            state['executor_decision'] = 'fail'
            state['executor_feedback'] = (
                "EXECUTOR EXECUTION FAILED:\n"
                f"- {e}\n\n"
                "Fix ALL errors above and regenerate a valid tool call matching the parameter schema exactly.\n"
                "Return exactly one valid slide XML tool. Approved image assets are injected by the executor; do not emit image-search calls."
            )
            state['executor_retry_count'] = retry_count + 1
            state['retry_count'] = int(state.get('retry_count', 0)) + 1
            if state['executor_retry_count'] >= EXECUTOR_MAX_RETRIES:
                _store_best_available_fallback(
                    state,
                    active_execute_tool,
                    tool_call,
                    str(e),
                )
            return state

        for key in list(state.keys()):
            if isinstance(key, str) and key.startswith("current_image_tool_call_"):
                state.pop(key, None)
        for i, call in enumerate(search_history, start=1):
            state[f"current_image_tool_call_{i}"] = call

        state['current_tool_call'] = final_tool_call
        state['current_search_history'] = search_history
        _store_xml_with_random_transitions(state, slide_content)
        state['last_valid_tool_call'] = final_tool_call
        state['last_valid_xml_content'] = state.get('current_xml_content', '')
    else:
        error_report = "\n".join(f"  • {e}" for e in errors)
        print(f"  ❌ FAIL — {len(errors)} error(s) found:")
        print(error_report)

        # Determine if schema hint would help the model fix the errors.
        # Inject full parameter schema whenever there are missing/extra/schema errors
        # so the model knows the EXACT correct argument names on the next retry.
        schema_hint = ""
        needs_schema = any(
            err.startswith(("MISSING_REQUIRED_PARAM", "EXTRA_ARGUMENT", "SCHEMA_VALIDATION_ERROR"))
            for err in errors
        )
        if needs_schema:
            schema_lookup = _get_schema_lookup(active_tools_dict, "xml")
            schema_hint = _build_schema_hint(tool_name, schema_lookup)

        state['executor_decision'] = 'fail'
        state['executor_feedback'] = (
            f"EXECUTOR VALIDATION FAILED ({len(errors)} errors):\n"
            + "\n".join(f"- {e}" for e in errors)
            + schema_hint
            + "\n\nFix ALL errors above and regenerate the tool call using ONLY the parameter names listed in the schema above."
        )
        state['executor_retry_count'] = retry_count + 1
        state['retry_count'] = int(state.get('retry_count', 0)) + 1
        if state['executor_retry_count'] >= EXECUTOR_MAX_RETRIES:
            _store_best_available_fallback(
                state,
                active_execute_tool,
                tool_call,
                "; ".join(errors),
            )
    
    return state
