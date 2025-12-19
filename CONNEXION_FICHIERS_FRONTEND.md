# 🔗 Connexion des Fichiers Frontend

## ✅ Système de Navigation Créé

### 1. Routes Centralisées

**Fichier :** `esa/lib/core/routes/app_router.dart`

Toutes les routes de l'application sont maintenant centralisées :

```dart
// Routes publiques
AppRoutes.login → LoginScreen
AppRoutes.register → RegisterScreen

// Routes authentifiées
AppRoutes.home → HomeScreen
AppRoutes.adminDashboard → AdminDashboardScreen
AppRoutes.comptabiliteDashboard → ComptabiliteDashboardScreen
AppRoutes.enseignantDashboard → EnseignantDashboardScreen
AppRoutes.etudiantDashboard → EtudiantDashboardScreen
AppRoutes.parentDashboard → ParentDashboardScreen
```

### 2. Service de Navigation Global

**Fichier :** `esa/lib/core/navigation/navigation_service.dart`

Permet de naviguer depuis n'importe où dans l'application :

```dart
final navService = NavigationService();
navService.navigateTo(AppRoutes.login);
navService.replaceWith(AppRoutes.home);
navService.goBack();
```

### 3. Intégration dans MaterialApp

**Fichier modifié :** `esa/lib/main.dart`

- ✅ `navigatorKey` configuré pour accès global
- ✅ `onGenerateRoute` configuré pour toutes les routes
- ✅ Tous les écrans sont maintenant accessibles

## 📊 Structure de Connexion

```
main.dart
  ↓
MaterialApp (avec routes)
  ↓
AuthWrapper
  ├─ LoginScreen ←→ RegisterScreen
  └─ HomeScreen
       ├─ AdminDashboardScreen
       ├─ ComptabiliteDashboardScreen
       ├─ EnseignantDashboardScreen
       ├─ EtudiantDashboardScreen
       └─ ParentDashboardScreen
```

## 🔄 Flux de Connexion

### Services
- `ApiService` → Connecté à `AuthService`
- `AuthService` → Connecté à `AuthProvider`
- `AuthProvider` → Utilisé par tous les écrans

### Écrans
- `LoginScreen` → Connecté à `RegisterScreen` et `AuthProvider`
- `RegisterScreen` → Connecté à `LoginScreen` et `AuthProvider`
- `HomeScreen` → Connecté à tous les dashboards selon le rôle
- Tous les dashboards → Connectés à `AuthProvider` pour l'utilisateur

### Navigation
- Tous les écrans peuvent naviguer via `Navigator.pushNamed()`
- Routes centralisées dans `AppRoutes`
- Service global disponible via `NavigationService()`

## 💻 Utilisation

### Navigation depuis un écran
```dart
// Vers login
Navigator.pushNamed(context, AppRoutes.login);

// Vers dashboard admin
Navigator.pushNamed(context, AppRoutes.adminDashboard);

// Retour en arrière
Navigator.pop(context);
```

### Navigation depuis un service/provider
```dart
final navService = NavigationService();
navService.navigateTo(AppRoutes.login);
```

### Navigation depuis un drawer/menu
```dart
ListTile(
  title: Text('Mon profil'),
  onTap: () {
    Navigator.pushNamed(context, AppRoutes.profile);
  },
)
```

## ✅ Tous les Fichiers Sont Maintenant Connectés

1. ✅ Routes centralisées
2. ✅ Navigation globale disponible
3. ✅ Services connectés entre eux
4. ✅ Providers accessibles partout
5. ✅ Écrans peuvent naviguer entre eux

---

**🎉 Tous les fichiers frontend sont maintenant correctement connectés !**

