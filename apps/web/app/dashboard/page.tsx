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
  RefreshCw
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
          <h2 className="text-2xl font-bold text-white tracking-tight">Recovery Dashboard</h2>
          <p className="text-xs text-slate-400 mt-1">Real-time revenue recovery metrics and case activity</p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
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
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Recent Recovery Cases</h3>
            <p className="text-xs text-slate-400">Latest payment failure ingestion events</p>
          </div>
          <Link
            href="/recovery"
            className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            <span>View All Cases</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3.5">Case ID</th>
                <th className="p-3.5">Payment ID</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Created At</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data?.recent_cases && data.recent_cases.length > 0 ? (
                data.recent_cases.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3.5">
                      <Link href={`/recovery/${c.id}`}>
                        <ShortIdBadge id={c.id} prefix="case" />
                      </Link>
                    </td>
                    <td className="p-3.5">
                      <Link href={`/payments/${c.payment_id}`}>
                        <ShortIdBadge id={c.payment_id} prefix="pay" />
                      </Link>
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                        c.status === "RECOVERED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : c.status === "PENDING_APPROVAL"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-slate-800 text-slate-300 border border-slate-700"
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400">
                      {new Date(c.created_at).toLocaleString("en-IN")}
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        href={`/recovery/${c.id}`}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-medium transition-colors"
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
                    No recent recovery cases found.
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
