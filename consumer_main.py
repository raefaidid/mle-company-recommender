"""Consume company-events and store each message, one at a time."""

import asyncio
import os
from typing import Protocol

import aio_pika

from catalogue import Catalogue
from consumer import Ack, Consumer, Retry
from embedder import FastEmbedder
from quarantine import Quarantine

QUEUE = "company-events"
DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/companies"
DEFAULT_URL = "amqp://guest:guest@localhost:5672/"


class Message(Protocol):
    async def ack(self) -> None: ...

    async def nack(self, requeue: bool = False) -> None: ...


async def settle(message: Message, decision: Ack | Retry, retry_delay: float = 0.0) -> None:
    """Acknowledge a stored message; requeue a transient failure."""
    if isinstance(decision, Ack):
        await message.ack()
        return
    if retry_delay:
        await asyncio.sleep(retry_delay)
    await message.nack(requeue=True)


async def consume(url: str, dsn: str, retry_delay: float = 1.0) -> None:
    catalogue = Catalogue(dsn)
    quarantine = Quarantine(dsn)
    consumer = Consumer(catalogue, FastEmbedder(), quarantine)
    connection = await aio_pika.connect_robust(url)
    try:
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(QUEUE, durable=True)
            async with queue.iterator() as messages:
                async for message in messages:
                    await settle(message, consumer.handle(message.body), retry_delay)
    finally:
        catalogue.close()
        quarantine.close()


def main() -> None:
    url = os.environ.get("RABBITMQ_URL", DEFAULT_URL)
    dsn = os.environ.get("POSTGRES_DSN", DEFAULT_DSN)
    retry_delay = float(os.environ.get("RETRY_DELAY_SECONDS", "1"))
    asyncio.run(consume(url, dsn, retry_delay))


if __name__ == "__main__":
    main()
