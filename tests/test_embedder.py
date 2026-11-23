from embedder import FastEmbedder

MALAY = "Pengeluaran sarung tangan getah untuk eksport"
ENGLISH = "Production of rubber gloves for export"
UNRELATED = "Tuition centre for primary and secondary students"


def _cosine(first: list[float], second: list[float]) -> float:
    dot = sum(a * b for a, b in zip(first, second))
    first_norm = sum(a * a for a in first) ** 0.5
    second_norm = sum(b * b for b in second) ** 0.5
    return dot / (first_norm * second_norm)


def test_malay_description_is_closer_to_its_english_translation():
    embedder = FastEmbedder()
    malay = embedder.embed(MALAY)
    english = embedder.embed(ENGLISH)
    unrelated = embedder.embed(UNRELATED)

    assert len(malay) == 384
    assert _cosine(malay, english) > _cosine(malay, unrelated)
