# BRIEF WEB — La ChorAlchimie
> À coller dans le projet Claude pour reprendre le travail en contexte

## Stack technique
- HTML5 / CSS3 / Vanilla JS — zéro framework
- GitHub Pages (auto-deploy sur push main)
- Repo : https://github.com/FlowyFirefox/choralchimie-web
- Live : https://flowyfirefox.github.io/choralchimie-web/
- Dossier local : C:\Users\pierr\OneDrive\00_Choralchimie\ChorAlchimie_Web\

## Charte graphique IMMUABLE
- Police : Outfit (Google Fonts, 300-800)
- Fond : #F5EFE3 crème · Texte : #2C2416 encre
- Braise #C25918 = actions uniquement (jamais texte courant)
- Eucalyptus #4E7A65 = validation
- Boutons min 48px · inputs min 16px · mobile-first 375px

## Google Sheets
- Sheet Répertoire : 1tkQ1J7bzU_4reaTiF4LMvWeRwE0auRheOWofjVnJyFw (600 morceaux, onglet "Base de données")
- Sheet Codex Bureau : 1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g (onglets : Membres / Musiciens / Sessions / Collaborations)

## Apps Script déployés
- Sessions universel : https://script.google.com/macros/s/AKfycbynLReyKmoWz3pwBnsi6aDgfbYYAxdy0NRRP-MU4g2hIj4Hqns1o00e5o0FK8mO_NjKWQ/exec
- Musiciens : https://script.google.com/macros/s/AKfycbx6n0_63O59hXKfpZeQgo894wVnYTy2xbrFOtaLJw_MGacAnkErgpo-Mfm9f-IRyBfzHQ/exec
- Propositions chansons : https://script.google.com/macros/s/AKfycbw777HCJidq_qLbPdrHqfYFTVf6ufxCSKNz1-gBS0z-thYu4g06A07LJ5GGExbVAZD5/exec
- Membres adhésion : https://script.google.com/macros/s/AKfycbyq_gHLOMjW2PzCEkKMBFyA8f5OMEyoD50EgGaq6iBLg8G2PHe2UIpNMk9CA2OD0MC0RQ/exec
- Collaborations : https://script.google.com/macros/s/AKfycby83ISI713NNCeiItXX9H3XRnXHJhmkJxyPQ03nhh92MDur1FJYSc9w_5SA-hxJpoYvLQ/exec

## Pages live
- accueil/index.html — sas orientation
- hub-chanteurs/index.html — hub participants
- hub-musiciens/index.html — hub musiciens
- planning/index.html — 12 sessions 2026
- sessions/29-avril.html → sessions/14-oct.html — 12 pages sessions
- quisommesnous/index.html — histoire + équipe
- formulaires/musicien.html — candidature musicien
- formulaires/collab.html — collaboration
- outils/adhesion.html — formulaire adhésion (10€/an)
- choraoke-app/index.html — app 600 morceaux LIVE

## Pipeline répertoire
- Script : scripts/sync_repertoire.py
- Commande : PYTHONIOENCODING=utf-8 py -3 scripts/sync_repertoire.py
- Lit l'onglet "Base de données" du Sheet Répertoire (attention : sans emoji, renommé le 27/04/2026)
- Génère choraoke-app/index.html

## Règles fetch vers Apps Script
TOUJOURS utiliser :
- method: 'POST'
- headers: { 'Content-Type': 'text/plain;charset=utf-8' }
- redirect: 'follow'
- .then(r => r.text()) — jamais .json()

## Tracking
- PostHog installé sur toutes les pages
- API key : phc_pMHwRzFBmQ5ofa5jibDA8rqMJXHooKk87SDE5RvNuzG5
- Dashboard : https://eu.posthog.com

## WhatsApp communauté
https://chat.whatsapp.com/DWzssCj3cDS9Gng6vbXJpm

## Décisions importantes
- Fetch Apps Script : text/plain;charset=utf-8 + redirect:follow + .then(r=>r.text())
- Tester UNIQUEMENT sur GitHub Pages (pas en file://)
- Ctrl+Shift+R pour vider le cache après push
- Le CLAUDE.md du repo est la source de vérité pour Claude Code
- Laetitia (sans tréma) partout dans le site
- Cotisation : 10€/an (PV bureau du 22/04/2026)
- IBAN : FR76 1027 8073 1200 0219 3550 138 · BIC : CMCIFR2A
- Onglet Sheet Répertoire : "Base de données" (sans emoji — renommé 27/04/2026)
