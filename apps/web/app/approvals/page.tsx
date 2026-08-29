"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { CheckSquare, CheckCircle2, XCircle, Clock, AlertCircle } from "lucide-react";
import { TablePageSkeleton } from "@/components/ui/Skeleton";
import { ShortIdBadge } from "@/components/ui/ShortIdBadge";

export default function ApprovalsPage() {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: approvals, isLoading } = useQuery<any[]>({
    queryKey: ["approvals-list"],
    queryFn: () => fetchApi<any>("/recovery-cases?status=PENDING_APPROVAL", { method: "GET" }, token).then(res => res.items || []),
    refetchInterval: 6000,
  });

  const invalidateAll = () => {
    setActionError(null);
    queryClient.invalidateQueries({ queryKey: ["approvals-list"] });
    queryClient.invalidateQueries({ queryKey: ["recovery-cases-list"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    queryClient.invalidateQueries({ queryKey: ["payments-list"] });
  };

  const approveMutation = useMutation({
    mutationFn: (caseId: string) => fetchApi(`/recovery-cases/${caseId}/approve`, { method: "POST" }, token),
    onSuccess: () => invalidateAll(),
    onError: (err: any) => setActionError(err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: (caseId: string) => fetchApi(`/recovery-cases/${caseId}/reject`, { method: "POST" }, token),
    onSuccess: () => invalidateAll(),
    onError: (err: any) => setActionError(err.message),
  });

  const isOwner = user?.role?.toLowerCase() === "owner" || user?.role?.toLowerCase() === "admin";

  if (isLoading && !approvals) {
    return <TablePageSkeleton title="Pending Approvals Queue" subtitle="Cases escalated for human owner authorization (§15 & §19)" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Pending Approvals Queue</h2>
        <p className="text-xs text-slate-500 font-medium mt-1">Cases escalated for human owner authorization (§15 & §19)</p>
      </div>

      {actionError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      <div className="glass-panel rounded-2xl border border-slate-200 bg-white shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="p-4">Case ID</th>
                <th className="p-4">Payment ID</th>
                <th className="p-4">Escalated At</th>
                <th className="p-4">SLA Expiry (24h)</th>
                <th className="p-4 text-right">Owner Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={5} className="p-4 h-12 bg-slate-50" />
                  </tr>
                ))
              ) : approvals && approvals.length > 0 ? (
                approvals.map((app: any) => (
                  <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-4 font-mono font-semibold text-blue-600">
                      <Link href={`/recovery/${app.id}`}>
                        <ShortIdBadge id={app.id} prefix="case" />
                      </Link>
                    </td>
                    <td className="p-4 font-mono text-slate-600">
                      <Link href={`/payments/${app.payment_id}`}>
                        <ShortIdBadge id={app.payment_id} prefix="pay" />
                      </Link>
                    </td>
                    <td className="p-4 text-slate-500 font-medium">{new Date(app.created_at).toLocaleString("en-IN")}</td>
                    <td className="p-4">
                      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 w-fit">
                        <Clock className="w-3 h-3" />
                        <span>SLA Active</span>
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      {isOwner ? (
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => approveMutation.mutate(app.id)}
                            disabled={approveMutation.isPending}
                            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold flex items-center gap-1 transition-colors shadow-2xs cursor-pointer"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => rejectMutation.mutate(app.id)}
                            disabled={rejectMutation.isPending}
                            className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold flex items-center gap-1 transition-colors shadow-2xs cursor-pointer"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">Owner Role Required</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-400 font-medium">
                    No pending approval requests.
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
