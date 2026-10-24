# 0001 : sobriété des outils

- Date : 2026-10-23 · Statut : décidée · Phase : 1
- Décision : uv, pytest, pandas, openpyxl, pillow, pyyaml, globus-sdk. Pas de DVC, MLflow ni
  ASReview tant qu'une phase n'en a pas besoin (DVC et MLflow à réévaluer en phases 5-6 ;
  ASReview seulement si la revue ramène plusieurs centaines d'articles).
- Conséquence : le suivi des données repose sur `data_manifests/` et celui des expériences
  sur `results/runs/` (un dossier par exécution : configuration, graine, hash Git).
