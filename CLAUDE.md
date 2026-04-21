# La ChorAlchimie — CLAUDE.md
> Fichier de contexte permanent pour Claude Code
> Version : 1.0 · Créé le 15 avril 2026
> À placer à la racine du repo `choralchimie-web`

---

## 🎯 QUI EST PIERRICK

**Pierrick OBLIN** — Président de La ChorAlchimie Lyon + créateur chez Oblink Studio.
- Email : pierrick.oblin@hotmail.fr · Tel : 06 45 45 00 89
- Adresse : 4 allée Marcel Achard, 69100 Villeurbanne
- Il gère seul l'admin, la com et la logistique. Objectif : déléguer davantage.
- **Profil technique** : curieux, débutant en dev, apprend vite. Toujours expliquer les choix en langage clair.

---

## 🎵 LE PROJET — LA CHORALCHIMIE LYON

Association loi 1901 · RNA W691110282 · Créée le 26/10/2024
Siège social : 112 rue de Sèze, 69006 Lyon
Contact : choralchimielyon2@gmail.com
Instagram : @lachoralchimie
Linktree provisoire : linktr.ee/choralchimie (à remplacer par la page custom)

**Concept** : Chorale participative et inclusive. Inspiré de Choir! Choir! Choir! (Canada).
Tout le monde peut chanter, sans prérequis, sans audition.

**Deux formats en alternance (mercredis soirs) :**
- 🎵 **ChorAlchimie** — arrangement 2-3 voix, animé par Laëtitia (cheffe de chœur)
- 🎤 **Choraoké** — live karaoke avec musiciens, animé par Axel

**Chiffres clés :**
~250 personnes sur WhatsApp · ~30-40 réguliers · 20+ sessions depuis 2021 · 587 morceaux

**Bureau :** Pierrick OBLIN (Président) · Benoît DREYER (Secrétaire) · Véronica DIBSI (Trésorière)

---

## 🎨 CHARTE GRAPHIQUE — IMMUABLE

> Ne jamais dévier de ces choix. Validés et actés le 15/04/2026.

### Couleurs
```css
:root {
  --cream:      #F5EFE3;   /* fond principal */
  --cream2:     #EDE6D6;   /* surfaces / fond secondaire */
  --cream3:     #E3D9C6;   /* hover / fond tertiaire */
  --white:      #FDFAF5;   /* blanc chaud — cartes */
  --ink:        #2C2416;   /* texte principal — JAMAIS #000 */
  --ink2:       #4A3E2E;   /* texte secondaire */
  --muted:      #8A7B6A;   /* labels désactivés */
  --sub:        #6B5E4E;   /* texte descriptif */
  --braise:     #C25918;   /* ACTION — boutons, badges, signaux */
  --braise-bg:  rgba(194,89,24,0.08);
  --braise-bd:  rgba(194,89,24,0.22);
  --euca:       #4E7A65;   /* VALIDATION — "fait", succès */
  --euca-bg:    rgba(78,122,101,0.08);
  --euca-bd:    rgba(78,122,101,0.22);
  --gold:       #B08640;   /* SECONDAIRE — états intermédiaires */
  --gold-bg:    rgba(176,134,64,0.08);
  --border:     rgba(44,36,22,0.10);
  --border2:    rgba(44,36,22,0.06);
}
```

### Rôle des couleurs — règle stricte
- **Braise `#C25918`** → boutons d'action, badges CTA, traits décoratifs, underlines. **JAMAIS en texte courant.**
- **Eucalyptus `#4E7A65`** → éléments validés/faits, succès, confirmations.
- **Or `#B08640`** → états intermédiaires, secondaire.
- **Encre `#2C2416`** → tout le texte. Plus chaud que le noir pur.

### Typographie
```
Police UNIQUE : Outfit (Google Fonts)
Import CDN : https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap

300 → légendes très discrètes
400 → corps de texte
500 → labels, sous-titres
600 → titres de sections
700 → titres principaux, CTA
800 → grands titres hero
```
**Polices INTERDITES** : Arial, Inter, Roboto, system-ui — jamais.

### Logo
```
Horizontal : assets/ChorAlchimie_Horizontal_Fond_Foncé_New.png
Carré      : assets/ChorAlchimie_Carré_Logo_New.png
Règles : fond sombre ou transparent · ne jamais déformer · min 44px hauteur
```

### Ton éditorial
Chaleureux, direct, jamais corporate. Informel pour WhatsApp/Instagram.
Ne jamais faire "asso de quartier". Ambitieux et accessible à la fois.

---

## 📱 RÈGLES DE DÉVELOPPEMENT — NON NÉGOCIABLES

### Mobile-first absolu
**Concevoir pour iPhone SE (375px) EN PREMIER.** Desktop est secondaire.
Compatible : Safari iOS · Chrome Android · Samsung Internet · Firefox mobile · tous modèles.

**Checklist obligatoire :**
- `env(safe-area-inset-*)` pour encoches et Dynamic Island
- Préfixes `-webkit-` pour Safari iOS
- Boutons minimum **48px de hauteur** (doigt, pas souris)
- Inputs minimum **16px font-size** (évite le zoom iOS)
- Pas de `hover` comme seule interaction
- Pas de scroll horizontal
- Touch events natifs (pas de librairies souris)

### Stack technique
```
HTML5 / CSS3 / Vanilla JS (ES6+) — pas de framework
Hébergement   : GitHub Pages (auto-deploy sur push)
Data          : Google Sheets → Apps Script (Web App)
Sync          : Python 3 script local
Polices       : Google Fonts — Outfit uniquement
```

### Apps Script — pattern établi
```javascript
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName('NOM_ONGLET');
  sheet.appendRow([new Date(), data.champ1, data.champ2]);
  MailApp.sendEmail('pierrick.oblin@hotmail.fr', 'Sujet', 'Corps');
  return ContentService
    .createTextOutput(JSON.stringify({status:'ok'}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### Fetch depuis HTML (no-cors)
```javascript
fetch(APPS_SCRIPT_URL, {
  method: 'POST',
  headers: {'Content-Type': 'text/plain'},
  body: JSON.stringify(formData)
}).then(r => r.json()).then(data => { /* confirmation */ });
```

---

## 🗂️ ARCHITECTURE DE L'ÉCOSYSTÈME

```
URL : lachoralchimie.github.io
         │
   PAGE D'ACCUEIL (sas)
         │
    ┌────┴────┐
    ▼         ▼
HUB           HUB
CHANTEURS     MUSICIENS
    │              │
 6 écrans       3 écrans
```

### Structure des fichiers
```
choralchimie-web/
├── CLAUDE.md                        ← CE FICHIER
├── .claude/hooks/
├── accueil/index.html               ← Sas orientation ✓
├── hub-chanteurs/index.html         ← Hub participants ✓
├── hub-musiciens/index.html         ← Hub musiciens ✓
├── planning/index.html              ← Dates saison ✓
├── quisommesnous/index.html         ← Histoire+charte ✓
├── formulaires/
│   ├── musicien.html                ← Formulaire musicien ✓
│   └── collab.html                  ← Collaboration ✓
├── sessions/
│   ├── 29-avril.html                ← Session 29 avr ✓
│   ├── 12-mai.html                  ← Session 12 mai ✓
│   ├── 27-mai.html                  ← Session 27 mai ✓
│   ├── 10-juin.html                 ← Session 10 jun ✓
│   ├── 24-juin.html                 ← Session 24 jun ✓
│   ├── 11-juillet.html              ← Session 11 jul ✓
│   ├── 22-juillet.html              ← Session 22 jul ✓
│   ├── 19-aout.html                 ← Session 19 aoû ✓
│   ├── 02-sept.html                 ← Session 2 sep ✓
│   ├── 19-sept.html                 ← Session 19 sep ✓
│   ├── 30-sept.html                 ← Session 30 sep ✓
│   └── 14-oct.html                  ← Session 14 oct ✓
├── choraoke-app/index.html          ← LIVE ✓ GitHub Pages
├── assets/
│   ├── ChorAlchimie_Horizontal_Fond_Foncé_New.png
│   └── ChorAlchimie_Carré_Logo_New.png
├── outils/
│   ├── intake_form.html             ← FAIT ✓
│   ├── benchmark_form.html          ← FAIT ✓
│   └── adhesion.html                ← FAIT ✓
└── scripts/
    ├── sync_repertoire.py           ← À créer 🔴
    └── README.md
```

---

## 🖥️ SPEC DÉTAILLÉE — CHAQUE ÉCRAN

### 1. Page d'accueil `accueil/index.html` 🔴
**Rôle** : Sas d'orientation. Une URL. Deux chemins. Pas de scroll nécessaire.

**Contenu :**
- Logo centré en header
- Stats : 250 membres · 20+ sessions · 587 titres
- Titre hero court
- Bouton 1 (plein, fond encre) : "🎤 Je veux chanter" → hub-chanteurs
- Bouton 2 (outline) : "🎸 Je suis musicien·ne" → hub-musiciens
- Lien discret : "Qui sommes-nous ?" → quisommesnous

---

### 2. Hub Chanteurs `hub-chanteurs/index.html` 🔴
**Contenu dans l'ordre :**
1. Header + bouton retour ← Accueil
2. Bannière "Prochaine session" (fond encre) : date + titre + lieu
3. Section "Nous rejoindre" : Instagram · WhatsApp
4. Section "Ressources" :
   - App Choraoké → `choraoke-app/` (badge "Live ✓")
   - Planning → `planning/`
   - Adhérer → `outils/adhesion.html` (badge "Live ✓")
   - Qui sommes-nous → `quisommesnous/`

---

### 3. App Choraoké `choraoke-app/index.html` — LIVE ✓
**Ne pas reconstruire.** Ajouter uniquement :

**Bouton ➕ "Proposer un titre" :**
- FAB flottant bas-droite (52px, fond braise)
- Au tap : modal sheet par le bas (border-radius 24px top)
- Champs : Titre* + Artiste* + Langue (chips) + Instrument (optionnel)
- Submit → Apps Script → onglet "📥 Suggestions" du Google Sheet
- Toast de confirmation : "✓ Suggestion envoyée !"

---

### 4. Planning `planning/index.html` 🔴
**Contenu :**
- Bannière prochaine session
- Liste par mois : date (carré) + badge (ChorAlchimie en braise / Choraoké en eucalyptus) + titre + lieu

**Sessions actées :**
```
15 avr → ChorAlchimie · Parc de la Tête d'Or
29 avr → Choraoké · Berges du Rhône (Axel)
12 mai → ChorAlchimie · Parc de la Tête d'Or
27 mai → Choraoké · TBD
10 jun → ChorAlchimie · Parc de la Tête d'Or
```
Mise à jour : manuelle par Pierrick dans le HTML.

---

### 5. Adhésion `outils/adhesion.html` — FAIT ✓
Apps Script + HelloAsso + charte + droit à l'image. Ne pas reconstruire.

---

### 6. Qui sommes-nous `quisommesnous/index.html` 🟡
**Contenu :**
- Image/vidéo hero (placeholder si absent)
- Histoire : 2021 · Choir! Choir! Choir! · Adrien · Parc de la Tête d'Or
- Citation blockquote (border-left braise)
- La Charte (lisible, pas formulaire)
- Équipe : Pierrick · Laëtitia · Axel · Benoît · Véronica

---

### 7. Hub Musiciens `hub-musiciens/index.html` 🔴
**Contenu :**
- Hero : "Tu joues, on chante dessus."
- Info block : sessions, 587 titres, lieu
- Bouton 1 : "🎹 Musicien·ne solo" → formulaires/musicien.html
- Bouton 2 : "🎶 Chorale ou groupe" → formulaires/collab.html

---

### 8. Formulaire Musicien `formulaires/musicien.html` 🔴
**Champs :** Prénom+Nom* · Instrument(s) chips · Disponibilité chips · Niveau textarea · Lien audio · Email*
**Technique :** Apps Script → onglet "🎹 Musiciens" + notif email Pierrick

---

### 9. Formulaire Collaboration `formulaires/collab.html` 🟡
**Champs :** Nom structure* · Type chips · Idée de projet textarea · Contact*
**Technique :** Apps Script → onglet "🤝 Collaborations" + notif email Pierrick

---

## ⚙️ PIPELINE DE DONNÉES

### Google Sheet — onglets
```
🎵 Base de données    → 587 morceaux validés (source de vérité)
📥 Suggestions        → ajouts in-app (validation manuelle)
🎹 Musiciens          → candidatures musiciens
🤝 Collaborations     → demandes partenariat
```

### Colonnes IMMUABLES du Sheet principal
`# | Langue | Track Name | Artist Name(s) | Instrument | Difficulté vocale | BPM | Tonalité | Key (EN) | Capo (guitare) | Genres | Validée Choraoké | Spotify Link | Lien UltimateGuitar | genius_url | Notes`

`genius_url` : optionnel. Si rempli, bouton Genius pointe directement sur la page paroles (ex: `https://genius.com/4-non-blondes-whats-up-lyrics`). Si vide, fallback sur recherche Genius.

### Flux mise à jour répertoire
```
1. Modifier le Sheet (ajouter/valider lignes)
2. python scripts/sync_repertoire.py
3. Script régénère choraoke-app/index.html (liste complète + setlist si cochés)
4. git push → GitHub Pages update (~2 min)
```

### Flux mise à jour setlist (avant une session)
```
1. Ouvrir l'onglet "🎵 Base de données" dans le Sheet
2. Cocher la colonne "Setlist" sur les morceaux prévus
3. Réordonner les lignes cochées pour définir l'ordre de passage
4. Configurer SESSION_NAME / SESSION_DATE / SESSION_LIEU dans sync_repertoire.py
5. python scripts/sync_repertoire.py
6. git push → setlist visible dans l'app en ~2 min
7. Après la session : décocher tout → re-sync → bouton Setlist disparaît
```

---

## 🔗 URLS — À REMPLIR AU FUR ET À MESURE

```
GitHub repo principal     : [à remplir]
App Choraoké live         : [à remplir]
Netlify (ancien)          : https://creative-lolly-8e5933.netlify.app/
Linktree provisoire       : https://linktr.ee/choralchimie
Instagram                 : https://www.instagram.com/lachoralchimie/
WhatsApp communauté       : https://chat.whatsapp.com/DWzssCj3cDS9Gng6vbXJpm
HelloAsso                 : [à remplir]
Apps Script adhésion      : [à remplir]
Apps Script suggestions   : [à déployer] (code dans scripts/apps_script_propositions.js)
Apps Script musiciens     : [à déployer] (code dans scripts/apps_script_musiciens.js)
Apps Script collabs       : [à déployer] (code dans scripts/apps_script_propositions.js)
Apps Script sessions      : [à déployer] (code dans scripts/apps_script_sessions_universal.js)
APPS_SCRIPT_SESSIONS_URL  : [à remplir après déploiement]
Google Sheet master       : [à remplir]
```

---

## ❌ JAMAIS FAIRE

1. Éditer un PDF exporté → toujours repartir du HTML source
2. Renommer les colonnes du Google Sheet → casse le script sync
3. Utiliser `localStorage` / `sessionStorage` dans les artifacts Claude
4. Casser la compatibilité mobile (tester avant de commiter)
5. Utiliser Inter, Roboto, Arial → Outfit uniquement
6. Orange `#C25918` en texte courant → signaux/actions seulement
7. Boutons de moins de 48px de hauteur
8. Noir pur `#000` pour le texte → toujours `#2C2416`
9. Framework JS (React, Vue...) → Vanilla uniquement
10. Design "asso de quartier" → chaleureux mais ambitieux

---

## 📋 ÉTAT D'AVANCEMENT — PRIORITÉS

### ✅ Fait et live
- App Choraoké (587 titres, Spotify deep link, Deezer, UG, GitHub Pages)
- Formulaire adhésion (Apps Script + HelloAsso)
- Formulaire Intake créatif (outil interne)
- Formulaire Benchmark esthétique (outil interne)
- Charte graphique validée
- Maquette navigable `maquette_choralchimie.html`
- Documents officiels (PV AGO, statuts, bureau)

### 🔴 Priorité 1 — Commencer par là
1. `scripts/sync_repertoire.py` (pipeline Sheet → HTML + setlist)
2. Bouton ➕ "Proposer un titre" dans `choraoke-app/index.html`
3. Bouton "🎯 Setlist du soir" dans `choraoke-app/index.html`
4. `accueil/index.html`
5. `hub-chanteurs/index.html`
6. `hub-musiciens/index.html`
7. `planning/index.html`
8. `formulaires/musicien.html`

### 🟡 Priorité 2 — Suite
- `quisommesnous/index.html` ✓
- `formulaires/collab.html` ✓

### 🔮 Futur
- Site complet multi-pages
- Capture email membres
- Galerie vidéos sessions
- GitHub Actions pour auto-sync
- La Nuit des Flux (page événement)

---

## 🚀 COMMENT DÉMARRER UNE SESSION CLAUDE CODE

1. Claude lit ce CLAUDE.md en priorité absolue
2. Identifier la prochaine tâche priorité 1 non faite
3. Construire · Tester sur mobile · Commiter
4. Mettre à jour le log ci-dessous à chaque décision importante

---

## 📝 LOG DES DÉCISIONS

- [15/04/2026] — Charte actée : Outfit + crème #F5EFE3 + braise #C25918 + eucalyptus #4E7A65
- [15/04/2026] — Architecture validée : 1 accueil + 2 hubs + modules existants
- [15/04/2026] — Pipeline : script Python manuel (→ GitHub Actions à terme)
- [15/04/2026] — Bouton suggestion in-app : Apps Script → onglet Suggestions du Sheet
- [15/04/2026] — Décision : tout en HTML custom GitHub Pages, pas de Linktree payant
- [15/04/2026] — Décision : Vanilla JS uniquement, pas de framework
- [15/04/2026] — App Choraoké : live sur GitHub (choraoke-app repo) + Netlify (temporaire)
- [15/04/2026] — Maquette navigable créée comme référence visuelle
- [21/04/2026] — Bouton Genius ajouté comme action principale (paroles) — Spotify/Deezer en secondaire
- [21/04/2026] — Logique validée : musiciens live = mélodie guidée. Genius = paroles session. Spotify/Deezer = écoute perso avant/après
- [21/04/2026] — Layout boutons app : Genius (pleine largeur, vert eucalyptus) / Spotify + Deezer (secondaires côte à côte) / Pour jouer (pleine largeur)
- [21/04/2026] — Vote communautaire planifié en Niveau 2 (après reprise). Niveau 1 = suggestion simple déjà prévu
- [21/04/2026] — Feature Setlist validée : colonne "Setlist" dans le Sheet (checkbox) → onglet auto "🎯 Setlist" → bouton dans l'app
- [21/04/2026] — Accès setlist : bouton dédié sur l'écran principal de l'app (au-dessus de la recherche)
- [21/04/2026] — Setlist disparaît de l'app si aucun morceau coché → pas de bouton fantôme
- [21/04/2026] — Mode jour/nuit ajouté : bouton 🌙/🌑 flottant en bas à droite. Préférence sauvegardée en localStorage
- [21/04/2026] — Colonne optionnelle `genius_url` ajoutée au Sheet. Si remplie → lien direct paroles (1 clic). Si vide → fallback recherche Genius
- [21/04/2026] — Sur GitHub Pages : popup Claude.ai disparaît → 2 clics pour les paroles (vs 5 en test Claude.ai)
- [21/04/2026] — Pages sessions × 12 créées · quisommesnous · collab · Apps Script universel sessions
- [21/04/2026] — WhatsApp communauté URL ajoutée partout : https://chat.whatsapp.com/DWzssCj3cDS9Gng6vbXJpm
- [21/04/2026] — Planning : chaque session = lien cliquable vers sa page dédiée

---

*Document vivant — compléter sans jamais supprimer de sections*
*Dernière mise à jour : 15 avril 2026*
