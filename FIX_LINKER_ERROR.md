# 🔧 Solution pour l'Erreur de Linker Linux

## Problème

Erreur lors de la compilation Flutter sur Linux :
```
/snap/flutter/current/usr/bin/ld : /lib/x86_64-linux-gnu/libsecret-1.so.0 : référence indéfinie vers « g_task_set_static_name »
/snap/flutter/current/usr/bin/ld : /lib/x86_64-linux-gnu/libsecret-1.so.0 : référence indéfinie vers « g_once_init_enter_pointer »
```

## Cause

Le plugin `flutter_secure_storage_linux` utilise `libsecret-1` qui nécessite GLib, mais les symboles ne sont pas correctement liés.

## Solution 1 : Installer les dépendances système

```bash
sudo apt-get update
sudo apt-get install -y \
  libglib2.0-dev \
  libsecret-1-dev \
  libgtk-3-dev \
  libblkid-dev \
  liblzma-dev
```

## Solution 2 : Modifier CMakeLists.txt

Les fichiers CMakeLists.txt ont été modifiés pour lier explicitement GLib.

## Solution 3 : Alternative - Désactiver flutter_secure_storage temporairement

Si le problème persiste, vous pouvez temporairement retirer `flutter_secure_storage` du `pubspec.yaml` pour tester le reste de l'application.

## Vérification

Après installation des dépendances :
```bash
cd esa
flutter clean
flutter pub get
flutter run -d linux
```

## Si le problème persiste

1. Vérifiez les versions de GLib et libsecret :
   ```bash
   pkg-config --modversion glib-2.0
   pkg-config --modversion libsecret-1
   ```

2. Essayez de mettre à jour Flutter :
   ```bash
   flutter upgrade
   ```

3. Vérifiez que vous utilisez la bonne version de clang :
   ```bash
   clang --version
   ```


