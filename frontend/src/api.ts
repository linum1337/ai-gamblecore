import type { GenerateResponse, ProviderConfig, RollResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Неизвестная ошибка" }));
    throw new Error(body.detail ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function createRoll(adultMode: boolean, allowTokenBurn: boolean): Promise<RollResponse> {
  const params = new URLSearchParams({
    adult_mode: String(adultMode),
    allow_token_burn: String(allowTokenBurn),
  });
  return request<RollResponse>(`/roll?${params}`, { method: "POST" });
}

export function generate(
  prompt: string,
  rollId: string,
  demo: boolean,
  provider: ProviderConfig,
): Promise<GenerateResponse> {
  return request<GenerateResponse>("/generate", {
    method: "POST",
    body: JSON.stringify({ prompt, roll_id: rollId, demo, provider: demo ? null : provider }),
  });
}
