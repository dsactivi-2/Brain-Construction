"""Config Loading — Shared Kernel

Laedt databases.yaml und stellt Pfad-Konfigurationen bereit.
Extrahiert aus brain/db.py.
"""

import os
import yaml
from pathlib import Path
from functools import lru_cache


# Pfade
_CONFIG_DIR = os.environ.get(
    "CONFIG_DIR",
    str(Path(__file__).parent.parent.parent / "config")
)
_BRAIN_DIR = os.environ.get(
    "BRAIN_DIR",
    str(Path(__file__).parent.parent)
)


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Laedt databases.yaml einmalig."""
    config_path = Path(_CONFIG_DIR) / "databases.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"databases.yaml nicht gefunden: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_config() -> dict:
    """Gibt die gesamte Konfiguration zurueck."""
    return load_config()


def get_brain_dir() -> str:
    """Gibt den Brain-Verzeichnispfad zurueck."""
    return _BRAIN_DIR


def get_config_dir() -> str:
    """Gibt den Config-Verzeichnispfad zurueck."""
    return _CONFIG_DIR
