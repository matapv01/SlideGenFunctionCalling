
from __future__ import annotations
import asyncio
import logging
import threading
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Literal, Protocol

from backend.application.services.language_service import (
    detect_language,
    language_instruction,
)
from backend.application.services.rag_query_planner import (
    RagQueryPlan,
    RagQueryPlanner,
)
from backend.config import resolve_chatbot_generation_config
from backend.domain.entities.chat import ChatMessage, ChatSession
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.chat_repository import ChatRepository
from backend.domain.entities.chat_document import RetrievedContext
from backend.application.services.slide_intent_service import (
    SlideFlowDecision,
    SlideIntentService,
)
from backend.application.services.subscription_service import (
    SlideCountLimitError,
    SubscriptionService,
)
from backend.domain.ports.user_repository import UserRepository

logger = logging.getLogger(__name__)


def _friendly_slide_generation_error(exc: Exception) -> str:
    """Keep internal workflow/parser details out of the chat UI."""
    message = str(exc or "").strip()
    if "XML tool returned empty content" in message:
        return "Một slide không tạo được nội dung hoàn chỉnh. Hệ thống đã giữ các slide hợp lệ; vui lòng thử lại."
    if "XML tool returned invalid XML" in message:
        return "Một slide tạo ra cấu trúc không hợp lệ. Vui lòng thử lại."
    if "XML root element" in message:
        return "Một slide tạo ra cấu trúc không hợp lệ. Vui lòng thử lại."
    return message or "Không thể tạo slide lúc này. Vui lòng thử lại."


class ChatContextProvider(Protocol):
    """Retrieval boundary for the document RAG service."""

    async def retrieve(self, session: ChatSession, query: str) -> RetrievedContext: ...

    async def retrieve_many(
        self,
        session: ChatSession,
        queries: list[str],
        *,
        mode: str = "targeted_section",
        include_root: bool = False,
        include_ancestors: bool = True,
        include_siblings: bool = False,
        max_detail_nodes: int = 6,
        target_slide_count: int | None = None,
    ) -> RetrievedContext: ...

    def has_ready_documents(self, session: ChatSession) -> bool: ...

    async def ensure_documents_ready(
        self, *, session: ChatSession, document_ids: list[str]
    ) -> None: ...

    def list_session_documents(self, session_id: str, user_id: int) -> list[Any]: ...


class SlideGenerationPort(Protocol):
    async def generate(
        self,
        *,
        session: ChatSession,
        prompt: str,
        retrieved_context: str,
        model_name: str | None,
        effort: str | None,
        target_slide_count: int,
        document_images: list[dict[str, Any]] | None = None,
        callback: Callable[[str, dict[str, Any]], None] | None = None,
    ): ...


class SlideGenerationInProgressError(RuntimeError):
    """Raised when a user tries to start a second deck before the first ends."""

    def __init__(self) -> None:
        super().__init__(
            "Một deck đang được tạo. Bạn vẫn có thể trò chuyện, "
            "nhưng hãy đợi deck hiện tại hoàn tất trước khi tạo deck khác."
        )


class ChatMessageInProgressError(RuntimeError):
    """Raised when a second ordinary chat turn is started for the user."""

    def __init__(self) -> None:
        super().__init__(
            "Một câu trả lời đang được tạo. Vui lòng đợi câu trả lời hiện tại hoàn tất."
        )


@dataclass(frozen=True)
class ChatTurnResult:
    session: ChatSession
    user_message: ChatMessage
    assistant_message: ChatMessage
    standalone_query: str
    citations: list[dict]
    project_id: int | None = None


@dataclass
class SlideGenerationJob:
    """Process-owned slide job that survives an individual SSE disconnect.

    The browser is only a subscriber to this job.  The renderer continues in
    the application task when a tab reloads or the streaming panel is closed,
    while a short event history lets a new browser connection catch up.
    """

    id: str
    user_id: int
    session_id: str
    query: str
    model_name: str | None
    effort: str | None
    slide_count: int | None
    loop: asyncio.AbstractEventLoop
    document_ids: list[str] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    events: list[tuple[int, str, dict[str, Any]]] = field(default_factory=list)
    subscribers: set[asyncio.Queue[tuple[int, str, dict[str, Any]]]] = field(
        default_factory=set
    )
    task: asyncio.Task[None] | None = None
    finished: bool = False


@dataclass
class ChatMessageJob:
    """Process-owned ordinary chat job that survives an SSE disconnect."""

    id: str
    user_id: int
    session_id: str
    query: str
    model_name: str | None
    effort: str | None
    slide_count: int | None
    loop: asyncio.AbstractEventLoop
    document_ids: list[str] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    events: list[tuple[int, str, dict[str, Any]]] = field(default_factory=list)
    subscribers: set[asyncio.Queue[tuple[int, str, dict[str, Any]]]] = field(
        default_factory=set
    )
    task: asyncio.Task[None] | None = None
    finished: bool = False


class ChatbotService:
    """Application boundary for Slidegenius conversations.

    Conversation persistence, follow-up contextualization, document retrieval
    and short-term compaction live behind this application boundary. The
    service does not import the cloned RAG application's PostgreSQL runtime.
    """

    _SYSTEM_PROMPT = (
        "You are Slidegenius, a precise and helpful creative assistant. "
        "Answer entirely in the user's language and never switch languages "
        "without being asked. Keep the answer useful and direct. "
        "Do not invent facts or claim that you performed an action you did not perform. "
        "Do not replace a request to create a slide deck with a generic copied outline; "
        "the slide workflow handles that request separately."
    )
    _CONTEXTUALIZE_PROMPT = (
        "Rewrite the latest user message as one standalone question using the "
        "conversation context. Preserve the user's intent and language. "
        "If it is already standalone, return it unchanged. Return only the rewrite."
    )
    _COMPACT_PROMPT = (
        "Summarize the older conversation into durable context for a later assistant. "
        "Keep decisions, user preferences, project facts, open questions and constraints. "
        "Do not add facts. Return a concise summary in the conversation's language."
    )

    def __init__(
        self,
        repository: ChatRepository,
        llm_provider: LLMProvider,
        *,
        context_provider: ChatContextProvider | None = None,
        slide_generator: SlideGenerationPort | None = None,
        rag_query_planner: RagQueryPlanner | None = None,
        user_repository: UserRepository | None = None,
        subscription_service: SubscriptionService | None = None,
        default_max_turns: int = 5,
    ) -> None:
        self.repository = repository
        self.llm_provider = llm_provider
        self.context_provider = context_provider
        self.slide_generator = slide_generator
        self.rag_query_planner = rag_query_planner or RagQueryPlanner(llm_provider)
        self.user_repository = user_repository
        self.subscription_service = subscription_service
        self.default_max_turns = max(1, default_max_turns)
        self.slide_intent_service = SlideIntentService(llm_provider)
        # The chatbot service is a process-wide singleton in the API container.
        # Keep the guard here, at the application boundary, so multiple browser
        # tabs cannot start competing slide workflows for the same user while
        # ordinary chat messages continue to work.
        self._active_slide_generations: dict[int, str] = {}
        self._active_slide_generations_lock = threading.Lock()
        self._slide_generation_jobs: dict[str, SlideGenerationJob] = {}
        self._active_slide_generation_jobs: dict[int, str] = {}
        self._chat_message_jobs: dict[str, ChatMessageJob] = {}
        self._active_chat_message_jobs: dict[int, str] = {}

    def create_session(
        self,
        user_id: int,
        *,
        project_id: int | None = None,
        title: str | None = None,
    ) -> ChatSession:
        return self.repository.create_session(
            user_id,
            project_id=project_id,
            title=(title or "").strip() or None,
            max_turns=self.default_max_turns,
        )

    def list_sessions(self, user_id: int) -> list[ChatSession]:
        sessions = self.repository.list_sessions(user_id)
        # A detached job may not have persisted its first turn yet. Keep that
        # session addressable while it is running, without making every empty
        # draft look like a saved conversation in the normal history list.
        active_session_ids: set[str] = set()
        with self._active_slide_generations_lock:
            for job_id in (
                self._active_chat_message_jobs.get(user_id),
                self._active_slide_generation_jobs.get(user_id),
            ):
                if not job_id:
                    continue
                job = (
                    self._chat_message_jobs.get(job_id)
                    or self._slide_generation_jobs.get(job_id)
                )
                if job is not None:
                    active_session_ids.add(job.session_id)

        known_ids = {session.id for session in sessions}
        for session_id in active_session_ids - known_ids:
            session = self.repository.get_session(session_id, user_id)
            if session is not None and not session.archived:
                sessions.append(session)
        return sorted(sessions, key=lambda session: session.updated_at, reverse=True)

    def get_session(self, session_id: str, user_id: int) -> ChatSession | None:
        return self.repository.get_session(session_id, user_id)

    def list_messages(self, session_id: str, user_id: int) -> list[ChatMessage]:
        return self.repository.list_messages(session_id, user_id)

    def archive_session(self, session_id: str, user_id: int) -> None:
        self.repository.archive_session(session_id, user_id)

    async def send_message(
        self,
        session_id: str,
        user_id: int,
        query: str,
        *,
        model_name: str | None = None,
        effort: str | None = None,
        canvas_enabled: bool = False,
        slide_count: int | None = None,
        document_ids: list[str] | None = None,
        slide_callback: Callable[[str, dict[str, Any]], None] | None = None,
        slide_job_id: str | None = None,
    ) -> ChatTurnResult:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Message cannot be empty")
        if len(clean_query) > 12_000:
            raise ValueError("Message is too long")

        generation_config = resolve_chatbot_generation_config(model_name, effort)
        if self.subscription_service is not None:
            generation_config["usage_cost"] = self.subscription_service.get_chat_usage_cost(
                str(generation_config["model"]),
                str(generation_config["effort"]),
            )

        session = self.repository.get_session(session_id, user_id)
        if session is None or session.archived:
            raise LookupError("Chat session not found")

        # Every user-authored chatbot turn consumes one chat unit. The
        # subscription service owns the rolling five-hour quota so ordinary
        # chat and slide-generation confirmations use the same counter.
        if self.subscription_service is not None:
            self.subscription_service.consume_feature(
                user_id,
                "chat_message",
                usage_cost=float(generation_config.get("usage_cost", 1.0)),
            )

        normalized_document_ids = self._normalize_document_ids(document_ids)
        await self._ensure_documents_ready(session, normalized_document_ids)
        document_attached = self._has_ready_documents(session)
        message_attachments = self._resolve_document_attachments(
            session, normalized_document_ids
        )
        active_generation_session = self._active_slide_session(user_id)
        # A normal chat turn must remain available while the renderer works.
        # Only the dedicated SSE entry point represents an explicit second
        # deck-generation attempt and is rejected by the active-generation
        # guard. ``canvas_enabled`` is retained for request compatibility but
        # is not a concurrency signal by itself.
        active_job_id = self._active_slide_generation_jobs.get(user_id)
        owns_active_job = (
            slide_job_id is not None
            and active_job_id == slide_job_id
            and active_generation_session == session_id
        )
        if (
            active_generation_session is not None
            and slide_callback is not None
            and not owns_active_job
        ):
            raise SlideGenerationInProgressError()

        history = self.repository.list_messages(
            session_id, user_id, limit=max(20, session.max_turns * 2)
        )
        active_slide_flow = (
            None
            if active_generation_session == session.id and not owns_active_job
            else self._latest_slide_flow(history)
        )
        if active_slide_flow and active_slide_flow.get("state") in {
            "clarifying",
            "awaiting_confirmation",
            "limit_reached",
        }:
            standalone_query = clean_query
            decision = await self.slide_intent_service.continue_flow(
                active_slide_flow,
                clean_query,
                history,
                generation_config,
                max_slide_count=self._max_slide_count(user_id),
                requested_slide_count=slide_count,
                document_attached=document_attached,
            )
            if decision.start_generation:
                slide_prompt = str(
                    decision.brief
                    or active_slide_flow.get("brief")
                    or clean_query
                ).strip()
                target_slide_count = (
                    slide_count
                    or decision.target_slide_count
                    or self._flow_slide_count(active_slide_flow)
                )
                if target_slide_count is not None:
                    self._validate_slide_count(user_id, target_slide_count)
                    return await self._run_slide_generation(
                        session=session,
                        user_id=user_id,
                        query=clean_query,
                        slide_prompt=slide_prompt,
                        standalone_query=slide_prompt,
                        model_name=model_name,
                        effort=effort,
                        generation_config=generation_config,
                        target_slide_count=target_slide_count,
                        history=history,
                        document_attached=document_attached,
                        slide_callback=slide_callback,
                        slide_job_id=slide_job_id,
                        attachments=message_attachments,
                    )
            answers = self._flow_answers_with_latest_input(
                active_slide_flow,
                clean_query,
            )
            metadata = self._generation_metadata(generation_config)
            metadata["slide_flow"] = self._slide_flow_metadata(
                decision,
                original_prompt=str(
                    active_slide_flow.get("original_prompt") or clean_query
                ).strip(),
                answers=answers,
            )
            return await self._record_turn(
                session=session,
                user_id=user_id,
                query=clean_query,
                standalone_query=standalone_query,
                answer=decision.message,
                model_name=str(generation_config["model"]),
                effort=str(generation_config["effort"]),
                generation_config=generation_config,
                metadata=metadata,
                citations=[],
                attachments=message_attachments,
            )

        if canvas_enabled or slide_count is not None:
            slide_intent = "slide_creation"
        else:
            slide_intent = (
                await self.slide_intent_service.classify(
                    clean_query,
                    history,
                    generation_config,
                    history_summary=session.history_summary,
                )
            ).intent

        if slide_intent == "slide_creation":
            standalone_query = clean_query
            max_slide_count = self._max_slide_count(user_id)
            decision = await self.slide_intent_service.start(
                clean_query,
                history,
                generation_config,
                max_slide_count=max_slide_count,
                requested_slide_count=slide_count,
                document_attached=document_attached,
            )
            metadata = self._generation_metadata(generation_config)
            metadata["slide_flow"] = self._slide_flow_metadata(
                decision,
                original_prompt=clean_query,
                answers=[],
            )
            return await self._record_turn(
                session=session,
                user_id=user_id,
                query=clean_query,
                standalone_query=standalone_query,
                answer=decision.message,
                model_name=str(generation_config["model"]),
                effort=str(generation_config["effort"]),
                generation_config=generation_config,
                metadata=metadata,
                citations=[],
                attachments=message_attachments,
            )

        standalone_query = await self._contextualize(
            clean_query, session.history_summary, history, generation_config
        )

        retrieved, rag_plan = await self._retrieve_with_plan(
            session=session,
            query=standalone_query,
            history=history,
            generation_config=generation_config,
            document_attached=document_attached,
            slide_request=False,
        )

        prompt_messages = self._build_prompt(
            session.history_summary,
            history,
            standalone_query,
            retrieved.context,
            detect_language(clean_query),
        )
        answer = (await self._complete(prompt_messages, generation_config)).strip()
        if not answer:
            raise RuntimeError("Chatbot returned an empty answer")

        metadata = self._generation_metadata(generation_config, retrieved)
        metadata["rag_plan"] = rag_plan.as_dict()
        return await self._record_turn(
            session=session,
            user_id=user_id,
            query=clean_query,
            standalone_query=standalone_query,
            answer=answer,
            model_name=str(generation_config["model"]),
            effort=str(generation_config["effort"]),
            generation_config=generation_config,
            metadata=metadata,
            citations=retrieved.citations,
            attachments=message_attachments,
        )

    async def _run_slide_generation(
        self,
        *,
        session: ChatSession,
        user_id: int,
        query: str,
        slide_prompt: str,
        standalone_query: str,
        model_name: str | None,
        effort: str | None,
        generation_config: dict[str, str | float | int],
        target_slide_count: int,
        history: list[ChatMessage],
        document_attached: bool,
        slide_callback: Callable[[str, dict[str, Any]], None] | None = None,
        slide_job_id: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChatTurnResult:
        if not self._begin_slide_generation(user_id, session.id, slide_job_id=slide_job_id):
            raise SlideGenerationInProgressError()
        try:
            return await self._generate_slide_turn(
                session=session,
                user_id=user_id,
                query=query,
                slide_prompt=slide_prompt,
                standalone_query=standalone_query,
                model_name=model_name,
                effort=effort,
                generation_config=generation_config,
                target_slide_count=target_slide_count,
                history=history,
                document_attached=document_attached,
                slide_callback=slide_callback,
                attachments=attachments,
            )
        finally:
            self._end_slide_generation(user_id, session.id, job_id=slide_job_id)

    async def _generate_slide_turn(
        self,
        *,
        session: ChatSession,
        user_id: int,
        query: str,
        slide_prompt: str,
        standalone_query: str,
        model_name: str | None,
        effort: str | None,
        generation_config: dict[str, str | float | int],
        target_slide_count: int,
        history: list[ChatMessage],
        document_attached: bool,
        slide_callback: Callable[[str, dict[str, Any]], None] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChatTurnResult:
        if self.slide_generator is None:
            raise RuntimeError("Slide generation is not available")
        self._validate_slide_count(user_id, target_slide_count)

        self._emit_slide_event(
            slide_callback,
            "status",
            {
                "stage": "retrieval",
                "title": "Preparing content",
                "description": "Preparing document context for the presentation...",
                "message": "Preparing content",
            },
        )
        retrieved, rag_plan = await self._retrieve_with_plan(
            session=session,
            query=slide_prompt,
            history=history,
            generation_config=generation_config,
            document_attached=document_attached,
            slide_request=True,
            brief=slide_prompt,
            target_slide_count=target_slide_count,
        )
        generation_kwargs: dict[str, Any] = {
            "session": session,
            "prompt": slide_prompt,
            "retrieved_context": retrieved.context,
            "model_name": model_name,
            "effort": effort,
            "target_slide_count": target_slide_count,
            "document_images": self._session_document_images(session),
        }
        if slide_callback is not None:
            generation_kwargs["callback"] = slide_callback
        slide_result = await self.slide_generator.generate(**generation_kwargs)
        answer = (
            f"Đã tạo project '{slide_result.project_name}' với "
            f"{slide_result.slide_count} slide."
        )
        metadata = self._generation_metadata(generation_config, retrieved)
        metadata["rag_plan"] = rag_plan.as_dict()
        metadata["slide_generation"] = {
            "project_id": slide_result.project_id,
            "project_name": slide_result.project_name,
            "slide_count": slide_result.slide_count,
            "target_slide_count": target_slide_count,
        }
        # Close the preflight state so a later message cannot re-enter the
        # previous awaiting-confirmation branch after the project is created.
        metadata["slide_flow"] = {
            "state": "completed",
            "brief": slide_prompt,
            "question": None,
            "options": [],
            "answers": [],
            "target_slide_count": target_slide_count,
            "max_slide_count": self._max_slide_count(user_id),
            "question_kind": None,
        }
        return await self._record_turn(
            session=session,
            user_id=user_id,
            query=query,
            standalone_query=standalone_query,
            answer=answer,
            model_name=str(generation_config["model"]),
            effort=str(generation_config["effort"]),
            generation_config=generation_config,
            metadata=metadata,
            citations=retrieved.citations,
            project_id=slide_result.project_id,
            attachments=attachments,
        )

    @staticmethod
    def _emit_slide_event(
        callback: Callable[[str, dict[str, Any]], None] | None,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Keep progress transport failures isolated from slide generation."""
        if callback is None:
            return
        try:
            callback(event_type, data)
        except Exception:
            logger.exception("Chat slide progress callback failed")

    async def _record_turn(
        self,
        *,
        session: ChatSession,
        user_id: int,
        query: str,
        standalone_query: str,
        answer: str,
        model_name: str,
        effort: str,
        generation_config: dict[str, str | float | int],
        metadata: dict[str, Any],
        citations: list[dict],
        project_id: int | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChatTurnResult:
        if attachments:
            metadata = {**metadata, "attachments": attachments}
        user_message, assistant_message = self.repository.append_turn(
            session.id,
            user_id,
            query=query,
            standalone_query=standalone_query,
            answer=answer,
            model=model_name,
            effort=effort,
            project_id=project_id,
            metadata=metadata,
            citations=citations,
        )
        await self._compact_if_needed(session, user_id, generation_config)
        refreshed = self.repository.get_session(session.id, user_id) or session
        return ChatTurnResult(
            session=refreshed,
            user_message=user_message,
            assistant_message=assistant_message,
            standalone_query=standalone_query,
            citations=citations,
            project_id=project_id,
        )

    async def _retrieve_with_plan(
        self,
        *,
        session: ChatSession,
        query: str,
        history: list[ChatMessage],
        generation_config: dict[str, str | float | int],
        document_attached: bool,
        slide_request: bool,
        brief: str | None = None,
        target_slide_count: int | None = None,
    ) -> tuple[RetrievedContext, RagQueryPlan]:
        """Plan document use first, then execute the chosen retrieval queries."""
        plan = await self.rag_query_planner.plan(
            query,
            history,
            generation_config,
            document_attached=document_attached,
            slide_request=slide_request,
            brief=brief,
        )
        empty_context = RetrievedContext(context="", citations=[])
        if (
            not plan.needs_rag
            or plan.source_policy == "conversation_only"
            or not plan.queries
            or self.context_provider is None
        ):
            return empty_context, plan

        retrieve_many = getattr(self.context_provider, "retrieve_many", None)
        if callable(retrieve_many):
            retrieval_kwargs = {
                "mode": plan.mode,
                "include_root": plan.include_root,
                "include_ancestors": plan.include_ancestors,
                "include_siblings": plan.include_siblings,
                "max_detail_nodes": plan.max_detail_nodes,
                "target_slide_count": target_slide_count,
            }
            try:
                retrieved = await retrieve_many(
                    session,
                    list(plan.queries),
                    **retrieval_kwargs,
                )
            except TypeError as exc:
                # Keep older external context adapters usable while making the
                # built-in hierarchical service receive the complete plan.
                if "unexpected keyword" not in str(exc).lower():
                    raise
                retrieved = await retrieve_many(session, list(plan.queries))
            return retrieved, plan

        # Keep third-party context adapters compatible with the old one-query
        # protocol while the built-in DocumentRagService uses one batched call.
        retrieve = getattr(self.context_provider, "retrieve", None)
        if not callable(retrieve):
            return empty_context, plan
        contexts = await asyncio.gather(
            *(retrieve(session, query) for query in plan.queries)
        )
        return self._merge_retrieved_contexts(contexts), plan

    @staticmethod
    def _merge_retrieved_contexts(
        contexts: list[RetrievedContext],
    ) -> RetrievedContext:
        context_parts: list[str] = []
        citations: list[dict[str, Any]] = []
        seen_citations: set[tuple[str, str]] = set()
        for retrieved in contexts:
            if retrieved.context.strip():
                context_parts.append(retrieved.context.strip())
            for citation in retrieved.citations:
                key = (
                    str(citation.get("document_id") or ""),
                    str(citation.get("chunk_id") or ""),
                )
                if key in seen_citations:
                    continue
                seen_citations.add(key)
                citations.append(citation)
        return RetrievedContext(
            context="\n\n".join(context_parts),
            citations=citations,
        )

    @staticmethod
    def _normalize_document_ids(document_ids: list[str] | None) -> list[str]:
        """Keep attachment ids deterministic and free of duplicate entries."""
        if not document_ids:
            return []
        normalized: list[str] = []
        seen: set[str] = set()
        for raw_id in document_ids:
            document_id = str(raw_id).strip()
            if not document_id or document_id in seen:
                continue
            seen.add(document_id)
            normalized.append(document_id)
        return normalized

    def _resolve_document_attachments(
        self,
        session: ChatSession,
        document_ids: list[str] | None,
    ) -> list[dict[str, Any]]:
        """Resolve documents linked to this session for the message attachment.

        ``processing`` is valid here because a confirmed slide-stream job can
        start before its deferred DOCX analysis finishes; the job's normal
        chat turn completes that work before retrieval.
        """
        normalized_ids = self._normalize_document_ids(document_ids)
        if not normalized_ids:
            return []
        if self.context_provider is None:
            raise ValueError("Document attachments are not available")

        list_documents = getattr(self.context_provider, "list_session_documents", None)
        if not callable(list_documents):
            raise ValueError("Document attachments are not available")
        documents = list_documents(session.id, session.user_id)
        attachable_documents = {
            str(document.id): document
            for document in documents
            if str(document.status).lower() in {"ready", "processing"}
        }
        missing_ids = [
            document_id
            for document_id in normalized_ids
            if document_id not in attachable_documents
        ]
        if missing_ids:
            raise ValueError("Tài liệu chưa sẵn sàng hoặc không thuộc phiên chat")

        attachments: list[dict[str, Any]] = []
        for document_id in normalized_ids:
            document = attachable_documents[document_id]
            display_name = str(
                document.title or document.original_filename or "Document"
            ).strip()
            attachments.append(
                {
                    "id": document_id,
                    "name": display_name or "Document",
                    "original_filename": str(document.original_filename),
                }
            )
        return attachments

    def _session_document_images(self, session: ChatSession) -> list[dict[str, Any]]:
        """Return private image assets from ready documents in this session."""
        if self.context_provider is None:
            return []
        list_documents = getattr(self.context_provider, "list_session_documents", None)
        if not callable(list_documents):
            return []
        images: list[dict[str, Any]] = []
        for document in list_documents(session.id, session.user_id):
            if str(getattr(document, "status", "")).lower() != "ready":
                continue
            for image in getattr(document, "images", []) or []:
                if isinstance(image, dict):
                    images.append(dict(image))
        return images

    @staticmethod
    def _generation_metadata(
        generation_config: dict[str, str | float | int],
        retrieved: RetrievedContext | None = None,
    ) -> dict[str, Any]:
        citations = retrieved.citations if retrieved is not None else []
        return {
            "provider_model": generation_config["provider_model"],
            "temperature": generation_config["temperature"],
            "max_tokens": generation_config["max_tokens"],
            "top_p": generation_config["top_p"],
            "retrieval": {
                "enabled": bool(citations),
                "citations": citations,
            },
        }

    @staticmethod
    def _slide_flow_metadata(
        decision: SlideFlowDecision,
        *,
        original_prompt: str,
        answers: list[dict[str, str]],
    ) -> dict[str, Any]:
        return {
            "state": decision.state,
            "original_prompt": original_prompt,
            "brief": decision.brief,
            "question": decision.question,
            "answers": answers,
            "options": [option.as_dict() for option in decision.options],
            "target_slide_count": decision.target_slide_count,
            "max_slide_count": decision.max_slide_count,
            "question_kind": decision.question_kind,
        }

    def get_slide_generation_limits(self, user_id: int) -> dict[str, Any]:
        """Expose the active plan limit to the chatbot UI."""
        if self.user_repository is None:
            return {"tier": "free", "max_slide_count": 50}
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise LookupError("User not found")
        return {
            "tier": user.subscription_tier,
            "max_slide_count": self._max_slide_count(user_id),
        }

    def start_chat_message(
        self,
        session_id: str,
        user_id: int,
        query: str,
        *,
        model_name: str | None = None,
        effort: str | None = None,
        slide_count: int | None = None,
        document_ids: list[str] | None = None,
    ) -> ChatMessageJob:
        """Start an ordinary chat turn independently of the HTTP connection.

        The request that opens the SSE stream only creates/subscribes to this
        job.  The actual LLM/RAG work continues in the service task when the
        browser changes route, refreshes, or loses its network connection.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Message cannot be empty")
        if len(clean_query) > 12_000:
            raise ValueError("Message is too long")

        session = self.repository.get_session(session_id, user_id)
        if session is None or session.archived:
            raise LookupError("Chat session not found")

        normalized_document_ids = self._normalize_document_ids(document_ids)
        attachments = self._resolve_document_attachments(
            session, normalized_document_ids
        )
        generation_config = resolve_chatbot_generation_config(model_name, effort)
        if self.subscription_service is not None:
            generation_config["usage_cost"] = self.subscription_service.get_chat_usage_cost(
                str(generation_config["model"]),
                str(generation_config["effort"]),
            )

        loop = asyncio.get_running_loop()
        with self._active_slide_generations_lock:
            active_job_id = self._active_chat_message_jobs.get(user_id)
            if active_job_id is not None:
                active_job = self._chat_message_jobs.get(active_job_id)
                if (
                    active_job is not None
                    and active_job.session_id == session_id
                    and active_job.query == clean_query
                    and active_job.model_name == model_name
                    and active_job.effort == effort
                    and active_job.document_ids == normalized_document_ids
                ):
                    return active_job
                raise ChatMessageInProgressError()

            if self.subscription_service is not None:
                # Preflight before scheduling so the stream gets a useful
                # HTTP error and the usage is consumed exactly once by the
                # detached task after it starts successfully.
                self.subscription_service.check_feature_access_for_user(
                    user_id,
                    "chat_message",
                    usage_cost=float(generation_config.get("usage_cost", 1.0)),
                )

            job = ChatMessageJob(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                query=clean_query,
                model_name=model_name,
                effort=effort,
                slide_count=slide_count,
                loop=loop,
                document_ids=normalized_document_ids,
                attachments=attachments,
                state={
                    "phase": "running",
                    "status": {
                        "stage": "thinking",
                        "title": "Thinking",
                        "description": "Đang chuẩn bị câu trả lời...",
                        "message": "Thinking",
                    },
                    "error": "",
                },
            )
            self._chat_message_jobs[job.id] = job
            self._active_chat_message_jobs[user_id] = job.id

        self._publish_chat_message_event(job, "status", job.state["status"])
        job.task = asyncio.create_task(
            self._run_chat_message_job(job),
            name=f"chat-message-{job.id}",
        )
        return job

    def get_active_chat_message(self, user_id: int) -> dict[str, Any] | None:
        with self._active_slide_generations_lock:
            job_id = self._active_chat_message_jobs.get(user_id)
            job = self._chat_message_jobs.get(job_id) if job_id else None
            return self._chat_message_snapshot(job) if job else None

    def cancel_active_chat_message(self, user_id: int) -> bool:
        """Interrupt the user's current ordinary chat response."""
        with self._active_slide_generations_lock:
            job_id = self._active_chat_message_jobs.get(user_id)
            job = self._chat_message_jobs.get(job_id) if job_id else None
            if job is None or job.finished:
                return False

            status = {
                "stage": "cancelled",
                "title": "Stopped",
                "description": "The response was interrupted.",
                "message": "Stopped",
            }
            job.finished = True
            job.state["phase"] = "cancelled"
            job.state["status"] = status
            event = (len(job.events) + 1, "cancelled", status)
            job.events.append(event)
            subscribers = list(job.subscribers)
            task = job.task
            if self._active_chat_message_jobs.get(user_id) == job.id:
                self._active_chat_message_jobs.pop(user_id, None)

        if task is not None and not task.done():
            task.cancel()
        for queue in subscribers:
            if not job.loop.is_closed():
                job.loop.call_soon_threadsafe(queue.put_nowait, event)
        return True

    def subscribe_chat_message(
        self,
        job_id: str,
        user_id: int,
    ) -> tuple[ChatMessageJob, asyncio.Queue[tuple[int, str, dict[str, Any]]]]:
        """Subscribe to all known events and future events for a chat job."""
        with self._active_slide_generations_lock:
            job = self._chat_message_jobs.get(job_id)
            if job is None or job.user_id != user_id:
                raise LookupError("Chat message job not found")
            queue: asyncio.Queue[tuple[int, str, dict[str, Any]]] = asyncio.Queue()
            for event in job.events:
                queue.put_nowait(event)
            if not job.finished:
                job.subscribers.add(queue)
            return job, queue

    def unsubscribe_chat_message(
        self,
        job: ChatMessageJob,
        queue: asyncio.Queue[tuple[int, str, dict[str, Any]]],
    ) -> None:
        with self._active_slide_generations_lock:
            job.subscribers.discard(queue)

    def _publish_chat_message_event(
        self,
        job: ChatMessageJob,
        event_type: str,
        data: dict[str, Any] | None,
    ) -> None:
        payload = dict(data or {})
        with self._active_slide_generations_lock:
            sequence = len(job.events) + 1
            event = (sequence, str(event_type), payload)
            job.events.append(event)
            self._apply_chat_message_event(job, event[1], payload)
            if event[1] in {"complete", "error_event", "cancelled"}:
                job.finished = True
            subscribers = list(job.subscribers)

        for queue in subscribers:
            if job.loop.is_closed():
                continue
            job.loop.call_soon_threadsafe(queue.put_nowait, event)

    @staticmethod
    def _apply_chat_message_event(
        job: ChatMessageJob,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        if event_type == "status":
            job.state["status"] = {
                "stage": str(data.get("stage") or "thinking"),
                "title": str(data.get("title") or "Thinking"),
                "description": str(data.get("description") or ""),
                "message": str(data.get("message") or ""),
            }
            return
        if event_type == "complete":
            job.state["phase"] = "completed"
            job.state["status"] = {
                "stage": "completed",
                "title": "Completed",
                "description": "Câu trả lời đã được lưu vào cuộc trò chuyện.",
                "message": "Completed",
            }
            job.state["result"] = data.get("result")
            return
        if event_type == "error_event":
            message = str(data.get("message") or "Không thể nhận phản hồi lúc này.")
            job.state["phase"] = "error"
            job.state["error"] = message
            job.state["status"] = {
                "stage": "error",
                "title": "Chat failed",
                "description": message,
                "message": "Something went wrong",
            }
            return
        if event_type == "cancelled":
            job.state["phase"] = "cancelled"
            job.state["status"] = {
                "stage": "cancelled",
                "title": "Stopped",
                "description": "The response was interrupted.",
                "message": "Stopped",
            }

    @staticmethod
    def _chat_message_snapshot(job: ChatMessageJob | None) -> dict[str, Any] | None:
        if job is None:
            return None
        return {
            "id": job.id,
            "session_id": job.session_id,
            "phase": job.state.get("phase", "running"),
            "status": dict(job.state.get("status") or {}),
            "query": job.query,
            "model": job.model_name,
            "effort": job.effort,
            "slide_count": job.slide_count,
            "document_ids": list(job.document_ids),
            "attachments": [dict(item) for item in job.attachments],
            "error": str(job.state.get("error") or ""),
        }

    async def _run_chat_message_job(self, job: ChatMessageJob) -> None:
        try:
            result = await self.send_message(
                job.session_id,
                job.user_id,
                job.query,
                model_name=job.model_name,
                effort=job.effort,
                canvas_enabled=False,
                slide_count=job.slide_count,
                document_ids=job.document_ids,
            )
            self._publish_chat_message_event(
                job,
                "complete",
                {"result": asdict(result)},
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Detached chat message failed for job %s", job.id)
            detail = getattr(exc, "detail", None)
            if isinstance(detail, dict):
                message = str(detail.get("message") or detail.get("detail") or exc)
            else:
                message = str(detail or exc).strip()
            self._publish_chat_message_event(
                job,
                "error_event",
                {
                    "message": message or "Không thể nhận phản hồi lúc này.",
                    "code": "chat_failed",
                },
            )
        finally:
            self._end_chat_message_job(job.user_id, job.id)

    def _end_chat_message_job(self, user_id: int, job_id: str) -> None:
        with self._active_slide_generations_lock:
            if self._active_chat_message_jobs.get(user_id) == job_id:
                self._active_chat_message_jobs.pop(user_id, None)

    def start_slide_generation(
        self,
        session_id: str,
        user_id: int,
        query: str,
        *,
        model_name: str | None = None,
        effort: str | None = None,
        slide_count: int | None = None,
        document_ids: list[str] | None = None,
    ) -> SlideGenerationJob:
        """Start a detached slide job and return its reconnectable handle.

        The HTTP stream is deliberately not the owner of the generation task.
        A browser reload only removes a subscriber; the job remains owned by
        this application service and can be observed again by job id.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Message cannot be empty")
        session = self.repository.get_session(session_id, user_id)
        if session is None or session.archived:
            raise LookupError("Chat session not found")
        normalized_document_ids = self._normalize_document_ids(document_ids)
        self._resolve_document_attachments(session, normalized_document_ids)
        generation_config = resolve_chatbot_generation_config(model_name, effort)
        if self.subscription_service is not None:
            generation_config["usage_cost"] = self.subscription_service.get_chat_usage_cost(
                str(generation_config["model"]),
                str(generation_config["effort"]),
            )

        loop = asyncio.get_running_loop()
        with self._active_slide_generations_lock:
            active_job_id = self._active_slide_generation_jobs.get(user_id)
            if active_job_id is not None:
                active_job = self._slide_generation_jobs.get(active_job_id)
                if active_job is not None and active_job.session_id == session_id:
                    return active_job
                raise SlideGenerationInProgressError()
            if user_id in self._active_slide_generations:
                raise SlideGenerationInProgressError()

            if self.subscription_service is not None:
                # Preflight the quota synchronously so a stream request gets a
                # useful HTTP 429 instead of starting a job that fails later.
                self.subscription_service.check_feature_access_for_user(
                    user_id,
                    "chat_message",
                    usage_cost=float(generation_config.get("usage_cost", 1.0)),
                )

            job = SlideGenerationJob(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                query=clean_query,
                model_name=model_name,
                effort=effort,
                slide_count=slide_count,
                loop=loop,
                document_ids=normalized_document_ids,
                state={
                    "phase": "running",
                    "status": {
                        "stage": "starting",
                        "title": "Starting slide generation",
                        "description": "The confirmed request is being prepared...",
                        "message": "Starting slide generation",
                    },
                    "progress": 0.0,
                    "slides": [],
                    "total_slides": slide_count,
                    "target_slide_count": slide_count,
                    "project_id": None,
                    "project_name": "",
                    "error": "",
                },
            )
            self._slide_generation_jobs[job.id] = job
            # Reserve the user before scheduling the coroutine so two tabs
            # cannot both pass the generation guard during the same tick.
            self._active_slide_generations[user_id] = session_id
            self._active_slide_generation_jobs[user_id] = job.id

        self._publish_slide_generation_event(
            job,
            "status",
            job.state["status"],
        )
        job.task = asyncio.create_task(
            self._run_slide_generation_job(job),
            name=f"slide-generation-{job.id}",
        )
        return job

    def get_active_slide_generation(self, user_id: int) -> dict[str, Any] | None:
        with self._active_slide_generations_lock:
            job_id = self._active_slide_generation_jobs.get(user_id)
            job = self._slide_generation_jobs.get(job_id) if job_id else None
            return self._slide_generation_snapshot(job) if job else None

    def get_slide_generation(
        self, generation_id: str, user_id: int
    ) -> SlideGenerationJob | None:
        with self._active_slide_generations_lock:
            job = self._slide_generation_jobs.get(generation_id)
            if job is None or job.user_id != user_id:
                return None
            return job

    def subscribe_slide_generation(
        self, generation_id: str, user_id: int
    ) -> tuple[SlideGenerationJob, asyncio.Queue[tuple[int, str, dict[str, Any]]]]:
        """Subscribe to the complete event history plus future events."""
        with self._active_slide_generations_lock:
            job = self._slide_generation_jobs.get(generation_id)
            if job is None or job.user_id != user_id:
                raise LookupError("Slide generation not found")
            queue: asyncio.Queue[tuple[int, str, dict[str, Any]]] = asyncio.Queue()
            for event in job.events:
                queue.put_nowait(event)
            if not job.finished:
                job.subscribers.add(queue)
            return job, queue

    def unsubscribe_slide_generation(
        self,
        job: SlideGenerationJob,
        queue: asyncio.Queue[tuple[int, str, dict[str, Any]]],
    ) -> None:
        with self._active_slide_generations_lock:
            job.subscribers.discard(queue)

    @staticmethod
    def _event_int(value: Any) -> int | None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        return parsed

    def _publish_slide_generation_event(
        self,
        job: SlideGenerationJob,
        event_type: str,
        data: dict[str, Any] | None,
    ) -> None:
        payload = dict(data or {})
        with self._active_slide_generations_lock:
            sequence = len(job.events) + 1
            event = (sequence, str(event_type), payload)
            job.events.append(event)
            self._apply_slide_generation_event(job, event[1], payload)
            if event[1] in {"complete", "error_event", "limit_event"}:
                job.finished = True
            subscribers = list(job.subscribers)

        # Workflow callbacks may be invoked by a parallel renderer worker, so
        # wake subscribers through the event loop instead of touching an
        # asyncio.Queue directly from that worker thread.
        for queue in subscribers:
            if job.loop.is_closed():
                continue
            job.loop.call_soon_threadsafe(queue.put_nowait, event)

    def _apply_slide_generation_event(
        self,
        job: SlideGenerationJob,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        state = job.state
        if event_type == "status":
            state["status"] = {
                "stage": str(data.get("stage") or "starting"),
                "title": str(data.get("title") or "Creating slides"),
                "description": str(data.get("description") or ""),
                "message": str(data.get("message") or ""),
            }
            return

        if event_type == "progress":
            current = self._event_int(data.get("current"))
            total = self._event_int(data.get("total"))
            percentage = data.get("percentage")
            try:
                progress = float(percentage)
            except (TypeError, ValueError):
                progress = (
                    current / total * 100
                    if current is not None and total and total > 0
                    else float(state.get("progress") or 0)
                )
            state["progress"] = min(100.0, max(0.0, progress))
            if total and total > 0:
                state["total_slides"] = total
            current_message = str(data.get("message") or "").strip()
            if current_message:
                state["status"] = {
                    **state.get("status", {}),
                    "stage": "design",
                    "title": str(data.get("title") or "Creating slides"),
                    "message": current_message,
                }
            return

        if event_type == "slide_completed":
            index = self._event_int(data.get("index"))
            if index is None:
                return
            path = str(data.get("xml_path") or data.get("content_path") or "")
            slide = {
                "index": index,
                "title": str(data.get("title") or f"Slide {index + 1}"),
                "content_path": path,
                "xml_path": path,
            }
            slides = [
                item for item in state.get("slides", [])
                if int(item.get("index", -1)) != index
            ]
            slides.append(slide)
            state["slides"] = sorted(slides, key=lambda item: int(item["index"]))
            total = self._event_int(data.get("total"))
            current = self._event_int(data.get("current"))
            if total and total > 0:
                state["total_slides"] = total
            if current is not None and total and total > 0:
                state["progress"] = min(100.0, max(0.0, current / total * 100))
            return

        if event_type == "complete":
            state["phase"] = "completed"
            state["progress"] = 100.0
            project_id = self._event_int(data.get("project_id"))
            if project_id is not None:
                state["project_id"] = project_id
            state["project_name"] = str(data.get("project_name") or state.get("project_name") or "")
            total = self._event_int(data.get("total_slides"))
            if total and total > 0:
                state["total_slides"] = total
            state["status"] = {
                "stage": "completed",
                "title": "Completed",
                "description": "The deck has been saved to your project.",
                "message": "Completed",
            }
            return

        if event_type in {"error_event", "limit_event"}:
            message = str(data.get("message") or "Unable to create slides right now.")
            state["phase"] = "error"
            state["error"] = message
            state["status"] = {
                "stage": "error",
                "title": "Slide generation failed",
                "description": message,
                "message": "Something went wrong",
            }

    @staticmethod
    def _slide_generation_snapshot(job: SlideGenerationJob | None) -> dict[str, Any] | None:
        if job is None:
            return None
        state = job.state
        return {
            "id": job.id,
            "session_id": job.session_id,
            "phase": state.get("phase", "running"),
            "status": dict(state.get("status") or {}),
            "progress": float(state.get("progress") or 0),
            "slides": [dict(slide) for slide in state.get("slides", [])],
            "total_slides": state.get("total_slides"),
            "target_slide_count": state.get("target_slide_count"),
            "project_id": state.get("project_id"),
            "project_name": str(state.get("project_name") or ""),
            "error": str(state.get("error") or ""),
        }

    async def _run_slide_generation_job(self, job: SlideGenerationJob) -> None:
        try:
            result = await self.send_message(
                job.session_id,
                job.user_id,
                job.query,
                model_name=job.model_name,
                effort=job.effort,
                canvas_enabled=False,
                slide_count=job.slide_count,
                document_ids=job.document_ids,
                slide_callback=lambda event_type, data: self._publish_slide_generation_event(
                    job, event_type, data
                ),
                slide_job_id=job.id,
            )
            assistant_metadata = result.assistant_message.metadata
            slide_metadata = (
                assistant_metadata.get("slide_generation")
                if isinstance(assistant_metadata, dict)
                else None
            )
            if not isinstance(slide_metadata, dict):
                slide_metadata = {}
            self._publish_slide_generation_event(
                job,
                "complete",
                {
                    "project_id": result.project_id,
                    "project_name": slide_metadata.get("project_name"),
                    "total_slides": slide_metadata.get("slide_count", 0),
                },
            )
        except asyncio.CancelledError:
            raise
        except SlideCountLimitError as exc:
            self._publish_slide_generation_event(
                job,
                "limit_event",
                {
                    "code": "slide_count_limit",
                    "requested": exc.requested,
                    "max_slide_count": exc.maximum,
                    "tier": exc.tier,
                    "message": str(exc),
                },
            )
        except SlideGenerationInProgressError as exc:
            self._publish_slide_generation_event(
                job,
                "error_event",
                {"message": str(exc), "code": "generation_in_progress"},
            )
        except LookupError:
            self._publish_slide_generation_event(
                job,
                "error_event",
                {"message": "Không tìm thấy phiên chat", "code": "not_found"},
            )
        except ValueError as exc:
            self._publish_slide_generation_event(
                job,
                "error_event",
                {
                    "message": _friendly_slide_generation_error(exc),
                    "code": "invalid_request",
                },
            )
        except Exception:
            logger.exception("Detached chat slide generation failed for job %s", job.id)
            self._publish_slide_generation_event(
                job,
                "error_event",
                {
                    "message": "Không thể tạo slide lúc này. Vui lòng thử lại.",
                    "code": "generation_failed",
                },
            )
        finally:
            self._end_slide_generation(job.user_id, job.session_id, job_id=job.id)

    def _active_slide_session(self, user_id: int) -> str | None:
        with self._active_slide_generations_lock:
            return self._active_slide_generations.get(user_id)

    def _begin_slide_generation(
        self,
        user_id: int,
        session_id: str,
        *,
        slide_job_id: str | None = None,
    ) -> bool:
        with self._active_slide_generations_lock:
            current_session = self._active_slide_generations.get(user_id)
            current_job_id = self._active_slide_generation_jobs.get(user_id)
            if current_session is not None and current_session != session_id:
                return False
            if current_job_id is not None and current_job_id != slide_job_id:
                return False
            self._active_slide_generations[user_id] = session_id
            if slide_job_id is not None:
                self._active_slide_generation_jobs[user_id] = slide_job_id
            return True

    def _end_slide_generation(
        self,
        user_id: int,
        session_id: str,
        *,
        job_id: str | None = None,
    ) -> None:
        with self._active_slide_generations_lock:
            if self._active_slide_generations.get(user_id) == session_id:
                self._active_slide_generations.pop(user_id, None)
            if job_id is None or self._active_slide_generation_jobs.get(user_id) == job_id:
                self._active_slide_generation_jobs.pop(user_id, None)

    def _max_slide_count(self, user_id: int) -> int:
        if self.user_repository is None:
            return -1
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise LookupError("User not found")
        if self.subscription_service is not None:
            return self.subscription_service.get_max_slide_count(user)
        return int(user.get_usage_limits().get("max_docx_slides", -1))

    def _validate_slide_count(self, user_id: int, slide_count: int) -> int:
        if self.user_repository is None:
            return int(slide_count)
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise LookupError("User not found")
        if self.subscription_service is not None:
            return self.subscription_service.validate_slide_count(user, slide_count)
        requested = int(slide_count)
        maximum = int(user.get_usage_limits().get("max_docx_slides", -1))
        if maximum != -1 and requested > maximum:
            raise SlideCountLimitError(requested, maximum, user.subscription_tier)
        return requested

    @staticmethod
    def _flow_slide_count(flow: dict[str, Any]) -> int | None:
        value = flow.get("target_slide_count")
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        return parsed if parsed > 0 else None

    @staticmethod
    def _latest_slide_flow(history: list[ChatMessage]) -> dict[str, Any] | None:
        for message in reversed(history):
            if message.role != "assistant":
                continue
            if not isinstance(message.metadata, dict):
                return None
            flow = message.metadata.get("slide_flow")
            return flow if isinstance(flow, dict) else None
        return None

    @staticmethod
    def _flow_answers_with_latest_input(
        flow: dict[str, Any],
        answer: str,
    ) -> list[dict[str, str]]:
        answers = [
            {
                "question": str(item.get("question") or "").strip(),
                "answer": str(item.get("answer") or "").strip(),
            }
            for item in flow.get("answers", [])
            if isinstance(item, dict)
        ]
        question = str(flow.get("question") or "Bổ sung yêu cầu").strip()
        if answer.strip():
            answers.append({"question": question, "answer": answer.strip()})
        return answers

    def _has_ready_documents(self, session: ChatSession) -> bool:
        """Ask the RAG boundary whether this session has a usable document."""
        if self.context_provider is None:
            return False
        checker = getattr(self.context_provider, "has_ready_documents", None)
        if not callable(checker):
            return False
        try:
            return bool(checker(session))
        except Exception:
            logger.exception("Unable to inspect attached chatbot documents")
            return False

    async def _ensure_documents_ready(
        self,
        session: ChatSession,
        document_ids: list[str],
    ) -> None:
        """Complete deferred DOCX analysis before the turn uses its context."""
        if not document_ids or self.context_provider is None:
            return
        preparer = getattr(self.context_provider, "ensure_documents_ready", None)
        if not callable(preparer):
            return
        await preparer(session=session, document_ids=document_ids)

    async def _contextualize(
        self,
        query: str,
        history_summary: str | None,
        history: list[ChatMessage],
        generation_config: dict[str, str | float | int],
    ) -> str:
        if not history and not history_summary:
            return query
        history_text = self._format_messages(history[-6:])
        response = await self._complete(
            [
                {"role": "system", "content": self._CONTEXTUALIZE_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Summary of earlier context:\n{history_summary or '(none)'}\n\n"
                        f"Recent conversation:\n{history_text}\n\n"
                        f"Latest message:\n{query}"
                    ),
                },
            ],
            generation_config,
        )
        return response.strip() or query

    def _build_prompt(
        self,
        history_summary: str | None,
        history: list[ChatMessage],
        standalone_query: str,
        context: str,
        language: Literal["vi", "en"],
    ) -> list[dict[str, str]]:
        system = f"{self._SYSTEM_PROMPT}\n\n{language_instruction(language)}"
        if history_summary:
            system += f"\n\nConversation memory:\n{history_summary}"
        if context:
            system += (
                "\n\nRetrieved document context follows. Use it as the source of truth "
                "and say when it does not contain the requested information. "
                "When a claim comes from a retrieved source, cite it as [Source N].\n"
                + context
            )
        messages = [{"role": "system", "content": system}]
        messages.extend(
            {"role": message.role, "content": message.content}
            for message in history[-10:]
            if message.role in {"user", "assistant"}
        )
        messages.append({"role": "user", "content": standalone_query})
        return messages

    async def _compact_if_needed(
        self,
        session: ChatSession,
        user_id: int,
        generation_config: dict[str, str | float | int],
    ) -> None:
        messages = self.repository.list_messages(session.id, user_id, limit=1000)
        max_entries = session.max_turns * 2
        if len(messages) <= max_entries:
            return
        older = messages[:-max_entries]
        recent_context = self._format_messages(older)
        summary = await self._complete(
            [
                {"role": "system", "content": self._COMPACT_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Previous summary:\n{session.history_summary or '(none)'}\n\n"
                        f"Older conversation:\n{recent_context}"
                    ),
                },
            ],
            generation_config,
        )
        if summary.strip():
            self.repository.update_history_summary(session.id, user_id, summary.strip())

    @staticmethod
    def _format_messages(messages: list[ChatMessage]) -> str:
        if not messages:
            return "(none)"
        return "\n".join(
            f"{message.role.title()}: {message.content}" for message in messages
        )

    async def _complete(
        self,
        messages: list[dict[str, str]],
        generation_config: dict[str, str | float | int],
    ) -> str:
        """Call the existing synchronous LLM adapter without blocking FastAPI."""
        return await asyncio.to_thread(
            self.llm_provider.generate_completion,
            messages,
            model=str(generation_config["provider_model"]),
            max_tokens=int(generation_config["max_tokens"]),
            temperature=float(generation_config["temperature"]),
            top_p=float(generation_config["top_p"]),
        )
