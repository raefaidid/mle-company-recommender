from fastembed import TextEmbedding

MODEL = "BAAI/bge-small-en-v1.5"


class FastEmbedder:
    def __init__(self) -> None:
        self._model = TextEmbedding(MODEL)

    def embed(self, text: str) -> list[float]:
        vector = next(iter(self._model.embed([text])))
        return [float(value) for value in vector]
