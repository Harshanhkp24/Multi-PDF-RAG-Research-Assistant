import { useState } from "react";
import type { SourceCitation as Source } from "../types";

interface Props {
  sources: Source[];
}

export function SourceCitationList({ sources }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  if (!sources.length) return null;

  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Sources</p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s, i) => (
          <div key={`${s.document_id}-${s.page}-${i}`} className="w-full sm:w-auto">
            <button
              type="button"
              onClick={() => setExpanded(expanded === i ? null : i)}
              className="text-xs px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition"
            >
              {s.filename} · p.{s.page}
            </button>
            {expanded === i && (
              <p className="mt-2 p-3 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-700">
                {s.snippet}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
