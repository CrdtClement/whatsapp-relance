# 💬 WhatsApp Relance

**Envoie un message personnalisé à toute une liste de contacts WhatsApp, sans créer de groupe, en quelques secondes par personne.**

Je gère une liste d'étudiants (Vice-Président) à l'N7. Ce script permet de prévenir individuellement chaque membres de la liste. Ce code transforme ton fichier CSV en liens `wa.me` / `whatsapp://` préremplis avec le prénom de chaque personne. Il suffit simplement d'appuyer sur **Entrée**.

> Rien n'est envoyé automatiquement : c'est à l'utilisateur de valider chaque message. Zéro risque de ban lié à de l'envoi en masse.

---

## ✨ Fonctionnalités

- 📄 **Lit le CSV tel quel** : séparateur (tabulation, `;` ou `,`) détecté automatiquement, en-têtes insensibles à la casse
- ✍️ **Message générique** avec champs personnalisés : `{prenom}`, `{nom}`, `{filiere}`…
- 📱 **Numéros normalisés** : `06 12 34 56 78`, `+33 6…` et `0033 6…` sont tous acceptés
- 🎯 **Filtres** par filière ou par statut pour cibler un sous-groupe
- ⚡ **3 modes d'envoi**, du plus simple au plus rapide
- ✅ **Suivi visuel** : les liens déjà cliqués se barrent en gris dans la page HTML
- 🚫 **Détection des lignes sans numéro valide**, listées à part
- 🪶 **Un seul fichier, aucune dépendance** (bibliothèque standard Python uniquement)

---

## 🚀 Démarrage rapide

```bash
#1: avoir l'app whatsapp ouverte avec son compte connecté
#2: avoir le ficher MEMBRES.csv au bon format prévu: NOM, PRENOM, MAIL, NUMERO, FILIERE, FISA
#3: etre pret à cliquer pour chaque personne (5 sec entre chacun, géré par 'delai')
#4: entrer ce script (modifie bien le message dans le fichier python !):
python Messages_Auto_Whatsapp.py MEMBRES.csv --sequence --delai 5
```

---

## 📋 Format du CSV

Le fichier doit contenir ces colonnes (l'ordre n'a pas d'importance) :

| NOM | PRENOM | MAIL | NUMERO | FILIERE | FISA |
|---|---|---|---|---|---|
| MACHIN | Bidule | bidule.machin@exemple.fr | 0612345678 | SN | |

Seules `PRENOM` et `NUMERO` sont indispensables, les autres colonnes servent aux champs du message et aux filtres. Un exemple est fourni dans [`MEMBRES.csv`](MEMBRES.csv).

> 💡 Un export Excel en « Texte (séparateur : tabulation) » ou « CSV UTF-8 » fonctionne directement.

---

## ✍️ Personnaliser le message

Ouvre `Messages_Auto_Whatsapp.py` et modifie la variable `MESSAGE` en haut du fichier :

```python
MESSAGE = (
    "Salut {prenom},\n"
    "Je t'envoie un message à propos de ..."
)
```

| Champ | Contenu |
|---|---|
| `{prenom}` | Prénom du contact |
| `{nom}` | Nom de famille (première lettre en majuscule) |
| `{mail}` | Adresse e-mail |
| `{numero}` | Numéro tel qu'écrit dans le CSV |
| `{filiere}` | Filière |
| `{fisa}` | Statut FISA |

Pour un retour à la ligne, utilise un vrai `\n`. **N'écris pas `%0A` ou `%20` à la main** : le script encode déjà le texte pour l'URL, ils seraient encodés une seconde fois et s'afficheraient tels quels dans WhatsApp.

---

## 🕹️ Les 3 modes

### Mode classique : page HTML avec liens `wa.me`
```bash
python Messages_Auto_Whatsapp.py membres.csv
```
Génère `liens.html`. Chaque clic ouvre WhatsApp (via la page `wa.me`) avec le message prêt. Compatible partout, y compris WhatsApp Web et mobile.

### Mode `--direct` : sans la page intermédiaire
```bash
python Messages_Auto_Whatsapp.py membres.csv --direct
```
Les liens utilisent le protocole `whatsapp://` et ouvrent directement l'application de bureau. Un clic en moins.

### Mode `--sequence` : le plus rapide ⚡
```bash
python Messages_Auto_Whatsapp.py membres.csv --sequence
```
Le script ouvre les conversations **les unes après les autres**, message prérempli. Le curseur est déjà dans le champ de texte : tu appuies sur **Entrée**, et la suivante s'ouvre toute seule après quelques secondes.

```bash
python Messages_Auto_Whatsapp.py membres.csv --sequence --delai 5     # 5 s entre chaque conversation
python Messages_Auto_Whatsapp.py membres.csv --sequence --debut 23    # reprendre au 23e contact
python Messages_Auto_Whatsapp.py membres.csv --sequence --filiere SN  # seulement la filière SN
```

`Ctrl + C` pour arrêter à tout moment.

---

## ⚙️ Toutes les options

| Option | Description | Défaut |
|---|---|---|
| `--filiere X` | Ne garder qu'une filière (ex. `SN`) | tous |
| `--fisa X` | Filtrer sur la colonne `FISA` (ex. `oui`) | tous |
| `--direct` | Liens `whatsapp://` au lieu de `wa.me` | désactivé |
| `--sequence` | Ouvre les conversations à la suite, sans page HTML | désactivé |
| `--delai N` | Secondes entre deux conversations (`--sequence`) | `8` |
| `--debut N` | Reprendre à partir du N-ième contact (`--sequence`) | `1` |
| `--sortie fichier.html` | Nom du fichier HTML généré | `liens.html` |

---

## 🧰 Prérequis

- **Python 3.8+**, rien à installer
- Pour `--direct` et `--sequence` : l'**application WhatsApp de bureau** (version Microsoft Store ou installateur officiel sur Windows, application macOS) installée et connectée **avant** de lancer le script. WhatsApp Web ne gère pas le protocole `whatsapp://`
- Au premier lancement, le système ou le navigateur peut demander l'autorisation d'ouvrir WhatsApp : choisis « toujours autoriser »

**Test rapide** : sous Windows, `Win + R` puis colle `whatsapp://send?phone=33612345678&text=test` avec ton propre numéro. La conversation doit s'ouvrir avec « test » dans le champ.

---

## 🔒 Confidentialité et bon usage

- **Ne pas publier son vrai CSV.** Il contient les numéros et adresses de tes contacts. Le code est simplement à télecharger et à utiliser.
- Le script n'envoie rien à ta place. Ce choix est volontaire : l'automatisation complète de l'envoi (bots, `whatsapp-web.js`, etc.) est bloqué par WhatsApp.
- Pour les contacts qui t'ont déjà enregistré, une **liste de diffusion** WhatsApp est encore plus rapide (un seul envoi). Ce script est surtout utile pour les autres.

---

## ⚠️ Avertissement

Ce projet est indépendant, pas approuvé par WhatsApp. Il se contente de générer des liens publics documentés (`wa.me`). Il faut l'utiliser dans le respect des conditions d'utilisation de WhatsApp et de la vie privée des personnes que tu contactes.
