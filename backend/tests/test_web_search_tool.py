import pytest

from app.agents.tools.web_search import WebSearchTool


class FakeResponse:

    def __init__(
        self,
        data,
        status_code=200,
    ):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def json(self):
        return self._data


class FakeAsyncClient:

    def __init__(
        self,
        response,
    ):
        self.response = response
        self.payload = None

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        pass

    async def post(
        self,
        url,
        json,
    ):
        self.payload = json
        return self.response


@pytest.mark.asyncio
async def test_web_search_success(monkeypatch):

    response = FakeResponse(
        {
            "results": [
                {
                    "title": "Python",
                    "url": "https://python.org",
                    "content": "Python programming language.",
                    "score": 0.95,
                }
            ]
        }
    )

    client = FakeAsyncClient(response)

    monkeypatch.setattr(
        "app.agents.tools.web_search.httpx.AsyncClient",
        lambda **kwargs: client,
    )

    monkeypatch.setattr(
        "app.agents.tools.web_search.settings.TAVILY_API_KEY",
        "test-api-key",
    )

    tool = WebSearchTool()

    result = await tool.execute(
        query="Python programming"
    )

    assert result["status"] == "success"
    assert result["query"] == "Python programming"

    assert len(result["results"]) == 1

    assert result["results"][0]["title"] == "Python"
    assert result["results"][0]["url"] == "https://python.org"


@pytest.mark.asyncio
async def test_query_is_required():

    tool = WebSearchTool()

    with pytest.raises(
        ValueError,
        match="query.*string",
    ):
        await tool.execute()


@pytest.mark.asyncio
async def test_query_must_be_string():

    tool = WebSearchTool()

    with pytest.raises(
        ValueError,
        match="query.*string",
    ):
        await tool.execute(
            query=123
        )


@pytest.mark.asyncio
async def test_empty_query_is_rejected():

    tool = WebSearchTool()

    with pytest.raises(
        ValueError,
        match="Search query cannot be empty",
    ):
        await tool.execute(
            query="   "
        )


@pytest.mark.asyncio
async def test_missing_api_key(monkeypatch):

    monkeypatch.setattr(
        "app.agents.tools.web_search.settings.TAVILY_API_KEY",
        "",
    )

    tool = WebSearchTool()

    with pytest.raises(
        RuntimeError,
        match="TAVILY_API_KEY is not configured",
    ):
        await tool.execute(
            query="latest AI news"
        )


@pytest.mark.asyncio
async def test_search_timeout(monkeypatch):

    import httpx

    class TimeoutClient:

        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            raise httpx.ReadTimeout(
                "Request timed out"
            )

    monkeypatch.setattr(
        "app.agents.tools.web_search.httpx.AsyncClient",
        TimeoutClient,
    )

    monkeypatch.setattr(
        "app.agents.tools.web_search.settings.TAVILY_API_KEY",
        "test-api-key",
    )

    tool = WebSearchTool()

    with pytest.raises(
        RuntimeError,
        match="timed out",
    ):
        await tool.execute(
            query="test query"
        )


@pytest.mark.asyncio
async def test_search_connection_error(monkeypatch):

    import httpx

    class ErrorClient:

        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            raise httpx.ConnectError(
                "Connection failed"
            )

    monkeypatch.setattr(
        "app.agents.tools.web_search.httpx.AsyncClient",
        ErrorClient,
    )

    monkeypatch.setattr(
        "app.agents.tools.web_search.settings.TAVILY_API_KEY",
        "test-api-key",
    )

    tool = WebSearchTool()

    with pytest.raises(
        RuntimeError,
        match="Unable to connect",
    ):
        await tool.execute(
            query="test query"
        )