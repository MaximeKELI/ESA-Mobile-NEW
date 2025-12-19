import 'package:flutter/material.dart';

/// Service de navigation global
class NavigationService {
  static final NavigationService _instance = NavigationService._internal();
  factory NavigationService() => _instance;
  NavigationService._internal();

  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  /// Obtient le contexte de navigation
  BuildContext? get context => navigatorKey.currentContext;

  /// Navigue vers une route
  Future<T?> navigateTo<T>(String route, {Object? arguments}) {
    if (context == null) return Future.value(null);
    return Navigator.pushNamed<T>(
      context!,
      route,
      arguments: arguments,
    );
  }

  /// Remplace la route actuelle
  Future<T?> replaceWith<T extends Object?>(String route, {Object? arguments}) {
    if (context == null) return Future.value(null);
    return Navigator.pushReplacementNamed<T, Object?>(
      context!,
      route,
      arguments: arguments,
    );
  }

  /// Remplace toutes les routes
  Future<T?> navigateAndClearStack<T>(String route, {Object? arguments}) {
    if (context == null) return Future.value(null);
    return Navigator.pushNamedAndRemoveUntil<T>(
      context!,
      route,
      (route) => false,
      arguments: arguments,
    );
  }

  /// Retour en arrière
  void goBack<T>([T? result]) {
    if (context == null) return;
    Navigator.pop<T>(context!, result);
  }

  /// Retourne à une route spécifique
  void popUntil(String route) {
    if (context == null) return;
    Navigator.popUntil(context!, ModalRoute.withName(route));
  }
}

