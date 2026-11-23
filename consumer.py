from dataclasses import dataclass

from catalogue import Catalogue
from embedder import FastEmbedder
from intake import Company, interpret
from quarantine import Quarantine


@dataclass(frozen=True)
class Ack:
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

    def handle(self, raw: bytes) -> Ack:
        company = interpret(raw)
        if not isinstance(company, Company):
            raise TypeError(company)
        vector = None
        if company.nature_of_business:
            vector = self._embedder.embed(company.nature_of_business)
        self._catalogue.upsert(company, vector)
        return Ack()
