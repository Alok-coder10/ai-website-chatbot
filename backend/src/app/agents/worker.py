
import asyncio
import logging

from app.agents.task_queue import TaskQueue, TaskHandler

logger = logging.getLogger(__name__)


class AgentWorker:
    """Continuously processes tasks from an in-process queue."""

    def __init__(
        self,
        queue: TaskQueue,
        handlers: dict[str, TaskHandler],
        poll_interval: float = 0.25,
    ):
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive.")

        self.queue = queue
        self.handlers = handlers
        self.poll_interval = poll_interval
        self._stop_event = asyncio.Event()

    async def run_once(self) -> bool:
        """Process one task; return False when the queue is empty."""
        task = await self.queue.process_next(self.handlers)
        return task is not None

    async def run(self) -> None:
        """Process tasks until stop() is requested."""
        self._stop_event.clear()

        while not self._stop_event.is_set():
            try:
                processed = await self.run_once()

                if not processed:
                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self.poll_interval,
                        )
                    except asyncio.TimeoutError:
                        pass

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Agent worker encountered an unexpected error")
                await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        """Request graceful shutdown."""
        self._stop_event.set()
