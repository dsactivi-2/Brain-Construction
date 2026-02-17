"""Learning Graphs — S5 (COMPAT WRAPPER)

Delegiert an brain.knowledge_graph.service.KnowledgeGraphService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.learning_graphs.patterns import learning_graph_update, consolidate, decay_prune
"""


def learning_graph_update(session_data: dict) -> dict:
    """Aktualisiert Learning Graphs basierend auf Session-Daten.

    Erkennt Patterns (haeufig genutzte Entitaeten, wiederholte Workflows)
    und erstellt/staerkt Pattern-Knoten im Graph.

    Args:
        session_data: Dict mit session_id, entities, tools_used, etc.

    Returns:
        Dict: {patterns_found, patterns_updated, session_id}
    """
    from brain.shared.factory import get_knowledge_graph_service

    return get_knowledge_graph_service().update_patterns(session_data=session_data)


def consolidate() -> dict:
    """Konsolidiert schwache Pattern-Knoten.

    Merged Patterns mit Score < 0.5 und altem last_seen.
    Loescht Patterns mit Score < 0.1.

    Returns:
        Dict: {merged, deleted}
    """
    from brain.shared.factory import get_knowledge_graph_service

    return get_knowledge_graph_service().consolidate()


def decay_prune() -> dict:
    """Taelicher Score-Decay + Archivierung alter Eintraege.

    - Patterns > 90 Tage ohne Abruf: Score -10%
    - Patterns > 180 Tage: Archivieren/Loeschen

    Returns:
        Dict: {decayed, archived}
    """
    from brain.shared.factory import get_knowledge_graph_service

    return get_knowledge_graph_service().decay_prune()
