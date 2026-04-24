"use client";
import React from "react";
import s from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export function IntegrationsTab() {
  const [connected, setConnected] = React.useState<Record<string, boolean>>({
    "sql_account": true
  });
  const [selectedIntegration, setSelectedIntegration] = React.useState<any>(null);

  const handleConnect = (id: string, name: string, color: string) => {
    if (connected[id]) {
      setConnected(prev => ({ ...prev, [id]: false }));
    } else {
      setSelectedIntegration({ id, name, color });
    }
  };

  const handleAuthComplete = (id: string) => {
    setConnected(prev => ({ ...prev, [id]: true }));
    setSelectedIntegration(null);
  };

  return <div style={{ overflowY: "auto", paddingBottom: 40 }}>
    <div className={s.pageHeader} style={{ marginBottom: 24 }}>
      <div className={s.pageTitle} style={{ fontSize: 28 }}>Financial Integrations</div>
      <div className={s.pageSub}>Connect your accounting and banking software to automatically verify your financial health for grant applications.</div>
    </div>

    <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>

      {/* Live Data Dashboard */}
      <div style={{ flex: "1 1 300px", display: "flex", flexDirection: "column", gap: 16 }}>
        <div className={s.panel} style={{ borderRadius: 24, padding: 24, background: "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)", border: "1px solid #bae6fd" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <MI name="sync" size={20} color="#0087A5" />
            <span style={{ fontSize: 16, fontWeight: 800, color: "#0F172A" }}>Live Financial Sync</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: "#334155" }}>Verified MRR</span>
            <span style={{ fontSize: 15, fontWeight: 900, color: "#006780" }}>$15,240</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ fontSize: 13, color: "#334155" }}>Monthly Burn Rate</span>
            <span style={{ fontSize: 15, fontWeight: 900, color: "#93000A" }}>$8,400</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 13, color: "#334155" }}>Runway</span>
            <span style={{ fontSize: 15, fontWeight: 900, color: "#0F172A" }}>14 Months</span>
          </div>
          <div style={{ marginTop: 20, fontSize: 11, color: "#64748b", textAlign: "right" }}>Last synced: 2 mins ago via SQL Account</div>
        </div>
      </div>

      {/* Integration Cards */}
      <div style={{ flex: "2 1 500px", display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 16 }}>

        <IntegrationCard
          id="sql_account" name="SQL Account" type="Accounting" icon="account_balance_wallet" color="#E31837"
          connected={connected["sql_account"]} onToggle={() => handleConnect("sql_account", "SQL Account", "#E31837")}
        />
        <IntegrationCard
          id="autocount" name="AutoCount" type="Accounting" icon="calculate" color="#ED7B22"
          connected={connected["autocount"]} onToggle={() => handleConnect("autocount", "AutoCount", "#ED7B22")}
        />
        <IntegrationCard
          id="maybank" name="Maybank2u Biz" type="Corporate Banking" icon="account_balance" color="#FDB813"
          connected={connected["maybank"]} onToggle={() => handleConnect("maybank", "Maybank2u Biz", "#FDB813")}
        />
        <IntegrationCard
          id="cimb" name="CIMB BizChannel" type="Corporate Banking" icon="business_center" color="#ED1C24"
          connected={connected["cimb"]} onToggle={() => handleConnect("cimb", "CIMB BizChannel", "#ED1C24")}
        />
        <IntegrationCard
          id="tng" name="Touch 'n Go eWallet" type="Payment Gateway" icon="payments" color="#015E9B"
          connected={connected["tng"]} onToggle={() => handleConnect("tng", "Touch 'n Go eWallet", "#015E9B")}
        />

      </div>
    </div>

    {selectedIntegration && (
      <IntegrationAuthModal
        integration={selectedIntegration}
        onClose={() => setSelectedIntegration(null)}
        onComplete={() => handleAuthComplete(selectedIntegration.id)}
      />
    )}
  </div>;
}

function IntegrationAuthModal({ integration, onClose, onComplete }: any) {
  const [step, setStep] = React.useState(0);

  React.useEffect(() => {
    if (step === 1) {
      const timer = setTimeout(() => setStep(2), 2000);
      return () => clearTimeout(timer);
    }
  }, [step]);

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(15, 23, 42, 0.4)", backdropFilter: "blur(4px)" }}>
      <div className={s.panel} style={{ width: 480, maxWidth: "90vw", display: "flex", flexDirection: "column", overflow: "hidden", background: "#fff", borderRadius: 24, boxShadow: "0 24px 48px rgba(0,0,0,0.2)", padding: 0 }}>

        {step === 0 && (
          <div style={{ padding: 32, textAlign: "center" }}>
            <div style={{ width: 64, height: 64, borderRadius: 16, background: `${integration.color}1a`, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
              <MI name="sync" size={32} color={integration.color} />
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 900, color: "#191C1E", margin: "0 0 12px 0" }}>Connect {integration.name}</h2>
            <p style={{ fontSize: 14, color: "#6D797E", lineHeight: 1.5, margin: "0 0 32px 0" }}>
              Grantly will securely sync your financial metrics (MRR, Burn Rate, Runway) directly from {integration.name} to strengthen your grant applications. We use bank-level encryption.
            </p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button className="btn-outline-sm" onClick={onClose} style={{ padding: "10px 20px", fontSize: 14 }}>Cancel</button>
              <button className="btn-primary" onClick={() => setStep(1)} style={{ padding: "10px 20px", fontSize: 14, background: integration.color, borderColor: integration.color }}>
                Authorize Access
              </button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div style={{ padding: 48, textAlign: "center" }}>
            <MI name="loop" size={48} color={integration.color} />
            <h3 style={{ fontSize: 18, fontWeight: 800, color: "#191C1E", margin: "20px 0 8px 0" }}>Authenticating...</h3>
            <p style={{ fontSize: 14, color: "#6D797E" }}>Securely handshaking with {integration.name}</p>
          </div>
        )}

        {step === 2 && (
          <div style={{ padding: 32, textAlign: "center" }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#ecfdf5", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
              <MI name="check" size={32} color="#059669" />
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 900, color: "#191C1E", margin: "0 0 12px 0" }}>Successfully Connected!</h2>
            <p style={{ fontSize: 14, color: "#6D797E", lineHeight: 1.5, margin: "0 0 32px 0" }}>
              Your financial data is now syncing. Your Live Financial Sync dashboard will update shortly.
            </p>
            <button className="btn-primary" onClick={onComplete} style={{ padding: "10px 32px", fontSize: 14 }}>Continue</button>
          </div>
        )}

      </div>
    </div>
  )
}

function IntegrationCard({ id, name, type, icon, color, connected, onToggle }: any) {
  return (
    <div className={s.panel} style={{ borderRadius: 20, padding: 20, border: connected ? `2px solid ${color}` : "1px solid #E0E7EC", transition: "all 0.2s" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: `${color}1a`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <MI name={icon} size={24} color={color} />
        </div>
        <div
          onClick={onToggle}
          style={{
            padding: "4px 12px", borderRadius: 999, fontSize: 11, fontWeight: 800, cursor: "pointer",
            background: connected ? `${color}1a` : "#F2F4F6", color: connected ? color : "#6D797E"
          }}
        >
          {connected ? "CONNECTED" : "CONNECT"}
        </div>
      </div>
      <div style={{ fontSize: 16, fontWeight: 900, color: "#191C1E" }}>{name}</div>
      <div style={{ fontSize: 12, color: "#6D797E", marginTop: 4 }}>{type}</div>
    </div>
  )
}

export function TeamTab() {
  const [inviteOpen, setInviteOpen] = React.useState(false);

  return <div style={{ overflowY: "auto", paddingBottom: 40 }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24 }}>
      <div className={s.pageHeader} style={{ marginBottom: 0 }}>
        <div className={s.pageTitle} style={{ fontSize: 28 }}>Workspace Team</div>
        <div className={s.pageSub}>Manage access for founders, financial reviewers, and external grant writers.</div>
      </div>
      <button className="btn-primary" onClick={() => setInviteOpen(true)} style={{ padding: "8px 16px", fontSize: 14 }}><MI name="person_add" size={18} /> Invite Member</button>
    </div>

    <div className={s.panel} style={{ borderRadius: 24, padding: 0, overflow: "hidden" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
        <thead>
          <tr style={{ background: "#F8FAFC", borderBottom: "1px solid #E0E7EC" }}>
            <th style={{ padding: "16px 24px", fontSize: 12, fontWeight: 800, color: "#6D797E" }}>MEMBER</th>
            <th style={{ padding: "16px 24px", fontSize: 12, fontWeight: 800, color: "#6D797E" }}>ROLE</th>
            <th style={{ padding: "16px 24px", fontSize: 12, fontWeight: 800, color: "#6D797E" }}>STATUS</th>
            <th style={{ padding: "16px 24px", fontSize: 12, fontWeight: 800, color: "#6D797E", textAlign: "right" }}>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <TeamRow name="Alex Johnson" email="alex@nexusdynamics.com" role="Workspace Admin" status="Active" isMe />
          <TeamRow name="Sarah Chen" email="sarah.c@nexusdynamics.com" role="Financial Reviewer" status="Active" />
          <TeamRow name="Marcus Vance" email="marcus@vancegrants.com" role="External Grant Writer" status="Pending" />
        </tbody>
      </table>
    </div>

    {inviteOpen && <InviteModal onClose={() => setInviteOpen(false)} />}
  </div>;
}

function TeamRow({ name, email, role, status, isMe }: any) {
  return (
    <tr style={{ borderBottom: "1px solid #F2F4F6" }}>
      <td style={{ padding: "16px 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: "50%", background: "#006780", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 900 }}>
            {name.charAt(0)}
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, color: "#191C1E", display: "flex", alignItems: "center", gap: 8 }}>
              {name} {isMe && <span style={{ fontSize: 10, background: "#F2F4F6", padding: "2px 6px", borderRadius: 4, color: "#6D797E" }}>YOU</span>}
            </div>
            <div style={{ fontSize: 12, color: "#6D797E", marginTop: 2 }}>{email}</div>
          </div>
        </div>
      </td>
      <td style={{ padding: "16px 24px" }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: "#3D494D" }}>{role}</span>
      </td>
      <td style={{ padding: "16px 24px" }}>
        <span style={{
          fontSize: 11, fontWeight: 800, padding: "4px 10px", borderRadius: 999,
          background: status === "Active" ? "#ecfdf5" : "#fef3c7",
          color: status === "Active" ? "#059669" : "#d97706"
        }}>
          {status}
        </span>
      </td>
      <td style={{ padding: "16px 24px", textAlign: "right" }}>
        <button className="btn-soft" style={{ padding: "6px 8px" }}><MI name="more_vert" size={18} /></button>
      </td>
    </tr>
  )
}

function InviteModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = React.useState(0);

  const handleInvite = () => {
    setStep(1);
    setTimeout(() => setStep(2), 1500);
  };

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(15, 23, 42, 0.4)", backdropFilter: "blur(4px)" }}>
      <div className={s.panel} style={{ width: 500, maxWidth: "90vw", display: "flex", flexDirection: "column", overflow: "hidden", background: "#fff", borderRadius: 24, boxShadow: "0 24px 48px rgba(0,0,0,0.2)", padding: 0 }}>

        {step === 0 && (
          <>
            <div style={{ padding: "20px 24px", borderBottom: "1px solid #E0E7EC", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: 18, fontWeight: 900, color: "#191C1E", margin: 0 }}>Invite Team Member</h2>
              <button onClick={onClose} style={{ background: "transparent", border: "none", cursor: "pointer", padding: 0, display: "flex" }}><MI name="close" size={24} color="#6D797E" /></button>
            </div>
            <div style={{ padding: 24 }}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 700, color: "#3D494D", marginBottom: 8 }}>Email Address</label>
                <div style={{ display: "flex", alignItems: "center", border: "1px solid #E0E7EC", borderRadius: 8, padding: "10px 14px" }}>
                  <MI name="mail" size={18} color="#91A0B6" />
                  <input type="email" placeholder="colleague@company.com" style={{ border: "none", outline: "none", flex: 1, marginLeft: 8, fontSize: 14 }} />
                </div>
              </div>
              <div style={{ marginBottom: 24 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 700, color: "#3D494D", marginBottom: 8 }}>Workspace Role</label>
                <select style={{ width: "100%", padding: "10px 14px", border: "1px solid #E0E7EC", borderRadius: 8, fontSize: 14, outline: "none", backgroundColor: "#fff" }}>
                  <option>Workspace Admin</option>
                  <option>Financial Reviewer</option>
                  <option>External Grant Writer</option>
                  <option>Viewer</option>
                </select>
                <div style={{ fontSize: 11, color: "#6D797E", marginTop: 6 }}>Role permissions can be changed later.</div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 16, margin: "24px 0" }}>
                <div style={{ flex: 1, height: 1, background: "#E0E7EC" }} />
                <span style={{ fontSize: 12, fontWeight: 700, color: "#91A0B6" }}>OR INVITE VIA</span>
                <div style={{ flex: 1, height: 1, background: "#E0E7EC" }} />
              </div>

              <button className="btn-outline" style={{ width: "100%", justifyContent: "center", padding: "10px", fontSize: 14, borderColor: "#E0E7EC", color: "#3D494D", gap: 8, marginBottom: 24 }}>
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" width={18} height={18} alt="Google" />
                Invite from Google Contacts
              </button>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
                <button className="btn-outline-sm" onClick={onClose} style={{ padding: "10px 20px", fontSize: 14 }}>Cancel</button>
                <button className="btn-primary" onClick={handleInvite} style={{ padding: "10px 20px", fontSize: 14 }}>Send Invite</button>
              </div>
            </div>
          </>
        )}

        {step === 1 && (
          <div style={{ padding: 48, textAlign: "center" }}>
            <MI name="mail" size={48} color="#006780" />
            <h3 style={{ fontSize: 18, fontWeight: 800, color: "#191C1E", margin: "20px 0 8px 0" }}>Sending Invitation...</h3>
            <p style={{ fontSize: 14, color: "#6D797E" }}>Dispatching email via Gmail integration.</p>
          </div>
        )}

        {step === 2 && (
          <div style={{ padding: 32, textAlign: "center" }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#ecfdf5", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
              <MI name="check" size={32} color="#059669" />
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 900, color: "#191C1E", margin: "0 0 12px 0" }}>Invite Sent!</h2>
            <p style={{ fontSize: 14, color: "#6D797E", lineHeight: 1.5, margin: "0 0 32px 0" }}>
              They will receive an email shortly with a secure link to join your Grantly workspace.
            </p>
            <button className="btn-primary" onClick={onClose} style={{ padding: "10px 32px", fontSize: 14 }}>Done</button>
          </div>
        )}

      </div>
    </div>
  )
}
