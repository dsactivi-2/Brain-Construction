"""Recall Memory Store — S6 (COMPAT WRAPPER)

Delegiert an brain.conversation.service via Factory.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.recall_memory.store import save_conversation
"""


def save_conversation(session_id, role, content, tool_calls=None, metadata=None):
    """Speichert eine Nachricht in der Recall Memory.

    Args:
        session_id: Session-ID (z.B. UUID).
        role: Rolle (user, assistant, system, tool).
        content: Nachrichteninhalt.
        tool_calls: Optional — Tool-Aufrufe als Dict.
        metadata: Optional — Zusaetzliche Metadaten.

    Returns:
        Dict: {id, stored_in, session_id}
    """
    from brain.shared.factory import get_conversation_service
    return get_conversation_service().save(
        session_id=session_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        metadata=metadata,
    )
