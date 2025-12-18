import 'package:flutter/material.dart';

/// Tableau de bord parent
class ParentDashboardScreen extends StatelessWidget {
  const ParentDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace Parent'),
      ),
      body: const Center(
        child: Text('Tableau de bord parent - À implémenter'),
      ),
    );
  }
}

