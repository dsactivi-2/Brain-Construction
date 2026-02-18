"""Entity/Relation Extraction — S3

Regex-basierte Extraktion von Entitaeten und Beziehungen aus Text.
Extrahiert aus hipporag_service/indexer.py und retriever.py.
"""

import re
from typing import List, Tuple

from brain.knowledge_graph.model import Entity, Relation


def extract_entities(text: str) -> List[Entity]:
    """Extrahiert Entitaeten aus Text (Regex-basiert).

    Erkennt:
    - Gross geschriebene Woerter mit > 2 Zeichen (z.B. "Qdrant", "Claude")
    - Ausdruecke in Anfuehrungszeichen (z.B. "brain system")

    Args:
        text: Der zu analysierende Text.

    Returns:
        Liste von Entity-Instanzen (dedupliziert).
    """
    # Gross geschriebene Woerter (> 2 Zeichen)
    words = re.findall(r'\b[A-Z][a-zA-Z0-9\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df]{2,}\b', text)

    # Ausdruecke in Anfuehrungszeichen
    quoted = re.findall(r'"([^"]+)"', text)

    # Deduplizierung
    entity_names = list(set(words + quoted))

    return [Entity(name=name, type="Entity") for name in entity_names]


def extract_relations(text: str, entities: List[Entity]) -> List[Relation]:
    """Extrahiert Beziehungen aus Text (Co-Occurrence in Saetzen).

    Entitaeten die im selben Satz vorkommen, werden als verbunden angenommen.

    Args:
        text: Der zu analysierende Text.
        entities: Liste von Entity-Instanzen.

    Returns:
        Liste von Relation-Instanzen.
    """
    entity_names = [e.name for e in entities]
    relations = []

    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        found = [name for name in entity_names if name in sentence]
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                relations.append(
                    Relation(
                        source=found[i],
                        target=found[j],
                        type="RELATED_TO",
                        context=sentence.strip()[:200],
                    )
                )

    return relations


def extract_entity_names(text: str) -> List[str]:
    """Convenience: Extrahiert nur Entity-Namen (fuer Retriever/Suche).

    Identisch mit retriever.py::_extract_entities().

    Args:
        text: Der zu analysierende Text.

    Returns:
        Liste von Entity-Namen. Fallback: [text] wenn nichts gefunden.
    """
    words = re.findall(r'\b[A-Z][a-zA-Z0-9\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df]{2,}\b', text)
    quoted = re.findall(r'"([^"]+)"', text)
    result = list(set(words + quoted))
    return result or [text]
