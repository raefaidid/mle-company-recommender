"""Consume company-events and store each message, one at a time."""

import asyncio
from typing import Protocol

import aio_pika

from company_recommender.config import (
    POSTGRES_DSN,
    QUEUE,
    RABBITMQ_URL,
    RETRY_DELAY_SECONDS,
)
from company_recommender.consumer.handler import Ack, Consumer, Retry
from company_recommender.embeddings.embedder import FastEmbedder
from company_recommender.storage.catalogue import Catalogue
from company_recommender.storage.quarantine import Quarantine


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
    try:
        asyncio.run(consume(RABBITMQ_URL, POSTGRES_DSN, RETRY_DELAY_SECONDS))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
