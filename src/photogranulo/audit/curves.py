"""Contrôle de cohérence d'une courbe granulométrique (cahier, axe 5).

Pour des ouvertures d_1 < ... < d_N, les pourcentages passants doivent vérifier
0 <= P_i <= 100 et P_1 <= P_2 <= ... <= P_N.
"""

from __future__ import annotations

from collections.abc import Sequence


def check_psd_curve(
    openings: Sequence[float], passing: Sequence[float], tol: float = 1e-9
) -> list[str]:
    """Retourne la liste des problèmes (vide si la courbe est valide)."""
    problems: list[str] = []
    if len(openings) != len(passing):
        return [f"longueurs différentes : {len(openings)} ouvertures, {len(passing)} valeurs"]
    if any(b <= a for a, b in zip(openings, openings[1:])):
        problems.append("ouvertures non strictement croissantes")
    for d, p in zip(openings, passing):
        if p < -tol or p > 100 + tol:
            problems.append(f"pourcentage hors [0, 100] à l'ouverture {d} : {p}")
    for (d0, p0), (d1, p1) in zip(zip(openings, passing), list(zip(openings, passing))[1:]):
        if p1 < p0 - tol:
            problems.append(f"courbe décroissante entre {d0} ({p0}) et {d1} ({p1})")
    return problems
