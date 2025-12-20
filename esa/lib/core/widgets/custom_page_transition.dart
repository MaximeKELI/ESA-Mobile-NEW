import 'package:flutter/material.dart';
import '../theme/app_theme_enhanced.dart';

/// Transition personnalisée avec fade et slide
class FadeUpwardsPageTransitionsBuilder extends PageTransitionsBuilder {
  const FadeUpwardsPageTransitionsBuilder();

  @override
  Widget buildTransitions<T extends Object?>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.0, 0.1),
          end: Offset.zero,
        ).animate(
          CurvedAnimation(
            parent: animation,
            curve: AppThemeEnhanced.smoothCurve,
          ),
        ),
        child: child,
      ),
    );
  }
}

/// Transition avec scale et fade
class ScalePageTransitionsBuilder extends PageTransitionsBuilder {
  const ScalePageTransitionsBuilder();

  @override
  Widget buildTransitions<T extends Object?>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: animation,
      child: ScaleTransition(
        scale: Tween<double>(
          begin: 0.9,
          end: 1.0,
        ).animate(
          CurvedAnimation(
            parent: animation,
            curve: AppThemeEnhanced.smoothCurve,
          ),
        ),
        child: child,
      ),
    );
  }
}

