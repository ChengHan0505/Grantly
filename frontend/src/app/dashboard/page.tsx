"use client";
import React from "react";
import Link from "next/link";
import {
  getWorkspace,
  type CompanyProfileRead,
  type DocumentRead,
  type GrantRead,
  type RankedGrantRead,
  type UserRead,
} from "@/services/grantlyApi";
import { clearCurrentUser, rehydrateCurrentUser } from "@/services/grantlySession";
import s from "./page.module.css";
import { HomeTab, GrantTab } from "./tabs";
import { CompanyTab } from "./tabs2";
import { ReimbursementTab, TeamTab } from "./tabs3";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

const TAB_ICONS = ["grid_view", "folder", "domain", "group", "request_quote"];
const TAB_LABELS = ["Home", "Grants", "Company", "Team", "Reimbursement"];

export default function DashboardPage() {
  const [tab, setTab] = React.useState(0);
  const [width, setWidth] = React.useState(1200);
  const [profileOpen, setProfileOpen] = React.useState(false);
  const [compactMenuOpen, setCompactMenuOpen] = React.useState(false);
  const [currentUser, setCurrentUser] = React.useState<UserRead | null>(null);
  const [rankedMatches, setRankedMatches] = React.useState<RankedGrantRead[]>([]);
  const [grantLibrary, setGrantLibrary] = React.useState<GrantRead[]>([]);
  const [profile, setProfile] = React.useState<CompanyProfileRead | null>(null);
  const [documents, setDocuments] = React.useState<DocumentRead[]>([]);
  const [dataLoading, setDataLoading] = React.useState(true);
  const [dataError, setDataError] = React.useState("");
  const [focusGrantId, setFocusGrantId] = React.useState<number | null>(null);

  React.useEffect(() => {
    const u = () => setWidth(window.innerWidth);
    u();
    window.addEventListener("resize", u);
    return () => window.removeEventListener("resize", u);
  }, []);

  const reloadWorkspace = React.useCallback(async () => {
    const user = await rehydrateCurrentUser();
    setCurrentUser(user);
    if (!user) {
      setDataLoading(false);
      setRankedMatches([]);
      setGrantLibrary([]);
      setProfile(null);
      setDocuments([]);
      return;
    }

    setDataLoading(true);
    setDataError("");
    try {
      const workspace = await getWorkspace(user.id);
      setCurrentUser(workspace.user);
      setRankedMatches(workspace.ranked_grants);
      setDocuments(workspace.documents);
      setProfile(workspace.profile ?? null);
      setGrantLibrary(workspace.grants);
    } catch (error: unknown) {
      setDataError(error instanceof Error ? error.message : "Unable to load dashboard data from the backend.");
    } finally {
      setDataLoading(false);
    }
  }, []);

  React.useEffect(() => {
    const timer = window.setTimeout(() => {
      void reloadWorkspace();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [reloadWorkspace]);

  const compact = width < 900;
  const pages = [
    <HomeTab
      key="home"
      currentUser={currentUser}
      rankedGrants={rankedMatches}
      allGrants={grantLibrary}
      profile={profile}
      documents={documents}
      loading={dataLoading}
      error={dataError}
      onApply={(grantId) => {
        setFocusGrantId(grantId);
        setTab(1);
      }}
    />,
    <GrantTab
      key={`grants-${focusGrantId ?? "none"}`}
      currentUser={currentUser}
      rankedGrants={rankedMatches}
      allGrants={grantLibrary}
      profile={profile}
      documents={documents}
      loading={dataLoading}
      error={dataError}
      focusGrantId={focusGrantId}
      onRefresh={reloadWorkspace}
    />,
    <CompanyTab key="company" currentUser={currentUser} profile={profile} documents={documents} onRefresh={reloadWorkspace} />,
    <TeamTab key="team" />,
    <ReimbursementTab key="reimbursement" currentUser={currentUser} profile={profile} documents={documents} />,
  ];

  return <div className={s.root}>
    <div className={s.bgWrap}>
      <div className={s.glowOrb} style={{ top: -180, right: -120, width: 680, height: 680, background: "rgba(254,147,44,0.12)" }} />
      <div className={s.glowOrb} style={{ bottom: -220, left: -160, width: 760, height: 760, background: "rgba(0,180,216,0.10)" }} />
    </div>
    <div className={s.shell}>
      {/* top nav */}
      <div className={`${s.topNav} glass`}>
        {/* Left side (Logo) */}
        <div style={{ display: "flex", alignItems: "center", width: compact ? "auto" : 200, flexShrink: 0 }}>
          <MI name="auto_awesome" size={20} color="#006780" />
          <div style={{ width: 8 }} />
          <span className={s.logo}>Grantly</span>
        </div>

        {/* Center (Tabs or Spacer) */}
        <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
          {compact ? (
            <div className={s.compactTabBtn} onClick={() => setCompactMenuOpen(!compactMenuOpen)}>
              <MI name={TAB_ICONS[tab]} size={20} color="#fff" />
              {compactMenuOpen && <div className={s.compactMenu}>
                {TAB_LABELS.map((l, i) => <div key={l} className={s.compactMenuItem} onClick={() => { setTab(i); setCompactMenuOpen(false); }}>
                  <MI name={TAB_ICONS[i]} size={20} color={tab === i ? "#006780" : "#3D494D"} />{l}
                </div>)}
              </div>}
            </div>
          ) : (
            <div className={s.tabBar} style={{ margin: 0, background: "rgba(0,103,128,0.06)" }}>
              {TAB_ICONS.map((ic, i) =>
                <button key={ic} className={`${s.tabBtn} ${tab === i ? s.tabBtnActive : ""}`} onClick={() => setTab(i)}>
                  <MI name={ic} size={18} color={tab === i ? "#fff" : "#91A0B6"} />
                  <span>{TAB_LABELS[i]}</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Right side (Icons & Profile) */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", width: compact ? "auto" : 200, flexShrink: 0 }}>
          <div className={s.profileBtn} onClick={() => setProfileOpen(!profileOpen)}>
            <MI name="person" size={20} color="#18212A" />
            {profileOpen && <div className={s.profileMenu}>
              {["Alerts", "Account Settings", "Subscriptions & Billing", "Earn Commission", "Country"].map(item =>
                <div key={item} className={s.profileMenuItem} onClick={() => setProfileOpen(false)}>{item}</div>
              )}
              <div className={s.profileMenuDivider} />
              <Link href="/" className={s.profileMenuItem} onClick={() => { clearCurrentUser(); setProfileOpen(false); }}>Sign Out</Link>
            </div>}
          </div>
        </div>
      </div>

      {/* body */}
      <div className={s.bodyCol}>
        {/* content */}
        <div className={s.contentArea}>{pages[tab]}</div>
      </div>
    </div>
  </div>;
}
