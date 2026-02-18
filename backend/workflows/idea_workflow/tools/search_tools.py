# File: backend/workflows/idea_workflow/tools/search_tools.py

from langchain.tools import tool
from pydantic import BaseModel, field_validator
from tavily import TavilyClient
import os

# --- Singleton client ---
_TAVILY_CLIENT = None
index = 0

tavily_keys = {
    0: "TAVILY_API_KEY1",
    1: "TAVILY_API_KEY2",
    2: "TAVILY_API_KEY3",
}


def get_tavily_client() -> TavilyClient:
    global _TAVILY_CLIENT, index
    if _TAVILY_CLIENT is None:
        index = (index + 1) % 2
        api_key = os.getenv(tavily_keys[index])
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        _TAVILY_CLIENT = TavilyClient(api_key=api_key)
        index += 1
    return _TAVILY_CLIENT


class TavilySearchInput(BaseModel):
    query: str
    max_results: int = 5
    search_depth: str = "basic"  # basic | advanced
    max_content_length: int = 500

    @field_validator("query")
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        return v

    @field_validator("search_depth")
    def validate_depth(cls, v):
        if v not in {"basic", "advanced"}:
            raise ValueError("search_depth must be 'basic' or 'advanced'")
        return v


@tool("tavily_search", args_schema=TavilySearchInput)
def tavily_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    max_content_length: int = 500,
) -> dict:
    """
    Perform a Tavily web search and return structured results.

    Returns:
        {
            "query": str,
            "results": [
                {
                    "title": str,
                    "content": str,
                    "url": str
                }
            ]
        }
    """

    client = get_tavily_client()

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth=search_depth,
        include_answer=False,
        include_raw_content=False,
    )

    results = []
    for item in response.get("results", []):
        content = (item.get("content") or "").strip()
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        results.append(
            {
                "title": item.get("title", ""),
                "content": content,
                "url": item.get("url", ""),
            }
        )

    print("=" * 30, "Tavily Search Results", "=" * 30)
    for r in results:
        print(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n{'-'*20}")
    print("=" * 70)

    return {
        "query": query,
        "results": results,
    }


def get_all_search_tools():
    return [
        tavily_search,
    ]