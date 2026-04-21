/**
 * Apps Script — Présence session 29 avril 2026
 * Sheet : Codex Bureau (1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g)
 * Onglet : 📅 29 Avril 2026
 *
 * Colonnes : Date soumission | Prénom | Source
 *
 * Déploiement :
 * 1. Ouvrir le Google Sheet Codex Bureau
 * 2. Extensions → Apps Script
 * 3. Créer un nouveau fichier (ou un nouveau projet) et coller ce code
 * 4. Déployer → Nouveau déploiement → Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde
 * 5. Copier l'URL et la coller dans sessions/29-avril.html (APPS_SCRIPT_SESSION_29AVRIL_URL)
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    var ss = SpreadsheetApp.openById('1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g');
    var sheetName = '📅 29 Avril 2026';
    var sheet = ss.getSheetByName(sheetName);

    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.appendRow(['Date soumission', 'Prénom', 'Source']);
    }

    sheet.appendRow([
      new Date(),
      data.prenom || '',
      data.source || ''
    ]);

    // Notification email
    MailApp.sendEmail(
      'pierrick.oblin@hotmail.fr',
      '👋 Présence confirmée — 29 avril : ' + (data.prenom || '(anonyme)'),
      'Prénom : ' + (data.prenom || '') + '\n'
      + 'Source : ' + (data.source || '—') + '\n'
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
