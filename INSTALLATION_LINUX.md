# 🔧 Installation des Dépendances Linux pour Flutter

## Problème de Compilation

Si vous rencontrez des erreurs de linker (`clang: error: linker command failed`), installez les dépendances système suivantes :

## Dépendances Requises

```bash
sudo apt-get update
sudo apt-get install -y \
  libgtk-3-dev \
  libblkid-dev \
  liblzma-dev \
  pkg-config \
  cmake \
  ninja-build \
  clang \
  libclang-dev
```

## Vérification

Après installation, vérifiez avec :
```bash
flutter doctor -v
```

## Compilation

Ensuite, réessayez :
```bash
cd esa
flutter clean
flutter pub get
flutter run -d linux
```

## Note sur file_picker

Les avertissements sur `file_picker` pour Linux/macOS/Windows sont normaux et ne bloquent pas la compilation. Ils indiquent simplement que ces plateformes utilisent des implémentations par défaut.

## Si le problème persiste

1. Vérifiez que vous avez les dernières mises à jour :
   ```bash
   flutter upgrade
   ```

2. Vérifiez les dépendances manquantes :
   ```bash
   flutter doctor -v
   ```

3. Essayez de compiler avec plus de détails :
   ```bash
   flutter run -d linux -v
   ```

