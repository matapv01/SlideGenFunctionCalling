from __future__ import annotations
import io

from base import BaseModel
from base import BaseService

from functools import cached_property

from easydict import EasyDict
from langgraph.graph import START
from langgraph.graph import END
from langgraph.graph import StateGraph

from graph.shared.agent import SlidegenState
from graph.domain.convert_document import ConvertDocumentService
from graph.domain.organize_chunks import OrganizeChunkService
from graph.domain.split_content import SplitContentService
from graph.domain.planning_slide import PlanningSlideService
from graph.domain.provide_next_slide import ProvideNextSlideService
from graph.domain.generate_slide import GenerateSlideService

from graph.domain.upload_minio import MinioUploaderInput
from graph.domain.upload_minio import MinioUploaderService

from pydantic import ConfigDict
from pydantic import Field

from typing import Any
from typing import  Annotated
from fastapi import UploadFile

from logger import get_logger

logger = get_logger(__name__)

class GraphInput(BaseModel):
    docx_file: UploadFile


class GraphOutput(BaseModel):
    pass

class GraphService(BaseService):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: Annotated[Any, Field(exclude=True)]
    settings: Annotated[Any, Field(exclude=True)]
    
    @property
    def minio_uploader_service(self) -> MinioUploaderService:
        return MinioUploaderService(
            minio=self.request.app.state.minio,
            minio_settings=self.settings.minio
        )

    @property
    def convert_document_service(self) -> ConvertDocumentService:
        return ConvertDocumentService(
            minio=self.request.app.state.minio,
            minio_settings=self.settings.minio
        )
    
    
    @property
    def organize_chunk_service(self) -> OrganizeChunkService:
        return OrganizeChunkService(organize_chunk_settings=self.settings.organize_chunk_settings)
    
    
    @property
    def split_content_service(self) -> SplitContentService:
        return SplitContentService(
            litellm=self.request.app.state.litellm,
            content_splitter_settings=self.settings.content_splitter_settings
        )
    
    @property
    def planning_slide_service(self) -> PlanningSlideService:
        return PlanningSlideService(
            agent=self.request.app.state.agent,
            planning_settings=self.settings.planning_slide_settings
        )
    
    @property
    def provide_next_slide_service(self) -> ProvideNextSlideService:
        return ProvideNextSlideService()
    
    
    @property
    def generate_slide_service(self) -> GenerateSlideService:
        return GenerateSlideService(
            agent=self.request.app.state.agent,
            registry=self.request.app.state.registry
        )
    
    @property
    def nodes(self) -> EasyDict:
        
        return EasyDict(
            {
                'convert_document': self.convert_document_service.process,
                'split_content': self.split_content_service.process,
                'organize_chunk': self.organize_chunk_service.process,
                'planning_slide': self.planning_slide_service.process,
                'provide_next_slide': self.provide_next_slide_service.process,
                'generate_slide': self.generate_slide_service.process,
            }
        )
    
    @cached_property
    def complied_graph(self) -> Any:
        graph = StateGraph(SlidegenState)
        
        for key, tool in self.nodes.items():
            graph.add_node(key, tool)
            
        graph.add_edge(START, 'convert_document')
        graph.add_edge('convert_document', 'split_content')
        graph.add_edge('split_content', 'organize_chunk')
        graph.add_edge('organize_chunk', 'planning_slide')
        graph.add_edge('planning_slide', 'provide_next_slide')
        graph.add_edge('provide_next_slide', 'generate_slide')
        graph.add_edge('generate_slide', END)

        return graph.compile()
    
    async def process(self, inputs: GraphInput) -> GraphOutput:
        """Run the graph pipeline against provided inputs.

        Args:
            inputs: GraphInput containing the path to the source DOCX file.

        Returns:
            GraphOutput: placeholder output object (expandable later).
        """

        try:
            
            content = await inputs.docx_file.read()
            buffer = io.BytesIO(content)
            
            minio_uploader = self.minio_uploader_service.process(
                inputs=MinioUploaderInput(
                    file_path=inputs.docx_file.filename,
                    file=buffer
                )
            )

        except Exception as e:
            logger.exception('Error occurred while uploading file to MinIO', extra={'error': str(e)})
            raise

        logger.info('Starting GraphService.process', extra={'docx_file': inputs.docx_file})
        state = SlidegenState(
            object_name=minio_uploader.object_name,
            document_title='',
            document_structure=[],
            document_outline=[],
            slide_chunks=[],
            slide_positions=[],
            slide_context_maps=[],
            slide_plans=[],
            current_slide_index=0,
            length_slide_chunks=0,
            current_slide_text='',
            current_tool_call={},
            current_html_content='',
            current_html_path='',
            current_image_path='',
            previous_image_path='',
            previous_accepted_tool_call={},
            previous_slide_context={},
            retry_count=2,
            vlm_decision='',
            vlm_feedback='',
            messages=[],
            final_slides=[],
            all_debug_info=[],
        )
        
        try:
            graph_output = await self.complied_graph.ainvoke(state)
            
            
            logger.info('GraphService completed invoke')
        except Exception as e:
            logger.exception('Graph invocation failed', extra={'error': str(e)})
            raise

        return GraphOutput()