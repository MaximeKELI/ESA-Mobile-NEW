# 🔧 Résolution Complète de l'Erreur de Linker Linux

## Erreur Identifiée

```
/snap/flutter/current/usr/bin/ld : /lib/x86_64-linux-gnu/libsecret-1.so.0 : référence indéfinie vers « g_task_set_static_name »
/snap/flutter/current/usr/bin/ld : /lib/x86_64-linux-gnu/libsecret-1.so.0 : référence indéfinie vers « g_once_init_enter_pointer »
```

## Cause

Le plugin `flutter_secure_storage_linux` utilise `libsecret-1` qui nécessite GLib 2.0, mais les symboles ne sont pas correctement résolus lors du linking.

## Solution Complète

### Étape 1 : Installer les Dépendances Système

```bash
sudo apt-get update
sudo apt-get install -y \
  libglib2.0-dev \
  libsecret-1-dev \
  libgtk-3-dev \
  libblkid-dev \
  liblzma-dev \
  pkg-config \
  cmake \
  ninja-build \
  clang \
  libclang-dev
```

### Étape 2 : Vérifier les Versions

```bash
pkg-config --modversion glib-2.0
pkg-config --modversion libsecret-1
```

Vous devriez avoir :
- glib-2.0 >= 2.56.0
- libsecret-1 >= 0.18.0

### Étape 3 : Nettoyer et Recompiler

```bash
cd /home/maxime/Application_ESA/esa
flutter clean
flutter pub get
flutter run -d linux
```

## Solution Alternative : Si le Problème Persiste

### Option 1 : Mettre à jour GLib

Si votre version de GLib est trop ancienne :

```bash
sudo apt-get install --reinstall libglib2.0-0 libglib2.0-dev
```

### Option 2 : Utiliser une Version Plus Récente de Flutter

```bash
flutter upgrade
flutter channel stable
flutter upgrade
```

### Option 3 : Désactiver Temporairement flutter_secure_storage

Si vous voulez tester le reste de l'application sans le stockage sécurisé :

1. Commentez `flutter_secure_storage` dans `pubspec.yaml`
2. Supprimez les imports dans le code
3. Utilisez `shared_preferences` à la place temporairement

### Option 4 : Compiler avec des Flags Spécifiques

Modifiez `linux/runner/CMakeLists.txt` pour ajouter :

```cmake
target_link_options(${BINARY_NAME} PRIVATE 
  -Wl,--no-as-needed 
  -lglib-2.0 
  -lgobject-2.0
)
```

## Vérification Finale

Après avoir installé les dépendances, vérifiez :

```bash
flutter doctor -v
pkg-config --exists glib-2.0 && echo "GLib OK" || echo "GLib manquant"
pkg-config --exists libsecret-1 && echo "libsecret OK" || echo "libsecret manquant"
```

## Si Rien Ne Fonctionne

1. Vérifiez que vous utilisez bien Ubuntu 24.04 (compatible)
2. Essayez de compiler une application Flutter simple pour isoler le problème
3. Consultez les issues GitHub de `flutter_secure_storage_linux`
4. Envisagez d'utiliser Flutter sans snap (installation manuelle)

## Note Importante

Les modifications dans `CMakeLists.txt` ont déjà été faites pour lier GLib explicitement. Le problème vient probablement de dépendances système manquantes ou de versions incompatibles.


