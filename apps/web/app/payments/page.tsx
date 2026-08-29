"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { CreditCard, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import { TablePageSkeleton } from "@/components/ui/Skeleton";
import { ShortIdBadge } from "@/components/ui/ShortIdBadge";

interface PaymentListResponse {
  items: any[];
  total: number;
  page: number;
  page_size: number;
}

export default function PaymentsPage() {
  const { token } = useAuth();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const pageSize = 20;

  const { data, isLoading } = useQuery<PaymentListResponse>({
    queryKey: ["payments-list", statusFilter, page],
    queryFn: () => {
      let endpoint = `/payments?page=${page}&page_size=${pageSize}`;
      if (statusFilter) {
        endpoint += `&status=${statusFilter}`;
      }
      return fetchApi<PaymentListResponse>(endpoint, { method: "GET" }, token);
    },
    refetchInterval: 6000,
  });

  const formatCurrency = (amountMinor: number = 0) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amountMinor / 100);
  };

  if (isLoading && !data) {
    return <TablePageSkeleton title="Payments Directory" subtitle="Ingested payment transactions and status history" columns={7} />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Payments Directory</h2>
          <p className="text-xs text-slate-400 mt-1">Ingested payment transactions and status history</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 rounded-xl px-3 py-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-slate-900 text-slate-200">All Statuses</option>
              <option value="created" className="bg-slate-900 text-slate-200">Created</option>
              <option value="attempted" className="bg-slate-900 text-slate-200">Attempted</option>
              <option value="failed" className="bg-slate-900 text-slate-200">Failed</option>
              <option value="captured" className="bg-slate-900 text-slate-200">Captured</option>
              <option value="recovered" className="bg-slate-900 text-slate-200">Recovered</option>
            </select>
          </div>
        </div>
      </div>

      {/* Payment List Table (§19) */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Payment ID</th>
                <th className="p-4">External Provider ID</th>
                <th className="p-4">Amount</th>
                <th className="p-4">Status</th>
                <th className="p-4">Failure Reason</th>
                <th className="p-4">Created At</th>
                <th className="p-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={7} className="p-4 h-12 bg-slate-800/20" />
                  </tr>
                ))
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((p: any) => (
                  <tr key={p.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-4">
                      <Link href={`/payments/${p.id}`}>
                        <ShortIdBadge id={p.id} prefix="pay" />
                      </Link>
                    </td>
                    <td className="p-4 font-mono text-slate-400">{p.provider_payment_id || p.external_payment_id || "N/A"}</td>
                    <td className="p-4 font-semibold text-white">{formatCurrency(p.amount_minor)}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                        p.status === "captured" || p.status === "recovered"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : p.status === "failed"
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          : "bg-slate-800 text-slate-300 border border-slate-700"
                      }`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{p.failure_reason || "N/A"}</td>
                    <td className="p-4 text-slate-400">{new Date(p.created_at).toLocaleString("en-IN")}</td>
                    <td className="p-4 text-right">
                      <Link
                        href={`/payments/${p.id}`}
                        className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    No payments found matching filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {data && data.total > 0 && (
          <div className="p-4 bg-slate-900/60 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Showing Page {data.page} of {Math.ceil(data.total / pageSize)} ({data.total} total)</span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= Math.ceil(data.total / pageSize)}
                onClick={() => setPage((prev) => prev + 1)}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
