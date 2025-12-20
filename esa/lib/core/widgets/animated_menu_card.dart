import 'package:flutter/material.dart';
import '../theme/app_theme_enhanced.dart';
import 'asset_icon.dart';
import 'fade_in_widget.dart';

/// Carte de menu améliorée avec animations
class AnimatedMenuCard extends StatefulWidget {
  final String title;
  final IconData? icon;
  final String? assetPath;
  final Color color;
  final VoidCallback onTap;
  final int index;
  final Gradient? gradient;

  const AnimatedMenuCard({
    super.key,
    required this.title,
    required this.color,
    required this.onTap,
    required this.index,
    this.icon,
    this.assetPath,
    this.gradient,
  }) : assert(icon != null || assetPath != null, 'Either icon or assetPath must be provided');

  @override
  State<AnimatedMenuCard> createState() => _AnimatedMenuCardState();
}

class _AnimatedMenuCardState extends State<AnimatedMenuCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: AppThemeEnhanced.fastAnimation,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: AppThemeEnhanced.smoothCurve),
    );
    _rotationAnimation = Tween<double>(begin: 0.0, end: 0.05).animate(
      CurvedAnimation(parent: _controller, curve: AppThemeEnhanced.smoothCurve),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    setState(() => _isPressed = true);
    _controller.forward();
  }

  void _handleTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
    _controller.reverse();
    widget.onTap();
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return FadeInWidget(
      delay: Duration(milliseconds: widget.index * 100),
      child: GestureDetector(
        onTapDown: _handleTapDown,
        onTapUp: _handleTapUp,
        onTapCancel: _handleTapCancel,
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Transform.rotate(
                angle: _rotationAnimation.value,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: widget.gradient ??
                        LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            widget.color,
                            widget.color.withOpacity(0.8),
                          ],
                        ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: widget.color.withOpacity(0.3),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                        spreadRadius: 0,
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: widget.onTap,
                      borderRadius: BorderRadius.circular(20),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                shape: BoxShape.circle,
                              ),
                              child: widget.assetPath != null
                                  ? AssetIcon(
                                      assetPath: widget.assetPath!,
                                      size: 32,
                                      color: Colors.white,
                                    )
                                  : Icon(
                                      widget.icon,
                                      size: 32,
                                      color: Colors.white,
                                    ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              widget.title,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.5,
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
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

