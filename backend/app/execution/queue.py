"""
queue.py — Module 2 (Execution Engine)

Dispatch point for the one conditional edge in the diagram:

    Return Response -> Self-Healing (only if execution fails)

This is deliberately a thin abstraction. The in-memory implementation
below is fine for local dev and tests; swap it for a Celery/SQS/Kafka-
backed SelfHealingQueue in production without touching service.py.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, Protocol

logger = logging.getLogger("execution_engine.queue")


@dataclass
class SelfHealingTask:
    execution_id: str
    agent: str
    prompt: str
    error: str


class SelfHealingQueue(Protocol):
    async def enqueue(self, execution_id: str, agent: str, prompt: str, error: str) -> None:
        ...


class InMemorySelfHealingQueue:
    """
    Dependency-free default. Holds failed executions in an asyncio.Queue;
    a background worker (started via `start_worker`) drains it and invokes
    a handler supplied by the Self-Healing module.
    """

    def __init__(self) -> None:
        self._queue: "asyncio.Queue[SelfHealingTask]" = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    async def enqueue(self, execution_id: str, agent: str, prompt: str, error: str) -> None:
        task = SelfHealingTask(execution_id=execution_id, agent=agent, prompt=prompt, error=error)
        await self._queue.put(task)
        logger.info("enqueued self-healing task for execution_id=%s", execution_id)

    def start_worker(self, handler: Callable[[SelfHealingTask], Awaitable[None]]) -> None:
        """
        handler: async callable(SelfHealingTask) -> None, owned by the
        Self-Healing module. Injected here so this file has zero import-time
        coupling to Self-Healing internals.
        """

        async def _loop() -> None:
            while True:
                task = await self._queue.get()
                try:
                    await handler(task)
                except Exception:  # noqa: BLE001
                    logger.exception(
                        "self-healing handler raised for execution_id=%s", task.execution_id
                    )
                finally:
                    self._queue.task_done()

        self._worker_task = asyncio.create_task(_loop())

    async def stop_worker(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            self._worker_task = None
