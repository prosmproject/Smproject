"""CLI de Mouns.

Commandes :
    mouns chat         — session interactive (REPL)
    mouns brief        — affiche le brief du jour et termine
    mouns daily        — exécute la routine quotidienne (relances, idées contenu, KPI)
    mouns ask "..."    — pose une question unique en non-interactif
    mouns init         — initialise les fichiers de données vides
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import run_turn
from .config import load_config
from .storage import write_json

console = Console()


def _check_api_key(cfg) -> bool:
    if not cfg.api_key:
        console.print(
            "[red]ANTHROPIC_API_KEY n'est pas configurée.[/red] "
            "Copie .env.example en .env et renseigne ta clé."
        )
        return False
    return True


def cmd_init():
    cfg = load_config()
    files = {
        "prospects.json": [],
        "missions.json": [],
        "kpis.json": {"objectifs": [], "strategie": ""},
        "content.json": [],
        "tasks.json": [],
    }
    for name, default in files.items():
        path = cfg.data_dir / name
        if not path.exists():
            write_json(path, default)
            console.print(f"[green]✓[/green] créé {path.relative_to(cfg.data_dir.parent)}")
        else:
            console.print(f"[dim]= existe   {path.relative_to(cfg.data_dir.parent)}[/dim]")
    console.print(f"\nDonnées dans : [bold]{cfg.data_dir}[/bold]")


def cmd_ask(question: str):
    cfg = load_config()
    if not _check_api_key(cfg):
        return
    messages = [{"role": "user", "content": question}]
    text, _ = run_turn(messages, cfg)
    console.print(Markdown(text or "(pas de réponse)"))


def cmd_brief():
    cmd_ask(
        "Donne-moi un brief du jour : pipeline actuel, top-3 actions à mener aujourd'hui, "
        "alertes (relances en retard, objectifs en dérive), et 2-3 questions à me poser pour "
        "aller plus loin."
    )


def cmd_daily():
    cmd_ask(
        "Lance la routine quotidienne : "
        "1) Diagnostique le pipeline et les KPI. "
        "2) Liste les relances dues et propose pour chacune un brouillon d'email personnalisé. "
        "3) Propose 1 idée de contenu LinkedIn pour cette semaine. "
        "4) Ajoute les tâches correspondantes dans la todo. "
        "5) Termine par un compte rendu structuré : ce qui a été fait, ce qui attend "
        "Mounir, ce qui suit demain."
    )


def cmd_chat():
    cfg = load_config()
    if not _check_api_key(cfg):
        return
    console.print(
        Panel.fit(
            f"[bold]Mouns[/bold] — agent business de [bold]{cfg.company}[/bold]\n"
            f"Modèle : {cfg.model}    Données : {cfg.data_dir}\n"
            "Tape [italic]/quit[/italic] pour sortir, [italic]/reset[/italic] pour repartir à zéro.",
            border_style="cyan",
        )
    )

    messages: list[dict] = []
    # Premier tour : Mouns propose un brief.
    messages.append({"role": "user", "content": "Bonjour Mouns. Donne-moi un brief de démarrage."})
    text, messages = run_turn(messages, cfg)
    console.print(Markdown(text or "(pas de réponse)"))

    while True:
        try:
            console.print()
            user = console.input("[bold cyan]Mounir ›[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\nÀ bientôt.")
            return
        if not user:
            continue
        if user in ("/quit", "/exit"):
            return
        if user == "/reset":
            messages = []
            console.print("[dim]Conversation réinitialisée.[/dim]")
            continue
        messages.append({"role": "user", "content": user})
        try:
            text, messages = run_turn(messages, cfg)
        except Exception as e:
            console.print(f"[red]Erreur : {e}[/red]")
            continue
        console.print()
        console.print(Markdown(text or "(pas de réponse)"))


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "chat"
    rest = argv[1:]

    if cmd == "init":
        cmd_init()
    elif cmd == "chat":
        cmd_chat()
    elif cmd == "brief":
        cmd_brief()
    elif cmd == "daily":
        cmd_daily()
    elif cmd == "ask":
        if not rest:
            console.print("[red]Usage : mouns ask \"ta question\"[/red]")
            return 2
        cmd_ask(" ".join(rest))
    elif cmd in ("-h", "--help", "help"):
        console.print(__doc__ or "")
    else:
        console.print(f"[red]Commande inconnue : {cmd}[/red]")
        console.print(__doc__ or "")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
