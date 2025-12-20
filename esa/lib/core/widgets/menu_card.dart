import 'package:flutter/material.dart';
import 'asset_icon.dart';

/// Widget de carte de menu avec support pour assets ou icônes Material
class MenuCard extends StatelessWidget {
  final String title;
  final IconData? icon;
  final String? assetPath;
  final Color color;
  final VoidCallback onTap;

  const MenuCard({
    super.key,
    required this.title,
    required this.color,
    required this.onTap,
    this.icon,
    this.assetPath,
  }) : assert(icon != null || assetPath != null, 'Either icon or assetPath must be provided');

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (assetPath != null)
                AssetIcon(
                  assetPath: assetPath!,
                  size: 40,
                  color: color,
                )
              else if (icon != null)
                Icon(icon, size: 40, color: color),
              const SizedBox(height: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

