"use client";

import React from "react";
import Link from "next/link";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function LoginPage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const isWide = width >= 1024;

  return (
    <div className={styles.root}>
      {/* background */}
      <div className={styles.bgWrap}>
        {isWide && (
          <div className={styles.leftBg}>
            <div className={styles.meshLayer}>
              <div className={styles.glow} style={{ left: "42%", top: "20%", width: 420, height: 300, background: "radial-gradient(circle, rgba(0,103,128,0.5), transparent)" }} />
              <div className={styles.glow} style={{ left: "80%", top: "2%", width: 360, height: 280, background: "radial-gradient(circle, rgba(69,177,212,0.4), transparent)" }} />
              <div className={styles.glow} style={{ left: "2%", top: "48%", width: 380, height: 320, background: "radial-gradient(circle, rgba(73,75,214,0.4), transparent)" }} />
              <div className={styles.glow} style={{ left: "78%", top: "50%", width: 300, height: 260, background: "radial-gradient(circle, rgba(254,147,44,0.25), transparent)" }} />
            </div>
            <div className={styles.leftFade} />
          </div>
        )}
        <div className={styles.rightBg}>
          <div className={styles.meshLayerLight}>
            <div className={styles.glow} style={{ left: "42%", top: "20%", width: 420, height: 300, background: "radial-gradient(circle, rgba(0,103,128,0.12), transparent)" }} />
            <div className={styles.glow} style={{ left: "80%", top: "2%", width: 360, height: 280, background: "radial-gradient(circle, rgba(69,177,212,0.1), transparent)" }} />
          </div>
        </div>
      </div>

      {/* back button */}
      <Link href="/" className={styles.backBtn}>
        <MI name="arrow_back" size={18} color="#006780" />
        <span>Return to Home</span>
      </Link>

      {/* content */}
      <div className={styles.content}>
        <div className={styles.inner}>
          {isWide && <LeftPane />}
          <div className={styles.formSide}>
            <div className={styles.formScroll}>
              <LoginCard />
              <div style={{ height: 24 }} />
              <RegisterLink />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeftPane() {
  return (
    <div className={styles.leftPane}>
      <div className={styles.leftContent}>
        <h1 className={styles.leftTitle}>The Intelligent</h1>
        <h1 className={styles.etherGradient}>Ether.</h1>
        <div style={{ height: 16 }} />
        <p className={styles.leftSub}>
          Weave data into narrative. Dissolve the friction{"\n"}between insight and impact.
        </p>
      </div>
    </div>
  );
}

function LoginCard() {
  const [rememberMe, setRememberMe] = React.useState(false);

  return (
    <div className={`${styles.loginCard} glass-strong`}>
      <h2 className={styles.cardTitle}>Grantly</h2>
      <p className={styles.cardSub}>Enter your credentials to access the workspace.</p>
      <div style={{ height: 24 }} />

      <GhostField label="EMAIL ADDRESS" hint="jane@example.com" />
      <div style={{ height: 16 }} />
      <GhostField label="PASSWORD" hint="••••••••" forgotText="Forgot?" obscure />
      <div style={{ height: 16 }} />

      <label className={styles.remember}>
        <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className={styles.checkbox} />
        <span>Remember me on this device</span>
      </label>
      <div style={{ height: 20 }} />

      <Link href="/initialize" className="btn-gradient" style={{ height: 48, display: "flex", alignItems: "center", justifyContent: "center" }}>
        Access Workspace
      </Link>
      <div style={{ height: 24 }} />

      <div className={styles.dividerRow}>
        <div className={styles.dividerLine} />
        <span className={styles.dividerText}>OR</span>
        <div className={styles.dividerLine} />
      </div>
      <div style={{ height: 24 }} />

      <Link href="/initialize" className={styles.googleBtn}>
        <div className={styles.googleMark}>G</div>
        <span>Continue with Google</span>
      </Link>
    </div>
  );
}

function GhostField({ label, hint, forgotText, obscure }: { label: string; hint: string; forgotText?: string; obscure?: boolean }) {
  return (
    <div className="ghost-field">
      <div className={styles.fieldHeader}>
        <label>{label}</label>
        {forgotText && <button className={styles.forgotBtn}>{forgotText}</button>}
      </div>
      <input type={obscure ? "password" : "text"} placeholder={hint} />
    </div>
  );
}

function RegisterLink() {
  return (
    <Link href="/initialize" className={styles.registerLink}>
      <span>Register for Node Initialization</span>
      <MI name="arrow_forward" size={16} color="#904D00" />
    </Link>
  );
}
