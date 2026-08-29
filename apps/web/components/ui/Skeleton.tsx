import React from "react";

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-slate-800/40 before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-indigo-500/10 before:to-transparent ${className}`}
    />
  );
}

export function DecisionChainSkeleton() {
  return (
    <div className="space-y-8 max-w-6xl animate-fade-in">
      {/* Header bar skeleton */}
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-36" />
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-6 w-28 rounded-full" />
          </div>
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-32 rounded-xl" />
          <Skeleton className="h-10 w-32 rounded-xl" />
        </div>
      </div>

      {/* 3-column Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Risk Signals */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500/20 animate-pulse" />
            <Skeleton className="h-4 w-28" />
          </div>
          <div className="space-y-3 pt-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>

        {/* AI Recommendation */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 relative overflow-hidden">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-indigo-500/30 animate-ping" />
            <Skeleton className="h-4 w-36" />
          </div>
          <div className="space-y-3 pt-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-20 w-full rounded-xl" />
          </div>
        </div>

        {/* Policy Decision */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-emerald-500/20 animate-pulse" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="space-y-3 pt-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
      </div>

      {/* Timeline Skeleton */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-indigo-500/20" />
          <Skeleton className="h-4 w-40" />
        </div>
        <div className="space-y-3 pt-2">
          <Skeleton className="h-12 w-full rounded-xl" />
          <Skeleton className="h-12 w-full rounded-xl" />
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>
      </div>
    </div>
  );
}

export function TablePageSkeleton({ 
  title = "Loading Data...", 
  subtitle = "Fetching latest records...",
  columns = 5,
  rows = 6 
}: { 
  title?: string;
  subtitle?: string;
  columns?: number;
  rows?: number;
}) {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
          <p className="text-xs text-slate-400">{subtitle}</p>
        </div>
        <Skeleton className="h-9 w-40 rounded-xl" />
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-4 w-28" />
        </div>
        <div className="divide-y divide-slate-800/60 p-2 space-y-2">
          {[...Array(rows)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-5 w-20 rounded-full" />
              <Skeleton className="h-5 w-28" />
              <Skeleton className="h-7 w-20 rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="space-y-1.5">
          <h2 className="text-2xl font-bold text-white tracking-tight">Recovery Dashboard</h2>
          <p className="text-xs text-slate-400">Real-time revenue recovery metrics and case activity</p>
        </div>
        <Skeleton className="h-8 w-24 rounded-xl" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-32 glass-panel rounded-2xl border border-slate-800 p-5 space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <Skeleton className="h-3.5 w-16" />
              <Skeleton className="h-7 w-7 rounded-lg" />
            </div>
            <Skeleton className="h-7 w-28" />
            <Skeleton className="h-3 w-32" />
          </div>
        ))}
      </div>

      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between mb-4">
          <Skeleton className="h-5 w-44" />
          <Skeleton className="h-4 w-28" />
        </div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full rounded-xl" />
          ))}
        </div>
      </div>
    </div>
  );
}
