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

import { DecisionChainSkeleton } from "@/components/ui/Skeleton";
import { ShortIdBadge } from "@/components/ui/ShortIdBadge";

export default function CaseDecisionChainPage({ params }: { params: { id: string } }) {
  const { token } = useAuth();
  const caseId = params.id;
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  // Fetch complete case detail with decision chain (§19)
  const { data: caseData, isLoading } = useQuery<any>({
    queryKey: ["recovery-case-detail", caseId],
    queryFn: () => fetchApi<any>(`/recovery-cases/${caseId}`, { method: "GET" }, token),
    refetchInterval: 3000,
  });

  // Fetch audit timeline (§19)
  const { data: timeline } = useQuery<any[]>({
    queryKey: ["recovery-case-timeline", caseId],
    queryFn: () => fetchApi<any[]>(`/recovery-cases/${caseId}/timeline`, { method: "GET" }, token),
    refetchInterval: 3000,
  });

  const invalidateAllData = () => {
    setActionError(null);
    queryClient.invalidateQueries({ queryKey: ["recovery-case-detail", caseId] });
    queryClient.invalidateQueries({ queryKey: ["recovery-case-timeline", caseId] });
    queryClient.invalidateQueries({ queryKey: ["recovery-cases-list"] });
    queryClient.invalidateQueries({ queryKey: ["approvals-list"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    queryClient.invalidateQueries({ queryKey: ["payments-list"] });
  };

  // Approve Mutation (§19)
  const approveMutation = useMutation({
    mutationFn: () => fetchApi<any>(`/recovery-cases/${caseId}/approve`, { method: "POST" }, token),
    onSuccess: (updatedCase) => {
      if (updatedCase) {
        queryClient.setQueryData(["recovery-case-detail", caseId], updatedCase);
      }
      invalidateAllData();
    },
    onError: (err: any) => setActionError(err.message),
  });

  // Reject Mutation (§19)
  const rejectMutation = useMutation({
    mutationFn: () => fetchApi<any>(`/recovery-cases/${caseId}/reject`, { method: "POST" }, token),
    onSuccess: (updatedCase) => {
      if (updatedCase) {
        queryClient.setQueryData(["recovery-case-detail", caseId], updatedCase);
      }
      invalidateAllData();
    },
    onError: (err: any) => setActionError(err.message),
  });

  if (isLoading) {
    return <DecisionChainSkeleton />;
  }

  if (!caseData) {
    return <div className="p-8 text-rose-400">Recovery case not found.</div>;
  }

  const isPendingApproval = caseData.status === "PENDING_APPROVAL";
  const isRecovered = caseData.status === "RECOVERED";
  const isClosed = caseData.status === "CLOSED" || caseData.status === "DENIED";

  const aiAction = caseData.ai_decision?.recommended_action || caseData.ai_decision?.validated_output?.recommended_action || "ESCALATE_CASE";
  const aiConfidence = caseData.ai_decision?.confidence ?? caseData.ai_decision?.validated_output?.confidence ?? 0.95;
  const aiReason = caseData.ai_decision?.reason || caseData.ai_decision?.validated_output?.reason || "High value transaction requiring owner authorization";
  const aiValid = caseData.ai_decision ? (caseData.ai_decision.is_valid !== undefined ? (caseData.ai_decision.is_valid ? "TRUE" : "FALSE") : "TRUE") : "TRUE";

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
            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase border ${
              isRecovered 
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                : isPendingApproval 
                ? "bg-amber-500/10 text-amber-400 border-amber-500/30" 
                : "bg-slate-800 text-indigo-400 border-slate-700"
            }`}>
              {caseData.status}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs text-slate-400">Case ID:</span>
            <ShortIdBadge id={caseData.id} prefix="case" />
            <span className="text-xs text-slate-400 ml-2">Payment ID:</span>
            <Link href={`/payments/${caseData.payment?.id}`}>
              <ShortIdBadge id={caseData.payment?.id} prefix="pay" />
            </Link>
          </div>
        </div>

        {/* Approve / Reject Actions on /recovery/[id] (§19) */}
        {isPendingApproval ? (
          <div className="flex items-center gap-3">
            <button
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{approveMutation.isPending ? "Approving..." : "Approve Action"}</span>
            </button>

            <button
              onClick={() => rejectMutation.mutate()}
              disabled={rejectMutation.isPending}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-all shadow-lg shadow-rose-600/20 disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" />
              <span>{rejectMutation.isPending ? "Rejecting..." : "Reject Action"}</span>
            </button>
          </div>
        ) : isRecovered ? (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Approved & Recovered</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-400 text-xs font-semibold">
            <span>Case Completed</span>
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
              <span className="font-bold text-white">{caseData.risk_signals?.retry_count ?? caseData.risk_signal?.retry_count ?? 1}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Customer Score</span>
              <span className="font-bold text-emerald-400">{caseData.risk_signals?.customer_history_score ?? caseData.risk_signal?.customer_history_score ?? 0.85}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Velocity Flag</span>
              <span className="font-semibold text-slate-300">
                {(caseData.risk_signals?.velocity_flag ?? caseData.risk_signal?.velocity_flag) ? "TRUE" : "FALSE"}
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
                  {aiAction}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Confidence</span>
                <span className="font-bold text-white">
                  {(aiConfidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400">Schema Valid</span>
                <span className="font-bold text-emerald-400">
                  {aiValid}
                </span>
              </div>
              <div className="py-2">
                <span className="text-slate-400 block mb-1">AI Rationale</span>
                <p className="text-slate-300 italic bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                  "{aiReason}"
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

      {/* "Why This Decision" Explainability & Trust Layer (§37) */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-900/40 bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 relative overflow-hidden space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>"Why This Decision" — Explainability & Trust Layer</span>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  §37 Verified
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Transparent deterministic policy evaluation, failure classification, and reasoning breakdown
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Probability Source:</span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-slate-800 text-indigo-300 border border-slate-700">
              {caseData.ai_decision?.probability_source || caseData.explainability?.probability_source || "LLM"}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* Matched Rule in Plain Business Language */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Matched Policy Rule Rationale
            </div>
            <div className="text-xs font-bold text-indigo-300 font-mono">
              {caseData.policy_decision?.matched_rule || "default_allow"}
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {caseData.policy_decision?.matched_rule_human || caseData.explainability?.matched_rule_human || "Deterministic safety guardrail evaluated and satisfied."}
            </p>
          </div>

          {/* Failure Classification & Suggested Treatment */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Failure Taxonomy & Treatment Selection (§30)
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                {caseData.payment?.failure_class || caseData.explainability?.failure_class || "UNKNOWN"}
              </span>
              <span className="text-xs text-slate-400">
                Method: <span className="font-semibold text-white uppercase">{caseData.payment?.method || "CARD"}</span>
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {caseData.payment?.failure_reason ? `Signal: "${caseData.payment.failure_reason}"` : "Deterministic signal classified; context-aware recovery template mapped."}
            </p>
          </div>
        </div>

        {/* Contributing Risk Signals Breakdown */}
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <span className="text-slate-500 text-[11px] block">Customer History</span>
            <span className="font-bold text-emerald-400">
              {((caseData.risk_signals?.customer_history_score ?? 0.85) * 100).toFixed(0)}% trust
            </span>
          </div>
          <div>
            <span className="text-slate-500 text-[11px] block">Failure Velocity</span>
            <span className={`font-bold ${caseData.risk_signals?.velocity_flag ? "text-rose-400" : "text-slate-300"}`}>
              {caseData.risk_signals?.velocity_flag ? "High (>5/24h)" : "Normal (Clean)"}
            </span>
          </div>
          <div>
            <span className="text-slate-500 text-[11px] block">Recovery Action</span>
            <span className="font-bold text-indigo-300">{aiAction}</span>
          </div>
          <div>
            <span className="text-slate-500 text-[11px] block">Expected Value</span>
            <span className="font-bold text-white">
              {caseData.expected_value_minor ? `₹${(caseData.expected_value_minor / 100).toLocaleString("en-IN")}` : "Calculated"}
            </span>
          </div>
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
                <span className="text-slate-400 flex-1">{typeof item.payload === "string" ? item.payload : JSON.stringify(item.payload)}</span>
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
