import hashlib
from dataclasses import dataclass

from catalogue import Catalogue
from embedder import FastEmbedder
from intake import Rejection, interpret
from quarantine import Quarantine


@dataclass(frozen=True)
class Ack:
    pass


@dataclass(frozen=True)
class Retry:
    pass


class Consumer:
    def __init__(
        self,
        catalogue: Catalogue,
        embedder: FastEmbedder,
        quarantine: Quarantine,
    ) -> None:
        self._catalogue = catalogue
        self._embedder = embedder
        self._quarantine = quarantine

    def handle(self, raw: bytes) -> Ack | Retry:
        company = interpret(raw)
        if isinstance(company, Rejection):
            try:
                self._quarantine.add(raw, company.reason)
            except Exception:
                return Retry()
            return Ack()
        vector = None
        try:
            if company.embedding_text:
                vector = self._embedder.embed(company.embedding_text)
            self._catalogue.upsert(company, vector, hashlib.sha256(raw).hexdigest())
        except Exception:
            return Retry()
        return Ack()
