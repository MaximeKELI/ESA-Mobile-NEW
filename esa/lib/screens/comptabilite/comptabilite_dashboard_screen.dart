import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/app_theme_enhanced.dart';
import '../../core/constants/asset_constants.dart';
import '../../core/widgets/asset_icon.dart';
import '../../core/widgets/animated_menu_card.dart';
import '../../core/widgets/fade_in_widget.dart';

/// Tableau de bord comptabilité
class ComptabiliteDashboardScreen extends StatelessWidget {
  const ComptabiliteDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace Comptabilité'),
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: BoxDecoration(
                color: AppTheme.primaryColor,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: Colors.white,
                    child: ClipOval(
                      child: Image.asset(
                        AssetConstants.profile,
                        width: 60,
                        height: 60,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          final nom = user?.nom;
                          return Text(
                            (nom != null && nom.isNotEmpty) 
                                ? nom.substring(0, 1).toUpperCase() 
                                : 'C',
                            style: TextStyle(
                              fontSize: 24,
                              color: AppTheme.primaryColor,
                              fontWeight: FontWeight.bold,
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '${user?.nom ?? ""} ${user?.prenom ?? ""}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.email ?? '',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.home),
              title: const Text('Tableau de bord'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.fee),
              title: const Text('Paiements'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Paiements - À implémenter')),
                );
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.downloads),
              title: const Text('Reçus'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Reçus - À implémenter')),
                );
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.profile),
              title: const Text('Mon profil'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Profil - À implémenter')),
                );
              },
            ),
            const Divider(),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.exit, color: Colors.red),
              title: const Text('Déconnexion', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                Provider.of<AuthProvider>(context, listen: false).logout();
              },
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            FadeInWidget(
              child: Text(
                'Bienvenue ${user?.prenom ?? "Comptable"} !',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
            ),
            const SizedBox(height: 24),
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.5,
              children: [
                AnimatedMenuCard(
                  title: 'Enregistrer paiement',
                  assetPath: AssetConstants.fee,
                  color: AppThemeEnhanced.primaryColor,
                  index: 0,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Enregistrer paiement - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Reçus',
                  assetPath: AssetConstants.downloads,
                  color: AppThemeEnhanced.secondaryColor,
                  index: 1,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Reçus - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Rapports',
                  assetPath: AssetConstants.downloads,
                  color: AppThemeEnhanced.accentColor,
                  index: 2,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Rapports - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Arriérés',
                  assetPath: AssetConstants.fee,
                  color: AppThemeEnhanced.errorColor,
                  index: 3,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Arriérés - À implémenter')),
                    );
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}


