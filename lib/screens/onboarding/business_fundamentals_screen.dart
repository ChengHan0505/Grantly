import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';
import 'document_vault_screen.dart';
import 'initialize_screen.dart';

class BusinessFundamentalsScreen extends StatefulWidget {
  const BusinessFundamentalsScreen({super.key});

  static const String routeName = '/business-fundamentals';

  @override
  State<BusinessFundamentalsScreen> createState() => _BusinessFundamentalsScreenState();
}

class _BusinessFundamentalsScreenState extends State<BusinessFundamentalsScreen> {
  final Set<String> _selectedTraction = {'Revenue', 'Users'};
  String _businessStage = 'MVP';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          color: Color(0xFFF4F8FC),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const _NavBar(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 20),
                  child: Column(
                    children: [
                      const _StepHeader(step: 2, progressLabel: '66% Complete', progress: 0.66),
                      const SizedBox(height: 12),
                      Container(
                        constraints: const BoxConstraints(maxWidth: 1020),
                        padding: const EdgeInsets.fromLTRB(46, 34, 46, 30),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.94),
                          borderRadius: BorderRadius.circular(28),
                          border: Border.all(color: const Color(0xFFE6ECF3)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Center(
                              child: Container(
                                width: 54,
                                height: 54,
                                decoration: const BoxDecoration(
                                  color: Color(0xFFE4F4FB),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.work_outline, color: AppTheme.accentTeal),
                              ),
                            ),
                            const SizedBox(height: 10),
                            const Center(
                              child: Text(
                                'Business Fundamentals',
                                style: TextStyle(fontSize: 52, fontWeight: FontWeight.w800),
                              ),
                            ),
                            const SizedBox(height: 6),
                            const Center(
                              child: Text(
                                "Let's understand your impact.",
                                style: TextStyle(fontSize: 24, color: AppTheme.mutedInk),
                              ),
                            ),
                            const SizedBox(height: 24),
                            const _SectionLabel('What does your business do & what problem are you solving?'),
                            const SizedBox(height: 8),
                            const TextField(
                              maxLines: 4,
                              decoration: InputDecoration(
                                hintText:
                                    'Describe your mission, the gap in the market, and how your solution bridges it...',
                              ),
                            ),
                            const SizedBox(height: 16),
                            const _SectionLabel('Which industry/sector does your company belong to?'),
                            const SizedBox(height: 8),
                            const TextField(
                              decoration: InputDecoration(
                                hintText: 'e.g., ICT, Medical, Cleantech, EdTech...',
                              ),
                            ),
                            const SizedBox(height: 16),
                            const _SectionLabel('What stage is your business currently at?'),
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 10,
                              runSpacing: 10,
                              children: ['Idea', 'Prototype', 'MVP', 'Revenue', 'Scaling']
                                  .map(
                                    (stage) => _SelectableChip(
                                      label: stage,
                                      selected: _businessStage == stage,
                                      onTap: () => setState(() => _businessStage = stage),
                                      selectedColor: const Color(0xFFD9F2FF),
                                    ),
                                  )
                                  .toList(),
                            ),
                            const SizedBox(height: 18),
                            const _SectionLabel('What is your current traction or progress?'),
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 10,
                              runSpacing: 10,
                              children: ['Revenue', 'Users', 'Partnerships', 'Product Completed', 'Other']
                                  .map(
                                    (item) => _SelectableChip(
                                      label: item,
                                      selected: _selectedTraction.contains(item),
                                      onTap: () {
                                        setState(() {
                                          if (_selectedTraction.contains(item)) {
                                            _selectedTraction.remove(item);
                                          } else {
                                            _selectedTraction.add(item);
                                          }
                                        });
                                      },
                                      selectedColor: const Color(0xFFFBE8C8),
                                    ),
                                  )
                                  .toList(),
                            ),
                            const SizedBox(height: 16),
                            const _SectionLabel('How much funding do you need & what will you use it for?'),
                            const SizedBox(height: 8),
                            const TextField(
                              maxLines: 4,
                              decoration: InputDecoration(
                                hintText:
                                    'Detail your budget allocation, critical hires, equipment needs...',
                              ),
                            ),
                            const SizedBox(height: 24),
                            Row(
                              children: [
                                TextButton.icon(
                                  onPressed: () => Navigator.pushNamed(context, InitializeScreen.routeName),
                                  icon: const Icon(Icons.arrow_back),
                                  label: const Text('Back'),
                                ),
                                const Spacer(),
                                InkWell(
                                  onTap: () =>
                                      Navigator.pushNamed(context, DocumentVaultScreen.routeName),
                                  borderRadius: BorderRadius.circular(999),
                                  child: Ink(
                                    decoration: AppTheme.gradientButton,
                                    padding:
                                        const EdgeInsets.symmetric(horizontal: 22, vertical: 12),
                                    child: const Row(
                                      children: [
                                        Text(
                                          'Next',
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        SizedBox(width: 8),
                                        Icon(Icons.arrow_forward, color: Colors.white, size: 18),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
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
  const _StepHeader({
    required this.step,
    required this.progressLabel,
    required this.progress,
  });

  final int step;
  final String progressLabel;
  final double progress;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 1020),
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
                widthFactor: progress,
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

class _SectionLabel extends StatelessWidget {
  const _SectionLabel(this.text);

  final String text;

  final TextStyle _style = const TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w600,
    color: AppTheme.ink,
  );

  @override
  Widget build(BuildContext context) => Text(text, style: _style);
}

class _SelectableChip extends StatelessWidget {
  const _SelectableChip({
    required this.label,
    required this.selected,
    required this.onTap,
    required this.selectedColor,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;
  final Color selectedColor;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
          decoration: BoxDecoration(
            color: selected ? selectedColor : const Color(0xFFF2F4F7),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: selected ? const Color(0xFF8DC7E6) : const Color(0xFFE1E7EE),
            ),
          ),
          child: Text(
            label,
            style: TextStyle(
              color: selected ? AppTheme.ink : const Color(0xFF555F70),
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}
