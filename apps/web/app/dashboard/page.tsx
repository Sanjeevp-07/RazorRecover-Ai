"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import { KPICard } from "@/components/dashboard/KPICard";
import Link from "next/link";
import { 
  AlertTriangle, 
  TrendingUp, 
  CheckCircle2, 
  Percent, 
  Clock, 
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  FlaskConical,
  Play
} from "lucide-react";

import { DashboardSkeleton } from "@/components/ui/Skeleton";
import { ShortIdBadge } from "@/components/ui/ShortIdBadge";

interface DashboardSummary {
  failed_revenue_minor: number;
  recoverable_revenue_minor: number;
  recovered_revenue_minor: number;
  recovery_rate: number;
  pending_cases: number;
  escalations: number;
  recent_cases: any[];
}

export default function DashboardPage() {
  const { token } = useAuth();

  const { data, isLoading, isError, error, refetch } = useQuery<DashboardSummary>({
    queryKey: ["dashboard-summary"],
    queryFn: () => fetchApi<DashboardSummary>("/dashboard/summary", { method: "GET" }, token),
    refetchInterval: 8000,
  });

  const formatCurrency = (amountMinor: number = 0) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amountMinor / 100);
  };

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-8">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Recovery Dashboard</h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">Real-time revenue recovery metrics and case activity</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/simulation"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run in Shadow Mode</span>
          </Link>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 shadow-2xs transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Action Simulator Dry Run Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-900 via-slate-900 to-indigo-950 text-white flex flex-col md:flex-row items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center flex-shrink-0">
            <FlaskConical className="w-5 h-5 text-blue-300" />
          </div>
          <div>
            <h3 className="font-extrabold text-sm text-white">🧪 Action Simulator / Dry Run Available</h3>
            <p className="text-xs text-slate-300 font-medium mt-0.5">
              Analyze 1,000 failed payment events in Shadow Mode to preview estimated recovery & incremental lift before turning on autonomous recovery.
            </p>
          </div>
        </div>
        <Link
          href="/simulation"
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs transition-colors flex-shrink-0"
        >
          Open Action Simulator →
        </Link>
      </div>

      {/* 6 KPI Cards (§19) */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard
          title="Failed Revenue"
          value={formatCurrency(data?.failed_revenue_minor || 0)}
          subtitle="Total failed payment volume"
          icon={AlertTriangle}
          color="rose"
        />
        <KPICard
          title="Recoverable"
          value={formatCurrency(data?.recoverable_revenue_minor || 0)}
          subtitle="Qualified for AI recovery"
          icon={TrendingUp}
          color="indigo"
        />
        <KPICard
          title="Recovered"
          value={formatCurrency(data?.recovered_revenue_minor || 0)}
          subtitle="Successfully captured revenue"
          icon={CheckCircle2}
          color="emerald"
        />
        <KPICard
          title="Recovery Rate"
          value={`${((data?.recovery_rate || 0) * 100).toFixed(1)}%`}
          subtitle="Conversion baseline vs AI"
          icon={Percent}
          color="violet"
        />
        <KPICard
          title="Pending Cases"
          value={String(data?.pending_cases || 0)}
          subtitle="Active recovery workflows"
          icon={Clock}
          color="amber"
        />
        <KPICard
          title="Escalations"
          value={String(data?.escalations || 0)}
          subtitle="Requiring human approval"
          icon={ShieldAlert}
          color="rose"
        />
      </div>

      {/* Recent Recovery Cases List (§19) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-200 bg-white shadow-xs">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Recent Recovery Cases</h3>
            <p className="text-xs text-slate-500 font-medium">Latest payment failure ingestion events</p>
          </div>
          <Link
            href="/recovery"
            className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span>View All Cases</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="p-3.5">Case ID</th>
                <th className="p-3.5">Payment ID</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Created At</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data?.recent_cases && data.recent_cases.length > 0 ? (
                data.recent_cases.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3.5 font-mono text-slate-800 font-semibold">
                      <ShortIdBadge id={c.id} />
                    </td>
                    <td className="p-3.5 font-mono text-slate-600">
                      <ShortIdBadge id={c.payment_id} />
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase border ${
                        c.status === "RECOVERED"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : c.status === "ESCALATED_HUMAN"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : c.status === "FAILED"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-blue-50 text-blue-700 border-blue-200"
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-500 font-medium">
                      {new Date(c.created_at || Date.now()).toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        href={`/recovery/${c.id}`}
                        className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-bold transition-colors"
                      >
                        Detail
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-400">
                    No recent recovery cases found. Run live simulation in scripts/stream_live_traffic.py
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
