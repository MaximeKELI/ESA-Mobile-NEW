import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../core/constants/app_constants.dart';
import '../admin/admin_dashboard_screen.dart';
import '../comptabilite/comptabilite_dashboard_screen.dart';
import '../enseignant/enseignant_dashboard_screen.dart';
import '../etudiant/etudiant_dashboard_screen.dart';
import '../parent/parent_dashboard_screen.dart';

/// Écran d'accueil principal avec navigation par rôle
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, _) {
        final user = authProvider.user;
        if (user == null) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Afficher le dashboard selon le rôle
        switch (user.role) {
          case AppConstants.roleAdmin:
            return const AdminDashboardScreen();
          case AppConstants.roleComptabilite:
            return const ComptabiliteDashboardScreen();
          case AppConstants.roleEnseignant:
            return const EnseignantDashboardScreen();
          case AppConstants.roleEtudiant:
            return const EtudiantDashboardScreen();
          case AppConstants.roleParent:
            return const ParentDashboardScreen();
          default:
            return Scaffold(
              body: Center(
                child: Text('Rôle non reconnu: ${user.role}'),
              ),
            );
        }
      },
    );
  }
}

