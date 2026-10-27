# Journal de provenance du jeu

| Champ | Valeur |
|---|---|
| Source | FRDR (Federated Research Data Repository) |
| Titre | Photogranulometry - Dataset of soil images with corresponding particle size distributions |
| DOI | 10.20383/103.01316 |
| Article de données | arXiv 2506.17469 (GeoManitoba 2025) |
| Mis à disposition | 20 juin 2025 |
| Licence / conditions |Creative Commons Attribution 4.0 International (CC BY 4.0) https://creativecommons.org/licenses/by/4.0/ |
| Date de téléchargement | |
| Méthode | Globus (collection source : à noter) |
| Taille réelle mesurée | |
| Nombre d'images réel | (annoncé : 12 714 dans l'article, 12 745 dans son résumé français) |
| Manifeste | manifests/raw.csv |
| Versions des outils | Python, photogran, globus-sdk : à noter |

## À vérifier une fois les données présentes

- Contenu réel du fichier Excel (14 tamis ; la page FRDR mentionne aussi un essai à l'hydromètre).
- Format exact des noms de fichiers (l'article indique : numéro d'échantillon, type, nombre de
  plateaux, numéro d'image, état humide/sec). Écrire le parseur seulement après avoir vu des noms réels.
- Correspondance images / courbes / images de calibration.
- Échantillons sans images humides ou sans images sèches.
