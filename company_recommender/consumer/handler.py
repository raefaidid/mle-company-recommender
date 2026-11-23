import hashlib
from dataclasses import dataclass

from company_recommender.embeddings.embedder import FastEmbedder
from company_recommender.intake.models import Rejection
from company_recommender.intake.parser import interpret
from company_recommender.storage.catalogue import Catalogue
from company_recommender.storage.quarantine import Quarantine


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
