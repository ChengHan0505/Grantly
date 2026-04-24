import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/app.dart';
import 'package:frontend/screens/landing/landing_screen.dart';
import 'package:frontend/screens/onboarding/business_fundamentals_screen.dart';
import 'package:frontend/screens/onboarding/document_vault_screen.dart';
import 'package:frontend/screens/onboarding/initialize_screen.dart';

void main() {
  testWidgets('renders landing headline', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1400, 1600);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const GrantlyApp());
    await tester.pumpAndSettle();

    expect(find.byType(LandingScreen), findsOneWidget);
    expect(find.text('Grant Copilot'), findsOneWidget);
    expect(
      find.text('Ready to transform your grant workflow?'),
      findsOneWidget,
    );
  });

  testWidgets('onboarding pages stay stable on a phone-sized viewport', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    Future<void> pumpScreen(Widget screen) async {
      await tester.pumpWidget(
        MaterialApp(
          home: screen,
          builder: (context, child) => MediaQuery(
            data: MediaQuery.of(
              context,
            ).copyWith(textScaler: const TextScaler.linear(1.0)),
            child: child ?? const SizedBox.shrink(),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    }

    await pumpScreen(const InitializeScreen());
    expect(find.byType(InitializeScreen), findsOneWidget);

    await pumpScreen(const BusinessFundamentalsScreen());
    expect(find.byType(BusinessFundamentalsScreen), findsOneWidget);

    await pumpScreen(const DocumentVaultScreen());
    expect(find.byType(DocumentVaultScreen), findsOneWidget);
  });
}
