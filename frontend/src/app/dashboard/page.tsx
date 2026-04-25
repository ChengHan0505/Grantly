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
import { CompanyTab, DraftsTab } from "./tabs2";
import { TeamTab } from "./tabs3";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

const TAB_ICONS = ["grid_view", "folder", "domain", "history_edu", "group"];
const TAB_LABELS = ["Home", "Grants", "Company", "Roadmaps", "Team"];

export default function DashboardPage() {
  const [tab, setTab] = React.useState(0);
  const [width, setWidth] = React.useState(1200);
  const [profileOpen, setProfileOpen] = React.useState(false);
  const [compactMenuOpen, setCompactMenuOpen] = React.useState(false);
  const [notificationsOpen, setNotificationsOpen] = React.useState(false);
  const [auditLogOpen, setAuditLogOpen] = React.useState(false);
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
    <DraftsTab key="drafts" documents={documents} rankedGrants={rankedMatches} />,
    <TeamTab key="team" />,
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
          {!compact && <>
            <div className={s.topIcon}><MI name="language" size={22} color="#5F6E84" /></div>
            <div style={{ width: 8 }} />
            <div className={s.topIcon} style={{position:"relative"}} onClick={() => setNotificationsOpen(!notificationsOpen)}>
              <MI name="notifications" size={22} color="#5F6E84" />
              <div style={{position:"absolute", top:6, right:8, width:8, height:8, background:"#BA1A1A", borderRadius:"50%", border:"2px solid #fff"}} />
              
              {notificationsOpen && (
                <div className={s.profileMenu} style={{width: 320, right: -60, padding: 0}}>
                  <div style={{padding:"16px", borderBottom:"1px solid #E0E7EC", background:"#F8FAFC", borderTopLeftRadius:16, borderTopRightRadius:16}}>
                    <span style={{fontSize:14, fontWeight:900, color:"#191C1E"}}>Activity & Audit Trail</span>
                  </div>
                  <div style={{maxHeight: 300, overflowY:"auto"}}>
                    <div style={{padding:"12px 16px", borderBottom:"1px solid #F2F4F6", display:"flex", gap:12}}>
                      <div style={{width:8, height:8, borderRadius:"50%", background:"#00B4D8", marginTop:6, flexShrink:0}}/>
                      <div>
                        <div style={{fontSize:13, fontWeight:700, color:"#191C1E"}}>AI updated financial projections</div>
                        <div style={{fontSize:11, color:"#6D797E", marginTop:4}}>2 mins ago</div>
                      </div>
                    </div>
                    <div style={{padding:"12px 16px", borderBottom:"1px solid #F2F4F6", display:"flex", gap:12}}>
                      <div style={{width:8, height:8, borderRadius:"50%", background:"#904D00", marginTop:6, flexShrink:0}}/>
                      <div>
                        <div style={{fontSize:13, fontWeight:700, color:"#191C1E"}}>New NSF grant matched your profile</div>
                        <div style={{fontSize:11, color:"#6D797E", marginTop:4}}>1 hour ago</div>
                      </div>
                    </div>
                    <div style={{padding:"12px 16px", borderBottom:"1px solid #F2F4F6", display:"flex", gap:12}}>
                      <div style={{width:8, height:8, borderRadius:"50%", background:"#10B981", marginTop:6, flexShrink:0}}/>
                      <div>
                        <div style={{fontSize:13, fontWeight:700, color:"#191C1E"}}>Sarah Chen approved Pitch Deck V2</div>
                        <div style={{fontSize:11, color:"#6D797E", marginTop:4}}>Yesterday at 4:30 PM</div>
                      </div>
                    </div>
                  </div>
                  <div style={{padding:"12px", textAlign:"center", borderTop:"1px solid #E0E7EC"}}>
                    <span 
                      style={{fontSize:12, fontWeight:800, color:"#006780", cursor:"pointer"}}
                      onClick={() => {
                        setNotificationsOpen(false);
                        setAuditLogOpen(true);
                      }}
                    >
                      View Full Log
                    </span>
                  </div>
                </div>
              )}
            </div>
            <div style={{ width: 10 }} />
          </>}
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

    {auditLogOpen && <AuditLogModal onClose={() => setAuditLogOpen(false)} />}
  </div>;
}

function AuditLogModal({onClose}: {onClose:()=>void}) {
  const logs = [
    {id: 1, type: "AI Action", user: "Grantly AI", action: "Updated financial projections based on new Xero sync", time: "2 mins ago", color: "#00B4D8"},
    {id: 2, type: "System", user: "System", action: "New NSF grant matched your profile (98% Match)", time: "1 hour ago", color: "#904D00"},
    {id: 3, type: "Team Action", user: "Sarah Chen", action: "Approved Pitch Deck V2 for review", time: "Yesterday, 4:30 PM", color: "#10B981"},
    {id: 4, type: "Integration", user: "System", action: "Successfully authenticated with QuickBooks Online", time: "Yesterday, 10:15 AM", color: "#2ca01c"},
    {id: 5, type: "Document", user: "Alex Johnson", action: "Uploaded Export Compliance Certificate (Form 89-B)", time: "Oct 24, 2:00 PM", color: "#494BD6"},
    {id: 6, type: "System", user: "Grantly AI", action: "Profile Readiness Score increased from 80 to 85", time: "Oct 24, 2:05 PM", color: "#00B4D8"},
    {id: 7, type: "Team Action", user: "Alex Johnson", action: "Invited Marcus Vance as External Grant Writer", time: "Oct 20, 9:00 AM", color: "#191C1E"},
  ];

  return (
    <div style={{position:"fixed", inset:0, zIndex:999, display:"flex", alignItems:"center", justifyContent:"center", background:"rgba(15, 23, 42, 0.4)", backdropFilter:"blur(4px)"}}>
      <div className={s.panel} style={{width: 900, maxWidth:"95vw", height: 600, maxHeight:"90vh", display:"flex", flexDirection:"column", overflow:"hidden", background:"#fff", borderRadius:24, boxShadow:"0 24px 48px rgba(0,0,0,0.2)", padding:0}}>
        
        {/* Header */}
        <div style={{padding: "20px 24px", borderBottom:"1px solid #E0E7EC", display:"flex", justifyContent:"space-between", alignItems:"center", background:"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)"}}>
          <div>
            <h2 style={{fontSize: 20, fontWeight: 900, color: "#0F172A", margin:0}}>Full Audit Log</h2>
            <div style={{fontSize: 13, color: "#6D797E", marginTop: 4}}>Comprehensive history of workspace activities and AI operations.</div>
          </div>
          <button onClick={onClose} style={{background:"transparent", border:"none", cursor:"pointer", padding:0, display:"flex"}}><MI name="close" size={24} color="#6D797E"/></button>
        </div>

        {/* Filters bar */}
        <div style={{padding: "12px 24px", borderBottom:"1px solid #E0E7EC", display:"flex", gap:12, background:"#fff"}}>
          <select style={{padding:"8px 12px", border:"1px solid #E0E7EC", borderRadius:6, fontSize:13, outline:"none", backgroundColor:"#fff", color:"#3D494D", fontWeight:600}}>
            <option>All Event Types</option>
            <option>AI Actions</option>
            <option>Team Actions</option>
            <option>System Events</option>
          </select>
          <select style={{padding:"8px 12px", border:"1px solid #E0E7EC", borderRadius:6, fontSize:13, outline:"none", backgroundColor:"#fff", color:"#3D494D", fontWeight:600}}>
            <option>All Users</option>
            <option>Grantly AI</option>
            <option>Alex Johnson</option>
            <option>Sarah Chen</option>
          </select>
          <div style={{flex:1}}/>
          <div style={{display:"flex", alignItems:"center", border:"1px solid #E0E7EC", borderRadius:6, padding:"0 12px"}}>
            <MI name="search" size={16} color="#91A0B6"/>
            <input type="text" placeholder="Search logs..." style={{border:"none", outline:"none", padding:"8px", fontSize:13, width:200}} />
          </div>
        </div>

        {/* Table */}
        <div style={{flex: 1, overflowY:"auto"}}>
          <table style={{width:"100%", borderCollapse:"collapse", textAlign:"left"}}>
            <thead style={{position:"sticky", top:0, background:"#F8FAFC", zIndex:10}}>
              <tr>
                <th style={{padding:"12px 24px", fontSize:12, fontWeight:800, color:"#6D797E", borderBottom:"1px solid #E0E7EC"}}>TIMESTAMP</th>
                <th style={{padding:"12px 24px", fontSize:12, fontWeight:800, color:"#6D797E", borderBottom:"1px solid #E0E7EC"}}>ACTOR</th>
                <th style={{padding:"12px 24px", fontSize:12, fontWeight:800, color:"#6D797E", borderBottom:"1px solid #E0E7EC"}}>TYPE</th>
                <th style={{padding:"12px 24px", fontSize:12, fontWeight:800, color:"#6D797E", borderBottom:"1px solid #E0E7EC"}}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} style={{borderBottom:"1px solid #F2F4F6"}}>
                  <td style={{padding:"16px 24px", fontSize:13, color:"#6D797E"}}>{log.time}</td>
                  <td style={{padding:"16px 24px"}}>
                    <div style={{display:"flex", alignItems:"center", gap:8}}>
                      <div style={{width:24, height:24, borderRadius:"50%", background:`${log.color}1a`, display:"flex", alignItems:"center", justifyContent:"center"}}>
                        <MI name={log.user === "Grantly AI" ? "auto_awesome" : "person"} size={14} color={log.color}/>
                      </div>
                      <span style={{fontSize:13, fontWeight:700, color:"#191C1E"}}>{log.user}</span>
                    </div>
                  </td>
                  <td style={{padding:"16px 24px"}}>
                    <span style={{fontSize:11, fontWeight:800, padding:"4px 8px", borderRadius:4, background:"#F2F4F6", color:"#3D494D", textTransform:"uppercase"}}>{log.type}</span>
                  </td>
                  <td style={{padding:"16px 24px", fontSize:13, color:"#3D494D", lineHeight:1.5}}>{log.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
