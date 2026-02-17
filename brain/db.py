"""Database Connection Manager — Brain System

Laedt config/databases.yaml und stellt Verbindungen bereit.
Lazy initialization: Verbindung wird erst bei erstem Zugriff aufgebaut.
Fallback: Lokal -> Cloud (wenn lokal nicht erreichbar).
"""

import os
import yaml
from pathlib import Path
from functools import lru_cache

# Pfade
_CONFIG_DIR = os.environ.get(
    "CONFIG_DIR",
    str(Path(__file__).parent.parent / "config")
)
_BRAIN_DIR = os.environ.get(
    "BRAIN_DIR",
    str(Path(__file__).parent)
)


@lru_cache(maxsize=1)
def _load_config() -> dict:
    """Laedt databases.yaml einmalig."""
    config_path = Path(_CONFIG_DIR) / "databases.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"databases.yaml nicht gefunden: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_config() -> dict:
    """Gibt die gesamte Konfiguration zurueck."""
    return _load_config()


# --- Qdrant ---

_qdrant_client = None


def get_qdrant():
    """Gibt QdrantClient zurueck (Singleton, Lazy)."""
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    from qdrant_client import QdrantClient

    cfg = _load_config()["qdrant"]
    url = cfg.get("url", "http://localhost:6333")
    api_key = cfg.get("api_key")

    try:
        client = QdrantClient(url=url, api_key=api_key if "cloud" in url else None, timeout=5)
        # Schneller Health-Check
        client.get_collections()
        _qdrant_client = client
        return _qdrant_client
    except Exception:
        # Fallback: Versuche ohne API-Key (lokal)
        try:
            client = QdrantClient(url="http://localhost:6333", timeout=5)
            client.get_collections()
            _qdrant_client = client
            return _qdrant_client
        except Exception as e:
            raise ConnectionError(f"Qdrant nicht erreichbar: {e}")


# --- Neo4j ---

_neo4j_driver = None


def get_neo4j():
    """Gibt Neo4j Driver zurueck (Singleton, Lazy)."""
    global _neo4j_driver
    if _neo4j_driver is not None:
        return _neo4j_driver

    from neo4j import GraphDatabase

    cfg = _load_config()["neo4j"]

    # Versuche lokal zuerst
    try:
        driver = GraphDatabase.driver(
            cfg.get("uri", "bolt://localhost:7687"),
            auth=(cfg.get("user", "neo4j"), cfg.get("password", "")),
        )
        driver.verify_connectivity()
        _neo4j_driver = driver
        return _neo4j_driver
    except Exception:
        pass

    # Fallback: Cloud
    try:
        driver = GraphDatabase.driver(
            cfg.get("cloud_uri", ""),
            auth=(cfg.get("cloud_user", "neo4j"), cfg.get("cloud_password", "")),
        )
        driver.verify_connectivity()
        _neo4j_driver = driver
        return _neo4j_driver
    except Exception as e:
        raise ConnectionError(f"Neo4j nicht erreichbar (lokal + cloud): {e}")


# --- Redis ---

_redis_client = None


def get_redis():
    """Gibt Redis Client zurueck (Singleton, Lazy)."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    import redis as redis_lib

    cfg = _load_config()["redis"]

    # Versuche lokal zuerst
    try:
        client = redis_lib.from_url(cfg.get("url", "redis://localhost:6379/0"), decode_responses=True)
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception:
        pass

    # Fallback: Cloud
    try:
        cloud_url = cfg.get("cloud_url", "")
        if cloud_url:
            client = redis_lib.from_url(cloud_url, decode_responses=True)
            client.ping()
            _redis_client = client
            return _redis_client
    except Exception:
        pass

    raise ConnectionError("Redis nicht erreichbar (lokal + cloud)")


# --- PostgreSQL ---

_pg_conn = None


def get_postgres():
    """Gibt psycopg2 Connection zurueck (Singleton, Lazy)."""
    global _pg_conn
    if _pg_conn is not None:
        try:
            _pg_conn.cursor().execute("SELECT 1")
            return _pg_conn
        except Exception:
            _pg_conn = None

    import psycopg2

    cfg = _load_config()["recall_memory"]

    # Versuche lokal zuerst
    try:
        conn = psycopg2.connect(cfg.get("url", ""), connect_timeout=5)
        conn.autocommit = True
        _pg_conn = conn
        return _pg_conn
    except Exception:
        pass

    # Fallback: Cloud
    try:
        cloud_url = cfg.get("cloud_url", "")
        if cloud_url:
            conn = psycopg2.connect(cloud_url, connect_timeout=5)
            conn.autocommit = True
            _pg_conn = conn
            return _pg_conn
    except Exception:
        pass

    raise ConnectionError("PostgreSQL nicht erreichbar (lokal + cloud)")


# --- SQLite (Fallback fuer Recall Memory) ---

_sqlite_conn = None


def get_sqlite():
    """Gibt SQLite Connection zurueck (Fallback wenn PostgreSQL nicht erreichbar)."""
    global _sqlite_conn
    if _sqlite_conn is not None:
        return _sqlite_conn

    import sqlite3

    db_path = Path(_BRAIN_DIR) / "recall_memory" / "conversations.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _sqlite_conn = conn
    return _sqlite_conn


# --- Hilfsfunktionen ---

def get_brain_dir() -> str:
    """Gibt den Brain-Verzeichnispfad zurueck."""
    return _BRAIN_DIR


def get_config_dir() -> str:
    """Gibt den Config-Verzeichnispfad zurueck."""
    return _CONFIG_DIR
