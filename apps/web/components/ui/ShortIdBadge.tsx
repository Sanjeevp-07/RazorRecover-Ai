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
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200 font-mono text-[11px] hover:border-blue-300 hover:bg-blue-50/50 cursor-pointer transition-colors group shadow-2xs ${className}`}
    >
      <span className={prefix === "case" ? "text-blue-600 font-bold" : "text-slate-700 font-bold"}>
        {shortText}
      </span>
      {copied ? (
        <Check className="w-3 h-3 text-emerald-600" />
      ) : (
        <Copy className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
      )}
    </span>
  );
}
