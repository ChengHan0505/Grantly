import 'dart:ui';

import 'package:flutter/material.dart';

import '../auth/login_screen.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({super.key});

  static const String routeName = '/';

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;
    final showSideDock = screenWidth >= 1100;

    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FB),
      body: Stack(
        children: [
          const Positioned.fill(child: _MeshBackground()),
          SafeArea(
            child: Stack(
              children: [
                if (showSideDock)
                  Positioned(
                    left: 16,
                    top: 170,
                    child: _SideDock(onHomeTap: () {}),
                  ),
                SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(22, 14, 22, 36),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1280),
                      child: Column(
                        children: [
                          _TopBar(
                            onLogin: () => Navigator.pushNamed(
                              context,
                              LoginScreen.routeName,
                            ),
                          ),
                          const SizedBox(height: 70),
                          const _HeroSection(),
                          const SizedBox(height: 56),
                          const _PipelineStagePanel(),
                          const SizedBox(height: 76),
                          const _PipelineRevealSection(),
                          const SizedBox(height: 74),
                          const _IntentSwitchSection(),
                          const SizedBox(height: 92),
                          _BottomCta(
                            onTap: () => Navigator.pushNamed(
                              context,
                              LoginScreen.routeName,
                            ),
                          ),
                          const SizedBox(height: 40),
                        ],
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

class _MeshBackground extends StatelessWidget {
  const _MeshBackground();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: const [
        _Blob(top: -120, left: -100, size: 760, color: Color(0x4000B4D8)),
        _Blob(bottom: -140, right: -120, size: 680, color: Color(0x33494BD6)),
        _Blob(top: 290, left: 320, size: 540, color: Color(0x26006780)),
        _Blob(bottom: 40, left: -220, size: 820, color: Color(0x32999CFF)),
        _Blob(top: 80, right: 120, size: 430, color: Color(0x406CD3F7)),
      ],
    );
  }
}

class _Blob extends StatelessWidget {
  const _Blob({
    this.top,
    this.left,
    this.right,
    this.bottom,
    required this.size,
    required this.color,
  });

  final double? top;
  final double? left;
  final double? right;
  final double? bottom;
  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: top,
      left: left,
      right: right,
      bottom: bottom,
      child: IgnorePointer(
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(shape: BoxShape.circle, color: color),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({required this.onLogin});

  final VoidCallback onLogin;

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 720;

    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          height: 62,
          width: double.infinity,
          padding: EdgeInsets.symmetric(horizontal: compact ? 14 : 20),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.56)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0F191C1E),
                blurRadius: 40,
                offset: Offset(0, 18),
              ),
            ],
          ),
          child: Row(
            children: [
              const Icon(
                Icons.auto_awesome,
                size: 19,
                color: Color(0xFF00B4D8),
              ),
              const SizedBox(width: 8),
              Text(
                'Grant Copilot',
                style: TextStyle(
                  fontSize: compact ? 18 : 23,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const Spacer(),
              _PillButton(label: 'Login', onTap: onLogin),
              if (!compact) ...[
                const SizedBox(width: 8),
                const _TopBarIcon(icon: Icons.language),
                const SizedBox(width: 6),
                const _TopBarIcon(icon: Icons.notifications),
                const SizedBox(width: 10),
                const CircleAvatar(
                  radius: 15,
                  backgroundColor: Color(0xFF252C35),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _TopBarIcon extends StatelessWidget {
  const _TopBarIcon({required this.icon});
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.3),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 18, color: const Color(0xFF5A6776)),
    );
  }
}

class _SideDock extends StatelessWidget {
  const _SideDock({required this.onHomeTap});
  final VoidCallback onHomeTap;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          width: 72,
          padding: const EdgeInsets.symmetric(vertical: 18),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.56)),
          ),
          child: Column(
            children: [
              _DockItem(
                icon: Icons.grid_view_rounded,
                selected: true,
                onTap: onHomeTap,
              ),
              const SizedBox(height: 14),
              const _DockItem(icon: Icons.folder_open_rounded),
              const SizedBox(height: 14),
              const _DockItem(icon: Icons.auto_awesome_rounded),
              const SizedBox(height: 14),
              const _DockItem(icon: Icons.edit_note_rounded),
            ],
          ),
        ),
      ),
    );
  }
}

class _DockItem extends StatelessWidget {
  const _DockItem({required this.icon, this.selected = false, this.onTap});

  final IconData icon;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final child = Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        color: selected ? const Color(0xFF00B4D8) : Colors.transparent,
        borderRadius: BorderRadius.circular(999),
        boxShadow: selected
            ? const [
                BoxShadow(
                  color: Color(0x4000B4D8),
                  blurRadius: 14,
                  offset: Offset(0, 7),
                ),
              ]
            : null,
      ),
      child: Icon(
        icon,
        size: 19,
        color: selected ? Colors.white : const Color(0xFF677585),
      ),
    );
    if (onTap == null) return child;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: child,
    );
  }
}

class _HeroSection extends StatelessWidget {
  const _HeroSection();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 700;
        final headlineSize = compact ? 42.0 : 66.0;

        return Column(
          children: [
            RichText(
              textAlign: TextAlign.center,
              text: TextSpan(
                style: TextStyle(
                  color: const Color(0xFF191C1E),
                  fontSize: headlineSize,
                  fontWeight: FontWeight.w700,
                  height: 1.06,
                ),
                children: [
                  const TextSpan(text: 'The Future of Grants is\n'),
                  TextSpan(
                    text: 'Generative',
                    style: TextStyle(
                      foreground: Paint()
                        ..shader =
                            const LinearGradient(
                              colors: [
                                Color(0xFF00B4D8),
                                Color(0xFF494BD6),
                                Color(0xFF904D00),
                              ],
                            ).createShader(
                              Rect.fromLTWH(0, 0, compact ? 220 : 320, 70),
                            ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: Text(
                'An AI-powered workflow copilot that automates the entire grant readiness process. '
                'Fluid, intelligent, and designed for technical storytelling.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: compact ? 18 : 21,
                  height: 1.5,
                  color: const Color(0xFF3D494D),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _PipelineStagePanel extends StatelessWidget {
  const _PipelineStagePanel();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 760;
        final stages = const [
          _Stage(icon: Icons.upload_file, label: 'Ingest'),
          _Stage(
            icon: Icons.analytics,
            label: 'Evaluate',
            bg: Color(0x3300B4D8),
            fg: Color(0xFF00B4D8),
          ),
          _Stage(
            icon: Icons.hub,
            label: 'Orchestrate',
            bg: Color(0x33999CFF),
            fg: Color(0xFF494BD6),
          ),
          _Stage(
            icon: Icons.edit_document,
            label: 'Draft',
            bg: Color(0x33FE932C),
            fg: Color(0xFF904D00),
          ),
        ];

        return _GlassContainer(
          radius: 48,
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 20 : 34,
            vertical: compact ? 24 : 28,
          ),
          child: compact
              ? Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 18,
                  runSpacing: 18,
                  children: stages,
                )
              : const Row(
                  children: [
                    _Stage(icon: Icons.upload_file, label: 'Ingest'),
                    _StageDivider(),
                    _Stage(
                      icon: Icons.analytics,
                      label: 'Evaluate',
                      bg: Color(0x3300B4D8),
                      fg: Color(0xFF00B4D8),
                    ),
                    _StageDivider(),
                    _Stage(
                      icon: Icons.hub,
                      label: 'Orchestrate',
                      bg: Color(0x33999CFF),
                      fg: Color(0xFF494BD6),
                    ),
                    _StageDivider(),
                    _Stage(
                      icon: Icons.edit_document,
                      label: 'Draft',
                      bg: Color(0x33FE932C),
                      fg: Color(0xFF904D00),
                    ),
                  ],
                ),
        );
      },
    );
  }
}

class _StageDivider extends StatelessWidget {
  const _StageDivider();
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 14),
        height: 1,
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: Color(0x3300B4D8), width: 1)),
        ),
      ),
    );
  }
}

class _Stage extends StatelessWidget {
  const _Stage({
    required this.icon,
    required this.label,
    this.bg = const Color(0x40FFFFFF),
    this.fg = const Color(0xFF3D494D),
  });
  final IconData icon;
  final String label;
  final Color bg;
  final Color fg;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 62,
          height: 62,
          decoration: BoxDecoration(
            color: bg,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white.withValues(alpha: 0.55)),
          ),
          child: Icon(icon, size: 30, color: fg),
        ),
        const SizedBox(height: 10),
        Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
        ),
      ],
    );
  }
}

class _PipelineRevealSection extends StatelessWidget {
  const _PipelineRevealSection();
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 960;

        return compact
            ? const Column(
                children: [
                  _IngestCard(),
                  SizedBox(height: 24),
                  _EvaluateCard(),
                ],
              )
            : const Row(
                children: [
                  Expanded(child: _IngestCard()),
                  SizedBox(width: 24),
                  Expanded(child: _EvaluateCard()),
                ],
              );
      },
    );
  }
}

class _IngestCard extends StatelessWidget {
  const _IngestCard();

  @override
  Widget build(BuildContext context) {
    return _GlassContainer(
      radius: 40,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const _IconBadge(
                icon: Icons.document_scanner,
                color: Color(0xFF191C1E),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Ingest & Parse',
                  style: TextStyle(fontSize: 30, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xFF3D494D),
                height: 1.55,
                fontSize: 17,
              ),
              children: [
                TextSpan(text: 'Automating '),
                TextSpan(
                  text: 'unstructured RFP parsing',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                TextSpan(text: ' to translate complex requirements into '),
                TextSpan(
                  text: 'discrete semantic logic blocks.',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Stack(
            children: [
              Container(
                margin: const EdgeInsets.only(left: 12, top: 20),
                height: 180,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.45),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.6),
                  ),
                ),
              ),
              Positioned(
                right: 0,
                top: 0,
                child: Container(
                  width: 220,
                  height: 220,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.85),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.65),
                    ),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x1F191C1E),
                        blurRadius: 24,
                        offset: Offset(0, 12),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(18),
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _TinyLine(),
                      SizedBox(height: 10),
                      _TinyLine(width: 120),
                    ],
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

class _TinyLine extends StatelessWidget {
  const _TinyLine({this.width = 92});
  final double width;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 8,
      width: width,
      decoration: BoxDecoration(
        color: const Color(0x3300B4D8),
        borderRadius: BorderRadius.circular(999),
      ),
    );
  }
}

class _EvaluateCard extends StatelessWidget {
  const _EvaluateCard();

  @override
  Widget build(BuildContext context) {
    return _GlassContainer(
      radius: 40,
      padding: const EdgeInsets.all(30),
      tint: const Color(0x2600B4D8),
      borderColor: const Color(0x4000B4D8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const _IconBadge(icon: Icons.radar, color: Color(0xFF00B4D8)),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Evaluate Logic',
                  style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF00B4D8),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xCC006780),
                height: 1.55,
                fontSize: 17,
              ),
              children: [
                TextSpan(text: 'Systematic '),
                TextSpan(
                  text: 'benchmarking of internal evidence',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                TextSpan(text: ' against project criteria, verified through '),
                TextSpan(
                  text: 'precision-weighted confidence intervals.',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const Center(
            child: Text(
              '94%',
              style: TextStyle(
                fontSize: 96,
                fontWeight: FontWeight.w900,
                color: Color(0xFF00B4D8),
                height: 0.9,
              ),
            ),
          ),
          const Center(
            child: Text(
              'MATCH ALIGNMENT SCORE',
              style: TextStyle(
                color: Color(0x99006780),
                letterSpacing: 2.6,
                fontWeight: FontWeight.w700,
                fontSize: 11,
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Row(
            children: [
              Text(
                'Mission Alignment',
                style: TextStyle(color: Color(0xFF3D494D)),
              ),
              Spacer(),
              Text(
                'High',
                style: TextStyle(
                  color: Color(0xFF00B4D8),
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 8,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: Colors.white.withValues(alpha: 0.6)),
            ),
            child: FractionallySizedBox(
              widthFactor: 0.94,
              alignment: Alignment.centerLeft,
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF00B4D8),
                  borderRadius: BorderRadius.circular(999),
                  boxShadow: const [
                    BoxShadow(color: Color(0x8000B4D8), blurRadius: 12),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _IntentSwitchSection extends StatelessWidget {
  const _IntentSwitchSection();
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 960;

        return _GlassContainer(
          radius: 48,
          padding: const EdgeInsets.all(6),
          child: compact
              ? const Column(
                  children: [
                    _LogicArchitecturePanel(),
                    SizedBox(height: 12),
                    _LogicPipelinePanel(),
                  ],
                )
              : const Row(
                  children: [
                    Expanded(child: _LogicArchitecturePanel()),
                    SizedBox(width: 1),
                    Expanded(child: _LogicPipelinePanel()),
                  ],
                ),
        );
      },
    );
  }
}

class _LogicArchitecturePanel extends StatelessWidget {
  const _LogicArchitecturePanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(34),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.62),
        borderRadius: BorderRadius.circular(38),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.table_chart, color: Color(0xFF00B4D8)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Orchestrated Logic Architecture',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 24,
                    color: Color(0xFF00B4D8),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xFF3D494D),
                height: 1.45,
                fontSize: 16,
              ),
              children: [
                TextSpan(text: 'Navigate your data landscape by '),
                TextSpan(
                  text: 'mapping evidence traces to specific narrative nodes',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                TextSpan(text: ' within your project blueprint.'),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Row(
            children: const [
              Expanded(child: _MiniBox(active: false)),
              SizedBox(width: 12),
              Expanded(child: _MiniBox(active: true)),
            ],
          ),
          const SizedBox(height: 12),
          const _MiniBox(active: false, wide: true),
        ],
      ),
    );
  }
}

class _LogicPipelinePanel extends StatelessWidget {
  const _LogicPipelinePanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(34),
      decoration: BoxDecoration(
        color: const Color(0x14904D00),
        borderRadius: BorderRadius.circular(38),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.draw, color: Color(0xFF904D00)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Universal Logic Pipeline',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 24,
                    color: Color(0xFF904D00),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xFF3D494D),
                height: 1.45,
                fontSize: 16,
              ),
              children: [
                TextSpan(text: 'Seamlessly '),
                TextSpan(
                  text:
                      'compiling technical blueprints into a final, deployable grant architecture',
                  style: TextStyle(
                    color: Color(0xFF904D00),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                TextSpan(text: ' ready for submission.'),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Container(
            height: 126,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.62),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: const Color(0x1A904D00)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _TinyLine(width: 120),
                SizedBox(height: 14),
                _TinyLine(width: 250),
                SizedBox(height: 8),
                _TinyLine(width: 190),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MiniBox extends StatelessWidget {
  const _MiniBox({required this.active, this.wide = false});
  final bool active;
  final bool wide;
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 64,
      decoration: BoxDecoration(
        color: active
            ? const Color(0x1400B4D8)
            : Colors.white.withValues(alpha: 0.52),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: active ? const Color(0x3300B4D8) : const Color(0x66FFFFFF),
        ),
      ),
    );
  }
}

class _BottomCta extends StatelessWidget {
  const _BottomCta({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text(
          'Ready to transform your grant workflow?',
          style: TextStyle(
            fontSize: 62,
            fontWeight: FontWeight.w700,
            color: Color(0xFF191C1E),
          ),
        ),
        const SizedBox(height: 24),
        _PillButton(
          label: 'Unlock Your Grant Potential',
          onTap: onTap,
          large: true,
        ),
      ],
    );
  }
}

class _PillButton extends StatelessWidget {
  const _PillButton({
    required this.label,
    required this.onTap,
    this.large = false,
  });
  final String label;
  final VoidCallback onTap;
  final bool large;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Ink(
        padding: EdgeInsets.symmetric(
          horizontal: large ? 42 : 24,
          vertical: large ? 18 : 10,
        ),
        decoration: BoxDecoration(
          color: const Color(0xFF00B4D8),
          borderRadius: BorderRadius.circular(999),
          boxShadow: const [
            BoxShadow(
              color: Color(0x4000B4D8),
              blurRadius: 18,
              offset: Offset(0, 10),
            ),
          ],
        ),
        child: Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontSize: large ? 24 : 13,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _IconBadge extends StatelessWidget {
  const _IconBadge({required this.icon, required this.color});
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.64)),
      ),
      child: Icon(icon, color: color),
    );
  }
}

class _GlassContainer extends StatelessWidget {
  const _GlassContainer({
    required this.child,
    this.radius = 30,
    this.padding = const EdgeInsets.all(20),
    this.tint = const Color(0x66FFFFFF),
    this.borderColor = const Color(0x80FFFFFF),
  });
  final Widget child;
  final double radius;
  final EdgeInsetsGeometry padding;
  final Color tint;
  final Color borderColor;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: tint,
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: borderColor),
            boxShadow: const [
              BoxShadow(
                color: Color(0x14191C1E),
                blurRadius: 30,
                offset: Offset(0, 12),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
