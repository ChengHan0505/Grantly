import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';
import '../dashboard/dashboard_shell_screen.dart';
import 'business_fundamentals_screen.dart';

class DocumentVaultScreen extends StatelessWidget {
  const DocumentVaultScreen({super.key});

  static const String routeName = '/document-vault';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        color: const Color(0xFFF3F8FD),
        child: SafeArea(
          child: Column(
            children: [
              const _TopBar(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1080),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const _ProgressHeader(),
                          const SizedBox(height: 22),
                          const Center(
                            child: Text(
                              'The Document Vault',
                              style: TextStyle(fontSize: 62, fontWeight: FontWeight.w800),
                            ),
                          ),
                          const SizedBox(height: 6),
                          const Center(
                            child: Text(
                              'Upload your proof of excellence for the final review.',
                              style: TextStyle(fontSize: 26, color: AppTheme.mutedInk),
                            ),
                          ),
                          const SizedBox(height: 26),
                          const Row(
                            children: [
                              Expanded(child: _SmallUploadCard(title: 'SSM Cert', icon: Icons.verified)),
                              SizedBox(width: 14),
                              Expanded(child: _SmallUploadCard(title: 'Pitch Deck', icon: Icons.upload_file)),
                              SizedBox(width: 14),
                              Expanded(
                                child: _SmallUploadCard(
                                  title: 'Financials',
                                  icon: Icons.account_balance_outlined,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 14),
                          const Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: _SmallUploadCard(
                                  title: 'Business Plan',
                                  icon: Icons.lightbulb_outline,
                                  height: 330,
                                ),
                              ),
                              SizedBox(width: 14),
                              Expanded(flex: 2, child: _LargeUploadCard()),
                            ],
                          ),
                          const SizedBox(height: 22),
                          const Divider(color: Color(0xFFDDE7F1)),
                          const SizedBox(height: 14),
                          Row(
                            children: [
                              TextButton.icon(
                                onPressed: () => Navigator.pushNamed(
                                  context,
                                  BusinessFundamentalsScreen.routeName,
                                ),
                                icon: const Icon(Icons.arrow_back),
                                label: const Text('Back to Narrative'),
                              ),
                              const Spacer(),
                              InkWell(
                                onTap: () => Navigator.pushNamedAndRemoveUntil(
                                  context,
                                  DashboardShellScreen.routeName,
                                  (_) => false,
                                ),
                                borderRadius: BorderRadius.circular(999),
                                child: Ink(
                                  decoration: AppTheme.gradientButton,
                                  padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 14),
                                  child: const Row(
                                    children: [
                                      Text(
                                        'Submit Application',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 20,
                                          fontWeight: FontWeight.w700,
                                        ),
                                      ),
                                      SizedBox(width: 10),
                                      Icon(Icons.check_circle, color: Colors.white, size: 20),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 18),
                        ],
                      ),
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

class _TopBar extends StatelessWidget {
  const _TopBar();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 10),
      child: Row(
        children: const [
          Icon(Icons.auto_awesome, size: 18, color: Color(0xFF1F9CB5)),
          SizedBox(width: 8),
          Text('Grantly', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          Spacer(),
          _LoginPill(),
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

class _LoginPill extends StatelessWidget {
  const _LoginPill();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: AppTheme.gradientButton,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 9),
      child: const Text('Login', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
    );
  }
}

class _ProgressHeader extends StatelessWidget {
  const _ProgressHeader();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Row(
          children: [
            Text('STEP 3 OF 3', style: TextStyle(fontWeight: FontWeight.w700)),
            Spacer(),
            Text('100% Complete'),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 5,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(99),
            color: AppTheme.accentTeal,
          ),
        ),
      ],
    );
  }
}

class _SmallUploadCard extends StatelessWidget {
  const _SmallUploadCard({
    required this.title,
    required this.icon,
    this.height = 222,
  });

  final String title;
  final IconData icon;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.86),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE4EDF5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
              const Spacer(),
              Icon(icon, size: 18, color: AppTheme.accentTeal),
            ],
          ),
          const SizedBox(height: 14),
          const Expanded(child: _DashedUploadField(maxMb: 10, text: 'Click to upload')),
        ],
      ),
    );
  }
}

class _LargeUploadCard extends StatelessWidget {
  const _LargeUploadCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 330,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.86),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE4EDF5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Row(
            children: [
              Text('Project Proposal', style: TextStyle(fontSize: 34, fontWeight: FontWeight.w700)),
              Spacer(),
              Icon(Icons.description_outlined, color: AppTheme.accentTeal),
            ],
          ),
          Text(
            'The core narrative of your grant application.',
            style: TextStyle(color: AppTheme.mutedInk, fontSize: 18),
          ),
          SizedBox(height: 14),
          Expanded(
            child: _DashedUploadField(
              maxMb: 25,
              text: 'Drag & drop your primary proposal document',
            ),
          ),
        ],
      ),
    );
  }
}

class _DashedUploadField extends StatelessWidget {
  const _DashedUploadField({required this.maxMb, required this.text});

  final int maxMb;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFFF8FCFF),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFD7E8F3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircleAvatar(
            radius: 25,
            backgroundColor: Color(0xFFEEF6FB),
            child: Icon(Icons.file_upload_outlined, color: AppTheme.accentTeal),
          ),
          const SizedBox(height: 10),
          Text(text, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text('PDF, JPG, PNG (Max ${maxMb}MB)', style: const TextStyle(color: AppTheme.mutedInk)),
        ],
      ),
    );
  }
}
