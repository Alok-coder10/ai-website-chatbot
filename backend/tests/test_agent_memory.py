
import pytest

from app.agents.memory import AgentMemoryStore


@pytest.mark.asyncio
async def test_save_and_get_memory():
    store = AgentMemoryStore()

    saved = await store.save(
        "research",
        "Python supports asynchronous programming",
        {"source": "test"},
    )

    retrieved = await store.get(saved.id)

    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.agent_id == "research"
    assert retrieved.content == "Python supports asynchronous programming"
    assert retrieved.metadata == {"source": "test"}


@pytest.mark.asyncio
async def test_list_memories_is_agent_specific():
    store = AgentMemoryStore()

    await store.save("research", "First memory")
    await store.save("research", "Second memory")
    await store.save("compute", "Other agent memory")

    memories = await store.list_memories("research")

    assert len(memories) == 2
    assert all(m.agent_id == "research" for m in memories)


@pytest.mark.asyncio
async def test_list_memories_returns_newest_first():
    store = AgentMemoryStore()

    await store.save("research", "First")
    await store.save("research", "Second")
    await store.save("research", "Third")

    memories = await store.list_memories("research")

    assert [m.content for m in memories] == [
        "Third",
        "Second",
        "First",
    ]


@pytest.mark.asyncio
async def test_list_memories_limit():
    store = AgentMemoryStore()

    for number in range(5):
        await store.save("research", f"Memory {number}")

    memories = await store.list_memories("research", limit=2)

    assert len(memories) == 2
    assert [m.content for m in memories] == [
        "Memory 4",
        "Memory 3",
    ]


@pytest.mark.asyncio
async def test_search_matches_content_terms():
    store = AgentMemoryStore()

    await store.save("research", "Python asynchronous programming")
    await store.save("research", "Database indexing")
    await store.save("compute", "Python numerical calculations")

    matches = await store.search("research", "Python programming")

    assert len(matches) == 1
    assert matches[0].content == "Python asynchronous programming"


@pytest.mark.asyncio
async def test_delete_memory():
    store = AgentMemoryStore()
    saved = await store.save("research", "Delete me")

    assert await store.delete(saved.id) is True
    assert await store.get(saved.id) is None
    assert await store.delete(saved.id) is False


@pytest.mark.asyncio
async def test_clear_agent_memories():
    store = AgentMemoryStore()

    await store.save("research", "One")
    await store.save("research", "Two")
    await store.save("compute", "Keep this")

    deleted_count = await store.clear_agent("research")

    assert deleted_count == 2
    assert await store.list_memories("research") == []
    assert len(await store.list_memories("compute")) == 1


@pytest.mark.asyncio
async def test_rejects_empty_agent_id():
    store = AgentMemoryStore()

    with pytest.raises(ValueError, match="Agent ID"):
        await store.save(" ", "Memory")


@pytest.mark.asyncio
async def test_rejects_empty_content():
    store = AgentMemoryStore()

    with pytest.raises(ValueError, match="content"):
        await store.save("research", "  ")


@pytest.mark.asyncio
async def test_rejects_invalid_limit():
    store = AgentMemoryStore()

    with pytest.raises(ValueError, match="Limit"):
        await store.list_memories("research", limit=0)
