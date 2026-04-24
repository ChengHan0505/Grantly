"use client";

import React from "react";
import Link from "next/link";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function DocumentVaultPage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const compact = width < 760;

  return (
    <div className={styles.root}>
      {/* background */}
      <div className={styles.bgOrbs}>
        <div className={styles.orb} style={{ top: -160, left: -140, width: 720, height: 720, background: "radial-gradient(circle, rgba(255,255,255,0.4), transparent)" }} />
        <div className={styles.orb} style={{ top: -60, right: -180, width: 680, height: 680, background: "radial-gradient(circle, rgba(224,242,254,0.25), transparent)" }} />
        <div className={styles.orb} style={{ bottom: -180, right: -200, width: 820, height: 820, background: "radial-gradient(circle, rgba(186,230,253,0.2), transparent)" }} />
        <div className={styles.orb} style={{ bottom: -180, left: -120, width: 720, height: 720, background: "radial-gradient(circle, rgba(255,255,255,0.33), transparent)" }} />
      </div>

      <div className={styles.main}>
        {/* nav */}
        <div style={{ padding: "8px 14px 0" }}>
          <div className={`${styles.navBar} glass`} style={{ background: "rgba(255,255,255,0.58)", borderColor: "rgba(255,255,255,0.82)" }}>
            <MI name="auto_awesome" size={16} color="#0087A5" />
            <span className={styles.navLogo}>Grantly</span>
            <div style={{ flex: 1 }} />
            <Link href="/login" className={styles.loginBtn}>Login</Link>
            {width >= 720 && (
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
        </div>

        <div className={styles.scrollArea}>
          <div className={styles.centerWrap}>
            {/* progress */}
            <div className={styles.progressWrap}>
              <div className={styles.progressHeader}>
                <span className={styles.stepLabel}>STEP 3 OF 3</span>
                <span className={styles.stepPercent}>100% Complete</span>
              </div>
              <div style={{ height: 12 }} />
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: "100%" }} />
              </div>
            </div>
            <div style={{ height: 6 }} />

            {/* hero */}
            <div className={styles.hero}>
              <h1 className={styles.heroTitle} style={{ fontSize: compact ? 24 : 36 }}>The Document Vault</h1>
              <p className={styles.heroSub}>Upload your proof of excellence for the final review.</p>
            </div>
            <div style={{ height: 16 }} />

            {/* grid */}
            <VaultGrid wide={width >= 900} />
            <div style={{ height: 14 }} />

            <div className={styles.divider} />
            <div style={{ height: 10 }} />

            {/* footer */}
            <div className={compact ? styles.footerCol : styles.footerRow}>
              <Link href="/business-fundamentals" className={styles.backBtn}>
                <MI name="arrow_back" size={15} />
                <span>Back to Narrative</span>
              </Link>
              <Link href="/dashboard" className={styles.submitBtn}>
                <span>Submit Application</span>
                <MI name="check_circle" size={16} color="#fff" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VaultGrid({ wide }: { wide: boolean }) {
  if (!wide) {
    return (
      <div className={styles.colGap18}>
        <SmallUploadCard title="SSM Cert" icon="domain_verification" iconColor="#0087A5" />
        <SmallUploadCard title="Pitch Deck" icon="present_to_all" iconColor="#904D00" />
        <SmallUploadCard title="Financials" icon="account_balance" iconColor="#0087A5" />
        <SmallUploadCard title="Business Plan" icon="lightbulb" iconColor="#494BD6" />
        <LargeUploadCard />
      </div>
    );
  }

  return (
    <div className={styles.colGap18}>
      <div className={styles.rowGap18}>
        <SmallUploadCard title="SSM Cert" icon="domain_verification" iconColor="#0087A5" />
        <SmallUploadCard title="Pitch Deck" icon="present_to_all" iconColor="#904D00" />
        <SmallUploadCard title="Financials" icon="account_balance" iconColor="#0087A5" />
      </div>
      <div className={styles.rowGap18}>
        <div style={{ flex: 1 }}>
          <SmallUploadCard title="Business Plan" icon="lightbulb" iconColor="#494BD6" />
        </div>
        <div style={{ flex: 2 }}>
          <LargeUploadCard />
        </div>
      </div>
    </div>
  );
}

function SmallUploadCard({ title, icon, iconColor }: { title: string; icon: string; iconColor: string }) {
  return (
    <label className={styles.uploadCard} style={{ cursor: "pointer" }}>
      <input type="file" style={{ display: "none" }} />
      <div className={styles.uploadCardHeader}>
        <span className={styles.uploadCardTitle}>{title}</span>
        <MI name={icon} size={18} color={iconColor} />
      </div>
      <div style={{ height: 6 }} />
      <UploadZone text="Click to upload" caption="PDF, JPG, PNG (Max 10MB)" icon="upload_file" />
    </label>
  );
}

function LargeUploadCard() {
  return (
    <label className={styles.largeUploadCard} style={{ cursor: "pointer" }}>
      <input type="file" style={{ display: "none" }} />
      <div className={styles.uploadCardHeader}>
        <div>
          <div className={styles.uploadCardTitle} style={{ fontSize: 16 }}>Project Proposal</div>
          <div style={{ fontSize: 12, color: "#475569", marginTop: 4 }}>The core narrative of your grant application.</div>
        </div>
        <MI name="description" size={20} color="#0087A5" />
      </div>
      <div style={{ height: 8 }} />
      <UploadZone text="Drag & drop your primary proposal document" caption="PDF, JPG, PNG (Max 25MB)" icon="cloud_upload" large />
    </label>
  );
}

function UploadZone({ text, caption, icon, large }: { text: string; caption: string; icon: string; large?: boolean }) {
  return (
    <div className={styles.uploadZone} style={{ flex: 1, minHeight: large ? 120 : 100 }}>
      <div className={styles.uploadZoneInner}>
        <div className={styles.uploadIcon} style={{ width: large ? 50 : 40, height: large ? 50 : 40 }}>
          <MI name={icon} size={large ? 22 : 18} color="#0087A5" />
        </div>
        <div style={{ height: large ? 12 : 10 }} />
        <div className={styles.uploadText} style={{ fontSize: large ? 13 : 12 }}>{text}</div>
        <div style={{ height: 6 }} />
        <div className={styles.uploadCaption}>{caption}</div>
      </div>
    </div>
  );
}
