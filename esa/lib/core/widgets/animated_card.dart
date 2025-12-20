import 'package:flutter/material.dart';
import '../theme/app_theme_enhanced.dart';

/// Carte animée avec effet de hover et shadow
class AnimatedCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final Color? color;
  final double? elevation;
  final BorderRadius? borderRadius;
  final Duration animationDuration;
  final bool enableHover;

  const AnimatedCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding,
    this.color,
    this.elevation,
    this.borderRadius,
    this.animationDuration = AppThemeEnhanced.normalAnimation,
    this.enableHover = true,
  });

  @override
  State<AnimatedCard> createState() => _AnimatedCardState();
}

class _AnimatedCardState extends State<AnimatedCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _elevationAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.02).animate(
      CurvedAnimation(parent: _controller, curve: AppThemeEnhanced.smoothCurve),
    );
    _elevationAnimation = Tween<double>(
      begin: widget.elevation ?? 4.0,
      end: (widget.elevation ?? 4.0) + 4.0,
    ).animate(
      CurvedAnimation(parent: _controller, curve: AppThemeEnhanced.smoothCurve),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    if (widget.enableHover) {
      _controller.forward();
    }
  }

  void _handleTapUp(TapUpDetails details) {
    if (widget.enableHover) {
      _controller.reverse();
    }
    widget.onTap?.call();
  }

  void _handleTapCancel() {
    if (widget.enableHover) {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: widget.onTap != null ? _handleTapDown : null,
      onTapUp: widget.onTap != null ? _handleTapUp : null,
      onTapCancel: widget.onTap != null ? _handleTapCancel : null,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Card(
              color: widget.color,
              elevation: _elevationAnimation.value,
              shape: RoundedRectangleBorder(
                borderRadius: widget.borderRadius ?? BorderRadius.circular(16),
              ),
              child: Padding(
                padding: widget.padding ?? const EdgeInsets.all(16),
                child: widget.child,
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Carte avec gradient animé
class GradientCard extends StatelessWidget {
  final Widget child;
  final Gradient gradient;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final BorderRadius? borderRadius;

  const GradientCard({
    super.key,
    required this.child,
    required this.gradient,
    this.onTap,
    this.padding,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedCard(
      onTap: onTap,
      padding: EdgeInsets.zero,
      borderRadius: borderRadius ?? BorderRadius.circular(16),
      child: Container(
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: borderRadius ?? BorderRadius.circular(16),
        ),
        padding: padding ?? const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}

