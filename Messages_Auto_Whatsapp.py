#!/usr/bin/env python3
"""
     ╔═══════════════════════════════════════════════════════════╗
     ║                  Cardot Clément - INP-N7                  ║
     ║   Objectif: Envoi de messages automatique sur whatsapp    ║
     ╚═══════════════════════════════════════════════════════════╝

 ═══════════════════════ Objectif de ce code: ═══════════════════════

 Recommandation pour envoi automatique:
    1: avoir l'app whatsapp ouverte avec son compte connecté
    2: avoir le ficher MEMBRES.csv au bon format prévu: NOM, PRENOM, MAIL, NUMERO, FILIERE, FISA
    3: etre pret à cliquer pour chaque personne (5 sec entre chacun, géré par 'delai')
    4: entrer ce script:
        python Messages_Auto_Whatsapp.py MEMBRES.csv --sequence --delai 5

Si impossibilité d'utiliser l'appli whatsapp:
    Création d'un ficher HTML qui génere les liens à ouvrir.
    ATTENTION:
        1: une seule fenetre whatsapp à la fois.
        2: plusieurs clics necessaires pour un seul message.
"""

from __future__ import annotations

import argparse
import csv
import html
import os
import subprocess
import sys
import time
import urllib.parse

# ═══════════════════════ MESSAGE À MODIFIER: ════════════════════════
# Champs utilisables : {prenom} {nom} {mail} {numero} {filiere} {fisa}
# Retour à la ligne : un vrai "\n" (l'encodage en %0A est fait automatiquement)
# Ne pas écrire %20 / %0A à la main : ils seraient encodés une 2e fois.

MESSAGE = (
    "Salut {prenom} {nom} de {filiere} !\n"
    "Tu peux modifier ici ton message et même ajouter des liens !"
    "Voici le lien test: https://www.ain7.com/fr"
)

INDICATIF = "33"  # France


# ═════════════════════════ CREATION LIENS: ══════════════════════════

def normaliser_numero(brut: str) -> str | None:
    """Renvoie le numéro au format international sans '+' (ex: 33612345678)."""
    n = "".join(c for c in brut if c.isdigit() or c == "+")
    if not n:
        return None
    if n.startswith("+"):
        return n[1:]
    if n.startswith("00"):
        return n[2:]
    if n.startswith("0"):
        return INDICATIF + n[1:]
    return n


def lire_membres(chemin: str) -> list[dict]:
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        echantillon = f.read(4096)
        f.seek(0)
        try:
            dialecte = csv.Sniffer().sniff(echantillon, delimiters="\t;,")
        except csv.Error:
            dialecte = csv.excel_tab
        lecteur = csv.DictReader(f, dialect=dialecte)
        membres = []
        for ligne in lecteur:
            # clés en minuscules, valeurs nettoyées
            membres.append({(k or "").strip().lower(): (v or "").strip()
                            for k, v in ligne.items()})
        return membres


def construire_lien(membre: dict, direct: bool = False) -> str | None:
    numero = normaliser_numero(membre.get("numero", ""))
    if not numero:
        return None
    texte = MESSAGE.format_map({
        "prenom": membre.get("prenom", ""),
        "nom": membre.get("nom", "").title(),
        "mail": membre.get("mail", ""),
        "numero": membre.get("numero", ""),
        "filiere": membre.get("filiere", ""),
        "fisa": membre.get("fisa", ""),
    })
    texte_enc = urllib.parse.quote(texte)
    if direct:  # ouvre directement l'appli WhatsApp, sans la page wa.me
        return f"whatsapp://send?phone={numero}&text={texte_enc}"
    return f"https://wa.me/{numero}?text={texte_enc}"



# ══════════════════════════ CREATION HTML: ══════════════════════════

def ouvrir(url: str) -> None:
    """Ouvre un lien avec l'application par défaut du système."""
    if hasattr(os, "startfile"):                 # Windows
        os.startfile(url)
    elif sys.platform == "darwin":               # macOS
        subprocess.run(["open", url])
    else:                                        # Linux
        subprocess.run(["xdg-open", url])


def generer_html(liens: list[tuple[dict, str]], ignores: list[dict]) -> str:
    lignes = []
    for m, url in liens:
        nom_complet = f"{m.get('prenom', '')} {m.get('nom', '').upper()}".strip()
        details = " · ".join(x for x in (m.get("filiere"), m.get("fisa")) if x)
        lignes.append(
            f'<li><a href="{html.escape(url)}" target="_blank">'
            f"{html.escape(nom_complet)}</a> "
            f'<small>{html.escape(details)}</small></li>'
        )
    sans_num = "".join(
        f"<li>{html.escape(m.get('prenom', ''))} {html.escape(m.get('nom', ''))}</li>"
        for m in ignores
    )
    bloc_ignores = (
        f"<h3>Sans numéro valide ({len(ignores)})</h3><ul>{sans_num}</ul>"
        if ignores else ""
    )
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Liens WhatsApp</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }}
  li {{ margin: .6rem 0; font-size: 1.1rem; }}
  a {{ color: #128c7e; font-weight: 600; text-decoration: none; }}
  a:visited {{ color: #aaa; text-decoration: line-through; }}  /* déjà cliqué */
  small {{ color: #666; }}
</style></head><body>
<h2>{len(liens)} message(s) à envoyer</h2>
<ol>{''.join(lignes)}</ol>
{bloc_ignores}
</body></html>"""



# ═══════════════════════════════ MAIN: ══════════════════════════════

def main():
    p = argparse.ArgumentParser(description="Génère des liens wa.me depuis un CSV.")
    p.add_argument("csv", help="fichier CSV/TSV des membres")
    p.add_argument("--filiere", help="ne garder qu'une filière (ex: SN)")
    p.add_argument("--fisa", help="filtre sur la colonne FISA (ex: oui)")
    p.add_argument("--sortie", default="liens.html", help="fichier HTML de sortie")
    p.add_argument("--direct", action="store_true",
                   help="liens whatsapp:// (ouvre l'appli sans passer par wa.me)")
    p.add_argument("--sequence", action="store_true",
                   help="ouvre chaque conversation à la suite, sans page HTML")
    p.add_argument("--delai", type=float, default=8,
                   help="secondes entre deux conversations en mode --sequence")
    p.add_argument("--debut", type=int, default=1,
                   help="numéro du membre à partir duquel reprendre (--sequence)")
    args = p.parse_args()

    membres = lire_membres(args.csv)

    if args.filiere:
        membres = [m for m in membres
                   if m.get("filiere", "").lower() == args.filiere.lower()]
    if args.fisa:
        membres = [m for m in membres
                   if m.get("fisa", "").lower() == args.fisa.lower()]

    liens, ignores = [], []
    for m in membres:
        url = construire_lien(m, args.direct or args.sequence)
        (liens.append((m, url)) if url else ignores.append(m))

    if args.sequence:
        print(f"{len(liens)} conversations. Appuie sur Entrée dans WhatsApp pour "
              f"envoyer, la suivante s'ouvre toute seule. Ctrl+C pour arrêter.")
        for i, (m, url) in enumerate(liens, 1):
            if i < args.debut:
                continue
            print(f"[{i}/{len(liens)}] {m.get('prenom', '')} {m.get('nom', '')}")
            ouvrir(url)
            time.sleep(args.delai)
        return

    with open(args.sortie, "w", encoding="utf-8") as f:
        f.write(generer_html(liens, ignores))

    print(f"{len(liens)} liens générés dans {args.sortie} "
          f"({len(ignores)} sans numéro valide).")


if __name__ == "__main__":
    main()