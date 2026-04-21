/**
 * Apps Script — Adhésion / Membres
 * Sheet : Codex Bureau (1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g)
 * Onglet : Membres
 *
 * Colonnes : N° | Nom | Prénom | Rôle | Statut | Téléphone | Adresse mail |
 *            Date adhésion | Cotisation payée ? | Montant payé (€) | Date paiement |
 *            Formulaire rempli ? | Consentement photo/vidéo ? | Comment connu ? |
 *            Nb sessions assistées
 *
 * Déploiement :
 * 1. Ouvrir le Google Sheet Codex Bureau
 * 2. Extensions → Apps Script
 *    ⚠️ Si le script Musiciens est déjà là, créer un NOUVEAU projet Apps Script
 *       (ou utiliser des fichiers séparés dans le même projet)
 * 3. Coller ce code
 * 4. Déployer → Nouveau déploiement → Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde
 * 5. Copier l'URL et la coller dans outils/adhesion.html (APPS_SCRIPT_MEMBRES_URL)
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    var sheet = SpreadsheetApp.getActiveSpreadsheet()
      .getSheetByName('Membres');

    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet()
        .insertSheet('Membres');
      sheet.appendRow([
        'N°', 'Nom', 'Prénom', 'Rôle', 'Statut', 'Téléphone',
        'Adresse mail', 'Date adhésion', 'Cotisation payée ?',
        'Montant payé (€)', 'Date paiement', 'Formulaire rempli ?',
        'Consentement photo/vidéo ?', 'Comment connu ?', 'Nb sessions assistées'
      ]);
    }

    // Calculer le prochain N° automatiquement
    var lastRow = sheet.getLastRow();
    var nextNum = lastRow; // Row 1 = header, so lastRow = count of members

    sheet.appendRow([
      nextNum,
      data.nom || '',
      data.prenom || '',
      data.role || 'Membre',
      data.statut || 'Actif',
      data.telephone || '',
      data.email || '',
      new Date(),                         // Date adhésion = maintenant
      data.cotisation_payee || 'Non',
      data.montant || '',
      data.cotisation_payee === 'Oui' ? new Date() : '',
      'Oui',                              // Formulaire rempli = Oui (il vient de le remplir)
      data.consentement_photo || 'Non',
      data.comment_connu || '',
      0                                   // Nb sessions = 0 au départ
    ]);

    // Notification email
    MailApp.sendEmail(
      'pierrick.oblin@hotmail.fr',
      '✅ Nouvelle adhésion : ' + (data.prenom || '') + ' ' + (data.nom || ''),
      'Prénom : ' + (data.prenom || '') + '\n'
      + 'Nom : ' + (data.nom || '') + '\n'
      + 'Email : ' + (data.email || '') + '\n'
      + 'Téléphone : ' + (data.telephone || '') + '\n'
      + 'Consentement photo/vidéo : ' + (data.consentement_photo || 'Non') + '\n'
      + 'Comment connu : ' + (data.comment_connu || '') + '\n'
      + 'Cotisation payée : ' + (data.cotisation_payee || 'Non') + '\n'
      + 'Montant : ' + (data.montant || '—') + ' €\n'
      + '\nN° membre : ' + nextNum
      + '\nDate : ' + new Date().toLocaleString('fr-FR')
    );

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', numero: nextNum }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
