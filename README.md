# Mouns — agent IA business pour SM Project

**Mouns** est l'agent IA personnel de [Mounir Stili](mailto:contact@smproject.fr),
fondateur de **SM Project** (gestion de projets et formation MS Project).

Il identifie les leviers à plus fort impact pour développer la société (visibilité,
activité commerciale, CA, optimisation du revenu net), exécute les actions courantes
(prospection, rédaction d'emails personnalisés, calendrier éditorial, suivi du
pipeline) et construit un plan d'enchaînement de missions sur 3 à 6 mois.

Propulsé par **Claude Opus 4.7** via le SDK Anthropic, avec adaptive thinking et un
runner d'outils maison persistant en JSON.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# édite .env : ANTHROPIC_API_KEY, identité société, SMTP optionnel
mouns init
```

## Usage

```bash
mouns chat                        # session interactive (REPL)
mouns brief                       # brief du jour (état pipeline + top-3 actions)
mouns daily                       # routine quotidienne complète
mouns ask "Prépare un email pour le DSI de Veolia, signal LinkedIn ce matin sur leur PMO"
```

## Ce que Mouns sait faire

### Pipeline & prospection
- `add_prospect`, `list_prospects`, `update_prospect`, `score_prospect`, `overdue_followups`
- Pipeline qualifié par étapes (nouveau → qualifié → contacté → RDV → proposition → négo → gagné/perdu)
- Pondération budgétaire par étape pour chiffrer le pipeline en € HT

### Emails
- `draft_email` : rédige un brouillon `.eml` personnalisé dans `data/drafts/`
- `send_email` : envoi SMTP **uniquement si confirmation explicite + SMTP configuré**
- `list_email_drafts` : revue des brouillons en cours
- Signature automatique, journal des envois (`data/email_log.jsonl`)

### Visibilité
- `add_content_idea`, `list_content_ideas`, `update_content_state`
- Calendrier éditorial multi-canal (LinkedIn, blog, newsletter, webinaire, vidéo)

### Finances
- `add_mission`, `update_mission_status`, `list_missions`
- `compute_metrics` : CA encaissé / signé / prévu, pipeline pondéré, taux de conversion

### Stratégie
- `set_objective`, `list_objectives`, `update_objective_status`
- `write_strategy_note`, `read_strategy_note` : plan court/moyen terme en Markdown

### Opérationnel
- `add_task`, `list_tasks`, `complete_task` : todo priorisée par domaine

## Sécurité & confidentialité

- Toutes les données restent **en local**, dans `data/` (déjà ignoré par Git).
- Aucun envoi SMTP sans configuration explicite + confirmation au moment de l'appel.
- Politique RGPD intégrée au prompt système (pas de scraping, base "intérêt légitime"
  pour le B2B, mention de désinscription).

## Structure

```
mouns/
├── agent.py        # boucle Claude + tool runner
├── prompts.py      # system prompt (persona Mouns)
├── config.py       # chargement .env
├── storage.py      # I/O JSON atomique
├── tools/          # outils exposés au modèle
│   ├── prospects.py
│   ├── emails.py
│   ├── visibility.py
│   ├── finance.py
│   ├── strategy.py
│   └── tasks.py
└── __main__.py     # CLI
```

## Roadmap suggérée

- [ ] Connecteur LinkedIn (via API officielle / Sales Navigator export)
- [ ] Synchronisation Google Calendar pour les RDV planifiés
- [ ] Génération de propositions commerciales (PDF) à partir d'un template
- [ ] Tableau de bord web (lecture seule sur les fichiers JSON)
- [ ] Modules Datadock / Qualiopi pour la conformité formation
