import 'package:flutter/material.dart';

class AppTheme {
  static const Color ink = Color(0xFF0E1320);
  static const Color mutedInk = Color(0xFF566070);
  static const Color panel = Color(0xFFF8FAFC);
  static const Color card = Color(0xFFFFFFFF);
  static const Color accentTeal = Color(0xFF0D7B93);
  static const Color accentBlue = Color(0xFF39B8ED);
  static const Color line = Color(0xFFDCE3EC);

  static final ThemeData themeData = ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: const Color(0xFFF3F6FB),
    colorScheme: ColorScheme.fromSeed(
      seedColor: accentTeal,
      primary: accentTeal,
      secondary: accentBlue,
      brightness: Brightness.light,
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontSize: 54,
        fontWeight: FontWeight.w700,
        letterSpacing: -1.2,
        color: ink,
      ),
      headlineMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: ink,
      ),
      titleLarge: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w700,
        color: ink,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        height: 1.45,
        color: ink,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        height: 1.4,
        color: mutedInk,
      ),
      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: ink,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFFF3F5F8),
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide.none,
      ),
      hintStyle: const TextStyle(
        color: Color(0xFF9AA4B2),
        fontSize: 14,
      ),
    ),
  );

  static BoxDecoration gradientButton = BoxDecoration(
    gradient: const LinearGradient(
      begin: Alignment.centerLeft,
      end: Alignment.centerRight,
      colors: [accentTeal, accentBlue],
    ),
    borderRadius: BorderRadius.circular(999),
    boxShadow: const [
      BoxShadow(
        color: Color(0x330D7B93),
        blurRadius: 14,
        offset: Offset(0, 6),
      ),
    ],
  );
}
