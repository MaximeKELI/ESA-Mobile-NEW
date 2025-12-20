import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/app_theme_enhanced.dart';
import '../../core/constants/asset_constants.dart';
import '../../core/widgets/asset_icon.dart';
import '../../core/widgets/menu_card.dart';
import '../../core/widgets/animated_stat_card.dart';
import '../../core/widgets/fade_in_widget.dart';
import '../../providers/auth_provider.dart';

/// Tableau de bord administrateur
class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tableau de bord - Administration'),
        actions: [
          IconButton(
            icon: AssetIconWithBadge(
              assetPath: AssetConstants.notification,
              badgeCount: 0, // TODO: Récupérer le nombre réel de notifications
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Notifications - À implémenter')),
              );
            },
          ),
          PopupMenuButton(
            icon: AssetIcon(assetPath: AssetConstants.profile, size: 28),
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: const [
                    Icon(Icons.person),
                    SizedBox(width: 8),
                    Text('Profil'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'settings',
                child: Row(
                  children: [
                    Icon(Icons.settings),
                    SizedBox(width: 8),
                    Text('Paramètres'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout),
                    SizedBox(width: 8),
                    Text('Déconnexion'),
                  ],
                ),
              ),
            ],
            onSelected: (value) {
              if (value == 'logout') {
                Provider.of<AuthProvider>(context, listen: false).logout();
              } else if (value == 'profile') {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Profil de ${user?.nom ?? "Admin"}')),
                );
              }
            },
          ),
        ],
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
                                : 'A',
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
              selected: _selectedIndex == 0,
              onTap: () {
                setState(() => _selectedIndex = 0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.classroom),
              title: const Text('Utilisateurs'),
              selected: _selectedIndex == 1,
              onTap: () {
                setState(() => _selectedIndex = 1);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.schoolBuilding),
              title: const Text('Académique'),
              selected: _selectedIndex == 2,
              onTap: () {
                setState(() => _selectedIndex = 2);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.fee),
              title: const Text('Financier'),
              selected: _selectedIndex == 3,
              onTap: () {
                setState(() => _selectedIndex = 3);
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: AssetIcon(assetPath: AssetConstants.settingGif),
              title: const Text('Paramètres'),
              selected: _selectedIndex == 4,
              onTap: () {
                setState(() => _selectedIndex = 4);
                Navigator.pop(context);
              },
            ),
            const Divider(),
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
            ListTile(
              leading: const Icon(Icons.help),
              title: const Text('Aide'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Aide - À implémenter')),
                );
              },
            ),
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
      body: IndexedStack(
        index: _selectedIndex,
        children: const [
          _DashboardTab(),
          _UsersTab(),
          _AcademicTab(),
          _FinancialTab(),
          _SettingsTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() => _selectedIndex = index);
        },
        destinations: [
          NavigationDestination(
            icon: ImageIcon(AssetImage(AssetConstants.home), size: 24),
            label: 'Tableau de bord',
          ),
          NavigationDestination(
            icon: ImageIcon(AssetImage(AssetConstants.classroom), size: 24),
            label: 'Utilisateurs',
          ),
          NavigationDestination(
            icon: ImageIcon(AssetImage(AssetConstants.schoolBuilding), size: 24),
            label: 'Académique',
          ),
          NavigationDestination(
            icon: ImageIcon(AssetImage(AssetConstants.fee), size: 24),
            label: 'Financier',
          ),
          NavigationDestination(
            icon: ImageIcon(AssetImage(AssetConstants.settingGif), size: 24),
            label: 'Paramètres',
          ),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatelessWidget {
  const _DashboardTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Statistiques',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 1.5,
            children: [
              AnimatedStatCard(
                title: 'Étudiants',
                value: '0',
                assetPath: AssetConstants.classroom,
                color: AppThemeEnhanced.primaryColor,
                index: 0,
              ),
              AnimatedStatCard(
                title: 'Enseignants',
                value: '0',
                assetPath: AssetConstants.profile,
                color: AppThemeEnhanced.secondaryColor,
                index: 1,
              ),
              AnimatedStatCard(
                title: 'Classes',
                value: '0',
                assetPath: AssetConstants.classroom,
                color: AppThemeEnhanced.accentColor,
                index: 2,
              ),
              AnimatedStatCard(
                title: 'Taux de réussite',
                value: '0%',
                assetPath: AssetConstants.exam,
                color: AppThemeEnhanced.successColor,
                index: 3,
              ),
            ],
          ),
        ],
      ),
    );
  }
}


class _UsersTab extends StatelessWidget {
  const _UsersTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Gestion des utilisateurs - À implémenter'),
    );
  }
}

class _AcademicTab extends StatelessWidget {
  const _AcademicTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Gestion académique - À implémenter'),
    );
  }
}

class _FinancialTab extends StatelessWidget {
  const _FinancialTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Gestion financière - À implémenter'),
    );
  }
}

class _SettingsTab extends StatelessWidget {
  const _SettingsTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Paramètres - À implémenter'),
    );
  }
}

