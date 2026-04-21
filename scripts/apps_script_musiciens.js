/**
 * Apps Script — Candidatures Musiciens
 * Sheet : Codex Bureau (1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g)
 * Onglet : Musiciens
 *
 * Colonnes : Date | Nom | Prénom | Instrument(s) | Téléphone | Adresse mail |
 *            Niveau (1-5) | Format | Disponibilités | Rémunération / défraiement
 *
 * Déploiement :
 * 1. Ouvrir le Google Sheet Codex Bureau
 * 2. Extensions → Apps Script
 * 3. Coller ce code (remplacer tout le contenu)
 * 4. Déployer → Nouveau déploiement → Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde
 * 5. Copier l'URL et la coller dans formulaires/musicien.html (APPS_SCRIPT_MUSICIENS_URL)
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    var sheet = SpreadsheetApp.getActiveSpreadsheet()
      .getSheetByName('Musiciens');

    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet()
        .insertSheet('Musiciens');
      sheet.appendRow([
        'Date', 'Nom', 'Prénom', 'Instrument(s)', 'Téléphone',
        'Adresse mail', 'Niveau (1-5)', 'Format', 'Disponibilités',
        'Rémunération / défraiement'
      ]);
    }

    sheet.appendRow([
      new Date(),
      data.nom || '',
      data.prenom || '',
      data.instruments || '',
      data.telephone || '',
      data.email || '',
      data.niveau || '',
      data.format || '',
      data.disponibilites || '',
      data.remuneration || ''
    ]);

    // Notification email
    MailApp.sendEmail(
      'pierrick.oblin@hotmail.fr',
      '🎹 Nouvelle candidature musicien : ' + (data.prenom || '') + ' ' + (data.nom || ''),
      'Prénom : ' + (data.prenom || '') + '\n'
      + 'Nom : ' + (data.nom || '') + '\n'
      + 'Instrument(s) : ' + (data.instruments || '') + '\n'
      + 'Email : ' + (data.email || '') + '\n'
      + 'Téléphone : ' + (data.telephone || '') + '\n'
      + 'Niveau : ' + (data.niveau || '') + '\n'
      + 'Format : ' + (data.format || '') + '\n'
      + 'Disponibilités : ' + (data.disponibilites || '') + '\n'
      + 'Rémunération : ' + (data.remuneration || '') + '\n'
      + '\nDate : ' + new Date().toLocaleString('fr-FR')
    );

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
