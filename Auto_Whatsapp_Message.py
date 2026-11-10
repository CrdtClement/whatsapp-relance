#!/usr/bin/env python3
"""
     ╔═══════════════════════════════════════════════════════════╗
     ║                  Cardot Clément - INP-N7                  ║
     ║          Goal: Automatic WhatsApp message sending         ║
     ╚═══════════════════════════════════════════════════════════╝

 ══════════════════════ Purpose of this code: ══════════════════════

 Recommended way to send messages automatically:
    1: have the WhatsApp desktop app open, logged in to your account
    2: have your MEMBERS.csv file in the expected format:
       LAST_NAME, FIRST_NAME, EMAIL, PHONE, TRACK, FISA
       (French headers NOM, PRENOM, MAIL, NUMERO, FILIERE work too)
    3: write your message in message.txt (UTF-8, emojis allowed)
    4: be ready to press Enter for each person (time between two
       conversations is handled by '--delay', 5 seconds in the example)
    5: run this script:
        python Auto_Whatsapp_Message.py MEMBERS.csv --sequence --delay 5

 If you can't use the WhatsApp app:
    An HTML file is generated with the links to open.
    WARNING:
        1: only one WhatsApp window at a time.
        2: several clicks needed for a single message.

 ═════════════════════════════ Options: ════════════════════════════

 --message FILE     : text file containing the message (default: message.txt)
 --preview          : print the first message and its link, then exit
 --track X          : only keep one track, e.g. SN (alias: --filiere)
 --fisa X           : only keep the contacts whose FISA column equals X
 --country-code N   : country code for numbers starting with 0 (default: 33)
 --direct           : open the WhatsApp app directly (whatsapp:// links)
 --sequence         : open each conversation one after the other, no HTML page
 --delay N          : time between two auto messages, in seconds (default: 8)
 --start N          : resume from contact number N (--sequence mode)
 --output FILE      : name of the generated HTML file (default: links.html)

"""

from __future__ import annotations

import argparse
import csv
import html
import io
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

# ════════════════════ MESSAGE: EDIT message.txt ═════════════════════
# The message is read from message.txt (next to this script) or from the
# file given with --message. The text below is only used if no file exists.
#
# Fields you can use: {first_name} {last_name} {email} {phone} {track} {fisa}
# (French fields {prenom} {nom} {mail} {numero} {filiere} also work)
# Line break: a real new line in the file (the %0A encoding is automatic).
# Emojis: save the file as UTF-8. Do NOT write %20 / %0A by hand:
# they would be encoded a second time.

DEFAULT_MESSAGE = (
    "Hi {first_name} {last_name} from {track}!\n"
    "You can edit your message here and even add links!\n"
    "Here is the test link: https://www.ain7.com/fr"
)

MESSAGE_FILE = "message.txt"
COUNTRY_CODE = "33"  # France


FIELD_ALIASES = {
    "first_name": "first_name", "firstname": "first_name",
    "prenom": "first_name", "prénom": "first_name",
    "last_name": "last_name", "lastname": "last_name", "nom": "last_name",
    "email": "email", "e-mail": "email", "mail": "email",
    "phone": "phone", "tel": "phone", "numero": "phone", "numéro": "phone",
    "track": "track", "filiere": "track", "filière": "track",
    "fisa": "fisa",
}

# French fields still accepted inside the message
PLACEHOLDER_ALIASES = {
    "prenom": "first_name", "nom": "last_name", "mail": "email",
    "numero": "phone", "filiere": "track",
}


# ══════════════════════════ READING FILES: ══════════════════════════

def load_message(path: str | None) -> str:
    """Read the message from a UTF-8 text file (or use the default one)."""
    candidate = Path(path or MESSAGE_FILE)
    if candidate.is_file():
        try:
            text = candidate.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            sys.exit(f"{candidate} must be saved as UTF-8 (needed for emojis). "
                     "In Notepad: File > Save As > Encoding: UTF-8.")
        return text.replace("\r\n", "\n").rstrip("\n")
    if path:
        sys.exit(f"Message file not found: {path}")
    return DEFAULT_MESSAGE


def read_members(path: str) -> list[dict]:
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:  # e.g. "CSV" exported by Excel on Windows
        text = raw.decode("cp1252", errors="replace")

    # detect the delimiter: tab, ; or ,
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters="\t;,")
    except csv.Error:
        dialect = csv.excel_tab

    members = []
    for row in csv.DictReader(io.StringIO(text, newline=""), dialect=dialect):
        # lowercase keys renamed to field names, cleaned values
        member = {}
        for key, value in row.items():
            if key is None or not isinstance(value, str):
                continue  # extra column without a header
            key = key.strip().lower().replace(" ", "_")
            member[FIELD_ALIASES.get(key, key)] = value.strip()
        members.append(member)
    return members


# ══════════════════════════ LINK CREATION: ══════════════════════════

def normalize_phone(raw: str, country_code: str) -> str | None:
    """Return the number in international format without '+' (e.g. 33612345678)."""
    n = "".join(c for c in raw if c.isdigit() or c == "+")
    if not n:
        return None
    if n.startswith("+"):    # already international
        return n[1:] or None
    if n.startswith("00"):   # 0033...
        return n[2:] or None
    if n.startswith("0"):    # 06... -> 336...
        return country_code + n[1:]
    return n


def build_message(template: str, member: dict) -> str:
    """Replace the {fields}; unknown ones are left untouched."""
    values = dict(member)
    values["last_name"] = member.get("last_name", "").title()

    def replace(match: re.Match) -> str:
        key = PLACEHOLDER_ALIASES.get(match.group(1), match.group(1))
        return values.get(key, match.group(0))

    return re.sub(r"\{(\w+)\}", replace, template)


def build_link(member: dict, template: str, country_code: str,
               direct: bool = False) -> str | None:
    phone = normalize_phone(member.get("phone", ""), country_code)
    if not phone:
        return None
    # quote() encodes in UTF-8: spaces, line breaks AND emojis
    # (👋 becomes %F0%9F%91%8B)
    encoded = urllib.parse.quote(build_message(template, member))
    if direct:  # opens the WhatsApp app directly, without the wa.me page
        return f"whatsapp://send?phone={phone}&text={encoded}"
    return f"https://wa.me/{phone}?text={encoded}"


def open_link(url: str) -> None:
    """Open a link with the system's default application."""
    if hasattr(os, "startfile"):                 # Windows
        os.startfile(url)
    elif sys.platform == "darwin":               # macOS
        subprocess.run(["open", url])
    else:                                        # Linux
        subprocess.run(["xdg-open", url])


# ══════════════════════════ HTML CREATION: ══════════════════════════

def generate_html(links: list[tuple[dict, str]], skipped: list[dict]) -> str:
    rows = []
    for m, url in links:
        full_name = f"{m.get('first_name', '')} {m.get('last_name', '').upper()}".strip()
        details = " · ".join(x for x in (m.get("track"), m.get("fisa")) if x)
        rows.append(
            f'<li><a href="{html.escape(url)}" target="_blank">'
            f"{html.escape(full_name)}</a> "
            f'<small>{html.escape(details)}</small></li>'
        )
    no_phone = "".join(
        f"<li>{html.escape(m.get('first_name', ''))} {html.escape(m.get('last_name', ''))}</li>"
        for m in skipped
    )
    skipped_block = (
        f"<h3>No valid phone number ({len(skipped)})</h3><ul>{no_phone}</ul>"
        if skipped else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WhatsApp links</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }}
  li {{ margin: .6rem 0; font-size: 1.1rem; }}
  a {{ color: #128c7e; font-weight: 600; text-decoration: none; }}
  a:visited {{ color: #aaa; text-decoration: line-through; }}  /* already clicked */
  small {{ color: #666; }}
</style></head><body>
<h2>{len(links)} message(s) to send</h2>
<ol>{''.join(rows)}</ol>
{skipped_block}
</body></html>"""


# ══════════════════════════════ MAIN: ═══════════════════════════════

def main():
    # names and emojis printable even on legacy consoles
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    p = argparse.ArgumentParser(
        description="Generate personalized WhatsApp links from a contact file.")
    p.add_argument("contacts", help="CSV/TSV/TXT file of the members")
    p.add_argument("--message", metavar="FILE",
                   help=f"text file containing the message (default: {MESSAGE_FILE})")
    p.add_argument("--track", "--filiere", dest="track",
                   help="only keep one track (e.g. SN)")
    p.add_argument("--fisa", help="filter on the FISA column (e.g. yes)")
    p.add_argument("--country-code", default=COUNTRY_CODE,
                   help="country code for numbers starting with 0 (default: 33)")
    p.add_argument("--preview", action="store_true",
                   help="print the first message and its link, then exit")
    p.add_argument("--direct", action="store_true",
                   help="whatsapp:// links (opens the app without going through wa.me)")
    p.add_argument("--sequence", action="store_true",
                   help="open each conversation in turn, no HTML page")
    p.add_argument("--delay", "--delai", dest="delay", type=float, default=8,
                   help="time between two auto messages, in seconds (--sequence mode)")
    p.add_argument("--start", "--debut", dest="start", type=int, default=1,
                   help="contact number to resume from (--sequence mode)")
    p.add_argument("--output", "--sortie", dest="output", default="links.html",
                   help="output HTML file")
    args = p.parse_args()

    template = load_message(args.message)
    members = read_members(args.contacts)

    if args.track:
        members = [m for m in members
                   if m.get("track", "").lower() == args.track.lower()]
    if args.fisa:
        members = [m for m in members
                   if m.get("fisa", "").lower() == args.fisa.lower()]

    country_code = args.country_code.lstrip("+")
    links, skipped = [], []
    for m in members:
        url = build_link(m, template, country_code, args.direct or args.sequence)
        (links.append((m, url)) if url else skipped.append(m))

    if args.preview:
        if not links:
            sys.exit("No member with a valid phone number.")
        member, url = links[0]
        print(build_message(template, member))
        print("\n" + url)
        return

    if args.sequence:
        print(f"{len(links)} conversations. Press Enter in WhatsApp to send, "
              f"the next one opens by itself. Ctrl+C to stop.")
        for i, (m, url) in enumerate(links, 1):
            if i < args.start:
                continue
            print(f"[{i}/{len(links)}] {m.get('first_name', '')} {m.get('last_name', '')}")
            open_link(url)
            time.sleep(args.delay)
        return

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(generate_html(links, skipped))

    print(f"{len(links)} links generated in {args.output} "
          f"({len(skipped)} without a valid phone number).")


if __name__ == "__main__":
    main()
