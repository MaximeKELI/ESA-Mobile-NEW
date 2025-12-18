import 'package:flutter/material.dart';

/// Tableau de bord étudiant
class EtudiantDashboardScreen extends StatelessWidget {
  const EtudiantDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace Étudiant'),
      ),
      body: const Center(
        child: Text('Tableau de bord étudiant - À implémenter'),
      ),
    );
  }
}

