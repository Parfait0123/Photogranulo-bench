"""Garde-fous anti-fuite : découpage PAR ÉCHANTILLON, test figé et journalisé.

Règle du cahier : toutes les images d'un même échantillon physique restent dans la
même partition ; le jeu de test est figé ; chaque accès au test est consigné.
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path


def make_splits(
    sample_ids: list[str],
    fractions: dict[str, float],
    seed: int,
) -> dict[str, list[str]]:
    """Répartit les ÉCHANTILLONS (pas les images) entre partitions, de façon déterministe."""
    if abs(sum(fractions.values()) - 1.0) > 1e-9:
        raise ValueError("les fractions doivent sommer à 1")
    ids = sorted(set(sample_ids))
    random.Random(seed).shuffle(ids)
    out: dict[str, list[str]] = {}
    start = 0
    names = list(fractions)
    for i, name in enumerate(names):
        end = len(ids) if i == len(names) - 1 else start + round(fractions[name] * len(ids))
        out[name] = sorted(ids[start:end])
        start = end
    return out


def assert_no_leakage(splits: dict[str, list[str]]) -> None:
    """Échoue si un échantillon apparaît dans deux partitions."""
    seen: dict[str, str] = {}
    for part, ids in splits.items():
        for sid in ids:
            if sid in seen and seen[sid] != part:
                raise AssertionError(f"fuite : {sid!r} dans {seen[sid]!r} et {part!r}")
            seen[sid] = part


def assert_images_follow_samples(
    image_to_sample: dict[str, str], splits: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Déduit les images de chaque partition à partir des échantillons.

    Toute image dont l'échantillon n'est dans aucune partition est une erreur.
    """
    where = {sid: part for part, ids in splits.items() for sid in ids}
    images: dict[str, list[str]] = {p: [] for p in splits}
    for img, sid in sorted(image_to_sample.items()):
        if sid not in where:
            raise AssertionError(f"image {img!r}: échantillon {sid!r} absent des partitions")
        images[where[sid]].append(img)
    return images


def splits_fingerprint(splits: dict[str, list[str]]) -> str:
    payload = json.dumps({k: sorted(v) for k, v in sorted(splits.items())}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def save_splits(splits: dict[str, list[str]], path: Path) -> None:
    assert_no_leakage(splits)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"sha256": splits_fingerprint(splits), "splits": splits}, indent=2),
        encoding="utf-8",
    )


def load_splits(path: Path) -> dict[str, list[str]]:
    """Charge les partitions et vérifie l'empreinte (le test ne doit pas avoir bougé)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if splits_fingerprint(data["splits"]) != data["sha256"]:
        raise ValueError(f"{path} a été modifié : l'empreinte ne correspond plus")
    assert_no_leakage(data["splits"])
    return data["splits"]


def load_test_ids(path: Path, log: Path, reason: str) -> list[str]:
    """Seul point d'entrée vers le test : chaque appel est consigné avec sa raison."""
    if not reason.strip():
        raise ValueError("une raison est obligatoire pour accéder au jeu de test")
    ids = load_splits(path)["test"]
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}\t{reason}\n")
    return ids
