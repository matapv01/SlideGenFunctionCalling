from __future__ import annotations

from base import BaseService
from agent import AgentService

from graph.shared.agent import SlidegenState
from graph.shared.settings import PlanningSlideSettings
from graph.shared.models import SlidePlan

from graph.shared.settings import PlanningSlideSettings

from langchain_core.prompts import ChatPromptTemplate

from .prompts import SLIDE_PLANNER_SYSTEM_PROMPT
from .prompts import SLIDE_PLANNER_HUMAN_PROMPT

from logger import get_logger
logger = get_logger(__name__)


class PlanningSlideService(BaseService):

    agent: AgentService
    planning_settings: PlanningSlideSettings
    
    def process(self, inputs: SlidegenState) -> dict:

        slide_chunks = inputs.get('slide_chunks', [])
        slide_context_maps = inputs.get('slide_context_maps', [])

        if not slide_chunks or not slide_context_maps:
            logger.warning("No slide chunks or context maps found. Skipping planning.")
            return {'slide_plans': []}
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SLIDE_PLANNER_SYSTEM_PROMPT),
            ("human", SLIDE_PLANNER_HUMAN_PROMPT)
        ])

        planner_chain = prompt | self.agent.with_structured_output(SlidePlan)
        
        # 1. Prepare a list of all inputs.
        all_inputs = []
        for i, content in enumerate(slide_chunks):
            all_inputs.append({
                "slide_context_map": slide_context_maps[i],
                "slide_content": content
            })
        
        total_slides = len(all_inputs)
        all_slide_plans = []

        logger.info('Total slides to plan and processing in chunks', 
                    extra={
                        'total_slides': total_slides, 
                        'batch_size': self.planning_settings.planning_batch_size
                    }
                )
        
        try:
            for i in range(0, total_slides, self.planning_settings.planning_batch_size):
                # Get the current chunk of inputs
                chunk_inputs = all_inputs[i : i + self.planning_settings.planning_batch_size]
                chunk_start_num = i + 1
                chunk_end_num = min(i + self.planning_settings.planning_batch_size, total_slides)
                
                logger.info(' -> Processing chunk: slides', extra={
                    'chunk_start_num': chunk_start_num,
                    'chunk_end_num': chunk_end_num
                })

                batch_results = planner_chain.batch(chunk_inputs, config={"max_concurrency": 5})
                
                chunk_plans = [plan.dict() for plan in batch_results]
                all_slide_plans.extend(chunk_plans)
                logger.info('Done processing chunk')

                return {
                    'slide_plans': all_slide_plans
                }

        except Exception as e:
            logger.exception('Failed during batch planning', extra={'error': str(e)})
            raise e