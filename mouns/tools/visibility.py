"""Calendrier éditorial et leviers de visibilité."""

from __future__ import annotations

from datetime import date
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import read_json, write_json, next_id


def _path():
    return load_config().data_dir / "content.json"


def _load() -> list[dict]:
    return read_json(_path(), [])


def _save(items: list[dict]) -> None:
    write_json(_path(), items)


@beta_tool
def add_content_idea(
    titre: str,
    canal: str,
    angle: str,
    cible: str,
    date_publication: Optional[str] = None,
    appel_action: Optional[str] = None,
) -> str:
    """Enregistre une idée de contenu (post LinkedIn, article, webinaire, etc.).

    Args:
        titre: Titre ou accroche.
        canal: "linkedin_post", "linkedin_article", "blog", "newsletter", "webinaire", "video".
        angle: Angle éditorial (problème résolu, retour d'expérience, méthode, débat, etc.).
        cible: Audience visée (DSI, RH formation, chef de projet, OPCO...).
        date_publication: Date prévue ISO (YYYY-MM-DD), optionnelle.
        appel_action: CTA final (RDV découverte, téléchargement template, inscription webinaire...).
    """
    items = _load()
    cid = next_id(items, "C")
    items.append({
        "id": cid,
        "titre": titre,
        "canal": canal,
        "angle": angle,
        "cible": cible,
        "date_publication": date_publication,
        "appel_action": appel_action,
        "etat": "idee",
        "created_at": date.today().isoformat(),
    })
    _save(items)
    return f"Idée enregistrée : {cid} — {titre}"


@beta_tool
def list_content_ideas(etat: Optional[str] = None) -> str:
    """Liste les idées de contenu, optionnellement filtrées par état (idee, redige, publie)."""
    items = _load()
    if etat:
        items = [c for c in items if c["etat"] == etat]
    if not items:
        return "Aucun contenu."
    items.sort(key=lambda c: c.get("date_publication") or "9999-99-99")
    lines = [f"{len(items)} contenu(s) :"]
    for c in items:
        when = c.get("date_publication") or "non planifié"
        lines.append(f"- [{c['id']}] ({c['canal']}) {c['titre']} — {c['etat']} — {when}")
    return "\n".join(lines)


@beta_tool
def update_content_state(content_id: str, etat: str, date_publication: Optional[str] = None) -> str:
    """Change l'état d'un contenu (idee, redige, publie) et éventuellement sa date.

    Args:
        content_id: Identifiant du contenu (ex: "C-0002").
        etat: Nouvel état : "idee", "redige" ou "publie".
        date_publication: Date prévue ou effective de publication (ISO).
    """
    if etat not in ("idee", "redige", "publie"):
        return "État invalide. Valeurs : idee, redige, publie."
    items = _load()
    c = next((x for x in items if x["id"] == content_id), None)
    if not c:
        return f"Contenu {content_id} introuvable."
    c["etat"] = etat
    if date_publication:
        c["date_publication"] = date_publication
    _save(items)
    return f"{content_id} → {etat}."


TOOLS = [add_content_idea, list_content_ideas, update_content_state]
