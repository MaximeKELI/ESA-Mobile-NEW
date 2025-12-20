import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/app_theme_enhanced.dart';
import '../../core/constants/asset_constants.dart';
import '../../core/widgets/asset_icon.dart';
import '../../core/widgets/animated_menu_card.dart';
import '../../core/widgets/fade_in_widget.dart';
import '../../providers/auth_provider.dart';

/// Tableau de bord étudiant
class EtudiantDashboardScreen extends StatelessWidget {
  const EtudiantDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Espace Étudiant'),
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
                                : 'E',
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
              leading: AssetIcon(assetPath: AssetConstants.exam),
              title: const Text('Mes notes'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Mes notes - À implémenter')),
                );
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.calendar),
              title: const Text('Emploi du temps'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Emploi du temps - À implémenter')),
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
                'Bienvenue ${user?.prenom ?? "Étudiant"} !',
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
                  title: 'Mes notes',
                  assetPath: AssetConstants.exam,
                  color: AppThemeEnhanced.primaryColor,
                  index: 0,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Mes notes - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Emploi du temps',
                  assetPath: AssetConstants.calendar,
                  color: AppThemeEnhanced.secondaryColor,
                  index: 1,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Emploi du temps - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Absences',
                  assetPath: AssetConstants.attendance,
                  color: AppThemeEnhanced.accentColor,
                  index: 2,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Absences - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Paiements',
                  assetPath: AssetConstants.fee,
                  color: AppThemeEnhanced.successColor,
                  index: 3,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Paiements - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Devoirs',
                  assetPath: AssetConstants.homework,
                  color: AppThemeEnhanced.infoColor,
                  index: 4,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Devoirs - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Bibliothèque',
                  assetPath: AssetConstants.library,
                  color: AppThemeEnhanced.warningColor,
                  index: 5,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Bibliothèque - À implémenter')),
                    );
                  },
                ),
                AnimatedMenuCard(
                  title: 'Messages',
                  assetPath: AssetConstants.smsAppGif,
                  color: AppThemeEnhanced.infoColor,
                  index: 6,
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Messages - À implémenter')),
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


