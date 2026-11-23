import asyncio
from pathlib import Path

from company_recommender.consumer.handler import Ack, Retry
from company_recommender.consumer.worker import settle


class FakeMessage:
    def __init__(self) -> None:
        self.acked = False
        self.requeued = False

    async def ack(self) -> None:
        self.acked = True

    async def nack(self, requeue: bool = False) -> None:
        self.requeued = requeue


def test_ack_settles_the_message():
    message = FakeMessage()

    asyncio.run(settle(message, Ack()))

    assert message.acked
    assert not message.requeued


def test_retry_requeues_without_acking():
    message = FakeMessage()

    asyncio.run(settle(message, Retry(), retry_delay=0))

    assert not message.acked
    assert message.requeued


def test_entrypoints_are_importable():
    from company_recommender.panel.server import main as serve

    assert callable(serve)


def test_readme_documents_the_pipeline():
    root = Path(__file__).resolve().parent.parent
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert "just publish" in readme
    assert "just consume" in readme
    assert "just serve" in readme
    assert (root / "DESIGN.md").is_file()
