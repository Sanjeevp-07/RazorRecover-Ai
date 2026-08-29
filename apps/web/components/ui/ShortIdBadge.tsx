"use client";

import React, { useState } from "react";
import { Copy, Check } from "lucide-react";
import { formatShortId } from "@/lib/utils/format";

interface ShortIdBadgeProps {
  id: string;
  prefix?: "case" | "pay" | "corr";
  className?: string;
}

export function ShortIdBadge({ id, prefix = "case", className = "" }: ShortIdBadgeProps) {
  const [copied, setCopied] = useState(false);
  const shortText = formatShortId(id, prefix);

  const copyToClipboard = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <span
      title={`Click to copy full ID: ${id}`}
      onClick={copyToClipboard}
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-900/80 border border-slate-800 font-mono text-[11px] hover:border-indigo-500/40 hover:bg-slate-800/80 cursor-pointer transition-colors group ${className}`}
    >
      <span className={prefix === "case" ? "text-indigo-300" : "text-slate-300 font-semibold"}>
        {shortText}
      </span>
      {copied ? (
        <Check className="w-3 h-3 text-emerald-400" />
      ) : (
        <Copy className="w-3 h-3 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity" />
      )}
    </span>
  );
}
