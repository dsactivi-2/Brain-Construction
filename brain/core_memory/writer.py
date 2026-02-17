"""Core Memory Writer — S1 (COMPAT WRAPPER)

Delegiert an brain.identity.service via Factory.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.core_memory.writer import core_memory_update
"""


def core_memory_update(block, content):
    """Updated einen Core Memory Block.

    Args:
        block: Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
        content: Neuer Inhalt (max 4000 Zeichen).

    Returns:
        Dict mit Ergebnis: {"block": name, "updated": True/False, "chars": len}
    """
    from brain.shared.factory import get_identity_service
    return get_identity_service().update(block, content)
