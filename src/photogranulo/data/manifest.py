"""Manifeste d'intégrité du jeu de données (phase 1).

Produit un fichier CSV (chemin relatif, taille, SHA-256) pour une arborescence,
le vérifie plus tard, et compte les fichiers par extension. Le comptage réel des
images sert à trancher entre 12 714 et 12 745 images.

Usage :
    python -m photogranulo.data.manifest build  data/raw manifests/raw.csv
    python -m photogranulo.data.manifest verify data/raw manifests/raw.csv
    python -m photogranulo.data.manifest count  data/raw
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from collections import Counter
from pathlib import Path

CHUNK = 8 * 1024 * 1024  # 8 Mo : adapté à des images de plusieurs dizaines de Mo
FIELDS = ["path", "size", "sha256"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path):
    """Fichiers réguliers sous root, en ordre déterministe (chemins relatifs POSIX)."""
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != ".gitkeep":
            yield p


def build_manifest(root: Path, out: Path) -> int:
    """Écrit le manifeste ; retourne le nombre de fichiers."""
    root = root.resolve()
    n = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for p in iter_files(root):
            w.writerow(
                {
                    "path": p.relative_to(root).as_posix(),
                    "size": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )
            n += 1
    return n


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
    missing = sorted(set(expected) - set(present))
    extra = sorted(set(present) - set(expected))
    corrupted = []
    for rel in sorted(set(expected) & set(present)):
        size, digest = expected[rel]
        p = present[rel]
        if p.stat().st_size != size or sha256_file(p) != digest:
            corrupted.append(rel)
    return {"missing": missing, "extra": extra, "corrupted": corrupted}


def count_by_extension(root: Path) -> Counter:
    return Counter(p.suffix.lower() or "(sans extension)" for p in iter_files(root))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("root", type=Path)
    b.add_argument("out", type=Path)
    v = sub.add_parser("verify")
    v.add_argument("root", type=Path)
    v.add_argument("manifest", type=Path)
    c = sub.add_parser("count")
    c.add_argument("root", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "build":
        n = build_manifest(args.root, args.out)
        print(f"{n} fichiers -> {args.out}")
        return 0
    if args.cmd == "verify":
        res = verify_manifest(args.root, args.manifest)
        for k, v_ in res.items():
            print(f"{k}: {len(v_)}")
            for rel in v_[:20]:
                print(f"  {rel}")
        return 0 if not any(res.values()) else 1
    for ext, n in sorted(count_by_extension(args.root).items()):
        print(f"{ext}\t{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
