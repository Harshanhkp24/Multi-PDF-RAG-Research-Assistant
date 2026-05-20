import { useEffect, useState } from "react";
import { getHealth } from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentUpload } from "./components/DocumentUpload";
import type { HealthStatus } from "./types";

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() =>
        setHealth({
          status: "unreachable",
          ollama: false,
          ollama_models: [],
          chroma: false,
          message: "Backend not running. Start FastAPI on port 8000.",
        })
      );
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Multi-PDF RAG Research Assistant</h1>
            <p className="text-sm text-slate-500">Upload PDFs · Ask questions · Get cited answers</p>
          </div>
          {health && (
            <span
              className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                health.status === "healthy"
                  ? "bg-green-100 text-green-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {health.status}
            </span>
          )}
        </div>
        {health?.message && health.status !== "healthy" && (
          <p className="max-w-6xl mx-auto px-4 pb-3 text-xs text-amber-700">{health.message}</p>
        )}
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 grid lg:grid-cols-2 gap-8">
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Documents</h2>
          <DocumentUpload />
        </section>
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col">
          <ChatPanel />
        </section>
      </main>
    </div>
  );
}

export default App;
