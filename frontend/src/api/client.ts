import type {
  ChatMessage,
  DocumentInfo,
  HealthStatus,
  SessionInfo,
  SourceCitation,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

export async function uploadDocuments(files: File[]): Promise<{
  documents: DocumentInfo[];
  total_chunks: number;
  message: string;
}> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function listDocuments(): Promise<{ documents: DocumentInfo[] }> {
  return request("/api/documents");
}

export async function sendChat(
  question: string,
  sessionId?: string | null
): Promise<{
  answer: string;
  sources: SourceCitation[];
  session_id: string;
}> {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
}

export async function listSessions(): Promise<{ sessions: SessionInfo[] }> {
  return request("/api/sessions");
}

export async function getSessionMessages(sessionId: string): Promise<{
  session_id: string;
  messages: Array<{
    id: string;
    role: string;
    content: string;
    sources: SourceCitation[];
    created_at: string;
  }>;
}> {
  return request(`/api/sessions/${sessionId}/messages`);
}

export type StreamCallbacks = {
  onSources: (sources: SourceCitation[]) => void;
  onToken: (token: string) => void;
  onDone: (sessionId: string) => void;
  onError: (error: Error) => void;
};

export async function streamChat(
  question: string,
  sessionId: string | null,
  callbacks: StreamCallbacks
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });

  if (!res.ok || !res.body) {
    callbacks.onError(new Error("Stream request failed"));
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let event = "message";
      let data = "";
      for (const line of lines) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        if (line.startsWith("data:")) data = line.slice(5).trim();
      }
      if (!data) continue;
      try {
        if (event === "sources") {
          callbacks.onSources(JSON.parse(data));
        } else if (event === "token") {
          callbacks.onToken(JSON.parse(data));
        } else if (event === "done") {
          const payload = JSON.parse(data);
          callbacks.onDone(payload.session_id);
        }
      } catch {
        /* skip malformed */
      }
    }
  }
}

export function mapSessionMessages(
  raw: Array<{
    id: string;
    role: string;
    content: string;
    sources: SourceCitation[];
  }>
): ChatMessage[] {
  return raw.map((m) => ({
    id: m.id,
    role: m.role as "user" | "assistant",
    content: m.content,
    sources: m.sources,
  }));
}
