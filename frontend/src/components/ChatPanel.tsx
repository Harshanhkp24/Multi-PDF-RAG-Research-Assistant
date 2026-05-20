import { useEffect, useRef, useState } from "react";
import {
  getSessionMessages,
  listSessions,
  mapSessionMessages,
  streamChat,
} from "../api/client";
import type { ChatMessage, SessionInfo } from "../types";
import { SourceCitationList } from "./SourceCitation";

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadSessions = async () => {
    try {
      const data = await listSessions();
      setSessions(data.sessions);
    } catch {
      /* optional */
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const selectSession = async (id: string) => {
    setSessionId(id);
    setError(null);
    try {
      const data = await getSessionMessages(id);
      setMessages(mapSessionMessages(data.messages));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load session");
    }
  };

  const newChat = () => {
    setSessionId(null);
    setMessages([]);
    setError(null);
  };

  const send = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    const assistantId = crypto.randomUUID();
    let streamedContent = "";

    setMessages((m) => [
      ...m,
      { id: assistantId, role: "assistant", content: "", sources: [] },
    ]);

    await streamChat(question, sessionId, {
      onSources: (sources) => {
        setMessages((m) =>
          m.map((msg) =>
            msg.id === assistantId ? { ...msg, sources } : msg
          )
        );
      },
      onToken: (token) => {
        streamedContent += token;
        setMessages((m) =>
          m.map((msg) =>
            msg.id === assistantId ? { ...msg, content: streamedContent } : msg
          )
        );
      },
      onDone: (sid) => {
        setSessionId(sid);
        setLoading(false);
        loadSessions();
      },
      onError: (err) => {
        setError(err.message);
        setLoading(false);
        setMessages((m) => m.filter((msg) => msg.id !== assistantId));
      },
    });
  };

  return (
    <div className="flex flex-col h-full min-h-[480px]">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-slate-800">Research chat</h2>
        <button
          type="button"
          onClick={newChat}
          className="text-sm px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50"
        >
          New chat
        </button>
      </div>

      {sessions.length > 0 && (
        <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
          {sessions.slice(0, 8).map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => selectSession(s.id)}
              className={`shrink-0 text-xs px-2 py-1 rounded-md border ${
                sessionId === s.id
                  ? "bg-indigo-100 border-indigo-300 text-indigo-800"
                  : "bg-white border-slate-200 text-slate-600"
              }`}
            >
              {(s.title || "Chat").slice(0, 30)}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.length === 0 && (
          <p className="text-slate-500 text-sm text-center py-12">
            Upload PDFs, then ask a question about your documents.
          </p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-white border border-slate-200 text-slate-800"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content || (loading ? "..." : "")}</p>
              {msg.role === "assistant" && msg.sources && (
                <SourceCitationList sources={msg.sources} />
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p className="text-sm text-red-600 mb-2">{error}</p>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="Ask about your documents..."
          disabled={loading}
          className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="button"
          onClick={send}
          disabled={loading || !input.trim()}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
