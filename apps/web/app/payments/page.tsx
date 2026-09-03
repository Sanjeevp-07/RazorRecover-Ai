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
    queryKey: ["payments-list", token, statusFilter, page],
    queryFn: () => {
      let endpoint = `/payments?page=${page}&page_size=${pageSize}`;
      if (statusFilter) {
        endpoint += `&status=${statusFilter}`;
      }
      return fetchApi<PaymentListResponse>(endpoint, { method: "GET" }, token);
    },
    refetchInterval: 4000,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
    enabled: !!token,
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
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Payments Directory</h2>
          <p className="text-xs text-slate-500 font-medium mt-1">Ingested payment transactions and status history</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-xs shadow-2xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="bg-transparent text-slate-700 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-white text-slate-700">All Statuses</option>
              <option value="created" className="bg-white text-slate-700">Created</option>
              <option value="attempted" className="bg-white text-slate-700">Attempted</option>
              <option value="failed" className="bg-white text-slate-700">Failed</option>
              <option value="captured" className="bg-white text-slate-700">Captured</option>
              <option value="recovered" className="bg-white text-slate-700">Recovered</option>
            </select>
          </div>
        </div>
      </div>

      {/* Payment List Table (§19) */}
      <div className="glass-panel rounded-2xl border border-slate-200 bg-white shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
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
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={7} className="p-4 h-12 bg-slate-50" />
                  </tr>
                ))
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((p: any) => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-4 font-mono font-semibold text-blue-600">
                      <Link href={`/payments/${p.id}`}>
                        <ShortIdBadge id={p.id} prefix="pay" />
                      </Link>
                    </td>
                    <td className="p-4 font-mono text-slate-600">{p.provider_payment_id || p.external_payment_id || "N/A"}</td>
                    <td className="p-4 font-extrabold text-slate-900">{formatCurrency(p.amount_minor)}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase border ${
                        p.status === "captured" || p.status === "recovered"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : p.status === "failed"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-slate-100 text-slate-700 border-slate-200"
                      }`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-600">{p.failure_reason || "N/A"}</td>
                    <td className="p-4 text-slate-500 font-medium">{new Date(p.created_at).toLocaleString("en-IN")}</td>
                    <td className="p-4 text-right">
                      <Link
                        href={`/payments/${p.id}`}
                        className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-bold transition-colors"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400 font-medium">
                    No payments found matching filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {data && data.total > 0 && (
          <div className="p-4 bg-slate-50/80 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Showing Page {data.page} of {Math.ceil(data.total / pageSize)} ({data.total} total)</span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                className="p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 disabled:opacity-40 transition-colors shadow-2xs cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= Math.ceil(data.total / pageSize)}
                onClick={() => setPage((prev) => prev + 1)}
                className="p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 disabled:opacity-40 transition-colors shadow-2xs cursor-pointer"
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
