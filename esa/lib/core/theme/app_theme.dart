import 'package:flutter/material.dart';

/// Thème de l'application ESA
class AppTheme {
  // Couleurs principales
  static const Color primaryColor = Color(0xFF1a237e); // Bleu foncé ESA
  static const Color secondaryColor = Color(0xFF3949ab);
  static const Color accentColor = Color(0xFF5c6bc0);
  static const Color errorColor = Color(0xFFd32f2f);
  static const Color successColor = Color(0xFF388e3c);
  static const Color warningColor = Color(0xFFf57c00);
  static const Color infoColor = Color(0xFF1976d2);
  
  // Couleurs de fond
  static const Color backgroundColor = Color(0xFFf5f5f5);
  static const Color surfaceColor = Colors.white;
  static const Color cardColor = Colors.white;
  
  // Couleurs de texte
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color textDisabled = Color(0xFFbdbdbd);
  
  // Thème clair
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primaryColor,
    colorScheme: const ColorScheme.light(
      primary: primaryColor,
      secondary: secondaryColor,
      error: errorColor,
      surface: surfaceColor,
      background: backgroundColor,
    ),
    scaffoldBackgroundColor: backgroundColor,
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryColor,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        color: Colors.white,
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
    ),
    cardTheme: CardTheme(
      color: cardColor,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        elevation: 2,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: Colors.grey),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: Colors.grey),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: errorColor),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(color: textPrimary, fontSize: 32, fontWeight: FontWeight.bold),
      displayMedium: TextStyle(color: textPrimary, fontSize: 28, fontWeight: FontWeight.bold),
      displaySmall: TextStyle(color: textPrimary, fontSize: 24, fontWeight: FontWeight.bold),
      headlineMedium: TextStyle(color: textPrimary, fontSize: 20, fontWeight: FontWeight.w600),
      titleLarge: TextStyle(color: textPrimary, fontSize: 18, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(color: textPrimary, fontSize: 16, fontWeight: FontWeight.w500),
      bodyLarge: TextStyle(color: textPrimary, fontSize: 16),
      bodyMedium: TextStyle(color: textPrimary, fontSize: 14),
      bodySmall: TextStyle(color: textSecondary, fontSize: 12),
    ),
    iconTheme: const IconThemeData(
      color: primaryColor,
      size: 24,
    ),
  );
  
  // Thème sombre (optionnel)
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: accentColor,
    colorScheme: const ColorScheme.dark(
      primary: accentColor,
      secondary: secondaryColor,
      error: errorColor,
      surface: Color(0xFF1e1e1e),
      background: Color(0xFF121212),
    ),
    scaffoldBackgroundColor: const Color(0xFF121212),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF1e1e1e),
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
    ),
  );
}

