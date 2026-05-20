export interface SourceCitation {
  document_id: string;
  filename: string;
  page: number;
  snippet: string;
  score?: number | null;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  chunk_count: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
}

export interface SessionInfo {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface HealthStatus {
  status: string;
  ollama: boolean;
  ollama_models: string[];
  chroma: boolean;
  message?: string | null;
}
