from __future__ import annotations

import json
import httpx

from ..utils import get_settings

from logger import get_logger

logger = get_logger(__name__)

def get_relevant_tool(though: str, category: str) -> None:
    settings = get_settings()

    try:
        with httpx.Client() as client:
            response = client.post(
                url=settings.tool_retriver_url,
                json={
                    'thought': though,
                    'category': category
                }
            )

            if response.status_code != 200:
                logger.warning('API request failed', extra={
                    'status_code': response.status_code,
                    'response_text': response.text
                })

                return []
            
            response_data = response.json()

            return response_data

    except httpx.RequestError as e:
        logger.exception(f'Network error while fetching context: {e}')
        return []
    except json.JSONDecodeError as e:
        logger.exception(f'Failed to decode JSON response: {e}')
        return []
    except Exception as e:
        logger.exception(f'Unexpected error in get_context: {e}')
        return []
