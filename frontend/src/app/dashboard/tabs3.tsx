"use client";
import React from "react";
import { type CompanyProfileRead, type DocumentRead, type UserRead } from "@/services/grantlyApi";
import s from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

type Integration = {
  id: string;
  name: string;
  color: string;
};

type IntegrationCardProps = Integration & {
  type: string;
  icon: string;
  connected?: boolean;
  onToggle: () => void;
};

type TeamRowProps = {
  name: string;
  email: string;
  role: string;
  status: "Active" | "Pending";
  isMe?: boolean;
};

export function IntegrationsTab() {
  const [connected, setConnected] = React.useState<Record<string, boolean>>({
    "sql_account": true
  });
  const [selectedIntegration, setSelectedIntegration] = React.useState<Integration | null>(null);

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

function IntegrationAuthModal({ integration, onClose, onComplete }: { integration: Integration; onClose: () => void; onComplete: () => void }) {
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

function IntegrationCard({ id, name, type, icon, color, connected, onToggle }: IntegrationCardProps) {
  return (
    <div data-integration-id={id} className={s.panel} style={{ borderRadius: 20, padding: 20, border: connected ? `2px solid ${color}` : "1px solid #E0E7EC", transition: "all 0.2s" }}>
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

function TeamRow({ name, email, role, status, isMe }: TeamRowProps) {
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

type ClaimTone = "standard" | "formal" | "concise";
type EvidenceStatus = "Uploaded" | "Missing" | "Needs Review" | "Matched to Expense";

type EvidenceRow = {
  id: string;
  label: string;
  description: string;
  fileName: string;
  status: EvidenceStatus;
};

type DraftSection = {
  title: string;
  body: string;
};

type ReimbursementDraft = {
  title: string;
  subtitle: string;
  sections: DraftSection[];
};

const DEFAULT_EVIDENCE_ROWS: EvidenceRow[] = [
  { id: "invoice", label: "Invoices", description: "Supplier and vendor invoices linked to the claim period.", fileName: "", status: "Missing" },
  { id: "receipts", label: "Receipts", description: "Official receipts for reimbursable project spending.", fileName: "", status: "Missing" },
  { id: "bank", label: "Bank Statements", description: "Payment trail showing transfers and settlement.", fileName: "", status: "Missing" },
  { id: "screens", label: "Screenshots", description: "Progress screenshots, demo images, and workflow proof.", fileName: "", status: "Missing" },
  { id: "progress", label: "Progress Docs", description: "Monthly status notes, meeting minutes, or milestone evidence.", fileName: "", status: "Missing" },
];

const EVIDENCE_STATUSES: EvidenceStatus[] = ["Uploaded", "Missing", "Needs Review", "Matched to Expense"];

function formatClaimCurrency(value: string): string {
  const numeric = Number(value.replace(/[^0-9.]/g, ""));
  if (!Number.isFinite(numeric) || numeric === 0) return "RM 0";
  return `RM ${new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 }).format(numeric)}`;
}

function claimReadinessLabel(score: number): string {
  if (score >= 80) return "Ready to Draft";
  if (score >= 50) return "Needs Review";
  return "Collect More Inputs";
}

function buildReimbursementDraft(
  claim: {
    agency: string;
    grantName: string;
    claimPeriod: string;
    milestoneNumber: string;
    approvedBudget: string;
    actualExpenditure: string;
    claimAmount: string;
  },
  evidenceRows: EvidenceRow[],
  tone: ClaimTone,
): ReimbursementDraft {
  const evidenceSummary = evidenceRows.map((row) => `${row.label}: ${row.status}${row.fileName ? ` (${row.fileName})` : ""}`).join("; ");
  const uploaded = evidenceRows.filter((row) => row.status === "Uploaded" || row.status === "Matched to Expense");
  const needsReview = evidenceRows.filter((row) => row.status === "Needs Review");
  const missing = evidenceRows.filter((row) => row.status === "Missing");
  const evidenceSignal = uploaded.length >= 3 ? "Strong evidence coverage across the claim period." : uploaded.length >= 1 ? "Core evidence is present and ready for review." : "Evidence package still needs supporting files.";
  const formalPrefix = tone === "formal"
    ? `This technical progress report is submitted to ${claim.agency || "the grant agency"} for ${claim.grantName || "the relevant grant"} covering ${claim.claimPeriod || "the current claim period"}.`
    : `This report covers ${claim.grantName || "the grant"} for ${claim.claimPeriod || "the selected claim period"}.`;

  const workCompleted = tone === "concise"
    ? `Completed work is summarised for Milestone ${claim.milestoneNumber || "N/A"} and reflects the implementation progress captured in the evidence package.`
    : `${formalPrefix} The project team completed the milestone work package and documented the implementation progress for reimbursement review.`;

  const kpiAchievement = tone === "concise"
    ? `KPI achievement is aligned with the approved grant expectations and milestone output for this reporting cycle.`
    : `KPI achievement for Milestone ${claim.milestoneNumber || "N/A"} remains aligned with the approved grant expectations, project delivery objectives, and submission requirements.`;

  const challenges = tone === "formal"
    ? `The team monitored implementation risks and resolved operational blockers while keeping the claim evidence traceable for agency review.`
    : `The team tracked implementation risks, resolved blockers, and kept the claim evidence traceable for review.`;

  const fundUtilisation = tone === "concise"
    ? `Approved budget ${formatClaimCurrency(claim.approvedBudget)}; actual expenditure ${formatClaimCurrency(claim.actualExpenditure)}; claim amount ${formatClaimCurrency(claim.claimAmount)}.`
    : `The approved budget for this claim cycle is ${formatClaimCurrency(claim.approvedBudget)}, the actual expenditure recorded is ${formatClaimCurrency(claim.actualExpenditure)}, and the current reimbursement claim amount requested is ${formatClaimCurrency(claim.claimAmount)}.`;

  const milestoneStatus = tone === "formal"
    ? `Milestone ${claim.milestoneNumber || "N/A"} is documented as progress-ready and supported by the current evidence package.`
    : `Milestone ${claim.milestoneNumber || "N/A"} is supported by the current evidence package and project updates.`;

  const conclusion = tone === "concise"
    ? `The project remains on track and the claim is ready for agency review.`
    : `In conclusion, the project remains on track and the evidence package supports the reimbursement claim for ${claim.grantName || "the grant"}.`;

  const opening = tone === "formal"
    ? `This technical progress report is submitted to ${claim.agency || "the grant agency"} for ${claim.grantName || "the relevant grant"} covering ${claim.claimPeriod || "the current claim period"}.`
    : `This report covers ${claim.grantName || "the grant"} for ${claim.claimPeriod || "the selected claim period"}.`;

  const sections: DraftSection[] = [
    { title: "Project Summary", body: `${opening} The AI scan found ${uploaded.length} supporting files, ${needsReview.length} items needing review, and ${missing.length} missing items. ${evidenceSignal}`, },
    { title: "Work Completed", body: workCompleted },
    { title: "KPI Achievement", body: kpiAchievement },
    { title: "Challenges Faced", body: challenges },
    { title: "Fund Utilisation", body: `${fundUtilisation} Evidence status: ${evidenceSummary}.` },
    { title: "Milestone Status", body: milestoneStatus },
    { title: "Conclusion", body: conclusion },
  ];

  if (tone === "formal") {
    sections[0].body += " The draft is prepared in a formal submission style suitable for government or agency review.";
  }

  return {
    title: `${claim.grantName || "Grant"} Reimbursement Draft`,
    subtitle: `${claim.agency || "Agency"} | ${claim.claimPeriod || "Claim period not set"} | Milestone ${claim.milestoneNumber || "N/A"}`,
    sections,
  };
}

function draftToText(draft: ReimbursementDraft): string {
  return [
    draft.title,
    draft.subtitle,
    "",
    ...draft.sections.flatMap((section) => [section.title, section.body, ""]),
  ].join("\n");
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function draftToPrintHtml(draft: ReimbursementDraft): string {
  const sectionsHtml = draft.sections.map((section) => `
    <section class="report-section">
      <h2>${escapeHtml(section.title)}</h2>
      <p>${escapeHtml(section.body).replace(/\n/g, "<br />")}</p>
    </section>
  `).join("");

  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>${escapeHtml(draft.title)}</title>
      <style>
        :root {
          --ink: #0f172a;
          --muted: #475569;
          --line: #dce3ec;
          --accent: #006780;
          --accent2: #494bd6;
        }
        @page { size: A4; margin: 18mm; }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          font-family: Inter, Arial, sans-serif;
          color: var(--ink);
          background: #f8fafc;
        }
        .page {
          max-width: 860px;
          margin: 0 auto;
          background: #fff;
          min-height: 100vh;
          padding: 40px 36px;
        }
        .header {
          border-bottom: 2px solid var(--line);
          padding-bottom: 20px;
          margin-bottom: 24px;
        }
        .eyebrow {
          font-size: 12px;
          font-weight: 800;
          letter-spacing: 1.8px;
          color: var(--accent);
          text-transform: uppercase;
        }
        h1 {
          font-size: 28px;
          line-height: 1.15;
          margin: 10px 0 8px;
          font-weight: 900;
        }
        .subtitle {
          color: var(--muted);
          font-size: 13px;
          line-height: 1.5;
        }
        .meta {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 10px;
          margin-top: 18px;
        }
        .meta div {
          border: 1px solid var(--line);
          border-radius: 14px;
          padding: 12px 14px;
          background: #f8fafc;
        }
        .meta label {
          display: block;
          font-size: 10px;
          font-weight: 900;
          letter-spacing: 1.2px;
          color: var(--muted);
          margin-bottom: 4px;
        }
        .meta span {
          font-size: 13px;
          font-weight: 800;
          color: var(--ink);
        }
        .report-section {
          padding: 18px 18px 20px;
          border: 1px solid var(--line);
          border-radius: 18px;
          margin-bottom: 16px;
          break-inside: avoid;
          page-break-inside: avoid;
          background: linear-gradient(180deg, #fff, #fbfdff);
        }
        .report-section h2 {
          margin: 0 0 10px;
          font-size: 14px;
          letter-spacing: 1px;
          color: var(--accent);
          text-transform: uppercase;
        }
        .report-section p {
          margin: 0;
          font-size: 14px;
          line-height: 1.75;
          color: var(--ink);
          white-space: normal;
        }
        .footer {
          margin-top: 24px;
          padding-top: 14px;
          border-top: 1px solid var(--line);
          font-size: 11px;
          color: var(--muted);
          display: flex;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
        }
        .pill {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 10px;
          border-radius: 999px;
          background: #eef9fd;
          color: var(--accent);
          font-weight: 800;
          font-size: 11px;
        }
      </style>
    </head>
    <body>
      <div class="page">
        <div class="header">
          <div class="eyebrow">Reimbursement Draft</div>
          <h1>${escapeHtml(draft.title)}</h1>
          <div class="subtitle">${escapeHtml(draft.subtitle)}</div>
          <div class="meta">
            <div><label>Report Type</label><span>Technical Progress Report</span></div>
            <div><label>Status</label><span>Submission Ready</span></div>
            <div><label>Format</label><span>Agency / PDF Export</span></div>
          </div>
        </div>
        ${sectionsHtml}
        <div class="footer">
          <span>${escapeHtml(new Date().toLocaleString())}</span>
          <span class="pill">Generated by Grantly AI</span>
        </div>
      </div>
    </body>
  </html>`;
}

type AnalysisPhase = "idle" | "scanning" | "extracting" | "cross-checking" | "drafting" | "complete";

type IntelligenceSignal = {
  label: string;
  detail: string;
  status: "Detected" | "Indexed" | "Matched" | "Missing" | "Needs Review";
  source: string;
  confidence: number;
};

function normalizeText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ");
}

function detectSignals(documents: DocumentRead[]): IntelligenceSignal[] {
  const rows = [
    { label: "SSM Certificate", keywords: ["ssm", "certificate", "registration", "business profile"], source: "Company registry" },
    { label: "Financial Statement", keywords: ["financial", "statement", "accounts", "income", "balance"], source: "Accounting file" },
    { label: "Bank Statement", keywords: ["bank", "statement", "transfer", "payment"], source: "Cashflow proof" },
    { label: "Invoices & Receipts", keywords: ["invoice", "receipt", "bill", "supplier"], source: "Expense evidence" },
    { label: "Project Progress", keywords: ["progress", "report", "milestone", "demo", "update"], source: "Technical evidence" },
    { label: "Screenshots / Images", keywords: ["screenshot", "image", "png", "jpg", "jpeg", "demo"], source: "Visual proof" },
  ];

  const docs = documents.map((document) => ({
    ...document,
    normalized: normalizeText(`${document.file_name} ${document.document_type} ${document.status}`),
  }));

  return rows.map((row, index) => {
    const match = docs.find((document) => row.keywords.some((keyword) => document.normalized.includes(keyword)));
    const status: IntelligenceSignal["status"] = match
      ? row.label === "Invoices & Receipts" || row.label === "Bank Statement"
        ? "Matched"
        : "Detected"
      : index < 2
        ? "Needs Review"
        : "Missing";
    return {
      label: row.label,
      source: row.source,
      detail: match ? match.file_name : `No ${row.label.toLowerCase()} found in the workspace vault.`,
      status,
      confidence: match ? 84 - index * 4 : 36 + index * 3,
    };
  });
}

function buildSuggestedClaim(profile: CompanyProfileRead | null | undefined, documents: DocumentRead[]): {
  agency: string;
  grantName: string;
  claimPeriod: string;
  milestoneNumber: string;
  approvedBudget: string;
  actualExpenditure: string;
  claimAmount: string;
} {
  const signalCount = detectSignals(documents).filter((signal) => signal.status !== "Missing").length;
  const baseBudget = profile?.target_grant_amount ? String(profile.target_grant_amount) : "250000";
  const expenditure = signalCount > 3 ? "184500" : "124000";
  const claimAmount = signalCount > 3 ? "75000" : "50000";

  return {
    agency: "MDEC / SME Corp",
    grantName: profile?.company_name ? `${profile.company_name} Grant Reimbursement` : "Grant Reimbursement Claim",
    claimPeriod: "Current claim cycle",
    milestoneNumber: signalCount > 4 ? "2" : "1",
    approvedBudget: baseBudget,
    actualExpenditure: expenditure,
    claimAmount,
  };
}

export function ReimbursementTab({
  currentUser,
  profile,
  documents = [],
}: {
  currentUser?: UserRead | null;
  profile?: CompanyProfileRead | null;
  documents?: DocumentRead[];
}) {
  const [claim, setClaim] = React.useState({
    agency: "MDEC / SME Corp",
    grantName: profile?.company_name ? `${profile.company_name} Grant Reimbursement` : "Grant Reimbursement Claim",
    claimPeriod: "Current claim cycle",
    milestoneNumber: "1",
    approvedBudget: profile?.target_grant_amount ? String(profile.target_grant_amount) : "250000",
    actualExpenditure: "184500",
    claimAmount: "75000",
  });
  const [evidenceRows, setEvidenceRows] = React.useState<EvidenceRow[]>(DEFAULT_EVIDENCE_ROWS);
  const [draft, setDraft] = React.useState<ReimbursementDraft | null>(null);
  const [tone, setTone] = React.useState<ClaimTone>("formal");
  const [copyState, setCopyState] = React.useState<"idle" | "copied">("idle");
  const [analysisPhase, setAnalysisPhase] = React.useState<AnalysisPhase>("idle");
  const [analysisProgress, setAnalysisProgress] = React.useState(0);
  const [analysisHeadline, setAnalysisHeadline] = React.useState("Run autonomous analysis to read the workspace and build the submission pack.");
  const [analysisLog, setAnalysisLog] = React.useState<string[]>(["Waiting for workspace scan."]);
  const [selectedSection, setSelectedSection] = React.useState(0);

  const timersRef = React.useRef<number[]>([]);
  const runIdRef = React.useRef(0);
  const claimRef = React.useRef(claim);
  const evidenceRef = React.useRef(evidenceRows);
  const profileRef = React.useRef(profile);
  const documentsRef = React.useRef(documents);

  React.useEffect(() => {
    claimRef.current = claim;
  }, [claim]);
  React.useEffect(() => {
    evidenceRef.current = evidenceRows;
  }, [evidenceRows]);
  React.useEffect(() => {
    profileRef.current = profile;
  }, [profile]);
  React.useEffect(() => {
    documentsRef.current = documents;
  }, [documents]);

  const clearAnalysisTimers = React.useCallback(() => {
    for (const timer of timersRef.current) {
      window.clearTimeout(timer);
    }
    timersRef.current = [];
  }, []);

  React.useEffect(() => () => clearAnalysisTimers(), [clearAnalysisTimers]);

  const analysisSignals = detectSignals(documents);
  const evidenceScore = evidenceRows.filter((row) => row.status === "Uploaded" || row.status === "Matched to Expense").length;
  const formScore = [
    claim.agency.trim(),
    claim.grantName.trim(),
    claim.claimPeriod.trim(),
    claim.milestoneNumber.trim(),
    claim.approvedBudget.trim(),
    claim.actualExpenditure.trim(),
    claim.claimAmount.trim(),
  ].filter(Boolean).length;
  const readinessScore = Math.round(((formScore / 7) * 42) + ((evidenceScore / evidenceRows.length) * 28) + Math.min(30, analysisSignals.filter((signal) => signal.status !== "Missing").length * 6));
  const analysisConfidence = Math.min(99, 52 + analysisSignals.filter((signal) => signal.status !== "Missing").length * 7 + (analysisPhase === "complete" ? 10 : 0));
  const analysisBadge = analysisPhase === "complete" ? "AI draft ready" : analysisPhase === "drafting" ? "Synthesizing report" : analysisPhase === "cross-checking" ? "Reconciling evidence" : analysisPhase === "extracting" ? "Extracting data" : analysisPhase === "scanning" ? "Scanning workspace" : "Idle";

  const updateEvidence = (id: string, patch: Partial<EvidenceRow>) => {
    setEvidenceRows((current) => {
      const nextRows = current.map((row) => (row.id === id ? { ...row, ...patch } : row));
      if (draft) {
        setDraft(buildReimbursementDraft(claimRef.current, nextRows, tone));
      }
      return nextRows;
    });
  };

  const updateClaimField = (key: keyof typeof claim, value: string) => {
    setClaim((current) => {
      const nextClaim = { ...current, [key]: value };
      if (draft) {
        setDraft(buildReimbursementDraft(nextClaim, evidenceRef.current, tone));
      }
      return nextClaim;
    });
  };

  const updateSection = (index: number, body: string) => {
    setDraft((current) => {
      if (!current) return current;
      const sections = current.sections.map((section, sectionIndex) => (sectionIndex === index ? { ...section, body } : section));
      return { ...current, sections };
    });
  };

  const copyDraft = async () => {
    if (!draft) return;
    await navigator.clipboard.writeText(draftToText(draft));
    setCopyState("copied");
    window.setTimeout(() => setCopyState("idle"), 1500);
  };

  const exportAsPdf = () => {
    if (!draft) return;
    const frame = document.createElement("iframe");
    frame.style.position = "fixed";
    frame.style.right = "0";
    frame.style.bottom = "0";
    frame.style.width = "0";
    frame.style.height = "0";
    frame.style.border = "0";
    frame.style.visibility = "hidden";
    frame.setAttribute("aria-hidden", "true");
    document.body.appendChild(frame);

    const cleanup = () => {
      window.setTimeout(() => {
        frame.remove();
      }, 1000);
    };

    frame.onload = () => {
      const frameWindow = frame.contentWindow;
      if (!frameWindow) {
        cleanup();
        return;
      }

      const triggerPrint = () => {
        frameWindow.focus();
        frameWindow.print();
        cleanup();
      };

      window.setTimeout(() => {
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(triggerPrint);
        });
      }, 150);
    };

    frame.srcdoc = draftToPrintHtml(draft);
  };

  const runAnalysis = React.useCallback((reason: "auto" | "manual" = "manual") => {
    clearAnalysisTimers();
    const runId = ++runIdRef.current;
    const currentDocuments = documentsRef.current;
    const currentProfile = profileRef.current;
    const suggestedClaim = buildSuggestedClaim(currentProfile, currentDocuments);
    const signals = detectSignals(currentDocuments);
    const updatedEvidence = evidenceRef.current.map((row) => {
      const linkedSignal =
        row.label === "Invoices" || row.label === "Receipts" ? signals.find((signal) => signal.label === "Invoices & Receipts") :
        row.label === "Bank Statements" ? signals.find((signal) => signal.label === "Bank Statement") :
        row.label === "Screenshots / Images" ? signals.find((signal) => signal.label === "Screenshots / Images") :
        row.label === "Progress Docs" ? signals.find((signal) => signal.label === "Project Progress") :
        null;

      return {
        ...row,
        fileName: linkedSignal && !linkedSignal.detail.startsWith("No ") ? linkedSignal.detail : row.fileName,
        status: linkedSignal?.status === "Matched" ? "Matched to Expense" : linkedSignal?.status === "Detected" ? "Uploaded" : linkedSignal?.status === "Needs Review" ? "Needs Review" : row.status,
      };
    });
    const finalDraft = buildReimbursementDraft(suggestedClaim, updatedEvidence, "formal");

    setCopyState("idle");
    setDraft(null);
    setTone("formal");
    setClaim(suggestedClaim);
    setEvidenceRows(updatedEvidence);
    setAnalysisPhase("scanning");
    setAnalysisProgress(8);
    setAnalysisHeadline(reason === "auto" ? "Autonomous scan started automatically from the workspace." : "Autonomous scan started from the workspace.");
    setAnalysisLog([
      "Workspace unlocked and the reimbursement agent is reading source documents.",
      `Detected ${signals.filter((signal) => signal.status !== "Missing").length} relevant evidence signals.`,
    ]);

    const steps: Array<{ phase: AnalysisPhase; progress: number; headline: string; log: string }> = [
      { phase: "extracting", progress: 25, headline: "Reading SSM certificate, financial statement, and grant metadata...", log: "Identity and finance records have been indexed." },
      { phase: "cross-checking", progress: 52, headline: "Cross-checking receipts, bank movement, and expenditure lines...", log: "Evidence rows are being matched to expenses." },
      { phase: "drafting", progress: 78, headline: "Assembling a formal technical progress report...", log: "Project summary, KPI achievement, and utilisation sections are being composed." },
    ];

    steps.forEach((step, index) => {
      const timer = window.setTimeout(() => {
        if (runIdRef.current !== runId) return;
        setAnalysisPhase(step.phase);
        setAnalysisProgress(step.progress);
        setAnalysisHeadline(step.headline);
        setAnalysisLog((current) => [...current.slice(-3), step.log]);
      }, 850 * (index + 1));
      timersRef.current.push(timer);
    });

    const finishTimer = window.setTimeout(() => {
      if (runIdRef.current !== runId) return;
      setAnalysisPhase("complete");
      setAnalysisProgress(100);
      setAnalysisHeadline("Formal reimbursement draft generated and ready for review.");
      setAnalysisLog((current) => [...current.slice(-3), "Report assembled, evidence tagged, and submission tone set to formal."]);
      setDraft(finalDraft);
      setSelectedSection(0);
    }, 850 * (steps.length + 1));
    timersRef.current.push(finishTimer);
  }, [clearAnalysisTimers]);

  const regenerateDraft = (requestedTone: ClaimTone) => {
    setTone(requestedTone);
    if (!draft) return;
    setDraft(buildReimbursementDraft(claimRef.current, evidenceRef.current, requestedTone));
  };

  React.useEffect(() => {
    const timer = window.setTimeout(() => runAnalysis("auto"), 300);
    return () => window.clearTimeout(timer);
  }, [runAnalysis]);

  if (!currentUser) {
    return (
      <div style={{ overflowY: "auto", paddingBottom: 40 }}>
        <div className={s.panel} style={{ borderRadius: 26, padding: 28, textAlign: "center" }}>
          <MI name="lock" size={30} color="#006780" />
          <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E", marginTop: 10 }}>No workspace session</div>
          <div style={{ fontSize: 13, color: "#3D494D", marginTop: 8 }}>Log in first, then return to the Reimbursement tab to prepare a claim draft.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ overflowY: "auto", paddingBottom: 40 }}>
      <div className={s.pageHeader} style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span className={s.tag} style={{ background: "#FFF4E5", color: "#904D00" }}>Premium</span>
          <span style={{ fontSize: 12, fontWeight: 900, letterSpacing: 1.6, color: "#006780" }}>AI REIMBURSEMENT DRAFTER</span>
          <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>{analysisBadge}</span>
        </div>
        <div className={s.pageTitle} style={{ fontSize: 28, marginTop: 12 }}>Claim Draft Workspace</div>
        <div className={s.pageSub}>
          Let the AI read your SSM certificate, financial statement, invoices, receipts, and project evidence, then assemble a formal reimbursement report you can review and submit.
        </div>
      </div>

      <div className={s.panel} style={{ borderRadius: 28, padding: 22, marginBottom: 18, background: "linear-gradient(135deg, rgba(0,103,128,0.08), rgba(73,75,214,0.06))" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <div className="animate-spin" style={{ width: 20, height: 20, borderRadius: "50%", border: "2px solid rgba(0,180,216,0.2)", borderTopColor: "#00B4D8" }} />
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>{analysisHeadline}</div>
            </div>
            <div style={{ fontSize: 13, color: "#3D494D", marginTop: 6 }}>
              The reimbursement agent is reading the workspace, classifying evidence, and drafting the submission pack automatically.
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <span className={s.tag} style={{ background: "#F2F4F6", color: "#3D494D" }}>Confidence {analysisConfidence}%</span>
            <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>{documents.length} source files</span>
            <button type="button" className="btn-primary" onClick={() => runAnalysis("manual")}>
              <MI name="auto_awesome" size={15} color="#fff" />
              Re-run Analysis
            </button>
          </div>
        </div>
        <div style={{ height: 16 }} />
        <div style={{ height: 10, borderRadius: 999, background: "rgba(0,0,0,0.06)", overflow: "hidden" }}>
          <div style={{ width: `${analysisProgress}%`, height: "100%", borderRadius: 999, background: "linear-gradient(90deg, #006780, #494BD6)", transition: "width 0.35s ease" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginTop: 10, fontSize: 12, color: "#5F6E84", flexWrap: "wrap" }}>
          <span>{analysisPhase === "complete" ? "Workspace scan complete" : "Scanning workspace and building claim pack"}</span>
          <span>{Math.max(analysisProgress, evidenceScore * 10)}% processed</span>
        </div>
        <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 8 }}>
          {analysisLog.map((entry, index) => (
            <div key={`${entry}-${index}`} style={{ display: "flex", gap: 10, alignItems: "center", color: "#334155", fontSize: 13 }}>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: index === analysisLog.length - 1 ? "#00B4D8" : "#91A0B6", boxShadow: index === analysisLog.length - 1 ? "0 0 0 6px rgba(0,180,216,0.08)" : undefined }} />
              <span>{entry}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.15fr) minmax(320px, 0.85fr)", gap: 18, alignItems: "start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className={s.panel} style={{ borderRadius: 26, padding: 22, background: "linear-gradient(135deg, rgba(255,255,255,0.96), rgba(242,244,246,0.72))" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 900, letterSpacing: 1.2, color: "#006780" }}>AI EXTRACTED CLAIM CONTEXT</div>
                <div style={{ fontSize: 28, fontWeight: 900, color: "#191C1E", marginTop: 6 }}>{readinessScore}%</div>
                <div style={{ fontSize: 13, color: "#3D494D", marginTop: 4 }}>{claimReadinessLabel(readinessScore)}</div>
              </div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>{evidenceScore}/{evidenceRows.length} evidence linked</span>
                <span className={s.tag} style={{ background: "#F2F4F6", color: "#3D494D" }}>{documents.length} workspace documents</span>
              </div>
            </div>
            <div style={{ height: 16 }} />
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
              <InfoPill label="Grant Agency" value={claim.agency} />
              <InfoPill label="Grant Name" value={claim.grantName} />
              <InfoPill label="Claim Period" value={claim.claimPeriod} />
              <InfoPill label="Milestone" value={claim.milestoneNumber} />
              <InfoPill label="Claim Amount" value={formatClaimCurrency(claim.claimAmount)} />
              <InfoPill label="Evidence Confidence" value={`${analysisConfidence}%`} />
            </div>
          </div>

          <div className={s.panel} style={{ borderRadius: 26, padding: 22 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <MI name="document_scanner" size={18} color="#006780" />
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Claim Information</div>
              <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>AI suggested</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
              <ClaimField label="Grant Agency" value={claim.agency} onChange={(value) => updateClaimField("agency", value)} placeholder="MDEC / SME Corp / Other" />
              <ClaimField label="Grant Name" value={claim.grantName} onChange={(value) => updateClaimField("grantName", value)} placeholder="Project grant name" />
              <ClaimField label="Claim Period" value={claim.claimPeriod} onChange={(value) => updateClaimField("claimPeriod", value)} placeholder="Jan 2026 - Mar 2026" />
              <ClaimField label="Milestone Number" value={claim.milestoneNumber} onChange={(value) => updateClaimField("milestoneNumber", value)} placeholder="1" />
              <ClaimField label="Approved Budget" value={claim.approvedBudget} onChange={(value) => updateClaimField("approvedBudget", value)} placeholder="250000" />
              <ClaimField label="Actual Expenditure" value={claim.actualExpenditure} onChange={(value) => updateClaimField("actualExpenditure", value)} placeholder="184500" />
              <ClaimField label="Claim Amount" value={claim.claimAmount} onChange={(value) => updateClaimField("claimAmount", value)} placeholder="75000" />
            </div>
          </div>

          <div className={s.panel} style={{ borderRadius: 26, padding: 22 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <MI name="storage" size={18} color="#006780" />
                <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Supporting Evidence</div>
              </div>
              <span className={s.tag} style={{ background: "#F2F4F6", color: "#3D494D" }}>Invoices, receipts, bank statements, screenshots, and docs</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {evidenceRows.map((row) => (
                <EvidenceRowCard
                  key={row.id}
                  row={row}
                  onUpload={(fileName) => updateEvidence(row.id, { fileName, status: "Uploaded" })}
                  onStatusChange={(status) => updateEvidence(row.id, { status })}
                />
              ))}
            </div>
          </div>

        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16, position: "sticky", top: 12 }}>
          <div className={s.panel} style={{ borderRadius: 26, padding: 22, background: "linear-gradient(180deg, rgba(255,255,255,0.98), rgba(242,244,246,0.7))" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <MI name="radar" size={18} color="#494BD6" />
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Workspace Intelligence</div>
            </div>
            <div style={{ height: 14 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {analysisSignals.map((signal) => (
                <div key={signal.label} style={{ padding: 12, borderRadius: 16, background: "#fff", border: "1px solid #E0E7EC" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 900, color: "#191C1E" }}>{signal.label}</div>
                      <div style={{ fontSize: 12, color: "#5F6E84", marginTop: 4 }}>{signal.detail}</div>
                    </div>
                    <span className={s.tag} style={{ background: signal.status === "Matched" ? "#ECFDF5" : signal.status === "Needs Review" ? "#FFF4E5" : signal.status === "Missing" ? "#F2F4F6" : "#EAF8FC", color: signal.status === "Matched" ? "#059669" : signal.status === "Needs Review" ? "#904D00" : signal.status === "Missing" ? "#5F6E84" : "#006780" }}>
                      {signal.status}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginTop: 10, color: "#6B7280", fontSize: 11 }}>
                    <span>{signal.source}</span>
                    <span>{signal.confidence}% confidence</span>
                  </div>
                  <div style={{ height: 8, marginTop: 10, borderRadius: 999, background: "#F2F4F6", overflow: "hidden" }}>
                    <div style={{ width: `${signal.confidence}%`, height: "100%", borderRadius: 999, background: signal.status === "Missing" ? "#D7DEE4" : "linear-gradient(90deg, #006780, #494BD6)" }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={s.panel} style={{ borderRadius: 26, padding: 22 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <MI name="menu_book" size={18} color="#904D00" />
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Submission Blueprint</div>
            </div>
            <div style={{ height: 14 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {["Project summary", "Work completed", "KPI achievement", "Challenges faced", "Fund utilisation", "Milestone status", "Conclusion"].map((item) => (
                <div key={item} style={{ display: "flex", alignItems: "center", gap: 10, color: "#3D494D", fontSize: 13 }}>
                  <MI name="check_circle" size={14} color="#00B4D8" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={s.panel} style={{ borderRadius: 26, padding: 22 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <MI name="auto_awesome" size={18} color="#494BD6" />
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Submission Tone</div>
            </div>
            <div style={{ height: 12 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <ToneButton label="Standard" active={tone === "standard"} onClick={() => regenerateDraft("standard")} />
              <ToneButton label="More Formal" active={tone === "formal"} onClick={() => regenerateDraft("formal")} />
              <ToneButton label="Shorter Report" active={tone === "concise"} onClick={() => regenerateDraft("concise")} />
            </div>
          </div>
        </div>
      </div>

      <div style={{ height: 18 }} />

      <div className={s.panel} style={{ borderRadius: 28, padding: 0, overflow: "hidden", background: "#fff" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", padding: "20px 22px", borderBottom: "1px solid #E0E7EC", background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)", flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Document Editor</div>
            <div style={{ fontSize: 13, color: "#3D494D", marginTop: 4 }}>Review and edit the generated report before exporting or copying it.</div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" className="btn-soft" onClick={() => runAnalysis("manual")}><MI name="restart_alt" size={14} />Regenerate</button>
            <button type="button" className="btn-soft" onClick={() => regenerateDraft("formal")}><MI name="stacks" size={14} />Make More Formal</button>
            <button type="button" className="btn-soft" onClick={() => regenerateDraft("concise")}><MI name="short_text" size={14} />Shorten Report</button>
            <button type="button" className="btn-soft" onClick={exportAsPdf}><MI name="picture_as_pdf" size={14} />Export as PDF</button>
            <button type="button" className="btn-primary" onClick={copyDraft}><MI name="content_copy" size={14} color="#fff" />{copyState === "copied" ? "Copied" : "Copy to Clipboard"}</button>
          </div>
        </div>

        {draft ? (
          <div style={{ padding: 22, background: "#F8FAFC" }}>
            <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 320px) minmax(0, 1fr)", gap: 18, alignItems: "start", maxWidth: 1240, margin: "0 auto" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className={s.panel} style={{ borderRadius: 24, padding: 20, background: "linear-gradient(135deg, rgba(0,103,128,0.08), rgba(73,75,214,0.05))" }}>
                  <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: 1.4, color: "#006780" }}>DRAFT SNAPSHOT</div>
                  <div style={{ fontSize: 21, fontWeight: 900, color: "#191C1E", marginTop: 8 }} contentEditable suppressContentEditableWarning>{draft.title}</div>
                  <div style={{ fontSize: 13, color: "#5F6E84", marginTop: 6 }} contentEditable suppressContentEditableWarning>{draft.subtitle}</div>
                  <div style={{ height: 14 }} />
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 10 }}>
                    <InfoPill label="Sections" value={`${draft.sections.length}`} />
                    <InfoPill label="Tone" value={tone === "formal" ? "Formal" : tone === "concise" ? "Concise" : "Standard"} />
                    <InfoPill label="Evidence" value={`${evidenceRows.filter((row) => row.status !== "Missing").length}/${evidenceRows.length}`} />
                    <InfoPill label="Confidence" value={`${analysisConfidence}%`} />
                  </div>
                </div>

                <div className={s.panel} style={{ borderRadius: 24, padding: 20 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
                    <div style={{ fontSize: 16, fontWeight: 900, color: "#191C1E" }}>Section Map</div>
                    <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>Tap to focus</span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {draft.sections.map((section, index) => (
                      <button
                        key={section.title}
                        type="button"
                        onClick={() => setSelectedSection(index)}
                        style={{
                          textAlign: "left",
                          padding: 14,
                          borderRadius: 18,
                          border: selectedSection === index ? "1px solid #00B4D8" : "1px solid #E0E7EC",
                          background: selectedSection === index ? "linear-gradient(135deg, rgba(0,180,216,0.08), rgba(73,75,214,0.04))" : "#fff",
                          boxShadow: selectedSection === index ? "0 14px 28px rgba(0, 180, 216, 0.10)" : "none",
                          cursor: "pointer",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
                          <div>
                            <div style={{ fontSize: 13, fontWeight: 900, color: "#191C1E" }}>{section.title}</div>
                            <div style={{ fontSize: 11, color: "#5F6E84", marginTop: 4, lineHeight: 1.45, overflow: "hidden", textOverflow: "ellipsis" }}>
                              {section.body.slice(0, 90)}{section.body.length > 90 ? "..." : ""}
                            </div>
                          </div>
                          <MI name={selectedSection === index ? "chevron_right" : "drag_handle"} size={16} color={selectedSection === index ? "#006780" : "#91A0B6"} />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className={s.panel} style={{ borderRadius: 28, padding: 0, overflow: "hidden", background: "#fff" }}>
                <div style={{ padding: "20px 22px", borderBottom: "1px solid #E0E7EC", background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)", display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>Compiled Report Studio</div>
                    <div style={{ fontSize: 13, color: "#3D494D", marginTop: 4 }}>Edit any section directly in the full report, then export the entire submission as a PDF.</div>
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button type="button" className="btn-soft" onClick={() => regenerateDraft("formal")}><MI name="stacks" size={14} />Formalize</button>
                    <button type="button" className="btn-soft" onClick={() => regenerateDraft("concise")}><MI name="short_text" size={14} />Shorten</button>
                    <button type="button" className="btn-soft" onClick={() => regenerateDraft("standard")}><MI name="autorenew" size={14} />Refresh</button>
                    <button type="button" className="btn-primary" onClick={exportAsPdf}><MI name="picture_as_pdf" size={14} color="#fff" />Download PDF</button>
                  </div>
                </div>

                <div style={{ padding: 22, background: "#F8FAFC" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.35fr) minmax(220px, 0.65fr)", gap: 16, alignItems: "start" }}>
                    <div style={{ background: "#fff", borderRadius: 24, border: "1px solid #E0E7EC", boxShadow: "0 18px 40px rgba(25, 28, 30, 0.08)", padding: 24 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 16 }}>
                        <div>
                          <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: 1.2, color: "#006780" }}>LIVE DOCUMENT</div>
                          <div style={{ fontSize: 20, fontWeight: 900, color: "#191C1E", marginTop: 6 }}>{draft.title}</div>
                        </div>
                        <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>AI drafted</span>
                      </div>
                      <div style={{ fontSize: 13, color: "#5F6E84", marginBottom: 14 }} contentEditable suppressContentEditableWarning>
                        {draft.subtitle}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        {draft.sections.map((section, index) => (
                          <div
                            key={section.title}
                            style={{
                              padding: 16,
                              borderRadius: 18,
                              border: selectedSection === index ? "1px solid #00B4D8" : "1px solid #E0E7EC",
                              background: selectedSection === index ? "linear-gradient(135deg, rgba(0,180,216,0.08), rgba(73,75,214,0.04))" : "#fff",
                              boxShadow: selectedSection === index ? "0 12px 24px rgba(0, 180, 216, 0.08)" : "none",
                            }}
                          >
                            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", marginBottom: 10, flexWrap: "wrap" }}>
                              <div style={{ fontSize: 13, fontWeight: 900, letterSpacing: 0.8, color: "#006780" }}>{section.title.toUpperCase()}</div>
                              <button type="button" className="btn-soft" style={{ padding: "6px 10px", fontSize: 12 }} onClick={() => setSelectedSection(index)}>
                                <MI name="center_focus_strong" size={14} />Focus
                              </button>
                            </div>
                            <textarea
                              value={section.body}
                              onChange={(event) => updateSection(index, event.target.value)}
                              style={{
                                width: "100%",
                                minHeight: index === selectedSection ? 220 : 130,
                                padding: 16,
                                border: "1px solid #E0E7EC",
                                borderRadius: 16,
                                background: "#fff",
                                resize: "vertical",
                                color: "#191C1E",
                                lineHeight: 1.75,
                                fontSize: 14,
                                boxShadow: "inset 0 1px 0 rgba(255,255,255,0.6)",
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                      <div className={s.panel} style={{ borderRadius: 22, padding: 18, background: "linear-gradient(180deg, rgba(255,255,255,0.96), rgba(242,244,246,0.72))" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                          <MI name="auto_awesome" size={18} color="#494BD6" />
                          <div style={{ fontSize: 15, fontWeight: 900, color: "#191C1E" }}>What this section is doing</div>
                        </div>
                        <div style={{ fontSize: 13, color: "#3D494D", lineHeight: 1.55 }}>
                          {selectedSection === 0 && "This section frames the submission, agency, claim period, and the overall evidence position."}
                          {selectedSection === 1 && "This section describes completed implementation work for the claim cycle."}
                          {selectedSection === 2 && "This section states how the milestone outputs align with the approved grant expectations."}
                          {selectedSection === 3 && "This section captures blockers, issues, and how the team handled follow-up."}
                          {selectedSection === 4 && "This section summarizes budget, actual spend, and claim amount for reimbursement review."}
                          {selectedSection === 5 && "This section confirms milestone readiness and supporting evidence."}
                          {selectedSection === 6 && "This section closes the report with the submission-ready conclusion."}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ padding: 28, textAlign: "center", color: "#5F6E84" }}>
            The AI agent is still compiling the submission. If you click re-run analysis, the draft will regenerate with fresh source signals.
          </div>
        )}
      </div>
    </div>
  );
}

function ClaimField({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <span style={{ fontSize: 12, fontWeight: 800, letterSpacing: 1, color: "#5F6E84" }}>{label.toUpperCase()}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        style={{ padding: "12px 14px", border: "1px solid #E0E7EC", borderRadius: 14, background: "#fff", fontSize: 14, color: "#191C1E" }}
      />
    </label>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: 14, borderRadius: 18, background: "#fff", border: "1px solid #E0E7EC", boxShadow: "0 4px 12px rgba(25, 28, 30, 0.03)" }}>
      <div style={{ fontSize: 11, fontWeight: 900, letterSpacing: 1.2, color: "#5F6E84" }}>{label.toUpperCase()}</div>
      <div style={{ fontSize: 14, fontWeight: 800, color: "#191C1E", marginTop: 6, lineHeight: 1.4 }}>{value}</div>
    </div>
  );
}

function EvidenceRowCard({
  row,
  onUpload,
  onStatusChange,
}: {
  row: EvidenceRow;
  onUpload: (fileName: string) => void;
  onStatusChange: (status: EvidenceStatus) => void;
}) {
  const fileId = `evidence-${row.id}`;

  return (
    <div style={{ border: "1px solid #E0E7EC", borderRadius: 18, padding: 14, background: "#fff" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 900, color: "#191C1E" }}>{row.label}</div>
          <div style={{ fontSize: 12, color: "#5F6E84", marginTop: 4, lineHeight: 1.4 }}>{row.description}</div>
        </div>
        <span className={s.tag} style={{ background: row.status === "Matched to Expense" ? "#ECFDF5" : row.status === "Needs Review" ? "#FFF4E5" : row.status === "Uploaded" ? "#EAF8FC" : "#F2F4F6", color: row.status === "Matched to Expense" ? "#059669" : row.status === "Needs Review" ? "#904D00" : row.status === "Uploaded" ? "#006780" : "#5F6E84" }}>
          {row.status}
        </span>
      </div>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginTop: 14 }}>
        <input
          id={fileId}
          type="file"
          style={{ display: "none" }}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onUpload(file.name);
            event.currentTarget.value = "";
          }}
        />
        <label htmlFor={fileId} className="btn-soft" style={{ padding: "8px 14px" }}>
          <MI name="upload_file" size={14} />{row.fileName ? "Replace File" : "Upload File"}
        </label>
        <div style={{ flex: 1, minWidth: 180, padding: "10px 12px", borderRadius: 14, border: "1px dashed #E0E7EC", color: row.fileName ? "#191C1E" : "#91A0B6", fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {row.fileName || "No file uploaded yet"}
        </div>
        <select
          value={row.status}
          onChange={(event) => onStatusChange(event.target.value as EvidenceStatus)}
          style={{ padding: "10px 12px", borderRadius: 14, border: "1px solid #E0E7EC", background: "#fff", color: "#191C1E", fontSize: 13 }}
        >
          {EVIDENCE_STATUSES.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </div>
    </div>
  );
}

function ToneButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="btn-soft"
      style={{
        justifyContent: "flex-start",
        background: active ? "rgba(0,180,216,0.10)" : "#fff",
        borderColor: active ? "#00B4D8" : "#E0E7EC",
        color: active ? "#006780" : "#3D494D",
      }}
    >
      <MI name={active ? "radio_button_checked" : "radio_button_unchecked"} size={14} color={active ? "#006780" : "#91A0B6"} />
      {label}
    </button>
  );
}
