# 🏗️ Architecture Frontend - Connexion des Fichiers

## 📋 Vue d'Ensemble

Tous les fichiers frontend sont maintenant connectés via un système de navigation centralisé.

## 🔗 Structure de Connexion

```
┌─────────────────────────────────────────────────────────┐
│                    main.dart                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │         MaterialApp                               │   │
│  │  - navigatorKey: NavigationService               │   │
│  │  - onGenerateRoute: AppRoutes.generateRoute      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 AuthWrapper                             │
│  - Écoute AuthProvider                                  │
│  - Redirige vers LoginScreen ou HomeScreen             │
└─────────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
┌──────────────────┐      ┌──────────────────┐
│  LoginScreen     │◄─────┤  RegisterScreen  │
│  - AuthProvider  │      │  - AuthProvider  │
└──────────────────┘      └──────────────────┘
         │
         ▼ (après connexion)
┌─────────────────────────────────────────────────────────┐
│                 HomeScreen                              │
│  - Écoute AuthProvider                                  │
│  - Redirige selon le rôle                               │
└─────────────────────────────────────────────────────────┘
         │
         ├─── admin ────────► AdminDashboardScreen
         ├─── comptabilite ─► ComptabiliteDashboardScreen
         ├─── enseignant ───► EnseignantDashboardScreen
         ├─── etudiant ─────► EtudiantDashboardScreen
         └─── parent ───────► ParentDashboardScreen
```

## 🔄 Flux de Données

### 1. Services
```
ApiService (Singleton)
  │
  ├───► AuthService (Singleton)
  │       │
  │       └───► AuthProvider (ChangeNotifier)
  │               │
  │               └───► Tous les écrans (via Consumer)
```

### 2. Navigation
```
AppRoutes (Routes centralisées)
  │
  ├───► AppRouter.generateRoute()
  │       │
  │       └───► MaterialApp.onGenerateRoute
  │
  └───► NavigationService (Global)
          │
          └───► Accessible depuis n'importe où
```

## 📁 Fichiers et Leurs Connexions

### Core
- `core/routes/app_router.dart` → Connecte toutes les routes
- `core/navigation/navigation_service.dart` → Service de navigation global
- `core/services/api_service.dart` → Utilisé par AuthService
- `core/services/auth_service.dart` → Utilisé par AuthProvider
- `core/models/user_model.dart` → Utilisé partout

### Providers
- `providers/auth_provider.dart` → Utilisé par tous les écrans

### Screens
- `screens/auth/login_screen.dart` → Connecté à RegisterScreen et AuthProvider
- `screens/auth/register_screen.dart` → Connecté à LoginScreen et AuthProvider
- `screens/home/home_screen.dart` → Connecté à tous les dashboards
- `screens/admin/admin_dashboard_screen.dart` → Connecté à AuthProvider
- `screens/comptabilite/comptabilite_dashboard_screen.dart` → Connecté à AuthProvider
- `screens/enseignant/enseignant_dashboard_screen.dart` → Connecté à AuthProvider
- `screens/etudiant/etudiant_dashboard_screen.dart` → Connecté à AuthProvider
- `screens/parent/parent_dashboard_screen.dart` → Connecté à AuthProvider

## ✅ Vérification des Connexions

### ✅ Services Connectés
- [x] ApiService → AuthService
- [x] AuthService → AuthProvider
- [x] AuthProvider → Tous les écrans

### ✅ Navigation Connectée
- [x] Routes définies dans AppRoutes
- [x] Router configuré dans MaterialApp
- [x] NavigationService disponible globalement
- [x] Tous les écrans peuvent naviguer entre eux

### ✅ Écrans Connectés
- [x] LoginScreen ↔ RegisterScreen
- [x] LoginScreen → HomeScreen (après connexion)
- [x] HomeScreen → Dashboards (selon rôle)
- [x] Tous les dashboards → AuthProvider

## 🎯 Utilisation

### Navigation Simple
```dart
// Depuis n'importe quel écran
Navigator.pushNamed(context, AppRoutes.login);
```

### Navigation avec Arguments
```dart
Navigator.pushNamed(
  context,
  AppRoutes.profile,
  arguments: {'userId': 123},
);
```

### Navigation depuis Service
```dart
final navService = NavigationService();
navService.navigateTo(AppRoutes.login);
```

## 📝 Notes

- Tous les écrans utilisent `Consumer<AuthProvider>` pour accéder à l'utilisateur
- La navigation se fait via `Navigator.pushNamed()` avec les routes centralisées
- Les services sont des singletons accessibles partout
- Le système de routes permet d'ajouter facilement de nouveaux écrans

---

**🎉 Tous les fichiers frontend sont maintenant correctement connectés et peuvent communiquer entre eux !**

