import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../admin/admin_dashboard_screen.dart';
import '../parent/parent_dashboard_screen.dart';
import '../../core/constants/app_constants.dart';
import '../etudiant/etudiant_dashboard_screen.dart';
import '../enseignant/enseignant_dashboard_screen.dart';
import '../comptabilite/comptabilite_dashboard_screen.dart';

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

        // Debug: Afficher le rôle pour vérification
        print('HomeScreen - User role: ${user.role}');
        print('HomeScreen - User isActive: ${user.isActive}');
        print('HomeScreen - Role constants: admin=${AppConstants.roleAdmin}, parent=${AppConstants.roleParent}, enseignant=${AppConstants.roleEnseignant}');
        
        // Vérifier que l'utilisateur est actif (sauf pour les étudiants qui peuvent être inactifs)
        if (!user.isActive && user.role != AppConstants.roleEtudiant) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.lock, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Compte en attente d\'activation',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  const Text('Votre compte sera activé par un administrateur.'),
                ],
              ),
            ),
          );
        }

        // Afficher le dashboard selon le rôle
        switch (user.role) {
          case AppConstants.roleAdmin:
            print('HomeScreen - Redirecting to AdminDashboard');
            return const AdminDashboardScreen();
          case AppConstants.roleComptabilite:
            print('HomeScreen - Redirecting to ComptabiliteDashboard');
            return const ComptabiliteDashboardScreen();
          case AppConstants.roleEnseignant:
            print('HomeScreen - Redirecting to EnseignantDashboard');
            return const EnseignantDashboardScreen();
          case AppConstants.roleEtudiant:
            print('HomeScreen - Redirecting to EtudiantDashboard');
            return const EtudiantDashboardScreen();
          case AppConstants.roleParent:
            print('HomeScreen - Redirecting to ParentDashboard');
            return const ParentDashboardScreen();
          default:
            print('HomeScreen - Unknown role: ${user.role}');
            return Scaffold(
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Rôle non reconnu: ${user.role}'),
                    const SizedBox(height: 16),
                    Text('Rôles disponibles: ${AppConstants.roleAdmin}, ${AppConstants.roleComptabilite}, ${AppConstants.roleEnseignant}, ${AppConstants.roleEtudiant}, ${AppConstants.roleParent}'),
                  ],
                ),
              ),
            );
        }
      },
    );
  }
}

