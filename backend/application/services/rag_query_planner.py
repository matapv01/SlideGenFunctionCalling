from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Literal, cast

from backend.application.services.language_service import (
    detect_language,
    language_instruction,
)
from backend.domain.entities.chat import ChatMessage
from backend.domain.ports.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


RagMode = Literal[
    "none",
    "document_overview",
    "deck_from_document",
    "targeted_section",
    "topic_grounded",
    "multi_facet",
]
RagSourcePolicy = Literal[
    "none",
    "document_only",
    "document_preferred",
    "conversation_only",
]


@dataclass(frozen=True)
class RagQueryPlan:
    """The retrieval decision produced for one chatbot turn.

    ``queries`` are deliberately kept as plain strings. The retriever owns
    node ids and tree traversal; the LLM may describe the information it needs
    but must never choose a database node directly.
    """

    needs_rag: bool
    queries: tuple[str, ...]
    reason: str
    source: Literal["llm", "fallback", "none"]
    mode: RagMode = "none"
    source_policy: RagSourcePolicy = "none"
    include_root: bool = False
    include_ancestors: bool = True
    include_siblings: bool = False
    max_detail_nodes: int = 6

    def as_dict(self) -> dict[str, Any]:
        return {
            "needs_rag": self.needs_rag,
            "queries": list(self.queries),
            "reason": self.reason,
            "source": self.source,
            "mode": self.mode,
            "source_policy": self.source_policy,
            "include_root": self.include_root,
            "include_ancestors": self.include_ancestors,
            "include_siblings": self.include_siblings,
            "max_detail_nodes": self.max_detail_nodes,
        }


class RagQueryPlanner:
    """Let the existing LLM decide when and how a document should be used.

    This is intentionally separate from ``DocumentRagService``. The planner
    decides what information to retrieve; the RAG service remains responsible
    for embeddings, ranking, provenance and session scoping.
    """

    _SYSTEM_PROMPT = """
You are Slidegenius's document-retrieval planner.
Decide whether the current user request needs information from the uploaded
documents in the conversation. If it does, rewrite the request into a small
set of concrete search queries describing the information that must be found.
Return exactly one JSON object and no Markdown:
{
  "needs_rag": true or false,
  "mode": "document_overview" or "deck_from_document" or
          "targeted_section" or "topic_grounded" or "multi_facet" or "none",
  "source_policy": "document_only" or "document_preferred" or
                   "conversation_only" or "none",
  "queries": ["search query 1", "search query 2"],
  "include_root": true or false,
  "include_ancestors": true or false,
  "include_siblings": true or false,
  "max_detail_nodes": 0 to 16,
  "reason": "short internal reason"
}

Rules:
- Set needs_rag to false for greetings, casual conversation, creative requests
  that do not depend on the uploaded documents, and questions answerable from
  the conversation alone.
- Set needs_rag to true when the user asks about, summarises, analyses,
  compares, quotes, or creates slides from the uploaded documents.
- Use mode document_overview for questions such as "what is this document
  about?" or "summarise this document". It needs the document root and
  high-level sections before detailed chunks.
- Use mode deck_from_document for "make slides from this document". It needs
  the root and broad section coverage; retrieve details only as needed for the
  requested slide count.
- Use mode targeted_section for a specific fact, section, quote or explanation.
  Retrieve the matching detail and its parent chain for context.
- Use mode topic_grounded when the user asks for slides about a topic while a
  document is attached. Probe the root/outline first and do not blindly use
  unrelated document chunks.
- Use mode multi_facet for comparisons or requests with several independent
  aspects. Each query should represent one facet.
- For a slide request with an attached document, search for the facts,
  sections, arguments, metrics, timeline or other material needed to write the
  deck—not the command "make slides" itself.
- Produce one to four concise queries in the user's language. A query may be
  a focused search phrase or a complete information question. Do not answer
  the question and do not invent document facts.
- Set include_root for overview, deck_from_document and topic_grounded modes.
  Set include_ancestors for targeted details. Set include_siblings only when
  sibling sections help answer a comparison or enumeration.
- max_detail_nodes controls detailed node expansion, not root/section summary
  coverage. Keep it small and increase it only when the request needs facts.
- Use the conversation and the current brief to resolve references such as
  "nó", "phần này", or "tài liệu trên".
- If no document is attached, always return needs_rag=false and queries=[].
""".strip()

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def plan(
        self,
        query: str,
        history: list[ChatMessage],
        generation_config: dict[str, str | float | int],
        *,
        document_attached: bool,
        slide_request: bool = False,
        brief: str | None = None,
    ) -> RagQueryPlan:
        if not document_attached:
            return RagQueryPlan(
                needs_rag=False,
                queries=(),
                reason="No ready document is attached to this conversation.",
                source="none",
                mode="none",
                source_policy="none",
            )

        fallback = self._fallback_plan(
            slide_request=slide_request,
            query=brief or query,
        )
        raw = await self._ask_llm(
            self._build_messages(
                query,
                history,
                slide_request=slide_request,
                brief=brief,
            ),
            generation_config,
        )
        return self._normalise(raw, fallback=fallback, fallback_query=brief or query)

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
                max_tokens=min(900, int(generation_config["max_tokens"])),
                temperature=min(0.25, float(generation_config["temperature"])),
                top_p=float(generation_config["top_p"]),
            )
        except Exception:
            logger.exception("RAG query planning failed")
            return None
        return self._parse_json(response)

    def _build_messages(
        self,
        query: str,
        history: list[ChatMessage],
        *,
        slide_request: bool,
        brief: str | None,
    ) -> list[dict[str, str]]:
        language = detect_language(query)
        current_brief = (brief or "").strip() or "(none)"
        return [
            {
                "role": "system",
                "content": f"{self._SYSTEM_PROMPT}\n\n{language_instruction(language)}",
            },
            {
                "role": "user",
                "content": (
                    f"Current user request:\n{query[:6000]}\n\n"
                    f"Current slide brief:\n{current_brief[:6000]}\n\n"
                    f"Is this a slide-generation request: {'yes' if slide_request else 'no'}\n\n"
                    f"Recent conversation:\n{self._format_history(history)}\n\n"
                    "Return the retrieval decision and rewritten search queries now."
                ),
            },
        ]

    @staticmethod
    def _fallback_plan(*, slide_request: bool, query: str) -> RagQueryPlan:
        """Use only explicit workflow state when the planner output is invalid."""
        if slide_request:
            fallback_query = " ".join(query.split())[:320]
            return RagQueryPlan(
                needs_rag=True,
                queries=(fallback_query,) if fallback_query else (),
                reason="The slide workflow requires the attached document as context.",
                source="fallback",
                mode="deck_from_document",
                source_policy="document_only",
                include_root=True,
                include_ancestors=True,
                include_siblings=False,
                max_detail_nodes=8,
            )
        return RagQueryPlan(
            needs_rag=False,
            queries=(),
            reason="The retrieval planner did not return a valid decision.",
            source="fallback",
            mode="none",
            source_policy="none",
            include_root=False,
            include_ancestors=False,
            include_siblings=False,
            max_detail_nodes=0,
        )

    @classmethod
    def _normalise(
        cls,
        raw: dict[str, Any] | None,
        *,
        fallback: RagQueryPlan,
        fallback_query: str,
    ) -> RagQueryPlan:
        if not isinstance(raw, dict):
            return fallback

        needs_rag = cls._coerce_bool(raw.get("needs_rag"))
        if needs_rag is None:
            needs_rag = bool(raw.get("queries"))

        queries = cls._normalise_queries(raw.get("queries"))
        if needs_rag and not queries:
            query = " ".join(fallback_query.split())[:320]
            queries = (query,) if query else fallback.queries
        if not needs_rag:
            queries = ()

        mode = cls._normalise_mode(raw.get("mode"), fallback.mode, needs_rag)
        source_policy = cls._normalise_source_policy(
            raw.get("source_policy"), fallback.source_policy, needs_rag
        )
        include_root = cls._coerce_bool(raw.get("include_root"))
        include_ancestors = cls._coerce_bool(raw.get("include_ancestors"))
        include_siblings = cls._coerce_bool(raw.get("include_siblings"))
        max_detail_nodes = cls._coerce_int(raw.get("max_detail_nodes"))
        if include_root is None:
            include_root = fallback.include_root
        if include_ancestors is None:
            include_ancestors = fallback.include_ancestors
        if include_siblings is None:
            include_siblings = fallback.include_siblings
        if max_detail_nodes is None:
            max_detail_nodes = fallback.max_detail_nodes
        max_detail_nodes = max(0, min(16, max_detail_nodes)) if needs_rag else 0
        if mode in {"document_overview", "deck_from_document", "topic_grounded"}:
            include_root = True
        if mode == "multi_facet":
            include_siblings = True
        if not needs_rag:
            mode = "none"
            source_policy = "none"
            include_root = False
            include_siblings = False

        reason = str(raw.get("reason") or "").strip()[:400]
        return RagQueryPlan(
            needs_rag=needs_rag,
            queries=queries,
            reason=reason or fallback.reason,
            source="llm",
            mode=mode,
            source_policy=source_policy,
            include_root=include_root,
            include_ancestors=include_ancestors,
            include_siblings=include_siblings,
            max_detail_nodes=max_detail_nodes,
        )

    @staticmethod
    def _normalise_queries(value: Any) -> tuple[str, ...]:
        if isinstance(value, str):
            values = [value]
        elif isinstance(value, list):
            values = value
        else:
            values = []

        queries: list[str] = []
        seen: set[str] = set()
        for value in values:
            if not isinstance(value, str):
                continue
            query = " ".join(value.split()).strip()[:320]
            key = query.casefold()
            if not query or key in seen:
                continue
            seen.add(key)
            queries.append(query)
            if len(queries) == 4:
                break
        return tuple(queries)

    @staticmethod
    def _coerce_bool(value: Any) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().casefold()
            if normalized in {"true", "yes", "1", "required"}:
                return True
            if normalized in {"false", "no", "0", "not_needed"}:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        return None

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        try:
            if isinstance(value, bool) or value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalise_mode(value: Any, fallback: RagMode, needs_rag: bool) -> RagMode:
        allowed = {
            "document_overview",
            "deck_from_document",
            "targeted_section",
            "topic_grounded",
            "multi_facet",
        }
        normalized = str(value or "").strip().lower()
        if not needs_rag:
            return "none"
        if normalized in allowed:
            return cast(RagMode, normalized)
        return fallback if fallback in allowed else "targeted_section"

    @staticmethod
    def _normalise_source_policy(
        value: Any,
        fallback: RagSourcePolicy,
        needs_rag: bool,
    ) -> RagSourcePolicy:
        allowed = {"document_only", "document_preferred", "conversation_only"}
        normalized = str(value or "").strip().lower()
        if not needs_rag:
            return "none"
        if normalized in allowed:
            return cast(RagSourcePolicy, normalized)
        return fallback if fallback in allowed else "document_preferred"

    @staticmethod
    def _parse_json(response: Any) -> dict[str, Any] | None:
        if not isinstance(response, str):
            return None
        text = response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            payload = json.loads(text[start : end + 1])
        except (TypeError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _format_history(history: list[ChatMessage]) -> str:
        if not history:
            return "(none)"
        return "\n".join(
            f"{message.role.title()}: {message.content[:1200]}"
            for message in history[-6:]
            if message.role in {"user", "assistant"}
        ) or "(none)"
