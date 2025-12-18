import 'package:flutter/material.dart';

/// Tableau de bord enseignant
class EnseignantDashboardScreen extends StatelessWidget {
  const EnseignantDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace Enseignant'),
      ),
      body: const Center(
        child: Text('Tableau de bord enseignant - À implémenter'),
      ),
    );
  }
}

