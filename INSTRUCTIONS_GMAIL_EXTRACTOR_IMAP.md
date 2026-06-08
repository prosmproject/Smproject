# Guide — Gmail Client Extractor (version IMAP, sans OAuth)

Cette version évite complètement la configuration Google Cloud / OAuth.
Elle se connecte directement à Gmail via IMAP avec un **mot de passe d'application**.

---

## Étape 1 — Installer la dépendance

```powershell
pip install openpyxl
```

(`imaplib` et `email` sont inclus nativement avec Python.)

---

## Étape 2 — Activer la validation en 2 étapes

Pour CHAQUE compte (`stili.mounir@gmail.com` et `pro.smproject@gmail.com`) :

1. Va sur https://myaccount.google.com/security
2. Active **"Validation en 2 étapes"** (suis les instructions : numéro de téléphone, etc.)

> C'est obligatoire : Google n'autorise les mots de passe d'application que si la 2FA est active.

---

## Étape 3 — Générer un mot de passe d'application

Pour CHAQUE compte :

1. Va sur https://myaccount.google.com/apppasswords
   (connecte-toi avec le compte concerné si nécessaire)
2. Dans "Sélectionner une application" → choisis **"Autre (nom personnalisé)"**
3. Tape un nom, ex: `Extracteur Python`
4. Clique **Générer**
5. Google affiche un code à **16 caractères** (ex: `abcd efgh ijkl mnop`)
6. **Copie ce code SANS LES ESPACES** : `abcdefghijklmnop`

Répète pour le second compte.

---

## Étape 4 — Configurer le script

Ouvre `gmail_clients_extractor_imap.py` et remplace les lignes :

```python
ACCOUNTS = [
    {"email": "stili.mounir@gmail.com",  "app_password": "COLLE_TON_MOT_DE_PASSE_ICI"},
    {"email": "pro.smproject@gmail.com", "app_password": "COLLE_TON_MOT_DE_PASSE_ICI"},
]
```

par tes vrais mots de passe d'application (16 caractères, sans espaces) :

```python
ACCOUNTS = [
    {"email": "stili.mounir@gmail.com",  "app_password": "abcdefghijklmnop"},
    {"email": "pro.smproject@gmail.com", "app_password": "qrstuvwxyzabcdef"},
]
```

⚠️ **Ne partage jamais ce fichier avec tes mots de passe** — ils donnent un accès en lecture/écriture à ta boîte mail.

---

## Étape 5 — Lancer le script

```powershell
python gmail_clients_extractor_imap.py
```

Le script :
1. Se connecte aux deux comptes (sans navigateur, sans popup)
2. Analyse la boîte de réception et les messages envoyés
3. Détecte emails, noms, téléphones, LinkedIn, sites web dans les signatures
4. Génère **`clients_smproject.xlsx`**

---

## En cas d'erreur "Application password not valid"

- Vérifie que tu as bien copié les 16 caractères **sans espace**
- Vérifie que la validation en 2 étapes est bien **active** (pas juste configurée)
- Régénère un nouveau mot de passe d'application si besoin

---

## Réglages optionnels

```python
MAX_MESSAGES_PER_MAILBOX = 1000   # nombre de mails analysés par boîte (↑ = plus complet mais plus lent)
MAILBOXES_TO_SCAN = ["INBOX", '"[Gmail]/Sent Mail"']  # boîtes à analyser
EXCLUDED_DOMAINS = {...}          # domaines à ignorer (newsletters, plateformes...)
```
