import { normalizeLocale, type Locale } from "@/i18n";

function getStoredLocale(): Locale {
  if (typeof window === "undefined") return "zh-CN";
  return normalizeLocale(localStorage.getItem("vocab_locale"));
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function setToken(token: string) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
}

function langParam(): string {
  const locale = typeof window !== "undefined" ? getStoredLocale() : "zh-CN";
  return `lang=${encodeURIComponent(locale)}`;
}

function withLang(path: string): string {
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}${langParam()}`;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Accept-Language": getStoredLocale(),
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const url = path.startsWith("http") ? path : `${API_BASE}${withLang(path)}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const message = Array.isArray(detail)
      ? detail.map((d: { msg?: string }) => d.msg || "").filter(Boolean).join("; ")
      : typeof detail === "string"
        ? detail
        : res.statusText;
    throw new Error(message || "Request failed");
  }
  return res.json();
}

export const api = {
  register: (data: {
    username: string;
    password: string;
    level?: string;
    language?: Locale;
  }) =>
    request<{ access_token: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (username: string, password: string) =>
    request<{ access_token: string }>("/api/auth/login/json", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  profile: () => request<Record<string, unknown>>("/api/user/profile"),

  updateProfile: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>("/api/user/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  recommend: (scene: string, limit = 10) =>
    request<Record<string, unknown>>(
      `/api/recommend?scene_type=${scene}&limit=${limit}`
    ),

  recordLearning: (data: Record<string, unknown>) =>
    request<{ status: string }>("/api/learning/record", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  knowledgeStatus: () =>
    request<Record<string, unknown>>("/api/learning/knowledge/status"),

  rootPuzzle: () => request<Record<string, unknown>>("/api/games/root-puzzle"),

  submitPuzzle: (answers: Record<string, unknown>[], sceneType = "focus") =>
    request<Record<string, unknown>>("/api/games/root-puzzle/result", {
      method: "POST",
      body: JSON.stringify({ answers, scene_type: sceneType }),
    }),

  semanticMatch: () =>
    request<Record<string, unknown>>("/api/games/semantic-match"),

  submitSemanticMatch: (
    pairs: { word_id: number; meaning_id: number }[],
    sceneType = "focus"
  ) =>
    request<Record<string, unknown>>("/api/games/semantic-match/result", {
      method: "POST",
      body: JSON.stringify({ pairs, scene_type: sceneType }),
    }),

  wordPlanet: (rootId?: number) => {
    const base = rootId
      ? `/api/games/word-planet?root_id=${rootId}`
      : "/api/games/word-planet";
    return request<Record<string, unknown>>(base);
  },

  generateContent: (wordId: number, level: string, scene: string) =>
    request<Record<string, unknown>>(
      `/api/content/generate?word_id=${wordId}&level=${level}&scene_type=${scene}`
    ),

  scenes: () => request<Record<string, unknown>>("/api/context/scenes"),
};
