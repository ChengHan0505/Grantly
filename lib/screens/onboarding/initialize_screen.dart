import 'dart:ui';

import 'package:flutter/material.dart';

import '../auth/login_screen.dart';
import 'business_fundamentals_screen.dart';

void _showInitializeMessage(BuildContext context, String action) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('$action is ready for integration.'),
      behavior: SnackBarBehavior.floating,
      backgroundColor: const Color(0xFF0F7891),
    ),
  );
}

class InitializeScreen extends StatelessWidget {
  const InitializeScreen({super.key});

  static const String routeName = '/initialize';

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;
    final showSideAccent = screenWidth >= 1180;

    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FB),
      body: Stack(
        children: [
          const Positioned.fill(child: _InitializeBackground()),
          if (showSideAccent)
            const Positioned(left: 60, top: 0, bottom: 0, child: _SideAccent()),
          SafeArea(
            child: Column(
              children: [
                const Padding(
                  padding: EdgeInsets.fromLTRB(20, 12, 20, 0),
                  child: _InitializeNavBar(),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: EdgeInsets.fromLTRB(
                      showSideAccent ? 140 : 20,
                      34,
                      showSideAccent ? 140 : 20,
                      24,
                    ),
                    child: Column(
                      children: [
                        const _ProgressSection(),
                        const SizedBox(height: 18),
                        const _InitializeCard(),
                        const SizedBox(height: 28),
                        const _InitializeFooter(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InitializeBackground extends StatelessWidget {
  const _InitializeBackground();

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: const [
        ColoredBox(color: Color(0xFFF7F9FB)),
        _BackgroundBloom(
          alignment: Alignment.topLeft,
          colors: [Color(0x66E1E0FF), Color(0x00E1E0FF)],
          width: 760,
          height: 760,
          offset: Offset(-150, -80),
        ),
        _BackgroundBloom(
          alignment: Alignment.topCenter,
          colors: [Color(0x80B7EAFF), Color(0x00B7EAFF)],
          width: 840,
          height: 520,
          offset: Offset(0, -60),
        ),
        _BackgroundBloom(
          alignment: Alignment.topRight,
          colors: [Color(0x66FFDCC3), Color(0x00FFDCC3)],
          width: 700,
          height: 760,
          offset: Offset(140, -20),
        ),
        _BackgroundBloom(
          alignment: Alignment.bottomCenter,
          colors: [Color(0x55FFFFFF), Color(0x00FFFFFF)],
          width: 1200,
          height: 700,
          offset: Offset(0, 220),
        ),
      ],
    );
  }
}

class _BackgroundBloom extends StatelessWidget {
  const _BackgroundBloom({
    required this.alignment,
    required this.colors,
    required this.width,
    required this.height,
    required this.offset,
  });

  final Alignment alignment;
  final List<Color> colors;
  final double width;
  final double height;
  final Offset offset;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Transform.translate(
        offset: offset,
        child: IgnorePointer(
          child: Container(
            width: width,
            height: height,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(colors: colors),
            ),
          ),
        ),
      ),
    );
  }
}

class _InitializeNavBar extends StatelessWidget {
  const _InitializeNavBar();

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final compact = width < 720;
    final extraCompact = width < 430;

    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          height: 68,
          padding: EdgeInsets.symmetric(
            horizontal: extraCompact ? 14 : (compact ? 20 : 28),
          ),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.44),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.65)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x12191C1E),
                blurRadius: 42,
                offset: Offset(0, 18),
              ),
            ],
          ),
          child: Row(
            children: [
              const Icon(
                Icons.auto_awesome,
                color: Color(0xFF006780),
                size: 20,
              ),
              SizedBox(width: extraCompact ? 8 : 14),
              Text(
                'Grantly',
                style: TextStyle(
                  fontSize: extraCompact ? 16 : (compact ? 19 : 22),
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF191C1E),
                  letterSpacing: -0.5,
                ),
              ),
              const Spacer(),
              _NavLoginButton(
                onTap: () =>
                    Navigator.pushNamed(context, LoginScreen.routeName),
              ),
              if (!compact) ...[
                const SizedBox(width: 16),
                const _NavCircleIcon(icon: Icons.language, label: 'Language'),
                const SizedBox(width: 12),
                const _NavCircleIcon(
                  icon: Icons.notifications,
                  label: 'Notifications',
                ),
                const SizedBox(width: 14),
                const CircleAvatar(
                  radius: 19,
                  backgroundColor: Color(0xFF1F2126),
                  child: Icon(Icons.person, size: 18, color: Colors.white),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _NavLoginButton extends StatelessWidget {
  const _NavLoginButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 14),
          decoration: BoxDecoration(
            color: const Color(0xFF0F7891),
            borderRadius: BorderRadius.circular(999),
          ),
          child: const Text(
            'Login',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w700,
              fontSize: 16,
            ),
          ),
        ),
      ),
    );
  }
}

class _NavCircleIcon extends StatelessWidget {
  const _NavCircleIcon({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: label,
      child: IconButton(
        onPressed: () => _showInitializeMessage(context, label),
        icon: Icon(icon, size: 20, color: const Color(0xFF64748B)),
        style: IconButton.styleFrom(
          backgroundColor: Colors.white.withValues(alpha: 0.16),
          fixedSize: const Size(34, 34),
          padding: EdgeInsets.zero,
          shape: const CircleBorder(),
        ),
      ),
    );
  }
}

class _ProgressSection extends StatelessWidget {
  const _ProgressSection();

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 800),
      child: Column(
        children: [
          const Row(
            children: [
              Text(
                'STEP 1 OF 3',
                style: TextStyle(
                  fontSize: 14,
                  letterSpacing: 1.8,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF006780),
                ),
              ),
              Spacer(),
              Text(
                '33% Complete',
                style: TextStyle(fontSize: 14, color: Color(0xFF3D494D)),
              ),
            ],
          ),
          const SizedBox(height: 18),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: Container(
              height: 6,
              color: const Color(0xFFD7E3E8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: FractionallySizedBox(
                  widthFactor: 0.33,
                  child: Container(color: const Color(0xFF0F7891)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InitializeCard extends StatelessWidget {
  const _InitializeCard();

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 720;

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 720),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(42),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
          child: Container(
            padding: EdgeInsets.fromLTRB(
              compact ? 24 : 58,
              compact ? 30 : 42,
              compact ? 24 : 58,
              compact ? 32 : 38,
            ),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.74),
              borderRadius: BorderRadius.circular(42),
              border: Border.all(color: Colors.white.withValues(alpha: 0.68)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x10191C1E),
                  blurRadius: 60,
                  offset: Offset(0, 26),
                ),
              ],
            ),
            child: Stack(
              children: [
                const Positioned(
                  top: -100,
                  right: -90,
                  child: _SoftOrb(size: 220, color: Color(0x12006780)),
                ),
                const Positioned(
                  bottom: -110,
                  left: -90,
                  child: _SoftOrb(size: 220, color: Color(0x12494BD6)),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Align(
                      alignment: Alignment.center,
                      child: Text(
                        'Get Started Now',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: compact ? 32 : 38,
                          fontWeight: FontWeight.w800,
                          height: 1,
                          letterSpacing: -1,
                          color: const Color(0xFF191C1E),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Align(
                      alignment: Alignment.center,
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 560),
                        child: Text(
                          "It's easy to create your Grantly workspace. Tell us who you are, secure your account, and we'll prepare your grant roadmap workflow.",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: compact ? 15 : 16,
                            height: 1.55,
                            color: const Color(0xFF3D494D),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(height: compact ? 24 : 30),
                    const _InitializeField(label: 'Full Name *'),
                    const SizedBox(height: 16),
                    const _InitializeField(label: 'Email Address *'),
                    const SizedBox(height: 16),
                    const _InitializeField(
                      label: 'Password *',
                      showVisibility: true,
                    ),
                    const SizedBox(height: 16),
                    const _InitializeField(
                      label: 'Confirm Password *',
                      showVisibility: true,
                    ),
                    const SizedBox(height: 22),
                    const _CertificationRow(),
                    SizedBox(height: compact ? 28 : 34),
                    _ContinueButton(
                      label: 'Create New Account',
                      onTap: () => Navigator.pushNamed(
                        context,
                        BusinessFundamentalsScreen.routeName,
                      ),
                    ),
                    const SizedBox(height: 26),
                    Center(
                      child: Wrap(
                        alignment: WrapAlignment.center,
                        children: [
                          const Text(
                            'Already have an account? ',
                            style: TextStyle(
                              fontSize: 16,
                              color: Color(0xFF3D494D),
                            ),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pushNamed(
                              context,
                              LoginScreen.routeName,
                            ),
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFF006780),
                              padding: EdgeInsets.zero,
                              minimumSize: const Size(0, 0),
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            child: const Text(
                              'Log In',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SoftOrb extends StatelessWidget {
  const _SoftOrb({required this.size, required this.color});

  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
    );
  }
}

class _CertificationRow extends StatefulWidget {
  const _CertificationRow();

  @override
  State<_CertificationRow> createState() => _CertificationRowState();
}

class _CertificationRowState extends State<_CertificationRow> {
  bool _checked = false;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => setState(() => _checked = !_checked),
      borderRadius: BorderRadius.circular(18),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Checkbox(
            value: _checked,
            onChanged: (value) => setState(() => _checked = value ?? false),
            activeColor: const Color(0xFF0F7891),
            side: const BorderSide(color: Color(0xFF6D797E)),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(5),
            ),
          ),
          const SizedBox(width: 8),
          const Expanded(
            child: Text(
              "I certify that I agree to Grantly's Privacy Policy, Terms and Conditions, and Refund Policy; and I understand it is my responsibility to do due diligence on any grant or investor I meet via this platform.",
              style: TextStyle(
                color: Color(0xFF191C1E),
                fontSize: 15,
                height: 1.45,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InitializeField extends StatelessWidget {
  const _InitializeField({required this.label, this.showVisibility = false});

  final String label;
  final bool showVisibility;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 68,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F5),
        borderRadius: BorderRadius.circular(28),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              obscureText: showVisibility,
              decoration: InputDecoration(
                hintText: label,
                hintStyle: const TextStyle(
                  color: Color(0xFF24323B),
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
                border: InputBorder.none,
              ),
              style: const TextStyle(color: Color(0xFF191C1E), fontSize: 16),
            ),
          ),
          if (showVisibility)
            const Icon(
              Icons.visibility_outlined,
              color: Color(0xFF93A4BA),
              size: 22,
            ),
        ],
      ),
    );
  }
}

class _ContinueButton extends StatelessWidget {
  const _ContinueButton({required this.onTap, required this.label});

  final VoidCallback onTap;
  final String label;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final compact = width < 480;

    return SizedBox(
      width: double.infinity,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(999),
          child: Ink(
            padding: EdgeInsets.symmetric(
              horizontal: compact ? 18 : 30,
              vertical: compact ? 12 : 24,
            ),
            decoration: BoxDecoration(
              color: const Color(0xFF0F7891),
              borderRadius: BorderRadius.circular(999),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x33006780),
                  blurRadius: 18,
                  offset: Offset(0, 9),
                ),
              ],
            ),
            child: Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 12,
              children: [
                Text(
                  label,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: compact ? 15 : 19,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Icon(Icons.arrow_forward, color: Colors.white, size: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _InitializeFooter extends StatelessWidget {
  const _InitializeFooter();

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 760;

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 720),
      child: compact
          ? const Column(
              children: [
                _SecurityBadge(),
                SizedBox(height: 14),
                Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 28,
                  runSpacing: 8,
                  children: [
                    _FooterLink('PRIVACY'),
                    _FooterLink('TERMS'),
                    _FooterLink('COMPLIANCE'),
                  ],
                ),
              ],
            )
          : const Row(
              children: [
                _SecurityBadge(),
                Spacer(),
                _FooterLink('PRIVACY'),
                SizedBox(width: 34),
                _FooterLink('TERMS'),
                SizedBox(width: 34),
                _FooterLink('COMPLIANCE'),
              ],
            ),
    );
  }
}

class _SecurityBadge extends StatelessWidget {
  const _SecurityBadge();

  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 12,
      children: const [
        Icon(Icons.verified_user_rounded, color: Color(0xFF75A9B6), size: 24),
        Text(
          'Enterprise-Grade Security Protocol',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 14,
            color: Color(0xFF5B6770),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _FooterLink extends StatelessWidget {
  const _FooterLink(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: const TextStyle(
        fontSize: 14,
        color: Color(0xFF6B7280),
        fontWeight: FontWeight.w700,
        letterSpacing: 0.7,
      ),
    );
  }
}

class _SideAccent extends StatelessWidget {
  const _SideAccent();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: 180,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 60,
              height: 5,
              decoration: BoxDecoration(
                color: const Color(0xFFA5C8DB),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(height: 12),
            Container(
              width: 120,
              height: 5,
              decoration: BoxDecoration(
                color: const Color(0xFFB8B7F4),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(height: 12),
            Container(
              width: 80,
              height: 5,
              decoration: BoxDecoration(
                color: const Color(0xFFB7EAFF),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(height: 64),
            Container(width: 1, height: 116, color: const Color(0x33BCC9CE)),
            const SizedBox(height: 22),
            const Text(
              'EMPOWERING THE\nNEXT WAVE OF\nNON-PROFIT IMPACT.',
              style: TextStyle(
                fontSize: 13,
                height: 1.9,
                letterSpacing: 2.2,
                fontWeight: FontWeight.w800,
                color: Color(0xFF006780),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
