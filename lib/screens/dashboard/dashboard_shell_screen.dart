import 'dart:ui';

import 'package:flutter/material.dart';

import '../landing/landing_screen.dart';

const _bg = Color(0xFFF7F9FB);
const _surface = Color(0xFFFFFFFF);
const _surfaceLow = Color(0xFFF2F4F6);
const _ink = Color(0xFF191C1E);
const _muted = Color(0xFF3D494D);
const _outline = Color(0xFFE0E7EC);
const _primary = Color(0xFF006780);
const _cyan = Color(0xFF00B4D8);
const _tertiary = Color(0xFF494BD6);
const _secondary = Color(0xFF904D00);
const _amber = Color(0xFFFE932C);
const _error = Color(0xFFBA1A1A);

void _showDashboardMessage(BuildContext context, String action) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('$action is ready for integration.'),
      behavior: SnackBarBehavior.floating,
      backgroundColor: _primary,
    ),
  );
}

class DashboardShellScreen extends StatefulWidget {
  const DashboardShellScreen({super.key});

  static const String routeName = '/dashboard';

  @override
  State<DashboardShellScreen> createState() => _DashboardShellScreenState();
}

class _DashboardShellScreenState extends State<DashboardShellScreen> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final compact = size.width < 900;
    final pages = [
      const _HomeTab(),
      _GrantTab(onApply: () => setState(() => _tab = 3)),
      const _CompanyProfileTab(),
      const _DraftsTab(),
    ];

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          const Positioned.fill(child: _AmbientBackground()),
          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1160),
                child: Column(
                  children: [
                    _TopNav(
                      selected: _tab,
                      compact: compact,
                      onTabSelected: (index) => setState(() => _tab = index),
                    ),
                    Expanded(
                      child: compact
                          ? Padding(
                              padding: const EdgeInsets.fromLTRB(
                                16,
                                18,
                                16,
                                18,
                              ),
                              child: pages[_tab],
                            )
                          : Row(
                              children: [
                                _SideRail(
                                  selected: _tab,
                                  onTap: (index) =>
                                      setState(() => _tab = index),
                                ),
                                Expanded(
                                  child: Padding(
                                    padding: const EdgeInsets.fromLTRB(
                                      0,
                                      20,
                                      20,
                                      20,
                                    ),
                                    child: pages[_tab],
                                  ),
                                ),
                              ],
                            ),
                    ),
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

class _AmbientBackground extends StatelessWidget {
  const _AmbientBackground();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        const ColoredBox(color: _bg),
        Positioned(
          top: -180,
          right: -120,
          child: _Glow(color: _amber.withValues(alpha: 0.12), size: 680),
        ),
        Positioned(
          bottom: -220,
          left: -160,
          child: _Glow(color: _cyan.withValues(alpha: 0.10), size: 760),
        ),
      ],
    );
  }
}

class _Glow extends StatelessWidget {
  const _Glow({required this.color, required this.size});

  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    return ImageFiltered(
      imageFilter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      ),
    );
  }
}

class _TopNav extends StatelessWidget {
  const _TopNav({
    required this.selected,
    required this.compact,
    required this.onTabSelected,
  });

  final int selected;
  final bool compact;
  final ValueChanged<int> onTabSelected;

  @override
  Widget build(BuildContext context) {
    return _Glass(
      margin: EdgeInsets.fromLTRB(compact ? 14 : 20, 16, compact ? 14 : 20, 0),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 16 : 24,
        vertical: compact ? 12 : 14,
      ),
      radius: 999,
      child: Row(
        children: [
          const Icon(Icons.auto_awesome, size: 20, color: _primary),
          const SizedBox(width: 8),
          Text(
            'Grantly',
            style: TextStyle(
              color: _ink,
              fontSize: compact ? 20 : 22,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.6,
            ),
          ),
          if (compact) ...[
            const Spacer(),
            _CompactTabMenu(selected: selected, onSelected: onTabSelected),
            const SizedBox(width: 10),
          ] else
            const Spacer(),
          if (!compact) ...const [
            _TopIcon(icon: Icons.language_rounded, label: 'Language'),
            SizedBox(width: 8),
            _TopIcon(icon: Icons.notifications_rounded, label: 'Notifications'),
            SizedBox(width: 10),
          ],
          _ProfileMenu(compact: compact),
        ],
      ),
    );
  }
}

class _CompactTabMenu extends StatelessWidget {
  const _CompactTabMenu({required this.selected, required this.onSelected});

  final int selected;
  final ValueChanged<int> onSelected;

  static const _labels = ['Home', 'Grants', 'Company', 'Roadmaps'];
  static const _icons = [
    Icons.grid_view_rounded,
    Icons.folder_rounded,
    Icons.domain_rounded,
    Icons.history_edu_rounded,
  ];

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<int>(
      tooltip: 'Navigation',
      onSelected: onSelected,
      itemBuilder: (context) => [
        for (var i = 0; i < _labels.length; i++)
          PopupMenuItem(
            value: i,
            child: Row(
              children: [
                Icon(_icons[i], color: selected == i ? _primary : _muted),
                const SizedBox(width: 12),
                Text(_labels[i]),
              ],
            ),
          ),
      ],
      child: Container(
        width: 38,
        height: 38,
        decoration: const BoxDecoration(color: _cyan, shape: BoxShape.circle),
        child: Icon(_icons[selected], color: Colors.white, size: 20),
      ),
    );
  }
}

class _ProfileMenu extends StatelessWidget {
  const _ProfileMenu({required this.compact});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      tooltip: 'Profile menu',
      offset: const Offset(0, 46),
      onSelected: (value) {
        if (value == 'sign-out') {
          Navigator.pushNamedAndRemoveUntil(
            context,
            LandingScreen.routeName,
            (route) => false,
          );
        } else {
          _showDashboardMessage(context, value);
        }
      },
      itemBuilder: (context) => const [
        PopupMenuItem(value: 'Alerts', child: Text('Alerts')),
        PopupMenuItem(
          value: 'Account Settings',
          child: Text('Account Settings'),
        ),
        PopupMenuItem(
          value: 'Subscriptions & Billing',
          child: Text('Subscriptions & Billing'),
        ),
        PopupMenuItem(value: 'Earn Commission', child: Text('Earn Commission')),
        PopupMenuItem(value: 'Country', child: Text('Country')),
        PopupMenuDivider(),
        PopupMenuItem(value: 'sign-out', child: Text('Sign Out')),
      ],
      child: CircleAvatar(
        radius: compact ? 16 : 18,
        backgroundColor: const Color(0xFFEFF3F6),
        child: const Icon(Icons.person, color: Color(0xFF18212A), size: 20),
      ),
    );
  }
}

class _TopIcon extends StatelessWidget {
  const _TopIcon({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: label,
      child: IconButton(
        onPressed: () => _showDashboardMessage(context, label),
        icon: Icon(icon, color: const Color(0xFF5F6E84), size: 22),
        splashRadius: 22,
      ),
    );
  }
}

class _SideRail extends StatelessWidget {
  const _SideRail({required this.selected, required this.onTap});

  final int selected;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    final items = [
      Icons.grid_view_rounded,
      Icons.folder_rounded,
      Icons.domain_rounded,
      Icons.history_edu_rounded,
    ];

    return _Glass(
      width: 68,
      margin: const EdgeInsets.fromLTRB(18, 150, 26, 56),
      padding: const EdgeInsets.symmetric(vertical: 14),
      radius: 999,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  for (var i = 0; i < items.length; i++) ...[
                    _DockButton(
                      icon: items[i],
                      selected: selected == i,
                      onTap: () => onTap(i),
                    ),
                    if (i != items.length - 1) const SizedBox(height: 14),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _DockButton extends StatelessWidget {
  const _DockButton({
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: selected ? _cyan : Colors.transparent,
            borderRadius: BorderRadius.circular(999),
            boxShadow: selected
                ? const [
                    BoxShadow(
                      color: Color(0x3300B4D8),
                      blurRadius: 18,
                      offset: Offset(0, 10),
                    ),
                  ]
                : null,
          ),
          child: Icon(
            icon,
            color: selected ? Colors.white : const Color(0xFF91A0B6),
            size: 24,
          ),
        ),
      ),
    );
  }
}

class _HomeTab extends StatelessWidget {
  const _HomeTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              const cards = [
                _MetricCard(
                  title: 'READINESS SCORE',
                  value: '88.4%',
                  caption: '+2.1% from last audit',
                  icon: Icons.speed_rounded,
                  accent: _primary,
                ),
                _MetricCard(
                  title: 'ACTIVE PIPELINE',
                  value: '12',
                  caption: '3 grants requiring attention',
                  icon: Icons.account_tree_rounded,
                  accent: _tertiary,
                  progress: true,
                ),
                _MetricCard(
                  title: 'DOCUMENT HEALTH',
                  value: 'Good',
                  caption: '92% metadata completion',
                  icon: Icons.health_and_safety_rounded,
                  accent: _secondary,
                  footer: 'All critical tags present',
                ),
              ];

              if (constraints.maxWidth < 760) {
                return Column(
                  children: [
                    cards[0],
                    const SizedBox(height: 18),
                    cards[1],
                    const SizedBox(height: 18),
                    cards[2],
                  ],
                );
              }

              return Row(
                children: [
                  Expanded(child: cards[0]),
                  const SizedBox(width: 20),
                  Expanded(child: cards[1]),
                  const SizedBox(width: 20),
                  Expanded(child: cards[2]),
                ],
              );
            },
          ),
          const SizedBox(height: 26),
          _Panel(
            padding: const EdgeInsets.all(28),
            radius: 38,
            color: _surfaceLow.withValues(alpha: 0.78),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Grant Pipeline',
                          style: TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.w900,
                            letterSpacing: -0.8,
                            color: _ink,
                          ),
                        ),
                        SizedBox(height: 6),
                        Text(
                          'Real-time status of targeted opportunities',
                          style: TextStyle(fontSize: 16, color: _muted),
                        ),
                      ],
                    ),
                    const Spacer(),
                    _SoftButton(
                      icon: Icons.filter_list_rounded,
                      label: 'Filter Views',
                      onTap: () =>
                          _showDashboardMessage(context, 'Filter Views'),
                    ),
                  ],
                ),
                const SizedBox(height: 34),
                LayoutBuilder(
                  builder: (context, constraints) {
                    const pipeline = Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _PipelineColumn(
                          title: 'DISCOVERED',
                          count: '4',
                          dot: Color(0xFF6D797E),
                          cards: [
                            _GrantMiniData(
                              label: 'FEDERAL',
                              title: 'NSF AI Research Grant',
                              amount: '\$2.5M',
                              due: 'Due Oct 15',
                            ),
                            _GrantMiniData(
                              label: 'FOUNDATION',
                              title: 'Gates Global Health',
                              amount: '\$500k',
                              due: 'Due Nov 01',
                            ),
                          ],
                        ),
                        SizedBox(width: 18),
                        _PipelineColumn(
                          title: 'AUDITED',
                          count: '2',
                          dot: _tertiary,
                          cards: [
                            _GrantMiniData(
                              label: 'STATE',
                              title: 'CA Clean Energy Init',
                              amount: '\$1.2M',
                              due: 'Due Sep 30',
                              note: '85% Match',
                            ),
                          ],
                        ),
                        SizedBox(width: 18),
                        _PipelineColumn(
                          title: 'DRAFTING',
                          count: '3',
                          dot: _secondary,
                          cards: [
                            _GrantMiniData(
                              label: 'CORPORATE',
                              title: 'Google Tech Impact',
                              amount: '\$750k',
                              due: 'Due in 5d',
                              progress: 0.60,
                            ),
                          ],
                        ),
                        SizedBox(width: 18),
                        _PipelineColumn(
                          title: 'READY',
                          count: '1',
                          dot: _primary,
                          cards: [
                            _GrantMiniData(
                              label: 'FEDERAL',
                              title: 'NIH Early Stage Dev',
                              amount: '\$3.0M',
                              due: 'Submit',
                              ready: true,
                            ),
                          ],
                        ),
                      ],
                    );

                    if (constraints.maxWidth < 900) {
                      return const SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: SizedBox(width: 980, child: pipeline),
                      );
                    }

                    return pipeline;
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 92),
        ],
      ),
    );
  }
}

class _GrantTab extends StatelessWidget {
  const _GrantTab({required this.onApply});

  final VoidCallback onApply;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _PageHeader(
            icon: Icons.analytics_rounded,
            iconColor: _secondary,
            title: 'Evaluate Logic',
            subtitle:
                'Analyzing alignment across 42 active funding sources. Choose a suitable grant to generate a roadmap for the application.',
          ),
          const SizedBox(height: 30),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 7,
                child: _Panel(
                  radius: 50,
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Wrap(
                                  spacing: 10,
                                  runSpacing: 10,
                                  children: [
                                    _Tag(
                                      text: 'DOE - EERE',
                                      bg: _surfaceLow,
                                      fg: _muted,
                                    ),
                                    _Tag(
                                      text: 'High Confidence',
                                      bg: Color(0xFFEDEBFF),
                                      fg: _tertiary,
                                      icon: Icons.auto_awesome,
                                    ),
                                  ],
                                ),
                                SizedBox(height: 20),
                                Text(
                                  'Clean Energy Infrastructure Deployment Grant',
                                  style: TextStyle(
                                    color: _ink,
                                    fontSize: 34,
                                    height: 1.12,
                                    fontWeight: FontWeight.w900,
                                    letterSpacing: -0.8,
                                  ),
                                ),
                                SizedBox(height: 12),
                                Text(
                                  'FOA-0002894 - Deadline: Oct 15, 2024',
                                  style: TextStyle(color: _muted, fontSize: 16),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 24),
                          Container(
                            width: 116,
                            height: 116,
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFDDB6),
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: _secondary.withValues(alpha: 0.14),
                              ),
                            ),
                            child: const Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  '94%',
                                  style: TextStyle(
                                    color: _secondary,
                                    fontSize: 38,
                                    fontWeight: FontWeight.w900,
                                    letterSpacing: -1,
                                  ),
                                ),
                                Text(
                                  'MATCH',
                                  style: TextStyle(
                                    color: _secondary,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w800,
                                    letterSpacing: 2,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 36),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _SectionLabel(
                                  icon: Icons.verified_rounded,
                                  text: 'EVIDENCE TRACE',
                                  color: _secondary,
                                ),
                                SizedBox(height: 18),
                                _EvidenceTile(
                                  icon: Icons.eco_rounded,
                                  title:
                                      "Alignment with 'Decarbonization' objective",
                                  body:
                                      'Your prior project "Solar Grid V2" demonstrates successful deployment in underserved regions.',
                                ),
                                SizedBox(height: 14),
                                _EvidenceTile(
                                  icon: Icons.groups_rounded,
                                  title: 'Community Benefit Plan confirmed',
                                  body:
                                      'Identified partnerships with 3 local workforce development boards in your profile.',
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 36),
                          Expanded(
                            child: Column(
                              children: [
                                const _GapPanel(),
                                const SizedBox(height: 34),
                                const Text(
                                  'System is ready to convert source documents into a step-by-step application roadmap.',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    color: _muted,
                                    fontSize: 14,
                                    height: 1.4,
                                  ),
                                ),
                                const SizedBox(height: 18),
                                _AmberButton(
                                  icon: Icons.route_rounded,
                                  label: 'Apply & Generate Roadmap',
                                  onTap: onApply,
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
              const SizedBox(width: 34),
              Expanded(
                flex: 3,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Text(
                          'OTHER HIGH MATCHES',
                          style: TextStyle(
                            color: _ink,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 3,
                          ),
                        ),
                        Spacer(),
                        Text(
                          'View All',
                          style: TextStyle(
                            color: _secondary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 22),
                    _GrantMatchCard(
                      source: 'NSF - Convergence Accelerator',
                      title: 'Sustainable Materials Development',
                      score: '88%',
                      body:
                          'Strong patent overlap detected in polymer synthesis sub-category.',
                      onApply: onApply,
                    ),
                    const SizedBox(height: 22),
                    _GrantMatchCard(
                      source: 'NIH - R01 Research',
                      title: 'Advanced Biomarkers for Early Detection',
                      score: '82%',
                      body:
                          'Gap: Lacking required preliminary in-vivo data subset.',
                      hasGap: true,
                      onApply: onApply,
                    ),
                    const SizedBox(height: 22),
                    _ConnectSourceCard(),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _CompanyProfileTab extends StatelessWidget {
  const _CompanyProfileTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Expanded(
                child: _PageHeader(
                  title: 'Company Profile',
                  subtitle:
                      'Consolidated view of your registration, onboarding, and organizational narrative.',
                ),
              ),
              _SoftButton(
                icon: Icons.edit_rounded,
                label: 'Edit Profile',
                onTap: () => _showDashboardMessage(context, 'Edit Profile'),
              ),
            ],
          ),
          const SizedBox(height: 30),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Expanded(
                flex: 7,
                child: Column(
                  children: [
                    _BusinessFundamentalsCard(),
                    SizedBox(height: 28),
                    _DocumentRepositoryCard(),
                  ],
                ),
              ),
              SizedBox(width: 34),
              Expanded(
                flex: 3,
                child: Column(
                  children: [
                    _FundingNeedsCard(),
                    SizedBox(height: 28),
                    _TractionCard(),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DraftsTab extends StatelessWidget {
  const _DraftsTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _PageHeader(
            icon: Icons.history_edu_rounded,
            iconColor: _secondary,
            title: 'Roadmaps & Outputs',
            subtitle:
                'View generated grant application roadmaps, check milestones, and download the roadmap package after applying from the Grants tab.',
          ),
          const SizedBox(height: 30),
          LayoutBuilder(
            builder: (context, constraints) {
              const roadmapList = Column(
                children: [
                  _RoadmapOutputCard(
                    title: 'DOE_EERE_CleanEnergy_Roadmap',
                    tag: 'READY',
                    progress: 0.72,
                    grant: 'Clean Energy Infrastructure Deployment Grant',
                    generated: 'Generated just now',
                    accent: _primary,
                  ),
                  SizedBox(height: 26),
                  _RoadmapOutputCard(
                    title: 'NSF_Convergence_Materials_Roadmap',
                    tag: 'GENERATED',
                    progress: 0.56,
                    grant: 'Sustainable Materials Development',
                    generated: 'Generated yesterday',
                    accent: _tertiary,
                  ),
                  SizedBox(height: 26),
                  _RoadmapOutputCard(
                    title: 'NIH_R01_Biomarkers_Readiness_Map',
                    tag: 'DRAFT',
                    progress: 0.38,
                    grant: 'Advanced Biomarkers for Early Detection',
                    generated: 'Generated Oct 2, 2024',
                    accent: Color(0xFF6D797E),
                  ),
                ],
              );

              if (constraints.maxWidth < 980) {
                return const Column(
                  children: [
                    roadmapList,
                    SizedBox(height: 26),
                    _RoadmapSidePanel(),
                  ],
                );
              }

              return const Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(flex: 7, child: roadmapList),
                  SizedBox(width: 34),
                  Expanded(flex: 3, child: _RoadmapSidePanel()),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _PageHeader extends StatelessWidget {
  const _PageHeader({
    required this.title,
    required this.subtitle,
    this.icon,
    this.iconColor = _primary,
  });

  final IconData? icon;
  final Color iconColor;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final titleSize = width < 560 ? 32.0 : (width < 980 ? 38.0 : 44.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            if (icon != null) ...[
              Icon(icon, color: iconColor, size: 24),
              const SizedBox(width: 14),
            ],
            Expanded(
              child: Text(
                title,
                style: TextStyle(
                  color: _ink,
                  fontSize: titleSize,
                  height: 1,
                  fontWeight: FontWeight.w900,
                  letterSpacing: -1.4,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 22),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Text(
            subtitle,
            style: TextStyle(
              color: _muted,
              fontSize: width < 560 ? 16 : 18,
              height: 1.45,
            ),
          ),
        ),
      ],
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.title,
    required this.value,
    required this.caption,
    required this.icon,
    required this.accent,
    this.progress = false,
    this.footer,
  });

  final String title;
  final String value;
  final String caption;
  final IconData icon;
  final Color accent;
  final bool progress;
  final String? footer;

  @override
  Widget build(BuildContext context) {
    return _Panel(
      height: 190,
      radius: 48,
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 2.4,
                  ),
                ),
              ),
              Icon(icon, color: accent, size: 22),
            ],
          ),
          const Spacer(),
          Text(
            value,
            style: TextStyle(
              color: value == 'Good' ? _ink : accent,
              fontSize: value == 'Good' ? 36 : 50,
              height: 0.95,
              fontWeight: FontWeight.w900,
              letterSpacing: -2,
            ),
          ),
          const SizedBox(height: 10),
          Text(caption, style: const TextStyle(color: _muted, fontSize: 16)),
          if (progress) ...[
            const SizedBox(height: 18),
            const _StackedProgress(),
          ],
          if (footer != null) ...[
            const SizedBox(height: 18),
            Row(
              children: [
                const Icon(Icons.check_circle, color: _primary, size: 16),
                const SizedBox(width: 8),
                Text(
                  footer!,
                  style: const TextStyle(color: _muted, fontSize: 13),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _StackedProgress extends StatelessWidget {
  const _StackedProgress();

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: Row(
        children: const [
          Expanded(
            flex: 40,
            child: ColoredBox(color: _primary, child: SizedBox(height: 8)),
          ),
          Expanded(
            flex: 35,
            child: ColoredBox(color: _tertiary, child: SizedBox(height: 8)),
          ),
          Expanded(
            flex: 25,
            child: ColoredBox(color: _secondary, child: SizedBox(height: 8)),
          ),
        ],
      ),
    );
  }
}

class _GrantMiniData {
  const _GrantMiniData({
    required this.label,
    required this.title,
    required this.amount,
    required this.due,
    this.note,
    this.progress,
    this.ready = false,
  });

  final String label;
  final String title;
  final String amount;
  final String due;
  final String? note;
  final double? progress;
  final bool ready;
}

class _PipelineColumn extends StatelessWidget {
  const _PipelineColumn({
    required this.title,
    required this.count,
    required this.dot,
    required this.cards,
  });

  final String title;
  final String count;
  final Color dot;
  final List<_GrantMiniData> cards;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(color: dot, shape: BoxShape.circle),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 2,
                  ),
                ),
              ),
              _CountPill(count),
            ],
          ),
          const SizedBox(height: 26),
          for (final card in cards) ...[
            _PipelineCard(data: card, accent: dot),
            const SizedBox(height: 18),
          ],
        ],
      ),
    );
  }
}

class _PipelineCard extends StatelessWidget {
  const _PipelineCard({required this.data, required this.accent});

  final _GrantMiniData data;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: data.ready
            ? _primary.withValues(alpha: 0.08)
            : Colors.white.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(34),
        border: Border(left: BorderSide(color: accent, width: 4)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D191C1E),
            blurRadius: 14,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _Tag(
                text: data.label,
                bg: accent.withValues(alpha: 0.10),
                fg: accent,
              ),
              const Spacer(),
              if (data.ready)
                const Icon(Icons.check_circle, color: _primary, size: 18),
            ],
          ),
          const SizedBox(height: 22),
          Text(
            data.title,
            style: const TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.w900,
              height: 1.15,
            ),
          ),
          if (data.note != null) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                const Icon(Icons.auto_awesome, color: _tertiary, size: 14),
                const SizedBox(width: 4),
                Text(data.note!, style: const TextStyle(color: _tertiary)),
              ],
            ),
          ],
          if (data.progress != null) ...[
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: LinearProgressIndicator(
                value: data.progress,
                minHeight: 7,
                backgroundColor: _surfaceLow,
                color: accent,
              ),
            ),
          ],
          const SizedBox(height: 22),
          Row(
            children: [
              Text(
                data.amount,
                style: const TextStyle(
                  color: _primary,
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const Spacer(),
              data.ready
                  ? Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 9,
                      ),
                      decoration: BoxDecoration(
                        color: _primary,
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: const Text(
                        'Submit',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    )
                  : Text(
                      data.due,
                      style: TextStyle(
                        color: data.due.contains('in') ? _error : _muted,
                        fontWeight: data.due.contains('in')
                            ? FontWeight.w800
                            : FontWeight.w500,
                      ),
                    ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GrantMatchCard extends StatelessWidget {
  const _GrantMatchCard({
    required this.source,
    required this.title,
    required this.score,
    required this.body,
    required this.onApply,
    this.hasGap = false,
  });

  final String source;
  final String title;
  final String score;
  final String body;
  final VoidCallback onApply;
  final bool hasGap;

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 34,
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  source,
                  style: const TextStyle(
                    color: _muted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              _Tag(text: score, bg: _surfaceLow, fg: _primary),
            ],
          ),
          const SizedBox(height: 18),
          Text(
            title,
            style: const TextStyle(
              color: _ink,
              fontSize: 21,
              fontWeight: FontWeight.w900,
              height: 1.15,
            ),
          ),
          const SizedBox(height: 18),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 6,
                height: 6,
                margin: const EdgeInsets.only(top: 8),
                decoration: BoxDecoration(
                  color: hasGap ? _error : _tertiary,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  body,
                  style: TextStyle(
                    color: hasGap ? const Color(0xFF7D1A1A) : _muted,
                    height: 1.35,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Align(
            alignment: Alignment.centerRight,
            child: _SoftButton(
              icon: Icons.route_rounded,
              label: 'Apply',
              onTap: onApply,
            ),
          ),
        ],
      ),
    );
  }
}

class _ConnectSourceCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 34),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        border: Border.all(color: _outline, width: 2),
      ),
      child: const Column(
        children: [
          CircleAvatar(
            backgroundColor: _surfaceLow,
            child: Icon(Icons.add_link_rounded, color: _muted),
          ),
          SizedBox(height: 16),
          Text(
            'Connect New Data Source',
            style: TextStyle(
              color: _ink,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            ),
          ),
          SizedBox(height: 6),
          Text('Expand evaluation context', style: TextStyle(color: _muted)),
        ],
      ),
    );
  }
}

class _EvidenceTile extends StatelessWidget {
  const _EvidenceTile({
    required this.icon,
    required this.title,
    required this.body,
  });

  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _surfaceLow.withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: _primary.withValues(alpha: 0.12),
            child: Icon(icon, color: _primary, size: 18),
          ),
          const SizedBox(width: 18),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(body, style: const TextStyle(color: _muted, height: 1.45)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _GapPanel extends StatelessWidget {
  const _GapPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: const Color(0xFFFFEDEA),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _error.withValues(alpha: 0.20)),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.error_rounded, color: _error, size: 18),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'REQUIREMENT GAP',
                  style: TextStyle(
                    color: _error,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 2,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  'Missing: Export Compliance Certificate (Form 89-B). Required for international deployment phase.',
                  style: TextStyle(
                    color: Color(0xFF93000A),
                    height: 1.45,
                    fontSize: 16,
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

class _BusinessFundamentalsCard extends StatelessWidget {
  const _BusinessFundamentalsCard();

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 46,
      padding: const EdgeInsets.all(34),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          _CardTitle(
            icon: Icons.corporate_fare_rounded,
            title: 'Business Fundamentals',
            color: _primary,
          ),
          SizedBox(height: 30),
          _ProfileField(
            label: 'Legal Entity Name',
            value: 'Nexus Dynamics Sdn Bhd',
            prominent: true,
          ),
          SizedBox(height: 26),
          Row(
            children: [
              Expanded(
                child: _ProfileField(
                  label: 'Industry Vertical',
                  value: 'Information & Communication Tech (ICT)',
                  pill: true,
                ),
              ),
              SizedBox(width: 32),
              Expanded(
                child: _ProfileField(
                  label: 'Business Stage',
                  value: 'Early Stage / MVP',
                  pill: true,
                  teal: true,
                ),
              ),
            ],
          ),
          SizedBox(height: 30),
          _ProfileField(
            label: 'Business Description',
            value:
                'Nexus Dynamics develops AI-driven predictive maintenance software for the manufacturing sector. Our core platform utilizes machine learning algorithms to analyze sensor data from industrial machinery, predicting failures before they occur and minimizing costly downtime. We aim to transition traditional manufacturing into Industry 4.0 compliant smart factories.',
            boxed: true,
          ),
          SizedBox(height: 22),
          _ProfileField(
            label: 'Problem Solved',
            value:
                'Unplanned equipment downtime costs the global manufacturing industry an estimated \$50 billion annually. Current preventative maintenance schedules are often inefficient, replacing parts prematurely or failing to catch irregular faults. Our solution bridges the gap between reactive repairs and calendar-based maintenance with precise, data-backed predictions.',
            boxed: true,
          ),
        ],
      ),
    );
  }
}

class _DocumentRepositoryCard extends StatelessWidget {
  const _DocumentRepositoryCard();

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 46,
      padding: const EdgeInsets.all(34),
      child: Column(
        children: const [
          Row(
            children: [
              _CardTitle(
                icon: Icons.folder_rounded,
                title: 'Document Repository',
                color: _secondary,
              ),
              Spacer(),
              Text(
                'View All ->',
                style: TextStyle(color: _primary, fontWeight: FontWeight.w700),
              ),
            ],
          ),
          SizedBox(height: 30),
          Row(
            children: [
              Expanded(
                child: _DocumentCard(
                  icon: Icons.picture_as_pdf_rounded,
                  tag: 'SSM',
                  title: 'SSM_Registration_2023.pdf',
                  color: _error,
                ),
              ),
              SizedBox(width: 18),
              Expanded(
                child: _DocumentCard(
                  icon: Icons.slideshow_rounded,
                  tag: 'Pitch',
                  title: 'Nexus_InvestorDeck_v2.pptx',
                  color: _tertiary,
                ),
              ),
              SizedBox(width: 18),
              Expanded(
                child: _DocumentCard(
                  icon: Icons.table_chart_rounded,
                  tag: 'Financials',
                  title: 'Proj_Financials_24_26.xlsx',
                  color: _secondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _FundingNeedsCard extends StatelessWidget {
  const _FundingNeedsCard();

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 42,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          _CardTitle(
            icon: Icons.payments_rounded,
            title: 'Funding Needs',
            color: _secondary,
            small: true,
          ),
          SizedBox(height: 30),
          Text('Total Amount Requested', style: TextStyle(color: _muted)),
          SizedBox(height: 8),
          Text(
            'RM 500,000',
            style: TextStyle(
              color: _ink,
              fontSize: 31,
              fontWeight: FontWeight.w900,
              letterSpacing: -1,
            ),
          ),
          SizedBox(height: 28),
          Text(
            'Intended Use of Funds',
            style: TextStyle(color: _ink, fontWeight: FontWeight.w600),
          ),
          SizedBox(height: 16),
          _UseOfFunds(
            color: _primary,
            title: 'Product Development (40%)',
            subtitle: 'Finalizing V1.0 predictive algorithms.',
          ),
          _UseOfFunds(
            color: _secondary,
            title: 'Talent Acquisition (35%)',
            subtitle: 'Hiring 2 Senior Data Scientists.',
          ),
          _UseOfFunds(
            color: _tertiary,
            title: 'Marketing & Sales (25%)',
            subtitle: 'Pilot program rollouts in Klang Valley.',
          ),
        ],
      ),
    );
  }
}

class _TractionCard extends StatelessWidget {
  const _TractionCard();

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 42,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          _CardTitle(
            icon: Icons.trending_up_rounded,
            title: 'Traction & Progress',
            color: _tertiary,
            small: true,
          ),
          SizedBox(height: 28),
          _MetricProgress(
            label: 'Current Revenue (MRR)',
            value: 'RM 15,000',
            progress: 0.25,
            color: _tertiary,
          ),
          SizedBox(height: 24),
          _MetricProgress(
            label: 'Active Pilot Users',
            value: '4 Factories',
            progress: 0.40,
            color: _primary,
          ),
          SizedBox(height: 28),
          Text('Key Partnerships', style: TextStyle(color: _muted)),
          SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _Tag(
                text: 'TechHub MY',
                bg: Colors.white,
                fg: _ink,
                icon: Icons.handshake_rounded,
              ),
              _Tag(
                text: 'IoT Assoc.',
                bg: Colors.white,
                fg: _ink,
                icon: Icons.handshake_rounded,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RoadmapOutputCard extends StatelessWidget {
  const _RoadmapOutputCard({
    required this.title,
    required this.tag,
    required this.progress,
    required this.grant,
    required this.generated,
    required this.accent,
  });

  final String title;
  final String tag;
  final double progress;
  final String grant;
  final String generated;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 38,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                radius: 28,
                backgroundColor: accent.withValues(alpha: 0.12),
                child: Icon(Icons.route_rounded, color: accent, size: 28),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: _ink,
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              letterSpacing: -0.5,
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Flexible(
                          flex: 0,
                          child: _Tag(
                            text: tag,
                            bg: accent.withValues(alpha: 0.10),
                            fg: accent,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      grant,
                      style: const TextStyle(color: _muted, fontSize: 16),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      generated,
                      style: const TextStyle(color: Color(0xFF768190)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 28),
          Row(
            children: [
              Expanded(
                child: _RoadmapStep(
                  label: 'Profile Fit',
                  done: progress >= 0.25,
                  accent: accent,
                ),
              ),
              Expanded(
                child: _RoadmapStep(
                  label: 'Gap Closure',
                  done: progress >= 0.50,
                  accent: accent,
                ),
              ),
              Expanded(
                child: _RoadmapStep(
                  label: 'Submission Pack',
                  done: progress >= 0.75,
                  accent: accent,
                ),
              ),
              Expanded(
                child: _RoadmapStep(
                  label: 'Final Review',
                  done: progress >= 0.95,
                  accent: accent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 28),
          Wrap(
            spacing: 14,
            runSpacing: 12,
            children: [
              _SoftButton(
                icon: Icons.visibility_rounded,
                label: 'View Roadmap',
                onTap: () => _showDashboardMessage(context, 'Roadmap Preview'),
              ),
              _PrimaryButton(
                icon: Icons.download_rounded,
                label: 'Download',
                onTap: () => _showDashboardMessage(context, 'Roadmap Download'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RoadmapStep extends StatelessWidget {
  const _RoadmapStep({
    required this.label,
    required this.done,
    required this.accent,
  });

  final String label;
  final bool done;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            CircleAvatar(
              radius: 12,
              backgroundColor: done ? accent : _surfaceLow,
              child: Icon(
                done ? Icons.check_rounded : Icons.more_horiz_rounded,
                color: done ? Colors.white : _muted,
                size: 16,
              ),
            ),
            Expanded(
              child: Container(
                height: 3,
                color: done ? accent.withValues(alpha: 0.45) : _surfaceLow,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Text(
          label,
          style: TextStyle(
            color: done ? _ink : _muted,
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _RoadmapSidePanel extends StatelessWidget {
  const _RoadmapSidePanel();

  @override
  Widget build(BuildContext context) {
    return _Panel(
      radius: 38,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            'FILTER BY',
            style: TextStyle(
              color: _ink,
              fontWeight: FontWeight.w900,
              letterSpacing: 3,
            ),
          ),
          SizedBox(height: 24),
          _CheckRow(label: 'All Roadmaps', checked: true),
          _CheckRow(label: 'Ready to Execute'),
          _CheckRow(label: 'In Progress'),
          SizedBox(height: 26),
          Divider(color: _outline),
          SizedBox(height: 26),
          Text(
            'RECENT ACTIVITY',
            style: TextStyle(
              color: _ink,
              fontWeight: FontWeight.w900,
              letterSpacing: 3,
            ),
          ),
          SizedBox(height: 22),
          _ActivityDot(
            color: _secondary,
            title: 'Generated Roadmap',
            detail: 'DOE_EERE_CleanEnergy - just now',
          ),
          SizedBox(height: 18),
          _ActivityDot(
            color: _primary,
            title: 'Applied to Grant',
            detail: 'NSF_Convergence - 1d ago',
          ),
        ],
      ),
    );
  }
}

class _CheckRow extends StatelessWidget {
  const _CheckRow({required this.label, this.checked = false});

  final String label;
  final bool checked;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: checked ? _primary : Colors.transparent,
            child: checked
                ? const Icon(Icons.check_rounded, color: Colors.white, size: 16)
                : Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: _muted),
                    ),
                  ),
          ),
          const SizedBox(width: 14),
          Text(label, style: const TextStyle(color: _ink, fontSize: 16)),
        ],
      ),
    );
  }
}

class _ActivityDot extends StatelessWidget {
  const _ActivityDot({
    required this.color,
    required this.title,
    required this.detail,
  });

  final Color color;
  final String title;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 8,
          height: 8,
          margin: const EdgeInsets.only(top: 7),
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(color: _ink, fontSize: 15)),
              Text(detail, style: const TextStyle(color: _muted, fontSize: 13)),
            ],
          ),
        ),
      ],
    );
  }
}

class _ProfileField extends StatelessWidget {
  const _ProfileField({
    required this.label,
    required this.value,
    this.prominent = false,
    this.pill = false,
    this.teal = false,
    this.boxed = false,
  });

  final String label;
  final String value;
  final bool prominent;
  final bool pill;
  final bool teal;
  final bool boxed;

  @override
  Widget build(BuildContext context) {
    final valueWidget = pill
        ? Align(
            alignment: Alignment.centerLeft,
            child: _Tag(
              text: value,
              bg: teal ? _primary.withValues(alpha: 0.10) : _surfaceLow,
              fg: teal ? _primary : _ink,
            ),
          )
        : Text(
            value,
            style: TextStyle(
              color: _ink,
              fontSize: prominent ? 20 : 16,
              height: 1.6,
              fontWeight: prominent ? FontWeight.w800 : FontWeight.w500,
            ),
          );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: _muted, fontSize: 14)),
        const SizedBox(height: 8),
        boxed
            ? Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.62),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: _outline.withValues(alpha: 0.75)),
                ),
                child: valueWidget,
              )
            : valueWidget,
      ],
    );
  }
}

class _DocumentCard extends StatelessWidget {
  const _DocumentCard({
    required this.icon,
    required this.tag,
    required this.title,
    required this.color,
  });

  final IconData icon;
  final String tag;
  final String title;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.78),
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: _outline.withValues(alpha: 0.75)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                backgroundColor: color.withValues(alpha: 0.12),
                child: Icon(icon, color: color, size: 20),
              ),
              const Spacer(),
              _Tag(text: tag, bg: _surfaceLow, fg: _muted),
            ],
          ),
          const SizedBox(height: 22),
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: _ink,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Uploaded recently - 2.4 MB',
            style: TextStyle(color: _muted, fontSize: 12),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(child: _TinyButton(label: 'View')),
              const SizedBox(width: 10),
              Expanded(
                child: _TinyButton(label: 'Update', color: _primary),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _UseOfFunds extends StatelessWidget {
  const _UseOfFunds({
    required this.color,
    required this.title,
    required this.subtitle,
  });

  final Color color;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: _surfaceLow,
            child: CircleAvatar(radius: 4, backgroundColor: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: _ink,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(color: _muted, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricProgress extends StatelessWidget {
  const _MetricProgress({
    required this.label,
    required this.value,
    required this.progress,
    required this.color,
  });

  final String label;
  final String value;
  final double progress;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: Text(label, style: const TextStyle(color: _muted)),
            ),
            Text(
              value,
              style: const TextStyle(
                color: _ink,
                fontSize: 18,
                fontWeight: FontWeight.w900,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 7,
            backgroundColor: _surfaceLow,
            color: color,
          ),
        ),
      ],
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({
    required this.icon,
    required this.text,
    required this.color,
  });

  final IconData icon;
  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(width: 10),
        Text(
          text,
          style: const TextStyle(
            color: _ink,
            fontWeight: FontWeight.w900,
            letterSpacing: 3,
          ),
        ),
      ],
    );
  }
}

class _CardTitle extends StatelessWidget {
  const _CardTitle({
    required this.icon,
    required this.title,
    required this.color,
    this.small = false,
  });

  final IconData icon;
  final String title;
  final Color color;
  final bool small;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        CircleAvatar(
          radius: 21,
          backgroundColor: color.withValues(alpha: 0.12),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(width: 16),
        Text(
          title,
          style: TextStyle(
            color: _ink,
            fontSize: small ? 22 : 25,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.4,
          ),
        ),
      ],
    );
  }
}

class _Glass extends StatelessWidget {
  const _Glass({
    required this.child,
    this.margin,
    this.padding,
    this.radius = 30,
    this.width,
  });

  final Widget child;
  final EdgeInsetsGeometry? margin;
  final EdgeInsetsGeometry? padding;
  final double radius;
  final double? width;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      margin: margin,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
          child: Container(
            padding: padding,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.74),
              borderRadius: BorderRadius.circular(radius),
              border: Border.all(color: Colors.white.withValues(alpha: 0.65)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x10191C1E),
                  blurRadius: 42,
                  offset: Offset(0, 18),
                ),
              ],
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}

class _Panel extends StatelessWidget {
  const _Panel({
    required this.child,
    this.padding = const EdgeInsets.all(24),
    this.radius = 34,
    this.height,
    this.color,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;
  final double? height;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        color: color ?? _surface.withValues(alpha: 0.84),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: _outline.withValues(alpha: 0.74)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0F191C1E),
            blurRadius: 36,
            offset: Offset(0, 18),
          ),
        ],
      ),
      child: child,
    );
  }
}

class _Tag extends StatelessWidget {
  const _Tag({
    required this.text,
    required this.bg,
    required this.fg,
    this.icon,
  });

  final String text;
  final Color bg;
  final Color fg;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: fg),
            const SizedBox(width: 5),
          ],
          Text(
            text,
            style: TextStyle(
              color: fg,
              fontSize: 12,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.2,
            ),
          ),
        ],
      ),
    );
  }
}

class _CountPill extends StatelessWidget {
  const _CountPill(this.count);

  final String count;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFECEFF2),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(count, style: const TextStyle(color: _muted, fontSize: 12)),
    );
  }
}

class _SoftButton extends StatelessWidget {
  const _SoftButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18),
      label: Text(label),
      style: OutlinedButton.styleFrom(
        foregroundColor: _primary,
        backgroundColor: Colors.white.withValues(alpha: 0.70),
        side: const BorderSide(color: _outline),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        shape: const StadiumBorder(),
        textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
      ),
    );
  }
}

class _PrimaryButton extends StatelessWidget {
  const _PrimaryButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18),
      label: Text(label),
      style: FilledButton.styleFrom(
        backgroundColor: _primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: const StadiumBorder(),
        textStyle: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15),
      ),
    );
  }
}

class _AmberButton extends StatelessWidget {
  const _AmberButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 22),
      label: Text(label),
      style: FilledButton.styleFrom(
        backgroundColor: _secondary,
        foregroundColor: Colors.white,
        minimumSize: const Size.fromHeight(64),
        shape: const StadiumBorder(),
        elevation: 12,
        shadowColor: _secondary.withValues(alpha: 0.35),
        textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
      ),
    );
  }
}

class _TinyButton extends StatelessWidget {
  const _TinyButton({required this.label, this.color = _ink});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: () => _showDashboardMessage(context, label),
      style: OutlinedButton.styleFrom(
        foregroundColor: color,
        side: const BorderSide(color: _outline),
        shape: const StadiumBorder(),
      ),
      child: Text(label),
    );
  }
}
