# Photogranulo-bench

Étude du jeu *Photogranulometry* (Plante St-Cyr et al., FRDR, DOI 10.20383/103.01316),
benchmark reproductible des approches de photogranulométrie, puis conception d'un modèle de
prédiction de courbe granulométrique à partir d'images. Méthode : `docs/roadmap/` (cahier de recherche).
 
## État

L'arborescence complète existe. Le code écrit couvre la phase 1 et les garde-fous :
manifeste d'intégrité, résolution des chemins par profil, découpage par échantillon avec
contrôle de fuite, contrôle de monotonie des courbes. Les autres modules sont des dossiers vides,
à remplir quand leur phase commence. **Pas de DVC, MLflow ni ASReview** (voir `docs/decisions/0001-sobriete-des-outils.md`).

## Démarrage

```bash
uv sync
uv run pytest
```

Commiter `pyproject.toml` et `uv.lock`.

## Phase 1 : vérifier la copie brute

Placer le jeu dans `data/raw/frdr/` (voir `data/README.md`), puis :

```bash
make count      # nombre de fichiers par extension (12 714 ou 12 745 images ?)
make manifest   # écrit data_manifests/manifest.csv (chemin, taille, SHA-256)
make verify     # détecte fichiers manquants, en trop ou corrompus
```

Les chemins viennent de `configs/paths.yaml`. Choisir l'environnement avec
`PHOTOGRANULO_ENV=local|drive|kaggle|nebius` (défaut : local). Les profils drive, kaggle et nebius
sont des propositions à ajuster.

## Règles codées

- `splits/guard.py` : découpage par échantillon, détection de fuite, empreinte du fichier de
  partitions (toute modification est détectée), accès au test uniquement via `load_test_ids`
  qui exige une raison et l'écrit dans un journal.
- `audit/curves.py` : 0 ≤ P ≤ 100 et courbe croissante avec l'ouverture des tamis.
- `utils/paths.py` : aucun chemin en dur dans le code.

## Pas encore écrit

- `data/parse_filenames` : l'article décrit les éléments du nom (échantillon, type, plateaux,
  numéro d'image, état humide/sec) mais pas le format exact ; à écrire sur de vrais noms.
- `scripts/download.py` : demande l'identifiant de la collection Globus.
- Les scripts `run_experiment` et `evaluate`, et tous les modules des phases 3 à 9.
- Licence du code (voir `LICENSE`) et auteurs de `CITATION.cff`.

## Arborescence

```
photogranulo-bench/
├── README.md                        [écrit] ce fichier
├── LICENSE                          [gabarit] licence du code : à choisir
├── CITATION.cff                     [gabarit] auteurs à compléter ; cite le jeu FRDR
├── pyproject.toml                   [écrit] paquet installable `photogranulo` et dépendances
├── uv.lock                          [apparaît au premier `uv sync`] à commiter
├── .python-version                  [écrit] Python 3.12
├── Makefile                         [écrit] install, test, count, manifest, verify
├── .gitignore                       [écrit] ignore data/** et results/**, garde les .gitkeep
├── .github/workflows/ci.yml         [écrit] intégration continue : uv sync puis pytest
│
├── configs/
│   ├── paths.yaml                   [écrit] profils local, drive, kaggle, nebius
│   ├── data/                        [vide] résolutions, tailles et chevauchement des tuiles
│   ├── splits/                      [vide] définition des découpages (fractions, graine)
│   ├── models/                      [vide] un fichier par approche
│   └── experiments/                 [vide] un fichier par expérience : modèle, données, graine
│
├── data/                            NON versionné
│   ├── README.md                    [écrit] ce qui doit s'y trouver et comment l'obtenir
│   ├── raw/frdr/                    copie brute, lecture seule : soil_image/, calibration_image/, Excel
│   ├── raw/soranzo/                 second jeu, pour la généralisation (phase 10)
│   ├── interim/                     copies réduites, tuiles, caches
│   ├── processed/                   représentations par backbone et par résolution
│   ├── external/                    données de tiers : tableaux de référence, métadonnées
│   └── sample/                      petit sous-ensemble pour les tests et l'essai pilote
│
├── data_manifests/                  versionné
│   └── splits/                      [vide] partitions figées (JSON avec empreinte)
│                                    (manifest.csv et curves.csv y seront produits)
│
├── docs/
│   ├── roadmap/
│   │   └── cahier_de_recherche.pdf  [écrit] cahier de recherche (dix phases, catalogue, registre)
│   ├── research_log/
│   │   └── _modele.md               [gabarit] une note courte par jour : YYYY-MM-DD.md
│   ├── decisions/
│   │   ├── registre.md              [écrit] décisions ouvertes (cahier, section 7)
│   │   └── 0001-sobriete-des-outils.md  [écrit] une décision tranchée = un fichier NNNN-sujet.md
│   ├── questions/
│   │   ├── catalogue.csv            [écrit] les 128 questions (D1 à I10), colonne statut à remplir
│   │   ├── fiche_modele.md          [gabarit] fiche d'évaluation d'une question (5 points)
│   │   └── usages_matrice.csv       [gabarit] matrice usages × données requises (phase 2)
│   ├── literature/
│   │   ├── protocole.md             [gabarit] protocole de revue, écrit AVANT la recherche
│   │   ├── extraction.csv           [gabarit] grille d'extraction (tâche, cible, perte, métriques, fuite...)
│   │   └── references.bib           [gabarit] bibliographie
│   ├── datasheets/
│   │   ├── provenance.md            [gabarit] source, DOI, date, taille réelle, nombre réel d'images
│   │   ├── datasheet.md             [gabarit] fiche de données (phase 3)
│   │   └── reforms_checklist.md     [gabarit] liste REFORMS (phases 6 et 10)
│   └── protocol/
│       └── protocol_v1.md           [gabarit] protocole de comparaison, à figer par le tag `protocol-v1`
│
├── src/photogranulo/
│   ├── data/
│   │   └── manifest.py              [écrit] comptage, manifeste (taille, SHA-256), vérification
│   │                                (à venir : parse_filenames, lecture Excel, download, dataset, tiling)
│   ├── audit/
│   │   └── curves.py                [écrit] courbe entre 0 et 100 %, croissante avec l'ouverture
│   │                                (à venir : cohérence image/courbe, doublons, flou, exposition)
│   ├── splits/
│   │   └── guard.py                 [écrit] découpage par échantillon, fuite, test figé et journalisé
│   ├── utils/
│   │   └── paths.py                 [écrit] chemins lus dans paths.yaml (aucun chemin en dur)
│   │                                (à venir : graines, journalisation, détection de l'environnement)
│   ├── targets/                     [vide] représentations de la cible (phases 5 et 8)
│   ├── models/
│   │   ├── baselines/               [vide] approches reproduites (phase 6)
│   │   └── proposed/                [vide] modèle proposé (phases 8 et 9)
│   ├── losses/                      [vide]
│   ├── metrics/                     [vide] choisies en phase 5
│   ├── training/                    [vide] boucle, points de contrôle, reprise après interruption
│   ├── evaluation/                  [vide] évaluation commune, variance, tests statistiques
│   └── analysis/                    [vide] analyse d'erreurs, tranches, attributions (phase 7)
│
├── scripts/
│   └── build_manifest.py            [écrit] count | build | verify, chemins issus de paths.yaml
│                                    (à venir : download, run_experiment, evaluate)
├── notebooks/
│   ├── exploration/                 [vide] 01_eda, 02_audit (sorties effacées avant commit)
│   └── kaggle/                      [vide] carnets minces : clonent le dépôt et appellent scripts/
│
├── tests/
│   ├── test_manifest_integrity.py   [écrit] manifeste : manquants, en trop, corrompus
│   ├── test_no_leakage.py           [écrit] découpage par échantillon, test figé, accès journalisé
│   ├── test_curve_monotonic.py      [écrit] courbe valide : bornes, monotonie
│   ├── test_paths.py                [écrit] profils de paths.yaml
│   └── test_metrics.py              [ignoré] à écrire en phase 5
│
├── results/                         NON versionné (sauf petits résumés ajoutés explicitement)
│   ├── runs/                        une exécution = un dossier : configuration, graine, hash Git (convention prévue)
│   ├── tables/                      tableaux agrégés (CSV)
│   └── figures/                     figures (PNG)
│
└── paper/
    ├── data_note/                   [vide] note sur le jeu (après la phase 3)
    ├── benchmark/                   [vide] article de benchmark (après la phase 6)
    └── full_paper/                  [vide] article complet (après la phase 10)
```
 