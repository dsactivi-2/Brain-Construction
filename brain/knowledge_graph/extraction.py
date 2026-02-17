"""Entity/Relation Extraction — S3

spaCy-basierte NER + Dependency-Parsing fuer Entitaeten und Beziehungen.
Fallback auf Regex wenn spaCy nicht verfuegbar.
"""

import re
import logging
from typing import List, Optional

from brain.knowledge_graph.model import Entity, Relation

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy Lazy-Load (Singleton, analog zu shared/embeddings.py)
# ---------------------------------------------------------------------------

_nlp_de = None
_nlp_en = None
_spacy_available = None  # None = noch nicht geprueft


def _get_nlp_de():
    """Laedt deutsches spaCy-Modell (lazy, singleton)."""
    global _nlp_de, _spacy_available
    if _nlp_de is not None:
        return _nlp_de
    try:
        import spacy
        _nlp_de = spacy.load("de_core_news_md")
        _spacy_available = True
        _logger.info("spaCy DE model loaded: de_core_news_md")
        return _nlp_de
    except (ImportError, OSError) as e:
        _spacy_available = False
        _logger.warning("spaCy DE model not available: %s", e)
        return None


def _get_nlp_en():
    """Laedt englisches spaCy-Modell (lazy, singleton)."""
    global _nlp_en, _spacy_available
    if _nlp_en is not None:
        return _nlp_en
    try:
        import spacy
        _nlp_en = spacy.load("en_core_web_sm")
        _spacy_available = True
        _logger.info("spaCy EN model loaded: en_core_web_sm")
        return _nlp_en
    except (ImportError, OSError) as e:
        if _spacy_available is None:
            _spacy_available = False
        _logger.warning("spaCy EN model not available: %s", e)
        return None


# ---------------------------------------------------------------------------
# Spracherkennung (Heuristik)
# ---------------------------------------------------------------------------

def _detect_language(text: str) -> str:
    """Einfache Spracherkennung. Gibt 'de' oder 'en' zurueck."""
    german_chars = len(re.findall(r'[\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df]', text))
    german_words = len(re.findall(
        r'\b(und|oder|ist|der|die|das|ein|eine|fuer|mit|von|auf|'
        r'nicht|wird|wurde|haben|werden|nach|ueber|auch)\b',
        text, re.IGNORECASE,
    ))
    if german_chars > 0 or german_words >= 2:
        return "de"
    return "en"


# ---------------------------------------------------------------------------
# spaCy Label → Entity-Typ Mapping
# ---------------------------------------------------------------------------

_LABEL_MAP = {
    # Deutsches Modell (de_core_news_md)
    "PER": "Person",
    "PERSON": "Person",
    "ORG": "Organization",
    "LOC": "Location",
    "GPE": "Location",
    "MISC": "Entity",
    # Englisches Modell (en_core_web_sm)
    "NORP": "Group",
    "FAC": "Location",
    "PRODUCT": "Product",
    "EVENT": "Event",
    "WORK_OF_ART": "Entity",
    "LAW": "Entity",
    "LANGUAGE": "Entity",
    "DATE": "Date",
    "TIME": "Time",
    "MONEY": "Entity",
    "QUANTITY": "Entity",
    "ORDINAL": "Entity",
    "CARDINAL": "Entity",
}


def _map_label(spacy_label: str) -> str:
    """Mappt spaCy NER-Label auf unseren Entity-Typ."""
    return _LABEL_MAP.get(spacy_label, "Entity")


# ---------------------------------------------------------------------------
# Verb → Relation-Typ Mapping (Dependency-Parsing)
# ---------------------------------------------------------------------------

_VERB_RELATION_MAP = {
    "use": "USES", "uses": "USES", "using": "USES",
    "nutzt": "USES", "nutzen": "USES", "verwenden": "USES", "verwendet": "USES",
    "contain": "CONTAINS", "contains": "CONTAINS", "enthaelt": "CONTAINS",
    "create": "CREATES", "creates": "CREATES", "erstellt": "CREATES",
    "manage": "MANAGES", "manages": "MANAGES", "verwaltet": "MANAGES",
    "connect": "CONNECTS_TO", "connects": "CONNECTS_TO", "verbindet": "CONNECTS_TO",
    "depend": "DEPENDS_ON", "depends": "DEPENDS_ON", "abhaengt": "DEPENDS_ON",
    "part": "PART_OF",
    "belong": "BELONGS_TO", "belongs": "BELONGS_TO", "gehoert": "BELONGS_TO",
    "implement": "IMPLEMENTS", "implements": "IMPLEMENTS", "implementiert": "IMPLEMENTS",
    "call": "CALLS", "calls": "CALLS", "ruft": "CALLS",
    "store": "STORES", "stores": "STORES", "speichert": "STORES",
    "run": "RUNS", "runs": "RUNS", "laeuft": "RUNS",
    "send": "SENDS", "sends": "SENDS", "sendet": "SENDS",
    "receive": "RECEIVES", "receives": "RECEIVES", "empfaengt": "RECEIVES",
    "read": "READS", "reads": "READS", "liest": "READS",
    "write": "WRITES", "writes": "WRITES", "schreibt": "WRITES",
    "provide": "PROVIDES", "provides": "PROVIDES", "bietet": "PROVIDES",
    "require": "REQUIRES", "requires": "REQUIRES", "benoetigt": "REQUIRES",
}


def _infer_relation_type(verb_text: str) -> str:
    """Mappt ein Verb auf einen Relation-Typ. Fallback: RELATED_TO."""
    return _VERB_RELATION_MAP.get(verb_text.lower(), "RELATED_TO")


# ---------------------------------------------------------------------------
# spaCy-basierte Extraktion
# ---------------------------------------------------------------------------

def _get_nlp(text: str):
    """Gibt das passende spaCy-Modell zurueck (oder None)."""
    if _spacy_available is False:
        return None
    lang = _detect_language(text)
    nlp = _get_nlp_de() if lang == "de" else _get_nlp_en()
    if nlp is None:
        nlp = _get_nlp_en() if lang == "de" else _get_nlp_de()
    return nlp


def _extract_entities_spacy(text: str) -> Optional[List[Entity]]:
    """Extrahiert Entitaeten mit spaCy NER. Gibt None zurueck wenn nicht verfuegbar."""
    nlp = _get_nlp(text)
    if nlp is None:
        return None

    doc = nlp(text)
    seen = set()
    entities = []

    # 1. Named Entities aus NER
    for ent in doc.ents:
        name = ent.text.strip()
        if len(name) < 2 or name.lower() in seen:
            continue
        seen.add(name.lower())
        entities.append(Entity(name=name, type=_map_label(ent.label_)))

    # 2. Noun-Chunks fuer breitere Abdeckung (Typ: "Concept")
    for chunk in doc.noun_chunks:
        name = chunk.text.strip()
        if name.lower() in seen:
            continue
        if len(chunk) > 1 or (len(name) > 2 and name[0].isupper()):
            seen.add(name.lower())
            entities.append(Entity(name=name, type="Concept"))

    # 3. Quoted Strings (spaCy erkennt diese nicht)
    quoted = re.findall(r'"([^"]+)"', text)
    for q in quoted:
        if q.lower() not in seen and len(q) >= 2:
            seen.add(q.lower())
            entities.append(Entity(name=q, type="Entity"))

    return entities


def _extract_relations_spacy(text: str, entities: List[Entity]) -> Optional[List[Relation]]:
    """Extrahiert Relationen mit spaCy Dependency-Parsing. Gibt None zurueck wenn nicht verfuegbar."""
    nlp = _get_nlp(text)
    if nlp is None:
        return None

    doc = nlp(text)
    entity_names = {e.name.lower(): e.name for e in entities}
    relations = []
    seen_pairs = set()

    # Strategie 1: Subject-Verb-Object Tripel aus Dependency-Parse
    for token in doc:
        if token.pos_ != "VERB":
            continue

        subjects = [c for c in token.children if c.dep_ in ("nsubj", "nsubj:pass", "sb")]
        objects = [c for c in token.children if c.dep_ in ("dobj", "obj", "oa", "pobj", "oc")]

        # Praepositionalobjekte
        for child in token.children:
            if child.dep_ == "prep":
                for grandchild in child.children:
                    if grandchild.dep_ == "pobj":
                        objects.append(grandchild)

        for subj in subjects:
            subj_text = _match_entity(subj, doc, entity_names)
            if subj_text is None:
                continue

            for obj in objects:
                obj_text = _match_entity(obj, doc, entity_names)
                if obj_text is None or subj_text.lower() == obj_text.lower():
                    continue

                pair_key = (subj_text.lower(), obj_text.lower())
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    relations.append(Relation(
                        source=entity_names.get(subj_text.lower(), subj_text),
                        target=entity_names.get(obj_text.lower(), obj_text),
                        type=_infer_relation_type(token.lemma_),
                        context=token.sent.text.strip()[:200],
                    ))

    # Strategie 2: Co-Occurrence Fallback fuer nicht erkannte Paare
    for sent in doc.sents:
        sent_lower = sent.text.lower()
        found = [name for name_lower, name in entity_names.items() if name_lower in sent_lower]
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                pair_key = (found[i].lower(), found[j].lower())
                reverse_key = (found[j].lower(), found[i].lower())
                if pair_key not in seen_pairs and reverse_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    relations.append(Relation(
                        source=found[i],
                        target=found[j],
                        type="RELATED_TO",
                        context=sent.text.strip()[:200],
                    ))

    return relations


def _match_entity(token, doc, entity_names: dict) -> Optional[str]:
    """Prueft ob ein Token (oder sein Noun-Chunk) einer bekannten Entity entspricht."""
    if token.text.lower() in entity_names:
        return entity_names[token.text.lower()]
    for chunk in doc.noun_chunks:
        if token in chunk and chunk.text.lower() in entity_names:
            return entity_names[chunk.text.lower()]
    return None


# ---------------------------------------------------------------------------
# Regex-Fallback (Original-Verhalten)
# ---------------------------------------------------------------------------

def _extract_entities_regex(text: str) -> List[Entity]:
    """Regex-basierte Entity-Extraktion (Original, jetzt Fallback)."""
    words = re.findall(r'\b[A-Z][a-zA-Z0-9\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df]{2,}\b', text)
    quoted = re.findall(r'"([^"]+)"', text)
    entity_names = list(set(words + quoted))
    return [Entity(name=name, type="Entity") for name in entity_names]


def _extract_relations_regex(text: str, entities: List[Entity]) -> List[Relation]:
    """Regex Co-Occurrence Relation-Extraktion (Original, jetzt Fallback)."""
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


# ---------------------------------------------------------------------------
# Public API (Signatures identisch zum Original)
# ---------------------------------------------------------------------------

def extract_entities(text: str) -> List[Entity]:
    """Extrahiert Entitaeten aus Text. spaCy NER mit Regex-Fallback.

    Args:
        text: Der zu analysierende Text.

    Returns:
        Liste von Entity-Instanzen (dedupliziert).
    """
    result = _extract_entities_spacy(text)
    if result is not None:
        return result
    return _extract_entities_regex(text)


def extract_relations(text: str, entities: List[Entity]) -> List[Relation]:
    """Extrahiert Beziehungen aus Text. spaCy Dep-Parse mit Regex-Fallback.

    Args:
        text: Der zu analysierende Text.
        entities: Liste von Entity-Instanzen.

    Returns:
        Liste von Relation-Instanzen.
    """
    result = _extract_relations_spacy(text, entities)
    if result is not None:
        return result
    return _extract_relations_regex(text, entities)


def extract_entity_names(text: str) -> List[str]:
    """Convenience: Extrahiert nur Entity-Namen (fuer Retriever/Suche).

    Args:
        text: Der zu analysierende Text.

    Returns:
        Liste von Entity-Namen. Fallback: [text] wenn nichts gefunden.
    """
    entities = extract_entities(text)
    result = list(set(e.name for e in entities))
    return result or [text]
