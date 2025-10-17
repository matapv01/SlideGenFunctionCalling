from __future__ import annotations

import httpx
from collections.abc import Generator
from collections.abc import AsyncGenerator

from .datatypes import CompletionMessage
from .datatypes import Message
# Giả sử Response là Union[str, BaseModel] hoặc tương tự. 
# Chúng ta sẽ định nghĩa rõ ràng hơn trong Output
 
from .datatypes import TokensLLM

from typing import Any
from typing import Dict
from typing import Optional
from typing import List
from typing import Union

from base import BaseModel



class FunctionCall(BaseModel):
    """Describes the specific function the LLM wants to call."""
    name: str
    arguments: str


class ToolCall(BaseModel):
    """Represents a tool call request from the LLM."""
    id: str
    type: str = "function"
    function: FunctionCall


class LiteLLMToolInput(BaseModel):
    """
    Input model for LiteLLM Tool Calling service.
    """
    message: Message
    frequency_penalty: Optional[int] = None
    n: Optional[int] = None
    model: str
    presence_penalty: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    tools: list[dict[str, str | object]]
    count_tokens: bool = False

class LiteLLMToolOutput(BaseModel):
    """
    Output model for LiteLLM Tool Calling service.

    Attributes:
        response (Union[str, List[ToolCall]]):
            Response from LLM. Can be a text message (str) or a list of tool call requests (List[ToolCall]).
        metadata (dict[str, Any]): Additional metadata.
        count_tokens (bool): Whether tokens are counted.
        tokens (TokensLLM): Token usage information.
    """

    response: Union[str, List[ToolCall]] # Thay đổi quan trọng ở đây
    metadata: dict[str, Any] = {}
    count_tokens: bool = False
    tokens: TokensLLM = TokensLLM()


class LiteLLMToolService:

    def use_tools(self, client: Generator[httpx.Client], inputs: LiteLLMToolInput) -> LiteLLMToolOutput:
        """
        Perform a synchronous LLM request using tools.

        Args:
            client (Generator[httpx.Client]): Synchronous HTTP client.
            inputs (LiteLLMToolInput): Input parameters for the LLM request.

        Returns:
            LiteLLMToolOutput: Output from LLM, containing text or tool calls.
        """
        return self.__inference_by_llm(
            client=client,
            message=inputs.message,
            frequency_penalty=inputs.frequency_penalty or 0,
            n=inputs.n or 1,
            model=inputs.model,
            presence_penalty=inputs.presence_penalty or 0,
            count_tokens=inputs.count_tokens,
            tools=inputs.tools,
            max_completion_tokens=inputs.max_completion_tokens
        )


    async def use_tools_async(self, client: AsyncGenerator[httpx.AsyncClient], inputs: LiteLLMToolInput) -> LiteLLMToolOutput:
        """
        Perform an asynchronous LLM request using tools.

        Args:
            client (AsyncGenerator[httpx.AsyncClient]): Asynchronous HTTP client.
            inputs (LiteLLMToolInput): Input parameters for the LLM request.

        Returns:
            LiteLLMToolOutput: Output from LLM, containing text or tool calls.
        """
        return await self.__inference_by_llm_async(
            client=client,
            message=inputs.message,
            frequency_penalty=inputs.frequency_penalty or 0,
            n=inputs.n or 1,
            model=inputs.model,
            presence_penalty=inputs.presence_penalty or 0,
            count_tokens=inputs.count_tokens,
            tools=inputs.tools,
            max_completion_tokens=inputs.max_completion_tokens
        )
        
    def __build_request_payload(
        self,
        message: Message,
        frequency_penalty: int,
        n: int,
        model: str,
        presence_penalty: int,
        tools: list[dict[str, str | object]],
        max_completion_tokens: Optional[int],
    ) -> Dict[str, Any]:
        """
        Build payload for chat completion API with tool calling.
        """
        payload: Dict[str, Any]
        # sanitize tools so we never send raw callables or other non-serializable
        # objects in the HTTP payload. This keeps tool metadata (id/name/desc)
        # while dropping local 'func' references.
        sanitized_tools = self._sanitize_tools_for_payload(tools)

        if 'claude' in model.lower():
            payload = {
                'model': model,
                'messages': [self.__parse_to_openai_message(m) for m in message],
                'n': n,
                'tools': sanitized_tools,
            }
        else:
            payload = {
                'model': model,
                'messages': [self.__parse_to_openai_message(m) for m in message],
                'frequency_penalty': frequency_penalty,
                'presence_penalty': presence_penalty,
                'n': n,
                'tools': sanitized_tools,
            }

        if max_completion_tokens:
            payload['max_tokens'] = max_completion_tokens

        
        return payload

    def _sanitize_tools_for_payload(self, tools: list[dict[str, object]] | None) -> list[dict[str, object]]:
        """
        Return a JSON-serializable copy of tools metadata. Skip local callables
        (especially the 'func' key) and coerce non-serializable values to strings.
        """
        import json as _json

        sanitized: list[dict[str, object]] = []
        if not tools:
            return sanitized

        for t in tools:
            if not isinstance(t, dict):
                # try to coerce to dict via str fallback
                sanitized.append({'value': str(t)})
                continue

            tool_obj: dict[str, object] = {}
            for k, v in t.items():
                # never include local function references
                if k == 'func':
                    continue

                if callable(v):
                    # include the function name rather than the object
                    tool_obj[k] = getattr(v, '__name__', str(v))
                    continue

                # try JSON serializing simple values; fallback to str()
                try:
                    _json.dumps(v)
                    tool_obj[k] = v
                except Exception:
                    tool_obj[k] = str(v)

            # ensure id/name/description preserved if present
            for field in ('id', 'name', 'description'):
                if field in t and field not in tool_obj:
                    tool_obj[field] = t[field]

            sanitized.append(tool_obj)

        return sanitized
        
    def __inference_by_llm(
        self,
        *,
        client: Generator[httpx.Client],
        message: Message,
        frequency_penalty: int,
        n: int,
        model: str,
        presence_penalty: int,
        tools: list[dict[str, str | object]],
        max_completion_tokens: Optional[int],
        count_tokens: bool = False,
    ) -> LiteLLMToolOutput:
        """
        Perform synchronous inference with tools.
        """
        payload = self.__build_request_payload(
            message=message,
            frequency_penalty=frequency_penalty,
            n=n,
            model=model,
            presence_penalty=presence_penalty,
            tools=tools,
            max_completion_tokens=max_completion_tokens
        )

        try:
            response = client.post('/v1/chat/completions', json=payload)
            response.raise_for_status()
            response_data = response.json()

            return self.__post_tool_call_response(
                response=response_data,
                count_token=count_tokens,
            )

        except Exception as e:
            raise e

    

    async def __inference_by_llm_async(
        self,
        *,
        client: AsyncGenerator[httpx.AsyncClient],
        message: Message,
        frequency_penalty: int,
        n: int,
        model: str,
        presence_penalty: int,
        tools: list[dict[str, str | object]],
        max_completion_tokens: Optional[int],
        count_tokens: bool = False,
    ) -> LiteLLMToolOutput:
        """
        Perform asynchronous inference with tools.
        """
        payload = self.__build_request_payload(
            message=message,
            frequency_penalty=frequency_penalty,
            n=n,
            model=model,
            presence_penalty=presence_penalty,
            tools=tools,
            max_completion_tokens=max_completion_tokens
        )

        try:
            response = await client.post('/v1/chat/completions', json=payload)
            response.raise_for_status()
            response_data = response.json()

            return self.__post_tool_call_response(
                response=response_data,
                count_token=count_tokens,
            )

        except Exception as e:
            raise e
        
    def __parse_to_openai_message(self, message: CompletionMessage) -> Dict[str, str]:
        """
        Parse CompletionMessage to OpenAI API message format.
        Note: This function only supports messages with 'role' and 'content'.
        To fully support tool-call rounds, extend CompletionMessage and this function to handle 'tool' role and 'tool_call_id'.
        """
        return {
            'role': message.role.value,
            'content': message.content,
        }

    def __post_tool_call_response(
        self,
        response: Dict[str, Any],
        count_token: bool,
    ) -> LiteLLMToolOutput:
        """
        Post-process the response from chat completion API for tool calling.
        """
        if not response.get('choices') or not response['choices']:
            raise ValueError('No choices returned in response')

        choice = response['choices'][0]
        message = choice.get('message', {})

        final_response: Union[str, List[ToolCall]]

        if message.get('tool_calls'):
            tool_calls_data = message['tool_calls']
            final_response = [ToolCall.model_validate(tc) for tc in tool_calls_data]
            
        elif message.get('content'):
            final_response = message['content']
            
        else:
            raise ValueError('Response message has neither content nor tool_calls')

        tokens = TokensLLM()
        if count_token and response.get('usage'):
            usage = response['usage']
            tokens.completion_tokens = usage.get('completion_tokens', 0)
            tokens.prompt_tokens = usage.get('prompt_tokens', 0)
            tokens.total_tokens = usage.get('total_tokens', 0)

        return LiteLLMToolOutput(
            response=final_response,
            count_tokens=count_token,
            tokens=tokens,
        )