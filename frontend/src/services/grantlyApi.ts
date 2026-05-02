export const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || "http://localhost:8000";
const AI_SANDBOX_BASE_URL = process.env.NEXT_PUBLIC_AI_SANDBOX_BASE_URL || "http://localhost:8001";

export type UserRead = {
  id: number;
  username: string;
  email: string;
  external_auth_id?: string | null;
  created_at: string;
};

export type DocumentInput = {
  document_type: string;
  file_name: string;
  file_url?: string | null;
  status?: string;
  metadata?: Record<string, unknown>;
};

export type DocumentRead = {
  id: number;
  document_type: string;
  file_name: string;
  file_url?: string | null;
  status: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type CompanyProfileRead = {
  id: number;
  user_id: number;
  company_name: string;
  industry?: string | null;
  nationality?: string | null;
  annual_revenue?: number | null;
  employee_count?: number | null;
  target_grant_amount?: number | null;
  business_stage?: string | null;
  summary?: string | null;
  questionnaire_answers: Record<string, unknown>;
  extracted_data: Record<string, unknown>;
  readiness_score: number;
  created_at: string;
  updated_at: string;
};

export type ExtractorProfileInput = {
  company_name?: string | null;
  ssm_number?: string | null;
  age_in_months?: number | null;
  full_time_employees?: number | null;
  ownership_majority?: string | null;
  sector?: string | null;
  total_project_cost_rm?: number | null;
  requested_funding_rm?: number | null;
  outsourced_cost_rm?: number | null;
  has_end_user_partner?: boolean | null;
  documents_provided?: string[];
  uploaded_pitch_deck_text?: string | null;
};

export type CompanyProfileExtractRequest = {
  raw_text?: string | null;
  questionnaire_answers?: Record<string, unknown>;
  extracted_data?: Record<string, unknown>;
  extractor_profile?: ExtractorProfileInput | null;
  documents?: DocumentInput[];
};

export type SystemStateRead = {
  user_id: number;
  readiness_score: number;
  current_track: string;
  evidence_trace: Record<string, unknown>;
  last_step?: string | null;
  updated_at: string;
};

export type CompanyProfileGenerationRead = {
  profile: CompanyProfileRead;
  documents: DocumentRead[];
  system_state: SystemStateRead;
  next_endpoint: string;
};

export type CompanyProfileUpdateRequest = {
  company_name: string;
  industry?: string | null;
  nationality?: string | null;
  annual_revenue?: number | null;
  employee_count?: number | null;
  target_grant_amount?: number | null;
  business_stage?: string | null;
  summary?: string | null;
  questionnaire_answers?: Record<string, unknown>;
  extracted_data?: Record<string, unknown>;
  documents?: DocumentInput[];
};

export type RequirementRead = {
  id: number;
  name: string;
  description?: string | null;
  source_type: "attached" | "generated";
  document_type?: string | null;
  is_required: boolean;
};

export type GrantRead = {
  id: number;
  title: string;
  provider_name: string;
  source_url?: string | null;
  description?: string | null;
  amount_min?: number | null;
  amount_max?: number | null;
  nationality?: string | null;
  industry?: string | null;
  eligibility_notes?: string | null;
  application_deadline?: string | null;
  status: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  requirements: RequirementRead[];
};

export type EvidenceTraceRead = {
  requirement: string;
  status: string;
  source_document: string;
  reasoning: string;
};

export type RankedGrantRead = {
  grant: GrantRead;
  suitability_score: number;
  readiness_score: number;
  readiness_level: string;
  track: string;
  status: string;
  reasons: string[];
  evidence_traces: EvidenceTraceRead[];
};

export type WorkspaceRead = {
  user: UserRead;
  profile?: CompanyProfileRead | null;
  documents: DocumentRead[];
  ranked_grants: RankedGrantRead[];
  grants: GrantRead[];
};

export type ChecklistItemRead = {
  requirement_id: number;
  name: string;
  description?: string | null;
  source_type: "attached" | "generated";
  document_type?: string | null;
  is_required: boolean;
  fulfilled: boolean;
  fulfillment_source?: string | null;
  category: string;
  completion_status: string;
  can_generate: boolean;
  can_upload: boolean;
  download_url?: string | null;
  action_label: string;
};

export type GrantApplicationRead = {
  grant: GrantRead;
  checklist: ChecklistItemRead[];
  readiness_score: number;
  readiness_level: string;
  track: string;
  missing_required_documents: string[];
  attached_documents: DocumentRead[];
  generated_documents: DocumentRead[];
  coach?: {
    encouraging_message: string;
    next_steps: { document_name: string; explanation: string; action_required: string }[];
  } | null;
  download_package_url: string;
};

export type ApplicationRoadmapStepRead = {
  step_number: number;
  title: string;
  status: string;
  owner: string;
  description: string;
  action: string;
  requirement_id?: number | null;
  document_type?: string | null;
  download_url?: string | null;
};

export type ApplicationRoadmapRead = {
  grant_id: number;
  grant_title: string;
  provider_name: string;
  generated_by: string;
  encouraging_message: string;
  steps: ApplicationRoadmapStepRead[];
};

export type GeneratedDocumentRead = {
  document: DocumentRead;
  requirement_id?: number | null;
  document_type: string;
  content_markdown: string;
  message: string;
};

export type StoredPitchDeckRead = {
  document: {
    id: number;
    document_type: string;
    file_name: string;
    status: string;
    content_type?: string | null;
    generation_mode?: string | null;
    created_at: string;
  };
  download_url: string;
  message: string;
  layout_plan: Record<string, unknown>;
};

export type DrafterOutputRead = {
  business_proposal_markdown: string;
  presentation_script_markdown: string;
  generated_deck?: {
    slide_number: number;
    title: string;
    subtitle?: string | null;
    bullet_points: string[];
    metrics?: { label: string; value: string }[];
    grant_alignment?: string | null;
    speaker_notes?: string | null;
  }[] | null;
  deck_critique?: {
    strengths: string[];
    weaknesses: string[];
    action_items_to_improve: string[];
  } | null;
  generated_documents: DocumentRead[];
};

export type DeckCritiqueRead = {
  overall_score?: number | null;
  review_summary?: string | null;
  strengths: string[];
  weaknesses: string[];
  action_items_to_improve: string[];
};

export type PitchDeckEvaluationRead = {
  critique: DeckCritiqueRead;
  evaluated_document: DocumentRead;
  message: string;
};

export type ScoutStatusRead = {
  status: string;
  run_mode?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  max_runtime_hours: number;
  stop_requested: boolean;
  last_report?: Record<string, unknown> | null;
  message?: string | null;
};

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    const message =
      typeof detail === "string"
        ? detail
        : detail && typeof detail === "object" && "message" in detail
          ? String((detail as { message?: unknown }).message)
          : `API error ${status}`;
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function backendUrl(path: string): string {
  return `${BACKEND_BASE_URL}${path}`;
}

function sandboxUrl(path: string): string {
  return `${AI_SANDBOX_BASE_URL}${path}`;
}

function queryString(params: Record<string, string | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  const rendered = search.toString();
  return rendered ? `?${rendered}` : "";
}

async function ensureOk(response: Response, acceptedCodes: Set<number> = new Set([200])): Promise<void> {
  if (acceptedCodes.has(response.status)) return;

  let detail: unknown = `API error ${response.status}`;
  try {
    const text = await response.text();
    if (text) {
      try {
        const body = JSON.parse(text) as { detail?: unknown };
        detail = body.detail ?? body;
      } catch {
        detail = text;
      }
    }
  } catch {
    /* keep default detail */
  }
  throw new ApiError(response.status, detail);
}

async function requestJson<T>(
  path: string,
  options?: RequestInit,
  acceptedCodes: Set<number> = new Set([200]),
): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && options?.body instanceof FormData;
  const response = await fetch(backendUrl(path), {
    ...options,
    headers: {
      ...(options?.body && !isFormData ? { "Content-Type": "application/json" } : {}),
      ...options?.headers,
    },
  });
  await ensureOk(response, acceptedCodes);
  return response.json() as Promise<T>;
}

export function backendDownloadUrl(path: string): string {
  return backendUrl(path);
}

export async function healthCheck(): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>("/");
}

export async function createUser(params: {
  username: string;
  email: string;
  externalAuthId?: string;
}): Promise<UserRead> {
  return requestJson<UserRead>(
    "/users",
    {
      method: "POST",
      body: JSON.stringify({
        username: params.username,
        email: params.email,
        external_auth_id: params.externalAuthId,
      }),
    },
    new Set([201]),
  );
}

export async function lookupUser(params: {
  email?: string;
  externalAuthId?: string;
}): Promise<UserRead> {
  return requestJson<UserRead>(
    `/users/lookup${queryString({ email: params.email, external_auth_id: params.externalAuthId })}`,
  );
}

export async function createOrLookupUser(params: {
  username: string;
  email: string;
  externalAuthId?: string;
}): Promise<UserRead> {
  try {
    return await createUser(params);
  } catch (error) {
    if (error instanceof ApiError && error.status === 409) {
      return lookupUser({ email: params.email, externalAuthId: params.externalAuthId });
    }
    throw error;
  }
}

export async function getCompanyProfile(userId: number): Promise<CompanyProfileRead> {
  return requestJson<CompanyProfileRead>(`/users/${userId}/company-profile`);
}

export async function updateCompanyProfile(
  userId: number,
  payload: CompanyProfileUpdateRequest,
): Promise<CompanyProfileRead> {
  return requestJson<CompanyProfileRead>(
    `/users/${userId}/company-profile`,
    { method: "PUT", body: JSON.stringify({ ...payload, documents: payload.documents ?? [] }) },
  );
}

export async function getWorkspace(userId: number): Promise<WorkspaceRead> {
  return requestJson<WorkspaceRead>(`/users/${userId}/workspace`);
}

export async function extractCompanyProfile(
  userId: number,
  payload: CompanyProfileExtractRequest,
): Promise<CompanyProfileGenerationRead> {
  return requestJson<CompanyProfileGenerationRead>(
    `/users/${userId}/company-profile/extract`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export async function listDocuments(userId: number): Promise<DocumentRead[]> {
  return requestJson<DocumentRead[]>(`/users/${userId}/documents`);
}

export async function listGrants(params?: { includeAll?: boolean }): Promise<GrantRead[]> {
  return requestJson<GrantRead[]>(`/grants${params?.includeAll ? "?include_all=true" : ""}`);
}

export async function rankedGrants(userId: number): Promise<RankedGrantRead[]> {
  return requestJson<RankedGrantRead[]>(`/grants/match/${userId}`);
}

export async function getGrantApplication(grantId: number, userId: number): Promise<GrantApplicationRead> {
  return requestJson<GrantApplicationRead>(`/grants/${grantId}/application/${userId}`);
}

export async function getApplicationRoadmap(grantId: number, userId: number): Promise<ApplicationRoadmapRead> {
  return requestJson<ApplicationRoadmapRead>(`/grants/${grantId}/application/${userId}/roadmap`);
}

export async function generateApplicationDocument(params: {
  grantId: number;
  userId: number;
  requirementId?: number;
  documentType?: string | null;
  documentName?: string | null;
}): Promise<GeneratedDocumentRead> {
  return requestJson<GeneratedDocumentRead>(
    `/grants/${params.grantId}/application/${params.userId}/documents/generate`,
    {
      method: "POST",
      body: JSON.stringify({
        requirement_id: params.requirementId,
        document_type: params.documentType,
        document_name: params.documentName,
        regenerate: false,
        extra_context: {},
      }),
    },
  );
}

export async function uploadApplicationDocument(params: {
  grantId: number;
  userId: number;
  file: File;
  documentType?: string | null;
  documentName?: string | null;
  requirementId?: number | null;
}): Promise<DocumentRead> {
  const formData = new FormData();
  formData.set("file", params.file);
  formData.set("document_type", params.documentType || "uploaded_document");
  if (params.documentName) formData.set("document_name", params.documentName);
  if (params.requirementId !== undefined && params.requirementId !== null) {
    formData.set("requirement_id", String(params.requirementId));
  }
  return requestJson<DocumentRead>(
    `/grants/${params.grantId}/application/${params.userId}/documents/upload`,
    { method: "POST", body: formData },
  );
}

export async function generatePitchDeck(params: {
  grantId: number;
  userId: number;
  creative?: boolean;
}): Promise<StoredPitchDeckRead> {
  return requestJson<StoredPitchDeckRead>(
    `/grants/${params.grantId}/application/${params.userId}/pitch-deck/generate`,
    {
      method: "POST",
      body: JSON.stringify({
        creative: params.creative ?? false,
        extra_context: {},
      }),
    },
  );
}

export async function draftApplicationBundle(params: {
  grantId: number;
  userId: number;
  uploadedPitchDeckText?: string | null;
}): Promise<DrafterOutputRead> {
  return requestJson<DrafterOutputRead>(
    `/grants/${params.grantId}/application/${params.userId}/draft`,
    {
      method: "POST",
      body: JSON.stringify({
        uploaded_pitch_deck_text: params.uploadedPitchDeckText,
        extra_context: {},
      }),
    },
  );
}

export async function evaluateUploadedPitchDeck(params: {
  grantId: number;
  userId: number;
  documentId?: number | null;
}): Promise<PitchDeckEvaluationRead> {
  const query = params.documentId ? `?document_id=${params.documentId}` : "";
  return requestJson<PitchDeckEvaluationRead>(
    `/grants/${params.grantId}/application/${params.userId}/pitch-deck/evaluate${query}`,
    { method: "POST" },
  );
}

export async function runScoutAgent(): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>("/grants/scout/run", { method: "POST" });
}

export async function getScoutStatus(): Promise<ScoutStatusRead> {
  return requestJson<ScoutStatusRead>("/grants/scout/status");
}

export async function aiSandboxPing(): Promise<Record<string, unknown>> {
  const response = await fetch(sandboxUrl("/health"));
  await ensureOk(response);
  return response.json();
}
