"""Bootstrap initial de Mouns — produit les fondations stratégiques de démarrage.

À exécuter UNE SEULE FOIS au démarrage du projet, avant que Mounir ne lance
`mouns chat` avec sa vraie clé API. Ce script écrit :

- data/strategy.md             — plan stratégique 12 mois (ICP, leviers, montage)
- data/kpis.json               — 4 objectifs Q1 chiffrés
- data/content.json            — calendrier éditorial démarrage (12 idées)
- data/tasks.json               — todo des 2 premières semaines
- data/drafts/*.eml            — 3 templates d'emails de prospection

Ces données serviront de base que Mouns enrichira ensuite via la conversation
(au lieu de partir de zéro à chaque session).
"""
from __future__ import annotations

from datetime import date, timedelta
from email.message import EmailMessage

from mouns.config import load_config
from mouns.storage import write_json


def iso(d: date) -> str:
    return d.isoformat()


SM_PROJECT_FOLDERS = (
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


def main():
    cfg = load_config()
    today = date.today()

    # ---------- 0. Arborescence documentaire SM_PROJECT/ ----------
    sm_root = cfg.data_dir / "SM_PROJECT"
    for f in SM_PROJECT_FOLDERS:
        (sm_root / f).mkdir(parents=True, exist_ok=True)
    # Index README dans chaque section pour expliquer son rôle
    sections_doc = {
        "01_Strategie": "Plans 12 mois, revues hebdo/mensuelles/trimestrielles, pivots, notes de positionnement.",
        "02_Prospection": "Listes de cibles, séquences d'emails et messages LinkedIn, scripts d'appel.",
        "03_Missions": "Documents de missions en cours (cadrage, livrables, plannings, comptes rendus).",
        "04_Clients": "Fiches clients, retours d'expérience, contrats-cadres, témoignages.",
        "05_Formation_MS_Project": "Supports, programmes pédagogiques, parcours certifiants, exercices.",
        "06_LinkedIn": "Posts publiés, articles longs, calendrier éditorial, captures et analytics.",
        "07_Administratif": "Statuts, attestations Qualiopi, RGPD, URSSAF, attestations OPCO.",
        "08_Finances": "CA, factures, devis, prévisionnel, échéances fiscales.",
        "09_Portfolio": "Cas d'étude anonymisés, témoignages, références mobilisables en RDV.",
        "10_Opportunites": "AO en cours, opportunités détectées sur Malt/Freelance/LinkedIn, missions à candidater.",
    }
    for folder, desc in sections_doc.items():
        readme = sm_root / folder / "README.md"
        if not readme.exists():
            readme.write_text(f"# {folder}\n\n{desc}\n", encoding="utf-8")
    q1_end = date(today.year, 3, 31) if today.month <= 3 else date(today.year + 1, 3, 31)
    q2_end = date(today.year, 6, 30) if today.month <= 6 else date(today.year + 1, 6, 30)

    # ---------- 1. Plan stratégique 12 mois ----------
    strategy = f"""# Plan stratégique 12 mois — SM Project

> Rédigé par Mouns au démarrage. À actualiser à chaque revue trimestrielle.

## Vision

Faire de **SM Project** la référence francophone reconnue sur l'expertise
**MS Project + gestion de projets** sur le segment ETI / grandes entreprises,
avec une présence forte sur LinkedIn, un pipeline de missions chaînées et un
mix de revenus diversifié (50 % formation, 30 % conseil/PMO, 20 % récurrent).

## Positionnement

- **Promesse** : « Faire tenir vos plannings et certifier vos équipes
  MS Project, sans cabinet de conseil entre nous. »
- **Différenciateur** : expertise opérationnelle (Mounir est praticien, pas
  seulement formateur) + interventions courtes à fort impact + tarification
  transparente.

## ICP (Ideal Customer Profile)

### Persona 1 — *Le Directeur PMO en surchauffe*
- Profil : Directeur de projets / Head of PMO dans ETI (BTP, énergie,
  industrie, ingénierie, IT)
- Effectif : 500-5000 personnes
- Douleur : plannings qui glissent, équipes pas montées sur MS Project,
  reporting CODIR difficile à produire
- Déclencheur : nouveau gros projet, audit interne, arrivée d'un nouveau
  DG/CFO qui demande de la visibilité
- Offre adaptée : audit flash (5 jours) + mission PMO mensuelle (3-5 j/mois)
- Panier moyen visé : 25-60 k€ HT sur 6 mois

### Persona 2 — *Le Responsable Formation / RH Dev*
- Profil : Responsable formation ou L&D dans grand groupe
- Douleur : trouver un formateur MS Project crédible, finançable OPCO/CPF,
  qui produit des supports propres et qui s'adapte au contexte métier
- Déclencheur : nouveau projet majeur, plan de développement des compétences
- Offre adaptée : parcours certifiant intra (3-5 jours, intra) + e-learning
  d'accompagnement
- Panier moyen visé : 8-25 k€ HT par cohorte

### Persona 3 — *Le Cabinet de conseil partenaire*
- Profil : Cabinet de conseil en management ou IT (10-200 personnes) sans
  expert MS Project en interne
- Douleur : décrocher des missions où MS Project est exigé, sans embaucher
- Déclencheur : appel d'offres avec contrainte MS Project
- Offre adaptée : sous-traitance facturée TJM 750-950 € HT, badge cabinet
- Panier moyen visé : 15-40 k€ HT par mission

### Persona 4 — *Le Responsable Formation OPCO / OF partenaire*
- Profil : Référent pédagogique chez un OPCO ou un OF généraliste
- Douleur : besoin d'un formateur référencé pour cataloguer une offre
- Offre adaptée : intervention au catalogue, refacturation OPCO
- Panier moyen visé : 1 200-2 500 € HT / journée

## Leviers prioritaires (par ordre d'impact)

| # | Levier | Impact | Effort | Cadence |
|---|---|---|---|---|
| 1 | LinkedIn : 4 posts/sem (retours d'expérience, méthodes, débats) | Élevé | Moyen | hebdo |
| 2 | Prospection LinkedIn ciblée : 15 demandes connexion/sem + 5 messages personnalisés | Élevé | Moyen | hebdo |
| 3 | Demande de recommandations clients (chaque mission terminée) | Élevé | Faible | continu |
| 4 | Webinaire mensuel "MS Project en 30 minutes" (lead magnet) | Élevé | Élevé | mensuel |
| 5 | Référencement Mon Compte Formation + Qualiopi | Moyen | Élevé | trimestriel |
| 6 | Articles de fond blog (1/mois, SEO long terme) | Moyen | Moyen | mensuel |
| 7 | Partenariat avec 2 cabinets de conseil (sous-traitance) | Élevé | Moyen | semestriel |
| 8 | Catalogue OPCO (Atlas, Akto, Opcommerce) | Moyen | Élevé | semestriel |

## Plan d'enchaînement des missions (court/moyen terme)

**Principe** : ne jamais finir une mission sans avoir signé la suivante.

1. **Mois 1-2** : 2 formations courtes pour cash-flow rapide + lancement
   campagne LinkedIn
2. **Mois 2-4** : 1 audit flash PMO → conversion en mission PMO récurrente
3. **Mois 3-6** : 1 partenariat cabinet activé → 2 missions sous-traitées
4. **Mois 6-9** : 1ʳᵉ cohorte parcours certifiant (8-12 stagiaires) +
   2 missions PMO récurrentes en cours
5. **Mois 9-12** : webinaire mensuel produit, audience LinkedIn 5 000+,
   pipeline pondéré ≥ 80 k€ HT en permanence

## Hypothèses tarifaires (à valider)

- Journée formation intra : 1 500-1 800 € HT
- Journée audit / conseil expert : 1 200-1 400 € HT
- TJM PMO récurrent (engagement 3 mois +) : 950-1 100 € HT
- Sous-traitance cabinet : 750-950 € HT (selon marge laissée au cabinet)
- E-learning accompagnement : pack 350-500 € HT/stagiaire

## Optimisation revenu net

- **Statut** : revoir adéquation (EI au réel / EURL IS / SASU) selon CA
  projeté. Si CA > 80 k€ HT, basculer IS pour optimiser dividendes/RSI.
- **Charges** : passer 100 % des outils en abonnement annuel (économie 15-20 %).
- **Aides** : explorer CIR si développement de cours en ligne propres ;
  abondement CPF pour les particuliers.
- **Trésorerie** : maintenir 3 mois de charges en réserve avant
  réinvestissement.

## Réinvestissement (par ordre de priorité)

1. **Production de contenu pérenne** (cours en ligne propre, templates
   premium) — actif qui produit du CA sans temps consommé.
2. **Certification PMP** (différenciateur côté grands comptes).
3. **Outillage CRM/automation** (HubSpot Starter ou équivalent) à partir de
   50+ prospects actifs.
4. **Sous-traitance d'un binôme formateur** quand 2 cohortes simultanées
   deviennent récurrentes.

## Revue

- **Hebdo (vendredi 30 min)** : pipeline, relances, contenus publiés, CA
  signé/encaissé.
- **Mensuelle (1er du mois, 1h)** : KPI, objectifs, ajustements tarifs.
- **Trimestrielle** : actualisation de ce document.
"""
    (cfg.data_dir / "strategy.md").write_text(strategy, encoding="utf-8")

    # ---------- 2. Objectifs Q1 ----------
    objectifs = {
        "objectifs": [
            {
                "id": "O-0001",
                "intitule": "Atteindre 25 k€ HT signés ce trimestre",
                "horizon": "trimestre",
                "cible_chiffree": "25 000 € HT",
                "echeance": iso(q1_end),
                "levier": "2 formations intra + 1 audit flash PMO converti en mission",
                "statut": "en_cours",
                "created_at": iso(today),
            },
            {
                "id": "O-0002",
                "intitule": "Construire un vivier de 30 prospects qualifiés",
                "horizon": "trimestre",
                "cible_chiffree": "30 prospects score ≥ 50",
                "echeance": iso(q1_end),
                "levier": "60 prises de contact LinkedIn + 20 emails personnalisés",
                "statut": "en_cours",
                "created_at": iso(today),
            },
            {
                "id": "O-0003",
                "intitule": "Passer 2 000 → 3 000 abonnés LinkedIn",
                "horizon": "trimestre",
                "cible_chiffree": "+1 000 abonnés",
                "echeance": iso(q1_end),
                "levier": "4 posts/sem + 1 webinaire mensuel",
                "statut": "en_cours",
                "created_at": iso(today),
            },
            {
                "id": "O-0004",
                "intitule": "Activer 1 partenariat cabinet de conseil",
                "horizon": "semestre",
                "cible_chiffree": "1 contrat-cadre signé",
                "echeance": iso(q2_end),
                "levier": "Approche directe de 8 cabinets ciblés + offre sous-traitance",
                "statut": "en_cours",
                "created_at": iso(today),
            },
        ],
        "strategie": "Voir data/strategy.md",
    }
    write_json(cfg.data_dir / "kpis.json", objectifs)

    # ---------- 3. Idées de contenu LinkedIn ----------
    base = today
    ideas = [
        ("Les 3 erreurs qui font sauter un planning MS Project", "linkedin_post", "Retour d'expérience", "Chef de projet", 1, "RDV découverte"),
        ("Pourquoi 80 % des PMO échouent au bout de 18 mois", "linkedin_post", "Débat", "Directeur PMO", 3, "Téléchargement audit gratuit"),
        ("MS Project vs Smartsheet vs Jira : ce que personne ne vous dit", "linkedin_article", "Comparaison", "DSI", 5, "RDV découverte"),
        ("Comment j'ai sauvé un projet à 4 mois du go-live (étude de cas anonymisée)", "linkedin_post", "Étude de cas", "Directeur de projet", 8, "Témoignage long en commentaire"),
        ("3 indicateurs CODIR qui sortent de MS Project en 2 clics", "linkedin_post", "Méthode", "Directeur PMO", 10, "Template offert"),
        ("Pourquoi former vos chefs de projet plutôt que recruter (calcul ROI)", "linkedin_post", "Argumentaire RH", "Responsable formation", 12, "Brochure parcours certifiant"),
        ("Le RACI que j'utilise pour TOUS mes projets MS Project", "linkedin_post", "Outil", "Chef de projet", 15, "Template offert"),
        ("Webinaire : MS Project en 30 minutes — l'essentiel pour démarrer", "webinaire", "Lead magnet", "Mixte", 18, "Inscription webinaire"),
        ("Comment financer une formation MS Project (OPCO / CPF / plan)", "linkedin_post", "Pratique", "Responsable formation", 20, "Devis personnalisé"),
        ("J'ai audité 30 plannings cette année : voici les 5 patterns qui reviennent", "linkedin_article", "Synthèse", "Directeur PMO", 22, "Audit flash"),
        ("Le réflexe `Update Project` que 90 % des utilisateurs ignorent", "linkedin_post", "Astuce produit", "Chef de projet", 25, "Inscription newsletter"),
        ("Pourquoi je refuse les missions PMO < 3 mois (et ce que je propose à la place)", "linkedin_post", "Positionnement", "Directeur PMO", 28, "RDV découverte"),
    ]
    content = [
        {
            "id": f"C-{i+1:04d}",
            "titre": titre,
            "canal": canal,
            "angle": angle,
            "cible": cible,
            "date_publication": iso(base + timedelta(days=delta)),
            "appel_action": cta,
            "etat": "idee",
            "created_at": iso(today),
        }
        for i, (titre, canal, angle, cible, delta, cta) in enumerate(ideas)
    ]
    write_json(cfg.data_dir / "content.json", content)

    # ---------- 4. Tâches des 2 premières semaines ----------
    tasks_data = [
        ("Valider statut juridique cible (EI réel vs EURL IS) avec expert-comptable", "haute", 5, "strategie"),
        ("Refondre profil LinkedIn (bandeau, accroche, expérience, expertise)", "haute", 3, "marketing"),
        ("Préparer kit prospection : pitch 30s, slides 1-pager, étude de cas anonyme", "haute", 5, "commercial"),
        ("Lister 30 entreprises cibles ETI (BTP/industrie) + identifier 1 contact PMO chacune", "haute", 7, "commercial"),
        ("Publier 1er post LinkedIn (idée C-0001)", "haute", 1, "marketing"),
        ("Planifier webinaire 'MS Project en 30 min' (date, page d'inscription)", "moyenne", 14, "marketing"),
        ("Mettre à jour les tarifs publics (grille HT, conditions, mentions OPCO)", "moyenne", 7, "commercial"),
        ("Demander recommandation LinkedIn aux 3 derniers clients", "moyenne", 5, "marketing"),
        ("Lancer démarche Qualiopi si pas déjà certifié (devis cabinet d'audit)", "moyenne", 14, "admin"),
        ("Identifier 8 cabinets de conseil cibles pour partenariat sous-traitance", "moyenne", 10, "commercial"),
    ]
    tasks = [
        {
            "id": f"T-{i+1:04d}",
            "intitule": txt,
            "priorite": pri,
            "echeance": iso(today + timedelta(days=delta)),
            "domaine": dom,
            "lien_id": None,
            "statut": "todo",
            "created_at": iso(today),
        }
        for i, (txt, pri, delta, dom) in enumerate(tasks_data)
    ]
    write_json(cfg.data_dir / "tasks.json", tasks)

    # ---------- 5. Templates d'emails ----------
    signature = f"--\n{cfg.owner_name}\n{cfg.company}\n{cfg.email or '(email à renseigner)'}\n{cfg.phone or ''}".rstrip()

    templates = [
        (
            "modele_pmo_eti.eml",
            "[NOM] – audit flash de votre planning projet ?",
            """Bonjour [PRENOM],

J'ai vu chez [SOCIETE] un projet [NOM_PROJET / domaine] récemment annoncé.
Côté planning et coordination, ce type de chantier passe souvent par 3 phases
critiques où une lecture extérieure fait gagner 4 à 6 semaines.

Je propose des audits flash de 5 jours sur MS Project : revue du planning,
des charges, du chemin critique et du reporting CODIR. Livrable concret en
sortie, et 90 % de mes audits débouchent sur une mission PMO mensuelle si
besoin (3-5 j/mois, engagement révisable).

Si l'angle vous parle, je vous propose 20 minutes en visio la semaine
prochaine pour un premier échange.

Bien à vous,
""",
            "prospection",
        ),
        (
            "modele_rh_formation.eml",
            "Parcours MS Project certifiant pour vos chefs de projet",
            """Bonjour [PRENOM],

[SOCIETE] communique régulièrement sur sa montée en maturité projet. Si
vous avez des chefs de projet à monter en compétence sur MS Project (de
l'initiation au pilotage multi-projet), j'anime des parcours intra de 3 à 5
jours, finançables OPCO et CPF, avec une option e-learning d'accompagnement
sur 8 semaines pour ancrer les acquis.

Mes promotions tournent autour de 8-12 stagiaires et le taux d'aboutissement
à la certification est de [XX] %. Je peux vous envoyer la brochure parcours
+ 2 références récentes si pertinent.

Vous me dites si on cale 20 minutes pour balayer vos besoins ?

Bien à vous,
""",
            "prospection",
        ),
        (
            "modele_cabinet_partenaire.eml",
            "Sous-traitance MS Project / PMO pour vos missions",
            """Bonjour [PRENOM],

Je suis [PRENOM_MOUNIR], expert MS Project & PMO indépendant ([XX] ans
d'expérience, références ETI dans [SECTEURS]). J'interviens régulièrement en
sous-traitance pour des cabinets qui ont besoin d'un expert MS Project sur
un appel d'offres sans embaucher un permanent dédié.

Mes modalités : badge cabinet, TJM transparent (entre 750 et 950 € HT
selon mission), 0 démarchage de vos clients en direct. Je peux intervenir
en planification initiale, sauvetage, formation intra côté client ou audit.

Si vous avez une mission ou un AO en cours où le sujet revient, je vous
réserve 20 minutes pour qu'on se cale ?

Bien à vous,
""",
            "prospection",
        ),
    ]

    drafts_dir = cfg.data_dir / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    for fname, subj, body, _ in templates:
        msg = EmailMessage()
        msg["Subject"] = subj
        msg["From"] = cfg.email or "contact@smproject.fr"
        msg["To"] = "[A_PERSONNALISER]@exemple.com"
        msg.set_content(body.rstrip() + "\n\n" + signature)
        (drafts_dir / fname).write_bytes(bytes(msg))

    # ---------- Récap ----------
    print(f"""
Mouns initialisé pour {cfg.company} ({cfg.owner_name}).

Données créées dans {cfg.data_dir} :
  • SM_PROJECT/           — arborescence documentaire en 10 sections
  • strategy.md           — plan stratégique 12 mois (ICP, leviers, montage)
  • kpis.json             — 4 objectifs (3 Q1 + 1 semestriel)
  • content.json          — 12 idées de contenus (LinkedIn / article / webinaire)
  • tasks.json            — 10 tâches priorisées sur les 2 prochaines semaines
  • drafts/               — 3 templates emails (PMO, RH formation, cabinet)

Prochaines étapes :
  1. Édite .env avec ta clé ANTHROPIC_API_KEY et ton identité.
  2. Lance `mouns chat` : Mouns lira ces fondations et te proposera un
     plan d'attaque pour la semaine.
  3. À mesure que tu ajoutes des vrais prospects et missions, Mouns
     enrichira le pipeline et chiffrera les KPI réels.
""")


if __name__ == "__main__":
    main()
