/// Constantes de l'application
class AppConstants {
  // Informations de l'école
  static const String schoolName = 'École Supérieure des Affaires';
  static const String schoolLocation = 'Lomé, Togo';
  
  // Rôles utilisateurs
  static const String roleAdmin = 'admin';
  static const String roleComptabilite = 'comptabilite';
  static const String roleEnseignant = 'enseignant';
  static const String roleEtudiant = 'etudiant';
  static const String roleParent = 'parent';
  
  // Types de notes
  static const String typeNoteDevoir = 'devoir';
  static const String typeNoteControle = 'controle';
  static const String typeNoteExamen = 'examen';
  
  // Types d'absences
  static const String typeAbsence = 'absence';
  static const String typeRetard = 'retard';
  static const String typeJustifie = 'justifie';
  
  // Modes de paiement
  static const String modePaiementEspeces = 'especes';
  static const String modePaiementMobileMoney = 'mobile_money';
  static const String modePaiementVirement = 'virement';
  
  // Statuts de paiement
  static const String statutPaiementEnAttente = 'en_attente';
  static const String statutPaiementValide = 'valide';
  static const String statutPaiementRejete = 'rejete';
  
  // Périodes académiques
  static const String periodeTrimestre1 = 'trimestre1';
  static const String periodeTrimestre2 = 'trimestre2';
  static const String periodeTrimestre3 = 'trimestre3';
  static const String periodeAnnuel = 'annuel';
  
  // Décisions académiques
  static const String decisionAdmis = 'admis';
  static const String decisionRedouble = 'redouble';
  static const String decisionExclu = 'exclu';
  static const String decisionPassageConditionnel = 'passage_conditionnel';
  
  // Seuil de réussite
  static const double seuilReussite = 10.0;
  
  // Délai de verrouillage pour impayés (en jours)
  static const int delaiVerrouillageImpaye = 30;
  
  // Format de date
  static const String dateFormat = 'dd/MM/yyyy';
  static const String dateTimeFormat = 'dd/MM/yyyy HH:mm';
  
  // Taille maximale des fichiers
  static const int maxFileSize = 5 * 1024 * 1024; // 5MB
  
  // Nombre d'éléments par page
  static const int itemsPerPage = 20;
}

