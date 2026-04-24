import 'dart:ui';

import 'package:flutter/material.dart';

import '../auth/login_screen.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({super.key});

  static const String routeName = '/';

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final showSideDock = width >= 1180;

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
                    left: 14,
                    top: 206,
                    child: _SideDock(
                      onHomeTap: () {},
                      onNewGrantTap: () =>
                          Navigator.pushNamed(context, LoginScreen.routeName),
                    ),
                  ),
                SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(14, 14, 14, 40),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1180),
                      child: Column(
                        children: [
                          _TopBar(
                            onLogin: () => Navigator.pushNamed(
                              context,
                              LoginScreen.routeName,
                            ),
                          ),
                          const SizedBox(height: 72),
                          const _HeroSection(),
                          const SizedBox(height: 42),
                          const _PipelineStagePanel(),
                          const SizedBox(height: 78),
                          const _PipelineRevealSection(),
                          const SizedBox(height: 78),
                          const _IntentSwitchSection(),
                          const SizedBox(height: 96),
                          _BottomCta(
                            onTap: () => Navigator.pushNamed(
                              context,
                              LoginScreen.routeName,
                            ),
                          ),
                          const SizedBox(height: 28),
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
      fit: StackFit.expand,
      children: const [
        ColoredBox(color: Color(0xFFF7F9FB)),
        _MeshBlob(
          alignment: Alignment.topLeft,
          width: 640,
          height: 640,
          offset: Offset(-120, -80),
          color: Color(0x4000B4D8),
        ),
        _MeshBlob(
          alignment: Alignment.bottomRight,
          width: 620,
          height: 620,
          offset: Offset(120, 90),
          color: Color(0x33494BD6),
        ),
        _MeshBlob(
          alignment: Alignment.center,
          width: 520,
          height: 520,
          offset: Offset(-80, -40),
          color: Color(0x22006780),
        ),
        _MeshBlob(
          alignment: Alignment.bottomLeft,
          width: 760,
          height: 760,
          offset: Offset(-180, 180),
          color: Color(0x24999CFF),
        ),
        _MeshBlob(
          alignment: Alignment.topRight,
          width: 420,
          height: 420,
          offset: Offset(60, 20),
          color: Color(0x306CD3F7),
        ),
      ],
    );
  }
}

class _MeshBlob extends StatelessWidget {
  const _MeshBlob({
    required this.alignment,
    required this.width,
    required this.height,
    required this.offset,
    required this.color,
  });

  final Alignment alignment;
  final double width;
  final double height;
  final Offset offset;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Transform.translate(
        offset: offset,
        child: IgnorePointer(
          child: ImageFiltered(
            imageFilter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
            child: Container(
              width: width,
              height: height,
              decoration: BoxDecoration(shape: BoxShape.circle, color: color),
            ),
          ),
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
          height: 56,
          width: double.infinity,
          padding: EdgeInsets.symmetric(horizontal: compact ? 16 : 20),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.56)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x10191C1E),
                blurRadius: 28,
                offset: Offset(0, 10),
              ),
            ],
          ),
          child: Row(
            children: [
              const Icon(
                Icons.auto_awesome,
                size: 18,
                color: Color(0xFF00B4D8),
              ),
              const SizedBox(width: 8),
              Text(
                'Grantly',
                style: TextStyle(
                  fontSize: compact ? 17 : 18,
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF191C1E),
                  letterSpacing: -0.4,
                ),
              ),
              const Spacer(),
              _PillButton(label: 'Login', onTap: onLogin),
              if (!compact) ...const [
                SizedBox(width: 10),
                _TopBarIcon(icon: Icons.language),
                SizedBox(width: 6),
                _TopBarIcon(icon: Icons.notifications),
                SizedBox(width: 10),
                CircleAvatar(
                  radius: 14,
                  backgroundColor: Color(0xFF252C35),
                  child: Icon(Icons.person, size: 15, color: Colors.white),
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
      width: 30,
      height: 30,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.22),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 17, color: const Color(0xFF5A6776)),
    );
  }
}

class _SideDock extends StatelessWidget {
  const _SideDock({required this.onHomeTap, required this.onNewGrantTap});

  final VoidCallback onHomeTap;
  final VoidCallback onNewGrantTap;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          width: 64,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: 0.56)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x10191C1E),
                blurRadius: 28,
                offset: Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            children: [
              _DockItem(
                icon: Icons.grid_view_rounded,
                selected: true,
                onTap: onHomeTap,
              ),
              const SizedBox(height: 12),
              const _DockItem(icon: Icons.folder_open_rounded),
              const SizedBox(height: 12),
              const _DockItem(icon: Icons.auto_awesome_rounded),
              const SizedBox(height: 12),
              const _DockItem(icon: Icons.history_edu_outlined),
              const SizedBox(height: 20),
              _SmallDockButton(onTap: onNewGrantTap),
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
      width: 38,
      height: 38,
      decoration: BoxDecoration(
        color: selected ? const Color(0xFF00B4D8) : Colors.transparent,
        borderRadius: BorderRadius.circular(999),
        boxShadow: selected
            ? const [
                BoxShadow(
                  color: Color(0x3300B4D8),
                  blurRadius: 14,
                  offset: Offset(0, 8),
                ),
              ]
            : null,
      ),
      child: Icon(
        icon,
        size: 18,
        color: selected ? Colors.white : const Color(0xFF677585),
      ),
    );

    if (onTap == null) {
      return child;
    }

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: child,
    );
  }
}

class _SmallDockButton extends StatelessWidget {
  const _SmallDockButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: const Color(0x1400B4D8),
            borderRadius: BorderRadius.circular(999),
          ),
          child: const Icon(Icons.add, color: Color(0xFF00B4D8), size: 20),
        ),
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  const _HeroSection();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 720;
        final headlineSize = compact ? 38.0 : 58.0;

        return Column(
          children: [
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: RichText(
                textAlign: TextAlign.center,
                text: TextSpan(
                  style: TextStyle(
                    color: const Color(0xFF191C1E),
                    fontSize: headlineSize,
                    fontWeight: FontWeight.w800,
                    height: 1.08,
                    letterSpacing: -1.4,
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
                                Rect.fromLTWH(0, 0, compact ? 220 : 320, 80),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 18),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 620),
              child: Text(
                'An AI-powered workflow copilot that automates the entire grant readiness process. Fluid, intelligent, and designed for technical storytelling.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: compact ? 17 : 18,
                  height: 1.65,
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

        return _GlassContainer(
          radius: 34,
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 18 : 28,
            vertical: compact ? 18 : 24,
          ),
          child: compact
              ? Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 24,
                  runSpacing: 22,
                  children: const [
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
                  ],
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
          border: Border(top: BorderSide(color: Color(0x2200B4D8), width: 1)),
        ),
      ),
    );
  }
}

class _Stage extends StatelessWidget {
  const _Stage({
    required this.icon,
    required this.label,
    this.bg = const Color(0x26FFFFFF),
    this.fg = const Color(0xFF2D3748),
  });

  final IconData icon;
  final String label;
  final Color bg;
  final Color fg;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 110,
      child: Column(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: bg,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white.withValues(alpha: 0.6)),
            ),
            child: Icon(icon, size: 24, color: fg),
          ),
          const SizedBox(height: 10),
          Text(
            label,
            style: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 13,
              color: Color(0xFF191C1E),
            ),
          ),
        ],
      ),
    );
  }
}

class _PipelineRevealSection extends StatelessWidget {
  const _PipelineRevealSection();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 880;

        return compact
            ? const Column(
                children: [
                  _IngestCard(),
                  SizedBox(height: 22),
                  _EvaluateCard(),
                ],
              )
            : const Row(
                children: [
                  Expanded(child: _IngestCard()),
                  SizedBox(width: 22),
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
      radius: 30,
      padding: const EdgeInsets.all(24),
      tint: const Color(0x74FFFFFF),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              _IconBadge(
                icon: Icons.document_scanner,
                color: Color(0xFF191C1E),
              ),
              SizedBox(width: 12),
              Text(
                'Ingest & Parse',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
              ),
            ],
          ),
          const SizedBox(height: 16),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xFF3D494D),
                height: 1.55,
                fontSize: 14,
              ),
              children: [
                TextSpan(text: 'Automating '),
                TextSpan(
                  text: 'unstructured RFP parsing',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w800,
                  ),
                ),
                TextSpan(text: ' to translate complex requirements into '),
                TextSpan(
                  text: 'discrete semantic logic blocks.',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 170,
            child: Stack(
              children: [
                Positioned(
                  left: 26,
                  top: 28,
                  child: Transform.rotate(
                    angle: -0.05,
                    child: Container(
                      width: 210,
                      height: 116,
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.62),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: Colors.white.withValues(alpha: 0.7),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          _TinyLine(width: 110),
                          SizedBox(height: 10),
                          _TinyLine(width: 148),
                          SizedBox(height: 10),
                          _TinyLine(width: 126),
                        ],
                      ),
                    ),
                  ),
                ),
                Positioned(
                  right: 26,
                  top: 10,
                  child: Transform.rotate(
                    angle: 0.04,
                    child: Container(
                      width: 146,
                      height: 136,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.96),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x14191C1E),
                            blurRadius: 22,
                            offset: Offset(0, 14),
                          ),
                        ],
                      ),
                      child: const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _ChecklistRow(),
                          SizedBox(height: 10),
                          _ChecklistRow(width: 78),
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

class _ChecklistRow extends StatelessWidget {
  const _ChecklistRow({this.width = 96});

  final double width;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(Icons.check_circle, size: 14, color: Color(0xFF00B4D8)),
        const SizedBox(width: 8),
        Expanded(
          child: Align(
            alignment: Alignment.centerLeft,
            child: _TinyLine(width: width),
          ),
        ),
      ],
    );
  }
}

class _TinyLine extends StatelessWidget {
  const _TinyLine({this.width = 92, this.color = const Color(0x2900B4D8)});

  final double width;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 7,
      width: width,
      decoration: BoxDecoration(
        color: color,
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
      radius: 30,
      padding: const EdgeInsets.all(24),
      tint: const Color(0x3A00B4D8),
      borderColor: const Color(0x3000B4D8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              _IconBadge(icon: Icons.radar, color: Color(0xFF00B4D8)),
              SizedBox(width: 12),
              Text(
                'Evaluate Logic',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF00B4D8),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          RichText(
            text: const TextSpan(
              style: TextStyle(
                color: Color(0xCC006780),
                height: 1.55,
                fontSize: 14,
              ),
              children: [
                TextSpan(text: 'Systematic '),
                TextSpan(
                  text: 'benchmarking of internal evidence',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w800,
                  ),
                ),
                TextSpan(text: ' against project criteria, verified through '),
                TextSpan(
                  text: 'precision-weighted confidence intervals.',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w800,
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
                fontSize: 68,
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
                letterSpacing: 2.4,
                fontWeight: FontWeight.w700,
                fontSize: 10,
              ),
            ),
          ),
          const SizedBox(height: 20),
          const Row(
            children: [
              Text(
                'Mission Alignment',
                style: TextStyle(color: Color(0xFF3D494D), fontSize: 13),
              ),
              Spacer(),
              Text(
                'High',
                style: TextStyle(
                  color: Color(0xFF00B4D8),
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 6,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(999),
            ),
            child: FractionallySizedBox(
              widthFactor: 0.94,
              alignment: Alignment.centerLeft,
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF00B4D8),
                  borderRadius: BorderRadius.circular(999),
                  boxShadow: const [
                    BoxShadow(color: Color(0x6600B4D8), blurRadius: 10),
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
        final compact = constraints.maxWidth < 900;

        return _GlassContainer(
          radius: 34,
          padding: const EdgeInsets.all(5),
          tint: const Color(0x52FFFFFF),
          child: compact
              ? const Column(
                  children: [
                    _LogicArchitecturePanel(),
                    SizedBox(height: 8),
                    _LogicPipelinePanel(),
                  ],
                )
              : const Row(
                  children: [
                    Expanded(child: _LogicArchitecturePanel()),
                    SizedBox(width: 0.5),
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
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.66),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.table_chart, color: Color(0xFF00B4D8), size: 18),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Orchestrated Logic Architecture',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
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
                height: 1.55,
                fontSize: 13,
              ),
              children: [
                TextSpan(text: 'Navigate your data landscape by '),
                TextSpan(
                  text: 'mapping evidence traces to specific narrative nodes',
                  style: TextStyle(
                    color: Color(0xFF00B4D8),
                    fontWeight: FontWeight.w800,
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
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: const Color(0x14904D00),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.draw, color: Color(0xFF904D00), size: 18),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Universal Logic Pipeline',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
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
                height: 1.55,
                fontSize: 13,
              ),
              children: [
                TextSpan(text: 'Seamlessly '),
                TextSpan(
                  text:
                      'compiling technical blueprints into a final, deployable grant architecture',
                  style: TextStyle(
                    color: Color(0xFF904D00),
                    fontWeight: FontWeight.w800,
                  ),
                ),
                TextSpan(text: ' ready for submission.'),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Container(
            height: 108,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.72),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0x14FFFFFF)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _TinyLine(width: 96, color: Color(0x26904D00)),
                SizedBox(height: 14),
                _TinyLine(width: 210, color: Color(0x12A7B2C6)),
                SizedBox(height: 8),
                _TinyLine(width: 176, color: Color(0x12A7B2C6)),
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
      height: 38,
      decoration: BoxDecoration(
        color: active
            ? const Color(0x1600B4D8)
            : Colors.white.withValues(alpha: 0.58),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: active ? const Color(0x2200B4D8) : const Color(0x22FFFFFF),
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
    final compact = MediaQuery.sizeOf(context).width < 700;

    return Column(
      children: [
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Text(
            'Ready to transform your grant workflow?',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: compact ? 34 : 42,
              fontWeight: FontWeight.w800,
              color: const Color(0xFF191C1E),
              letterSpacing: -1.0,
            ),
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
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: EdgeInsets.symmetric(
            horizontal: large ? 28 : 22,
            vertical: large ? 15 : 8,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFF00B4D8),
            borderRadius: BorderRadius.circular(999),
            boxShadow: const [
              BoxShadow(
                color: Color(0x3300B4D8),
                blurRadius: 18,
                offset: Offset(0, 8),
              ),
            ],
          ),
          child: Text(
            label,
            style: TextStyle(
              color: Colors.white,
              fontSize: large ? 15 : 12,
              fontWeight: FontWeight.w800,
            ),
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
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.64)),
      ),
      child: Icon(icon, color: color, size: 20),
    );
  }
}

class _GlassContainer extends StatelessWidget {
  const _GlassContainer({
    required this.child,
    this.radius = 30,
    this.padding = const EdgeInsets.all(20),
    this.tint = const Color(0x66FFFFFF),
    this.borderColor = const Color(0x72FFFFFF),
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
                color: Color(0x0F00B4D8),
                blurRadius: 32,
                offset: Offset(0, 10),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
