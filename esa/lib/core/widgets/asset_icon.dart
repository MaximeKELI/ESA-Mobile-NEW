import 'package:flutter/material.dart';

/// Widget réutilisable pour afficher une icône depuis les assets
class AssetIcon extends StatelessWidget {
  final String assetPath;
  final double? size;
  final Color? color;
  final BoxFit fit;

  const AssetIcon({
    super.key,
    required this.assetPath,
    this.size,
    this.color,
    this.fit = BoxFit.contain,
  });

  /// Vérifie si le fichier est un GIF
  bool get _isGif => assetPath.toLowerCase().endsWith('.gif');

  @override
  Widget build(BuildContext context) {
    // Pour les GIFs, ne pas utiliser le paramètre color (désactive l'animation)
    if (_isGif) {
      return Image.asset(
        assetPath,
        width: size ?? 24,
        height: size ?? 24,
        fit: fit,
        // Pas de color pour préserver l'animation
        errorBuilder: (context, error, stackTrace) {
          return Icon(
            Icons.image_not_supported,
            size: size ?? 24,
            color: color ?? Colors.grey,
          );
        },
      );
    }
    
    // Pour les autres formats (PNG, JPEG), on peut utiliser color
    return Image.asset(
      assetPath,
      width: size ?? 24,
      height: size ?? 24,
      fit: fit,
      color: color,
      errorBuilder: (context, error, stackTrace) {
        return Icon(
          Icons.image_not_supported,
          size: size ?? 24,
          color: color ?? Colors.grey,
        );
      },
    );
  }
}

/// Widget spécialisé pour afficher des GIFs animés
class AnimatedGifIcon extends StatelessWidget {
  final String assetPath;
  final double? size;
  final BoxFit fit;

  const AnimatedGifIcon({
    super.key,
    required this.assetPath,
    this.size,
    this.fit = BoxFit.contain,
  });

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      assetPath,
      width: size ?? 24,
      height: size ?? 24,
      fit: fit,
      // Ne pas utiliser color pour préserver l'animation
      errorBuilder: (context, error, stackTrace) {
        return Icon(
          Icons.animation,
          size: size ?? 24,
          color: Colors.grey,
        );
      },
    );
  }
}

/// Widget pour afficher une icône avec un badge (ex: notifications)
class AssetIconWithBadge extends StatelessWidget {
  final String assetPath;
  final double? size;
  final Color? color;
  final int? badgeCount;
  final Color badgeColor;

  const AssetIconWithBadge({
    super.key,
    required this.assetPath,
    this.size,
    this.color,
    this.badgeCount,
    this.badgeColor = Colors.red,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        AssetIcon(
          assetPath: assetPath,
          size: size,
          color: color,
        ),
        if (badgeCount != null && badgeCount! > 0)
          Positioned(
            right: -8,
            top: -8,
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: badgeColor,
                shape: BoxShape.circle,
              ),
              constraints: const BoxConstraints(
                minWidth: 16,
                minHeight: 16,
              ),
              child: Text(
                badgeCount! > 99 ? '99+' : badgeCount.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
      ],
    );
  }
}

