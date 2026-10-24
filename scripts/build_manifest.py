"""Phase 1 : compter, construire et vérifier le manifeste de la copie brute.

    python scripts/build_manifest.py count|build|verify [--profile local]
Les chemins viennent de configs/paths.yaml (raw/frdr) ; le manifeste va dans data_manifests/.
"""

import argparse
import sys

from photogranulo.data.manifest import build_manifest, count_by_extension, verify_manifest
from photogranulo.utils.paths import load_paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["count", "build", "verify"])
    ap.add_argument("--profile", default=None)
    args = ap.parse_args()

    paths = load_paths(args.profile)
    root = paths["raw"] / "frdr"
    manifest = paths["manifests"] / "manifest.csv"
    if args.cmd == "count":
        for ext, n in sorted(count_by_extension(root).items()):
            print(f"{ext}\t{n}")
    elif args.cmd == "build":
        print(f"{build_manifest(root, manifest)} fichiers -> {manifest}")
    else:
        res = verify_manifest(root, manifest)
        for k, v in res.items():
            print(f"{k}: {len(v)}")
            for rel in v[:20]:
                print(f"  {rel}")
        return 0 if not any(res.values()) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
