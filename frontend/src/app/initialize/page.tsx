"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { createBackendSession } from "@/services/grantlySession";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return React.createElement("span", { className: "material-icon", style: { fontSize: size, color } }, name);
}

export default function InitializePage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const showSideAccent = width >= 1180;
  const compact = width < 720;

  return (
    <div className={styles.root}>
      <div className={styles.bgBlooms}>
        <div className={styles.bloom} style={{ top: -80, left: -150, width: 760, height: 760, background: "radial-gradient(circle, rgba(225,224,255,0.4), transparent)" }} />
        <div className={styles.bloom} style={{ top: -60, left: "50%", transform: "translateX(-50%)", width: 840, height: 520, background: "radial-gradient(circle, rgba(183,234,255,0.5), transparent)" }} />
        <div className={styles.bloom} style={{ top: -20, right: -140, width: 700, height: 760, background: "radial-gradient(circle, rgba(255,220,195,0.4), transparent)" }} />
        <div className={styles.bloom} style={{ bottom: -220, left: "50%", transform: "translateX(-50%)", width: 1200, height: 700, background: "radial-gradient(circle, rgba(255,255,255,0.33), transparent)" }} />
      </div>

      {showSideAccent && <SideAccent />}

      <div className={styles.main}>
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
        <p className={styles.sideText}>EMPOWERING THE{"\n"}NEXT WAVE OF{"\n"}SME IMPACT.</p>
      </div>
    </div>
  );
}

function ProgressSection() {
  return (
    <div className={styles.progressWrap}>
      <div className={styles.progressHeader}>
        <span className={styles.stepLabel}>STEP 1 OF 3</span>
        <span className={styles.stepPercent}>Account Setup</span>
      </div>
      <div style={{ height: 18 }} />
      <div className={styles.progressTrack}>
        <div className={styles.progressFill} style={{ width: "33%" }} />
      </div>
    </div>
  );
}

function InitializeCard({ compact }: { compact: boolean }) {
  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false);
  const [agreed, setAgreed] = React.useState(false);
  const [submittingPath, setSubmittingPath] = React.useState<string | null>(null);
  const [error, setError] = React.useState("");
  const router = useRouter();

  const authErrorMessage = (err: unknown): string => {
    const code = typeof err === "object" && err !== null && "code" in err ? String((err as { code?: string }).code) : "";
    if (code.includes("auth/email-already-in-use")) return "This email is already registered. Log in instead.";
    if (code.includes("auth/invalid-email")) return "Enter a valid email address.";
    if (code.includes("auth/weak-password")) return "Use a password with at least 6 characters.";
    if (code.includes("auth/operation-not-allowed")) return "Email/password registration is not enabled for this Firebase project.";
    return err instanceof Error ? err.message : "Unable to create the account. Please try again.";
  };

  const handleCreate = async (nextPath: string) => {
    if (!email.trim()) {
      setError("Enter an email address before creating your workspace.");
      return;
    }
    if (password.length < 6) {
      setError("Use a password with at least 6 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (!agreed) {
      setError("Please confirm the privacy and due diligence acknowledgement.");
      return;
    }

    setSubmittingPath(nextPath);
    setError("");
    try {
      const credential = await createUserWithEmailAndPassword(auth, email.trim(), password);
      const displayName = fullName.trim() || email.split("@")[0];
      if (displayName) {
        await updateProfile(credential.user, { displayName });
      }
      await createBackendSession({
        email: credential.user.email || email.trim(),
        displayName,
        externalAuthId: credential.user.uid,
      });
      router.push(nextPath);
    } catch (err: unknown) {
      setError(authErrorMessage(err));
      setSubmittingPath(null);
    }
  };

  return (
    <div className={`${styles.initCard} glass`} style={{ padding: compact ? "20px 16px 20px" : "28px 38px 24px" }}>
      <div className={styles.softOrb} style={{ top: -100, right: -90, background: "rgba(0,103,128,0.07)" }} />
      <div className={styles.softOrb} style={{ bottom: -110, left: -90, background: "rgba(73,75,214,0.07)" }} />

      <h2 className={styles.cardTitle} style={{ fontSize: compact ? 24 : 28 }}>Get Started Now</h2>
      <p className={styles.cardSub}>
        Create your Grantly workspace first. You can complete Business Fundamentals and the Document Vault now, or skip to the dashboard and return later.
      </p>
      <div style={{ height: compact ? 14 : 18 }} />

      <div className="init-field"><input placeholder="Full Name *" value={fullName} onChange={(event) => setFullName(event.target.value)} /></div>
      <div style={{ height: 10 }} />
      <div className="init-field"><input placeholder="Email Address *" value={email} onChange={(event) => setEmail(event.target.value)} /></div>
      <div style={{ height: 10 }} />
      <div className="init-field">
        <input type={showPassword ? "text" : "password"} placeholder="Password *" value={password} onChange={(event) => setPassword(event.target.value)} style={{ flex: 1 }} />
        <button
          type="button"
          aria-label={showPassword ? "Hide password" : "Show password"}
          onClick={() => setShowPassword((value) => !value)}
          style={{ border: "none", background: "transparent", padding: 0, display: "flex", cursor: "pointer" }}
        >
          <MI name={showPassword ? "visibility_off" : "visibility"} size={16} color="#93A4BA" />
        </button>
      </div>
      <div style={{ height: 10 }} />
      <div className="init-field">
        <input type={showConfirmPassword ? "text" : "password"} placeholder="Confirm Password *" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} style={{ flex: 1 }} />
        <button
          type="button"
          aria-label={showConfirmPassword ? "Hide confirmation password" : "Show confirmation password"}
          onClick={() => setShowConfirmPassword((value) => !value)}
          style={{ border: "none", background: "transparent", padding: 0, display: "flex", cursor: "pointer" }}
        >
          <MI name={showConfirmPassword ? "visibility_off" : "visibility"} size={16} color="#93A4BA" />
        </button>
      </div>
      <div style={{ height: 14 }} />

      <label className={styles.certRow}>
        <input type="checkbox" checked={agreed} onChange={(event) => setAgreed(event.target.checked)} style={{ accentColor: "#0F7891", width: 14, height: 14 }} />
        <span className={styles.certText}>
          I certify that I agree to Grantly&apos;s Privacy Policy, Terms and Conditions, and Refund Policy; and I understand it is my responsibility to do due diligence on any grant or investor I meet via this platform.
        </span>
      </label>
      <div style={{ height: compact ? 16 : 20 }} />

      {error && (
        <div style={{ background: "#fff0f0", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 14px", marginBottom: 14, fontSize: 13, color: "#BA1A1A" }}>
          {error}
        </div>
      )}

      <button
        type="button"
        onClick={() => handleCreate("/business-fundamentals")}
        disabled={Boolean(submittingPath)}
        className={styles.continueBtn}
        style={{ padding: compact ? "10px 14px" : "14px 20px", border: "none" }}
      >
        <span style={{ fontSize: compact ? 13 : 14 }}>{submittingPath === "/business-fundamentals" ? "Creating Account..." : "Create Account & Continue Setup"}</span>
        <MI name="arrow_forward" size={16} color="#fff" />
      </button>
      <div style={{ height: 10 }} />
      <button
        type="button"
        onClick={() => handleCreate("/dashboard")}
        disabled={Boolean(submittingPath)}
        className={styles.continueBtn}
        style={{ padding: compact ? "10px 14px" : "12px 20px", border: "1px solid rgba(0,103,128,0.25)", background: "rgba(255,255,255,0.72)", color: "#006780", boxShadow: "none" }}
      >
        <span style={{ fontSize: compact ? 13 : 14 }}>{submittingPath === "/dashboard" ? "Opening Dashboard..." : "Skip Setup for Now"}</span>
        <MI name="dashboard" size={16} color="#006780" />
      </button>
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
    <div className={styles.footer} style={{ flexDirection: compact ? "column" : "row", alignItems: "center", gap: compact ? 14 : 0 }}>
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
