// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/app.dart';
import 'package:frontend/screens/landing/landing_screen.dart';

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
}
