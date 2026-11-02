"""Manifeste d'intégrité du jeu de données (phase 1).

Produit un fichier CSV (chemin relatif, taille, SHA-256) pour une arborescence,
le vérifie plus tard, et compte les fichiers par extension.

Point d'entrée : scripts/build_manifest.py (count | build | verify), ou `make`.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

from tqdm import tqdm

CHUNK = 64 * 1024 * 1024  # 8 Mo : adapté à des images de plusieurs dizaines de Mo
FIELDS = ["path", "size", "sha256"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path) -> list[Path]:
    """Fichiers réguliers sous root, triés par chemin relatif POSIX.

    Le tri sur la chaîne POSIX donne le même ordre sous Windows et Linux, donc un
    manifeste identique d'une machine à l'autre.
    """
    files = (p for p in root.rglob("*") if p.is_file() and p.name != ".gitkeep")
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _bar(total_bytes: int, desc: str, initial: int = 0) -> tqdm:
    """Barre de progression en octets (la durée dépend du volume, pas du nombre de fichiers)."""
    return tqdm(total=total_bytes, desc=desc, unit="B", unit_scale=True, unit_divisor=1024, initial=initial)


def _load_partial(tmp: Path, expected_sizes: dict[str, int]) -> dict[str, str]:
    """Empreintes déjà calculées par une exécution interrompue (lues dans le .tmp).

    Une ligne n'est reprise que si elle est complète et si la taille du fichier n'a pas
    changé ; une dernière ligne tronquée par une coupure est simplement ignorée.
    """
    done: dict[str, str] = {}
    if not tmp.exists():
        return done
    with tmp.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                size = int(row["size"])
            except (KeyError, TypeError, ValueError):
                continue
            digest = row.get("sha256") or ""
            if len(digest) == 64 and expected_sizes.get(row["path"]) == size:
                done[row["path"]] = digest
    return done


def build_manifest(root: Path, out: Path) -> int:
    """Écrit le manifeste ; retourne le nombre de fichiers.

    Écriture dans un fichier temporaire puis renommage : un manifeste partiel ne prend
    jamais la place d'un manifeste valide. Si l'exécution est interrompue, le .tmp est
    conservé et la relance reprend sans recalculer les empreintes déjà écrites.
    """
    root = root.resolve()
    files = iter_files(root)
    rels = {p: p.relative_to(root).as_posix() for p in files}
    sizes = {p: p.stat().st_size for p in files}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    done = _load_partial(tmp, {rels[p]: sizes[p] for p in files})
    already = sum(sizes[p] for p in files if rels[p] in done)
    with tmp.open("w", newline="", encoding="utf-8") as f, _bar(sum(sizes.values()), "Manifeste", already) as bar:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for p in files:
            rel = rels[p]
            if rel in done:
                w.writerow({"path": rel, "size": sizes[p], "sha256": done[rel]})
                continue
            w.writerow({"path": rel, "size": sizes[p], "sha256": sha256_file(p)})
            f.flush()
            bar.update(sizes[p])
    tmp.replace(out)
    return len(files)


def verify_manifest(root: Path, manifest: Path) -> dict[str, list[str]]:
    """Compare l'arborescence au manifeste.

    Retourne les listes: missing (absents), extra (non listés), corrupted (taille
    ou empreinte différente).
    """
    root = root.resolve()
    expected: dict[str, tuple[int, str]] = {}
    with manifest.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            expected[row["path"]] = (int(row["size"]), row["sha256"])

    present = {p.relative_to(root).as_posix(): p for p in iter_files(root)}
    sizes = {rel: p.stat().st_size for rel, p in present.items()}
    missing = sorted(set(expected) - set(present))
    extra = sorted(set(present) - set(expected))
    common = sorted(set(expected) & set(present))
    corrupted = []
    with _bar(sum(sizes[rel] for rel in common), "Vérification") as bar:
        for rel in common:
            size, digest = expected[rel]
            if sizes[rel] != size or sha256_file(present[rel]) != digest:
                corrupted.append(rel)
            bar.update(sizes[rel])
    return {"missing": missing, "extra": extra, "corrupted": corrupted}


def count_by_extension(root: Path) -> Counter:
    """Nombre de fichiers par extension (en minuscules)."""
    return Counter(p.suffix.lower() or "(sans extension)" for p in iter_files(root))