import 'package:flutter/material.dart';

import 'core/app_config.dart';
import 'screens/auth/login_screen.dart';
import 'screens/dashboard/dashboard_shell_screen.dart';
import 'screens/landing/landing_screen.dart';
import 'screens/onboarding/business_fundamentals_screen.dart';
import 'screens/onboarding/document_vault_screen.dart';
import 'screens/onboarding/initialize_screen.dart';
import 'theme/app_theme.dart';

class GrantlyApp extends StatelessWidget {
  const GrantlyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Grantly',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.themeData,
      initialRoute: LandingScreen.routeName,
      routes: {
        LandingScreen.routeName: (_) => const LandingScreen(),
        LoginScreen.routeName: (_) => const LoginScreen(),
        InitializeScreen.routeName: (_) => const InitializeScreen(),
        BusinessFundamentalsScreen.routeName: (_) =>
            const BusinessFundamentalsScreen(),
        DocumentVaultScreen.routeName: (_) => const DocumentVaultScreen(),
        DashboardShellScreen.routeName: (_) => const DashboardShellScreen(),
      },
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(
            context,
          ).copyWith(textScaler: const TextScaler.linear(1.0)),
          child: child ?? const SizedBox.shrink(),
        );
      },
      onUnknownRoute: (_) => MaterialPageRoute<void>(
        builder: (_) =>
            const Scaffold(body: Center(child: Text('Unknown route.'))),
      ),
    );
  }
}

class AppEnvironmentBanner extends StatelessWidget {
  const AppEnvironmentBanner({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    if (AppConfig.environment == 'prod') {
      return child;
    }
    return Banner(
      message: AppConfig.environment.toUpperCase(),
      location: BannerLocation.topStart,
      color: Colors.teal.shade700,
      child: child,
    );
  }
}
