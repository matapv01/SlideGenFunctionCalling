from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable

from backend.application.services.language_service import (
    detect_language,
    language_instruction,
)
from backend.application.services.project_service import ProjectService
from backend.application.services.slidegen_workflow_service import SlideGenWorkflowService
from backend.application.services.slide_intent_service import MIN_SLIDE_COUNT
from backend.config import resolve_chatbot_generation_config
from backend.domain.entities.chat import ChatSession
from backend.domain.ports.llm_provider import LLMProvider
from backend.workflows.slidegen_workflow.utils.markdown_parser import (
    parse_markdown_to_hierarchical_json,
)


@dataclass(frozen=True)
class SlideGenerationResult:
    project_id: int
    project_name: str
    script: str
    slide_count: int


class SlideGenerationService:
    """Canonical chat-driven orchestration for creating a slide project.

    The input can be a free-form request plus retrieved document context. The
    service turns that request into one canonical slide script, converts the
    script to slide chunks, and delegates rendering to the existing XML slide
    workflow. DOCX is only an optional preprocessing source and the manual
    editor is a separate workflow.
    """

    _SCRIPT_SYSTEM_PROMPT = (
        "You are the Slidegenius presentation script editor. "
        "Write a factually grounded slide script in the user's language. "
        "Use only the supplied source context for document claims. "
        "Return Markdown only: one # heading for the deck title and one ## "
        "heading per slide, followed by concise slide content. Do not include "
        "JSON, code fences, notes, or explanations outside the script."
    )

    def __init__(
        self,
        llm_provider: LLMProvider,
        slide_workflow: SlideGenWorkflowService,
        project_service: ProjectService,
    ) -> None:
        self.llm_provider = llm_provider
        self.slide_workflow = slide_workflow
        self.project_service = project_service

    async def generate(
        self,
        *,
        session: ChatSession,
        prompt: str,
        retrieved_context: str,
        model_name: str | None,
        effort: str | None,
        target_slide_count: int,
        callback: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> SlideGenerationResult:
        """Generate one deck from the chat request and optional RAG context."""
        target_slide_count = int(target_slide_count)
        if target_slide_count < MIN_SLIDE_COUNT:
            raise ValueError(
                f"Bộ slide cần có ít nhất {MIN_SLIDE_COUNT} slide."
            )
        generation_config = resolve_chatbot_generation_config(model_name, effort)
        self._emit_event(
            callback,
            "status",
            {
                "stage": "script",
                "title": "Preparing script",
                "description": "Writing the presentation script from your brief...",
                "message": "Preparing script",
            },
        )
        presentation_instruction = await self._generate_presentation_instruction(
            prompt=prompt,
            target_slide_count=target_slide_count,
            generation_config=generation_config,
        )
        script = await self._generate_script(
            prompt=prompt,
            retrieved_context=retrieved_context,
            target_slide_count=target_slide_count,
            generation_config=generation_config,
        )
        script = self._clean_script(script)
        title, structure = parse_markdown_to_hierarchical_json(script)
        chunks = self._to_slide_chunks(title, structure, script)
        if not chunks:
            raise ValueError("Không tạo được kịch bản slide từ yêu cầu này")
        if len(chunks) != target_slide_count:
            self._emit_event(
                callback,
                "status",
                {
                    "stage": "script",
                    "title": "Adjusting script",
                    "description": (
                        f"Aligning the outline to exactly {target_slide_count} slides..."
                    ),
                    "message": "Adjusting slide count",
                },
            )
            script = await self._generate_script(
                prompt=prompt,
                retrieved_context=retrieved_context,
                target_slide_count=target_slide_count,
                generation_config=generation_config,
                draft=script,
            )
            script = self._clean_script(script)
            title, structure = parse_markdown_to_hierarchical_json(script)
            chunks = self._to_slide_chunks(title, structure, script)
        if len(chunks) != target_slide_count:
            raise ValueError(
                f"Không thể tạo đúng {target_slide_count} slide từ yêu cầu hiện tại. "
                "Vui lòng thử lại hoặc chọn số lượng slide khác."
            )

        project_name = self._safe_project_name(title or prompt)
        slide_options = {
            "output_format": "xml",
            "enable_transition_slides": True,
            "enable_thank_you_slide": True,
            "target_slide_count": target_slide_count,
            "presentation_instruction": presentation_instruction,
        }
        self._emit_event(
            callback,
            "status",
            {
                "stage": "design",
                "title": "Design Slides",
                "description": f"Rendering {len(chunks)} slides in the canonical workflow...",
                "message": "Design Slides",
            },
        )
        workflow_kwargs: dict[str, Any] = {
            "slide_chunks": chunks,
            "title": project_name,
            "slide_options": slide_options,
        }
        if callback is not None:
            workflow_kwargs["callback"] = callback
        output_folder = await self.slide_workflow.generate_from_chunks(
            **workflow_kwargs,
        )
        if not output_folder:
            raise RuntimeError("Slide workflow returned no output")

        project_id = self.project_service.import_project_from_workflow(
            user_id=session.user_id,
            project_name=project_name,
            source_type="chatbot",
            source_data={
                "session_id": session.id,
                "prompt": prompt,
                "script": script,
                "presentation_instruction": presentation_instruction,
            },
            slide_options=slide_options,
            output_folder=output_folder,
        )
        if not project_id:
            raise RuntimeError("Không thể lưu project được tạo từ chatbot")
        return SlideGenerationResult(
            project_id=project_id,
            project_name=project_name,
            script=script,
            slide_count=len(chunks),
        )

    async def _generate_presentation_instruction(
        self,
        *,
        prompt: str,
        target_slide_count: int,
        generation_config: dict[str, str | float | int],
    ) -> str:
        """Turn the user's display request into one deck-level planner brief.

        The brief is intentionally generated once before the workflow starts.
        The canonical planner then receives the same brief in every batch, so
        independent batch calls share the user's presentation intent without
        introducing code-side action overrides.
        """
        system_prompt = """
You are a presentation-design requirements interpreter for Slidegenius.
Convert the user's request into a concise deck-level instruction for a
downstream slide planner.

Preserve every explicit request about presentation form: charts, diagrams,
timelines, processes, comparisons, tables, images, visual density, layout,
ordering, and whether the request applies to one slide, several slides, or the
whole deck. If the user says full deck, every slide, all slides, or an
equivalent phrase, state clearly that the instruction applies to all relevant
content slides. If the scope is not explicit, describe the most natural scope
without inventing one.

Do not write slide content, do not invent facts or data, and do not turn an
example into a universal requirement. Return plain text only, no JSON,
Markdown heading, or explanation outside the planner instruction. Keep it
under 180 words.
""".strip()
        user_prompt = (
            f"User request:\n{prompt}\n\n"
            f"Requested content-slide count: {target_slide_count}\n\n"
            "Write the deck-level presentation instruction now."
        )
        try:
            result = await asyncio.to_thread(
                self.llm_provider.generate_completion,
                [
                    {
                        "role": "system",
                        "content": (
                            f"{system_prompt}\n\n"
                            f"{language_instruction(detect_language(prompt))}"
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                model=str(generation_config["provider_model"]),
                max_tokens=min(700, int(generation_config["max_tokens"])),
                temperature=min(0.25, float(generation_config["temperature"])),
                top_p=float(generation_config["top_p"]),
            )
        except Exception:
            # The user request remains available to the planner if this small
            # interpretation call is unavailable; generation must not fail for
            # an optional planning brief.
            return f"Preserve the user's explicit presentation requirements from this request: {prompt.strip()}"
        instruction = " ".join(str(result or "").split()).strip()
        return instruction[:4000] or (
            f"Preserve the user's explicit presentation requirements from this request: {prompt.strip()}"
        )

    async def _generate_script(
        self,
        *,
        prompt: str,
        retrieved_context: str,
        target_slide_count: int,
        generation_config: dict[str, str | float | int],
        draft: str | None = None,
    ) -> str:
        newline = chr(10)
        exact_count_instruction = (
            f"Create exactly {target_slide_count} content slides. "
            "The single # deck title is not counted. Use exactly one ## heading "
            f"for each of the {target_slide_count} slides, and do not use ## headings "
            "inside slide content."
        )
        draft_instruction = ""
        if draft:
            draft_instruction = (
                newline + newline
                + "Draft that must be rewritten to the required count:" + newline
                + draft
            )
        script_prompt = (
            "User's presentation request:" + newline + prompt + newline + newline
            + "Retrieved document context:" + newline
            + (retrieved_context or "(No uploaded document context.)")
            + newline + newline + exact_count_instruction
            + newline + "Keep the content concise and create the presentation script now."
            + draft_instruction
        )
        system_prompt = (
            f"{self._SCRIPT_SYSTEM_PROMPT}\n\n"
            f"{language_instruction(detect_language(prompt))}\n\n"
            f"{exact_count_instruction}"
        )
        return await asyncio.to_thread(
            self.llm_provider.generate_completion,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": script_prompt},
            ],
            model=str(generation_config["provider_model"]),
            max_tokens=self._script_max_tokens(generation_config, target_slide_count),
            temperature=float(generation_config["temperature"]),
            top_p=float(generation_config["top_p"]),
        )

    @staticmethod
    def _script_max_tokens(
        generation_config: dict[str, str | float | int],
        target_slide_count: int,
    ) -> int:
        """Reserve enough output budget for the explicitly selected count."""
        configured = int(generation_config["max_tokens"])
        count_budget = 800 + target_slide_count * 100
        return min(20_000, max(configured, count_budget))

    @staticmethod
    def _emit_event(
        callback: Callable[[str, dict[str, Any]], None] | None,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        if callback is None:
            return
        try:
            callback(event_type, data)
        except Exception:
            # The renderer already treats progress as best-effort. Keep the
            # same rule for the preparation stages owned by this service.
            return

    @staticmethod
    def _clean_script(script: str) -> str:
        clean = (script or "").strip()
        if clean.startswith("```"):
            lines = clean.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            clean = chr(10).join(lines)
        return clean.strip()

    @staticmethod
    def _to_slide_chunks(
        title: str, structure: list[dict[str, Any]], script: str
    ) -> list[dict[str, Any]]:
        roots = structure or []
        if len(roots) == 1 and roots[0].get("children"):
            deck_title = title or str(roots[0].get("title") or "Untitled")
            nodes = roots[0].get("children") or []
        else:
            deck_title = title or (
                str(roots[0].get("title")) if roots else "Untitled"
            )
            nodes = roots

        chunks: list[dict[str, Any]] = []
        for index, node in enumerate(nodes):
            node_title = str(node.get("title") or f"Slide {index + 1}").strip()
            content = str(node.get("content") or "").strip()
            child_text = []
            for child in node.get("children") or []:
                child_title = str(child.get("title") or "").strip()
                child_content = str(child.get("content") or "").strip()
                if child_title:
                    child_text.append(f"{child_title}: {child_content}".strip(": "))
            if child_text:
                content = (chr(10) + chr(10)).join(
                    [part for part in [content, *child_text] if part]
                )
            chunks.append(
                {
                    "title": node_title,
                    "heading": node_title,
                    "content": content or deck_title,
                    "slide_type": "intro" if index == 0 else "content",
                    "section_id": f"chat_{index + 1}",
                }
            )
        if not chunks and script.strip():
            chunks.append(
                {
                    "title": deck_title,
                    "heading": deck_title,
                    "content": script,
                    "slide_type": "intro",
                    "section_id": "chat_1",
                }
            )
        return chunks

    @staticmethod
    def _safe_project_name(value: str) -> str:
        name = " ".join(value.split()).strip()
        for character in '<>:"/\\|?*':
            name = name.replace(character, "-")
        return (name[:120] or "Chatbot presentation").strip()
