"use client";

import React from "react";
import Link from "next/link";
import styles from "./page.module.css";

/* ── Icon helper ── */
function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return (
    <span className="material-icon" style={{ fontSize: size, color }}>
      {name}
    </span>
  );
}

/* ========================================================================== */
/*  Landing Page                                                               */
/* ========================================================================== */
export default function LandingPage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const showSideDock = width >= 1180;
  const compact = width < 720;

  return (
    <div className={styles.root}>
      {/* ── mesh background ── */}
      <div className={styles.meshBg}>
        <div className={styles.meshBlob} style={{ top: -80, left: -120, width: 640, height: 640, background: "rgba(0,180,216,0.25)" }} />
        <div className={styles.meshBlob} style={{ bottom: -90, right: -120, width: 620, height: 620, background: "rgba(73,75,214,0.20)" }} />
        <div className={styles.meshBlob} style={{ top: "40%", left: "30%", width: 520, height: 520, background: "rgba(0,103,128,0.13)" }} />
        <div className={styles.meshBlob} style={{ bottom: -180, left: -180, width: 760, height: 760, background: "rgba(153,156,255,0.14)" }} />
        <div className={styles.meshBlob} style={{ top: 20, right: -60, width: 420, height: 420, background: "rgba(108,211,247,0.19)" }} />
      </div>

      {/* ── side dock removed, moved to top bar ── */}

      {/* ── main content ── */}
      <div className={styles.scrollWrap}>
        <div className={styles.center}>
          {/* top bar */}
          <TopBar compact={compact} />
          <div style={{ height: 32 }} />

          {/* hero */}
          <HeroSection compact={compact} />
          <div style={{ height: 24 }} />

          {/* pipeline stages */}
          <PipelineStagePanel compact={compact} />
          <div style={{ height: 32 }} />

          {/* sme features */}
          <SmeFeaturesSection compact={width < 880} />
          <div style={{ height: 48 }} />

          {/* testimonials */}
          <TestimonialSection compact={compact} />
          <div style={{ height: 48 }} />

          {/* bottom cta */}
          <BottomCta compact={compact} />
          <div style={{ height: 16 }} />
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────── Top Bar ─────────────────────── */
function TopBar({ compact }: { compact: boolean }) {
  return (
    <div className={`${styles.topBar} glass-light`} style={{ justifyContent: "space-between" }}>
      {/* Left side (Logo) */}
      <div style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
        <MI name="auto_awesome" size={18} color="#00B4D8" />
        <div style={{ width: 6 }} />
        <span className={styles.logo}>Grantly</span>
      </div>

      {/* Right side (Actions) */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, flexShrink: 0 }}>
        <Link href="/login" style={{ fontSize: 13, fontWeight: 700, color: "#334155", textDecoration: "none" }}>Log in</Link>
        <Link href="/login" className="btn-pill" style={{ padding: "8px 16px", fontSize: 13 }}>Get Started for Free</Link>
      </div>
    </div>
  );
}

/* ─────────────────────── Hero Section ─────────────────────── */
function HeroSection({ compact }: { compact: boolean }) {
  return (
    <div className={styles.hero}>
      <h1 className={styles.heroTitle} style={{ fontSize: compact ? 32 : 48, color: "#0F172A" }}>
        Secure SME Grants.{"\n"}
        <span className={styles.heroGradient}>Faster. Smarter.</span>
      </h1>
      <p className={styles.heroSub} style={{ fontSize: compact ? 15 : 18, color: "#334155" }}>
        Your AI Copilot for business grants. We match your profile with the best funding opportunities and auto-draft your pitch deck.
      </p>
    </div>
  );
}

/* ─────────────────────── Pipeline Stage Panel ─────────────────────── */
function PipelineStagePanel({ compact }: { compact: boolean }) {
  const stages = [
    { icon: "upload_file", label: "1. Upload Profile", bg: "rgba(0,180,216,0.15)", fg: "#006780" },
    { icon: "radar", label: "2. Discover Matches", bg: "rgba(0,180,216,0.15)", fg: "#006780" },
    { icon: "edit_document", label: "3. Auto-Draft", bg: "rgba(0,180,216,0.15)", fg: "#006780" },
    { icon: "payments", label: "4. Get Funded", bg: "rgba(0,180,216,0.15)", fg: "#006780" },
  ];

  return (
    <div className={`${styles.glassContainer}`} style={{ borderRadius: 34, padding: compact ? "18px" : "24px 28px" }}>
      <div className={compact ? styles.stageWrap : styles.stageRow}>
        {stages.map((s, i) => (
          <React.Fragment key={s.label}>
            {!compact && i > 0 && <div className={styles.stageDivider} />}
            <div className={styles.stage}>
              <div className={styles.stageCircle} style={{ background: s.bg, borderColor: "rgba(0,180,216,0.3)" }}>
                <MI name={s.icon} size={24} color={s.fg} />
              </div>
              <span className={styles.stageLabel} style={{color: "#0F172A", fontWeight: 800}}>{s.label}</span>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────── Sme Features Section ─────────────────────── */
function SmeFeaturesSection({ compact }: { compact: boolean }) {
  return (
    <div className={compact ? styles.colGap22 : styles.rowGap22}>
      {/* Feature 1 */}
      <div className={styles.glassContainer} style={{ borderRadius: 30, padding: 32, flex: 1, background: "rgba(255,255,255,0.6)" }}>
        <div className={styles.rowCenter} style={{ gap: 12 }}>
          <div className={styles.iconBadge} style={{ background: "rgba(0,180,216,0.15)" }}><MI name="radar" size={24} color="#0087A5" /></div>
          <span style={{ fontSize: 22, fontWeight: 800, color: "#0F172A" }}>Precision Matching</span>
        </div>
        <div style={{ height: 16 }} />
        <p style={{ color: "#334155", lineHeight: 1.6, fontSize: 15 }}>
          Stop wasting time on grants you won't win. Our AI cross-references your <strong style={{ color: "#0087A5" }}>business fundamentals</strong> with thousands of active grants to find your perfect fit.
        </p>
        <div style={{ height: 32 }} />
        <div style={{ textAlign: "center", background: "#fff", padding: "24px", borderRadius: 20, boxShadow: "0 10px 30px rgba(0,0,0,0.05)", border: "1px solid rgba(0,180,216,0.2)" }}>
          <div style={{ fontSize: 64, fontWeight: 900, color: "#00B4D8", lineHeight: 1 }}>98%</div>
          <div style={{ color: "#0087A5", letterSpacing: 2, fontWeight: 800, fontSize: 11, marginTop: 8 }}>MATCH ALIGNMENT</div>
        </div>
      </div>

      {/* Feature 2 */}
      <div className={styles.glassContainer} style={{ borderRadius: 30, padding: 32, flex: 1, background: "rgba(255,255,255,0.6)" }}>
        <div className={styles.rowCenter} style={{ gap: 12 }}>
          <div className={styles.iconBadge} style={{ background: "rgba(0,180,216,0.15)" }}><MI name="auto_awesome" size={24} color="#0087A5" /></div>
          <span style={{ fontSize: 22, fontWeight: 800, color: "#0F172A" }}>AI Pitch Deck Generation</span>
        </div>
        <div style={{ height: 16 }} />
        <p style={{ color: "#334155", lineHeight: 1.6, fontSize: 15 }}>
          Turn your raw SSMs and financial PDFs into a <strong style={{ color: "#0087A5" }}>winning narrative</strong>. Grantly auto-drafts your proposal sections instantly.
        </p>
        <div style={{ height: 32 }} />
        <div style={{ background: "#fff", padding: "24px", borderRadius: 20, boxShadow: "0 10px 30px rgba(0,0,0,0.05)", border: "1px solid rgba(0,180,216,0.2)" }}>
          <div className={styles.rowCenter} style={{ gap: 8 }}>
            <MI name="sync" size={16} color="#0087A5" />
            <span style={{ fontWeight: 800, fontSize: 13, color: "#0087A5" }}>Drafting "Financials"</span>
          </div>
          <div style={{ height: 20 }} />
          <div className={styles.tinyLine} style={{ width: "100%", background: "#E2E8F0", height: 6 }} />
          <div style={{ height: 12 }} />
          <div className={styles.tinyLine} style={{ width: "80%", background: "#E2E8F0", height: 6 }} />
          <div style={{ height: 12 }} />
          <div className={styles.tinyLine} style={{ width: "90%", background: "#E2E8F0", height: 6 }} />
        </div>
      </div>
      {/* Feature 3 */}
      <div className={styles.glassContainer} style={{ borderRadius: 30, padding: 32, flex: 1, background: "rgba(255,255,255,0.6)" }}>
        <div className={styles.rowCenter} style={{ gap: 12 }}>
          <div className={styles.iconBadge} style={{ background: "rgba(0,180,216,0.15)" }}><MI name="event_available" size={24} color="#0087A5" /></div>
          <span style={{ fontSize: 22, fontWeight: 800, color: "#0F172A" }}>Never Miss a Deadline</span>
        </div>
        <div style={{ height: 16 }} />
        <p style={{ color: "#334155", lineHeight: 1.6, fontSize: 15 }}>
          We automatically track <strong style={{ color: "#0087A5" }}>rolling deadlines</strong> and submission windows for your targeted grants so you can focus on running your business.
        </p>
        <div style={{ height: 32 }} />
        <div style={{ background: "#fff", padding: "20px", borderRadius: 20, boxShadow: "0 10px 30px rgba(0,0,0,0.05)", border: "1px solid rgba(0,180,216,0.2)" }}>
          <div className={styles.rowCenter} style={{ gap: 12 }}>
            <div style={{ width: 4, height: 40, background: "#00B4D8", borderRadius: 4 }} />
            <div>
              <div style={{ fontWeight: 800, fontSize: 14, color: "#0F172A" }}>NSF SME Research</div>
              <div style={{ fontWeight: 700, fontSize: 12, color: "#0087A5", marginTop: 4 }}>Due in 5 Days</div>
            </div>
          </div>
          <div style={{ height: 12 }} />
          <div className={styles.rowCenter} style={{ gap: 12 }}>
            <div style={{ width: 4, height: 40, background: "#E2E8F0", borderRadius: 4 }} />
            <div>
              <div style={{ fontWeight: 800, fontSize: 14, color: "#0F172A" }}>State Clean Energy</div>
              <div style={{ fontSize: 12, color: "#64748B", marginTop: 4 }}>Due Oct 15</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────── Bottom CTA ─────────────────────── */
function BottomCta({ compact }: { compact: boolean }) {
  return (
    <div style={{ textAlign: "center" }}>
      <h2 style={{ fontSize: compact ? 24 : 32, fontWeight: 800, color: "#0F172A", letterSpacing: -1, maxWidth: 760, margin: "0 auto" }}>
        Ready to secure your next business grant?
      </h2>
      <div style={{ height: 24 }} />
      <Link href="/login" className="btn-pill large">Get Started for Free</Link>
    </div>
  );
}

/* ─────────────────────── Testimonial Section ─────────────────────── */
function TestimonialSection({ compact }: { compact: boolean }) {
  return (
    <div style={{ textAlign: "center", padding: "0 10px" }}>
      <h2 style={{ fontSize: compact ? 22 : 28, fontWeight: 800, color: "#0F172A", letterSpacing: -0.5 }}>
        SMEs winning with Grantly
      </h2>
      <div style={{ height: 24 }} />
      <div className={compact ? styles.colGap22 : styles.rowGap22}>
        <TestimonialCard 
          quote="Grantly helped us secure a $1.2M clean energy grant. The AI drafted our technical proposal perfectly from our raw sensor data documents. It saved us months."
          name="Sarah Jenkins"
          role="CEO, Nexus Dynamics"
          avatarColor="#00B4D8"
        />
        <TestimonialCard 
          quote="We didn't even know we qualified for the state manufacturing grant until Grantly matched us. The platform completely eliminated the guesswork."
          name="David Chen"
          role="Founder, BuildTech Solutions"
          avatarColor="#494BD6"
        />
      </div>
    </div>
  );
}

function TestimonialCard({quote, name, role, avatarColor}:{quote:string;name:string;role:string;avatarColor:string}) {
  return (
    <div className={styles.glassContainer} style={{ borderRadius: 26, padding: 28, flex: 1, textAlign: "left", background: "rgba(255,255,255,0.7)" }}>
      <MI name="format_quote" size={32} color={avatarColor} />
      <div style={{ height: 12 }} />
      <p style={{ fontSize: 15, lineHeight: 1.6, color: "#334155", fontStyle: "italic" }}>
        "{quote}"
      </p>
      <div style={{ height: 24 }} />
      <div className={styles.rowCenter} style={{ gap: 12 }}>
        <div style={{ width: 40, height: 40, borderRadius: "50%", background: `${avatarColor}22`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <MI name="person" size={20} color={avatarColor} />
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 800, color: "#0F172A" }}>{name}</div>
          <div style={{ fontSize: 12, color: "#64748B", marginTop: 2 }}>{role}</div>
        </div>
      </div>
    </div>
  );
}
