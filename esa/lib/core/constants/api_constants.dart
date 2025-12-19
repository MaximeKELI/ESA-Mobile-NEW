/// Constantes de l'API
class ApiConstants {
  // URL de base de l'API (à modifier selon votre configuration)
  // static const String baseUrl = 'http://10.0.2.2:5000/api'; // Pour émulateur Android
  static const String baseUrl = 'http://localhost:5000/api'; // Pour Linux/Web/iOS
  // static const String baseUrl = 'http://192.168.1.74:5000/api'; // Pour appareil physique (remplacer par votre IP)
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Endpoints d'authentification
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refresh = '/auth/refresh';
  static const String changePassword = '/auth/change-password';
  static const String forgotPassword = '/auth/forgot-password';
  static const String resetPassword = '/auth/reset-password';
  static const String me = '/auth/me';
  
  // Endpoints communs
  static const String annonces = '/commun/annonces';
  static const String messages = '/commun/messages';
  static const String searchUsers = '/commun/users/search';
  static const String parametres = '/commun/parametres';
  
  // Endpoints admin
  static const String users = '/admin/users';
  static const String anneesAcademiques = '/admin/annees-academiques';
  static const String filieres = '/admin/filieres';
  static const String niveaux = '/admin/niveaux';
  static const String classes = '/admin/classes';
  static const String matieres = '/admin/matieres';
  static const String typesFrais = '/admin/types-frais';
  static const String fraisClasses = '/admin/frais-classes';
  static const String dashboardStats = '/admin/dashboard/stats';
  
  // Endpoints comptabilité
  static const String paiements = '/comptabilite/paiements';
  static const String validatePaiement = '/comptabilite/paiements';
  static const String financialReport = '/comptabilite/reports/financier';
  static const String situationFinanciere = '/comptabilite/etudiants';
  
  // Endpoints enseignant
  static const String enseignantClasses = '/enseignant/classes';
  static const String enseignantMatieres = '/enseignant/matieres';
  static const String enseignantNotes = '/enseignant/notes';
  static const String enseignantAbsences = '/enseignant/absences';
  
  // Endpoints étudiant
  static const String etudiantProfile = '/etudiant/profile';
  static const String etudiantNotes = '/etudiant/notes';
  static const String etudiantMoyennes = '/etudiant/moyennes';
  static const String etudiantClassement = '/etudiant/classement';
  static const String etudiantBulletin = '/etudiant/bulletin';
  static const String etudiantAbsences = '/etudiant/absences';
  static const String etudiantEmploiTemps = '/etudiant/emploi-temps';
  static const String etudiantDecisions = '/etudiant/decisions-academiques';
  static const String etudiantNotifications = '/etudiant/notifications';
  
  // Endpoints parent
  static const String parentEnfants = '/parent/enfants';
  static const String parentEnfantNotes = '/parent/enfants';
  static const String parentEnfantMoyennes = '/parent/enfants';
  static const String parentEnfantAbsences = '/parent/enfants';
  static const String parentEnfantSituation = '/parent/enfants';
  static const String parentNotifications = '/parent/notifications';
}

