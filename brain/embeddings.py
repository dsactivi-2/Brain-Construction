"""Embedding-Generierung — COMPAT WRAPPER

Delegiert an brain.shared.embeddings.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.embeddings import embed_text, embed_batch, get_vector_size
"""

from brain.shared.embeddings import (
    embed_text,
    embed_batch,
    get_vector_size,
    _get_model,
)

# Re-export fuer volle Rueckwaertskompatibilitaet
__all__ = [
    "embed_text",
    "embed_batch",
    "get_vector_size",
    "_get_model",
]
