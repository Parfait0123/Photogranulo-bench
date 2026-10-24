# data/ : non versionné

Ce dossier est ignoré par Git (seuls ce fichier et les `.gitkeep` sont suivis).

| Dossier | Contenu |
|---|---|
| `raw/frdr/` | Copie brute en lecture seule du jeu FRDR : `soil_image/`, `calibration_image/`, fichier Excel des courbes |
| `raw/soranzo/` | Second jeu, pour la généralisation (phase 10) |
| `interim/` | Copies réduites, tuiles, caches |
| `processed/` | Représentations par backbone et par résolution |
| `external/` | Données de tiers : tableaux de référence, métadonnées |
| `sample/` | Petit sous-ensemble pour les tests et l'essai pilote |

## Obtenir le jeu

Source : FRDR, DOI 10.20383/103.01316 (téléchargement via Globus).
Lire la licence sur la page du dépôt avant toute redistribution.
Après copie : `make count`, `make manifest`, `make verify`, puis `chmod -R a-w data/raw/frdr`.
Le manifeste produit est dans `data_manifests/` (versionné).
