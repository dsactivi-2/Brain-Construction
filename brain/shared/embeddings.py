"""Embedding-Generierung — Shared Kernel

Generiert 384-dimensionale Vektoren mit sentence-transformers (all-MiniLM-L6-v2).
Lazy-Load: Modell wird erst beim ersten Aufruf geladen.

Extrahiert aus brain/embeddings.py.
"""

from typing import List

_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"
_VECTOR_SIZE = 384


def _get_model():
    """Laedt das Embedding-Modell (Lazy, Singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_text(text: str) -> List[float]:
    """Generiert einen 384-dimensionalen Vektor fuer einen Text.

    Args:
        text: Der zu embedende Text.

    Returns:
        Liste mit 384 Floats.
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Generiert Vektoren fuer mehrere Texte (effizient batched).

    Args:
        texts: Liste von Texten.
        batch_size: Batch-Groesse fuer parallele Verarbeitung.

    Returns:
        Liste von 384-dimensionalen Vektoren.
    """
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    return [e.tolist() for e in embeddings]


def get_vector_size() -> int:
    """Gibt die Vektordimension zurueck (384)."""
    return _VECTOR_SIZE
