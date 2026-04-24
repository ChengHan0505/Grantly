"use client";

import React from "react";
import Link from "next/link";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function BusinessFundamentalsPage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const compact = width < 760;
  const narrow = width < 640;
  const [stage, setStage] = React.useState("MVP");
  const [traction, setTraction] = React.useState<Set<string>>(new Set(["Revenue", "Users"]));

  const toggleTraction = (item: string) => {
    setTraction((prev) => {
      const next = new Set(prev);
      if (next.has(item)) next.delete(item);
      else next.add(item);
      return next;
    });
  };

  return (
    <div className={styles.root}>
      {/* background */}
      <div className={styles.bgOrbs}>
        <div className={styles.orb} style={{ top: -120, left: -260, width: 900, height: 900, background: "radial-gradient(circle, rgba(69,177,212,0.2), transparent)" }} />
        <div className={styles.orb} style={{ bottom: -80, right: -140, width: 760, height: 760, background: "radial-gradient(circle, rgba(254,147,44,0.15), transparent)" }} />
        <div className={styles.orb} style={{ top: "50%", right: -120, width: 760, height: 760, background: "radial-gradient(circle, rgba(73,75,214,0.09), transparent)" }} />
      </div>

      <div className={styles.main}>
        {/* nav */}
        <div style={{ padding: "8px 14px 0" }}>
          <div className={`${styles.navBar} glass`}>
            <MI name="auto_awesome" size={16} color="#006780" />
            <span className={styles.navLogo}>Grantly</span>
            <div style={{ flex: 1 }} />
            <Link href="/login" className={styles.loginBtn}>Login</Link>
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
            {/* progress */}
            <div className={styles.progressWrap}>
              <div className={styles.progressHeader}>
                <span className={styles.stepLabel}>STEP 2 OF 3</span>
                <span className={styles.stepPercent}>66% Complete</span>
              </div>
              <div style={{ height: 18 }} />
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: "66%" }} />
              </div>
            </div>
            <div style={{ height: 12 }} />

            {/* card */}
            <div className={`${styles.card} glass`} style={{ padding: compact ? "16px 14px 14px" : "24px 28px 18px" }}>
              <div style={{ textAlign: "center" }}>
                <div className={styles.stepBadge}>
                  <MI name="business_center" size={20} color="#006780" />
                </div>
              </div>
              <h2 className={styles.title} style={{ fontSize: compact ? 24 : 28 }}>Business Fundamentals</h2>
              <p className={styles.subtitle}>Let&apos;s understand your impact.</p>
              <div style={{ height: 14 }} />

              <label className={styles.promptLabel}>What does your business do &amp; what problem are you solving?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-textarea">
                <textarea rows={2} placeholder="Describe your mission, the gap in the market, and how your solution bridges it..." />
              </div>
              <div style={{ height: 16 }} />

              <label className={styles.promptLabel}>Which industry/sector does your company belong to?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-input"><input placeholder="e.g., ICT, Medical, Cleantech, EdTech..." /></div>
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
                ].map((s) => (
                  <button
                    key={s.label}
                    className={`${styles.stageCard} ${stage === s.label ? styles.stageActive : ""}`}
                    onClick={() => setStage(s.label)}
                  >
                    <MI name={s.icon} size={22} color={stage === s.label ? "#006780" : "#3D494D"} />
                    <span>{s.label}</span>
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
                    className={`${styles.chip} ${traction.has(item) ? styles.chipActive : ""}`}
                    onClick={() => toggleTraction(item)}
                  >
                    {item === "Other" && <MI name="add" size={16} color="#3D494D" />}
                    <span>{item}</span>
                  </button>
                ))}
              </div>
              <div style={{ height: 18 }} />

              <label className={styles.promptLabel}>How much funding do you need &amp; what will you use it for?</label>
              <div style={{ height: 8 }} />
              <div className="prompt-textarea">
                <textarea rows={2} placeholder="Detail your budget allocation, critical hires, equipment needs..." />
              </div>
              <div style={{ height: 16 }} />

              {/* nav buttons */}
              <div className={narrow ? styles.navColBtns : styles.navRowBtns}>
                <Link href="/initialize" className={styles.backBtn}>
                  <MI name="arrow_back" size={16} />
                  <span>Back</span>
                </Link>
                <Link href="/document-vault" className={styles.nextBtn}>
                  <span>Next</span>
                  <MI name="arrow_forward" size={16} color="#fff" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
