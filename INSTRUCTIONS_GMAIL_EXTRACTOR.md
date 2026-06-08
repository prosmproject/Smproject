# Guide d'utilisation — Gmail Client Extractor

## Étape 1 — Installer les dépendances

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client openpyxl
```

---

## Étape 2 — Créer le projet Google Cloud & activer l'API Gmail

1. Va sur https://console.cloud.google.com/
2. Crée un nouveau projet (ex: "SMProject Gmail Extractor")
3. Dans le menu gauche : **API et services → Bibliothèque**
4. Recherche **"Gmail API"** → Activer
5. Dans **API et services → Écran de consentement OAuth** :
   - Choisis "Externe"
   - Remplis le nom de l'appli (ex: "SM Extractor")
   - Ajoute tes deux emails comme **utilisateurs de test** (stili.mounir@gmail.com et pro.smproject@gmail.com)
6. Dans **API et services → Identifiants** :
   - Cliquer **+ Créer des identifiants → ID client OAuth 2.0**
   - Type : **Application de bureau**
   - Nom : "SM Extractor Desktop"
   - Cliquer **Créer** puis **Télécharger le JSON**
7. **Renomme ce fichier en `credentials.json`** et place-le dans le même dossier que le script

---

## Étape 3 — Lancer le script

Place-toi dans le dossier du script, puis :

```bash
python gmail_clients_extractor.py
```

**Première exécution :**
- Une fenêtre de navigateur s'ouvre automatiquement pour chaque compte
- Connecte-toi avec `stili.mounir@gmail.com` puis autorise l'accès
- Fait pareil pour `pro.smproject@gmail.com`
- Les tokens sont sauvegardés (`token_perso.json`, `token_pro.json`) → plus besoin de se reconnecter les fois suivantes

---

## Résultat

Le fichier **`clients_smproject.xlsx`** est généré avec :

| Colonne | Description |
|---------|-------------|
| Nom / Prénom | Nom extrait du header email |
| Email | Adresse email du contact |
| Téléphone(s) | Numéros détectés dans les signatures |
| LinkedIn | Profils LinkedIn détectés |
| Site Web | URLs détectées dans les échanges |
| Compte source | Depuis quel compte Gmail |
| 1er contact | Date du premier échange |
| Dernier contact | Date du dernier échange |
| Nb échanges | Nombre total de mails échangés |
| Sujets | Aperçu des sujets des échanges |

---

## Configuration avancée (optionnel)

Dans le script, tu peux modifier :

```python
MAX_RESULTS_PER_QUERY = 500   # Augmente pour analyser plus de threads
```

```python
EXCLUDED_DOMAINS = {...}  # Ajoute des domaines à exclure
```

```python
MISSION_KEYWORDS = [...]  # Mots-clés pour cibler les emails de missions
```
