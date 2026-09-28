import asyncio
from pathlib import Path

from PIL import Image

from backend.application.services import document_image_tool as image_tool_module
from backend.application.services.chatbot_service import ChatbotService
from backend.application.services.document_image_tool import DocumentImageTool
from backend.domain.entities.chat import ChatSession
from backend.domain.entities.chat_document import ChatDocument
from backend.domain.entities.chat_document import RetrievedContext


class _Repository:
    def __init__(self, documents):
        self.documents = documents

    def list_session_documents(self, session_id, user_id):
        return self.documents


def _document(image):
    return ChatDocument(
        id="doc-1",
        user_id=7,
        project_id=None,
        original_filename="notes.docx",
        title="Notes",
        status="ready",
        content_hash="hash",
        markdown_path=None,
        structure=[],
        error_message=None,
        created_at="now",
        updated_at="now",
        images=[image],
    )


def test_document_image_tool_returns_bounded_data_uri_and_hides_path(tmp_path, monkeypatch):
    monkeypatch.setattr(image_tool_module, "CHATBOT_DOCUMENTS_DIR", tmp_path)
    source = Path(tmp_path) / "doc-1_images" / "image.png"
    source.parent.mkdir()
    image = Image.new("RGB", (32, 32), (255, 120, 20))
    image.save(source, format="PNG")
    metadata = {
        "image_id": "doc-1:0",
        "source_path": str(source),
        "filename": "image.png",
        "section_path": "Overview",
    }
    tool = DocumentImageTool(_Repository([_document(metadata)]))

    result = tool.get_document_image(
        session_id="session-1",
        user_id=7,
        document_id="doc-1",
        image_id="doc-1:0",
    )

    assert result is not None
    assert result["data_uri"].startswith("data:image/")
    assert str(source) not in result["data_uri"]
    assert result["image_id"] == "doc-1:0"


def test_document_image_tool_rejects_document_outside_session(tmp_path, monkeypatch):
    monkeypatch.setattr(image_tool_module, "CHATBOT_DOCUMENTS_DIR", tmp_path)
    tool = DocumentImageTool(_Repository([]))

    assert (
        tool.get_document_image(
            session_id="session-1",
            user_id=7,
            document_id="doc-1",
            image_id="doc-1:0",
        )
        is None
    )


class _AnswerProvider:
    def __init__(self):
        self.multimodal_messages = None

    def generate_tool_calls(self, messages, tools, **kwargs):
        return {
            "content": "",
            "tool_calls": [
                {
                    "name": "get_document_image",
                    "args": {"document_id": "doc-1", "image_id": "doc-1:0"},
                }
            ],
        }

    def generate_completion(self, messages, **kwargs):
        self.multimodal_messages = messages
        return "Đây là nội dung nhìn thấy trong ảnh."


class _Tool:
    name = "get_document_image"

    @staticmethod
    def schema():
        return {"type": "function", "function": {"name": _Tool.name}}

    @staticmethod
    def get_document_image(**kwargs):
        return {
            "data_uri": "data:image/png;base64,ZmFrZQ==",
            "filename": "image.png",
            "section_path": "Overview",
            "nearby_text": "An image near the overview.",
        }


def test_chatbot_sends_image_only_after_the_model_calls_the_tool():
    provider = _AnswerProvider()
    service = ChatbotService(
        repository=object(),
        llm_provider=provider,
        document_image_tool=_Tool(),
    )
    session = ChatSession(
        id="session-1",
        user_id=7,
        project_id=None,
        title=None,
        history_summary=None,
        max_turns=5,
        created_at="now",
        updated_at="now",
    )

    answer = asyncio.run(
        service._complete_with_document_images(
            prompt_messages=[{"role": "user", "content": "ảnh này nói gì?"}],
            retrieved=RetrievedContext(
                context="Document context",
                citations=[],
                image_refs=[
                    {"document_id": "doc-1", "image_id": "doc-1:0"}
                ],
            ),
            session=session,
            user_id=7,
            generation_config={
                "provider_model": "qwen",
                "max_tokens": 100,
                "temperature": 0.5,
                "top_p": 1.0,
            },
        )
    )

    assert answer == "Đây là nội dung nhìn thấy trong ảnh."
    assert provider.multimodal_messages[-1]["content"][-1]["type"] == "image_url"


class _TextualToolCallProvider(_AnswerProvider):
    def generate_tool_calls(self, messages, tools, **kwargs):
        return {
            "content": (
                'get_document_image(document_id="doc-1", image_id="doc-1")'
            ),
            "tool_calls": [],
        }


def test_chatbot_recovers_textual_tool_call_without_leaking_it_to_the_ui():
    provider = _TextualToolCallProvider()
    service = ChatbotService(
        repository=object(),
        llm_provider=provider,
        document_image_tool=_Tool(),
    )

    answer = asyncio.run(
        service._complete_with_document_images(
            prompt_messages=[{"role": "user", "content": "ảnh này là ảnh gì?"}],
            retrieved=RetrievedContext(
                context="",
                citations=[],
                image_refs=[{"document_id": "doc-1", "image_id": "doc-1:0"}],
            ),
            session=ChatSession(
                id="session-1",
                user_id=7,
                project_id=None,
                title=None,
                history_summary=None,
                max_turns=5,
                created_at="now",
                updated_at="now",
            ),
            user_id=7,
            generation_config={
                "provider_model": "qwen",
                "max_tokens": 100,
                "temperature": 0.5,
                "top_p": 1.0,
            },
        )
    )

    assert answer == "Đây là nội dung nhìn thấy trong ảnh."
    assert "get_document_image" not in answer
    assert provider.multimodal_messages[-1]["content"][-1]["type"] == "image_url"
