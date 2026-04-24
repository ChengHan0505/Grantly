import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

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
    final pages = [
      const _HomeTab(),
      const _GrantTab(),
      const _OutputTab(),
      const _CompanyProfileTab(),
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1450),
            child: Column(
              children: [
                const _TopNav(),
                Expanded(
                  child: Row(
                    children: [
                      _SideRail(
                        selected: _tab,
                        onTap: (index) => setState(() => _tab = index),
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(0, 6, 18, 12),
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
    );
  }
}

class _TopNav extends StatelessWidget {
  const _TopNav();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(14, 8, 14, 4),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: const Color(0xFFE6EBF2)),
      ),
      child: Row(
        children: const [
          Icon(Icons.auto_awesome, size: 16, color: Color(0xFF1D91AF)),
          SizedBox(width: 6),
          Text(
            'Grantly',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
          ),
          Spacer(),
          Icon(Icons.language, size: 16, color: Color(0xFF616D7E)),
          SizedBox(width: 16),
          Icon(Icons.notifications, size: 16, color: Color(0xFF616D7E)),
          SizedBox(width: 16),
          CircleAvatar(radius: 13, backgroundColor: Color(0xFF18212A)),
        ],
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
      Icons.folder_open_rounded,
      Icons.auto_awesome_motion_rounded,
      Icons.domain_rounded,
    ];
    return Container(
      width: 70,
      margin: const EdgeInsets.fromLTRB(8, 6, 14, 16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFD),
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: const Color(0xFFE6EBF2)),
      ),
      child: Column(
        children: [
          const SizedBox(height: 18),
          for (var i = 0; i < items.length; i++)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () => onTap(i),
                child: Ink(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: selected == i
                        ? const Color(0xFF1AB8DF)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(21),
                    boxShadow: selected == i
                        ? const [
                            BoxShadow(
                              color: Color(0x331AB8DF),
                              blurRadius: 10,
                              offset: Offset(0, 5),
                            ),
                          ]
                        : null,
                  ),
                  child: Icon(
                    items[i],
                    size: 18,
                    color: selected == i
                        ? Colors.white
                        : const Color(0xFF8A96A9),
                  ),
                ),
              ),
            ),
          const Spacer(),
          const Icon(Icons.logout_rounded, size: 18, color: Color(0xFF97A4B8)),
          const SizedBox(height: 14),
        ],
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
          Row(
            children: const [
              Expanded(
                child: _MetricTopCard(
                  title: 'READINESS SCORE',
                  big: '88.4%',
                  sub: '+2.1% from last audit',
                  accent: Color(0xFF007C99),
                ),
              ),
              SizedBox(width: 14),
              Expanded(
                child: _MetricTopCard(
                  title: 'ACTIVE PIPELINE',
                  big: '12',
                  sub: '3 grants requiring attention',
                  accent: Color(0xFF4C4ED6),
                ),
              ),
              SizedBox(width: 14),
              Expanded(
                child: _MetricTopCard(
                  title: 'DOCUMENT HEALTH',
                  big: 'Good',
                  sub: '92% metadata completion',
                  accent: Color(0xFFAB6400),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFFF3F6FA),
              borderRadius: BorderRadius.circular(28),
              border: Border.all(color: const Color(0xFFE4EAF2)),
            ),
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
                            fontSize: 40,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        Text(
                          'Real-time status of targeted opportunities',
                          style: TextStyle(color: Color(0xFF556173)),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF9FBFD),
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(color: const Color(0xFFE3E8EF)),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.filter_list_rounded,
                            size: 16,
                            color: Color(0xFF3D7B8E),
                          ),
                          SizedBox(width: 8),
                          Text(
                            'Filter Views',
                            style: TextStyle(
                              color: Color(0xFF3D7B8E),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: const [
                    _PipelineCol(
                      title: 'DISCOVERED',
                      count: '4',
                      border: Color(0xFFB6B9BE),
                      cardTitle: 'NSF AI Research Grant',
                      amount: '\$2.5M',
                      due: 'Due Oct 15',
                    ),
                    SizedBox(width: 12),
                    _PipelineCol(
                      title: 'AUDITED',
                      count: '2',
                      border: Color(0xFF7A78E8),
                      cardTitle: 'CA Clean Energy Init',
                      amount: '\$1.2M',
                      due: 'Due Sep 30',
                    ),
                    SizedBox(width: 12),
                    _PipelineCol(
                      title: 'DRAFTING',
                      count: '3',
                      border: Color(0xFFC08933),
                      cardTitle: 'Google Tech Impact',
                      amount: '\$750k',
                      due: 'Due in 5d',
                    ),
                    SizedBox(width: 12),
                    _PipelineCol(
                      title: 'READY',
                      count: '1',
                      border: Color(0xFF118795),
                      cardTitle: 'NIH Early Stage Dev',
                      amount: '\$3.0M',
                      due: 'Submit',
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Align(
            alignment: Alignment.bottomRight,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: const Color(0xFFE4EAF2)),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 11),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.auto_awesome,
                    color: AppTheme.accentTeal,
                    size: 18,
                  ),
                  SizedBox(width: 8),
                  Text(
                    'Ask Copilot',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  SizedBox(width: 8),
                  CircleAvatar(radius: 3, backgroundColor: Color(0xFF22BACF)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GrantTab extends StatelessWidget {
  const _GrantTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(
                      Icons.auto_graph_rounded,
                      size: 18,
                      color: Color(0xFFAA6909),
                    ),
                    SizedBox(width: 8),
                    Text(
                      'Evaluate Logic',
                      style: TextStyle(
                        fontSize: 62,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Analyzing alignment across 42 active funding sources. The system is warming up\n'
                  'narrative constructs based on strong foundational evidence traces.',
                  style: TextStyle(fontSize: 20, color: AppTheme.mutedInk),
                ),
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(color: const Color(0xFFE4EAF2)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          _Tag(
                            text: 'DOE - EERE',
                            bg: Color(0xFFF1F2F6),
                            fg: Color(0xFF495668),
                          ),
                          SizedBox(width: 8),
                          _Tag(
                            text: 'High Confidence',
                            bg: Color(0xFFEFEAFE),
                            fg: Color(0xFF5748B5),
                          ),
                          Spacer(),
                          CircleAvatar(
                            radius: 42,
                            backgroundColor: Color(0xFFF7D8A8),
                            child: Text(
                              '94%',
                              style: TextStyle(
                                fontSize: 38,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Clean Energy Infrastructure\nDeployment Grant',
                        style: TextStyle(
                          fontSize: 48,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text('FOA-0002894 - Deadline: Oct 15, 2024'),
                      const SizedBox(height: 14),
                      const Row(
                        children: [
                          Expanded(
                            child: _EvidenceItem(
                              title:
                                  "Alignment with 'Decarbonization' objective",
                              subtitle:
                                  'Your prior project demonstrates successful deployment in underserved regions.',
                            ),
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: _EvidenceItem(
                              title: 'REQUIREMENT GAP',
                              subtitle:
                                  'Missing: Export Compliance Certificate (Form 89-B). Required for international deployment phase.',
                              warn: true,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      const _GoldButton(label: 'Generate Proposal Draft'),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Text(
                      'OTHER HIGH MATCHES',
                      style: TextStyle(
                        letterSpacing: 2,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Spacer(),
                    Text(
                      'View All',
                      style: TextStyle(color: Color(0xFF9B6F45)),
                    ),
                  ],
                ),
                SizedBox(height: 12),
                const _SimplePanel(
                  title: 'Sustainable Materials Development',
                  subtitle: '88%',
                ),
                SizedBox(height: 10),
                const _SimplePanel(
                  title: 'Advanced Biomarkers for Early Detection',
                  subtitle: '82%',
                ),
                SizedBox(height: 10),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 28,
                  ),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(
                      color: const Color(0xFFDCE3EC),
                      style: BorderStyle.solid,
                    ),
                  ),
                  child: const Column(
                    children: [
                      Icon(Icons.add_link_rounded, color: Color(0xFF576170)),
                      SizedBox(height: 10),
                      Text(
                        'Connect New Data Source',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Expand evaluation context',
                        style: TextStyle(color: Color(0xFF6D798A)),
                      ),
                    ],
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

class _CompanyProfileTab extends StatelessWidget {
  const _CompanyProfileTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Company Profile',
                style: TextStyle(fontSize: 62, fontWeight: FontWeight.w800),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 9,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: const Color(0xFFE4EAF2)),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.edit_outlined,
                      size: 15,
                      color: Color(0xFF2C7B92),
                    ),
                    SizedBox(width: 6),
                    Text(
                      'Edit Profile',
                      style: TextStyle(
                        color: Color(0xFF2C7B92),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Consolidated view of your registration, onboarding, and organizational narrative.',
            style: TextStyle(fontSize: 20, color: AppTheme.mutedInk),
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Expanded(
                flex: 2,
                child: _BigInfoCard(
                  title: 'Business Fundamentals',
                  body:
                      'Nexus Dynamics develops AI-driven predictive maintenance software for the manufacturing sector. Our core platform utilizes machine learning algorithms to analyze sensor data from industrial machinery, predicting failures before they occur and minimizing costly downtime.',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  children: const [
                    _SimplePanel(
                      title: 'Funding Needs\nRM 500,000',
                      subtitle:
                          'Product Development 40%\nTalent Acquisition 35%\nMarketing & Sales 25%',
                    ),
                    SizedBox(height: 12),
                    _SimplePanel(
                      title: 'Traction & Progress',
                      subtitle:
                          'Current Revenue (MRR)   RM 15,000\nActive Pilot Users        4 Factories',
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const _BigInfoCard(
            title: 'Document Repository',
            body:
                'SSM_Registration_2024.pdf\nNexus_InvestorDeck.pdf\nProj_Financials_24.pdf',
          ),
        ],
      ),
    );
  }
}

class _OutputTab extends StatelessWidget {
  const _OutputTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.rate_review_outlined,
                      size: 18,
                      color: Color(0xFFAA6909),
                    ),
                    SizedBox(width: 8),
                    Text(
                      'Drafts & Outputs',
                      style: TextStyle(
                        fontSize: 62,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  'Review and manage your generated application packages, proposal drafts, and\nsynthesized research outputs.',
                  style: TextStyle(fontSize: 20, color: AppTheme.mutedInk),
                ),
                SizedBox(height: 14),
                _DraftItem(
                  title: 'DOE_EERE_CleanEnergy_Draft_v1.pdf',
                  tag: 'READY FOR REVIEW',
                ),
                SizedBox(height: 12),
                _DraftItem(
                  title: 'NSF_Convergence_Final_Package.zip',
                  tag: 'GENERATED',
                ),
                SizedBox(height: 12),
                _DraftItem(
                  title: 'NIH_R01_Preliminary_Data_Summary.docx',
                  tag: 'DRAFT',
                ),
              ],
            ),
          ),
          SizedBox(width: 14),
          Expanded(
            child: _SimplePanel(
              title: 'FILTER BY',
              subtitle:
                  'All Drafts\nReady for Review\nFinal Packages\n\nRECENT ACTIVITY\nGenerated Narrative Draft\nPackaged Final Application',
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricTopCard extends StatelessWidget {
  const _MetricTopCard({
    required this.title,
    required this.big,
    required this.sub,
    required this.accent,
  });
  final String title;
  final String big;
  final String sub;
  final Color accent;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE3EAF2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(letterSpacing: 1.4)),
          const SizedBox(height: 10),
          Text(
            big,
            style: TextStyle(
              fontSize: 52,
              fontWeight: FontWeight.w800,
              color: accent,
            ),
          ),
          Text(sub, style: const TextStyle(color: AppTheme.mutedInk)),
        ],
      ),
    );
  }
}

class _PipelineCol extends StatelessWidget {
  const _PipelineCol({
    required this.title,
    required this.count,
    required this.border,
    required this.cardTitle,
    required this.amount,
    required this.due,
  });
  final String title;
  final String count;
  final Color border;
  final String cardTitle;
  final String amount;
  final String due;
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: border,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.3,
                ),
              ),
              const Spacer(),
              Text(count, style: const TextStyle(color: Color(0xFF5D6777))),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE3EAF2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(width: 3, height: 42, color: border),
                const SizedBox(height: 8),
                Text(
                  cardTitle,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Text(
                      amount,
                      style: const TextStyle(
                        fontSize: 26,
                        color: AppTheme.accentTeal,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      due,
                      style: TextStyle(
                        color: due.contains('in')
                            ? const Color(0xFFB03A26)
                            : const Color(0xFF5D6777),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _EvidenceItem extends StatelessWidget {
  const _EvidenceItem({
    required this.title,
    required this.subtitle,
    this.warn = false,
  });
  final String title;
  final String subtitle;
  final bool warn;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: warn ? const Color(0xFFFFF5F4) : const Color(0xFFF7FBFF),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: warn ? const Color(0xFFF2B3AC) : const Color(0xFFE0ECF6),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              color: warn ? const Color(0xFFA14034) : null,
            ),
          ),
          const SizedBox(height: 6),
          Text(subtitle, style: const TextStyle(color: AppTheme.mutedInk)),
        ],
      ),
    );
  }
}

class _GoldButton extends StatelessWidget {
  const _GoldButton({required this.label});
  final String label;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF9C5E00),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Center(
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _SimplePanel extends StatelessWidget {
  const _SimplePanel({required this.title, required this.subtitle});
  final String title;
  final String subtitle;
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE3EAF2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          Text(subtitle, style: const TextStyle(color: AppTheme.mutedInk)),
        ],
      ),
    );
  }
}

class _BigInfoCard extends StatelessWidget {
  const _BigInfoCard({required this.title, required this.body});
  final String title;
  final String body;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF9FDFF), Color(0xFFEAF7FF)],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE3EAF2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 36, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 12),
          Text(
            body,
            style: const TextStyle(
              fontSize: 19,
              color: AppTheme.mutedInk,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}

class _DraftItem extends StatelessWidget {
  const _DraftItem({required this.title, required this.tag});
  final String title;
  final String tag;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE3EAF2)),
      ),
      child: Row(
        children: [
          const CircleAvatar(
            backgroundColor: Color(0xFFE7F4FA),
            child: Icon(Icons.description, color: AppTheme.accentTeal),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  tag,
                  style: const TextStyle(
                    letterSpacing: 1.2,
                    color: AppTheme.mutedInk,
                  ),
                ),
              ],
            ),
          ),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.visibility),
            label: const Text('Preview'),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.download),
            label: const Text('Download'),
          ),
        ],
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  const _Tag({required this.text, required this.bg, required this.fg});

  final String text;
  final Color bg;
  final Color fg;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: TextStyle(color: fg, fontWeight: FontWeight.w600),
      ),
    );
  }
}
