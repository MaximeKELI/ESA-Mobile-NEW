import '../core/models/user_model.dart';
import 'package:flutter/foundation.dart';
import '../core/services/auth_service.dart';

/// Provider pour la gestion de l'authentification
class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  
  UserModel? _user;
  bool _isLoading = true;
  String? _error;

  UserModel? get user => _user;
  bool get isAuthenticated => _user != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  AuthProvider() {
    _loadUser();
  }

  /// Charge l'utilisateur depuis le service
  Future<void> _loadUser() async {
    _isLoading = true;
    notifyListeners();

    await _authService.init();
    _user = _authService.currentUser;
    _isLoading = false;
    notifyListeners();
  }
  
  /// Recharge l'utilisateur depuis le service
  Future<void> reloadUser() async {
    await _authService.init();
    _user = _authService.currentUser;
    notifyListeners();
  }

  /// Connexion
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final result = await _authService.login(username, password);

    _isLoading = false;

    if (result['success'] == true) {
      _user = result['user'] as UserModel;
      _error = null;
      // Forcer la mise à jour pour déclencher la navigation
      notifyListeners();
      // Attendre un peu pour s'assurer que l'UI est mise à jour
      await Future.delayed(const Duration(milliseconds: 100));
      notifyListeners();
      return true;
    } else {
      _error = result['error'] as String;
      notifyListeners();
      return false;
    }
  }

  /// Inscription
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String nom,
    required String prenom,
    required String role,
    String? telephone,
    String? adresse,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final result = await _authService.register(
      username: username,
      email: email,
      password: password,
      nom: nom,
      prenom: prenom,
      role: role,
      telephone: telephone,
      adresse: adresse,
    );

    _isLoading = false;

    if (result['success'] == true) {
      _user = result['user'] as UserModel;
      _error = null;
      notifyListeners();
      await Future.delayed(const Duration(milliseconds: 100));
      notifyListeners();
      return true;
    } else {
      _error = result['error'] as String;
      notifyListeners();
      return false;
    }
  }

  /// Déconnexion
  Future<void> logout() async {
    await _authService.logout();
    _user = null;
    _error = null;
    notifyListeners();
  }

  /// Change le mot de passe
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final result = await _authService.changePassword(oldPassword, newPassword);

    _isLoading = false;

    if (result['success'] == true) {
      _error = null;
      notifyListeners();
      return true;
    } else {
      _error = result['error'] as String;
      notifyListeners();
      return false;
    }
  }

  /// Rafraîchit les informations de l'utilisateur
  Future<void> refreshUser() async {
    await _authService.refreshUser();
    _user = _authService.currentUser;
    notifyListeners();
  }
}

