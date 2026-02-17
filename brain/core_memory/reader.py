"""Core Memory Reader — S1 (COMPAT WRAPPER)

Delegiert an brain.identity.service via Factory.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.core_memory.reader import core_memory_read
"""


def core_memory_read(block=None):
    """Liest Core Memory (komplett oder einzelnen Block).

    Args:
        block: Optional — Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
               Wenn None, werden alle Blocks zurueckgegeben.

    Returns:
        Dict mit Block-Inhalten. Bei einzelnem Block: {"block": name, "content": text, "storage": type}
        Bei allen: {"blocks": {name: {"content": ..., "storage": ...}, ...}}
    """
    from brain.shared.factory import get_identity_service
    return get_identity_service().read(block)
