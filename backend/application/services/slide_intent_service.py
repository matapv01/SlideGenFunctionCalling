from __future__ import annotations

import asyncio
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Literal

from backend.application.services.language_service import (
    Language,
    detect_language,
    is_language_compatible,
    language_instruction,
    normalize_language_text,
)
from backend.domain.entities.chat import ChatMessage
from backend.domain.ports.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

MIN_SLIDE_COUNT = 3
DEFAULT_SLIDE_COUNT_OPTIONS = (6, 10, 15)


@dataclass(frozen=True)
class SlideFlowOption:
    label: str
    value: str
    is_other: bool = False
    action: Literal["answer", "other", "upgrade"] = "answer"

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "value": self.value,
            "is_other": self.is_other,
            "action": self.action,
        }


@dataclass(frozen=True)
class SlideFlowDecision:
    state: Literal["clarifying", "awaiting_confirmation", "limit_reached"]
    message: str
    options: tuple[SlideFlowOption, ...]
    brief: str
    question: str | None = None
    target_slide_count: int | None = None
    max_slide_count: int | None = None
    question_kind: Literal["slide_count", "content"] | None = None


class SlideIntentService:
    """Plan a slide request before the canonical slide renderer is called.

    This service deliberately owns only the conversational preflight: it asks
    one multiple-choice question at a time or returns a confirmation prompt.
    The actual slide generation remains behind ``SlideGenerationPort``.
    """

    _SYSTEM_PROMPT = """
You are the preflight planner for Slidegenius slide creation.
Your job is to clarify a user's slide request before any slides are generated.
Return exactly one valid JSON object and no Markdown.

The JSON must have this shape:
{
  "type": "clarification" or "confirmation",
  "question": "one short question when type is clarification",
  "message": "one short confirmation message when type is confirmation",
  "options": [{"label": "short user-facing label", "value": "meaningful answer value"}],
  "brief": "the best concise slide brief assembled so far",
  "target_slide_count": "the requested integer slide count when already known"
}

Rules:
- Reply in the user's language.
- A clarification must contain 2 or 3 meaningful options followed by a final
  option for a custom answer. That final option must be labelled "Khác" in
  Vietnamese or "Other" in English. Never put the custom option elsewhere.
- Therefore a clarification has exactly 3 or 4 options in total.
- Options must be mutually useful and concrete, not generic filler.
- Ask only one question at a time.
- Return type "confirmation" when the brief is specific enough to begin.
- A confirmation must ask whether to start creating the slides. Its options
  should be a clear affirmative action and a clear way to add more details.
- Never choose or change the slide count silently. Preserve the requested count
  supplied by the application.
- Never generate slide content, JSON slide structures, or explanations here.
""".strip()

    _FALLBACK_VIETNAMESE_OPTIONS = (
        SlideFlowOption("Giới thiệu / ra mắt", "Tập trung giới thiệu hoặc ra mắt sản phẩm, dịch vụ."),
        SlideFlowOption("Phân tích / đề xuất", "Tập trung phân tích vấn đề và đưa ra đề xuất."),
        SlideFlowOption("Đào tạo / hướng dẫn", "Tập trung giải thích quy trình hoặc hướng dẫn người xem."),
        SlideFlowOption("Khác", "Người dùng sẽ bổ sung yêu cầu riêng.", is_other=True),
    )
    _FALLBACK_ENGLISH_OPTIONS = (
        SlideFlowOption("Introduction / launch", "Focus on introducing or launching a product or service."),
        SlideFlowOption("Analysis / recommendation", "Focus on analyzing a problem and presenting recommendations."),
        SlideFlowOption("Training / how-to", "Focus on explaining a process or teaching the audience."),
        SlideFlowOption("Other", "The user will provide a custom direction.", is_other=True),
    )

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def start(
        self,
        prompt: str,
        history: list[ChatMessage],
        generation_config: dict[str, str | float | int],
        *,
        max_slide_count: int = 50,
        requested_slide_count: int | None = None,
        document_attached: bool = False,
    ) -> SlideFlowDecision:
        language = self._language_for(prompt)
        target_slide_count = requested_slide_count or self._extract_slide_count(prompt)
        if target_slide_count is None:
            return self._slide_count_clarification(prompt, language, max_slide_count)
        if target_slide_count < MIN_SLIDE_COUNT:
            return self._slide_count_clarification(
                prompt,
                language,
                max_slide_count,
                message=(
                    "Bộ slide cần có ít nhất 3 slide. Bạn muốn chọn bao nhiêu slide?"
                    if language == "vi"
                    else "A deck needs at least 3 slides. How many slides would you like?"
                ),
            )
        if self._exceeds_max(target_slide_count, max_slide_count):
            return self._slide_limit_decision(
                prompt,
                target_slide_count,
                max_slide_count,
                language,
            )

        fallback = self._fallback_clarification(prompt, language)
        raw = await self._ask_llm(
            self._build_start_messages(
                prompt,
                history,
                language,
                target_slide_count,
                document_attached,
            ),
            generation_config,
        )
        return self._normalise_decision(
            raw,
            current_brief=prompt,
            fallback=fallback,
            language=language,
            target_slide_count=target_slide_count,
            max_slide_count=max_slide_count,
            document_attached=document_attached,
        )

    async def continue_flow(
        self,
        flow: dict[str, Any],
        answer: str,
        history: list[ChatMessage],
        generation_config: dict[str, str | float | int],
        *,
        max_slide_count: int = 50,
        requested_slide_count: int | None = None,
        document_attached: bool = False,
    ) -> SlideFlowDecision:
        original_prompt = str(flow.get("original_prompt") or "").strip()
        current_brief = str(flow.get("brief") or original_prompt).strip()
        max_slide_count = self._flow_max_slide_count(flow, max_slide_count)
        target_slide_count = self._coerce_slide_count(flow.get("target_slide_count"))
        question_kind = str(flow.get("question_kind") or "")
        answer_slide_count = requested_slide_count or self._extract_slide_count(
            answer,
            allow_bare_number=question_kind == "slide_count" or flow.get("state") == "limit_reached",
        )
        if answer_slide_count is not None:
            target_slide_count = answer_slide_count
        if target_slide_count is None:
            return self._slide_count_clarification(
                original_prompt,
                self._language_for(original_prompt or answer),
                max_slide_count,
                message=(
                    "Mình cần số lượng slide cụ thể trước khi tiếp tục. Hãy chọn hoặc nhập một số từ 3 trở lên."
                    if self._language_for(original_prompt or answer) == "vi"
                    else "I need a concrete slide count before continuing. Choose an option or enter a number of at least 3."
                ),
            )
        language = self._language_for(original_prompt or answer)
        if target_slide_count is not None and target_slide_count < MIN_SLIDE_COUNT:
            return self._slide_count_clarification(
                original_prompt,
                language,
                max_slide_count,
                message=(
                    "Bộ slide cần có ít nhất 3 slide. Bạn muốn chọn bao nhiêu slide?"
                    if language == "vi"
                    else "A deck needs at least 3 slides. How many slides would you like?"
                ),
            )
        if target_slide_count is not None and self._exceeds_max(target_slide_count, max_slide_count):
            return self._slide_limit_decision(
                original_prompt,
                target_slide_count,
                max_slide_count,
                language,
            )

        answers = [
            item
            for item in flow.get("answers", [])
            if isinstance(item, dict)
        ]
        question = str(flow.get("question") or "").strip()
        if question:
            answers = [*answers, {"question": question, "answer": answer.strip()}]
        fallback = self._fallback_confirmation(
            current_brief,
            answers,
            language,
            target_slide_count,
            max_slide_count,
        )
        raw = await self._ask_llm(
            self._build_continue_messages(
                original_prompt,
                current_brief,
                answers,
                answer,
                history,
                language,
                target_slide_count,
                document_attached,
            ),
            generation_config,
        )
        decision = self._normalise_decision(
            raw,
            current_brief=current_brief,
            fallback=fallback,
            language=language,
            target_slide_count=target_slide_count,
            max_slide_count=max_slide_count,
            document_attached=document_attached,
        )
        # Keep all answers in the flow state through the caller. The latest
        # answer is included here so the brief survives a page reload even if
        # the LLM did not return a revised brief.
        if decision.brief == current_brief and answer.strip():
            decision = SlideFlowDecision(
                state=decision.state,
                message=decision.message,
                options=decision.options,
                brief=f"{current_brief}\nAdditional requirement: {answer.strip()}",
                question=decision.question,
                target_slide_count=decision.target_slide_count,
                max_slide_count=decision.max_slide_count,
                question_kind=decision.question_kind,
            )
        return decision

    async def _ask_llm(
        self,
        messages: list[dict[str, str]],
        generation_config: dict[str, str | float | int],
    ) -> dict[str, Any] | None:
        try:
            response = await asyncio.to_thread(
                self.llm_provider.generate_completion,
                messages,
                model=str(generation_config["provider_model"]),
                max_tokens=min(1400, int(generation_config["max_tokens"])),
                temperature=min(0.45, float(generation_config["temperature"])),
                top_p=float(generation_config["top_p"]),
            )
        except Exception:
            logger.exception("Slide intent clarification failed")
            return None
        return self._parse_json(response)

    def _build_start_messages(
        self,
        prompt: str,
        history: list[ChatMessage],
        language: Language,
        target_slide_count: int,
        document_attached: bool,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": f"{self._SYSTEM_PROMPT}\n\n{language_instruction(language)}",
            },
            {
                "role": "user",
                "content": (
                    f"Original slide request:\n{prompt}\n\n"
                    f"Requested slide count: {target_slide_count}\n\n"
                    f"{self._document_context_instruction(document_attached)}\n\n"
                    f"Recent conversation context:\n{self._format_history(history)}\n\n"
                    "Ask the single most useful first clarification question."
                ),
            },
        ]

    def _build_continue_messages(
        self,
        original_prompt: str,
        current_brief: str,
        answers: list[dict[str, Any]],
        latest_answer: str,
        history: list[ChatMessage],
        language: Language,
        target_slide_count: int | None,
        document_attached: bool,
    ) -> list[dict[str, str]]:
        answers_text = "\n".join(
            f"- {item.get('question', 'Question')}: {item.get('answer', '')}"
            for item in answers
        ) or "(none)"
        return [
            {
                "role": "system",
                "content": f"{self._SYSTEM_PROMPT}\n\n{language_instruction(language)}",
            },
            {
                "role": "user",
                "content": (
                    f"Original slide request:\n{original_prompt}\n\n"
                    f"Current brief:\n{current_brief}\n\n"
                    f"Requested slide count: {target_slide_count or '(not chosen yet)'}\n\n"
                    f"{self._document_context_instruction(document_attached)}\n\n"
                    f"Answers collected:\n{answers_text}\n\n"
                    f"Latest user input:\n{latest_answer}\n\n"
                    f"Recent conversation context:\n{self._format_history(history)}\n\n"
                    "Either ask the next single clarification question or ask for confirmation to start."
                ),
            },
        ]

    def _normalise_decision(
        self,
        raw: dict[str, Any] | None,
        *,
        current_brief: str,
        fallback: SlideFlowDecision,
        language: Literal["vi", "en"],
        target_slide_count: int | None = None,
        max_slide_count: int = 50,
        document_attached: bool = False,
    ) -> SlideFlowDecision:
        if not isinstance(raw, dict):
            if target_slide_count is None and fallback.target_slide_count is None:
                return fallback
            return SlideFlowDecision(
                state=fallback.state,
                message=fallback.message,
                options=fallback.options,
                brief=fallback.brief,
                question=fallback.question,
                target_slide_count=target_slide_count or fallback.target_slide_count,
                max_slide_count=max_slide_count,
                question_kind=fallback.question_kind or "content",
            )

        kind = str(raw.get("type") or raw.get("state") or "").strip().lower()
        brief = str(raw.get("brief") or current_brief).strip() or current_brief
        if not is_language_compatible(brief, language):
            brief = current_brief
        raw_target = self._coerce_slide_count(raw.get("target_slide_count"))
        target_slide_count = target_slide_count or raw_target
        if target_slide_count is not None and target_slide_count < MIN_SLIDE_COUNT:
            return self._slide_count_clarification(
                current_brief,
                language,
                max_slide_count,
                message=(
                    "Bộ slide cần có ít nhất 3 slide. Bạn muốn chọn bao nhiêu slide?"
                    if language == "vi"
                    else "A deck needs at least 3 slides. How many slides would you like?"
                ),
            )
        if target_slide_count is not None and self._exceeds_max(target_slide_count, max_slide_count):
            return self._slide_limit_decision(
                current_brief,
                target_slide_count,
                max_slide_count,
                language,
            )
        if kind in {"confirmation", "confirm", "ready"}:
            if target_slide_count is None:
                return self._slide_count_clarification(
                    current_brief,
                    language,
                    max_slide_count,
                )
            message = str(raw.get("message") or "").strip()
            if not is_language_compatible(message, language):
                message = self._confirmation_message(language)
            return SlideFlowDecision(
                state="awaiting_confirmation",
                message=message,
                options=self._confirmation_options(language),
                brief=brief,
                target_slide_count=target_slide_count,
                max_slide_count=max_slide_count,
            )

        if kind not in {"clarification", "question", "clarify"}:
            return self._fallback_with_metadata(
                fallback,
                target_slide_count=target_slide_count,
                max_slide_count=max_slide_count,
            )

        question = str(raw.get("question") or raw.get("message") or "").strip()
        options = self._normalise_options(raw.get("options"), language)
        if not question or not is_language_compatible(question, language) or len(options) < 3:
            return self._fallback_with_metadata(
                fallback,
                target_slide_count=target_slide_count,
                max_slide_count=max_slide_count,
            )
        if document_attached and self._is_document_source_question(question, options):
            # The document is already selected in this session. An LLM may
            # still return the old "upload/paste/source" question from a stale
            # prompt or a previous model configuration; replace it at the
            # preflight boundary so the user never has to upload the same file
            # twice.
            return self._fallback_with_metadata(
                fallback,
                target_slide_count=target_slide_count,
                max_slide_count=max_slide_count,
            )
        return SlideFlowDecision(
            state="clarifying",
            message=question,
            options=tuple(options),
            brief=brief,
            question=question,
            target_slide_count=target_slide_count,
            max_slide_count=max_slide_count,
            question_kind="content" if target_slide_count is not None else "slide_count",
        )

    def _normalise_options(
        self,
        raw_options: Any,
        language: Literal["vi", "en"],
    ) -> list[SlideFlowOption]:
        if not isinstance(raw_options, list):
            return list(self._fallback_clarification("", language).options)

        options: list[SlideFlowOption] = []
        for raw_option in raw_options:
            if isinstance(raw_option, str):
                label = raw_option.strip()
                value = label
                is_other = self._is_other_label(label)
            elif isinstance(raw_option, dict):
                label = str(raw_option.get("label") or "").strip()
                value = str(raw_option.get("value") or label).strip()
                is_other = bool(raw_option.get("is_other")) or self._is_other_label(label)
            else:
                continue
            if not label or is_other:
                continue
            if any(option.label.casefold() == label.casefold() for option in options):
                continue
            options.append(SlideFlowOption(label, value))
            if len(options) == 3:
                break

        if len(options) < 2:
            return list(self._fallback_clarification("", language).options)
        options.append(
            SlideFlowOption(
                "Khác" if language == "vi" else "Other",
                "Người dùng sẽ bổ sung yêu cầu riêng." if language == "vi" else "The user will provide a custom direction.",
                is_other=True,
            )
        )
        return options

    def _slide_count_clarification(
        self,
        prompt: str,
        language: Literal["vi", "en"],
        max_slide_count: int,
        *,
        message: str | None = None,
    ) -> SlideFlowDecision:
        if language == "vi":
            limit_text = (
                f" (gói hiện tại tối đa {max_slide_count} slide)"
                if max_slide_count != -1
                else ""
            )
            question = message or (
                f"Trước khi bắt đầu, bạn muốn bài có bao nhiêu slide{limit_text}?"
            )
            options = tuple(
                SlideFlowOption(f"{count} slide", f"{count} slide")
                for count in self._slide_count_options(max_slide_count)
            )
            options += (
                SlideFlowOption(
                    "Khác",
                    "Người dùng sẽ nhập số slide riêng.",
                    is_other=True,
                    action="other",
                ),
            )
        else:
            limit_text = (
                f" (up to {max_slide_count} slides on the current plan)"
                if max_slide_count != -1
                else ""
            )
            question = message or f"Before we start, how many slides would you like{limit_text}?"
            options = tuple(
                SlideFlowOption(f"{count} slides", f"{count} slides")
                for count in self._slide_count_options(max_slide_count)
            )
            options += (
                SlideFlowOption(
                    "Other",
                    "The user will enter a custom slide count.",
                    is_other=True,
                    action="other",
                ),
            )
        return SlideFlowDecision(
            state="clarifying",
            message=question,
            options=options,
            brief=prompt,
            question=question,
            max_slide_count=max_slide_count,
            question_kind="slide_count",
        )

    def _slide_limit_decision(
        self,
        prompt: str,
        requested_slide_count: int,
        max_slide_count: int,
        language: Literal["vi", "en"],
    ) -> SlideFlowDecision:
        if language == "vi":
            message = (
                f"Bạn đang chọn {requested_slide_count} slide, nhưng gói hiện tại chỉ hỗ trợ "
                f"tối đa {max_slide_count} slide. Hãy chọn lại số lượng hoặc nâng cấp gói."
            )
            options = (
                SlideFlowOption(
                    f"Tạo {max_slide_count} slide",
                    f"{max_slide_count} slide",
                ),
                SlideFlowOption(
                    "Chọn số khác",
                    "",
                    is_other=True,
                    action="other",
                ),
                SlideFlowOption("Nâng cấp gói", "upgrade", action="upgrade"),
            )
        else:
            message = (
                f"You selected {requested_slide_count} slides, but the current plan supports "
                f"up to {max_slide_count}. Choose a smaller deck or upgrade your plan."
            )
            options = (
                SlideFlowOption(
                    f"Create {max_slide_count} slides",
                    f"{max_slide_count} slides",
                ),
                SlideFlowOption("Choose another count", "", is_other=True, action="other"),
                SlideFlowOption("Upgrade plan", "upgrade", action="upgrade"),
            )
        return SlideFlowDecision(
            state="limit_reached",
            message=message,
            options=options,
            brief=prompt,
            max_slide_count=max_slide_count,
            question_kind="slide_count",
        )

    @staticmethod
    def _slide_count_options(max_slide_count: int) -> tuple[int, ...]:
        values = [
            count
            for count in DEFAULT_SLIDE_COUNT_OPTIONS
            if max_slide_count == -1 or count <= max_slide_count
        ]
        if max_slide_count != -1 and max_slide_count >= MIN_SLIDE_COUNT:
            if max_slide_count < max(DEFAULT_SLIDE_COUNT_OPTIONS):
                values.append(max_slide_count)
            if len(values) < 2:
                values.extend([MIN_SLIDE_COUNT, max_slide_count])
        unique = tuple(dict.fromkeys(count for count in values if count >= MIN_SLIDE_COUNT))
        return unique or (MIN_SLIDE_COUNT,)

    @staticmethod
    def _coerce_slide_count(value: Any) -> int | None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        return parsed if parsed > 0 else None

    @classmethod
    def _extract_slide_count(cls, value: str, *, allow_bare_number: bool = False) -> int | None:
        text = str(value or "")
        # A range is not an explicit choice. Do not silently use its lower
        # bound; send it back through the count question instead.
        if re.search(
            r"(?<!\d)\d{1,3}\s*-\s*\d{1,3}\s*(?:slides?|trang|pages?)\b",
            text,
            flags=re.IGNORECASE,
        ):
            return None
        patterns = (
            r"(?<!\d)(\d{1,3})\s*(?:-\s*)?(?:slides?|trang|pages?)\b",
            r"\b(?:slides?|trang|pages?)\s*(\d{1,3})(?!\d)\b",
        )
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return cls._coerce_slide_count(match.group(1))
        if allow_bare_number:
            match = re.fullmatch(r"\s*(\d{1,3})\s*", text)
            if match:
                return cls._coerce_slide_count(match.group(1))
        return None

    @staticmethod
    def _flow_max_slide_count(flow: dict[str, Any], fallback: int) -> int:
        value = flow.get("max_slide_count", fallback)
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _exceeds_max(value: int, maximum: int) -> bool:
        return maximum != -1 and value > maximum

    def _fallback_clarification(
        self,
        prompt: str,
        language: Literal["vi", "en"],
        *,
        target_slide_count: int | None = None,
        max_slide_count: int | None = None,
        question_kind: Literal["slide_count", "content"] | None = None,
    ) -> SlideFlowDecision:
        if language == "vi":
            return SlideFlowDecision(
                state="clarifying",
                message="Bạn muốn bộ slide tập trung theo hướng nào?",
                options=self._FALLBACK_VIETNAMESE_OPTIONS,
                brief=prompt,
                question="Bạn muốn bộ slide tập trung theo hướng nào?",
                target_slide_count=target_slide_count,
                max_slide_count=max_slide_count,
                question_kind=question_kind or (
                    "content" if target_slide_count is not None else None
                ),
            )
        return SlideFlowDecision(
            state="clarifying",
            message="What should the deck focus on most?",
            options=self._FALLBACK_ENGLISH_OPTIONS,
            brief=prompt,
            question="What should the deck focus on most?",
            target_slide_count=target_slide_count,
            max_slide_count=max_slide_count,
            question_kind=question_kind or (
                "content" if target_slide_count is not None else None
            ),
        )

    @staticmethod
    def _fallback_with_metadata(
        fallback: SlideFlowDecision,
        *,
        target_slide_count: int | None,
        max_slide_count: int,
    ) -> SlideFlowDecision:
        resolved_target = target_slide_count or fallback.target_slide_count
        return SlideFlowDecision(
            state=fallback.state,
            message=fallback.message,
            options=fallback.options,
            brief=fallback.brief,
            question=fallback.question,
            target_slide_count=resolved_target,
            max_slide_count=max_slide_count if max_slide_count is not None else fallback.max_slide_count,
            question_kind=fallback.question_kind or (
                "content" if resolved_target is not None else "slide_count"
            ),
        )

    def request_slide_count(
        self,
        prompt: str,
        *,
        max_slide_count: int = 50,
    ) -> SlideFlowDecision:
        """Return the mandatory count question for legacy or incomplete flows."""
        language = self._language_for(prompt)
        return self._slide_count_clarification(prompt, language, max_slide_count)

    def _fallback_confirmation(
        self,
        current_brief: str,
        answers: list[dict[str, Any]],
        language: Literal["vi", "en"],
        target_slide_count: int | None = None,
        max_slide_count: int = 50,
    ) -> SlideFlowDecision:
        answer_text = "\n".join(
            f"{item.get('question', 'Answer')}: {item.get('answer', '')}"
            for item in answers
        )
        brief = f"{current_brief}\n{answer_text}".strip()
        return SlideFlowDecision(
            state="awaiting_confirmation",
            message=self._confirmation_message(language),
            options=self._confirmation_options(language),
            brief=brief,
            target_slide_count=target_slide_count,
            max_slide_count=max_slide_count,
        )

    @staticmethod
    def _confirmation_message(language: Literal["vi", "en"]) -> str:
        if language == "vi":
            return "Mình đã đủ thông tin. Bắt đầu tạo slide nhé?"
        return "I have enough direction now. Shall I start creating the slides?"

    @staticmethod
    def _confirmation_options(language: Literal["vi", "en"]) -> tuple[SlideFlowOption, ...]:
        if language == "vi":
            return (
                SlideFlowOption("Bắt đầu tạo slide", "Bắt đầu tạo slide"),
                SlideFlowOption("Tôi muốn bổ sung", "Tôi muốn bổ sung thêm yêu cầu"),
            )
        return (
            SlideFlowOption("Start creating slides", "Start creating slides"),
            SlideFlowOption("I want to add more", "I want to add more requirements"),
        )

    @staticmethod
    def _parse_json(response: str) -> dict[str, Any] | None:
        text = str(response or "").strip()
        if not text:
            return None
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            value = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def _format_history(history: list[ChatMessage]) -> str:
        relevant = [message for message in history[-6:] if message.role in {"user", "assistant"}]
        if not relevant:
            return "(none)"
        return "\n".join(f"{message.role.title()}: {message.content}" for message in relevant)

    @staticmethod
    def _document_context_instruction(document_attached: bool) -> str:
        if document_attached:
            return (
                "A reference DOCX is already attached to this conversation and is the "
                "selected source. Do not ask whether to upload a file, paste text, "
                "choose a source, or provide another document. Ask about presentation "
                "direction only, or ask for confirmation if the brief is sufficient."
            )
        return (
            "No reference document is attached. Do not assume that a document exists; "
            "ask about the most useful content direction when needed."
        )

    @classmethod
    def _is_document_source_question(
        cls,
        question: str,
        options: list[SlideFlowOption] | tuple[SlideFlowOption, ...],
    ) -> bool:
        normalized_question = normalize_language_text(question)
        source_question_phrases = (
            "tai lieu nao",
            "nguon nao",
            "chon nguon",
            "tai len",
            "dan noi dung",
            "document",
            "source",
            "material",
            "upload",
            "paste",
        )
        if any(phrase in normalized_question for phrase in source_question_phrases):
            return True

        option_text = " ".join(
            normalize_language_text(f"{option.label} {option.value}")
            for option in options
        )
        source_option_phrases = (
            "tai lieu",
            "tai len",
            "dan noi dung",
            "document",
            "source",
            "material",
            "upload",
            "paste",
        )
        return sum(phrase in option_text for phrase in source_option_phrases) >= 2

    @classmethod
    def is_document_source_flow(cls, flow: dict[str, Any]) -> bool:
        """Detect a legacy flow that asks the user to choose a document source."""
        raw_options = flow.get("options")
        options: list[SlideFlowOption] = []
        if isinstance(raw_options, list):
            for raw_option in raw_options:
                if not isinstance(raw_option, dict):
                    continue
                label = str(raw_option.get("label") or "").strip()
                value = str(raw_option.get("value") or label).strip()
                if label:
                    options.append(SlideFlowOption(label, value))
        return cls._is_document_source_question(
            str(flow.get("question") or ""),
            options,
        )

    @staticmethod
    def _is_other_label(label: str) -> bool:
        normalized = unicodedata.normalize("NFKD", label.casefold())
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        return normalized.strip() in {"khac", "other", "something else", "custom"}

    @staticmethod
    def _language_for(value: str) -> Literal["vi", "en"]:
        return detect_language(value)
