from __future__ import annotations

import os
from dotenv import load_dotenv

from litellm import LiteLLMService

from graph.domain.convert_document import ConvertDocumentService
from graph.shared.agent import SlidegenState

from graph.domain.split_content import SplitContentService
from graph.shared.settings import ContentSplitterSettings

from graph.domain.organize_chunks import OrganizeChunkService
from graph.shared.settings import OrganizeChunkSettings

from graph.domain.planning_slide import PlanningSlideService
from graph.shared.settings import PlanningSlideSettings

from graph.domain.provide_next_slide import ProvideNextSlideService
from graph.domain.generate_slide import GenerateSlideService

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

litellm = LiteLLMService(
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

state = SlidegenState(
    docx_file=os.path.join("data", "input", "test_ttcs - heading.docx"),
    document_title='',
    document_structure=[],
    document_outline=[],
    slide_chunks=[],
    slide_positions=[],
    slide_context_maps=[],
    slide_plans=[],
    # Slide generation loop state
    current_slide_index=None,
    length_slide_chunks=None,
    current_slide_text=None,
    current_tool_call=None,
    current_html_content=None,
    current_html_path=None,
    current_image_path=None,
    previous_image_path=None,
    previous_accepted_tool_call=None,
    previous_slide_context=None,

    # Retry and evaluation state
    retry_count=2,
    vlm_decision=None,
    vlm_feedback=None,

    # History and final results
    messages=[],
    final_slides=[],
    all_debug_info=[]
)

content_splitter_settings = ContentSplitterSettings(
    CONTENT_CHAR_LIMIT_FOR_SPLIT=1000,
)

convert_document = ConvertDocumentService()
split_content = SplitContentService(
    litellm=litellm,
    content_splitter_settings=content_splitter_settings
)

organize_chunk_settings = OrganizeChunkSettings(
    THRESHOLD_CHAR_LIMIT=1000
)

organize_chunks = OrganizeChunkService(
    organize_chunk_settings=organize_chunk_settings
)

planning_slide = PlanningSlideService(
    litellm=litellm,
    planning_slide_settings=PlanningSlideSettings(
        model=LITELLM__MODEL
    )
)

next_slide_provider = ProvideNextSlideService()

generate_slide = GenerateSlideService(litellm=litellm)

state = convert_document.process(input=state)

state = split_content.process(inputs=state)

state = organize_chunks.process(inputs=state)

state = planning_slide.process(inputs=state)

state = next_slide_provider.process(inputs=state)

# print(generate_slide.process(inputs=state))
