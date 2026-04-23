"""Rédaction et envoi d'emails de prospection / relance.

Par défaut, tous les emails sont enregistrés en brouillon dans `data/drafts/`.
L'envoi SMTP réel n'est fait que si `confirm_send=True` ET la configuration
SMTP est complète.
"""

from __future__ import annotations

import re
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from anthropic import beta_tool

from ..config import load_config
from ..storage import append_jsonl, read_json, write_json


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "draft"


def _signature() -> str:
    cfg = load_config()
    parts = [f"{cfg.owner_name}", cfg.company]
    if cfg.phone:
        parts.append(cfg.phone)
    if cfg.email:
        parts.append(cfg.email)
    if cfg.website:
        parts.append(cfg.website)
    if cfg.linkedin:
        parts.append(cfg.linkedin)
    return "\n".join(parts)


@beta_tool
def draft_email(
    destinataire_email: str,
    destinataire_nom: str,
    sujet: str,
    corps: str,
    prospect_id: Optional[str] = None,
    type_email: str = "prospection",
) -> str:
    """Enregistre un email en brouillon (fichier .eml dans data/drafts/).

    Le brouillon est prêt à être relu, ajusté puis envoyé via send_email.
    La signature est ajoutée automatiquement à la fin du corps.

    Args:
        destinataire_email: Adresse email du destinataire.
        destinataire_nom: Nom complet du destinataire (pour le To: et le journal).
        sujet: Objet de l'email — court, concret, sans emoji.
        corps: Corps du message en français, déjà personnalisé. Pas de signature
            (elle est ajoutée automatiquement).
        prospect_id: Identifiant du prospect lié (optionnel).
        type_email: "prospection", "relance", "proposition", "remerciement", "nurturing".
    """
    cfg = load_config()
    full_body = corps.rstrip() + "\n\n--\n" + _signature()
    msg = EmailMessage()
    msg["Subject"] = sujet
    msg["From"] = cfg.smtp_from or cfg.email or "contact@example.com"
    msg["To"] = f"{destinataire_nom} <{destinataire_email}>"
    msg.set_content(full_body)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{ts}_{_slug(destinataire_nom)}_{_slug(type_email)}.eml"
    path = cfg.data_dir / "drafts" / filename
    path.write_bytes(bytes(msg))

    append_jsonl(
        cfg.data_dir / "email_log.jsonl",
        {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "etat": "brouillon",
            "type": type_email,
            "destinataire": destinataire_email,
            "destinataire_nom": destinataire_nom,
            "sujet": sujet,
            "prospect_id": prospect_id,
            "fichier": str(path.relative_to(cfg.data_dir)),
        },
    )
    return f"Brouillon créé : {path.relative_to(cfg.data_dir)}"


@beta_tool
def send_email(brouillon_fichier: str, confirm_send: bool = False) -> str:
    """Envoie un brouillon via SMTP. Nécessite une confirmation explicite.

    Args:
        brouillon_fichier: Chemin relatif du brouillon dans data/ (ex: "drafts/...eml").
        confirm_send: Doit être True pour effectivement envoyer. Si False, retourne
            un aperçu sans rien envoyer.
    """
    cfg = load_config()
    if not cfg.smtp_enabled:
        return (
            "SMTP non configuré (renseigne SMTP_HOST/USER/PASSWORD dans .env). "
            "Le brouillon reste disponible pour envoi manuel."
        )
    path = cfg.data_dir / brouillon_fichier
    if not path.exists():
        return f"Brouillon introuvable : {brouillon_fichier}"
    raw = path.read_bytes()
    if not confirm_send:
        head = raw.decode("utf-8", errors="replace").split("\n\n", 1)[0]
        return f"Aperçu (envoi non confirmé) :\n{head}\n\n→ Rappelle send_email avec confirm_send=True pour envoyer."

    msg = EmailMessage()
    from email import message_from_bytes
    parsed = message_from_bytes(raw)
    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as s:
        s.starttls()
        s.login(cfg.smtp_user, cfg.smtp_password)
        s.send_message(parsed)
    append_jsonl(
        cfg.data_dir / "email_log.jsonl",
        {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "etat": "envoye",
            "fichier": brouillon_fichier,
            "destinataire": parsed["To"],
            "sujet": parsed["Subject"],
        },
    )
    return f"Email envoyé à {parsed['To']}."


@beta_tool
def list_email_drafts(limit: int = 20) -> str:
    """Liste les derniers brouillons d'emails créés."""
    cfg = load_config()
    drafts_dir = cfg.data_dir / "drafts"
    if not drafts_dir.exists():
        return "Aucun brouillon."
    files = sorted(drafts_dir.glob("*.eml"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    if not files:
        return "Aucun brouillon."
    return "\n".join(f"- {f.relative_to(cfg.data_dir)}" for f in files)


TOOLS = [draft_email, send_email, list_email_drafts]
