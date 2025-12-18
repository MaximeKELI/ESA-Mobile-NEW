import 'package:flutter/foundation.dart';
import '../core/models/user_model.dart';
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

    _user = _authService.currentUser;
    _isLoading = false;
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

