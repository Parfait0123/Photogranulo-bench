"""Résolution des chemins depuis configs/paths.yaml (aucun chemin en dur dans le code)."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "paths.yaml"
DATA_SUBDIRS = ("raw", "interim", "processed", "external", "sample")


def _resolve(value: str, base: Path) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (base / p)


def load_paths(profile: str | None = None, config: Path | None = None) -> dict[str, Path]:
    """Retourne les chemins du profil (argument, sinon $PHOTOGRANULO_ENV, sinon local)."""
    config = config or DEFAULT_CONFIG
    profile = profile or os.environ.get("PHOTOGRANULO_ENV", "local")
    profiles = yaml.safe_load(config.read_text(encoding="utf-8"))["profiles"]
    if profile not in profiles:
        raise KeyError(f"profil inconnu {profile!r} ; disponibles : {sorted(profiles)}")
    cfg = profiles[profile]
    for key in ("data_root", "results_root"):
        if str(cfg.get(key, "TODO")) == "TODO":
            raise ValueError(f"profil {profile!r} : {key} non renseigné dans {config.name}")

    data_root = _resolve(cfg["data_root"], REPO_ROOT)
    results_root = _resolve(cfg["results_root"], REPO_ROOT)
    out = {name: data_root / name for name in DATA_SUBDIRS}
    out["data_root"], out["results"] = data_root, results_root
    out["manifests"] = REPO_ROOT / "data_manifests"
    for name in cfg.get("extra", []):
        out[name] = data_root / name
    for name, value in cfg.get("overrides", {}).items():
        out[name] = _resolve(value, REPO_ROOT)
    return out
