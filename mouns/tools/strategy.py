"""Objectifs, plan court/moyen terme, revue stratégique."""

from __future__ import annotations

from datetime import date
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import read_json, write_json, next_id


def _path():
    return load_config().data_dir / "kpis.json"


def _load() -> dict:
    return read_json(_path(), {"objectifs": [], "strategie": ""})


def _save(data: dict) -> None:
    write_json(_path(), data)


@beta_tool
def set_objective(
    intitule: str,
    horizon: str,
    cible_chiffree: str,
    echeance: str,
    levier: str,
) -> str:
    """Crée un objectif business mesurable.

    Args:
        intitule: Nom court de l'objectif (ex: "Décrocher 3 missions PMO").
        horizon: "trimestre", "semestre", "annee".
        cible_chiffree: Indicateur cible chiffré (ex: "30 000€ HT" ou "5 prospects qualifiés").
        echeance: Date butoir ISO (YYYY-MM-DD).
        levier: Levier principal pour l'atteindre (ex: "campagne LinkedIn + 20 contacts directs").
    """
    data = _load()
    oid = next_id(data["objectifs"], "O")
    data["objectifs"].append({
        "id": oid,
        "intitule": intitule,
        "horizon": horizon,
        "cible_chiffree": cible_chiffree,
        "echeance": echeance,
        "levier": levier,
        "statut": "en_cours",
        "created_at": date.today().isoformat(),
    })
    _save(data)
    return f"Objectif créé : {oid} — {intitule} ({cible_chiffree} d'ici {echeance})."


@beta_tool
def list_objectives(statut: Optional[str] = None) -> str:
    """Liste les objectifs (statut : en_cours, atteint, abandonne, repousse)."""
    data = _load()
    items = data["objectifs"]
    if statut:
        items = [o for o in items if o["statut"] == statut]
    if not items:
        return "Aucun objectif."
    items.sort(key=lambda o: o["echeance"])
    return "\n".join(
        f"- [{o['id']}] {o['intitule']} ({o['horizon']}) — cible {o['cible_chiffree']} — "
        f"échéance {o['echeance']} — {o['statut']}"
        for o in items
    )


@beta_tool
def update_objective_status(objective_id: str, statut: str, commentaire: Optional[str] = None) -> str:
    """Met à jour le statut d'un objectif (en_cours, atteint, abandonne, repousse)."""
    valid = ("en_cours", "atteint", "abandonne", "repousse")
    if statut not in valid:
        return f"Statut invalide. Valeurs : {', '.join(valid)}."
    data = _load()
    o = next((x for x in data["objectifs"] if x["id"] == objective_id), None)
    if not o:
        return f"Objectif {objective_id} introuvable."
    o["statut"] = statut
    if commentaire:
        o.setdefault("notes", []).append({"date": date.today().isoformat(), "txt": commentaire})
    _save(data)
    return f"{objective_id} → {statut}."


@beta_tool
def write_strategy_note(contenu_markdown: str) -> str:
    """Écrit/écrase la note stratégique (plan court/moyen terme) au format Markdown.

    Conseils : structurer en sections — Vision 12 mois, Objectifs trimestriels,
    Plan d'enchaînement des missions, Hypothèses tarifaires, Réinvestissement.

    Args:
        contenu_markdown: Le texte Markdown complet du plan stratégique.
    """
    cfg = load_config()
    path = cfg.data_dir / "strategy.md"
    path.write_text(contenu_markdown, encoding="utf-8")
    return f"Note stratégique mise à jour ({path.relative_to(cfg.data_dir)}, {len(contenu_markdown)} caractères)."


@beta_tool
def read_strategy_note() -> str:
    """Renvoie la note stratégique actuelle (si elle existe)."""
    cfg = load_config()
    path = cfg.data_dir / "strategy.md"
    if not path.exists():
        return "(Aucune note stratégique enregistrée.)"
    return path.read_text(encoding="utf-8")


TOOLS = [set_objective, list_objectives, update_objective_status, write_strategy_note, read_strategy_note]
