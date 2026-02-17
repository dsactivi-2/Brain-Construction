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


def _resolve_env_vars(obj):
    """Ersetzt ${VAR} und ${VAR:-default} Platzhalter mit Environment-Variablen."""
    import re
    if isinstance(obj, str):
        def _replace(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default = var_expr.split(":-", 1)
                return os.environ.get(var_name, default)
            return os.environ.get(var_expr, match.group(0))
        return re.sub(r'\$\{([^}]+)\}', _replace, obj)
    elif isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Laedt databases.yaml einmalig und ersetzt ${ENV_VAR} Platzhalter."""
    config_path = Path(_CONFIG_DIR) / "databases.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"databases.yaml nicht gefunden: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return _resolve_env_vars(raw)


def get_config() -> dict:
    """Gibt die gesamte Konfiguration zurueck."""
    return load_config()


def get_brain_dir() -> str:
    """Gibt den Brain-Verzeichnispfad zurueck."""
    return _BRAIN_DIR


def get_config_dir() -> str:
    """Gibt den Config-Verzeichnispfad zurueck."""
    return _CONFIG_DIR
