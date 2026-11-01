"""Liste ou télécharge le jeu FRDR (HTTPS de la collection Globus) vers raw/frdr du profil activé.

    python scripts/download.py list   # nombre de fichiers et taille totale, sans rien télécharger
    python scripts/download.py get    # copie les fichiers manquants (reprenable)
Paramètres : configs/data/frdr.yaml. Destination : paths.yaml (profil `enable: true`).
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import globus_sdk
import requests
import yaml
from tqdm import tqdm

from photogranulo.utils.paths import REPO_ROOT, load_paths

CONFIG = REPO_ROOT / "configs" / "data" / "frdr.yaml"


def login(cfg: dict) -> tuple[globus_sdk.TransferClient, str, str]:
    """Connexion interactive (lien + code collé). Retourne client, jeton HTTPS, URL du serveur HTTPS."""
    g = cfg["globus"]
    if g["client_id"] == "TODO":
        sys.exit("Renseigner globus.client_id dans configs/data/frdr.yaml")
    auth = globus_sdk.NativeAppAuthClient(g["client_id"])
    https_scope = f"https://auth.globus.org/scopes/{g['origin_id']}/https"
    auth.oauth2_start_flow(requested_scopes=[globus_sdk.TransferClient.scopes.all, https_scope])
    print("Ouvrir ce lien, se connecter, puis coller le code :\n" + auth.oauth2_get_authorize_url())
    tokens = auth.oauth2_exchange_code_for_tokens(input("Code : ").strip()).by_resource_server
    tc = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(tokens["transfer.api.globus.org"]["access_token"])
    )
    return tc, tokens[g["origin_id"]]["access_token"], tc.get_endpoint(g["origin_id"])["https_server"]


def walk(tc: globus_sdk.TransferClient, origin_id: str, path: str):
    """Fichiers (chemin, taille) sous `path`, récursivement."""
    for e in tc.operation_ls(origin_id, path=path):
        full = f"{path.rstrip('/')}/{e['name']}"
        if e["type"] == "dir":
            yield from walk(tc, origin_id, full)
        else:
            yield full, e["size"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["list", "get"])
    ap.add_argument("--workers", type=int, default=8, help="fichiers téléchargés en parallèle")
    args = ap.parse_args()

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    origin_id, root = cfg["globus"]["origin_id"], cfg["globus"]["origin_path"]
    tc, token, https = login(cfg)
    files = list(walk(tc, origin_id, root))
    print(f"{len(files)} fichiers, {sum(s for _, s in files) / 1e9:.1f} Go")
    if args.cmd == "list":
        return 0

    dest_root = load_paths()["raw"] / "frdr"
    todo = []
    for remote, size in files:
        dest = dest_root / Path(remote).relative_to(root)
        if not (dest.exists() and dest.stat().st_size == size):
            todo.append((remote, size, dest))
    total = sum(s for _, s in files)
    done = total - sum(s for _, s, _ in todo)
    print(f"{len(files) - len(todo)} fichiers déjà présents, {len(todo)} ")

    def fetch(item):
        remote, _, dest = item
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + ".part")
        with requests.get(https + remote, headers={"Authorization": f"Bearer {token}"}, stream=True) as r:
            r.raise_for_status()
            with part.open("wb") as f:
                for chunk in r.iter_content(64 * 1024 * 1024):
                    f.write(chunk)
                    bar.update(len(chunk))
        part.rename(dest)

    with tqdm(total=total, initial=done, unit="B", unit_scale=True, unit_divisor=1024,
              mininterval=1, smoothing=0.1) as bar, ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(fetch, todo))
    return 0


if __name__ == "__main__":
    sys.exit(main())