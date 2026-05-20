import { useCallback, useEffect, useRef, useState } from "react";
import { listDocuments, uploadDocuments } from "../api/client";
import type { DocumentInfo } from "../types";

interface Props {
  onUploaded?: () => void;
}

export function DocumentUpload({ onUploaded }: Props) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch {
      /* ignore on first load */
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleFiles = async (files: FileList | null) => {
    if (!files?.length) return;
    const pdfs = Array.from(files).filter((f) => f.name.toLowerCase().endsWith(".pdf"));
    if (!pdfs.length) {
      setError("Please select PDF files only.");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      await uploadDocuments(pdfs);
      await refresh();
      onUploaded?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        role="button"
        tabIndex={0}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
          dragOver
            ? "border-indigo-500 bg-indigo-50"
            : "border-slate-300 hover:border-indigo-400 hover:bg-slate-50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <p className="text-slate-700 font-medium">
          {uploading ? "Indexing PDFs..." : "Drop PDFs here or click to upload"}
        </p>
        <p className="text-sm text-slate-500 mt-1">Multiple files supported</p>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
      )}

      {documents.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-700">Indexed documents</h3>
          <ul className="space-y-1">
            {documents.map((d) => (
              <li
                key={d.document_id}
                className="flex justify-between text-sm bg-white border border-slate-200 rounded-lg px-3 py-2"
              >
                <span className="truncate text-slate-800">{d.filename}</span>
                <span className="text-slate-500 shrink-0 ml-2">{d.chunk_count} chunks</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
