import 'dart:ui';

import 'package:flutter/material.dart';

import '../auth/login_screen.dart';
import 'document_vault_screen.dart';
import 'initialize_screen.dart';

class BusinessFundamentalsScreen extends StatefulWidget {
  const BusinessFundamentalsScreen({super.key});

  static const String routeName = '/business-fundamentals';

  @override
  State<BusinessFundamentalsScreen> createState() =>
      _BusinessFundamentalsScreenState();
}

class _BusinessFundamentalsScreenState
    extends State<BusinessFundamentalsScreen> {
  final Set<String> _selectedTraction = {'Revenue', 'Users'};
  String _businessStage = 'MVP';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FB),
      body: Stack(
        children: [
          const Positioned.fill(child: _StepTwoBackground()),
          SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                  child: _OnboardingTopBar(
                    onLogin: () =>
                        Navigator.pushNamed(context, LoginScreen.routeName),
                  ),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 34, 20, 28),
                    child: Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 1040),
                        child: Column(
                          children: [
                            const _StepProgressHeader(
                              stepLabel: 'STEP 2 OF 3',
                              progressLabel: '66% Complete',
                              progress: 0.66,
                            ),
                            const SizedBox(height: 22),
                            _StepTwoCard(
                              selectedStage: _businessStage,
                              selectedTraction: _selectedTraction,
                              onStageChanged: (value) {
                                setState(() => _businessStage = value);
                              },
                              onTractionToggle: (value) {
                                setState(() {
                                  if (_selectedTraction.contains(value)) {
                                    _selectedTraction.remove(value);
                                  } else {
                                    _selectedTraction.add(value);
                                  }
                                });
                              },
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

class _StepTwoBackground extends StatelessWidget {
  const _StepTwoBackground();

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: const [
        ColoredBox(color: Color(0xFFF7F9FB)),
        _SoftGradientOrb(
          alignment: Alignment.topLeft,
          width: 900,
          height: 900,
          offset: Offset(-260, -120),
          colors: [Color(0x3345B1D4), Color(0x0045B1D4)],
        ),
        _SoftGradientOrb(
          alignment: Alignment.bottomRight,
          width: 760,
          height: 760,
          offset: Offset(140, 80),
          colors: [Color(0x26FE932C), Color(0x00FE932C)],
        ),
        _SoftGradientOrb(
          alignment: Alignment.center,
          width: 760,
          height: 760,
          offset: Offset(120, 120),
          colors: [Color(0x16494BD6), Color(0x00494BD6)],
        ),
      ],
    );
  }
}

class _SoftGradientOrb extends StatelessWidget {
  const _SoftGradientOrb({
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

class _OnboardingTopBar extends StatelessWidget {
  const _OnboardingTopBar({required this.onLogin});

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
                  fontSize: extraCompact ? 17 : (compact ? 19 : 22),
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF191C1E),
                  letterSpacing: -0.5,
                ),
              ),
              const Spacer(),
              _LoginButton(onTap: onLogin),
              if (!compact) ...const [
                SizedBox(width: 16),
                _CircleNavIcon(icon: Icons.language),
                SizedBox(width: 12),
                _CircleNavIcon(icon: Icons.notifications),
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

class _LoginButton extends StatelessWidget {
  const _LoginButton({required this.onTap});

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

class _CircleNavIcon extends StatelessWidget {
  const _CircleNavIcon({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 34,
      height: 34,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.16),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 20, color: const Color(0xFF64748B)),
    );
  }
}

class _StepProgressHeader extends StatelessWidget {
  const _StepProgressHeader({
    required this.stepLabel,
    required this.progressLabel,
    required this.progress,
  });

  final String stepLabel;
  final String progressLabel;
  final double progress;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 800),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  stepLabel,
                  style: const TextStyle(
                    fontSize: 14,
                    letterSpacing: 1.8,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF006780),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                progressLabel,
                style: const TextStyle(fontSize: 14, color: Color(0xFF3D494D)),
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
                  widthFactor: progress,
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

class _StepTwoCard extends StatelessWidget {
  const _StepTwoCard({
    required this.selectedStage,
    required this.selectedTraction,
    required this.onStageChanged,
    required this.onTractionToggle,
  });

  final String selectedStage;
  final Set<String> selectedTraction;
  final ValueChanged<String> onStageChanged;
  final ValueChanged<String> onTractionToggle;

  static const _stageOptions = [
    ('Idea', Icons.lightbulb),
    ('Prototype', Icons.architecture),
    ('MVP', Icons.rocket_launch),
    ('Revenue', Icons.payments),
    ('Scaling', Icons.trending_up),
  ];

  static const _tractionOptions = [
    'Revenue',
    'Users',
    'Partnerships',
    'Product Completed',
    'Other',
  ];

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final compact = width < 760;
    final narrow = width < 640;

    return ClipRRect(
      borderRadius: BorderRadius.circular(42),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          padding: EdgeInsets.fromLTRB(
            compact ? 22 : 52,
            compact ? 28 : 46,
            compact ? 22 : 52,
            compact ? 24 : 34,
          ),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.78),
            borderRadius: BorderRadius.circular(42),
            border: Border.all(color: Colors.white.withValues(alpha: 0.72)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x10191C1E),
                blurRadius: 60,
                offset: Offset(0, 26),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Align(
                alignment: Alignment.center,
                child: _StepIconBadge(
                  icon: Icons.business_center,
                  color: Color(0xFF006780),
                  background: Color(0x1A45B1D4),
                ),
              ),
              const SizedBox(height: 22),
              Align(
                alignment: Alignment.center,
                child: Text(
                  'Business Fundamentals',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: compact ? 42 : 58,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -1.6,
                    color: const Color(0xFF191C1E),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              const Align(
                alignment: Alignment.center,
                child: Text(
                  "Let's understand your impact.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 18,
                    height: 1.6,
                    color: Color(0xFF3D494D),
                  ),
                ),
              ),
              const SizedBox(height: 36),
              const _PromptLabel(
                'What does your business do & what problem are you solving?',
              ),
              const SizedBox(height: 14),
              const _PromptTextArea(
                hint:
                    'Describe your mission, the gap in the market, and how your solution bridges it...',
                minLines: 4,
              ),
              const SizedBox(height: 30),
              const _PromptLabel(
                'Which industry/sector does your company belong to?',
              ),
              const SizedBox(height: 14),
              const _PromptInput(
                hint: 'e.g., ICT, Medical, Cleantech, EdTech...',
              ),
              const SizedBox(height: 32),
              const _PromptLabel('What stage is your business currently at?'),
              const SizedBox(height: 18),
              Wrap(
                spacing: 14,
                runSpacing: 14,
                children: _stageOptions
                    .map(
                      (stage) => _StageCard(
                        label: stage.$1,
                        icon: stage.$2,
                        selected: selectedStage == stage.$1,
                        onTap: () => onStageChanged(stage.$1),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 34),
              const _PromptLabel('What is your current traction or progress?'),
              const SizedBox(height: 18),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: _tractionOptions
                    .map(
                      (item) => _TractionChip(
                        label: item,
                        selected: selectedTraction.contains(item),
                        onTap: () => onTractionToggle(item),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 34),
              const _PromptLabel(
                'How much funding do you need & what will you use it for?',
              ),
              const SizedBox(height: 14),
              const _PromptTextArea(
                hint:
                    'Detail your budget allocation, critical hires, equipment needs...',
                minLines: 4,
              ),
              const SizedBox(height: 42),
              if (narrow)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _BackButton(
                      label: 'Back',
                      onTap: () => Navigator.pushNamed(
                        context,
                        InitializeScreen.routeName,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Align(
                      alignment: Alignment.centerRight,
                      child: _NextButton(
                        label: 'Next',
                        onTap: () => Navigator.pushNamed(
                          context,
                          DocumentVaultScreen.routeName,
                        ),
                      ),
                    ),
                  ],
                )
              else
                Row(
                  children: [
                    _BackButton(
                      label: 'Back',
                      onTap: () => Navigator.pushNamed(
                        context,
                        InitializeScreen.routeName,
                      ),
                    ),
                    const Spacer(),
                    _NextButton(
                      label: 'Next',
                      onTap: () => Navigator.pushNamed(
                        context,
                        DocumentVaultScreen.routeName,
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StepIconBadge extends StatelessWidget {
  const _StepIconBadge({
    required this.icon,
    required this.color,
    required this.background,
  });

  final IconData icon;
  final Color color;
  final Color background;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 58,
      height: 58,
      decoration: BoxDecoration(color: background, shape: BoxShape.circle),
      child: Icon(icon, color: color, size: 28),
    );
  }
}

class _PromptLabel extends StatelessWidget {
  const _PromptLabel(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: Color(0xFF191C1E),
      ),
    );
  }
}

class _PromptInput extends StatelessWidget {
  const _PromptInput({required this.hint});

  final String hint;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 58,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F5),
        borderRadius: BorderRadius.circular(28),
      ),
      child: TextField(
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: const TextStyle(fontSize: 16, color: Color(0xFF7B8794)),
          border: InputBorder.none,
        ),
        style: const TextStyle(fontSize: 16, color: Color(0xFF191C1E)),
      ),
    );
  }
}

class _PromptTextArea extends StatelessWidget {
  const _PromptTextArea({required this.hint, required this.minLines});

  final String hint;
  final int minLines;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F5),
        borderRadius: BorderRadius.circular(28),
      ),
      child: TextField(
        minLines: minLines,
        maxLines: minLines,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: const TextStyle(
            fontSize: 16,
            color: Color(0xFF7B8794),
            height: 1.5,
          ),
          border: InputBorder.none,
        ),
        style: const TextStyle(
          fontSize: 16,
          height: 1.5,
          color: Color(0xFF191C1E),
        ),
      ),
    );
  }
}

class _StageCard extends StatelessWidget {
  const _StageCard({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(26),
        child: Ink(
          width: 136,
          height: 112,
          decoration: BoxDecoration(
            color: selected ? const Color(0x1F45B1D4) : const Color(0xFFF0F2F5),
            borderRadius: BorderRadius.circular(26),
            border: Border.all(
              color: selected ? const Color(0xFF45B1D4) : Colors.transparent,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 30,
                color: selected
                    ? const Color(0xFF006780)
                    : const Color(0xFF3D494D),
              ),
              const SizedBox(height: 12),
              const SizedBox(height: 0),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF191C1E),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TractionChip extends StatelessWidget {
  const _TractionChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isOther = label == 'Other';
    final compact = MediaQuery.sizeOf(context).width < 430;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 18 : 22,
            vertical: 14,
          ),
          decoration: BoxDecoration(
            color: selected ? const Color(0x1CFE932C) : const Color(0xFFF0F2F5),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(
              color: selected ? const Color(0x66FE932C) : Colors.transparent,
            ),
          ),
          child: Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 6,
            children: [
              if (isOther) ...[
                const Icon(Icons.add, size: 16, color: Color(0xFF3D494D)),
              ],
              Text(
                label,
                style: TextStyle(
                  fontSize: compact ? 15 : 16,
                  fontWeight: FontWeight.w500,
                  color: selected
                      ? const Color(0xFF904D00)
                      : const Color(0xFF3D494D),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BackButton extends StatelessWidget {
  const _BackButton({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return TextButton.icon(
      onPressed: onTap,
      style: TextButton.styleFrom(
        foregroundColor: const Color(0xFF191C1E),
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 12),
      ),
      icon: const Icon(Icons.arrow_back, size: 20),
      label: Text(
        label,
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
      ),
    );
  }
}

class _NextButton extends StatelessWidget {
  const _NextButton({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 34, vertical: 18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0F7891), Color(0xFF45B1D4)],
            ),
            borderRadius: BorderRadius.circular(999),
            boxShadow: const [
              BoxShadow(
                color: Color(0x33006780),
                blurRadius: 24,
                offset: Offset(0, 10),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 12),
              const Icon(Icons.arrow_forward, color: Colors.white, size: 22),
            ],
          ),
        ),
      ),
    );
  }
}
