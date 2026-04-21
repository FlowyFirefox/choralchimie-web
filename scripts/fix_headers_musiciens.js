function fixHeaders() {
  var ss = SpreadsheetApp.openById('1y3BPFWSWCW6E9MNjbO_9lqJ_ADYk8YPZwjSeyrbxI2g');
  var sheet = ss.getSheetByName('Musiciens');
  sheet.getRange(3,1,1,12).setValues([["N°","Nom","Prénom","Instrument(s)","Téléphone","Adresse mail","Sessions souhaitées","Durée souhaitée","Dis-nous en plus","Lien audio","Rémunération","Dernière intervention"]]);
}
