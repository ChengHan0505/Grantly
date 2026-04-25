"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getOnboardingDraft, saveOnboardingDraft } from "@/services/grantlySession";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

function numberOrNull(value: string): number | null {
  const parsed = Number(value.replace(/,/g, ""));
  return Number.isFinite(parsed) && value.trim() ? parsed : null;
}

export default function BusinessFundamentalsPage() {
  const [width, setWidth] = React.useState(1200);
  const router = useRouter();
  React.useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const compact = width < 760;
  const narrow = width < 640;
  const initialDraft = React.useMemo(() => getOnboardingDraft().business, []);
  const [stage, setStage] = React.useState(initialDraft?.stage || "MVP");
  const [traction, setTraction] = React.useState<Set<string>>(
    () => new Set(initialDraft?.traction && initialDraft.traction.length > 0 ? initialDraft.traction : ["Revenue", "Users"]),
  );
  const [companyName, setCompanyName] = React.useState(initialDraft?.companyName || "");
  const [summary, setSummary] = React.useState(initialDraft?.summary || "");
  const [industry, setIndustry] = React.useState(initialDraft?.industry || "");
  const [fundingUse, setFundingUse] = React.useState(initialDraft?.fundingUse || "");
  const [annualRevenue, setAnnualRevenue] = React.useState(initialDraft?.annualRevenue ? String(initialDraft.annualRevenue) : "");
  const [employeeCount, setEmployeeCount] = React.useState(initialDraft?.employeeCount ? String(initialDraft.employeeCount) : "");
  const [targetGrantAmount, setTargetGrantAmount] = React.useState(initialDraft?.targetGrantAmount ? String(initialDraft.targetGrantAmount) : "");

  const persistDraft = () => {
    saveOnboardingDraft({
      business: {
        companyName,
        summary,
        industry,
        stage,
        traction: Array.from(traction),
        fundingUse,
        annualRevenue: numberOrNull(annualRevenue),
        employeeCount: numberOrNull(employeeCount),
        targetGrantAmount: numberOrNull(targetGrantAmount),
      },
    });
  };

  const toggleTraction = (item: string) => {
    setTraction((prev) => {
      const next = new Set(prev);
      if (next.has(item)) next.delete(item);
      else next.add(item);
      return next;
    });
  };

  const continueToVault = () => {
    persistDraft();
    router.push("/document-vault");
  };

  const skipToDashboard = () => {
    persistDraft();
    router.push("/dashboard");
  };

  return (
    <div className={styles.root}>
      <div className={styles.bgOrbs}>
        <div className={styles.orb} style={{ top: -120, left: -260, width: 900, height: 900, background: "radial-gradient(circle, rgba(69,177,212,0.2), transparent)" }} />
        <div className={styles.orb} style={{ bottom: -80, right: -140, width: 760, height: 760, background: "radial-gradient(circle, rgba(254,147,44,0.15), transparent)" }} />
        <div className={styles.orb} style={{ top: "50%", right: -120, width: 760, height: 760, background: "radial-gradient(circle, rgba(73,75,214,0.09), transparent)" }} />
      </div>

      <div className={styles.main}>
        <div style={{ padding: "8px 14px 0" }}>
          <div className={`${styles.navBar} glass`}>
            <MI name="auto_awesome" size={16} color="#006780" />
            <span className={styles.navLogo}>Grantly</span>
            <div style={{ flex: 1 }} />
            <Link href="/dashboard" className={styles.loginBtn}>Dashboard</Link>
            {width >= 720 && (
              <>
                <div style={{ width: 12 }} />
                <div className={styles.navCircle}><MI name="language" size={16} color="#64748B" /></div>
                <div style={{ width: 8 }} />
                <div className={styles.navCircle}><MI name="notifications" size={16} color="#64748B" /></div>
                <div style={{ width: 10 }} />
                <div className={styles.navAvatar}><MI name="person" size={14} color="#fff" /></div>
              </>
            )}
          </div>
        </div>

        <div className={styles.scrollArea}>
          <div className={styles.centerWrap}>
            <div className={styles.progressWrap}>
              <div className={styles.progressHeader}>
                <span className={styles.stepLabel}>STEP 2 OF 3</span>
                <span className={styles.stepPercent}>Optional Profile Setup</span>
              </div>
              <div style={{ height: 18 }} />
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: "66%" }} />
              </div>
            </div>
            <div style={{ height: 12 }} />

            <div className={`${styles.card} glass`} style={{ padding: compact ? "16px 14px 14px" : "24px 28px 18px" }}>
              <div style={{ textAlign: "center" }}>
                <div className={styles.stepBadge}>
                  <MI name="business_center" size={20} color="#006780" />
                </div>
              </div>
              <h2 className={styles.title} style={{ fontSize: compact ? 24 : 28 }}>Business Fundamentals</h2>
              <p className={styles.subtitle}>These answers power backend grant matching. You can save them now or come back later.</p>
              <div style={{ height: 14 }} />

              <label className={styles.promptLabel}>Company name</label>
              <div style={{ height: 8 }} />
              <div className="prompt-input"><input value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="e.g., Nexus Dynamics Sdn Bhd" /></div>
              <div style={{ height: 16 }} />

              <label className={styles.promptLabel}>What does your business do &amp; what problem are you solving?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-textarea">
                <textarea rows={2} value={summary} onChange={(event) => setSummary(event.target.value)} placeholder="Describe your mission, market gap, and solution..." />
              </div>
              <div style={{ height: 16 }} />

              <label className={styles.promptLabel}>Which industry/sector does your company belong to?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-input"><input value={industry} onChange={(event) => setIndustry(event.target.value)} placeholder="e.g., ICT, Medical, Cleantech, EdTech..." /></div>
              <div style={{ height: 18 }} />

              <label className={styles.promptLabel}>What stage is your business currently at?</label>
              <div style={{ height: 10 }} />
              <div className={styles.stageGrid}>
                {[
                  { label: "Idea", icon: "lightbulb" },
                  { label: "Prototype", icon: "architecture" },
                  { label: "MVP", icon: "rocket_launch" },
                  { label: "Revenue", icon: "payments" },
                  { label: "Scaling", icon: "trending_up" },
                ].map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    className={`${styles.stageCard} ${stage === item.label ? styles.stageActive : ""}`}
                    onClick={() => setStage(item.label)}
                  >
                    <MI name={item.icon} size={22} color={stage === item.label ? "#006780" : "#3D494D"} />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
              <div style={{ height: 18 }} />

              <label className={styles.promptLabel}>What is your current traction or progress?</label>
              <div style={{ height: 10 }} />
              <div className={styles.chipGrid}>
                {["Revenue", "Users", "Partnerships", "Product Completed", "Other"].map((item) => (
                  <button
                    key={item}
                    type="button"
                    className={`${styles.chip} ${traction.has(item) ? styles.chipActive : ""}`}
                    onClick={() => toggleTraction(item)}
                  >
                    {item === "Other" && <MI name="add" size={16} color="#3D494D" />}
                    <span>{item}</span>
                  </button>
                ))}
              </div>
              <div style={{ height: 18 }} />

              <label className={styles.promptLabel}>Current scale</label>
              <div style={{ height: 8 }} />
              <div style={{ display: "grid", gridTemplateColumns: narrow ? "1fr" : "repeat(3, 1fr)", gap: 10 }}>
                <div className="prompt-input"><input value={annualRevenue} onChange={(event) => setAnnualRevenue(event.target.value)} placeholder="Annual revenue (RM)" /></div>
                <div className="prompt-input"><input value={employeeCount} onChange={(event) => setEmployeeCount(event.target.value)} placeholder="Employees" /></div>
                <div className="prompt-input"><input value={targetGrantAmount} onChange={(event) => setTargetGrantAmount(event.target.value)} placeholder="Target grant amount (RM)" /></div>
              </div>
              <div style={{ height: 18 }} />

              <label className={styles.promptLabel}>How much funding do you need &amp; what will you use it for?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-textarea">
                <textarea rows={2} value={fundingUse} onChange={(event) => setFundingUse(event.target.value)} placeholder="Detail your budget allocation, hires, equipment, and project milestones..." />
              </div>
              <div style={{ height: 16 }} />

              <div className={narrow ? styles.navColBtns : styles.navRowBtns}>
                <Link href="/initialize" className={styles.backBtn}>
                  <MI name="arrow_back" size={16} />
                  <span>Back</span>
                </Link>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: narrow ? "stretch" : "flex-end" }}>
                  <button type="button" onClick={skipToDashboard} className={styles.backBtn} style={{ border: "1px solid #D7E3E8", borderRadius: 999, padding: "12px 18px" }}>
                    <MI name="dashboard" size={16} />
                    <span>Save Later</span>
                  </button>
                  <button type="button" onClick={continueToVault} className={styles.nextBtn} style={{ border: "none" }}>
                    <span>Save & Continue</span>
                    <MI name="arrow_forward" size={16} color="#fff" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
