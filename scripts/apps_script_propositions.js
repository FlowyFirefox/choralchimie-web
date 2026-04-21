/**
 * Apps Script — Propositions de titres (Choraoké)
 * Sheet : Répertoire (1idt--gTrO4PUTl3UMk4YOxyTFfv0XE4O)
 * Onglet : 📥 Suggestions
 *
 * Colonnes : Date | Titre | Artiste | Langue | Instrument | Source
 *
 * Déploiement :
 * 1. Ouvrir le Google Sheet Répertoire
 * 2. Extensions → Apps Script
 * 3. Coller ce code (remplacer tout le contenu)
 * 4. Déployer → Nouveau déploiement → Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde
 * 5. Copier l'URL et la coller dans choraoke-app/index.html (APPS_SCRIPT_SUGGESTIONS_URL)
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    var sheet = SpreadsheetApp.getActiveSpreadsheet()
      .getSheetByName('📥 Suggestions');

    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet()
        .insertSheet('📥 Suggestions');
      sheet.appendRow(['Date', 'Titre', 'Artiste', 'Langue', 'Instrument', 'Source']);
    }

    sheet.appendRow([
      new Date(),
      data.titre || '',
      data.artiste || '',
      data.langue || '',
      data.instrument || '',
      data.source || 'App Choraoké'
    ]);

    // Notification email
    MailApp.sendEmail(
      'pierrick.oblin@hotmail.fr',
      '🎵 Nouvelle suggestion Choraoké : ' + (data.titre || '(sans titre)'),
      'Titre : ' + (data.titre || '') + '\n'
      + 'Artiste : ' + (data.artiste || '') + '\n'
      + 'Langue : ' + (data.langue || '') + '\n'
      + 'Instrument : ' + (data.instrument || '') + '\n'
      + 'Source : ' + (data.source || 'App Choraoké') + '\n'
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
