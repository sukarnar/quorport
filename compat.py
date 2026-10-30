"""Backward compatibility with projects created under the earlier names (Portwright, restforge).

Existing projects keep working unchanged after each rename:
* ``portwright.yaml`` or ``restforge.yaml`` is used when there is no ``quorport.yaml`` in the folder;
* ``PORTWRIGHT_*`` / ``RESTFORGE_*`` environment variables (e.g. in an existing .env) are read when the
  matching ``QUORPORT_*`` one is not set;
* the vault in ``.portwright`` / ``.restforge`` is used when it exists and the new one does not;
* API keys starting ``pw_`` or ``rf_`` stay valid (new keys start ``qp_``);
* ``import portwright`` / ``import restforge`` and the ``portwright``, ``pw`` and ``restforge`` commands work.
"""
from __future__ import annotations

import os
from pathlib import Path

CONFIG_NAME = "quorport.yaml"
LEGACY_CONFIG_NAMES = ("portwright.yaml", "restforge.yaml")
LEGACY_CONFIG_NAME = LEGACY_CONFIG_NAMES[0]          # kept for older imports
ENV_PREFIX = "QUORPORT_"
LEGACY_ENV_PREFIXES = ("PORTWRIGHT_", "RESTFORGE_")
VAULT_PATH = ".quorport/credentials.vault"
LEGACY_VAULT_PATHS = (".portwright/credentials.vault", ".restforge/credentials.vault")
KEY_PREFIX, LEGACY_KEY_PREFIXES = "qp", ("pw", "rf")


def legacy_env_names(name: str) -> list[str]:
    if not name.startswith(ENV_PREFIX):
        return []
    rest = name[len(ENV_PREFIX):]
    return [p + rest for p in LEGACY_ENV_PREFIXES]


def legacy_env_name(name: str) -> str | None:
    names = legacy_env_names(name)
    return names[0] if names else None


def getenv(name: str, default: str | None = None) -> str | None:
    """os.environ.get with a fallback from QUORPORT_X to PORTWRIGHT_X, then RESTFORGE_X."""
    if name in os.environ:
        return os.environ[name]
    for old in legacy_env_names(name):
        if old in os.environ:
            return os.environ[old]
    return default


def has_env(name: str) -> bool:
    return getenv(name) is not None


def config_in(directory: str | Path) -> Path:
    """The project file in a folder: quorport.yaml, else an existing portwright.yaml / restforge.yaml."""
    d = Path(directory)
    new = d / CONFIG_NAME
    if new.exists():
        return new
    for old in LEGACY_CONFIG_NAMES:
        if (d / old).exists():
            return d / old
    return new


def resolve_config(path: str | Path) -> str:
    """Map the default config name to an existing older file when needed."""
    p = Path(path)
    if p.name == CONFIG_NAME and not p.exists():
        for old in LEGACY_CONFIG_NAMES:
            if p.with_name(old).exists():
                return str(p.with_name(old))
    return str(path)


def vault_path(project_root: str | Path, configured: str) -> Path:
    root = Path(project_root)
    p = root / configured
    if configured == VAULT_PATH and not p.exists():
        for old in LEGACY_VAULT_PATHS:
            if (root / old).exists():
                return root / old
    return p
