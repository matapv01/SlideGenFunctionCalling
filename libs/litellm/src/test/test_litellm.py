from __future__ import annotations

import os

from dotenv import load_dotenv
from litellm import CompletionMessage
from litellm import LiteLLMEmbeddingInput
from litellm import LiteLLMInput
from litellm import LiteLLMService
from litellm import LiteLLMSetting
from litellm import MessageRole

load_dotenv()

LITELLM__URL = os.getenv('LITELLM__URL')
LITELLM__MODEL = os.getenv('LITELLM__MODEL', 'gemini-2.0-flash')

LITELLM__TEMPERATURE = float(os.getenv('LITELLM__TEMPERATURE', 0.7))
LITELLM__TOP_P = float(os.getenv('LITELLM__TOP_P', 0.9))
LITELLM__FREQUENCY_PENALTY = float(os.getenv('LITELLM__FREQUENCY_PENALTY', 0.0))
LITELLM__PRESENCE_PENALTY = float(os.getenv('LITELLM__PRESENCE_PENALTY', 0.0))
LITELLM__MAX_COMPLETION_TOKENS = int(os.getenv('LITELLM__MAX_COMPLETION_TOKENS', 4096))
LITELLM__N = int(os.getenv('LITELLM__N', 1))

LITELLM__EMBEDDING_MODEL = os.getenv('LITELLM__EMBEDDING_MODEL', 'embedding-004')
LITELLM__ENCODING_FORMAT = os.getenv('LITELLM__ENCODING_FORMAT', 'float')
LITELLM__DIMENSIONS = int(os.getenv('LITELLM__DIMENSIONS', 768))
LITELLM__MAX_LENGTH = int(os.getenv('LITELLM__MAX_LENGTH', 2048))

class TestLiteLLMService:
    
    def __init__(self):

        self.llm_setting = LiteLLMSetting(
            url=LITELLM__URL,
            model=LITELLM__MODEL,
            frequency_penalty=LITELLM__FREQUENCY_PENALTY,
            n=LITELLM__N,
            temperature=LITELLM__TEMPERATURE,
            presence_penalty=LITELLM__PRESENCE_PENALTY,
            top_p=LITELLM__TOP_P,
            max_completion_tokens=LITELLM__MAX_COMPLETION_TOKENS,
            embedding_model=LITELLM__EMBEDDING_MODEL,
            encoding_format=LITELLM__ENCODING_FORMAT,
            max_length=LITELLM__MAX_LENGTH,
            dimensions=LITELLM__DIMENSIONS,
        )

        self.litellm = LiteLLMService(settings=self.llm_setting)

    def test_rewrite(self) -> None:
        message: list[CompletionMessage] = [
            CompletionMessage(
                role=MessageRole.SYSTEM,
                content='You are helpful Slide Generator, Your task is rewrite query from user to more clearly understanding',
            ),
            CompletionMessage(
                role=MessageRole.USER,
                content='Tôi hoạt động ở PAYT Club.',
            ),
        ]

        result = self.litellm.process(
            inputs=LiteLLMInput(
                message=message,
            ),
        )
        print(result)

    def test_embedding(self):
        embedding_input = LiteLLMEmbeddingInput(
            input='Hello, world! This is a test text for embedding.',
            encoding_format=LITELLM__ENCODING_FORMAT,
            count_tokens=True,
            embedding_model=LITELLM__EMBEDDING_MODEL,
            dimensions=LITELLM__DIMENSIONS
        )

        print('Embedding input models created successfully!')
        print(f'Single text input: {embedding_input.input}')

        result = self.litellm.embedding(embedding_input)
        print(len(result.vector))


if __name__ == '__main__':
    litellm = TestLiteLLMService()
    
    litellm.test_rewrite()
    litellm.test_embedding()