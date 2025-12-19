import 'package:flutter/material.dart';
import '../../screens/auth/login_screen.dart';
import '../../screens/auth/register_screen.dart';
import '../../screens/home/home_screen.dart';
import '../../screens/admin/admin_dashboard_screen.dart';
import '../../screens/comptabilite/comptabilite_dashboard_screen.dart';
import '../../screens/enseignant/enseignant_dashboard_screen.dart';
import '../../screens/etudiant/etudiant_dashboard_screen.dart';
import '../../screens/parent/parent_dashboard_screen.dart';

/// Routes de l'application
class AppRoutes {
  // Routes publiques
  static const String login = '/login';
  static const String register = '/register';
  
  // Routes authentifiées
  static const String home = '/home';
  static const String adminDashboard = '/admin/dashboard';
  static const String comptabiliteDashboard = '/comptabilite/dashboard';
  static const String enseignantDashboard = '/enseignant/dashboard';
  static const String etudiantDashboard = '/etudiant/dashboard';
  static const String parentDashboard = '/parent/dashboard';
  
  /// Génère les routes de l'application
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case login:
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      
      case register:
        return MaterialPageRoute(builder: (_) => const RegisterScreen());
      
      case home:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      
      case adminDashboard:
        return MaterialPageRoute(builder: (_) => const AdminDashboardScreen());
      
      case comptabiliteDashboard:
        return MaterialPageRoute(builder: (_) => const ComptabiliteDashboardScreen());
      
      case enseignantDashboard:
        return MaterialPageRoute(builder: (_) => const EnseignantDashboardScreen());
      
      case etudiantDashboard:
        return MaterialPageRoute(builder: (_) => const EtudiantDashboardScreen());
      
      case parentDashboard:
        return MaterialPageRoute(builder: (_) => const ParentDashboardScreen());
      
      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(
              child: Text('Route non trouvée: ${settings.name}'),
            ),
          ),
        );
    }
  }
}

/// Helper pour la navigation
class AppNavigator {
  /// Navigue vers une route
  static Future<T?> push<T>(BuildContext context, String route, {Object? arguments}) {
    return Navigator.pushNamed<T>(
      context,
      route,
      arguments: arguments,
    );
  }
  
  /// Remplace la route actuelle
  static Future<T?> pushReplacement<T extends Object?>(BuildContext context, String route, {Object? arguments}) {
    return Navigator.pushReplacementNamed<T, Object?>(
      context,
      route,
      arguments: arguments,
    );
  }
  
  /// Remplace toutes les routes
  static Future<T?> pushAndRemoveUntil<T>(
    BuildContext context,
    String route, {
    Object? arguments,
  }) {
    return Navigator.pushNamedAndRemoveUntil<T>(
      context,
      route,
      (route) => false,
      arguments: arguments,
    );
  }
  
  /// Retour en arrière
  static void pop<T>(BuildContext context, [T? result]) {
    Navigator.pop<T>(context, result);
  }
  
  /// Retourne à la route initiale
  static void popUntil(BuildContext context, String route) {
    Navigator.popUntil(context, ModalRoute.withName(route));
  }
}

