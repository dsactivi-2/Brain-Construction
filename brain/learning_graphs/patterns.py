"""Learning Graphs — S5 (Neo4j)

Pattern-Detection, Konsolidierung und Score-Decay.
Laeuft periodisch (Consolidation: woechentlich, Decay: taeglich).
"""

from datetime import datetime, timezone, timedelta


def learning_graph_update(session_data: dict) -> dict:
    """Aktualisiert Learning Graphs basierend auf Session-Daten.

    Erkennt Patterns (haeufig genutzte Entitaeten, wiederholte Workflows)
    und erstellt/staerkt Pattern-Knoten im Graph.

    Args:
        session_data: Dict mit session_id, entities, tools_used, etc.

    Returns:
        Dict: {patterns_found, patterns_updated}
    """
    from brain.db import get_neo4j

    patterns_found = 0
    patterns_updated = 0

    try:
        driver = get_neo4j()
        entities = session_data.get("entities", [])
        session_id = session_data.get("session_id", "unknown")
        timestamp = datetime.now(timezone.utc).isoformat()

        with driver.session() as session:
            # Pattern: Entitaeten die zusammen auftreten
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    result = session.run(
                        """
                        MERGE (p:Pattern {
                            id: $pattern_id
                        })
                        ON CREATE SET
                            p.entity_a = $entity_a,
                            p.entity_b = $entity_b,
                            p.count = 1,
                            p.first_seen = $timestamp,
                            p.last_seen = $timestamp,
                            p.score = 1.0
                        ON MATCH SET
                            p.count = p.count + 1,
                            p.last_seen = $timestamp,
                            p.score = p.score + 0.1
                        RETURN p.count AS count
                        """,
                        pattern_id=f"{min(entities[i], entities[j])}_{max(entities[i], entities[j])}",
                        entity_a=entities[i],
                        entity_b=entities[j],
                        timestamp=timestamp,
                    )
                    record = result.single()
                    if record:
                        if record["count"] == 1:
                            patterns_found += 1
                        else:
                            patterns_updated += 1

    except Exception:
        pass

    return {
        "patterns_found": patterns_found,
        "patterns_updated": patterns_updated,
        "session_id": session_data.get("session_id", ""),
    }


def consolidate() -> dict:
    """Konsolidiert schwache Pattern-Knoten.

    Merged Patterns mit Score < 0.5 und altem last_seen.
    Loescht Patterns mit Score < 0.1.

    Returns:
        Dict: {merged, deleted}
    """
    from brain.db import get_neo4j

    merged = 0
    deleted = 0

    try:
        driver = get_neo4j()
        with driver.session() as session:
            # Schwache Patterns loeschen (Score < 0.1)
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.score < 0.1
                DELETE p
                RETURN count(p) AS deleted
                """
            )
            record = result.single()
            if record:
                deleted = record["deleted"]

            # Mittlere Patterns: Score halbieren wenn alt
            threshold = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.last_seen < $threshold AND p.score > 0.1
                SET p.score = p.score * 0.5
                RETURN count(p) AS merged
                """,
                threshold=threshold,
            )
            record = result.single()
            if record:
                merged = record["merged"]

    except Exception:
        pass

    return {"merged": merged, "deleted": deleted}


def decay_prune() -> dict:
    """Taelicher Score-Decay + Archivierung alter Eintraege.

    - Patterns > 90 Tage ohne Abruf: Score -10%
    - Patterns > 180 Tage: Archivieren/Loeschen

    Returns:
        Dict: {decayed, archived}
    """
    from brain.db import get_neo4j

    decayed = 0
    archived = 0

    try:
        driver = get_neo4j()
        now = datetime.now(timezone.utc)

        with driver.session() as session:
            # 90-Tage Decay
            threshold_90 = (now - timedelta(days=90)).isoformat()
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.last_seen < $threshold
                SET p.score = p.score * 0.9
                RETURN count(p) AS decayed
                """,
                threshold=threshold_90,
            )
            record = result.single()
            if record:
                decayed = record["decayed"]

            # 180-Tage Archiv (loeschen)
            threshold_180 = (now - timedelta(days=180)).isoformat()
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.last_seen < $threshold
                DELETE p
                RETURN count(p) AS archived
                """,
                threshold=threshold_180,
            )
            record = result.single()
            if record:
                archived = record["archived"]

    except Exception:
        pass

    return {"decayed": decayed, "archived": archived}
