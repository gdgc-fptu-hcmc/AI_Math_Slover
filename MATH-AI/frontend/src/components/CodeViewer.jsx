import React, { useState } from "react";
import { FiCopy, FiCheck, FiCode } from "react-icons/fi";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

const CodeViewer = ({ code, language = "python" }) => {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const truncatedCode = code.split("\n").slice(0, 10).join("\n");
  const shouldTruncate = code.split("\n").length > 10;

  return (
    <div className="my-4 overflow-hidden rounded-3xl border border-slate-800/60 bg-slate-950/70 shadow-[0_40px_120px_-60px_rgba(8,47,73,0.8)] backdrop-blur">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/60 bg-gradient-to-r from-slate-900/80 via-sky-900/40 to-slate-900/80 px-6 py-4">
        <div className="flex items-center gap-3 text-sky-200">
          <FiCode className="text-xl" />
          <div className="flex flex-col">
            <span className="font-mono text-[0.7rem] uppercase tracking-[0.4em] text-sky-300/80">
              Manim Blueprint
            </span>
            <span className="text-base font-semibold text-slate-100">
              Generated Scene Code
            </span>
          </div>
        </div>
        <button
          onClick={handleCopy}
          className="group flex items-center gap-2 rounded-2xl border border-slate-700/70 bg-slate-900/70 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100"
          title="Copy code"
        >
          {copied ? (
            <>
              <FiCheck className="text-emerald-300 transition group-hover:text-emerald-200" />
              <span className="text-emerald-200">Copied!</span>
            </>
          ) : (
            <>
              <FiCopy className="transition group-hover:text-sky-300" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Content */}
      <div className="relative">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            padding: "1.25rem",
            fontSize: "0.875rem",
            background: "rgba(15, 23, 42, 0.85)",
            borderRadius: "1.75rem",
            boxShadow: "inset 0 0 0 1px rgba(148, 163, 184, 0.18)",
            maxHeight: isExpanded ? "none" : "320px",
            overflow: "auto",
          }}
          showLineNumbers={true}
        >
          {isExpanded || !shouldTruncate ? code : truncatedCode}
        </SyntaxHighlighter>

        {/* Expand/Collapse Button */}
        {shouldTruncate && (
          <div className="pointer-events-none absolute inset-x-0 bottom-0 flex h-20 items-end justify-center bg-gradient-to-t from-slate-950/95 via-slate-900/20 to-transparent pb-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="pointer-events-auto rounded-2xl border border-slate-700/70 bg-slate-900/80 px-5 py-2 text-sm font-medium text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100"
            >
              {isExpanded
                ? "Show Less"
                : `Show More (${code.split("\n").length - 10} more lines)`}
            </button>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="flex flex-wrap items-center gap-3 border-t border-slate-800/60 bg-slate-950/70 px-6 py-3 text-xs text-slate-400">
        <span className="font-mono uppercase tracking-[0.35em] text-sky-300/80">
          {code.split("\n").length} lines
        </span>
        <span className="text-slate-600">•</span>
        <span className="font-mono text-slate-400">
          {code.length} characters
        </span>
      </div>
    </div>
  );
};

export default CodeViewer;
