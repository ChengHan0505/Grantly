"use client";
import React from "react";
import Link from "next/link";
import {
  backendDownloadUrl,
  draftApplicationBundle,
  evaluateUploadedPitchDeck,
  generateApplicationDocument,
  generatePitchDeck,
  getApplicationRoadmap,
  getGrantApplication,
  getScoutStatus,
  runScoutAgent,
  uploadApplicationDocument,
  type ApplicationRoadmapRead,
  type CompanyProfileRead,
  type DocumentRead,
  type GrantApplicationRead,
  type GrantRead,
  type PitchDeckEvaluationRead,
  type RankedGrantRead,
  type ScoutStatusRead,
  type UserRead,
} from "@/services/grantlyApi";
import s from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

type DashboardDataProps = {
  currentUser: UserRead | null;
  rankedGrants: RankedGrantRead[];
  allGrants?: GrantRead[];
  profile: CompanyProfileRead | null;
  documents: DocumentRead[];
  loading?: boolean;
  error?: string;
};

function formatAmount(grant: GrantRead): string {
  const formatter = new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 });
  if (grant.amount_min && grant.amount_max) {
    if (grant.amount_min === grant.amount_max) return `RM ${formatter.format(grant.amount_min)}`;
    return `RM ${formatter.format(grant.amount_min)}-${formatter.format(grant.amount_max)}`;
  }
  if (grant.amount_max) return `Up to RM ${formatter.format(grant.amount_max)}`;
  if (grant.amount_min) return `From RM ${formatter.format(grant.amount_min)}`;
  return "Amount TBC";
}

function formatDeadline(deadline?: string | null): string {
  if (!deadline) return "Rolling deadline";
  const date = new Date(deadline);
  if (Number.isNaN(date.getTime())) return deadline;
  return date.toLocaleDateString("en-MY", { day: "numeric", month: "short", year: "numeric" });
}

function deadlineStatus(deadline?: string | null): string {
  if (!deadline) return "Rolling deadline";
  const date = new Date(deadline);
  if (Number.isNaN(date.getTime())) return deadline;
  const now = new Date();
  const days = Math.ceil((date.getTime() - now.getTime()) / 86400000);
  if (days < 0) return `Closed ${Math.abs(days)} days ago`;
  if (days === 0) return "Due today";
  return `Due in ${days} days`;
}

function accentForIndex(index: number): string {
  return ["#006780", "#494BD6", "#904D00", "#6D797E"][index % 4];
}

function statusLabel(match: RankedGrantRead): string {
  if (match.track === "drafter") return "READY FOR DRAFTER";
  if (match.status === "needs_documents") return "NEEDS DOCUMENTS";
  return match.status.replace(/_/g, " ").toUpperCase();
}

function formatGrantStatus(status?: string | null): string {
  return (status || "unknown").replace(/_/g, " ").toUpperCase();
}

function grantStatusTone(status?: string | null): { background: string; border: string; color: string; icon: string } {
  const normalized = (status || "unknown").toLowerCase();
  if (normalized === "open") {
    return { background: "#EAF8FC", border: "#B7EAFF", color: "#006780", icon: "check_circle" };
  }
  if (normalized === "closed") {
    return { background: "#F2F4F6", border: "#D7DEE4", color: "#5F6E84", icon: "lock" };
  }
  return { background: "#FFF4E5", border: "#FFDDB6", color: "#904D00", icon: "help" };
}

function recordFromUnknown(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function stringListFromUnknown(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function critiqueFromUnknown(value: unknown): PitchDeckEvaluationRead["critique"] | null {
  const record = recordFromUnknown(value);
  if (!record) return null;
  const overallScore = typeof record.overall_score === "number" ? record.overall_score : null;
  const reviewSummary = typeof record.review_summary === "string" ? record.review_summary : null;
  const strengths = stringListFromUnknown(record.strengths);
  const weaknesses = stringListFromUnknown(record.weaknesses);
  const actionItems = stringListFromUnknown(record.action_items_to_improve);
  if (overallScore === null && !reviewSummary && strengths.length === 0 && weaknesses.length === 0 && actionItems.length === 0) {
    return null;
  }
  return {
    overall_score: overallScore,
    review_summary: reviewSummary,
    strengths,
    weaknesses,
    action_items_to_improve: actionItems,
  };
}

function storedPitchDeckEvaluationFromDocument(document: DocumentRead): PitchDeckEvaluationRead | null {
  const metadata = recordFromUnknown(document.metadata_json);
  const storedEvaluation = recordFromUnknown(metadata?.pitch_deck_evaluation);
  const critique = critiqueFromUnknown(storedEvaluation?.critique);
  if (!critique) return null;
  return {
    critique,
    evaluated_document: document,
    message: "Pitch Deck Evaluator reviewed this deck and returned inline analytics.",
  };
}

export function HomeTab({
  currentUser,
  rankedGrants,
  profile,
  documents,
  loading,
  error,
  onApply,
}: DashboardDataProps & { onApply?: (grantId: number) => void }) {
  const [selectedGrant, setSelectedGrant] = React.useState<RankedGrantRead | null>(null);

  if (!currentUser) return <EmptyState title="No workspace session" body="Log in or register so Grantly can store your profile and rank grants against it." actionHref="/login" actionLabel="Login" />;
  if (loading) return <DashboardLoading />;

  return (
    <div style={{ overflowY: "auto", paddingBottom: 40 }}>
      {error && <InlineNotice tone="error" text={error} />}
      {!profile && (
        <InlineNotice
          tone="info"
          text="Business Fundamentals and the Document Vault are optional, but completing them improves match quality."
          actionHref="/business-fundamentals"
          actionLabel="Complete setup"
        />
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 24 }}>
        <div style={{ flex: "1 1 600px", display: "flex", flexDirection: "column", gap: 16 }}>
          <PremiumFeatureCard />
          <MetricCards rankedGrants={rankedGrants} profile={profile} documents={documents} />

          <div className={s.panel} style={{ padding: 24, borderRadius: 26, background: "rgba(242,244,246,0.78)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
              <div>
                <div style={{ fontSize: 20, fontWeight: 900, letterSpacing: -0.5, color: "#191C1E" }}>Recommended Grants Feed</div>
                <div style={{ fontSize: 13, color: "#3D494D", marginTop: 4 }}>Ranked by the backend Evaluator against your SME profile</div>
              </div>
              <button className="btn-soft"><MI name="sort" size={15} />Sort: Match %</button>
            </div>
            <div style={{ height: 20 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {rankedGrants.length === 0 ? (
                <div style={{ padding: 24, color: "#3D494D", fontSize: 14 }}>No grants are available yet. Start the backend so it can seed the sample grant database.</div>
              ) : (
                rankedGrants.map((match, index) => (
                  <FeedCard key={match.grant.id} match={match} accent={accentForIndex(index)} onViewDetails={() => setSelectedGrant(match)} />
                ))
              )}
            </div>
          </div>
        </div>

        <div style={{ flex: "1 1 300px", display: "flex", flexDirection: "column", gap: 16 }}>
          <RadarWidget profile={profile} topMatch={rankedGrants[0]} documents={documents} />
          <PitchDeckWidget documents={documents} rankedGrants={rankedGrants} />
          <TimelineWidget rankedGrants={rankedGrants} />
        </div>
      </div>

      {selectedGrant && (
        <GrantModal grant={selectedGrant} onClose={() => setSelectedGrant(null)} onApply={onApply} />
      )}
    </div>
  );
}

function PremiumFeatureCard() {
  return (
    <div
      className={s.panel}
      style={{
        padding: 24,
        borderRadius: 28,
        background: "linear-gradient(135deg, rgba(0,103,128,0.08), rgba(73,75,214,0.08))",
        border: "1px solid rgba(0,180,216,0.18)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 18, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: 16, alignItems: "flex-start", minWidth: 0 }}>
          <div style={{ width: 56, height: 56, borderRadius: 18, background: "rgba(0,180,216,0.15)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <MI name="description" size={26} color="#006780" />
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <span className={s.tag} style={{ background: "#FFF4E5", color: "#904D00" }}>Premium</span>
              <span style={{ fontSize: 12, fontWeight: 800, letterSpacing: 1.2, color: "#006780" }}>AI REIMBURSEMENT DRAFTER</span>
            </div>
            <div style={{ fontSize: 18, fontWeight: 900, letterSpacing: -0.5, color: "#191C1E", marginTop: 8 }}>Generate formal technical progress reports for grant reimbursement claims using your project updates, expenses, and evidence.</div>
            <div style={{ fontSize: 13, color: "#3D494D", lineHeight: 1.55, marginTop: 8, maxWidth: 760 }}>
              Turn rough monthly notes into a government-style reimbursement draft with claim details, evidence tracking, and a polished report editor.
            </div>
          </div>
        </div>
        <Link href="/reimbursement-drafter" className="btn-primary" style={{ textDecoration: "none", whiteSpace: "nowrap" }}>
          <MI name="auto_awesome" size={15} color="#fff" />
          Start Claim Draft
        </Link>
      </div>
    </div>
  );
}

function DashboardLoading() {
  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 32, display: "flex", alignItems: "center", gap: 14 }}>
      <MI name="sync" size={22} color="#006780" />
      <div>
        <div style={{ fontSize: 16, fontWeight: 900, color: "#191C1E" }}>Loading backend workspace</div>
        <div style={{ fontSize: 13, color: "#3D494D", marginTop: 4 }}>Fetching profile, documents, and ranked grants.</div>
      </div>
    </div>
  );
}

function EmptyState({ title, body, actionHref, actionLabel }: { title: string; body: string; actionHref: string; actionLabel: string }) {
  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 32, textAlign: "center" }}>
      <MI name="account_circle" size={36} color="#006780" />
      <div style={{ height: 12 }} />
      <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E" }}>{title}</div>
      <div style={{ fontSize: 13, color: "#3D494D", margin: "8px auto 18px", maxWidth: 460, lineHeight: 1.5 }}>{body}</div>
      <Link href={actionHref} className="btn-primary" style={{ display: "inline-flex" }}>{actionLabel}</Link>
    </div>
  );
}

function InlineNotice({ tone, text, actionHref, actionLabel }: { tone: "info" | "error"; text: string; actionHref?: string; actionLabel?: string }) {
  const isError = tone === "error";
  return (
    <div style={{ padding: 14, borderRadius: 14, marginBottom: 16, background: isError ? "#fff0f0" : "#eef9fd", border: `1px solid ${isError ? "#fca5a5" : "#b7eaff"}`, display: "flex", gap: 12, alignItems: "center", color: isError ? "#93000A" : "#064F62", fontSize: 13 }}>
      <MI name={isError ? "error" : "info"} size={18} color={isError ? "#BA1A1A" : "#006780"} />
      <span style={{ flex: 1 }}>{text}</span>
      {actionHref && actionLabel && <Link href={actionHref} style={{ fontWeight: 900, color: isError ? "#BA1A1A" : "#006780" }}>{actionLabel}</Link>}
    </div>
  );
}

function clampScore(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, value));
}

function radarPoint(axis: "top" | "right" | "bottom" | "left", score: number): string {
  const radius = 8 + clampScore(score) * 0.32;
  if (axis === "top") return `50,${50 - radius}`;
  if (axis === "right") return `${50 + radius},50`;
  if (axis === "bottom") return `50,${50 + radius}`;
  return `${50 - radius},50`;
}

function RadarWidget({ profile, topMatch, documents }: { profile: CompanyProfileRead | null; topMatch?: RankedGrantRead; documents: DocumentRead[] }) {
  const readiness = Math.round(profile?.readiness_score ?? topMatch?.readiness_score ?? 0);
  const match = Math.round(topMatch?.suitability_score ?? 0);
  const requiredTypes = new Set(topMatch?.grant.requirements.filter((requirement) => requirement.document_type).map((requirement) => requirement.document_type?.toLowerCase()));
  const uploadedTypes = new Set(documents.map((document) => document.document_type.toLowerCase()));
  const documentCoverage = requiredTypes.size
    ? Math.round(([...requiredTypes].filter((type) => type && uploadedTypes.has(type)).length / requiredTypes.size) * 100)
    : Math.min(100, documents.length * 25);
  const fitConfidence = Math.round((readiness * 0.45) + (match * 0.55));
  const points = [
    radarPoint("top", readiness),
    radarPoint("right", match),
    radarPoint("bottom", documentCoverage),
    radarPoint("left", fitConfidence),
  ].join(" ");

  return (
    <div className={s.panel} style={{ padding: 24, borderRadius: 26 }}>
      <div style={{ fontWeight: 900, fontSize: 16, color: "#191C1E" }}>SME Suitability Analysis</div>
      <div style={{ color: "#3D494D", fontSize: 12, marginTop: 4 }}>Backend readiness: {readiness}%</div>
      <div style={{ height: 20 }} />
      <div style={{ position: "relative", width: 180, height: 180, margin: "0 auto" }}>
        <svg viewBox="0 0 100 100" style={{ width: "100%", height: "100%", overflow: "visible" }}>
          <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="#E0E7EC" strokeWidth="1" />
          <polygon points="50,30 70,50 50,70 30,50" fill="none" stroke="#E0E7EC" strokeWidth="1" />
          <line x1="50" y1="10" x2="50" y2="90" stroke="#E0E7EC" strokeWidth="1" />
          <line x1="10" y1="50" x2="90" y2="50" stroke="#E0E7EC" strokeWidth="1" />
          <polygon points={points} fill="rgba(0,180,216,0.2)" stroke="#00B4D8" strokeWidth="2" />
          <text x="50" y="5" fontSize="6" textAnchor="middle" fill="#3D494D" fontWeight="700">Profile</text>
          <text x="96" y="52" fontSize="6" textAnchor="start" fill="#3D494D" fontWeight="700">Market</text>
          <text x="50" y="99" fontSize="6" textAnchor="middle" fill="#3D494D" fontWeight="700">Docs</text>
          <text x="4" y="52" fontSize="6" textAnchor="end" fill="#3D494D" fontWeight="700">Fit</text>
        </svg>
      </div>
      <div style={{ height: 16 }} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: "#006780" }}>Top Match: {match}%</span>
        <span style={{ fontSize: 11, fontWeight: 800, color: "#3D494D" }}>Docs: {documentCoverage}%</span>
        <Link href="/business-fundamentals" className="btn-soft" style={{ fontSize: 11, padding: "4px 8px" }}><MI name="tune" size={14} /> Update</Link>
      </div>
    </div>
  );
}

function PitchDeckWidget({ documents, rankedGrants }: { documents: DocumentRead[]; rankedGrants: RankedGrantRead[] }) {
  const generatedDeck = documents.find((document) => document.document_type === "pitch_deck" && document.status === "generated");
  const needsDeck = rankedGrants.some((match) => match.grant.requirements.some((requirement) => requirement.document_type === "pitch_deck"));
  const progress = generatedDeck ? 100 : needsDeck ? 35 : 0;

  return (
    <div className={s.panel} style={{ padding: 24, borderRadius: 26, background: "linear-gradient(135deg, rgba(73,75,214,0.05), rgba(0,180,216,0.05))" }}>
      <div style={{ fontWeight: 900, fontSize: 16, color: "#191C1E" }}>AI Pitch Deck Engine</div>
      <div style={{ color: "#3D494D", fontSize: 12, marginTop: 4 }}>{generatedDeck ? "Generated deck stored in backend" : "Available on grants with pitch deck requirements"}</div>
      <div style={{ height: 20 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ position: "relative", width: 56, height: 56 }}>
          <svg viewBox="0 0 36 36" style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }}>
            <circle cx="18" cy="18" r="16" fill="none" stroke="#E0E7EC" strokeWidth="3" />
            <circle cx="18" cy="18" r="16" fill="none" stroke="#494BD6" strokeWidth="3" strokeDasharray="100" strokeDashoffset={100 - progress} strokeLinecap="round" />
          </svg>
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 12, color: "#494BD6" }}>{progress}%</div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#191C1E" }}>{generatedDeck?.file_name || "No generated pitch deck yet"}</div>
          <div style={{ fontSize: 11, color: "#3D494D", marginTop: 4 }}>Open a grant application to generate and store a deck.</div>
        </div>
      </div>
    </div>
  );
}

function TimelineWidget({ rankedGrants }: { rankedGrants: RankedGrantRead[] }) {
  const grantsWithDeadlines = rankedGrants
    .filter((match) => match.grant.application_deadline)
    .slice()
    .sort((a, b) => new Date(a.grant.application_deadline || "").getTime() - new Date(b.grant.application_deadline || "").getTime())
    .slice(0, 3);

  const items = grantsWithDeadlines.length > 0 ? grantsWithDeadlines : rankedGrants.slice(0, 3);

  return (
    <div className={s.panel} style={{ padding: 24, borderRadius: 26 }}>
      <div style={{ fontWeight: 900, fontSize: 16, color: "#191C1E" }}>Upcoming Deadlines</div>
      <div style={{ height: 16 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {items.length === 0 ? (
          <div style={{ fontSize: 13, color: "#3D494D" }}>No grant deadlines loaded yet.</div>
        ) : (
          items.map((match, index) => (
            <div key={match.grant.id} style={{ display: "flex", gap: 12 }}>
              <div style={{ width: 3, background: accentForIndex(index), borderRadius: 2 }} />
              <div>
                <div style={{ fontSize: 13, fontWeight: 800, color: "#191C1E" }}>{match.grant.title}</div>
                <div style={{ fontSize: 11, color: accentForIndex(index), fontWeight: 700, marginTop: 2 }}>
                  {deadlineStatus(match.grant.application_deadline)} ({formatDeadline(match.grant.application_deadline)})
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function MetricCards({ rankedGrants, profile, documents }: { rankedGrants: RankedGrantRead[]; profile: CompanyProfileRead | null; documents: DocumentRead[] }) {
  const readiness = Math.round(profile?.readiness_score ?? rankedGrants[0]?.readiness_score ?? 0);
  const attention = rankedGrants.filter((match) => match.status !== "ready").length;
  const generated = documents.filter((document) => document.status === "generated").length;

  return (
    <div className={s.metricGrid}>
      <div className={s.metricCard}>
        <div className={s.metricHeader}><span className={s.metricTitle}>READINESS SCORE</span><MI name="speed" size={16} color="#006780" /></div>
        <div className={s.metricValue} style={{ fontSize: 34, color: "#006780" }}>{readiness}%</div>
        <div className={s.metricCaption}>{profile ? "Stored in backend profile" : "Complete setup to improve this score"}</div>
      </div>
      <div className={s.metricCard}>
        <div className={s.metricHeader}><span className={s.metricTitle}>ACTIVE PIPELINE</span><MI name="account_tree" size={16} color="#494BD6" /></div>
        <div className={s.metricValue} style={{ fontSize: 34, color: "#494BD6" }}>{rankedGrants.length}</div>
        <div className={s.metricCaption}>{attention} grants requiring attention</div>
        <div style={{ height: 10 }} />
        <div className={s.stackedProgress}>
          <div style={{ flex: Math.max(1, rankedGrants.length - attention), background: "#006780" }} />
          <div style={{ flex: Math.max(1, attention), background: "#904D00" }} />
        </div>
      </div>
      <div className={s.metricCard}>
        <div className={s.metricHeader}><span className={s.metricTitle}>DOCUMENT HEALTH</span><MI name="health_and_safety" size={16} color="#904D00" /></div>
        <div className={s.metricValue} style={{ fontSize: 26, color: "#191C1E" }}>{documents.length ? "Active" : "Empty"}</div>
        <div className={s.metricCaption}>{documents.length} stored references, {generated} generated</div>
        <div style={{ height: 10 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}><MI name={documents.length ? "check_circle" : "pending"} size={13} color="#006780" /><span style={{ color: "#3D494D", fontSize: 12 }}>{documents.length ? "Backend vault connected" : "Vault setup optional"}</span></div>
      </div>
    </div>
  );
}

function FeedCard({ match, accent, onViewDetails }: { match: RankedGrantRead; accent: string; onViewDetails: () => void }) {
  return (
    <div className={s.panel} style={{ padding: 16, borderRadius: 16, display: "flex", alignItems: "center", gap: 16, background: "#fff", boxShadow: "0 4px 12px rgba(0,0,0,0.03)" }}>
      <div style={{ width: 54, height: 54, borderRadius: "50%", background: `${accent}1f`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", flexShrink: 0 }}>
        <span style={{ fontWeight: 900, fontSize: 15, color: accent, lineHeight: 1 }}>{Math.round(match.suitability_score)}%</span>
        <span style={{ fontSize: 9, fontWeight: 800, color: accent, marginTop: 2 }}>FIT</span>
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <span className={s.tag} style={{ background: `${accent}1a`, color: accent, fontSize: 10 }}>{match.grant.provider_name}</span>
          <span style={{ fontSize: 10, fontWeight: 800, color: "#6D797E", letterSpacing: 0.5 }}>{statusLabel(match)}</span>
        </div>
        <div style={{ fontSize: 15, fontWeight: 900, color: "#191C1E", marginTop: 8 }}>{match.grant.title}</div>
        <div style={{ fontSize: 11, color: "#3D494D", marginTop: 4 }}>{formatDeadline(match.grant.application_deadline)}</div>
      </div>
      <div style={{ textAlign: "right", flexShrink: 0, maxWidth: 140 }}>
        <div style={{ fontSize: 16, fontWeight: 900, color: "#006780", wordWrap: "break-word", overflowWrap: "break-word", wordBreak: "break-word" }}>{formatAmount(match.grant)}</div>
        <button className="btn-outline-sm" onClick={onViewDetails} style={{ marginTop: 10, padding: "6px 14px", fontSize: 12 }}>View Details</button>
      </div>
    </div>
  );
}

function GrantModal({ grant, onClose, onApply }: { grant: RankedGrantRead; onClose: () => void; onApply?: (grantId: number) => void }) {
  const accent = "#006780";
  const unmet = grant.evidence_traces.filter((trace) => trace.status !== "MET");

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(15, 23, 42, 0.4)", backdropFilter: "blur(4px)" }}>
      <div className={s.panel} style={{ width: 800, maxWidth: "90vw", maxHeight: "85vh", display: "flex", flexDirection: "column", overflow: "hidden", background: "#fff", borderRadius: 24, boxShadow: "0 24px 48px rgba(0,0,0,0.2)", padding: 0 }}>
        <div style={{ padding: 24, borderBottom: "1px solid #E0E7EC", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <span className={s.tag} style={{ background: `${accent}1a`, color: accent, fontSize: 12 }}>{grant.grant.provider_name}</span>
            <h2 style={{ fontSize: 20, fontWeight: 900, color: "#191C1E", margin: 0 }}>{grant.grant.title}</h2>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", cursor: "pointer", padding: 0, display: "flex" }}><MI name="close" size={24} color="#6D797E" /></button>
        </div>

        <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
          <div style={{ flex: 6, padding: 24, overflowY: "auto", borderRight: "1px solid #E0E7EC" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 24, gap: 20 }}>
              <div>
                <div style={{ fontSize: 12, color: "#6D797E", fontWeight: 700, marginBottom: 4 }}>GRANT AMOUNT</div>
                <div style={{ fontSize: 24, fontWeight: 900, color: accent, wordWrap: "break-word", overflowWrap: "break-word", wordBreak: "break-word" }}>{formatAmount(grant.grant)}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 12, color: "#6D797E", fontWeight: 700, marginBottom: 4 }}>DEADLINE</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: "#191C1E" }}>{formatDeadline(grant.grant.application_deadline)}</div>
              </div>
            </div>

            <div style={{ fontSize: 14, fontWeight: 800, color: "#191C1E", marginBottom: 8 }}>Description</div>
            <p style={{ fontSize: 14, color: "#3D494D", lineHeight: 1.6, marginBottom: 24 }}>
              {grant.grant.description || grant.grant.eligibility_notes || "No description provided by this grant source."}
            </p>

            <div style={{ fontSize: 14, fontWeight: 800, color: "#191C1E", marginBottom: 8 }}>Application Requirements</div>
            <ul style={{ fontSize: 14, color: "#3D494D", lineHeight: 1.6, paddingLeft: 20, margin: 0 }}>
              {grant.grant.requirements.length === 0 ? (
                <li>No explicit requirements captured yet.</li>
              ) : grant.grant.requirements.map((requirement) => (
                <li key={requirement.id} style={{ marginBottom: 8 }}>
                  {requirement.name} ({requirement.source_type === "generated" ? "AI can generate" : "upload required"})
                </li>
              ))}
            </ul>

            {grant.grant.source_url && (
              <div style={{ marginTop: 24 }}>
                <a href={grant.grant.source_url} target="_blank" rel="noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 14, fontWeight: 700, color: "#006780", textDecoration: "none" }}>
                  <MI name="launch" size={16} /> Official Grant Website
                </a>
              </div>
            )}
          </div>

          <div style={{ flex: 4, padding: 24, background: "#F8FAFC", overflowY: "auto" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
              <MI name="auto_awesome" size={20} color="#0087A5" />
              <span style={{ fontSize: 16, fontWeight: 900, color: "#0F172A" }}>Evaluator Analysis</span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
              <div style={{ width: 60, height: 60, borderRadius: "50%", background: `${accent}1f`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", flexShrink: 0 }}>
                <span style={{ fontWeight: 900, fontSize: 18, color: accent, lineHeight: 1 }}>{Math.round(grant.suitability_score)}%</span>
                <span style={{ fontSize: 9, fontWeight: 800, color: accent, marginTop: 2 }}>MATCH</span>
              </div>
              <div style={{ fontSize: 13, color: "#334155", lineHeight: 1.5 }}>
                Readiness: <strong>{grant.readiness_level}</strong>. Track: <strong>{grant.track}</strong>.
              </div>
            </div>

            <div style={{ fontSize: 12, fontWeight: 800, color: "#6D797E", letterSpacing: 1, marginBottom: 12 }}>WHY THIS RANKED HERE</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {grant.reasons.slice(0, 3).map((reason, index) => (
                <div key={index} style={{ background: "#fff", padding: 12, borderRadius: 8, display: "flex", gap: 10, boxShadow: "0 2px 4px rgba(0,0,0,0.02)", border: "1px solid #E0E7EC" }}>
                  <div style={{ flexShrink: 0 }}><MI name="check_circle" size={18} color="#10B981" /></div>
                  <span style={{ fontSize: 13, color: "#191C1E", lineHeight: 1.4 }}>{reason}</span>
                </div>
              ))}
              {unmet.slice(0, 3).map((trace, index) => (
                <div key={trace.requirement + index} style={{ background: "#fff", padding: 12, borderRadius: 8, display: "flex", gap: 10, boxShadow: "0 2px 4px rgba(0,0,0,0.02)", border: "1px solid #FCA5A5" }}>
                  <div style={{ flexShrink: 0 }}><MI name="warning" size={18} color="#F59E0B" /></div>
                  <span style={{ fontSize: 13, color: "#191C1E", lineHeight: 1.4 }}>{trace.reasoning}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div style={{ padding: 20, borderTop: "1px solid #E0E7EC", background: "#F8FAFC", display: "flex", justifyContent: "flex-end", gap: 12 }}>
          <button className="btn-outline-sm" onClick={onClose}>Close</button>
          <button className="btn-primary" onClick={() => {
            onApply?.(grant.grant.id);
            onClose();
          }}>
            <MI name="rocket_launch" size={16} /> Open Application
          </button>
        </div>
      </div>
    </div>
  );
}

export function GrantTab({
  currentUser,
  rankedGrants,
  allGrants = [],
  documents,
  focusGrantId,
  onRefresh,
}: DashboardDataProps & { focusGrantId?: number | null; onRefresh?: () => void }) {
  const grantLibrary = allGrants.length > 0 ? allGrants : rankedGrants.map((match) => match.grant);
  const [selectedGrantId, setSelectedGrantId] = React.useState<number | null>(focusGrantId || rankedGrants[0]?.grant.id || grantLibrary[0]?.id || null);
  const [snapshot, setSnapshot] = React.useState<GrantApplicationRead | null>(null);
  const [roadmap, setRoadmap] = React.useState<ApplicationRoadmapRead | null>(null);
  const [loadingSnapshot, setLoadingSnapshot] = React.useState(false);
  const [loadingRoadmap, setLoadingRoadmap] = React.useState(false);
  const [actionStatus, setActionStatus] = React.useState("");
  const [error, setError] = React.useState("");
  const [scoutStatus, setScoutStatus] = React.useState<ScoutStatusRead | null>(null);
  const [scoutRunning, setScoutRunning] = React.useState(false);
  const [uploadingRequirementId, setUploadingRequirementId] = React.useState<number | null>(null);
  const [uploadingPitchDeck, setUploadingPitchDeck] = React.useState(false);
  const [evaluatingPitchDeck, setEvaluatingPitchDeck] = React.useState(false);
  const [pitchDeckEvaluation, setPitchDeckEvaluation] = React.useState<PitchDeckEvaluationRead | null>(null);
  const [checklistCollapsed, setChecklistCollapsed] = React.useState(false);
  const [roadmapCollapsed, setRoadmapCollapsed] = React.useState(false);
  const pitchDeckUploadRef = React.useRef<HTMLInputElement | null>(null);

  const effectiveGrantId = selectedGrantId ?? focusGrantId ?? rankedGrants[0]?.grant.id ?? grantLibrary[0]?.id ?? null;

  React.useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(() => {
      if (!currentUser || !effectiveGrantId) {
        setSnapshot(null);
        setRoadmap(null);
        return;
      }
      setLoadingSnapshot(true);
      setError("");
      getGrantApplication(effectiveGrantId, currentUser.id)
        .then((result) => {
          if (!cancelled) {
            setSnapshot(result);
            setPitchDeckEvaluation(null);
          }
        })
        .catch((err: unknown) => {
          if (!cancelled) setError(err instanceof Error ? err.message : "Unable to load application checklist.");
        })
        .finally(() => {
          if (!cancelled) setLoadingSnapshot(false);
        });
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [currentUser, effectiveGrantId]);

  React.useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(() => {
      if (!currentUser || !effectiveGrantId) {
        setRoadmap(null);
        return;
      }
      setLoadingRoadmap(true);
      getApplicationRoadmap(effectiveGrantId, currentUser.id)
        .then((result) => {
          if (!cancelled) setRoadmap(result);
        })
        .catch((err: unknown) => {
          if (!cancelled) {
            setRoadmap(null);
            setError(err instanceof Error ? err.message : "Unable to load Coach Agent roadmap.");
          }
        })
        .finally(() => {
          if (!cancelled) setLoadingRoadmap(false);
        });
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [currentUser, effectiveGrantId]);

  const selectedMatch = rankedGrants.find((match) => match.grant.id === effectiveGrantId) || null;
  const selectedGrant = selectedMatch?.grant || grantLibrary.find((grant) => grant.id === effectiveGrantId) || rankedGrants[0]?.grant || grantLibrary[0] || null;

  const refreshSnapshot = async () => {
    if (!currentUser || !effectiveGrantId) return;
    const next = await getGrantApplication(effectiveGrantId, currentUser.id);
    setSnapshot(next);
    setLoadingRoadmap(true);
    void getApplicationRoadmap(effectiveGrantId, currentUser.id)
      .then(setRoadmap)
      .catch(() => setRoadmap(null))
      .finally(() => setLoadingRoadmap(false));
    onRefresh?.();
  };

  const handleGenerate = async (item: GrantApplicationRead["checklist"][number]) => {
    if (!currentUser || !effectiveGrantId) return;
    setActionStatus(`Generating ${item.name}...`);
    setError("");
    try {
      if (item.document_type === "pitch_deck") {
        await generatePitchDeck({ grantId: effectiveGrantId, userId: currentUser.id, creative: false });
      } else {
        await generateApplicationDocument({
          grantId: effectiveGrantId,
          userId: currentUser.id,
          requirementId: item.requirement_id,
          documentType: item.document_type,
          documentName: item.name,
        });
      }
      setActionStatus(`${item.name} generated and stored.`);
      await refreshSnapshot();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to generate document.");
      setActionStatus("");
    }
  };

  const handleRunDrafterBundle = async () => {
    if (!currentUser || !effectiveGrantId) return;
    setActionStatus("Running Drafter Agent...");
    setError("");
    try {
      const result = await draftApplicationBundle({ grantId: effectiveGrantId, userId: currentUser.id });
      const pptx = result.generated_documents.find((document) => document.file_name.toLowerCase().endsWith(".pptx"));
      const proposal = result.generated_documents.find((document) => document.file_name.toLowerCase().endsWith(".pdf"));
      setActionStatus(
        `Drafter Agent generated a professional proposal${proposal ? " PDF" : ""}, ${pptx ? "downloadable PPTX pitch deck" : "pitch deck"}, and companion script. Download them below.`,
      );
      await refreshSnapshot();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to run Drafter Agent.");
      setActionStatus("");
    }
  };

  const handleUploadDocument = async (item: GrantApplicationRead["checklist"][number], file: File) => {
    if (!currentUser || !effectiveGrantId) return;
    setUploadingRequirementId(item.requirement_id);
    setActionStatus(`Uploading ${file.name}...`);
    setError("");
    try {
      await uploadApplicationDocument({
        grantId: effectiveGrantId,
        userId: currentUser.id,
        file,
        documentType: item.document_type,
        documentName: item.name,
        requirementId: item.requirement_id,
      });
      setActionStatus(`${file.name} uploaded and linked to ${item.name}.`);
      await refreshSnapshot();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to upload document.");
      setActionStatus("");
    } finally {
      setUploadingRequirementId(null);
    }
  };

  const pitchDeckChecklistItem = snapshot?.checklist.find((item) => item.document_type === "pitch_deck");

  const handleUploadPitchDeck = async (file: File) => {
    if (!currentUser || !effectiveGrantId) return;
    setUploadingPitchDeck(true);
    setActionStatus(`Uploading ${file.name} for pitch deck review...`);
    setError("");
    setPitchDeckEvaluation(null);
    try {
      await uploadApplicationDocument({
        grantId: effectiveGrantId,
        userId: currentUser.id,
        file,
        documentType: "pitch_deck",
        documentName: "Uploaded Pitch Deck",
        requirementId: pitchDeckChecklistItem?.requirement_id,
      });
      setActionStatus(`${file.name} uploaded. Pitch Deck Evaluator can review it now.`);
      await refreshSnapshot();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to upload pitch deck.");
      setActionStatus("");
    } finally {
      setUploadingPitchDeck(false);
    }
  };

  const handleEvaluatePitchDeck = async (documentId?: number) => {
    if (!currentUser || !effectiveGrantId) return;
    setEvaluatingPitchDeck(true);
    setActionStatus("Pitch Deck Evaluator is reviewing the uploaded deck...");
    setError("");
    try {
      const result = await evaluateUploadedPitchDeck({
        grantId: effectiveGrantId,
        userId: currentUser.id,
        documentId,
      });
      setPitchDeckEvaluation(result);
      setActionStatus(result.message);
      await refreshSnapshot();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to evaluate the uploaded pitch deck.");
      setActionStatus("");
    } finally {
      setEvaluatingPitchDeck(false);
    }
  };

  const handleRunScoutAgent = async () => {
    setScoutRunning(true);
    setActionStatus("Running Scout Agent on curated grant files...");
    setError("");
    try {
      const report = await runScoutAgent();
      const grantsExtracted = typeof report.grants_extracted === "number" ? report.grants_extracted : "new";
      setActionStatus(`Scout Agent synced ${grantsExtracted} grant record(s) into the database.`);
      setScoutStatus(await getScoutStatus());
      await onRefresh?.();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to run Scout Agent.");
      setActionStatus("");
    } finally {
      setScoutRunning(false);
    }
  };

  if (!currentUser) return <EmptyState title="No workspace session" body="Log in before opening an application checklist." actionHref="/login" actionLabel="Login" />;

  return (
    <div style={{ overflowY: "auto" }}>
      <div className={s.pageHeader}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}><MI name="analytics" size={18} color="#904D00" />
          <div className={s.pageTitle} style={{ fontSize: 28 }}>Grant Match Details</div>
        </div>
        <div className={s.pageSub}>Live backend grant rankings, application checklist, generated documents, and submission package links.</div>
      </div>
      <div style={{ height: 16 }} />

      {error && <InlineNotice tone="error" text={error} />}
      {actionStatus && <InlineNotice tone="info" text={actionStatus} />}

      <div className={s.grantLayout}>
        <div className={s.grantMain}>
          {selectedGrant ? (
            <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
              <div style={{ display: "flex", gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                    <span className={s.tag} style={{ background: "#F2F4F6", color: "#3D494D" }}>{selectedGrant.provider_name}</span>
                    {selectedMatch ? (
                      <span className={s.tag} style={{ background: "#EDEBFF", color: "#494BD6" }}><MI name="auto_awesome" size={12} color="#494BD6" />{selectedMatch.readiness_level}</span>
                    ) : (
                      <span className={s.tag} style={{ background: grantStatusTone(selectedGrant.status).background, color: grantStatusTone(selectedGrant.status).color }}><MI name={grantStatusTone(selectedGrant.status).icon} size={12} color={grantStatusTone(selectedGrant.status).color} />{formatGrantStatus(selectedGrant.status)}</span>
                    )}
                  </div>
                  <div style={{ height: 12 }} />
                  <div style={{ fontSize: 20, fontWeight: 900, lineHeight: 1.12, letterSpacing: -0.5, color: "#191C1E" }}>{selectedGrant.title}</div>
                  <div style={{ height: 8 }} />
                  <div style={{ color: "#3D494D", fontSize: 13 }}>Deadline: {formatDeadline(selectedGrant.application_deadline)}</div>
                </div>
                {selectedMatch ? (
                  <div style={{ width: 76, height: 76, borderRadius: "50%", background: "#FFDDB6", border: "1px solid rgba(144,77,0,0.14)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <div style={{ fontSize: 24, fontWeight: 900, color: "#904D00", letterSpacing: -1 }}>{Math.round(selectedMatch.suitability_score)}%</div>
                    <div style={{ fontSize: 9, fontWeight: 800, color: "#904D00", letterSpacing: 2 }}>MATCH</div>
                  </div>
                ) : (
                  <div style={{ width: 76, height: 76, borderRadius: "50%", background: "#F2F4F6", border: "1px solid rgba(224,231,236,0.9)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <MI name="inventory_2" size={24} color="#5F6E84" />
                    <div style={{ fontSize: 9, fontWeight: 800, color: "#5F6E84", letterSpacing: 1 }}>LIBRARY</div>
                  </div>
                )}
              </div>
              <div style={{ height: 20 }} />
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 18 }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}><MI name="verified" size={14} color="#904D00" /><span style={{ fontWeight: 900, letterSpacing: 1, fontSize: 12, color: "#191C1E" }}>WHY YOU ARE A FIT</span></div>
                  <div style={{ height: 10 }} />
                  {selectedMatch ? (
                    selectedMatch.reasons.slice(0, 3).map((reason, index) => (
                      <div key={index} className={s.evidenceTile}><div className={s.evidenceIcon} style={{ background: "rgba(0,103,128,0.12)" }}><MI name="check_circle" size={14} color="#006780" /></div><div><div style={{ fontWeight: 700, color: "#191C1E", fontSize: 13 }}>{reason}</div></div></div>
                    ))
                  ) : (
                    <div className={s.evidenceTile}><div className={s.evidenceIcon} style={{ background: "rgba(95,110,132,0.12)" }}><MI name="inventory_2" size={14} color="#5F6E84" /></div><div><div style={{ fontWeight: 700, color: "#191C1E", fontSize: 13 }}>This grant is from the complete library. Update the company profile to include it in ranked matching if it is eligible.</div></div></div>
                  )}
                </div>
                <div>
                  <div className={s.gapPanel}><MI name="assignment" size={14} color="#BA1A1A" /><div><div style={{ color: "#BA1A1A", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>APPLICATION CHECKLIST</div><div style={{ height: 8 }} /><div style={{ color: "#93000A", lineHeight: 1.4, fontSize: 13 }}>{snapshot ? `${snapshot.missing_required_documents.length} missing required item(s). Track: ${snapshot.track}.` : loadingSnapshot ? "Loading checklist..." : "Select a grant to load its checklist."}</div></div></div>
                  <div style={{ height: 28 }} />
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            <button className="btn-primary" onClick={handleRunDrafterBundle} disabled={!snapshot || loadingSnapshot} style={{ opacity: !snapshot || loadingSnapshot ? 0.65 : 1 }}>
              <MI name="auto_awesome" size={16} color="#fff" />Run Drafter Agent
            </button>
            {snapshot?.download_package_url && (
              <a href={backendDownloadUrl(snapshot.download_package_url)} className="btn-amber" style={{ textDecoration: "none" }}>
                <MI name="archive" size={16} color="#fff" />Download Package
              </a>
            )}
          </div>
                </div>
              </div>
            </div>
          ) : (
            <EmptyState title="No grants available" body="Start the backend to seed grant data, then refresh this dashboard." actionHref="/dashboard" actionLabel="Refresh" />
          )}

          <div style={{ height: 12 }} />
          <ApplicationChecklist
            snapshot={snapshot}
            loading={loadingSnapshot}
            uploadingRequirementId={uploadingRequirementId}
            collapsed={checklistCollapsed}
            onToggleCollapse={() => setChecklistCollapsed((value) => !value)}
            onGenerate={handleGenerate}
            onUpload={handleUploadDocument}
          />
          <div style={{ height: 24 }} />
          <ApplicationRoadmap
            roadmap={roadmap}
            loading={loadingRoadmap}
            collapsed={roadmapCollapsed}
            onToggleCollapse={() => setRoadmapCollapsed((value) => !value)}
          />
          <div style={{ height: 16 }} />
          <PitchDeckEvaluationPanel
            snapshot={snapshot}
            documents={documents}
            evaluation={pitchDeckEvaluation}
            uploading={uploadingPitchDeck}
            evaluating={evaluatingPitchDeck}
            uploadInputRef={pitchDeckUploadRef}
            onUpload={handleUploadPitchDeck}
            onEvaluate={handleEvaluatePitchDeck}
          />
          <div style={{ height: 16 }} />
          <GeneratedOutputs snapshot={snapshot} currentUser={currentUser} grantId={effectiveGrantId} />
          <div style={{ height: 16 }} />
          <GrantLibrary
            grants={grantLibrary}
            rankedGrants={rankedGrants}
            selectedGrantId={selectedGrant?.id ?? effectiveGrantId}
            scoutStatus={scoutStatus}
            scoutRunning={scoutRunning}
            onRunScout={handleRunScoutAgent}
            onOpen={(grantId) => setSelectedGrantId(grantId)}
          />
        </div>

        <div className={s.grantSide}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 14 }}><span style={{ fontWeight: 900, letterSpacing: 2, fontSize: 12, color: "#191C1E" }}>RANKED PROFILE MATCHES</span><span style={{ color: "#904D00", fontWeight: 700, fontSize: 12 }}>{rankedGrants.length} total</span></div>
          {rankedGrants.length === 0 ? (
            <div className={s.matchCard} style={{ color: "#3D494D", fontSize: 13, lineHeight: 1.45 }}>No ranked matches yet. Complete or refresh the company profile to score grants against your SME readiness.</div>
          ) : (
            rankedGrants.map((match) => (
              <MatchCard key={match.grant.id} match={match} selected={effectiveGrantId === match.grant.id} onApply={() => setSelectedGrantId(match.grant.id)} />
            ))
          )}
          <Link href="/business-fundamentals" className={s.connectCard} style={{ display: "block", textDecoration: "none" }}>
            <div style={{ width: 30, height: 30, borderRadius: "50%", background: "#F2F4F6", display: "inline-flex", alignItems: "center", justifyContent: "center" }}><MI name="add_link" size={15} color="#3D494D" /></div>
            <div style={{ height: 10 }} />
            <div style={{ fontWeight: 900, fontSize: 13, color: "#191C1E" }}>Update Profile Inputs</div>
            <div style={{ height: 4 }} />
            <div style={{ color: "#3D494D", fontSize: 12 }}>Improve evaluation context</div>
          </Link>
        </div>
      </div>
    </div>
  );
}

function GrantLibrary({
  grants,
  rankedGrants,
  selectedGrantId,
  scoutStatus,
  scoutRunning,
  onRunScout,
  onOpen,
}: {
  grants: GrantRead[];
  rankedGrants: RankedGrantRead[];
  selectedGrantId?: number | null;
  scoutStatus: ScoutStatusRead | null;
  scoutRunning: boolean;
  onRunScout: () => void;
  onOpen: (grantId: number) => void;
}) {
  const pageSize = 10;
  const [page, setPage] = React.useState(0);
  const openCount = grants.filter((grant) => grant.status.toLowerCase() === "open").length;
  const closedCount = grants.filter((grant) => grant.status.toLowerCase() === "closed").length;
  const otherCount = Math.max(0, grants.length - openCount - closedCount);
  const rankedLookup = new Map<number, { match: RankedGrantRead; rank: number }>(
    rankedGrants.map((match, index): [number, { match: RankedGrantRead; rank: number }] => [match.grant.id, { match, rank: index + 1 }]),
  );
  const sortedGrants = grants
    .slice()
    .sort((a, b) => {
      const aRank = rankedLookup.get(a.id)?.rank ?? Number.POSITIVE_INFINITY;
      const bRank = rankedLookup.get(b.id)?.rank ?? Number.POSITIVE_INFINITY;
      if (aRank !== bRank) return aRank - bRank;
      return a.title.localeCompare(b.title);
    });
  const pageCount = Math.max(1, Math.ceil(sortedGrants.length / pageSize));
  const safePage = Math.min(page, pageCount - 1);
  const pageStart = safePage * pageSize;
  const visibleGrants = sortedGrants.slice(pageStart, pageStart + pageSize);

  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <MI name="inventory_2" size={17} color="#006780" />
            <div style={{ fontWeight: 900, letterSpacing: 1, fontSize: 13, color: "#191C1E" }}>COMPLETE GRANT LIBRARY</div>
          </div>
          <div style={{ color: "#3D494D", fontSize: 12, marginTop: 5 }}>
            Scout Agent syncs curated grant files into the database; Evaluator turns each grant&apos;s requirements into a checklist.
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <span className={s.tag} style={{ background: "#F2F4F6", color: "#191C1E" }}>{grants.length} total</span>
          <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>{openCount} open</span>
          <span className={s.tag} style={{ background: "#F2F4F6", color: "#5F6E84" }}>{closedCount} closed</span>
          {otherCount > 0 && <span className={s.tag} style={{ background: "#FFF4E5", color: "#904D00" }}>{otherCount} unknown</span>}
          <button className="btn-primary" onClick={onRunScout} disabled={scoutRunning} style={{ fontSize: 12, opacity: scoutRunning ? 0.7 : 1 }}>
            <MI name="travel_explore" size={14} color="#fff" />{scoutRunning ? "Syncing" : "Run Scout"}
          </button>
        </div>
      </div>
      {scoutStatus?.message && (
        <div style={{ marginTop: 12, color: "#3D494D", fontSize: 12 }}>
          Scout status: <strong>{scoutStatus.status}</strong> - {scoutStatus.message}
        </div>
      )}

      <div style={{ height: 16 }} />
      {grants.length === 0 ? (
        <div style={{ color: "#3D494D", fontSize: 13 }}>No grants are stored yet. Run the Scout Agent or seed the backend database to fill the library.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {visibleGrants.map((grant) => {
            const tone = grantStatusTone(grant.status);
            const ranked = rankedLookup.get(grant.id);
            const selected = selectedGrantId === grant.id;
            return (
              <div key={grant.id} style={{ padding: 14, border: `1px solid ${selected ? "#00B4D8" : "#E0E7EC"}`, borderRadius: 14, background: selected ? "#F2FBFE" : "#fff", display: "grid", gridTemplateColumns: "minmax(0, 1fr) auto", gap: 14, alignItems: "center" }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    <span className={s.tag} style={{ background: "#F2F4F6", color: "#3D494D" }}>{grant.provider_name}</span>
                    <span className={s.tag} style={{ background: tone.background, color: tone.color, border: `1px solid ${tone.border}` }}><MI name={tone.icon} size={12} color={tone.color} />{formatGrantStatus(grant.status)}</span>
                    {ranked && <span className={s.tag} style={{ background: "#FFF4E5", color: "#904D00" }}>Rank #{ranked.rank} - {Math.round(ranked.match.suitability_score)}%</span>}
                  </div>
                  <div style={{ height: 8 }} />
                  <div style={{ fontSize: 15, fontWeight: 900, color: "#191C1E", lineHeight: 1.25, overflowWrap: "anywhere" }}>{grant.title}</div>
                  <div style={{ color: "#3D494D", fontSize: 12, lineHeight: 1.45, marginTop: 6 }}>
                    {grant.description || grant.eligibility_notes || "No description captured yet."}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 10, color: "#5F6E84", fontSize: 12, fontWeight: 700 }}>
                    <span>{formatAmount(grant)}</span>
                    <span>{formatDeadline(grant.application_deadline)}</span>
                    {grant.industry && <span>{grant.industry}</span>}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", justifyContent: "flex-end", flexWrap: "wrap" }}>
                  {grant.source_url && (
                    <a href={grant.source_url} target="_blank" rel="noreferrer" className="btn-soft" style={{ fontSize: 12, textDecoration: "none" }}><MI name="launch" size={14} />Source</a>
                  )}
                  <button className={selected ? "btn-primary" : "btn-outline-sm"} onClick={() => onOpen(grant.id)} style={{ fontSize: 12 }}>
                    <MI name={selected ? "check" : "open_in_new"} size={14} color={selected ? "#fff" : undefined} />Open
                  </button>
                </div>
              </div>
            );
          })}
          {pageCount > 1 && (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, flexWrap: "wrap", marginTop: 6 }}>
              <div style={{ color: "#5F6E84", fontSize: 12 }}>
                Showing {pageStart + 1}-{Math.min(pageStart + pageSize, sortedGrants.length)} of {sortedGrants.length}
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <button className="btn-soft" disabled={safePage === 0} onClick={() => setPage((value) => Math.max(0, value - 1))} style={{ fontSize: 12, opacity: safePage === 0 ? 0.5 : 1 }}>
                  <MI name="chevron_left" size={14} />Prev
                </button>
                <span style={{ color: "#191C1E", fontSize: 12, fontWeight: 800 }}>
                  Page {safePage + 1} / {pageCount}
                </span>
                <button className="btn-soft" disabled={safePage >= pageCount - 1} onClick={() => setPage((value) => Math.min(pageCount - 1, value + 1))} style={{ fontSize: 12, opacity: safePage >= pageCount - 1 ? 0.5 : 1 }}>
                  Next<MI name="chevron_right" size={14} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function roadmapTone(status: string): { color: string; background: string; icon: string; label: string } {
  const normalized = status.toLowerCase();
  if (normalized === "complete") return { color: "#059669", background: "#ECFDF5", icon: "check_circle", label: "Complete" };
  if (normalized === "ready" || normalized === "ready_to_generate") return { color: "#494BD6", background: "#EDEBFF", icon: "auto_awesome", label: normalized === "ready" ? "Ready" : "Generate" };
  if (normalized === "needs_upload") return { color: "#904D00", background: "#FFF4E5", icon: "upload_file", label: "Upload" };
  if (normalized === "blocked") return { color: "#BA1A1A", background: "#FFF0F0", icon: "lock", label: "Blocked" };
  return { color: "#5F6E84", background: "#F2F4F6", icon: "schedule", label: "Pending" };
}

function ApplicationRoadmap({
  roadmap,
  loading,
  collapsed,
  onToggleCollapse,
}: {
  roadmap: ApplicationRoadmapRead | null;
  loading: boolean;
  collapsed: boolean;
  onToggleCollapse: () => void;
}) {
  if (loading) {
    return (
      <div className={s.panel} style={{ borderRadius: 26, padding: 18, color: "#3D494D", fontSize: 13 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <MI name="route" size={17} color="#006780" />
            <strong style={{ color: "#191C1E" }}>Coach Agent Application Roadmap</strong>
          </div>
          <button type="button" className="btn-soft" onClick={onToggleCollapse} style={{ fontSize: 11, padding: "4px 8px" }}>
            <MI name="unfold_less" size={14} />Collapse
          </button>
        </div>
        {!collapsed && <div style={{ marginTop: 10 }}>Generating a grant application pipeline...</div>}
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className={s.panel} style={{ borderRadius: 26, padding: 18, color: "#3D494D", fontSize: 13 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <MI name="route" size={17} color="#006780" />
            <strong style={{ color: "#191C1E" }}>Coach Agent Application Roadmap</strong>
          </div>
          <button type="button" className="btn-soft" onClick={onToggleCollapse} style={{ fontSize: 11, padding: "4px 8px" }}>
            <MI name="unfold_less" size={14} />Collapse
          </button>
        </div>
        {!collapsed && <div style={{ marginTop: 10 }}>Coach Agent roadmap will appear after the grant application checklist loads.</div>}
      </div>
    );
  }

  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <MI name="route" size={17} color="#006780" />
            <div style={{ fontWeight: 900, letterSpacing: 1, fontSize: 13, color: "#191C1E" }}>COACH AGENT APPLICATION ROADMAP</div>
          </div>
          <div style={{ color: "#3D494D", fontSize: 12, marginTop: 5 }}>
            {roadmap.encouraging_message}
          </div>
        </div>
        <span className={s.tag} style={{ background: "#EAF8FC", color: "#006780" }}>
          {roadmap.generated_by === "gemini_coach_agent" ? "Coach" : "Coach fallback"}
        </span>
      </div>
      <div style={{ height: 12 }} />
      <button type="button" className="btn-soft" onClick={onToggleCollapse} style={{ fontSize: 12, padding: "6px 10px" }}>
        <MI name={collapsed ? "unfold_more" : "unfold_less"} size={14} />
        {collapsed ? "Expand roadmap" : "Collapse roadmap"}
      </button>
      {!collapsed && (
        <>
          <div style={{ height: 16 }} />
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {roadmap.steps.map((step, index) => {
              const tone = roadmapTone(step.status);
              const isLast = index === roadmap.steps.length - 1;
              return (
                <div key={`${step.step_number}-${step.title}`} style={{ display: "grid", gridTemplateColumns: "34px minmax(0, 1fr)", gap: 12 }}>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <div style={{ width: 30, height: 30, borderRadius: "50%", background: tone.background, color: tone.color, display: "flex", alignItems: "center", justifyContent: "center", border: `1px solid ${tone.color}30` }}>
                      <MI name={tone.icon} size={16} color={tone.color} />
                    </div>
                    {!isLast && <div style={{ width: 2, flex: 1, minHeight: 42, background: "#E0E7EC", marginTop: 6 }} />}
                  </div>
                  <div style={{ border: "1px solid #E0E7EC", borderRadius: 14, padding: 12, background: "#fff" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "flex-start", flexWrap: "wrap" }}>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 900, color: "#191C1E", lineHeight: 1.3 }}>
                          {step.step_number}. {step.title}
                        </div>
                        <div style={{ color: "#5F6E84", fontSize: 11, marginTop: 3 }}>Owner: {step.owner}</div>
                      </div>
                      <span className={s.tag} style={{ background: tone.background, color: tone.color }}>{tone.label}</span>
                    </div>
                    <div style={{ color: "#3D494D", fontSize: 12, lineHeight: 1.45, marginTop: 8 }}>{step.description}</div>
                    <div style={{ color: "#191C1E", fontSize: 12, lineHeight: 1.45, marginTop: 8, fontWeight: 700 }}>{step.action}</div>
                    {step.download_url && (
                      <a href={backendDownloadUrl(step.download_url)} className="btn-soft" style={{ textDecoration: "none", fontSize: 12, marginTop: 10, display: "inline-flex" }}>
                        <MI name="download" size={14} />Download
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function PitchDeckEvaluationPanel({
  snapshot,
  documents,
  evaluation,
  uploading,
  evaluating,
  uploadInputRef,
  onUpload,
  onEvaluate,
}: {
  snapshot: GrantApplicationRead | null;
  documents: DocumentRead[];
  evaluation: PitchDeckEvaluationRead | null;
  uploading: boolean;
  evaluating: boolean;
  uploadInputRef: React.RefObject<HTMLInputElement | null>;
  onUpload: (file: File) => void;
  onEvaluate: (documentId?: number) => void;
}) {
  const documentLookup = new Map<number, DocumentRead>();
  for (const document of [...documents, ...(snapshot?.attached_documents || [])]) {
    documentLookup.set(document.id, document);
  }
  const uploadedDecks = [...documentLookup.values()]
    .filter((document) => document.document_type === "pitch_deck" && document.status !== "generated")
    .slice()
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  const uploadedDeck = uploadedDecks[0] || null;
  const activeEvaluation = evaluation || (uploadedDeck ? storedPitchDeckEvaluationFromDocument(uploadedDeck) : null);
  const critique = activeEvaluation?.critique || null;
  const evaluatedDeck = activeEvaluation?.evaluated_document || uploadedDeck;
  const reviewScore = typeof critique?.overall_score === "number" ? Math.max(0, Math.min(100, critique.overall_score)) : null;

  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <MI name="fact_check" size={17} color="#494BD6" />
            <div style={{ fontWeight: 900, letterSpacing: 1, fontSize: 13, color: "#191C1E" }}>PITCH DECK EVALUATOR</div>
          </div>
          <div style={{ color: "#3D494D", fontSize: 12, marginTop: 5 }}>
            Upload your own deck and get constructive grant-readiness feedback.
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <input
            ref={uploadInputRef}
            type="file"
            accept=".pptx,.pdf,.txt,.md,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/pdf,text/plain,text/markdown"
            style={{ display: "none" }}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(file);
              event.currentTarget.value = "";
            }}
          />
          <button type="button" className="btn-soft" disabled={uploading} onClick={() => uploadInputRef.current?.click()} style={{ fontSize: 12 }}>
            <MI name="upload_file" size={14} />{uploading ? "Uploading" : "Upload Deck"}
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={!uploadedDeck || evaluating}
            onClick={() => uploadedDeck && onEvaluate(uploadedDeck.id)}
            style={{ fontSize: 12, opacity: !uploadedDeck || evaluating ? 0.65 : 1 }}
          >
            <MI name="rate_review" size={14} color="#fff" />{evaluating ? "Reviewing" : "Evaluate Deck"}
          </button>
        </div>
      </div>

      <div style={{ height: 14 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        <div style={{ border: "1px solid #E0E7EC", borderRadius: 14, padding: 12, background: "#fff" }}>
          <div style={{ color: "#5F6E84", fontSize: 11, fontWeight: 900, letterSpacing: 1 }}>UPLOADED DECK</div>
          <div style={{ color: "#191C1E", fontSize: 13, fontWeight: 800, marginTop: 6, overflowWrap: "anywhere" }}>
            {uploadedDeck?.file_name || "No uploaded pitch deck yet"}
          </div>
          <div style={{ color: "#3D494D", fontSize: 12, marginTop: 6 }}>
            {uploadedDeck ? "This deck will be reviewed against the selected grant." : "Use Upload Deck to attach your own PPTX, PDF, TXT, or MD file."}
          </div>
        </div>
        <div style={{ border: "1px solid #E0E7EC", borderRadius: 14, padding: 12, background: "#fff" }}>
          <div style={{ color: "#5F6E84", fontSize: 11, fontWeight: 900, letterSpacing: 1 }}>INLINE REVIEW ANALYTICS</div>
          <div style={{ color: reviewScore !== null ? "#494BD6" : "#3D494D", fontSize: 24, fontWeight: 900, marginTop: 4 }}>
            {reviewScore !== null ? `${reviewScore}%` : "Pending"}
          </div>
          <div style={{ color: "#3D494D", fontSize: 12, lineHeight: 1.45 }}>
            {critique?.review_summary || "Upload a pitch deck to see review analytics directly in the interface."}
          </div>
        </div>
      </div>

      {critique && (
        <div aria-live="polite" style={{ marginTop: 16, padding: 16, border: "1px solid #E0E7EC", borderRadius: 20, background: "linear-gradient(180deg, #ffffff 0%, #fbfdff 100%)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 900, letterSpacing: 1.4, color: "#6B7280" }}>REVIEW ANALYTICS</div>
              <div style={{ fontSize: 18, fontWeight: 900, color: "#191C1E", marginTop: 4 }}>Deck evaluation results</div>
            </div>
            <span className={s.tag} style={{ background: "#FFF4E5", color: "#904D00" }}>
              INLINE RESULT
            </span>
          </div>

          <div style={{ height: 14 }} />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 12 }}>
            <div style={{ border: "1px solid #E0E7EC", borderRadius: 16, padding: 14, background: "#fff" }}>
              <div style={{ color: "#5F6E84", fontSize: 11, fontWeight: 900, letterSpacing: 1 }}>UPLOADED DECK</div>
              <div style={{ color: "#191C1E", fontSize: 13, fontWeight: 800, marginTop: 8, overflowWrap: "anywhere" }}>
                {evaluatedDeck?.file_name || "No uploaded pitch deck yet"}
              </div>
              <div style={{ color: "#3D494D", fontSize: 12, marginTop: 8, lineHeight: 1.5 }}>
                {evaluatedDeck ? "This inline review is attached to the selected grant and uploaded deck." : "Upload a deck to trigger evaluation."}
              </div>
            </div>

            <div style={{ border: "1px solid #E0E7EC", borderRadius: 16, padding: 14, background: "#fff" }}>
              <div style={{ color: "#5F6E84", fontSize: 11, fontWeight: 900, letterSpacing: 1 }}>REVIEW ANALYTICS</div>
              <div style={{ color: "#904D00", fontSize: 34, fontWeight: 900, marginTop: 8 }}>{reviewScore ?? 0}%</div>
              <div style={{ height: 10, borderRadius: 999, background: "#E5E7EB", overflow: "hidden", marginTop: 12 }}>
                <div style={{ width: `${reviewScore ?? 0}%`, height: "100%", background: "linear-gradient(90deg, #904D00, #006780)" }} />
              </div>
              <div style={{ marginTop: 10, fontSize: 12, color: "#3D494D", lineHeight: 1.55 }}>
                {critique.review_summary || "The evaluator has analysed the deck and generated inline analytics."}
              </div>
            </div>
          </div>

          <div style={{ height: 12 }} />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
            <CritiqueList title="Strengths" icon="thumb_up" color="#006780" items={critique.strengths} />
            <CritiqueList title="Improve" icon="construction" color="#904D00" items={critique.weaknesses} />
            <CritiqueList title="Next Actions" icon="playlist_add_check" color="#494BD6" items={critique.action_items_to_improve} />
          </div>
        </div>
      )}
    </div>
  );
}

function CritiqueList({ title, icon, color, items }: { title: string; icon: string; color: string; items: string[] }) {
  return (
    <div style={{ border: "1px solid #E0E7EC", borderRadius: 14, padding: 12, background: "#fff" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, color, fontSize: 12, fontWeight: 900, letterSpacing: 1 }}>
        <MI name={icon} size={14} color={color} />{title.toUpperCase()}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
        {items.slice(0, 4).map((item, index) => (
          <div key={`${title}-${index}`} style={{ display: "flex", gap: 8, color: "#3D494D", fontSize: 12, lineHeight: 1.4 }}>
            <span style={{ color, fontWeight: 900 }}>{index + 1}</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function GeneratedOutputs({
  snapshot,
  currentUser,
  grantId,
}: {
  snapshot: GrantApplicationRead | null;
  currentUser: UserRead | null;
  grantId: number | null;
}) {
  const inlineReviewTypes = new Set(["pitch_deck_critique", "pitch_deck_review", "pitch_deck_evaluation"]);
  const generated = (snapshot?.generated_documents || []).filter((document) => {
    const lowerName = document.file_name.toLowerCase();
    return !inlineReviewTypes.has(document.document_type.toLowerCase()) && !lowerName.endsWith(".md");
  });
  if (!snapshot || !currentUser || !grantId || generated.length === 0) return null;

  const iconForDocument = (document: DocumentRead): string => {
    if (document.file_name.toLowerCase().endsWith(".pptx")) return "slideshow";
    if (document.file_name.toLowerCase().endsWith(".pdf")) return "picture_as_pdf";
    if (document.document_type === "presentation_script") return "notes";
    return "description";
  };

  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
      <div style={{ fontWeight: 900, letterSpacing: 1, fontSize: 13, color: "#191C1E", marginBottom: 14 }}>DRAFTER AGENT OUTPUTS</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
        {generated.map((document) => (
          <a
            key={document.id}
            href={backendDownloadUrl(`/grants/${grantId}/application/${currentUser.id}/documents/${document.id}/download`)}
            className="btn-soft"
            style={{ justifyContent: "flex-start", textDecoration: "none", fontSize: 12, minHeight: 44 }}
          >
            <MI name={iconForDocument(document)} size={15} />
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{document.file_name}</span>
          </a>
        ))}
      </div>
    </div>
  );
}

function ApplicationChecklist({
  snapshot,
  loading,
  uploadingRequirementId,
  collapsed,
  onToggleCollapse,
  onGenerate,
  onUpload,
}: {
  snapshot: GrantApplicationRead | null;
  loading: boolean;
  uploadingRequirementId?: number | null;
  collapsed: boolean;
  onToggleCollapse: () => void;
  onGenerate: (item: GrantApplicationRead["checklist"][number]) => void;
  onUpload: (item: GrantApplicationRead["checklist"][number], file: File) => void;
}) {
  const inputRefs = React.useRef<Record<number, HTMLInputElement | null>>({});

  const checklistTone = (item: GrantApplicationRead["checklist"][number]) => {
    const source = (item.fulfillment_source || "").toLowerCase();
    if (item.download_url) return { background: "#ECFDF5", color: "#059669", icon: "check_circle" };
    if (item.fulfilled && source.includes("upload")) return { background: "#ECFDF5", color: "#059669", icon: "check_circle" };
    if (item.fulfilled && source.includes("generate")) return { background: "#ECFDF5", color: "#059669", icon: "check_circle" };
    if (item.can_generate && item.can_upload) return { background: "#fff", color: "#006780", icon: "auto_awesome" };
    if (item.can_generate) return { background: "#fff", color: "#006780", icon: "auto_awesome" };
    return { background: "#fff", color: "#904D00", icon: "upload_file" };
  };

  const actionButtons = (item: GrantApplicationRead["checklist"][number]) => {
    const buttons: React.ReactNode[] = [];

    if (item.can_generate) {
      buttons.push(
        <button key="generate" className="btn-primary" style={{ fontSize: 12 }} onClick={() => onGenerate(item)}>
          <MI name="auto_awesome" size={14} />Generate
        </button>,
      );
    }

    if (item.can_upload) {
      buttons.push(
        <React.Fragment key="upload">
          <input
            ref={(element) => {
              inputRefs.current[item.requirement_id] = element;
            }}
            type="file"
            style={{ display: "none" }}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(item, file);
              event.currentTarget.value = "";
            }}
          />
          <button
            type="button"
            className="btn-soft"
            style={{ fontSize: 12 }}
            disabled={uploadingRequirementId === item.requirement_id}
            onClick={() => inputRefs.current[item.requirement_id]?.click()}
          >
            <MI name="upload" size={14} />
            {uploadingRequirementId === item.requirement_id ? "Uploading" : "Upload"}
          </button>
        </React.Fragment>,
      );
    }

    if (item.download_url) {
      buttons.push(
        <a key="download" href={backendDownloadUrl(item.download_url)} className="btn-soft" style={{ fontSize: 12, textDecoration: "none" }}>
          <MI name="download" size={14} />Download
        </a>,
      );
    }

    return <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{buttons}</div>;
  };

  return (
    <div className={s.panel} style={{ borderRadius: 26, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: collapsed ? 0 : 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <MI name="assignment" size={17} color="#BA1A1A" />
          <div style={{ fontWeight: 900, letterSpacing: 1, fontSize: 13, color: "#191C1E" }}>EVALUATOR AGENT CHECKLIST</div>
        </div>
        <button type="button" className="btn-soft" onClick={onToggleCollapse} style={{ fontSize: 11, padding: "4px 8px" }}>
          <MI name={collapsed ? "unfold_more" : "unfold_less"} size={14} />
          {collapsed ? "Expand" : "Collapse"}
        </button>
      </div>
      {collapsed ? (
        <div style={{ color: "#3D494D", fontSize: 13 }}>Checklist collapsed. Expand to review the generated, uploaded, and missing items.</div>
      ) : loading ? (
        <div style={{ color: "#3D494D", fontSize: 13 }}>Loading checklist...</div>
      ) : !snapshot ? (
        <div style={{ color: "#3D494D", fontSize: 13 }}>No application snapshot loaded.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {snapshot.checklist.map((item) => (
            <div key={item.requirement_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, border: "1px solid #E0E7EC", borderRadius: 14, background: item.fulfilled ? checklistTone(item).background : "#fff" }}>
              <MI name={checklistTone(item).icon} size={20} color={checklistTone(item).color} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: "#191C1E" }}>{item.name}</div>
                <div style={{ fontSize: 11, color: "#3D494D", marginTop: 3 }}>
                  {item.action_label}{item.fulfilled && item.fulfillment_source ? ` · ${item.fulfillment_source}` : ""}
                </div>
              </div>
              {actionButtons(item)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MatchCard({ match, selected, onApply }: { match: RankedGrantRead; selected?: boolean; onApply: () => void }) {
  const unmet = match.evidence_traces.some((trace) => trace.status !== "MET");
  return (
    <div className={s.matchCard} style={{ borderColor: selected ? "#00B4D8" : undefined }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span style={{ color: "#3D494D", fontWeight: 600, fontSize: 12 }}>{match.grant.provider_name}</span><span className={s.tag} style={{ background: "#F2F4F6", color: "#006780" }}>{Math.round(match.suitability_score)}%</span></div>
      <div style={{ height: 10 }} />
      <div style={{ fontSize: 14, fontWeight: 900, lineHeight: 1.15, color: "#191C1E" }}>{match.grant.title}</div>
      <div style={{ height: 10 }} />
      <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}><div style={{ width: 5, height: 5, borderRadius: "50%", background: unmet ? "#BA1A1A" : "#494BD6", marginTop: 6, flexShrink: 0 }} /><span style={{ color: unmet ? "#7D1A1A" : "#3D494D", lineHeight: 1.35, fontSize: 12 }}>{deadlineStatus(match.grant.application_deadline)} - {statusLabel(match)}</span></div>
      <div style={{ height: 10, display: "flex", justifyContent: "flex-end" }} />
      <div style={{ display: "flex", justifyContent: "flex-end" }}><button className="btn-soft" onClick={onApply}><MI name="route" size={14} />Open</button></div>
    </div>
  );
}


