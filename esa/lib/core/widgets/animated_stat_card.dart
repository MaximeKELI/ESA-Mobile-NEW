import 'package:flutter/material.dart';
import '../theme/app_theme_enhanced.dart';
import 'asset_icon.dart';
import 'fade_in_widget.dart';

/// Carte de statistique animée
class AnimatedStatCard extends StatefulWidget {
  final String title;
  final String value;
  final String? assetPath;
  final IconData? icon;
  final Color color;
  final int index;
  final VoidCallback? onTap;

  const AnimatedStatCard({
    super.key,
    required this.title,
    required this.value,
    required this.color,
    required this.index,
    this.assetPath,
    this.icon,
    this.onTap,
  });

  @override
  State<AnimatedStatCard> createState() => _AnimatedStatCardState();
}

class _AnimatedStatCardState extends State<AnimatedStatCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _valueAnimation;
  bool _hasAnimated = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _valueAnimation = Tween<double>(begin: 0.0, end: double.tryParse(widget.value.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 0.0).animate(
      CurvedAnimation(parent: _controller, curve: AppThemeEnhanced.smoothCurve),
    );
    
    // Démarrer l'animation après un délai
    Future.delayed(Duration(milliseconds: widget.index * 150), () {
      if (mounted) {
        _controller.forward();
        _hasAnimated = true;
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String _formatValue(double value) {
    if (widget.value.contains('%')) {
      return '${value.toInt()}%';
    }
    return value.toInt().toString();
  }

  @override
  Widget build(BuildContext context) {
    return FadeInWidget(
      delay: Duration(milliseconds: widget.index * 100),
      child: Card(
        elevation: 6,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: InkWell(
          onTap: widget.onTap,
          borderRadius: BorderRadius.circular(20),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Colors.white,
                  widget.color.withOpacity(0.05),
                ],
              ),
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: widget.color.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: widget.assetPath != null
                      ? AssetIcon(
                          assetPath: widget.assetPath!,
                          size: 32,
                          color: widget.color,
                        )
                      : Icon(
                          widget.icon ?? Icons.info,
                          size: 32,
                          color: widget.color,
                        ),
                ),
                const SizedBox(height: 16),
                AnimatedBuilder(
                  animation: _valueAnimation,
                  builder: (context, child) {
                    return Text(
                      _hasAnimated ? _formatValue(_valueAnimation.value) : '0',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: widget.color,
                        letterSpacing: -1,
                      ),
                    );
                  },
                ),
                const SizedBox(height: 8),
                Text(
                  widget.title,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppThemeEnhanced.textSecondary,
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
      ),
    );
  }
}

