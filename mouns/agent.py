"""Boucle de l'agent Mouns — utilise le tool runner Anthropic."""

from __future__ import annotations

import anthropic

from .config import Config, load_config
from .prompts import system_prompt
from .tools import all_tools


def build_client(cfg: Config) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=cfg.api_key) if cfg.api_key else anthropic.Anthropic()


def run_turn(messages: list[dict], cfg: Config | None = None) -> tuple[str, list[dict]]:
    """Exécute un tour de conversation : laisse Mouns appeler ses outils en boucle.

    `messages` doit alterner user/assistant (texte uniquement). Renvoie le texte
    final de l'assistant et la liste mise à jour avec ce texte ajouté.
    """
    cfg = cfg or load_config()
    client = build_client(cfg)

    runner = client.beta.messages.tool_runner(
        model=cfg.model,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": system_prompt(cfg),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        thinking={"type": "adaptive"},
        output_config={"effort": "xhigh"},
        tools=all_tools(),
        messages=messages,
    )

    final_message = runner.until_done()
    final_text = "\n".join(
        block.text for block in final_message.content
        if block.type == "text" and getattr(block, "text", None)
    ).strip()

    new_messages = messages + [{"role": "assistant", "content": final_text or "(pas de réponse)"}]
    return final_text, new_messages
