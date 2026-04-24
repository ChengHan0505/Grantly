import 'dart:ui';

import 'package:flutter/material.dart';

import '../auth/login_screen.dart';
import '../dashboard/dashboard_shell_screen.dart';
import 'business_fundamentals_screen.dart';

class DocumentVaultScreen extends StatelessWidget {
  const DocumentVaultScreen({super.key});

  static const String routeName = '/document-vault';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4FAFF),
      body: Stack(
        children: [
          const Positioned.fill(child: _VaultBackground()),
          SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                  child: _VaultTopBar(
                    onLogin: () =>
                        Navigator.pushNamed(context, LoginScreen.routeName),
                  ),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 34, 20, 32),
                    child: Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 1220),
                        child: Column(
                          children: [
                            const _VaultProgressHeader(),
                            const SizedBox(height: 40),
                            const _VaultHero(),
                            const SizedBox(height: 42),
                            const _VaultGrid(),
                            const SizedBox(height: 34),
                            const Divider(color: Color(0x1ABCC9CE), height: 1),
                            const SizedBox(height: 26),
                            _VaultFooter(
                              onBack: () => Navigator.pushNamed(
                                context,
                                BusinessFundamentalsScreen.routeName,
                              ),
                              onSubmit: () => Navigator.pushNamedAndRemoveUntil(
                                context,
                                DashboardShellScreen.routeName,
                                (_) => false,
                              ),
                            ),
                          ],
                        ),
                      ),
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

class _VaultBackground extends StatelessWidget {
  const _VaultBackground();

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: const [
        ColoredBox(color: Color(0xFFF4FAFF)),
        _VaultOrb(
          alignment: Alignment.topLeft,
          width: 720,
          height: 720,
          offset: Offset(-140, -160),
          colors: [Color(0x66FFFFFF), Color(0x00FFFFFF)],
        ),
        _VaultOrb(
          alignment: Alignment.topRight,
          width: 680,
          height: 680,
          offset: Offset(180, -60),
          colors: [Color(0x40E0F2FE), Color(0x00E0F2FE)],
        ),
        _VaultOrb(
          alignment: Alignment.bottomRight,
          width: 820,
          height: 820,
          offset: Offset(200, 180),
          colors: [Color(0x33BAE6FD), Color(0x00BAE6FD)],
        ),
        _VaultOrb(
          alignment: Alignment.bottomLeft,
          width: 720,
          height: 720,
          offset: Offset(-120, 180),
          colors: [Color(0x55FFFFFF), Color(0x00FFFFFF)],
        ),
      ],
    );
  }
}

class _VaultOrb extends StatelessWidget {
  const _VaultOrb({
    required this.alignment,
    required this.width,
    required this.height,
    required this.offset,
    required this.colors,
  });

  final Alignment alignment;
  final double width;
  final double height;
  final Offset offset;
  final List<Color> colors;

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

class _VaultTopBar extends StatelessWidget {
  const _VaultTopBar({required this.onLogin});

  final VoidCallback onLogin;

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
          height: 78,
          padding: EdgeInsets.symmetric(
            horizontal: extraCompact ? 14 : (compact ? 20 : 28),
          ),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.58),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.82)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x14191C1E),
                blurRadius: 36,
                offset: Offset(0, 16),
              ),
            ],
          ),
          child: Row(
            children: [
              const Icon(
                Icons.auto_awesome,
                color: Color(0xFF0087A5),
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
              _VaultLoginButton(onTap: onLogin),
              if (!compact) ...const [
                SizedBox(width: 16),
                _VaultCircleIcon(icon: Icons.language),
                SizedBox(width: 12),
                _VaultCircleIcon(icon: Icons.notifications),
                SizedBox(width: 14),
                CircleAvatar(
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

class _VaultLoginButton extends StatelessWidget {
  const _VaultLoginButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 430;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 18 : 30,
            vertical: compact ? 12 : 14,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFF0F7891),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            'Login',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w700,
              fontSize: compact ? 14 : 16,
            ),
          ),
        ),
      ),
    );
  }
}

class _VaultCircleIcon extends StatelessWidget {
  const _VaultCircleIcon({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 34,
      height: 34,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 20, color: const Color(0xFF64748B)),
    );
  }
}

class _VaultProgressHeader extends StatelessWidget {
  const _VaultProgressHeader();

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 800),
      child: Column(
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'STEP 3 OF 3',
                  style: TextStyle(
                    fontSize: 14,
                    letterSpacing: 1.8,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0087A5),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                '100% Complete',
                style: TextStyle(fontSize: 14, color: Color(0xFF1F2937)),
              ),
            ],
          ),
          const SizedBox(height: 18),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: Container(
              height: 6,
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.45),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: Colors.white.withValues(alpha: 0.4)),
              ),
              child: Container(color: const Color(0xFF0087A5)),
            ),
          ),
        ],
      ),
    );
  }
}

class _VaultHero extends StatelessWidget {
  const _VaultHero();

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 760;

    return Column(
      children: [
        Text(
          'The Document Vault',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: compact ? 44 : 72,
            fontWeight: FontWeight.w800,
            letterSpacing: -1.8,
            color: const Color(0xFF0F172A),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Upload your proof of excellence for the final review.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 20, height: 1.6, color: Color(0xFF475569)),
        ),
      ],
    );
  }
}

class _VaultGrid extends StatelessWidget {
  const _VaultGrid();

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    if (width < 900) {
      return const Column(
        children: [
          _SmallUploadCard(
            title: 'SSM Cert',
            icon: Icons.domain_verification,
            iconColor: Color(0xFF0087A5),
          ),
          SizedBox(height: 18),
          _SmallUploadCard(
            title: 'Pitch Deck',
            icon: Icons.present_to_all,
            iconColor: Color(0xFF904D00),
          ),
          SizedBox(height: 18),
          _SmallUploadCard(
            title: 'Financials',
            icon: Icons.account_balance,
            iconColor: Color(0xFF0087A5),
          ),
          SizedBox(height: 18),
          _SmallUploadCard(
            title: 'Business Plan',
            icon: Icons.lightbulb,
            iconColor: Color(0xFF494BD6),
            height: 318,
          ),
          SizedBox(height: 18),
          _LargeUploadCard(height: 500),
        ],
      );
    }

    return const Column(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _SmallUploadCard(
                title: 'SSM Cert',
                icon: Icons.domain_verification,
                iconColor: Color(0xFF0087A5),
              ),
            ),
            SizedBox(width: 18),
            Expanded(
              child: _SmallUploadCard(
                title: 'Pitch Deck',
                icon: Icons.present_to_all,
                iconColor: Color(0xFF904D00),
              ),
            ),
            SizedBox(width: 18),
            Expanded(
              child: _SmallUploadCard(
                title: 'Financials',
                icon: Icons.account_balance,
                iconColor: Color(0xFF0087A5),
              ),
            ),
          ],
        ),
        SizedBox(height: 18),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _SmallUploadCard(
                title: 'Business Plan',
                icon: Icons.lightbulb,
                iconColor: Color(0xFF494BD6),
                height: 318,
              ),
            ),
            SizedBox(width: 18),
            Expanded(flex: 2, child: _LargeUploadCard()),
          ],
        ),
      ],
    );
  }
}

class _SmallUploadCard extends StatelessWidget {
  const _SmallUploadCard({
    required this.title,
    required this.icon,
    required this.iconColor,
    this.height = 318,
  });

  final String title;
  final IconData icon;
  final Color iconColor;
  final double height;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(34),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          height: height,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(34),
            border: Border.all(color: Colors.white.withValues(alpha: 0.8)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x140087A5),
                blurRadius: 30,
                offset: Offset(0, 12),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const Spacer(),
                  Icon(icon, color: iconColor, size: 26),
                ],
              ),
              const SizedBox(height: 18),
              const Expanded(
                child: _UploadZone(
                  text: 'Click to upload',
                  caption: 'PDF, JPG, PNG (Max 10MB)',
                  icon: Icons.upload_file,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LargeUploadCard extends StatelessWidget {
  const _LargeUploadCard({this.height = 318});

  final double height;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(34),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          height: height,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0x66FFFFFF), Color(0x33B7EAFF)],
            ),
            borderRadius: BorderRadius.circular(34),
            border: Border.all(color: Colors.white.withValues(alpha: 0.8)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x140087A5),
                blurRadius: 30,
                offset: Offset(0, 12),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Project Proposal',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        SizedBox(height: 6),
                        Text(
                          'The core narrative of your grant application.',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF475569),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.description, color: Color(0xFF0087A5), size: 30),
                ],
              ),
              const SizedBox(height: 20),
              Expanded(
                child: _UploadZone(
                  text: 'Drag & drop your primary proposal document',
                  caption: 'PDF, JPG, PNG (Max 25MB)',
                  icon: Icons.cloud_upload,
                  large: true,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _UploadZone extends StatelessWidget {
  const _UploadZone({
    required this.text,
    required this.caption,
    required this.icon,
    this.large = false,
  });

  final String text;
  final String caption;
  final IconData icon;
  final bool large;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final short = constraints.maxHeight < 240;
        final iconBox = short ? (large ? 62.0 : 52.0) : (large ? 74.0 : 60.0);
        final iconSize = short ? (large ? 28.0 : 24.0) : (large ? 32.0 : 28.0);
        final titleSize = short ? 15.0 : (large ? 18.0 : 16.0);
        final captionSize = short ? 12.0 : 14.0;
        final gap = short ? 12.0 : (large ? 20.0 : 18.0);
        final padding = short ? 14.0 : (large ? 24.0 : 16.0);

        return Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.34),
            borderRadius: BorderRadius.circular(28),
            border: Border.all(
              color: const Color(0x4DB7EAFF),
              style: BorderStyle.solid,
            ),
          ),
          child: Center(
            child: Padding(
              padding: EdgeInsets.all(padding),
              child: FittedBox(
                fit: BoxFit.scaleDown,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 260),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: iconBox,
                        height: iconBox,
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.85),
                          shape: BoxShape.circle,
                          border: Border.all(color: const Color(0x1ABCC9CE)),
                        ),
                        child: Icon(
                          icon,
                          color: const Color(0xFF0087A5),
                          size: iconSize,
                        ),
                      ),
                      SizedBox(height: gap),
                      Text(
                        text,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: titleSize,
                          fontWeight: FontWeight.w700,
                          color: const Color(0xFF111827),
                        ),
                      ),
                      SizedBox(height: short ? 6 : 8),
                      Text(
                        caption,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: captionSize,
                          color: const Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _VaultFooter extends StatelessWidget {
  const _VaultFooter({required this.onBack, required this.onSubmit});

  final VoidCallback onBack;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 760;

    return compact
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _VaultBackButton(onTap: onBack),
              const SizedBox(height: 16),
              _SubmitButton(onTap: onSubmit),
            ],
          )
        : Row(
            children: [
              _VaultBackButton(onTap: onBack),
              const Spacer(),
              _SubmitButton(onTap: onSubmit),
            ],
          );
  }
}

class _VaultBackButton extends StatelessWidget {
  const _VaultBackButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return TextButton.icon(
      onPressed: onTap,
      style: TextButton.styleFrom(
        foregroundColor: const Color(0xFF1F2937),
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 12),
      ),
      icon: const Icon(Icons.arrow_back, size: 20),
      label: const Text(
        'Back to Narrative',
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
      ),
    );
  }
}

class _SubmitButton extends StatelessWidget {
  const _SubmitButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 430;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 24 : 44,
            vertical: compact ? 16 : 20,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFF0087A5),
            borderRadius: BorderRadius.circular(999),
            boxShadow: const [
              BoxShadow(
                color: Color(0x330087A5),
                blurRadius: 28,
                offset: Offset(0, 12),
              ),
            ],
          ),
          child: Wrap(
            alignment: WrapAlignment.center,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 12,
            children: [
              Text(
                'Submit Application',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: compact ? 16 : 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Icon(Icons.check_circle, color: Colors.white, size: 22),
            ],
          ),
        ),
      ),
    );
  }
}
