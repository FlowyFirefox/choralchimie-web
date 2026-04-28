#!/usr/bin/env python3
"""
sync_repertoire.py — Pipeline Google Sheet -> choraoke-app/index.html

Lit le Google Sheet "Base de données" via export CSV public,
régénère le tableau JSON des morceaux dans l'app Choraoké,
et injecte la setlist du soir si la colonne Tracklist est remplie.

Structure du Sheet (colonnes A->P, 0-indexées 0..15) :
  A=0  #
  B=1  Langue
  C=2  Track Name
  D=3  Artist Name(s)
  E=4  Instrument
  F=5  Difficulté vocale
  G=6  BPM
  H=7  Tonalité
  I=8  Key (EN)
  J=9  Capo (guitare)
  K=10 Genres
  L=11 Validée Choraoké
  M=12 Spotify Link
  N=13 Lien UltimateGuitar
  O=14 Tracklist_XX_XX  -> numéro 1..N pour la setlist du soir,
                           "Backup" pour les backups, vide sinon.
  P=15 Paroles          -> texte des paroles (peut contenir des balises
                           [Verse]/[Chorus]). Renseigné par fetch_lyrics.py.

Auto-détectées (par nom d'en-tête, optionnelles) :
  - genius_url   (header contenant "genius" et "url")
  - tracklist    (header contenant "tracklist" — sinon fallback "setlist")

Usage :
    python scripts/sync_repertoire.py

Pré-requis :
    - Le Google Sheet doit être partagé en lecture publique (ou via lien)
    - SHEET_ID renseigné ci-dessous
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
# CONFIGURATION
# ============================================================================

SHEET_ID = "1tkQ1J7bzU_4reaTiF4LMvWeRwE0auRheOWofjVnJyFw"
SHEET_TAB = "Base de données"

# Métadonnées affichées dans l'overlay setlist (toutes optionnelles)
SESSION_NAME = ""     # Vide -> label par défaut "Ce soir 🎵"
SESSION_DATE = ""     # Ex: "29 avril 2026"
SESSION_LIEU = ""     # Ex: "Berges du Rhône"

REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = REPO_ROOT / "choraoke-app" / "index.html"

# ============================================================================
# COLONNES (0-indexées) — A->O
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
COL_TRACKLIST = 14   # O — numéro d'ordre, "Backup", ou vide
COL_LYRICS = 15      # P — paroles (rempli par fetch_lyrics.py)


def fetch_sheet_csv(sheet_id: str, tab_name: str) -> str:
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
    val = val.strip().upper()
    if val in ("E", "EN", "ENGLISH", "ANGLAIS"):
        return "E"
    if val in ("F", "FR", "FRENCH", "FRANÇAIS", "FRANCAIS"):
        return "F"
    if val in ("I", "IT", "ES", "IT/ES", "ITALIEN", "ESPAGNOL", "ITALIAN", "SPANISH"):
        return "I"
    return val[0] if val else "E"


def parse_instrument(val: str) -> str:
    val = val.strip().upper()
    if val in ("G", "GUITARE", "GUITAR"):
        return "G"
    if val in ("P", "PIANO", "KEYBOARD"):
        return "P"
    return "A"


def parse_difficulte(val: str) -> int:
    val = val.strip()
    for char in val:
        if char.isdigit():
            d = int(char)
            if 1 <= d <= 3:
                return d
    return 1


def parse_tracklist(val: str):
    """
    Lit la colonne Tracklist du soir.
    Retourne :
      ("order", int)   si entier valide -> position dans la setlist principale
      ("backup", None) si "Backup"
      (None, None)     si vide / non reconnu
    """
    val = val.strip()
    if not val:
        return None, None
    if val.lower() == "backup":
        return "backup", None
    try:
        return "order", int(val)
    except ValueError:
        return None, None


def detect_columns(header):
    """Auto-détecte tracklist_col et genius_col par nom d'en-tête."""
    tracklist_col = COL_TRACKLIST
    genius_col = -1
    header_lower = [h.strip().lower() for h in header]

    # Tracklist : priorité au header contenant "tracklist", sinon "setlist"
    found_tracklist = False
    for i, h in enumerate(header_lower):
        if "tracklist" in h:
            tracklist_col = i
            found_tracklist = True
            break
    if not found_tracklist:
        for i, h in enumerate(header_lower):
            if "setlist" in h:
                tracklist_col = i
                break

    for i, h in enumerate(header_lower):
        if "genius" in h and "url" in h:
            genius_col = i
            break

    return tracklist_col, genius_col


def parse_csv_to_songs(csv_text: str):
    """Parse le CSV et retourne (all_songs, setlist_songs, backup_songs)."""
    reader = csv.reader(io.StringIO(csv_text))

    header = next(reader, None)
    if header is None:
        print("❌ Le Sheet est vide.")
        sys.exit(1)

    tracklist_col, genius_col = detect_columns(header)

    all_songs = []
    setlist_indexed = []   # liste de tuples (order:int, song)
    backup_songs = []

    for row in reader:
        if not row or len(row) < COL_TRACK + 1:
            continue

        track = row[COL_TRACK].strip() if len(row) > COL_TRACK else ""
        artist = row[COL_ARTIST].strip() if len(row) > COL_ARTIST else ""
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

        if genius_col >= 0 and len(row) > genius_col:
            gu = row[genius_col].strip()
            if gu:
                song["gu"] = gu

        if len(row) > COL_LYRICS:
            ly = row[COL_LYRICS].strip()
            if ly:
                song["ly"] = ly

        all_songs.append(song)

        if len(row) > tracklist_col:
            kind, order = parse_tracklist(row[tracklist_col])
            if kind == "order":
                setlist_indexed.append((order, song))
            elif kind == "backup":
                backup_songs.append(song)

    setlist_indexed.sort(key=lambda x: x[0])
    setlist_songs = [s for _, s in setlist_indexed]

    return all_songs, setlist_songs, backup_songs


def build_setlist_data(setlist_songs, backup_songs):
    """Retourne le dict SETLIST à injecter dans l'app, ou None si rien à afficher."""
    if not setlist_songs and not backup_songs:
        return None
    label = SESSION_NAME or "Ce soir 🎵"
    parts = [p for p in [SESSION_DATE, SESSION_LIEU] if p]
    return {
        "label": label,
        "meta": " — ".join(parts),
        "songs": setlist_songs,
        "backup": backup_songs,
    }


# CSS / HTML / JS injectés une seule fois si l'UI setlist n'est pas déjà dans le HTML.
SETLIST_CSS = """
.setlist-btn{display:block;width:calc(100% - 32px);margin:8px 16px 12px;padding:14px;background:var(--braise);color:#fff;border:none;border-radius:14px;font-family:'DM Serif Display',serif;font-size:16px;cursor:pointer;text-align:center;transition:transform .15s;box-shadow:0 4px 16px rgba(194,89,24,.35)}
.setlist-btn:active{transform:scale(.97)}
.setlist-btn .sl-meta{font-family:'Cormorant Garamond',serif;font-size:12px;opacity:.85;margin-top:2px}
.setlist-overlay{display:none;position:fixed;inset:0;background:var(--bg);z-index:300;overflow-y:auto;-webkit-overflow-scrolling:touch}
.setlist-overlay.open{display:block}
.setlist-header{position:sticky;top:0;background:var(--bg);padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;z-index:301}
.setlist-back{background:none;border:none;color:var(--text);font-size:24px;cursor:pointer;padding:4px;min-width:36px;min-height:36px}
.setlist-title{font-family:'DM Serif Display',serif;font-size:18px;color:var(--text)}
.setlist-num{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--braise);color:#fff;font-size:13px;font-weight:700;flex-shrink:0;margin-right:8px}
.setlist-divider{list-style:none;padding:18px 16px 8px;font-family:'DM Serif Display',serif;font-size:13px;color:var(--sub);text-transform:uppercase;letter-spacing:.12em;border-top:1px solid var(--border);margin-top:8px}
"""

SETLIST_OVERLAY_HTML = """<div class="setlist-overlay" id="setlistOverlay">
  <div class="setlist-header">
    <button class="setlist-back" onclick="document.getElementById('setlistOverlay').classList.remove('open')">&larr;</button>
    <div class="setlist-title" id="setlistTitle">Setlist</div>
  </div>
  <ul class="list" id="setlistList"></ul>
</div>"""

SETLIST_JS = """// Setlist du soir
function openSetlist(){
  var ov=document.getElementById('setlistOverlay');
  document.getElementById('setlistTitle').textContent=SETLIST.label;
  function findIdx(s){return S.indexOf(S.find(function(x){return x.n===s.n&&x.a===s.a;}));}
  var mainHtml=(SETLIST.songs||[]).map(function(s,i){
    return card(s,findIdx(s)).replace('<div class="lang','<div class="setlist-num">'+(i+1)+'</div><div class="lang');
  }).join('');
  var bkHtml=(SETLIST.backup||[]).map(function(s){return card(s,findIdx(s));}).join('');
  var html=mainHtml;
  if(bkHtml) html+='<li class="setlist-divider">Backups</li>'+bkHtml;
  document.getElementById('setlistList').innerHTML=html;
  ov.classList.add('open');
}
if(SETLIST && ((SETLIST.songs && SETLIST.songs.length>0) || (SETLIST.backup && SETLIST.backup.length>0))){
  var slWrap=document.getElementById('setlistBtnWrap');
  if(slWrap){
    var slMeta=SETLIST.meta?'<div class="sl-meta">'+SETLIST.meta+'</div>':'';
    slWrap.innerHTML='<button class="setlist-btn" id="setlist-btn" onclick="openSetlist()">'+SETLIST.label+slMeta+'</button>';
  }
}
"""


def inject_into_html(html: str, all_songs, setlist_songs, backup_songs) -> str:
    """Remplace const S=[...] et const SETLIST=...; injecte l'UI si absente."""

    # 1. Remplacer const S=[...];
    # Ancrage `(?=\n|$)` : la ligne se termine par `;` suivi d'un newline.
    # Indispensable pour ne pas matcher un `;` situé dans une string JSON
    # (ex : artiste "Michel Fugain;Le Big Bazar").
    songs_json = json.dumps(all_songs, ensure_ascii=False, separators=(",", ":"))
    pattern_s = re.compile(r"const S=\[.*?\];(?=\n|$)", re.DOTALL)
    if not pattern_s.search(html):
        print("❌ Impossible de trouver 'const S=[...];' dans le HTML.")
        sys.exit(1)
    # lambda pour empêcher re.sub de réinterpréter les backslashes du JSON
    # (sinon les "\n" / "\t" / "\\" dans les paroles cassent le JSON injecté)
    html = pattern_s.sub(lambda _m: f"const S={songs_json};", html, count=1)

    # 2. Remplacer const SETLIST=...;
    setlist_data = build_setlist_data(setlist_songs, backup_songs)
    setlist_value = (
        json.dumps(setlist_data, ensure_ascii=False, separators=(",", ":"))
        if setlist_data is not None else "null"
    )
    setlist_line = f"const SETLIST={setlist_value};"
    pattern_sl = re.compile(r"const SETLIST=.*?;(?=\n|$)", re.DOTALL)
    if pattern_sl.search(html):
        html = pattern_sl.sub(lambda _m: setlist_line, html, count=1)
    else:
        # Insérer juste après const S=[...];  (lambda → backslashes JSON préservés)
        html = re.sub(
            r"const S=\[.*?\];(?=\n|$)",
            lambda m: m.group(0) + "\n" + setlist_line,
            html, count=1, flags=re.DOTALL,
        )

    # 3. Injecter l'UI setlist si absente (idempotent)
    if "setlistBtnWrap" not in html:
        html = html.replace("</style>", SETLIST_CSS + "</style>", 1)
        html = html.replace(
            '<div class="search-wrap">',
            '<div id="setlistBtnWrap"></div>\n  <div class="search-wrap">',
            1,
        )
        html = html.replace("</body>", SETLIST_OVERLAY_HTML + "\n</body>", 1)
        html = html.replace("render();", SETLIST_JS + "\nrender();", 1)

    return html


def main():
    print("=" * 60)
    print("🎵 Sync Répertoire — La ChorAlchimie")
    print("=" * 60)

    if not SHEET_ID:
        print("❌ SHEET_ID est vide ! Ouvre le script et renseigne l'ID.")
        sys.exit(1)
    if not HTML_PATH.exists():
        print(f"❌ Fichier introuvable : {HTML_PATH}")
        sys.exit(1)

    csv_text = fetch_sheet_csv(SHEET_ID, SHEET_TAB)
    print(f"   ✓ CSV reçu ({len(csv_text)} caractères)")

    all_songs, setlist_songs, backup_songs = parse_csv_to_songs(csv_text)
    print(f"\n📊 Résultats :")
    print(f"   {len(all_songs)} morceaux au total")
    print(f"   {len(setlist_songs)} morceaux dans la setlist (numérotés)")
    print(f"   {len(backup_songs)} morceaux backup")

    if len(all_songs) == 0:
        print("⚠️  Aucun morceau trouvé. Vérifie le Sheet et les colonnes.")
        sys.exit(1)

    html = HTML_PATH.read_text(encoding="utf-8")
    html = inject_into_html(html, all_songs, setlist_songs, backup_songs)
    HTML_PATH.write_text(html, encoding="utf-8")

    print(f"\n✅ {HTML_PATH.name} mis à jour")
    print(f"   → {len(all_songs)} morceaux injectés")
    if setlist_songs or backup_songs:
        label = SESSION_NAME or "Ce soir 🎵"
        print(f"   → Setlist active : {label} ({len(setlist_songs)} principaux + {len(backup_songs)} backups)")
        if SESSION_DATE:
            print(f"   → Date : {SESSION_DATE}")
        if SESSION_LIEU:
            print(f"   → Lieu : {SESSION_LIEU}")
    else:
        print("   → Pas de setlist active (colonne Tracklist vide partout)")

    print(f"\n📌 Prochaine étape : git add + commit + push")
    print("=" * 60)


if __name__ == "__main__":
    main()
