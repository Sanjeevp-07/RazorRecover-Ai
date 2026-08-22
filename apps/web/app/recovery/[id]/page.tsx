"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { 
  ArrowLeft, 
  Brain, 
  ShieldCheck, 
  Zap, 
  Activity, 
  Clock, 
  CheckCircle2, 
  XCircle,
  AlertTriangle
} from "lucide-react";

export default function CaseDecisionChainPage({ params }: { params: { id: string } }) {
  const { token } = useAuth();
  const caseId = params.id;
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  // Fetch complete case detail with decision chain (§19)
  const { data: caseData, isLoading } = useQuery<any>({
    queryKey: ["recovery-case-detail", caseId],
    queryFn: () => fetchApi<any>(`/recovery-cases/${caseId}`, { method: "GET" }, token),
  });

  // Fetch audit timeline (§19)
  const { data: timeline } = useQuery<any[]>({
    queryKey: ["recovery-case-timeline", caseId],
    queryFn: () => fetchApi<any[]>(`/recovery-cases/${caseId}/timeline`, { method: "GET" }, token),
  });

  // Approve Mutation (§19)
  const approveMutation = useMutation({
    mutationFn: () => fetchApi(`/recovery-cases/${caseId}/approve`, { method: "POST" }, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recovery-case-detail", caseId] });
      queryClient.invalidateQueries({ queryKey: ["recovery-case-timeline", caseId] });
    },
    onError: (err: any) => setActionError(err.message),
  });

  // Reject Mutation (§19)
  const rejectMutation = useMutation({
    mutationFn: () => fetchApi(`/recovery-cases/${caseId}/reject`, { method: "POST" }, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recovery-case-detail", caseId] });
      queryClient.invalidateQueries({ queryKey: ["recovery-case-timeline", caseId] });
    },
    onError: (err: any) => setActionError(err.message),
  });

  if (isLoading) {
    return <div className="p-8 text-slate-400">Loading recovery decision chain...</div>;
  }

  if (!caseData) {
    return <div className="p-8 text-rose-400">Recovery case not found.</div>;
  }

  const isPendingApproval = caseData.status === "PENDING_APPROVAL";

  return (
    <div className="space-y-8 max-w-6xl">
      <Link
        href="/recovery"
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Recovery Queue</span>
      </Link>

      {/* Case Overview Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-white tracking-tight">Recovery Decision Chain</h2>
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-slate-800 text-indigo-400 border border-slate-700">
              {caseData.status}
            </span>
          </div>
          <p className="font-mono text-xs text-slate-400 mt-1">Case ID: {caseData.id}</p>
        </div>

        {/* Approve / Reject Actions on /recovery/[id] (§19) */}
        {isPendingApproval && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Action</span>
            </button>

            <button
              onClick={() => rejectMutation.mutate()}
              disabled={rejectMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-all shadow-lg shadow-rose-600/20 disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" />
              <span>Reject Action</span>
            </button>
          </div>
        )}
      </div>

      {actionError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Decision Chain Grid (§19) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 1. Risk Signals Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>1. Risk Signals</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Retry Count</span>
              <span className="font-bold text-white">{caseData.risk_signal?.retry_count ?? 1}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Customer Score</span>
              <span className="font-bold text-emerald-400">{caseData.risk_signal?.customer_history_score ?? 0.85}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Velocity Flag</span>
              <span className="font-semibold text-slate-300">
                {caseData.risk_signal?.velocity_flag ? "TRUE" : "FALSE"}
              </span>
            </div>
          </div>
        </div>

        {/* 2. AI Decision Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Brain className="w-4 h-4 text-indigo-400" />
            <span>2. AI Recommendation</span>
          </h3>

          {caseData.ai_decision ? (
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Recommended Action</span>
                <span className="font-bold text-indigo-300">
                  {caseData.ai_decision.validated_output?.recommended_action || "ESCALATE_CASE"}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Confidence</span>
                <span className="font-bold text-white">
                  {((caseData.ai_decision.validated_output?.confidence || 0) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Schema Valid</span>
                <span className="font-bold text-emerald-400">
                  {caseData.ai_decision.is_valid ? "TRUE" : "FALSE (Fail-Closed)"}
                </span>
              </div>
              <div className="py-2">
                <span className="text-slate-400 block mb-1">AI Rationale</span>
                <p className="text-slate-300 italic bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                  "{caseData.ai_decision.validated_output?.reason || "Escalated for safety"}"
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-4">AI analysis pending.</p>
          )}
        </div>

        {/* 3. Policy Decision Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>3. Policy Decision</span>
          </h3>

          {caseData.policy_decision ? (
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Policy Outcome</span>
                <span className="font-bold text-emerald-400 uppercase">
                  {caseData.policy_decision.decision}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Matched Rule</span>
                <span className="font-mono text-indigo-300">
                  {caseData.policy_decision.matched_rule}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-400">Policy Version</span>
                <span className="font-mono text-slate-400">
                  v{caseData.policy_decision.policy_version}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-4">Policy evaluation pending.</p>
          )}
        </div>
      </div>

      {/* Ordered Audit Timeline (§19) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" />
          <span>Audit Trail Timeline</span>
        </h3>

        <div className="space-y-3">
          {timeline && timeline.length > 0 ? (
            timeline.map((item, idx) => (
              <div key={idx} className="flex items-start gap-4 text-xs p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <span className="font-mono text-indigo-400 font-semibold">{item.event_type}</span>
                <span className="text-slate-400 flex-1">{JSON.stringify(item.payload)}</span>
                <span className="text-slate-500">{new Date(item.created_at).toLocaleTimeString("en-IN")}</span>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500">No audit timeline entries recorded.</p>
          )}
        </div>
      </div>
    </div>
  );
}
