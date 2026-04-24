"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function DocumentVaultPage() {
  const [width, setWidth] = React.useState(1200);
  const [submitting, setSubmitting] = React.useState(false);
  const router = useRouter();

  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const handleSubmit = () => {
    setSubmitting(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 3000);
  };

  const compact = width < 760;

  return (
    <div className={styles.root}>
      {/* Full-screen submission overlay */}
      {submitting && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 9999,
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          background: "rgba(10, 20, 40, 0.72)", backdropFilter: "blur(10px)",
        }}>
          <div style={{
            background: "rgba(255,255,255,0.07)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: 32, padding: "52px 64px",
            display: "flex", flexDirection: "column", alignItems: "center", gap: 28,
            boxShadow: "0 32px 80px rgba(0,0,0,0.5)",
          }}>
            {/* Outer ring */}
            <div style={{ position: "relative", width: 96, height: 96 }}>
              <svg viewBox="0 0 100 100" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", animation: "spin 1.4s linear infinite" }}>
                <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(0,180,216,0.2)" strokeWidth="6" />
                <circle cx="50" cy="50" r="44" fill="none" stroke="#00B4D8" strokeWidth="6" strokeLinecap="round" strokeDasharray="276" strokeDashoffset="200" />
              </svg>
              {/* Inner icon */}
              <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <MI name="auto_awesome" size={36} color="#00B4D8" />
              </div>
            </div>

            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 24, fontWeight: 900, color: "#fff", letterSpacing: -0.5, marginBottom: 10 }}>
                Analysing Grant Compatibility
              </div>
              <div style={{ fontSize: 14, color: "rgba(255,255,255,0.6)", lineHeight: 1.6 }}>
                Our AI is cross-referencing your documents<br />with active grant requirements...
              </div>
            </div>

            {/* Animated dots */}
            <div style={{ display: "flex", gap: 8 }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%", background: "#00B4D8",
                  animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          </div>

          <style>{`
            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            @keyframes pulse { 0%, 100% { opacity: 0.2; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.15); } }
          `}</style>
        </div>
      )}
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
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className={styles.submitBtn}
                style={{ border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}
              >
                <span>Submit Application</span>
                <MI name="check_circle" size={16} color="#fff" />
              </button>
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
  const [file, setFile] = React.useState<File | null>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation(); e.preventDefault();
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <label className={styles.uploadCard} style={{ cursor: "pointer" }}>
      <input type="file" style={{ display: "none" }} ref={inputRef} onChange={handleChange} />
      <div className={styles.uploadCardHeader}>
        <span className={styles.uploadCardTitle}>{title}</span>
        <MI name={icon} size={18} color={iconColor} />
      </div>
      <div style={{ height: 6 }} />
      {file ? (
        <div className={styles.uploadZone} style={{ flex: 1, minHeight: 100 }}>
          <div className={styles.uploadZoneInner}>
            <MI name="check_circle" size={28} color="#10B981" />
            <div style={{ height: 8 }} />
            <div className={styles.uploadText} style={{ fontSize: 12, color: "#10B981", fontWeight: 700 }}>Uploaded!</div>
            <div style={{ fontSize: 11, color: "#475569", marginTop: 4, wordBreak: "break-all", textAlign: "center", padding: "0 8px" }}>{file.name}</div>
            <button onClick={handleRemove} style={{ marginTop: 8, fontSize: 11, color: "#BA1A1A", background: "transparent", border: "none", cursor: "pointer", fontWeight: 700 }}>Remove</button>
          </div>
        </div>
      ) : (
        <UploadZone text="Click to upload" caption="PDF, JPG, PNG (Max 10MB)" icon="upload_file" />
      )}
    </label>
  );
}

function LargeUploadCard() {
  const [file, setFile] = React.useState<File | null>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation(); e.preventDefault();
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <label className={styles.largeUploadCard} style={{ cursor: "pointer" }}>
      <input type="file" style={{ display: "none" }} ref={inputRef} onChange={handleChange} />
      <div className={styles.uploadCardHeader}>
        <div>
          <div className={styles.uploadCardTitle} style={{ fontSize: 16 }}>Project Proposal</div>
          <div style={{ fontSize: 12, color: "#475569", marginTop: 4 }}>The core narrative of your grant application.</div>
        </div>
        <MI name="description" size={20} color="#0087A5" />
      </div>
      <div style={{ height: 8 }} />
      {file ? (
        <div className={styles.uploadZone} style={{ flex: 1, minHeight: 120 }}>
          <div className={styles.uploadZoneInner}>
            <MI name="check_circle" size={36} color="#10B981" />
            <div style={{ height: 10 }} />
            <div className={styles.uploadText} style={{ fontSize: 14, color: "#10B981", fontWeight: 700 }}>Document Uploaded!</div>
            <div style={{ fontSize: 12, color: "#475569", marginTop: 6, wordBreak: "break-all", textAlign: "center", padding: "0 12px" }}>{file.name}</div>
            <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{(file.size / 1024).toFixed(1)} KB</div>
            <button onClick={handleRemove} style={{ marginTop: 10, fontSize: 12, color: "#BA1A1A", background: "transparent", border: "none", cursor: "pointer", fontWeight: 700 }}>Remove File</button>
          </div>
        </div>
      ) : (
        <UploadZone text="Drag & drop your primary proposal document" caption="PDF, JPG, PNG (Max 25MB)" icon="cloud_upload" large />
      )}
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
