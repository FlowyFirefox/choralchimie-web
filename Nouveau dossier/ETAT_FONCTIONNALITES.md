# ÉTAT FONCTIONNALITÉS — La ChorAlchimie
> Mis à jour : 27 avril 2026

## ✅ LIVE ET FONCTIONNEL
- App Choraoké — 600 morceaux, suggestions connectées, mode jour/nuit
- Formulaire adhésion — 2 sections (rejoindre / soutenir), charte complète, 10€/an
- Formulaire musicien — connecté Codex Bureau onglet Musiciens
- Formulaire collab — connecté Codex Bureau onglet Collaborations
- Inscriptions sessions — Apps Script universel, onglet par session
- Planning 12 sessions — toutes cliquables vers leur page dédiée
- Qui sommes-nous — photo groupe, histoire, équipe en ligne, CTAs
- Hub chanteurs — hiérarchie 3 niveaux, card Adhérer gradient, photo
- Hub musiciens — photo kiosque Gandhi, formulaire musicien
- PostHog analytics — installé sur toutes les pages
- Onglet Membres Gsheet — connecté, colonnes alignées

## 🔴 À FAIRE — URGENT
- HelloAsso — créer page cotisation 10€, remplacer LIEN_HELLOASSO dans adhesion.html
- Setlist / tracklist — fonctionnalité à construire (voir ci-dessous)
- Noms artistes dans app Choraoké — bug à investiguer
- Favicon — erreur 404 console sur toutes les pages

## 🟡 À FAIRE — MOYEN TERME
- Mode jour/nuit — propager sur toutes les pages via assets/theme.js
- Linktree — supprimer / rediriger vers le site
- QR code — générer nouveau pointant vers accueil du site
- Carte de fidélité — DA à finaliser

## 🟢 STRATÉGIE / FOND
- Instagram — 3 posts épinglés (teaser, face caméra, photo groupe)
- Dossiers subventions — DRAC, FDVA, Ville de Lyon
- Baragones — partenariat salle intérieure octobre 2026

## 🎯 FONCTIONNALITÉ SETLIST — À CONSTRUIRE
### Objectif
Permettre de créer une tracklist pour chaque session Choraoké
et la faire apparaître dans l'app mobile en mode "Ce soir 🎵"

### Process validé
1. Axel balaye la master database et renseigne ce qu'il sait jouer (colonne Axel_OK)
2. Pierrick + Axel sélectionnent les morceaux → numéro dans colonne "Setlist"
3. Lancer sync_repertoire.py → app mise à jour automatiquement
4. L'app affiche un bouton "Ce soir 🎵" qui filtre sur les morceaux setlist

### Ce qui reste à faire techniquement
1. Ajouter colonne "Setlist" dans Sheet Répertoire (onglet "Base de données")
2. Modifier sync_repertoire.py pour lire cette colonne et générer la vue setlist
3. Modifier choraoke-app/index.html pour afficher le bouton "Ce soir 🎵"
   et filtrer les morceaux dont Setlist != vide
4. Tester le pipeline complet

### Commande de lancement sync
PYTHONIOENCODING=utf-8 py -3 scripts/sync_repertoire.py

## FICHIERS ASSETS DISPONIBLES
- assets/PhotoGroup1.jpg — photo groupe intérieur violet
- assets/PhotoGroup2.jpg — photo groupe nuit piano
- assets/PhotoGroup3.jpg — photo groupe parc tête d'or (utilisée quisommesnous)
- assets/PhotoMusiciens.JPEG — piano kiosque Gandhi (utilisée hub-musiciens)
- assets/Pierrick.png — photo équipe
- assets/Laetitia.png — photo équipe (pas encore utilisée dans quisommesnous)
- assets/Benoît.png — photo équipe
- assets/Veronica.png — photo équipe
- assets/ChorAlchimie_Horizontal_Fond_Foncé_New.png — logo header actuel
- assets/ChorAlchimie_Horizontal_Texte_Day.png — ancien logo (encore sur certaines pages)
