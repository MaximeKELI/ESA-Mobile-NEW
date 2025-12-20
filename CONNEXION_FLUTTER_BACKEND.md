# 🔗 Connexion Flutter ↔ Backend

## ✅ Configuration Effectuée

### 1. Backend
- ✅ Serveur Flask démarré sur `http://localhost:5000`
- ✅ Base de données initialisée avec utilisateurs de test
- ✅ API REST complète avec tous les endpoints

### 2. Frontend Flutter
- ✅ URL de base configurée dans `api_constants.dart`
- ✅ Service API créé avec gestion des tokens JWT
- ✅ Constantes pour nouvelles fonctionnalités ajoutées

## 🔧 Configuration de l'URL

### Pour Linux (actuel)
```dart
static const String baseUrl = 'http://localhost:5000/api';
```

### Pour Android Emulator
```dart
static const String baseUrl = 'http://10.0.2.2:5000/api';
```

### Pour Appareil Physique
```dart
static const String baseUrl = 'http://192.168.1.74:5000/api'; // Remplacer par votre IP
```

## 🧪 Test de Connexion

### 1. Vérifier que le backend fonctionne
```bash
cd backend
python3 app.py
# Dans un autre terminal:
curl http://localhost:5000/api/health
```

### 2. Tester depuis Flutter

Dans votre code Flutter, testez la connexion :

```dart
import 'package:dio/dio.dart';
import 'package:esa/core/constants/api_constants.dart';

void testConnection() async {
  try {
    final dio = Dio(BaseOptions(baseUrl: ApiConstants.baseUrl));
    final response = await dio.get('/health');
    print('✅ Connexion OK: ${response.data}');
  } catch (e) {
    print('❌ Erreur de connexion: $e');
  }
}
```

## 🔑 Authentification

### Login depuis Flutter

```dart
import 'package:esa/core/services/api_service.dart';
import 'package:esa/core/constants/api_constants.dart';

Future<void> login() async {
  final apiService = ApiService();
  await apiService.init();
  
  try {
    final response = await apiService.post(
      ApiConstants.login,
      data: {
        'username': 'admin',
        'password': 'password123',
      },
    );
    
    if (response.statusCode == 200) {
      final accessToken = response.data['access_token'];
      final refreshToken = response.data['refresh_token'];
      
      await apiService.saveTokens(accessToken, refreshToken);
      print('✅ Login réussi');
    }
  } catch (e) {
    print('❌ Erreur de login: $e');
  }
}
```

## 📱 Utilisateurs de Test

- **Admin**: `admin` / `password123`
- **Comptable**: `comptable` / `password123`
- **Enseignant**: `enseignant1` / `password123`
- **Étudiant**: `etudiant1` / `password123`
- **Parent**: `parent1` / `password123`

## 🚀 Prochaines Étapes

1. **Tester la connexion** depuis Flutter
2. **Implémenter l'écran de login** avec AppService
3. **Créer les écrans** pour chaque module
4. **Intégrer les nouvelles fonctionnalités** (E-Learning, Gamification, etc.)

## ⚠️ Notes Importantes

- Le backend doit être démarré avant de lancer Flutter
- Pour Android, utilisez `10.0.2.2` au lieu de `localhost`
- Pour iOS/Web, utilisez `localhost` ou l'IP du réseau
- Les tokens JWT expirent après 24h par défaut

## 🐛 Dépannage

### Erreur "Connection refused"
- Vérifiez que le backend est démarré
- Vérifiez l'URL dans `api_constants.dart`
- Vérifiez le firewall

### Erreur CORS
- Le backend est configuré pour accepter toutes les origines en développement
- En production, configurez CORS correctement

### Erreur 401 (Unauthorized)
- Vérifiez que vous avez un token valide
- Vérifiez le format: `Authorization: Bearer <token>`


