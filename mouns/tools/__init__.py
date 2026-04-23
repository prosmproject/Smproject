"""Outils de Mouns — exposés au tool-runner Anthropic.

Chaque outil est une fonction décorée par `@beta_tool` (Anthropic SDK). Les fonctions
acceptent et retournent des chaînes JSON ou du texte ; elles persistent leurs effets
dans le répertoire `data/` configuré.
"""

from . import prospects, emails, visibility, finance, strategy, tasks

ALL_MODULES = [prospects, emails, visibility, finance, strategy, tasks]


def all_tools():
    out = []
    for mod in ALL_MODULES:
        out.extend(mod.TOOLS)
    return out
