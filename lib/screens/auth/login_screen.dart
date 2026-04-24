import 'dart:ui';

import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';
import '../landing/landing_screen.dart';
import '../onboarding/initialize_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  static const String routeName = '/login';

  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.of(context).size.width >= 1024;

    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FB),
      body: Stack(
        children: [
          Positioned.fill(child: _LoginBackground(showDesktopPane: isWide)),
          SafeArea(
            child: Stack(
              children: [
                Positioned(
                  top: 20,
                  left: 20,
                  child: _BackButton(
                    onTap: () => Navigator.pushNamedAndRemoveUntil(
                      context,
                      LandingScreen.routeName,
                      (_) => false,
                    ),
                  ),
                ),
                Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 1320),
                    child: Row(
                      children: [
                        if (isWide) const Expanded(flex: 5, child: _LeftPane()),
                        Expanded(
                          flex: isWide ? 7 : 12,
                          child: Padding(
                            padding: EdgeInsets.symmetric(
                              horizontal: isWide ? 64 : 20,
                              vertical: 24,
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                ConstrainedBox(
                                  constraints: const BoxConstraints(maxWidth: 460),
                                  child: const _LoginCard(),
                                ),
                                const SizedBox(height: 38),
                                const _RegisterLink(),
                              ],
                            ),
                          ),
                        ),
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

class _LoginBackground extends StatelessWidget {
  const _LoginBackground({required this.showDesktopPane});

  final bool showDesktopPane;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        if (showDesktopPane)
          Expanded(
            flex: 5,
            child: Stack(
              fit: StackFit.expand,
              children: const [
                ColoredBox(color: Color(0xFFECEEF0)),
                _MeshLayer(opacity: 0.9),
                DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [Color(0x00F7F9FB), Color(0xCCF7F9FB)],
                    ),
                  ),
                ),
              ],
            ),
          ),
        Expanded(
          flex: showDesktopPane ? 7 : 12,
          child: Stack(
            fit: StackFit.expand,
            children: const [
              ColoredBox(color: Color(0xFFF7F9FB)),
              _MeshLayer(opacity: 0.18),
            ],
          ),
        ),
      ],
    );
  }
}

class _MeshLayer extends StatelessWidget {
  const _MeshLayer({required this.opacity});

  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: opacity,
      child: Stack(
        children: const [
          _GlowBlob(
            left: 0.42,
            top: 0.20,
            width: 420,
            height: 300,
            colors: [Color(0x80006780), Color(0x00006780)],
          ),
          _GlowBlob(
            left: 0.80,
            top: 0.02,
            width: 360,
            height: 280,
            colors: [Color(0x6645B1D4), Color(0x0045B1D4)],
          ),
          _GlowBlob(
            left: 0.02,
            top: 0.48,
            width: 380,
            height: 320,
            colors: [Color(0x66494BD6), Color(0x00494BD6)],
          ),
          _GlowBlob(
            left: 0.78,
            top: 0.50,
            width: 300,
            height: 260,
            colors: [Color(0x40FE932C), Color(0x00FE932C)],
          ),
          _GlowBlob(
            left: 0.02,
            top: 0.95,
            width: 420,
            height: 320,
            colors: [Color(0x73006780), Color(0x00006780)],
          ),
          _GlowBlob(
            left: 0.78,
            top: 0.96,
            width: 360,
            height: 280,
            colors: [Color(0x5545B1D4), Color(0x0045B1D4)],
          ),
        ],
      ),
    );
  }
}

class _GlowBlob extends StatelessWidget {
  const _GlowBlob({
    required this.left,
    required this.top,
    required this.width,
    required this.height,
    required this.colors,
  });

  final double left;
  final double top;
  final double width;
  final double height;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    return FractionalTranslation(
      translation: Offset(left, top),
      child: IgnorePointer(
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: colors,
              radius: 0.7,
              center: Alignment.topLeft,
            ),
          ),
        ),
      ),
    );
  }
}

class _LeftPane extends StatelessWidget {
  const _LeftPane();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(56, 80, 34, 74),
      child: Align(
        alignment: Alignment.bottomLeft,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'The Intelligent',
              style: TextStyle(
                fontSize: 70,
                fontWeight: FontWeight.w800,
                color: AppTheme.ink,
                height: 0.92,
                letterSpacing: -1.6,
              ),
            ),
            const _EtherGradientText(),
            const SizedBox(height: 20),
            const SizedBox(
              width: 560,
              child: Text(
                'Weave data into narrative. Dissolve the friction\n'
                'between insight and impact.',
                style: TextStyle(
                  fontSize: 35,
                  color: Color(0xFF3D494D),
                  height: 1.35,
                  letterSpacing: -0.2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BackButton extends StatelessWidget {
  const _BackButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.82),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: const Color(0x26BCC9CE)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0F191C1E),
                blurRadius: 34,
                offset: Offset(0, 16),
              ),
            ],
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.arrow_back, size: 18, color: Color(0xFF006780)),
              SizedBox(width: 10),
              Text(
                'Return to Home',
                style: TextStyle(
                  color: Color(0xFF006780),
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LoginCard extends StatelessWidget {
  const _LoginCard();

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(38),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 38, vertical: 40),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.8),
            borderRadius: BorderRadius.circular(38),
            border: Border.all(color: const Color(0x4DBCC9CE)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0F191C1E),
                blurRadius: 60,
                offset: Offset(0, 40),
                spreadRadius: -5,
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Grant Copilot',
                style: TextStyle(
                  fontSize: 50,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF191C1E),
                  letterSpacing: -1.3,
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Enter your credentials to access the workspace.',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF3D494D),
                  height: 1.25,
                ),
              ),
              const SizedBox(height: 28),
              const _GhostField(
                label: 'EMAIL ADDRESS',
                hint: 'jane@example.com',
              ),
              const SizedBox(height: 14),
              const _GhostField(
                label: 'PASSWORD',
                hint: '••••••••',
                forgotText: 'Forgot?',
                obscure: true,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: Checkbox(
                      value: false,
                      onChanged: (_) {},
                      side: const BorderSide(color: Color(0x4DBCC9CE)),
                      fillColor: WidgetStateProperty.resolveWith(
                        (states) => states.contains(WidgetState.selected)
                            ? const Color(0xFF006780)
                            : const Color(0xFFF2F4F6),
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(5),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  const Text(
                    'Remember me on this device',
                    style: TextStyle(fontSize: 14, color: Color(0xFF3D494D)),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              SizedBox(
                width: double.infinity,
                child: _ActionButton(
                  label: 'Access Workspace',
                  onTap: () =>
                      Navigator.pushNamed(context, InitializeScreen.routeName),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  const Expanded(child: Divider(color: Color(0x33BCC9CE))),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Text(
                      'OR',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ),
                  const Expanded(child: Divider(color: Color(0x33BCC9CE))),
                ],
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () =>
                      Navigator.pushNamed(context, InitializeScreen.routeName),
                  icon: const Icon(
                    Icons.g_mobiledata_rounded,
                    size: 26,
                    color: Color(0xFF191C1E),
                  ),
                  label: const Padding(
                    padding: EdgeInsets.symmetric(vertical: 13),
                    child: Text(
                      'Continue with Google',
                      style: TextStyle(
                        fontSize: 14,
                        color: Color(0xFF191C1E),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    backgroundColor: const Color(0xFFF2F4F6),
                    side: const BorderSide(color: Color(0x1ABCC9CE)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(999),
                    ),
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

class _GhostField extends StatelessWidget {
  const _GhostField({
    required this.label,
    required this.hint,
    this.forgotText,
    this.obscure = false,
  });

  final String label;
  final String hint;
  final String? forgotText;
  final bool obscure;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(
        color: const Color(0x14FFFFFF),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0x26BCC9CE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (forgotText == null)
            Text(
              label,
              style: const TextStyle(
                color: Color(0xFF3D494D),
                fontSize: 11,
                letterSpacing: 1.1,
                fontWeight: FontWeight.w700,
              ),
            )
          else
            Row(
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    color: Color(0xFF3D494D),
                    fontSize: 11,
                    letterSpacing: 1.1,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {},
                  style: TextButton.styleFrom(
                    padding: EdgeInsets.zero,
                    minimumSize: const Size(0, 0),
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: Text(
                    forgotText!,
                    style: const TextStyle(
                      color: Color(0xFF006780),
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          TextField(
            obscureText: obscure,
            decoration: InputDecoration(
              hintText: hint,
              isDense: true,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.only(top: 2),
              hintStyle: const TextStyle(
                color: Color(0x80BCC9CE),
                fontSize: 16,
              ),
            ),
            style: const TextStyle(fontSize: 16, color: Color(0xFF191C1E)),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(100),
        child: Ink(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [Color(0xFF006780), Color(0xFF45B1D4)],
            ),
            borderRadius: BorderRadius.circular(100),
            boxShadow: const [
              BoxShadow(
                color: Color(0x33006780),
                blurRadius: 16,
                offset: Offset(0, 8),
              ),
            ],
          ),
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }
}

class _RegisterLink extends StatelessWidget {
  const _RegisterLink();

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () => Navigator.pushNamed(context, InitializeScreen.routeName),
      style: TextButton.styleFrom(
        foregroundColor: const Color(0xFF904D00),
        textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Register for Node Initialization'),
          SizedBox(width: 6),
          Icon(Icons.arrow_forward, size: 16),
        ],
      ),
    );
  }
}

class _EtherGradientText extends StatelessWidget {
  const _EtherGradientText();

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      blendMode: BlendMode.srcIn,
      shaderCallback: (bounds) => const LinearGradient(
        colors: [Color(0xFF006780), Color(0xFF494BD6)],
      ).createShader(bounds),
      child: const Text(
        'Ether.',
        style: TextStyle(
          fontSize: 70,
          fontWeight: FontWeight.w800,
          height: 0.95,
          letterSpacing: -1.4,
        ),
      ),
    );
  }
}
