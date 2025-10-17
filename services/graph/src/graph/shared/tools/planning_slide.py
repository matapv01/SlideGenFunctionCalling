from __future__ import annotations


from typing import Any, Dict


TOOL_CATEGORIES = [
    'INTRO_TOOLS',
    'TRANSITION_TOOLS',
    'CONTENT_TOOLS',
    'TEAM_TOOLS',
    'THANK_YOU_TOOLS',
]


def planning_slide_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a slide plan with 'thought' and 'action'.

    Expected payload keys: slide_content (str), slide_context_map (str)
    """
    content = (payload or {}).get('slide_content', '') or ''
    context = (payload or {}).get('slide_context_map', '') or ''

    text = (content + '\n' + context).strip().lower()

    # Simple heuristics to pick a tool category
    if any(k in text for k in ('thank', 'thanks', 'conclusion', 'wrap up', 'closing')):
        action = 'THANK_YOU_TOOLS'
    elif any(k in text for k in ('team', 'members', 'who', 'contributors')):
        action = 'TEAM_TOOLS'
    elif any(k in text for k in ('transition', 'next', 'then', 'after')):
        action = 'TRANSITION_TOOLS'
    elif len(content) < 80:
        action = 'INTRO_TOOLS'
    else:
        action = 'CONTENT_TOOLS'

    thought = f"Plan for slide: choose {action}. Short summary: {content[:200]}"

    return {
        'thought': thought,
        'action': action,
    }


# Tool metadata
TOOL_ID = "planning_slide"
TOOL_NAME = "planning_slide"
TOOL_DESC = "Create a slide plan (thought + action)"
