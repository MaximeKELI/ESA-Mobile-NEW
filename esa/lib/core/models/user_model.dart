/// Modèle utilisateur
class UserModel {
  final int id;
  final String username;
  final String email;
  final String role;
  final String nom;
  final String prenom;
  final String? telephone;
  final String? adresse;
  final String? photoPath;
  final bool isActive;
  final DateTime? lastLogin;

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    required this.nom,
    required this.prenom,
    this.telephone,
    this.adresse,
    this.photoPath,
    required this.isActive,
    this.lastLogin,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String,
      role: json['role'] as String,
      nom: json['nom'] as String,
      prenom: json['prenom'] as String,
      telephone: json['telephone'] as String?,
      adresse: json['adresse'] as String?,
      photoPath: json['photo_path'] as String?,
      isActive: json['is_active'] == 1 || json['is_active'] == true,
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'role': role,
      'nom': nom,
      'prenom': prenom,
      'telephone': telephone,
      'adresse': adresse,
      'photo_path': photoPath,
      'is_active': isActive,
      'last_login': lastLogin?.toIso8601String(),
    };
  }

  String get fullName => '$nom $prenom';
  
  bool get isAdmin => role == 'admin';
  bool get isComptabilite => role == 'comptabilite';
  bool get isEnseignant => role == 'enseignant';
  bool get isEtudiant => role == 'etudiant';
  bool get isParent => role == 'parent';
}

