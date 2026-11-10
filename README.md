# 💬 WhatsApp Link Sender

**Send a personalized WhatsApp message to a whole list of contacts, without creating a group, in a few seconds per person.**

Since I was elected vice president of an association at my engineering school (INP-N7), I had to send messages to a lot of people. This code can save a lot of time! 
I'm This script turns your contact file into pre-filled `wa.me` / `whatsapp://` links, personalized with each person's name. All that's left for you to do is press **Enter**.

> Nothing is sent automatically: you validate every message yourself. No mass-sending automation, so no risk of getting your number banned for it.

---

## Features

- **Message read from a text file**: write it once in `message.txt`, emojis included 🎉
- **Reads your contact file as is**: delimiter (tab, `;` or `,`) detected automatically, case-insensitive headers in English or French
- **Personalization fields**: `{first_name}`, `{last_name}`, `{track}`…
- **Preview mode** to check the final message and link (emojis too) before sending anything
- **Normalized phone numbers**: `06 12 34 56 78`, `+33 6…` and `0033 6…` are all accepted
- **Filters** to target a subset of your contacts
- **3 sending modes**, from the simplest to the fastest
- **Visual tracking**: links you already clicked are greyed out in the HTML page
- **Contacts without a valid number** are listed separately
- **Single file, no dependencies** (Python standard library only)

---

## Quick start

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# 1. Put your contact file in the folder (see format below)
# 2. Write your message in message.txt
# 3. Check it:
python Auto_Whatsapp_Message.py members.csv --preview
# 4. Send:
python Auto_Whatsapp_Message.py members.csv --sequence
```

---

## Contact file format

A CSV or TSV file (any extension, `.txt` included) with these columns, in any order:

| LAST_NAME | FIRST_NAME | EMAIL | PHONE | TRACK | FISA |
|---|---|---|---|---|---|
| MACHIN | Bidule | bidule.machin@example.com | 0612345678 | SN | |

French headers work too: `NOM`, `PRENOM`, `MAIL`, `NUMERO`, `FILIERE`.

Only `FIRST_NAME` and `PHONE` are required. The other columns feed the message fields and the filters. See [`members_example.csv`](members_example.csv).

> An Excel export as "Text (tab delimited)" or "CSV UTF-8" works directly. A classic Windows "CSV" export (cp1252) is also handled, so accents survive.

---

## Writing your message

Write your message in **`message.txt`**, next to the script. Use real line breaks, emojis and any of the fields below:

```text
Hi {first_name} 👋

Quick message about the next meeting ✨
Could you confirm if you're coming? 🙏

Thanks! ❤️
```

| Field | Content |
|---|---|
| `{first_name}` | First name |
| `{last_name}` | Last name (capitalized) |
| `{email}` | E-mail address |
| `{phone}` | Number as written in the file |
| `{track}` | Track |
| `{fisa}` | FISA status |

French fields (`{prenom}`, `{nom}`, `{mail}`, `{numero}`, `{filiere}`) are still accepted. Unknown `{fields}` are left untouched.

Use another file with `--message other_message.txt`. If no message file exists, a built-in default text is used.

### 😀 About emojis

- Save the message file as **UTF-8** (the default in recent versions of Notepad, VS Code, etc.). If it isn't, the script stops with an explicit error instead of sending garbage.
- Don't write `%20`, `%0A` or any URL encoding by hand: the script encodes the text itself (a 👋 becomes `%F0%9F%91%8B`), and doing it twice would show raw `%` codes in WhatsApp.
- Run `--preview` to see the first message exactly as it will be sent, along with its link.

---

## The 3 modes

### Classic mode: HTML page with `wa.me` links
```bash
python Auto_Whatsapp_Message.py members.csv
```
Generates `links.html`. Each click opens WhatsApp (through the `wa.me` page) with the message ready. Works everywhere, including WhatsApp Web and mobile.

### `--direct` mode: no intermediate page
```bash
python Auto_Whatsapp_Message.py members.csv --direct
```
Links use the `whatsapp://` protocol and open the desktop app directly. One click less.

### `--sequence` mode: the fastest ⚡
```bash
python Auto_Whatsapp_Message.py members.csv --sequence
```
The script opens the conversations **one after the other**, message pre-filled. The cursor is already in the text field: press **Enter**, and the next one opens by itself after a few seconds.

```bash
python Auto_Whatsapp_Message.py members.csv --sequence --delay 5     # 5 s between conversations
python Auto_Whatsapp_Message.py members.csv --sequence --start 23    # resume at contact #23
python Auto_Whatsapp_Message.py members.csv --sequence --track SN    # only the SN track
```

`Ctrl + C` to stop at any time.

---

## ⚙️ All options

| Option | Description | Default |
|---|---|---|
| `--message FILE` | UTF-8 text file containing the message | `message.txt` |
| `--preview` | Print the first message and its link, then exit | off |
| `--track X` | Only keep one track (e.g. `SN`) | all |
| `--fisa X` | Filter on the `FISA` column (e.g. `yes`) | all |
| `--country-code N` | Country code for numbers starting with `0` | `33` |
| `--direct` | `whatsapp://` links instead of `wa.me` | off |
| `--sequence` | Open conversations one after the other, no HTML page | off |
| `--delay N` | Seconds between two conversations (`--sequence`) | `8` |
| `--start N` | Resume from the N-th contact (`--sequence`) | `1` |
| `--output file.html` | Name of the generated HTML file | `links.html` |

The former French options (`--filiere`, `--delai`, `--debut`, `--sortie`) still work.

---

## Requirements

- **Python 3.8+**, nothing to install
- For `--direct` and `--sequence`: the **WhatsApp desktop app** (Microsoft Store version or official installer on Windows, macOS app) installed and logged in **before** running the script. WhatsApp Web doesn't handle the `whatsapp://` protocol
- On first use, the system or browser may ask permission to open WhatsApp: choose "always allow"

**Quick test**: on Windows, press `Win + R` and paste `whatsapp://send?phone=33612345678&text=test 👋` with your own number. The conversation should open with the text in the input field.

---

## Disclaimer

This project is independent and is neither affiliated with nor endorsed by WhatsApp or Meta. It only generates documented public links (`wa.me`). Use it in accordance with WhatsApp's terms of service and with respect for the privacy of the people you contact.
