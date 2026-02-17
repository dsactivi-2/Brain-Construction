"""Query Classifier — Retrieval Service

Klassifiziert Queries in Typen (fact, temporal, entity, multi)
anhand Regex-Heuristiken.

Extrahiert aus brain/agentic_rag/router.py.
"""

import re


# Query-Typ Heuristiken
_DATE_PATTERNS = [
    r'\b(gestern|heute|letzte woche|letzten monat|diesen monat)\b',
    r'\b\d{4}-\d{2}-\d{2}\b',
    r'\b(januar|februar|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\b',
]

_ENTITY_PATTERNS = [
    r'\b(wer|welche|zusammenhang|beziehung|verknuepf|verbind)\b',
]

_FACT_PATTERNS = [
    r'\b(wie heisst|was ist|name|version|stack|passwort)\b',
]


class QueryClassifier:
    """Klassifiziert Queries in Suchstrategie-Typen."""

    def classify(self, query: str) -> str:
        """Klassifiziert die Query in einen Typ.

        Args:
            query: Suchtext.

        Returns:
            "fact", "temporal", "entity" oder "multi"
        """
        q_lower = query.lower()

        for pattern in _FACT_PATTERNS:
            if re.search(pattern, q_lower):
                return "fact"

        for pattern in _DATE_PATTERNS:
            if re.search(pattern, q_lower):
                return "temporal"

        for pattern in _ENTITY_PATTERNS:
            if re.search(pattern, q_lower):
                return "entity"

        return "multi"
