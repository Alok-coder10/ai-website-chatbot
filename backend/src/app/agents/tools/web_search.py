from typing import Any

import httpx

from app.agents.tool import Tool
from app.core.config import settings


class WebSearchTool(Tool):

    name = "web_search"

    description = (
        "Searches the web for current information and returns "
        "relevant search results with titles, URLs, and content."
    )

    API_URL = "https://api.tavily.com/search"

    def __init__(
        self,
        max_results: int = 5,
        timeout: float = 20.0,
    ):
        self.max_results = max_results
        self.timeout = timeout

    async def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:

        query = kwargs.get("query")

        if not isinstance(query, str):
            raise ValueError(
                "Web search requires a 'query' string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        api_key = getattr(
            settings,
            "TAVILY_API_KEY",
            "",
        )

        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY is not configured."
            )

        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": self.max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    self.API_URL,
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Web search request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Web search request failed with "
                f"status {exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to web search service."
            ) from exc

        results = []

        for item in data.get("results", []):

            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score"),
                }
            )

        return {
            "status": "success",
            "query": query,
            "results": results,
        }