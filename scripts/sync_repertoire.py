#!/usr/bin/env python3
"""
sync_repertoire.py — Pipeline Google Sheet → choraoke-app/index.html

Lit le Google Sheet "🎵 Base de données" via export CSV public,
régénère le tableau JSON des morceaux dans l'app Choraoké,
et injecte l'onglet Setlist si des morceaux sont cochés.

Usage :
    python scripts/sync_repertoire.py

Pré-requis :
    - Le Google Sheet doit être partagé en lecture publique (ou via lien)
    - SHEET_ID doit être renseigné ci-dessous
    - Python 3.8+
"""

import csv
import io
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================================
# CONFIGURATION — À REMPLIR / MODIFIER AVANT CHAQUE SESSION
# ============================================================================

# ID du Google Sheet (visible dans l'URL entre /d/ et /edit)
SHEET_ID = "1tkQ1J7bzU_4reaTiF4LMvWeRwE0auRheOWofjVnJyFw"

# Nom de l'onglet dans le Sheet (encodé pour l'URL)
SHEET_TAB = "🎵 Base de données"

# Infos session — mettre à jour avant chaque Choraoké
SESSION_NAME = ""     # Ex: "Choraoké #21 — Summer Vibes"
SESSION_DATE = ""     # Ex: "29 avril 2025"
SESSION_LIEU = ""     # Ex: "Berges du Rhône"

# Chemins (relatifs à la racine du repo)
REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = REPO_ROOT / "choraoke-app" / "index.html"

# ============================================================================
# COLONNES DU SHEET — mapping exact (ordre dans le Sheet, 0-indexé)
# # | Langue | Track Name | Artist Name(s) | Instrument | Difficulté vocale |
# BPM | Tonalité | Key (EN) | Capo (guitare) | Genres |
# Validée Choraoké | Spotify Link | Lien UltimateGuitar | genius_url | Notes
# ============================================================================

COL_NUM = 0
COL_LANGUE = 1
COL_TRACK = 2
COL_ARTIST = 3
COL_INSTRUMENT = 4
COL_DIFFICULTE = 5
COL_BPM = 6
COL_TONALITE = 7
COL_KEY_EN = 8
COL_CAPO = 9
COL_GENRES = 10
COL_VALIDEE = 11
COL_SPOTIFY = 12
COL_UG = 13
COL_GENIUS_URL = 14
COL_NOTES = 15
# Colonne Setlist — checkbox ajoutée après Notes
COL_SETLIST = 16


def fetch_sheet_csv(sheet_id: str, tab_name: str) -> str:
    """Télécharge un onglet du Google Sheet au format CSV."""
    encoded_tab = urllib.request.quote(tab_name)
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={encoded_tab}"
    )
    print(f"📥 Téléchargement du Sheet...")
    print(f"   URL : {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8-sig")
    except urllib.error.URLError as e:
        print(f"❌ Erreur réseau : {e}")
        sys.exit(1)
    return data


def parse_langue(val: str) -> str:
    """Convertit la langue du Sheet en code court (E/F/I)."""
    val = val.strip().upper()
    if val in ("E", "EN", "ENGLISH", "ANGLAIS"):
        return "E"
    if val in ("F", "FR", "FRENCH", "FRANÇAIS", "FRANCAIS"):
        return "F"
    if val in ("I", "IT", "ES", "IT/ES", "ITALIEN", "ESPAGNOL", "ITALIAN", "SPANISH"):
        return "I"
    # Fallback : première lettre
    return val[0] if val else "E"


def parse_instrument(val: str) -> str:
    """Convertit l'instrument en code court (G/P/A)."""
    val = val.strip().upper()
    if val in ("G", "GUITARE", "GUITAR"):
        return "G"
    if val in ("P", "PIANO", "KEYBOARD"):
        return "P"
    return "A"


def parse_difficulte(val: str) -> int:
    """Convertit la difficulté en entier 1-3."""
    val = val.strip()
    for char in val:
        if char.isdigit():
            d = int(char)
            if 1 <= d <= 3:
                return d
    return 1


def parse_setlist(val: str) -> bool:
    """Vérifie si la colonne Setlist est cochée."""
    val = val.strip().upper()
    return val in ("TRUE", "VRAI", "OUI", "YES", "1", "X", "✓", "✔")


def parse_csv_to_songs(csv_text: str):
    """Parse le CSV et retourne (all_songs, setlist_songs)."""
    reader = csv.reader(io.StringIO(csv_text))

    # Sauter la ligne d'en-tête
    header = next(reader, None)
    if header is None:
        print("❌ Le Sheet est vide.")
        sys.exit(1)

    # Détecter dynamiquement la colonne Setlist si elle existe
    setlist_col = COL_SETLIST
    header_lower = [h.strip().lower() for h in header]
    for i, h in enumerate(header_lower):
        if "setlist" in h:
            setlist_col = i
            break

    all_songs = []
    setlist_songs = []

    for row_num, row in enumerate(reader, start=2):
        # Ignorer les lignes vides
        if not row or len(row) < COL_TRACK + 1:
            continue

        track = row[COL_TRACK].strip() if len(row) > COL_TRACK else ""
        artist = row[COL_ARTIST].strip() if len(row) > COL_ARTIST else ""

        # Ignorer si pas de titre ni d'artiste
        if not track and not artist:
            continue

        song = {
            "n": track,
            "a": artist,
            "l": parse_langue(row[COL_LANGUE] if len(row) > COL_LANGUE else ""),
            "i": parse_instrument(row[COL_INSTRUMENT] if len(row) > COL_INSTRUMENT else ""),
            "d": parse_difficulte(row[COL_DIFFICULTE] if len(row) > COL_DIFFICULTE else ""),
            "b": row[COL_BPM].strip() if len(row) > COL_BPM else "",
            "t": row[COL_TONALITE].strip() if len(row) > COL_TONALITE else "",
            "c": row[COL_CAPO].strip() if len(row) > COL_CAPO else "",
        }

        # genius_url (optionnel)
        genius_url = row[COL_GENIUS_URL].strip() if len(row) > COL_GENIUS_URL else ""
        if genius_url:
            song["gu"] = genius_url

        all_songs.append(song)

        # Vérifier la colonne Setlist
        setlist_val = row[setlist_col].strip() if len(row) > setlist_col else ""
        if parse_setlist(setlist_val):
            setlist_songs.append(song)

    return all_songs, setlist_songs


def build_setlist_html(setlist_songs: list) -> str:
    """Génère le HTML du bouton + onglet Setlist (injecté dans le JS)."""
    if not setlist_songs:
        return ""

    # Infos session
    session_label = SESSION_NAME or "Setlist du soir"
    session_meta = ""
    if SESSION_DATE or SESSION_LIEU:
        parts = [p for p in [SESSION_DATE, SESSION_LIEU] if p]
        session_meta = " — ".join(parts)

    return json.dumps({
        "label": session_label,
        "meta": session_meta,
        "songs": setlist_songs,
    }, ensure_ascii=False)


def inject_into_html(html: str, all_songs: list, setlist_songs: list) -> str:
    """Remplace le tableau const S=[...]; et injecte la setlist dans le HTML."""

    # 1. Remplacer const S=[...];
    songs_json = json.dumps(all_songs, ensure_ascii=False, separators=(",", ":"))
    pattern_s = re.compile(r"const S=\[.*?\];", re.DOTALL)
    match_s = pattern_s.search(html)
    if not match_s:
        print("❌ Impossible de trouver 'const S=[...];' dans le HTML.")
        sys.exit(1)
    html = html[:match_s.start()] + f"const S={songs_json};" + html[match_s.end():]

    # 2. Injecter/remplacer la variable SETLIST
    setlist_data = build_setlist_html(setlist_songs)
    setlist_line = f"const SETLIST={setlist_data};" if setlist_data else "const SETLIST=null;"

    # Remplacer si déjà présent, sinon insérer juste après const S=...;
    pattern_sl = re.compile(r"const SETLIST=.*?;")
    if pattern_sl.search(html):
        html = pattern_sl.sub(setlist_line, html)
    else:
        # Insérer après const S=[...];
        pattern_s2 = re.compile(r"(const S=\[.*?\];)", re.DOTALL)
        html = pattern_s2.sub(r"\1\n" + setlist_line, html)

    # 3. Injecter le bouton Setlist + onglet si pas déjà présent
    if setlist_songs and "setlist-btn" not in html:
        # Injecter le CSS pour le bouton setlist
        setlist_css = """
.setlist-btn{display:block;margin:8px 16px;padding:14px;background:var(--braise);color:#fff;border:none;border-radius:14px;font-family:'DM Serif Display',serif;font-size:16px;cursor:pointer;text-align:center;transition:transform .15s}
.setlist-btn:active{transform:scale(.97)}
.setlist-btn .sl-meta{font-family:'Cormorant Garamond',serif;font-size:12px;opacity:.8;margin-top:2px}
.setlist-overlay{display:none;position:fixed;inset:0;background:var(--bg);z-index:300;overflow-y:auto;-webkit-overflow-scrolling:touch}
.setlist-overlay.open{display:block}
.setlist-header{position:sticky;top:0;background:var(--bg);padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;z-index:301}
.setlist-back{background:none;border:none;color:var(--text);font-size:24px;cursor:pointer;padding:4px}
.setlist-title{font-family:'DM Serif Display',serif;font-size:18px;color:var(--text)}
.setlist-num{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--braise);color:#fff;font-size:13px;font-weight:700;flex-shrink:0}
"""
        html = html.replace("</style>", setlist_css + "</style>", 1)

        # Injecter le bouton setlist avant la search-wrap
        setlist_btn_html = """<div id="setlistBtnWrap"></div>"""
        html = html.replace('<div class="search-wrap">', setlist_btn_html + '\n<div class="search-wrap">', 1)

        # Injecter l'overlay setlist avant </body>
        setlist_overlay = """<div class="setlist-overlay" id="setlistOverlay">
  <div class="setlist-header">
    <button class="setlist-back" onclick="document.getElementById('setlistOverlay').classList.remove('open')">&larr;</button>
    <div class="setlist-title" id="setlistTitle">Setlist</div>
  </div>
  <ul class="list" id="setlistList"></ul>
</div>"""
        html = html.replace("</body>", setlist_overlay + "\n</body>", 1)

        # Injecter le JS de gestion setlist avant render();
        setlist_js = """
// Setlist management
if(SETLIST && SETLIST.songs && SETLIST.songs.length>0){
  var slWrap=document.getElementById('setlistBtnWrap');
  var slMeta=SETLIST.meta?'<div class="sl-meta">'+SETLIST.meta+'</div>':'';
  slWrap.innerHTML='<button class="setlist-btn" id="setlist-btn" onclick="openSetlist()">🎯 '+SETLIST.label+slMeta+'</button>';
  function openSetlist(){
    var ov=document.getElementById('setlistOverlay');
    document.getElementById('setlistTitle').textContent=SETLIST.label;
    var html=SETLIST.songs.map(function(s,i){
      return card(s,S.indexOf(S.find(function(x){return x.n===s.n&&x.a===s.a}))).replace(
        '<div class="lang','<div class="setlist-num">'+(i+1)+'</div><div class="lang'
      );
    }).join('');
    document.getElementById('setlistList').innerHTML=html;
    ov.classList.add('open');
  }
}
"""
        html = html.replace("render();", setlist_js + "\nrender();", 1)

    elif not setlist_songs and "setlist-btn" in html:
        # Pas de setlist → le bouton ne s'affichera pas car SETLIST=null
        # Le JS conditionnel gère déjà ce cas
        pass

    return html


def main():
    print("=" * 60)
    print("🎵 Sync Répertoire — La ChorAlchimie")
    print("=" * 60)

    # Vérifications
    if not SHEET_ID:
        print("❌ SHEET_ID est vide !")
        print("   Ouvre scripts/sync_repertoire.py et renseigne l'ID du Google Sheet.")
        print("   (C'est la partie de l'URL entre /d/ et /edit)")
        sys.exit(1)

    if not HTML_PATH.exists():
        print(f"❌ Fichier introuvable : {HTML_PATH}")
        sys.exit(1)

    # Télécharger le Sheet
    csv_text = fetch_sheet_csv(SHEET_ID, SHEET_TAB)
    print(f"   ✓ CSV reçu ({len(csv_text)} caractères)")

    # Parser les données
    all_songs, setlist_songs = parse_csv_to_songs(csv_text)
    print(f"\n📊 Résultats :")
    print(f"   {len(all_songs)} morceaux au total")
    print(f"   {len(setlist_songs)} morceaux dans la setlist")

    if len(all_songs) == 0:
        print("⚠️  Aucun morceau trouvé ! Vérifie le Sheet et les noms de colonnes.")
        sys.exit(1)

    # Lire le HTML existant
    html = HTML_PATH.read_text(encoding="utf-8")

    # Injecter les données
    html = inject_into_html(html, all_songs, setlist_songs)

    # Écrire le résultat
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"\n✅ {HTML_PATH.name} mis à jour !")
    print(f"   → {len(all_songs)} morceaux injectés")
    if setlist_songs:
        print(f"   → Setlist active : {SESSION_NAME or 'Setlist du soir'} ({len(setlist_songs)} titres)")
        if SESSION_DATE:
            print(f"   → Date : {SESSION_DATE}")
        if SESSION_LIEU:
            print(f"   → Lieu : {SESSION_LIEU}")
    else:
        print("   → Pas de setlist active (aucun morceau coché)")

    print(f"\n📌 Prochaine étape : git add + git push pour mettre à jour GitHub Pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
