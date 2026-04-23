"""Suivi des missions, du CA et des KPI financiers."""

from __future__ import annotations

from datetime import date
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import read_json, write_json, next_id


def _missions_path():
    return load_config().data_dir / "missions.json"


def _kpis_path():
    return load_config().data_dir / "kpis.json"


def _load_missions() -> list[dict]:
    return read_json(_missions_path(), [])


def _save_missions(items: list[dict]) -> None:
    write_json(_missions_path(), items)


@beta_tool
def add_mission(
    client: str,
    type_mission: str,
    montant_ht_eur: float,
    date_debut: str,
    date_fin: str,
    statut: str = "prevue",
    prospect_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Enregistre une mission (formation, conseil, audit) signée ou planifiée.

    Args:
        client: Nom de la société cliente.
        type_mission: "formation", "conseil_pmo", "audit", "coaching", "autre".
        montant_ht_eur: Montant total hors taxes en euros.
        date_debut: Date de début ISO (YYYY-MM-DD).
        date_fin: Date de fin ISO (YYYY-MM-DD).
        statut: "prevue", "en_cours", "facturee", "encaissee", "annulee".
        prospect_id: Identifiant du prospect d'origine si applicable.
        notes: Détail (nombre de jours, intervenant, modalités).
    """
    items = _load_missions()
    mid = next_id(items, "M")
    items.append({
        "id": mid,
        "client": client,
        "type": type_mission,
        "montant_ht_eur": montant_ht_eur,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statut": statut,
        "prospect_id": prospect_id,
        "notes": notes,
        "created_at": date.today().isoformat(),
    })
    _save_missions(items)
    return f"Mission enregistrée : {mid} — {client} — {montant_ht_eur:.0f}€ HT"


@beta_tool
def update_mission_status(mission_id: str, statut: str) -> str:
    """Met à jour le statut d'une mission (prevue, en_cours, facturee, encaissee, annulee)."""
    valid = ("prevue", "en_cours", "facturee", "encaissee", "annulee")
    if statut not in valid:
        return f"Statut invalide. Valeurs : {', '.join(valid)}."
    items = _load_missions()
    m = next((x for x in items if x["id"] == mission_id), None)
    if not m:
        return f"Mission {mission_id} introuvable."
    m["statut"] = statut
    _save_missions(items)
    return f"{mission_id} → {statut}."


@beta_tool
def list_missions(statut: Optional[str] = None) -> str:
    """Liste les missions, optionnellement filtrées par statut."""
    items = _load_missions()
    if statut:
        items = [m for m in items if m["statut"] == statut]
    if not items:
        return "Aucune mission."
    items.sort(key=lambda m: m["date_debut"])
    lines = [f"{len(items)} mission(s) :"]
    for m in items:
        lines.append(
            f"- [{m['id']}] {m['client']} ({m['type']}) — {m['montant_ht_eur']:.0f}€ HT — "
            f"{m['date_debut']}→{m['date_fin']} — {m['statut']}"
        )
    return "\n".join(lines)


@beta_tool
def compute_metrics(annee: Optional[int] = None) -> str:
    """Calcule les KPI commerciaux et financiers (CA signé, CA pondéré, taux conversion).

    Args:
        annee: Année cible (par défaut : année en cours).
    """
    cfg = load_config()
    yr = annee or date.today().year
    missions = _load_missions()
    prospects = read_json(cfg.data_dir / "prospects.json", [])

    en_cours = [m for m in missions if m["statut"] in ("en_cours", "facturee", "encaissee") and m["date_debut"].startswith(str(yr))]
    encaisse = [m for m in missions if m["statut"] == "encaissee" and m["date_debut"].startswith(str(yr))]
    facture = [m for m in missions if m["statut"] == "facturee" and m["date_debut"].startswith(str(yr))]
    prevu = [m for m in missions if m["statut"] == "prevue" and m["date_debut"].startswith(str(yr))]

    ca_signe = sum(m["montant_ht_eur"] for m in en_cours + facture + encaisse)
    ca_encaisse = sum(m["montant_ht_eur"] for m in encaisse)
    pipeline = sum(m["montant_ht_eur"] for m in prevu)

    # Pipeline pondéré : pondère le budget estimé par l'étape commerciale
    proba = {
        "qualifie": 0.10,
        "contacte": 0.20,
        "rdv_planifie": 0.40,
        "proposition_envoyee": 0.55,
        "negociation": 0.75,
    }
    pipe_pond = sum(
        (p.get("budget_estime_eur") or 0) * proba.get(p["stage"], 0)
        for p in prospects
    )

    gagnes = sum(1 for p in prospects if p["stage"] == "gagne")
    actifs = sum(1 for p in prospects if p["stage"] not in ("gagne", "perdu"))
    tx_conv = (gagnes / max(gagnes + sum(1 for p in prospects if p["stage"] == "perdu"), 1)) * 100

    return (
        f"KPI {yr}\n"
        f"- CA encaissé : {ca_encaisse:,.0f} € HT\n"
        f"- CA signé (hors annulé) : {ca_signe:,.0f} € HT\n"
        f"- CA prévu (missions planifiées) : {pipeline:,.0f} € HT\n"
        f"- Pipeline pondéré (prospects) : {pipe_pond:,.0f} € HT\n"
        f"- Prospects actifs : {actifs} • gagnés : {gagnes}\n"
        f"- Taux de conversion (gagné/(gagné+perdu)) : {tx_conv:.1f}%\n"
    )


TOOLS = [add_mission, update_mission_status, list_missions, compute_metrics]
