"""Knowledge Graph Domain Model — S3 + S5

Entitaeten und Wertobjekte fuer den Wissensgraph (HippoRAG + Learning Graphs).
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Entity:
    """Ein Knoten im Wissensgraph."""
    name: str
    type: str = "Entity"
    connections: int = 0


@dataclass
class Relation:
    """Eine Kante zwischen zwei Entitaeten im Wissensgraph."""
    source: str
    target: str
    type: str = "RELATED_TO"
    context: str = ""


@dataclass(frozen=True)
class GraphSearchResult:
    """Ein Suchergebnis aus der Wissensgraph-Suche."""
    entity: str
    type: str
    relations: list
    score: float
    context: str
    source: str

    def to_dict(self) -> dict:
        """Konvertiert zu Dict im Compat-Format (wie retriever.py).

        Returns:
            Dict: {entity, type, relations, score, context, source}
        """
        return {
            "entity": self.entity,
            "type": self.type,
            "relations": self.relations,
            "score": self.score,
            "context": self.context,
            "source": self.source,
        }


@dataclass
class Pattern:
    """Ein erkanntes Pattern aus dem Learning Graph (S5)."""
    id: str
    entity_a: str
    entity_b: str
    count: int = 1
    score: float = 1.0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None


@dataclass(frozen=True)
class IngestResult:
    """Ergebnis einer Wissens-Indizierung (HippoRAG Ingest)."""
    entities_created: int
    relations_created: int
    embedding_stored: bool
    entity_names: list

    def to_dict(self) -> dict:
        """Konvertiert zu Dict im Compat-Format (wie indexer.py).

        Returns:
            Dict: {entities_created, relations_created, embedding_stored, entities}
        """
        return {
            "entities_created": self.entities_created,
            "relations_created": self.relations_created,
            "embedding_stored": self.embedding_stored,
            "entities": self.entity_names,
        }
