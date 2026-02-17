"""Database Connection Manager — COMPAT WRAPPER

Delegiert an brain.shared.connections und brain.shared.config.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.db import get_qdrant, get_neo4j, get_redis, get_postgres, get_sqlite
"""

from brain.shared.connections import (
    get_qdrant,
    get_neo4j,
    get_redis,
    get_postgres,
    get_sqlite,
)
from brain.shared.config import (
    get_config,
    get_brain_dir,
    get_config_dir,
)

# Re-export fuer volle Rueckwaertskompatibilitaet
__all__ = [
    "get_qdrant",
    "get_neo4j",
    "get_redis",
    "get_postgres",
    "get_sqlite",
    "get_config",
    "get_brain_dir",
    "get_config_dir",
]
