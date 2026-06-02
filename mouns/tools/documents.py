"""Organisation documentaire — écrit dans `data/SM_PROJECT/<section>/`.

10 sections cibles :
01_Strategie, 02_Prospection, 03_Missions, 04_Clients,
05_Formation_MS_Project, 06_LinkedIn, 07_Administratif,
08_Finances, 09_Portfolio, 10_Opportunites.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional

from anthropic import beta_tool

from ..config import load_config

VALID_FOLDERS = (
    "01_Strategie",
    "02_Prospection",
    "03_Missions",
    "04_Clients",
    "05_Formation_MS_Project",
    "06_LinkedIn",
    "07_Administratif",
    "08_Finances",
    "09_Portfolio",
    "10_Opportunites",
)


def _root() -> Path:
    p = load_config().data_dir / "SM_PROJECT"
    for f in VALID_FOLDERS:
        (p / f).mkdir(parents=True, exist_ok=True)
    return p


def _safe_filename(name: str) -> str:
    base, _, ext = name.rpartition(".")
    if not base:
        base, ext = name, "md"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-") or "document"
    if ext not in ("md", "txt", "csv", "json"):
        ext = "md"
    return f"{base}.{ext}"


@beta_tool
def save_document(
    folder: str,
    filename: str,
    contenu: str,
    prefix_date: bool = True,
) -> str:
    """Sauvegarde un livrable durable dans SM_PROJECT/<folder>/.

    Args:
        folder: une des 10 sous-sections (01_Strategie, 02_Prospection,
            03_Missions, 04_Clients, 05_Formation_MS_Project, 06_LinkedIn,
            07_Administratif, 08_Finances, 09_Portfolio, 10_Opportunites).
        filename: nom court du fichier (extension .md par défaut, .txt/.csv/.json acceptés).
        contenu: contenu textuel complet du document.
        prefix_date: si True (par défaut), préfixe le nom par la date du jour.
    """
    if folder not in VALID_FOLDERS:
        return f"Folder invalide. Valeurs : {', '.join(VALID_FOLDERS)}."
    root = _root()
    safe = _safe_filename(filename)
    if prefix_date and not re.match(r"^\d{4}-\d{2}-\d{2}", safe):
        safe = f"{date.today().isoformat()}_{safe}"
    path = root / folder / safe
    path.write_text(contenu, encoding="utf-8")
    rel = path.relative_to(load_config().data_dir)
    return f"Document enregistré : {rel} ({len(contenu)} caractères)."


@beta_tool
def list_documents(folder: Optional[str] = None) -> str:
    """Liste les documents de SM_PROJECT/, optionnellement filtrés par section.

    Args:
        folder: si renseigné, filtre sur cette sous-section. Sinon, parcourt tout.
    """
    root = _root()
    folders = [folder] if folder else list(VALID_FOLDERS)
    if folder and folder not in VALID_FOLDERS:
        return f"Folder invalide. Valeurs : {', '.join(VALID_FOLDERS)}."
    lines: list[str] = []
    total = 0
    for f in folders:
        items = sorted((root / f).glob("*"))
        if not items:
            continue
        lines.append(f"\n[{f}]")
        for p in items:
            if p.is_file():
                lines.append(f"  - {p.name}  ({p.stat().st_size} o)")
                total += 1
    if total == 0:
        return "(SM_PROJECT vide)"
    return f"{total} document(s) dans SM_PROJECT/ :" + "\n".join(lines)


@beta_tool
def read_document(folder: str, filename: str) -> str:
    """Lit le contenu d'un document existant de SM_PROJECT/<folder>/.

    Args:
        folder: sous-section (voir save_document pour les valeurs).
        filename: nom exact du fichier (avec extension et préfixe date si présent).
    """
    if folder not in VALID_FOLDERS:
        return f"Folder invalide. Valeurs : {', '.join(VALID_FOLDERS)}."
    path = _root() / folder / filename
    if not path.exists():
        return f"Fichier introuvable : {folder}/{filename}"
    return path.read_text(encoding="utf-8")


TOOLS = [save_document, list_documents, read_document]
