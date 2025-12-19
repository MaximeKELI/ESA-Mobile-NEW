import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import 'api_service.dart';
import '../constants/api_constants.dart';

/// Service d'authentification
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final ApiService _apiService = ApiService();
  UserModel? _currentUser;
  SharedPreferences? _prefs;

  /// Initialise le service
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    await _loadUserFromStorage();
  }

  /// Charge l'utilisateur depuis le stockage local
  Future<void> _loadUserFromStorage() async {
    final userJson = _prefs?.getString('current_user');
    if (userJson != null) {
      try {
        _currentUser = UserModel.fromJson(
          Map<String, dynamic>.from(
            json.decode(userJson) as Map
          )
        );
      } catch (e) {
        // Erreur de parsing, ignorer
      }
    }
  }

  /// Connexion
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _apiService.post(
        ApiConstants.login,
        data: {
          'username': username,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        
        // Sauvegarder les tokens
        await _apiService.saveTokens(
          data['access_token'] as String,
          data['refresh_token'] as String,
        );

        // Sauvegarder l'utilisateur
        if (data.containsKey('user')) {
          _currentUser = UserModel.fromJson(data['user'] as Map<String, dynamic>);
          await _prefs?.setString('current_user', json.encode(_currentUser!.toJson()));

          return {
            'success': true,
            'user': _currentUser,
          };
        } else {
          return {
            'success': false,
            'error': 'Réponse invalide du serveur',
          };
        }
      }

      return {
        'success': false,
        'error': response.data['error'] ?? 'Identifiants invalides',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString().contains('SocketException') 
            ? 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré.'
            : e.toString(),
      };
    }
  }

  /// Inscription
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String nom,
    required String prenom,
    required String role,
    String? telephone,
    String? adresse,
  }) async {
    try {
      final response = await _apiService.post(
        ApiConstants.register,
        data: {
          'username': username,
          'email': email,
          'password': password,
          'nom': nom,
          'prenom': prenom,
          'role': role,
          'telephone': telephone,
          'adresse': adresse,
        },
      );

      if (response.statusCode == 201) {
        final data = response.data as Map<String, dynamic>;
        
        if (data.containsKey('user')) {
          _currentUser = UserModel.fromJson(data['user'] as Map<String, dynamic>);
          await _prefs?.setString('current_user', json.encode(_currentUser!.toJson()));

          return {
            'success': true,
            'user': _currentUser,
            'message': data['message'] ?? 'Inscription réussie',
          };
        }
      }

      return {
        'success': false,
        'error': response.data['error'] ?? 'Erreur lors de l\'inscription',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString().contains('SocketException')
            ? 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré.'
            : e.toString(),
      };
    }
  }

  /// Déconnexion
  Future<void> logout() async {
    try {
      await _apiService.post(ApiConstants.logout);
    } catch (e) {
      // Ignorer les erreurs lors de la déconnexion
    } finally {
      await _apiService.clearTokens();
      _currentUser = null;
      await _prefs?.remove('current_user');
    }
  }

  /// Obtient l'utilisateur actuel
  UserModel? get currentUser => _currentUser;

  /// Vérifie si l'utilisateur est connecté
  bool get isAuthenticated => _currentUser != null;

  /// Change le mot de passe
  Future<Map<String, dynamic>> changePassword(
    String oldPassword,
    String newPassword,
  ) async {
    try {
      final response = await _apiService.post(
        ApiConstants.changePassword,
        data: {
          'old_password': oldPassword,
          'new_password': newPassword,
        },
      );

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'Mot de passe modifié avec succès'};
      }

      return {
        'success': false,
        'error': response.data['error'] ?? 'Erreur lors du changement de mot de passe',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Demande de réinitialisation de mot de passe
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await _apiService.post(
        ApiConstants.forgotPassword,
        data: {'email': email},
      );

      return {
        'success': response.statusCode == 200,
        'message': response.data['message'] ?? 'Email envoyé',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Réinitialise le mot de passe avec un token
  Future<Map<String, dynamic>> resetPassword(String token, String newPassword) async {
    try {
      final response = await _apiService.post(
        ApiConstants.resetPassword,
        data: {
          'token': token,
          'new_password': newPassword,
        },
      );

      return {
        'success': response.statusCode == 200,
        'message': response.data['message'] ?? 'Mot de passe réinitialisé',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Rafraîchit les informations de l'utilisateur
  Future<void> refreshUser() async {
    try {
      final response = await _apiService.get(ApiConstants.me);
      if (response.statusCode == 200) {
        _currentUser = UserModel.fromJson(response.data as Map<String, dynamic>);
        await _prefs?.setString('current_user', json.encode(_currentUser!.toJson()));
      }
    } catch (e) {
      // Ignorer les erreurs
    }
  }
}

