"""Liste de tâches opérationnelle (todo du jour / de la semaine)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import read_json, write_json, next_id


def _path():
    return load_config().data_dir / "tasks.json"


def _load() -> list[dict]:
    return read_json(_path(), [])


def _save(items: list[dict]) -> None:
    write_json(_path(), items)


@beta_tool
def add_task(
    intitule: str,
    priorite: str = "moyenne",
    echeance: Optional[str] = None,
    domaine: str = "commercial",
    lien_id: Optional[str] = None,
) -> str:
    """Ajoute une tâche au backlog opérationnel.

    Args:
        intitule: Description courte de l'action.
        priorite: "haute", "moyenne", "basse".
        echeance: Date butoir ISO (YYYY-MM-DD).
        domaine: "commercial", "marketing", "production", "admin", "strategie".
        lien_id: ID lié si applicable (P-... pour prospect, M-... pour mission, C-... pour contenu).
    """
    if priorite not in ("haute", "moyenne", "basse"):
        return "Priorité invalide. Valeurs : haute, moyenne, basse."
    items = _load()
    tid = next_id(items, "T")
    items.append({
        "id": tid,
        "intitule": intitule,
        "priorite": priorite,
        "echeance": echeance,
        "domaine": domaine,
        "lien_id": lien_id,
        "statut": "todo",
        "created_at": date.today().isoformat(),
    })
    _save(items)
    return f"Tâche créée : {tid} — {intitule}"


@beta_tool
def list_tasks(statut: str = "todo", limit: int = 30) -> str:
    """Liste les tâches (statut : todo, fait, abandon)."""
    items = _load()
    items = [t for t in items if t["statut"] == statut]
    if not items:
        return f"Aucune tâche en statut '{statut}'."
    pri = {"haute": 0, "moyenne": 1, "basse": 2}
    items.sort(key=lambda t: (pri.get(t["priorite"], 1), t.get("echeance") or "9999"))
    items = items[:limit]
    lines = [f"{len(items)} tâche(s) :"]
    for t in items:
        when = t.get("echeance") or "—"
        link = f" • {t['lien_id']}" if t.get("lien_id") else ""
        lines.append(f"- [{t['id']}] ({t['priorite']}) {t['intitule']} — {t['domaine']} — {when}{link}")
    return "\n".join(lines)


@beta_tool
def complete_task(task_id: str, resultat: Optional[str] = None) -> str:
    """Marque une tâche comme faite (avec un résultat optionnel pour la traçabilité)."""
    items = _load()
    t = next((x for x in items if x["id"] == task_id), None)
    if not t:
        return f"Tâche {task_id} introuvable."
    t["statut"] = "fait"
    t["closed_at"] = date.today().isoformat()
    if resultat:
        t["resultat"] = resultat
    _save(items)
    return f"{task_id} ✓ fait."


TOOLS = [add_task, list_tasks, complete_task]
