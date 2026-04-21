/**
 * Apps Script — Inscriptions sessions (universel)
 * Sheet : Codex Bureau (1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g)
 *
 * Reçoit : { prenom, source, session_name }
 * Crée l'onglet "📅 {session_name}" si absent
 * Colonnes : Date soumission | Prénom | Source
 *
 * Déploiement :
 * 1. Ouvrir le Google Sheet Codex Bureau
 * 2. Extensions → Apps Script
 * 3. Coller ce code
 * 4. Déployer → Nouveau déploiement → Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde
 * 5. Copier l'URL et la coller dans toutes les pages sessions
 *    (remplacer APPS_SCRIPT_SESSIONS_URL)
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sessionName = data.session_name || 'Session inconnue';

    var ss = SpreadsheetApp.openById('1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g');
    var sheetName = '📅 ' + sessionName;
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

    MailApp.sendEmail(
      'pierrick.oblin@hotmail.fr',
      'Nouvelle inscription — ' + sessionName + ' : ' + (data.prenom || '(anonyme)'),
      'Prénom : ' + (data.prenom || '') + '\n'
      + 'Source : ' + (data.source || '—') + '\n'
      + 'Session : ' + sessionName + '\n'
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
