#!/usr/bin/env python3
"""
fetch_lyrics.py — Récupère les paroles depuis l'API Genius pour chaque
chanson du Google Sheet "Base de données" et les écrit dans la colonne P
"Paroles".

Idempotent : SKIP_IF_FILLED=True permet de relancer le script autant de
fois que nécessaire sans réécrire les paroles déjà présentes.

Pré-requis :
    pip install gspread lyricsgenius
    scripts/credentials.json  (Service Account Google, gitignoré)
    scripts/.env              (contient GENIUS_TOKEN=..., gitignoré)

    Le Sheet doit être partagé en lecture+écriture avec l'email du
    Service Account.

Usage :
    python scripts/fetch_lyrics.py
"""

import os
import re
import sys
import time
from pathlib import Path

import gspread
import lyricsgenius


def _load_env():
    """Charge scripts/.env (si présent) dans os.environ."""
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(
            key.strip(),
            val.strip().strip('"').strip("'"),
        )


_load_env()


# ============================================================================
# CONFIGURATION
# ============================================================================
GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN", "")
SHEET_ID = "1tkQ1J7bzU_4reaTiF4LMvWeRwE0auRheOWofjVnJyFw"
SHEET_TAB = "🎵 Base de données"
CREDENTIALS_FILE = "scripts/credentials.json"
LYRICS_COL = "P"
SKIP_IF_FILLED = True

# Tuning
BATCH_SIZE = 10               # nb d'appels API Genius entre 2 pauses
PAUSE_BETWEEN_BATCHES = 3.0   # secondes
GENIUS_TIMEOUT = 8            # secondes par requête
RATE_LIMIT_BACKOFF = 10.0     # secondes après un 429
MAX_CELL_LEN = 49000          # garde sous la limite 50k de Google Sheets

# ============================================================================
# Internes
# ============================================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
NOT_FOUND_LOG = REPO_ROOT / "scripts" / "lyrics_not_found.txt"

# Colonnes (1-based pour gspread)
COL_TITLE_IDX = 3   # C — Track Name
COL_ARTIST_IDX = 4  # D — Artist Name(s)

CLEAN_RE = re.compile(
    r"\s*[-–]\s*(\d{4}\s+)?(remaster(ed)?|live|remix|version|acoustic|"
    r"radio edit|feat\.?|ft\.?).*",
    re.IGNORECASE,
)
# Suffixe d'artefacts ajouté par Genius/lyricsgenius en fin de paroles
EMBED_TAIL_RE = re.compile(r"\d*Embed\s*$", re.IGNORECASE)


def col_letter_to_idx(letter: str) -> int:
    """A=1, B=2, ..., Z=26, AA=27, ..."""
    n = 0
    for c in letter.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


def clean_title(title: str) -> str:
    return CLEAN_RE.sub("", title).strip()


def clean_lyrics(raw: str) -> str:
    """Léger nettoyage des artefacts ajoutés par lyricsgenius."""
    if not raw:
        return ""
    text = EMBED_TAIL_RE.sub("", raw).strip()
    if len(text) > MAX_CELL_LEN:
        text = text[:MAX_CELL_LEN] + "\n[…troncage]"
    return text


def safe_search(genius, title: str, artist: str):
    """
    Cherche une chanson sur Genius avec gestion 429 + retry une fois.
    Retourne (song_or_none, error_message_or_none).
    """
    for attempt in range(2):
        try:
            song = genius.search_song(title, artist)
            return song, None
        except Exception as e:
            msg = str(e).lower()
            if ("429" in msg or "rate limit" in msg or "too many" in msg):
                if attempt == 0:
                    print(f"   [429 rate limit — pause {RATE_LIMIT_BACKOFF}s…]")
                    time.sleep(RATE_LIMIT_BACKOFF)
                    continue
            return None, str(e)[:200]
    return None, "max retries reached"


def main():
    print("=" * 60)
    print("🎤 Fetch Lyrics — La ChorAlchimie")
    print("=" * 60)

    if not GENIUS_TOKEN:
        print("❌ GENIUS_TOKEN manquant.")
        print("   Copie scripts/.env.example vers scripts/.env et renseigne :")
        print("   GENIUS_TOKEN=ton_token_genius")
        sys.exit(1)

    cred_path = REPO_ROOT / CREDENTIALS_FILE
    if not cred_path.exists():
        print(f"❌ Fichier credentials introuvable : {cred_path}")
        print("   Place le JSON Service Account dans scripts/credentials.json")
        sys.exit(1)

    print("🔐 Auth Service Account…")
    gc = gspread.service_account(filename=str(cred_path))

    print("📊 Ouverture du Sheet…")
    try:
        sh = gc.open_by_key(SHEET_ID)
    except Exception as e:
        print(f"❌ Impossible d'ouvrir le Sheet : {e}")
        sys.exit(1)

    try:
        ws = sh.worksheet(SHEET_TAB)
    except gspread.WorksheetNotFound:
        print(f"❌ Onglet introuvable : {SHEET_TAB!r}")
        print(f"   Onglets disponibles : {[w.title for w in sh.worksheets()]}")
        sys.exit(1)

    print("📥 Lecture des données…")
    rows = ws.get_all_values()
    if not rows:
        print("⚠️  Sheet vide.")
        sys.exit(1)

    header = rows[0]
    lyrics_col_idx = col_letter_to_idx(LYRICS_COL)

    # Header "Paroles" si la colonne n'a pas d'en-tête
    if (
        len(header) < lyrics_col_idx
        or not header[lyrics_col_idx - 1].strip()
    ):
        print(f"📝 Écriture du header 'Paroles' en {LYRICS_COL}1")
        ws.update_acell(f"{LYRICS_COL}1", "Paroles")

    print("🎵 Init lyricsgenius…")
    genius = lyricsgenius.Genius(
        GENIUS_TOKEN,
        timeout=GENIUS_TIMEOUT,
        retries=0,
        skip_non_songs=True,
        remove_section_headers=True,
    )

    n_total = len(rows) - 1  # exclude header
    print(f"   {n_total} lignes à traiter\n")

    found = 0
    not_found = 0
    skipped = 0
    errors = 0
    not_found_entries = []
    pending_writes = []
    api_calls = 0

    def flush_writes():
        if not pending_writes:
            return
        try:
            ws.batch_update([
                {"range": w["range"], "values": w["values"]}
                for w in pending_writes
            ])
        except Exception as e:
            print(f"   ⚠️  Erreur batch_update : {e}")
        pending_writes.clear()

    for i, row in enumerate(rows[1:], start=2):  # row 2 = first data row
        idx_disp = i - 1  # 1-based song count for display

        title = row[COL_TITLE_IDX - 1].strip() if len(row) >= COL_TITLE_IDX else ""
        artist = row[COL_ARTIST_IDX - 1].strip() if len(row) >= COL_ARTIST_IDX else ""
        existing = (
            row[lyrics_col_idx - 1].strip()
            if len(row) >= lyrics_col_idx else ""
        )

        if not title and not artist:
            continue  # ligne vide

        prefix = f"[{idx_disp:>3}/{n_total}]"
        label = f"{artist} — {title}"

        if SKIP_IF_FILLED and existing:
            print(f"{prefix} ⏭️  SKIP (déjà rempli) : {label}")
            skipped += 1
            continue

        ct = clean_title(title)
        song, err = safe_search(genius, ct, artist)
        api_calls += 1

        if err:
            print(f"{prefix} ⚠️  ERREUR : {label} ({err})")
            errors += 1
        elif song is None or not getattr(song, "lyrics", None):
            print(f"{prefix} ❌ NOT FOUND : {label}")
            not_found += 1
            not_found_entries.append(f"{artist} — {title}")
        else:
            lyrics = clean_lyrics(song.lyrics)
            pending_writes.append({
                "range": f"{LYRICS_COL}{i}",
                "values": [[lyrics]],
            })
            print(f"{prefix} ✅ {label}")
            found += 1

        # Toutes les BATCH_SIZE requêtes Genius : flush + pause anti rate-limit
        if api_calls and api_calls % BATCH_SIZE == 0:
            flush_writes()
            time.sleep(PAUSE_BETWEEN_BATCHES)

    # Flush du dernier batch
    flush_writes()

    # Log not-found
    if not_found_entries:
        NOT_FOUND_LOG.parent.mkdir(parents=True, exist_ok=True)
        NOT_FOUND_LOG.write_text(
            "\n".join(not_found_entries) + "\n",
            encoding="utf-8",
        )

    # Résumé
    print()
    print("=" * 60)
    print(f"✅ {found} paroles trouvées")
    if not_found:
        print(
            f"❌ {not_found} non trouvées"
            f" (voir {NOT_FOUND_LOG.relative_to(REPO_ROOT)})"
        )
    else:
        print(f"❌ {not_found} non trouvées")
    print(f"⏭️  {skipped} skippées (déjà remplies)")
    if errors:
        print(f"⚠️  {errors} erreurs")
    print("=" * 60)


if __name__ == "__main__":
    main()
