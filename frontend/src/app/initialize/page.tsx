"use client";

import React from "react";
import Link from "next/link";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function InitializePage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const showSideAccent = width >= 1180;
  const compact = width < 720;

  return (
    <div className={styles.root}>
      {/* background blooms */}
      <div className={styles.bgBlooms}>
        <div className={styles.bloom} style={{ top: -80, left: -150, width: 760, height: 760, background: "radial-gradient(circle, rgba(225,224,255,0.4), transparent)" }} />
        <div className={styles.bloom} style={{ top: -60, left: "50%", transform: "translateX(-50%)", width: 840, height: 520, background: "radial-gradient(circle, rgba(183,234,255,0.5), transparent)" }} />
        <div className={styles.bloom} style={{ top: -20, right: -140, width: 700, height: 760, background: "radial-gradient(circle, rgba(255,220,195,0.4), transparent)" }} />
        <div className={styles.bloom} style={{ bottom: -220, left: "50%", transform: "translateX(-50%)", width: 1200, height: 700, background: "radial-gradient(circle, rgba(255,255,255,0.33), transparent)" }} />
      </div>

      {/* side accent */}
      {showSideAccent && <SideAccent />}

      {/* main */}
      <div className={styles.main}>
        {/* nav bar */}
        <div style={{ padding: "8px 12px 0" }}>
          <NavBar compact={compact} extraCompact={width < 430} />
        </div>

        <div className={styles.scrollArea} style={{ paddingLeft: showSideAccent ? 140 : 20, paddingRight: showSideAccent ? 140 : 20 }}>
          <ProgressSection />
          <div style={{ height: 18 }} />
          <InitializeCard compact={compact} />
          <div style={{ height: 28 }} />
          <InitializeFooter compact={width < 760} />
        </div>
      </div>
    </div>
  );
}

function NavBar({ compact, extraCompact }: { compact: boolean; extraCompact: boolean }) {
  return (
    <div className={`${styles.navBar} glass`}>
      <MI name="auto_awesome" size={16} color="#006780" />
      <span className={styles.navLogo} style={{ fontSize: extraCompact ? 13 : compact ? 15 : 17 }}>Grantly</span>
      <div style={{ flex: 1 }} />
      <Link href="/login" className={styles.navLoginBtn}>Login</Link>
      {!compact && (
        <>
          <div style={{ width: 10 }} />
          <div className={styles.navCircle}><MI name="language" size={15} color="#64748B" /></div>
          <div style={{ width: 8 }} />
          <div className={styles.navCircle}><MI name="notifications" size={15} color="#64748B" /></div>
          <div style={{ width: 10 }} />
          <div className={styles.navAvatar}><MI name="person" size={14} color="#fff" /></div>
        </>
      )}
    </div>
  );
}

function SideAccent() {
  return (
    <div className={styles.sideAccent}>
      <div className={styles.sideAccentInner}>
        <div className={styles.accentLine} style={{ width: 60, background: "#A5C8DB" }} />
        <div className={styles.accentLine} style={{ width: 120, background: "#B8B7F4" }} />
        <div className={styles.accentLine} style={{ width: 80, background: "#B7EAFF" }} />
        <div style={{ height: 64 }} />
        <div style={{ width: 1, height: 116, background: "rgba(188,201,206,0.2)" }} />
        <div style={{ height: 22 }} />
        <p className={styles.sideText}>EMPOWERING THE{"\n"}NEXT WAVE OF{"\n"}NON-PROFIT IMPACT.</p>
      </div>
    </div>
  );
}

function ProgressSection() {
  return (
    <div className={styles.progressWrap}>
      <div className={styles.progressHeader}>
        <span className={styles.stepLabel}>STEP 1 OF 3</span>
        <span className={styles.stepPercent}>33% Complete</span>
      </div>
      <div style={{ height: 18 }} />
      <div className={styles.progressTrack}>
        <div className={styles.progressFill} style={{ width: "33%" }} />
      </div>
    </div>
  );
}

function InitializeCard({ compact }: { compact: boolean }) {
  const [agreed, setAgreed] = React.useState(false);

  return (
    <div className={`${styles.initCard} glass`} style={{ padding: compact ? "20px 16px 20px" : "28px 38px 24px" }}>
      <div className={styles.softOrb} style={{ top: -100, right: -90, background: "rgba(0,103,128,0.07)" }} />
      <div className={styles.softOrb} style={{ bottom: -110, left: -90, background: "rgba(73,75,214,0.07)" }} />

      <h2 className={styles.cardTitle} style={{ fontSize: compact ? 24 : 28 }}>Get Started Now</h2>
      <p className={styles.cardSub}>
        It&apos;s easy to create your Grantly workspace. Tell us who you are, secure your account, and we&apos;ll prepare your grant roadmap workflow.
      </p>
      <div style={{ height: compact ? 14 : 18 }} />

      <div className="init-field"><input placeholder="Full Name *" /></div>
      <div style={{ height: 10 }} />
      <div className="init-field"><input placeholder="Email Address *" /></div>
      <div style={{ height: 10 }} />
      <div className="init-field">
        <input type="password" placeholder="Password *" style={{ flex: 1 }} />
        <MI name="visibility" size={16} color="#93A4BA" />
      </div>
      <div style={{ height: 10 }} />
      <div className="init-field">
        <input type="password" placeholder="Confirm Password *" style={{ flex: 1 }} />
        <MI name="visibility" size={16} color="#93A4BA" />
      </div>
      <div style={{ height: 14 }} />

      <label className={styles.certRow} onClick={() => setAgreed(!agreed)}>
        <input type="checkbox" checked={agreed} onChange={() => setAgreed(!agreed)} style={{ accentColor: "#0F7891", width: 14, height: 14 }} />
        <span className={styles.certText}>
          I certify that I agree to Grantly&apos;s Privacy Policy, Terms and Conditions, and Refund Policy; and I understand it is my responsibility to do due diligence on any grant or investor I meet via this platform.
        </span>
      </label>
      <div style={{ height: compact ? 16 : 20 }} />

      <Link href="/business-fundamentals" className={styles.continueBtn} style={{ padding: compact ? "10px 14px" : "14px 20px" }}>
        <span style={{ fontSize: compact ? 13 : 14 }}>Create New Account</span>
        <MI name="arrow_forward" size={16} color="#fff" />
      </Link>
      <div style={{ height: 16 }} />

      <div className={styles.loginRedirect}>
        <span>Already have an account? </span>
        <Link href="/login" className={styles.loginLink}>Log In</Link>
      </div>
    </div>
  );
}

function InitializeFooter({ compact }: { compact: boolean }) {
  return (
    <div className={styles.footer} style={{ flexDirection: compact ? "column" : "row", alignItems: compact ? "center" : "center", gap: compact ? 14 : 0 }}>
      <div className={styles.securityBadge}>
        <MI name="verified_user" size={24} color="#75A9B6" />
        <span>Enterprise-Grade Security Protocol</span>
      </div>
      {!compact && <div style={{ flex: 1 }} />}
      <div className={styles.footerLinks}>
        <span className={styles.footerLink}>PRIVACY</span>
        <span className={styles.footerLink}>TERMS</span>
        <span className={styles.footerLink}>COMPLIANCE</span>
      </div>
    </div>
  );
}
