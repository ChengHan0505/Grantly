import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';
import 'business_fundamentals_screen.dart';

class InitializeScreen extends StatelessWidget {
  const InitializeScreen({super.key});

  static const String routeName = '/initialize';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFE9F4FF), Color(0xFFFDFBFF), Color(0xFFF6F2EA)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const _NavBar(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(32, 20, 32, 24),
                  child: Column(
                    children: [
                      const _StepHeader(step: 1, progressLabel: '33% Complete'),
                      const SizedBox(height: 12),
                      _StepOneCard(
                        onNext: () => Navigator.pushNamed(context, BusinessFundamentalsScreen.routeName),
                      ),
                      const SizedBox(height: 24),
                      const _Footer(),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StepOneCard extends StatelessWidget {
  const _StepOneCard({required this.onNext});

  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(maxWidth: 900),
      padding: const EdgeInsets.fromLTRB(52, 44, 52, 36),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(34),
        border: Border.all(color: const Color(0xFFE3EAF3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Initialize Your Copilot',
            style: TextStyle(fontSize: 62, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          const Text(
            "Let's set up your secure workspace to start drafting\nyour first proposal.",
            style: TextStyle(fontSize: 31, color: AppTheme.mutedInk, height: 1.35),
          ),
          const SizedBox(height: 24),
          const TextField(decoration: InputDecoration(hintText: 'Full Name')),
          const SizedBox(height: 16),
          const TextField(decoration: InputDecoration(hintText: 'Work Email')),
          const SizedBox(height: 16),
          TextField(
            decoration: InputDecoration(
              hintText: 'Create Password',
              suffixIcon: Icon(Icons.visibility_outlined, color: Colors.blueGrey.shade200),
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: InkWell(
              onTap: onNext,
              borderRadius: BorderRadius.circular(999),
              child: Ink(
                decoration: AppTheme.gradientButton,
                padding: const EdgeInsets.symmetric(vertical: 20),
                child: const Text(
                  'Continue to Company Setup   ->',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 28, color: Colors.white, fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Center(
            child: TextButton(
              onPressed: () {},
              child: const Text(
                'Already have an account? Log In',
                style: TextStyle(fontSize: 23),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NavBar extends StatelessWidget {
  const _NavBar();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: Row(
        children: const [
          Icon(Icons.auto_awesome, size: 18, color: Color(0xFF1F9CB5)),
          SizedBox(width: 8),
          Text('Grantly', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          Spacer(),
          _NavPill('Login'),
          SizedBox(width: 12),
          Icon(Icons.language, size: 18),
          SizedBox(width: 12),
          Icon(Icons.notifications_none, size: 18),
          SizedBox(width: 12),
          CircleAvatar(radius: 14, backgroundColor: Color(0xFF121212)),
        ],
      ),
    );
  }
}

class _NavPill extends StatelessWidget {
  const _NavPill(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: AppTheme.gradientButton,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 9),
      child: Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
    );
  }
}

class _StepHeader extends StatelessWidget {
  const _StepHeader({required this.step, required this.progressLabel});

  final int step;
  final String progressLabel;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 900),
      child: Column(
        children: [
          Row(
            children: [
              Text('STEP $step OF 3', style: const TextStyle(fontWeight: FontWeight.w700)),
              const Spacer(),
              Text(progressLabel),
            ],
          ),
          const SizedBox(height: 8),
          Stack(
            children: [
              Container(
                height: 5,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(99),
                  color: const Color(0xFFD8E4EF),
                ),
              ),
              FractionallySizedBox(
                widthFactor: 0.33,
                child: Container(
                  height: 5,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(99),
                    color: AppTheme.accentTeal,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  const _Footer();

  @override
  Widget build(BuildContext context) {
    return const Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.verified_user_outlined, size: 18, color: Color(0xFF7594A2)),
        SizedBox(width: 6),
        Text('Enterprise-Grade Security Protocol'),
        SizedBox(width: 32),
        Text('PRIVACY'),
        SizedBox(width: 18),
        Text('TERMS'),
        SizedBox(width: 18),
        Text('COMPLIANCE'),
      ],
    );
  }
}
