from __future__ import annotations

from base import BaseService

from logger import get_logger
from graph.shared.agent import SlidegenState

logger = get_logger(__name__)


class ProvideNextSlideService(BaseService):

    def process(self, inputs: SlidegenState) -> dict:
                
        slide_chunks = inputs.get('slide_chunks', [])
        results = {}
        
        if 'length_slide_chunks' not in inputs:
            results['length_slide_chunks'] = len(slide_chunks)


        if slide_chunks:
            # Get the next slide from the queue
            # We use pop(0) to remove the item from the list so the queue gets smaller
            next_chunk = slide_chunks[0]
            
            results['current_slide_text'] = next_chunk
            results['slide_chunks'] = slide_chunks # Update the state with the shorter list
            
            # Increment the index for the new slide
            current_index = inputs.get('current_slide_index', -1)
            results['current_slide_index'] = current_index + 1
            
            results['retry_count'] = 0
            
            logger.info('Done providing next slide chunk.')
        
            return {
                'length_slide_chunks': results['length_slide_chunks'] if results['length_slide_chunks'] else 0,
                'current_slide_text': results['current_slide_text'],
                'slide_chunks': results['slide_chunks'],
                'current_slide_index': results['current_slide_index'],
                'retry_count': results['retry_count']
                
            }
            
        else:
            logger.warning('Slide chunk queue is empty.')

            return {
                'length_slide_chunks': 0,
                'current_slide_text': None,
                'slide_chunks': [],
                'current_slide_index': None,
                'retry_count': 0
            }
