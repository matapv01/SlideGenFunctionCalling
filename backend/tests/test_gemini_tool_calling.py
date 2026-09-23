import json

from backend.infrastructure.llm_providers.base import GeminiAPIProvider


class _Response:
    content = ""
    tool_calls = [
        {
            "name": "generate_platform_instructions_slide_xml",
            "args": {"items": []},
        }
    ]


class _BoundLLM:
    def invoke(self, messages):
        self.messages = messages
        return _Response()


class _FakeLLM:
    def __init__(self):
        self.bound = _BoundLLM()
        self.bind_args = None
        self.bind_kwargs = None

    def bind_tools(self, tools, **kwargs):
        self.bind_args = tools
        self.bind_kwargs = kwargs
        return self.bound


def test_gemini_requires_a_native_tool_call_when_tools_are_supplied() -> None:
    llm = _FakeLLM()
    provider = GeminiAPIProvider(langchain_llm=llm)
    tools = [{"name": "generate_platform_instructions_slide_xml"}]

    raw = provider.generate_completion(
        messages=[{"role": "user", "content": "Generate the slide"}],
        tools=tools,
    )

    assert llm.bind_args == tools
    assert llm.bind_kwargs == {"tool_choice": "required"}
    assert json.loads(raw) == {
        "tool_calls": [
            {
                "name": "generate_platform_instructions_slide_xml",
                "arguments": {"items": []},
            }
        ]
    }
