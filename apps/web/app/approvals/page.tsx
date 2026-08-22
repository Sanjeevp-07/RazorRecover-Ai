"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { CheckSquare, CheckCircle2, XCircle, Clock, AlertCircle } from "lucide-react";

export default function ApprovalsPage() {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: approvals, isLoading } = useQuery<any[]>({
    queryKey: ["approvals-list"],
    queryFn: () => fetchApi<any>("/recovery-cases?status=PENDING_APPROVAL", { method: "GET" }, token).then(res => res.items || []),
  });

  const approveMutation = useMutation({
    mutationFn: (caseId: string) => fetchApi(`/recovery-cases/${caseId}/approve`, { method: "POST" }, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["approvals-list"] }),
    onError: (err: any) => setActionError(err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: (caseId: string) => fetchApi(`/recovery-cases/${caseId}/reject`, { method: "POST" }, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["approvals-list"] }),
    onError: (err: any) => setActionError(err.message),
  });

  const isOwner = user?.role?.toLowerCase() === "owner" || user?.role?.toLowerCase() === "admin";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Pending Approvals Queue</h2>
        <p className="text-xs text-slate-400 mt-1">Cases escalated for human owner authorization (§15 & §19)</p>
      </div>

      {actionError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{actionError}</span>
        </div>
      )}

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Case ID</th>
                <th className="p-4">Payment ID</th>
                <th className="p-4">Escalated At</th>
                <th className="p-4">SLA Expiry (24h)</th>
                <th className="p-4 text-right">Owner Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={5} className="p-4 h-12 bg-slate-800/20" />
                  </tr>
                ))
              ) : approvals && approvals.length > 0 ? (
                approvals.map((app: any) => (
                  <tr key={app.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-4 font-mono text-indigo-300">
                      <Link href={`/recovery/${app.id}`} className="hover:underline">
                        {app.id.substring(0, 8)}...
                      </Link>
                    </td>
                    <td className="p-4 font-mono text-slate-400">{app.payment_id.substring(0, 8)}...</td>
                    <td className="p-4 text-slate-400">{new Date(app.created_at).toLocaleString("en-IN")}</td>
                    <td className="p-4">
                      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 w-fit">
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
                            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1 transition-colors"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => rejectMutation.mutate(app.id)}
                            disabled={rejectMutation.isPending}
                            className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold flex items-center gap-1 transition-colors"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">Owner Role Required</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
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
