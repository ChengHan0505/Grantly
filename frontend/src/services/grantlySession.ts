import { ApiError, createOrLookupUser, lookupUser, type UserRead } from "./grantlyApi";

const CURRENT_USER_KEY = "grantly.currentUser";
const ONBOARDING_KEY = "grantly.onboarding";

export type OnboardingDraft = {
  business?: {
    summary?: string;
    industry?: string;
    stage?: string;
    traction?: string[];
    fundingUse?: string;
    companyName?: string;
    annualRevenue?: number | null;
    employeeCount?: number | null;
    targetGrantAmount?: number | null;
  };
  documents?: {
    document_type: string;
    file_name: string;
    file_url?: string | null;
    status?: string;
    metadata?: Record<string, unknown>;
  }[];
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function readJson<T>(key: string): T | null {
  if (!isBrowser()) return null;
  const value = window.localStorage.getItem(key);
  if (!value) return null;
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

function writeJson<T>(key: string, value: T): void {
  if (!isBrowser()) return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function getCurrentUser(): UserRead | null {
  return readJson<UserRead>(CURRENT_USER_KEY);
}

export function setCurrentUser(user: UserRead): void {
  writeJson(CURRENT_USER_KEY, user);
}

export function clearCurrentUser(): void {
  if (!isBrowser()) return;
  window.localStorage.removeItem(CURRENT_USER_KEY);
}

export async function rehydrateCurrentUser(): Promise<UserRead | null> {
  const cached = getCurrentUser();
  if (!cached) return null;
  try {
    const user = await lookupUser({
      email: cached.email,
      externalAuthId: cached.external_auth_id ?? undefined,
    });
    setCurrentUser(user);
    return user;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      clearCurrentUser();
      return null;
    }
    return cached;
  }
}

export function getOnboardingDraft(): OnboardingDraft {
  return readJson<OnboardingDraft>(ONBOARDING_KEY) || {};
}

export function saveOnboardingDraft(patch: OnboardingDraft): OnboardingDraft {
  const current = getOnboardingDraft();
  const next = {
    ...current,
    ...patch,
    business: { ...(current.business || {}), ...(patch.business || {}) },
    documents: patch.documents ?? current.documents,
  };
  writeJson(ONBOARDING_KEY, next);
  return next;
}

export function clearOnboardingDraft(): void {
  if (!isBrowser()) return;
  window.localStorage.removeItem(ONBOARDING_KEY);
}

export function usernameFromEmail(email: string): string {
  const localPart = email.split("@")[0] || "user";
  const normalized = localPart.toLowerCase().replace(/[^a-z0-9_]+/g, "_").replace(/^_+|_+$/g, "");
  return (normalized || "user").slice(0, 64).padEnd(3, "0");
}

export async function createBackendSession(params: {
  email: string;
  displayName?: string | null;
  externalAuthId?: string;
}): Promise<UserRead> {
  const username = params.displayName
    ? params.displayName.toLowerCase().replace(/[^a-z0-9_]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 64)
    : usernameFromEmail(params.email);
  const user = await createOrLookupUser({
    username: (username || usernameFromEmail(params.email)).padEnd(3, "0"),
    email: params.email,
    externalAuthId: params.externalAuthId,
  });
  setCurrentUser(user);
  return user;
}
