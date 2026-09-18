from __future__ import annotations

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    project_id: int | None = None
    title: str | None = Field(default=None, max_length=160)


class ChatSessionOut(BaseModel):
    id: str
    project_id: int | None = None
    title: str | None = None
    history_summary: str | None = None
    max_turns: int
    created_at: str
    updated_at: str
    archived: bool = False


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=12_000)
    model: str | None = Field(default=None, max_length=80)
    effort: str | None = Field(default=None, max_length=20)
    canvas: bool = False
    # The upload is indexed before the message is sent. These ids make the
    # attachment explicit on the message while the RAG service keeps the
    # document scoped to the conversation.
    document_ids: list[str] = Field(default_factory=list, max_length=20)
    # Optional structured override used when the user confirms a slide plan.
    # The service still validates it against the active subscription plan.
    slide_count: int | None = Field(default=None, ge=1)


class ChatMessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    standalone_query: str | None = None
    model: str | None = None
    effort: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: str


class ChatTurnOut(BaseModel):
    session: ChatSessionOut
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    standalone_query: str
    citations: list[dict] = Field(default_factory=list)
    project_id: int | None = None


class ChatDocumentOut(BaseModel):
    id: str
    original_filename: str
    title: str | None = None
    status: str
    content_hash: str
    error_message: str | None = None
    created_at: str
    updated_at: str


class ChatbotModelConfigOut(BaseModel):
    id: str
    temperature: float
    top_p: float


class ChatbotEffortConfigOut(BaseModel):
    id: str
    max_tokens: int
    temperature_delta: float


class ChatbotConfigOut(BaseModel):
    default_model: str
    default_effort: str
    models: list[ChatbotModelConfigOut]
    efforts: list[ChatbotEffortConfigOut]
    max_slide_count: int


class ChatSlideGenerationOut(BaseModel):
    """Reconnectable state for a detached chatbot slide-generation job."""

    id: str
    session_id: str
    phase: str
    status: dict
    progress: float = 0
    slides: list[dict] = Field(default_factory=list)
    total_slides: int | None = None
    target_slide_count: int | None = None
    project_id: int | None = None
    project_name: str = ""
    error: str = ""
