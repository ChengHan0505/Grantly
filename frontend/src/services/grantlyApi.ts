const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';
const AI_SANDBOX_BASE_URL = process.env.NEXT_PUBLIC_AI_SANDBOX_BASE_URL || 'http://localhost:8001';

function backendUrl(path: string): string {
  return `${BACKEND_BASE_URL}${path}`;
}

function sandboxUrl(path: string): string {
  return `${AI_SANDBOX_BASE_URL}${path}`;
}

function ensureOk(response: Response, acceptedCodes: Set<number> = new Set([200])): void {
  if (!acceptedCodes.has(response.status)) {
    throw new Error(`API error ${response.status}`);
  }
}

export async function healthCheck(): Promise<Record<string, unknown>> {
  const response = await fetch(backendUrl('/'));
  ensureOk(response);
  return response.json();
}

export async function createUser(params: {
  username: string;
  email: string;
  externalAuthId?: string;
}): Promise<Record<string, unknown>> {
  const response = await fetch(backendUrl('/users'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: params.username,
      email: params.email,
      external_auth_id: params.externalAuthId,
    }),
  });
  ensureOk(response, new Set([201]));
  return response.json();
}

export async function rankedGrants(userId: number): Promise<unknown[]> {
  const response = await fetch(backendUrl(`/grants/match/${userId}`));
  ensureOk(response);
  return response.json();
}

export async function aiSandboxPing(): Promise<Record<string, unknown>> {
  const response = await fetch(sandboxUrl('/health'));
  ensureOk(response);
  return response.json();
}
