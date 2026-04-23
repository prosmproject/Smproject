"""Gestion du pipeline de prospects (CRM léger en JSON)."""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import read_json, write_json, next_id

VALID_STAGES = (
    "nouveau",
    "qualifie",
    "contacte",
    "rdv_planifie",
    "proposition_envoyee",
    "negociation",
    "gagne",
    "perdu",
)


def _path():
    return load_config().data_dir / "prospects.json"


def _load() -> list[dict]:
    return read_json(_path(), [])


def _save(items: list[dict]) -> None:
    write_json(_path(), items)


def _today() -> str:
    return date.today().isoformat()


@beta_tool
def add_prospect(
    nom: str,
    societe: str,
    secteur: str,
    canal_origine: str,
    email: Optional[str] = None,
    poste: Optional[str] = None,
    telephone: Optional[str] = None,
    linkedin: Optional[str] = None,
    besoin: Optional[str] = None,
    budget_estime_eur: Optional[int] = None,
    notes: Optional[str] = None,
) -> str:
    """Ajoute un prospect au pipeline.

    Args:
        nom: Nom et prénom du contact (ex: "Claire Dupont").
        societe: Nom de l'entreprise du prospect.
        secteur: Secteur d'activité (BTP, industrie, IT, OPCO, etc.).
        canal_origine: Comment ce prospect est arrivé (LinkedIn, recommandation, salon, web, OPCO...).
        email: Email professionnel si connu.
        poste: Fonction du contact (DSI, RH formation, directeur de projet...).
        telephone: Téléphone si connu.
        linkedin: URL LinkedIn si connue.
        besoin: Synthèse du besoin pressenti (formation MS Project, mission PMO, etc.).
        budget_estime_eur: Budget pressenti en euros HT (estimation grossière acceptée).
        notes: Toute information utile (signaux, contexte, actualité de la société).
    """
    items = _load()
    pid = next_id(items, "P")
    record = {
        "id": pid,
        "nom": nom,
        "societe": societe,
        "secteur": secteur,
        "poste": poste,
        "email": email,
        "telephone": telephone,
        "linkedin": linkedin,
        "canal_origine": canal_origine,
        "besoin": besoin,
        "budget_estime_eur": budget_estime_eur,
        "notes": notes,
        "stage": "nouveau",
        "score": None,
        "created_at": _today(),
        "updated_at": _today(),
        "next_action": None,
        "next_action_due": None,
        "history": [{"date": _today(), "evt": "création"}],
    }
    items.append(record)
    _save(items)
    return f"Prospect créé : {pid} — {nom} ({societe})."


@beta_tool
def list_prospects(stage: Optional[str] = None, limit: int = 50) -> str:
    """Liste les prospects, optionnellement filtrés par étape du pipeline.

    Args:
        stage: Filtre sur l'étape (nouveau, qualifie, contacte, rdv_planifie,
            proposition_envoyee, negociation, gagne, perdu). Vide = tous.
        limit: Nombre maximum d'entrées à renvoyer (par défaut 50).
    """
    items = _load()
    if stage:
        if stage not in VALID_STAGES:
            return f"Étape invalide. Valeurs acceptées : {', '.join(VALID_STAGES)}."
        items = [p for p in items if p["stage"] == stage]
    items = sorted(items, key=lambda p: (p.get("next_action_due") or "9999-99-99", p["id"]))[:limit]
    if not items:
        return "Aucun prospect."
    lines = [f"{len(items)} prospect(s) :"]
    for p in items:
        due = p.get("next_action_due") or "—"
        budget = f" • {p['budget_estime_eur']}€" if p.get("budget_estime_eur") else ""
        score = f" • score {p['score']}" if p.get("score") is not None else ""
        lines.append(
            f"- [{p['id']}] {p['nom']} ({p['societe']}, {p['secteur']}) — "
            f"{p['stage']}{score}{budget} — prochaine action : {p.get('next_action') or '—'} ({due})"
        )
    return "\n".join(lines)


@beta_tool
def update_prospect(
    prospect_id: str,
    stage: Optional[str] = None,
    next_action: Optional[str] = None,
    next_action_due: Optional[str] = None,
    notes_ajoutees: Optional[str] = None,
    budget_estime_eur: Optional[int] = None,
    besoin: Optional[str] = None,
) -> str:
    """Met à jour un prospect existant et journalise le changement.

    Args:
        prospect_id: Identifiant du prospect (ex: "P-0003").
        stage: Nouvelle étape (voir list_prospects pour les valeurs acceptées).
        next_action: Description courte de la prochaine action (ex: "relance email J+5").
        next_action_due: Date prévue au format ISO YYYY-MM-DD.
        notes_ajoutees: Texte à ajouter à l'historique du prospect.
        budget_estime_eur: Mise à jour du budget pressenti.
        besoin: Mise à jour du besoin identifié.
    """
    items = _load()
    p = next((x for x in items if x["id"] == prospect_id), None)
    if not p:
        return f"Prospect {prospect_id} introuvable."
    changes = []
    if stage:
        if stage not in VALID_STAGES:
            return f"Étape invalide. Valeurs acceptées : {', '.join(VALID_STAGES)}."
        p["stage"] = stage
        changes.append(f"stage→{stage}")
    if next_action is not None:
        p["next_action"] = next_action
        changes.append(f"action: {next_action}")
    if next_action_due is not None:
        p["next_action_due"] = next_action_due
    if budget_estime_eur is not None:
        p["budget_estime_eur"] = budget_estime_eur
    if besoin is not None:
        p["besoin"] = besoin
    if notes_ajoutees:
        p["history"].append({"date": _today(), "evt": notes_ajoutees})
    p["updated_at"] = _today()
    _save(items)
    return f"{prospect_id} mis à jour : {', '.join(changes) if changes else 'note ajoutée'}."


@beta_tool
def score_prospect(prospect_id: str, score: int, justification: str) -> str:
    """Attribue un score de qualification (0-100) à un prospect.

    Conseil de scoring :
    - 80-100 : décideur identifié, besoin explicite, budget pressenti, calendrier sous 3 mois.
    - 50-79 : besoin probable, contact qualifié, calendrier sous 6 mois.
    - 20-49 : signal faible, à nurturer.
    - 0-19 : hors cible.

    Args:
        prospect_id: Identifiant du prospect.
        score: Score de 0 à 100.
        justification: Pourquoi ce score (1-2 phrases).
    """
    if not 0 <= score <= 100:
        return "Le score doit être entre 0 et 100."
    items = _load()
    p = next((x for x in items if x["id"] == prospect_id), None)
    if not p:
        return f"Prospect {prospect_id} introuvable."
    p["score"] = score
    p["history"].append({"date": _today(), "evt": f"scoring {score} — {justification}"})
    p["updated_at"] = _today()
    _save(items)
    return f"Score {score}/100 enregistré pour {prospect_id}."


@beta_tool
def overdue_followups() -> str:
    """Liste les prospects dont la prochaine action est en retard ou prévue aujourd'hui."""
    items = _load()
    today = _today()
    due = [
        p for p in items
        if p.get("next_action_due") and p["next_action_due"] <= today
        and p["stage"] not in ("gagne", "perdu")
    ]
    if not due:
        return "Aucune relance en retard. 👌"
    due.sort(key=lambda p: p["next_action_due"])
    lines = [f"{len(due)} relance(s) à traiter :"]
    for p in due:
        lines.append(
            f"- [{p['id']}] {p['nom']} ({p['societe']}) — {p['next_action']} (prévu {p['next_action_due']})"
        )
    return "\n".join(lines)


TOOLS = [add_prospect, list_prospects, update_prospect, score_prospect, overdue_followups]
