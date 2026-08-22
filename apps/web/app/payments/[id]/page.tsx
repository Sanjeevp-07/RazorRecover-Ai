"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { ArrowLeft, CreditCard, ShieldCheck, Clock, ExternalLink } from "lucide-react";

export default function PaymentDetailPage({ params }: { params: { id: string } }) {
  const { token } = useAuth();
  const paymentId = params.id;

  const { data: payment, isLoading } = useQuery<any>({
    queryKey: ["payment-detail", paymentId],
    queryFn: () => fetchApi<any>(`/payments/${paymentId}`, { method: "GET" }, token),
  });

  if (isLoading) {
    return <div className="p-8 text-slate-400">Loading payment details...</div>;
  }

  if (!payment) {
    return <div className="p-8 text-rose-400">Payment not found.</div>;
  }

  const formatCurrency = (amountMinor: number = 0) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(amountMinor / 100);
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <Link
        href="/payments"
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Payments</span>
      </Link>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Payment Details</h2>
          <p className="font-mono text-xs text-indigo-400 mt-1">ID: {payment.id}</p>
        </div>
        <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase ${
          payment.status === "captured" || payment.status === "recovered"
            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
        }`}>
          {payment.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Provider Fields Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-indigo-400" />
            <span>Provider Transaction Fields</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Amount</span>
              <span className="font-bold text-white text-sm">{formatCurrency(payment.amount_minor)}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">External Provider ID</span>
              <span className="font-mono text-slate-200">{payment.external_payment_id}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Currency</span>
              <span className="font-semibold text-slate-200">{payment.currency}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Payment Method</span>
              <span className="font-semibold text-slate-200">{payment.method || "N/A"}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Failure Reason</span>
              <span className="text-rose-400 font-medium">{payment.failure_reason || "None"}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Ingested At</span>
              <span className="text-slate-300">{new Date(payment.created_at).toLocaleString("en-IN")}</span>
            </div>
          </div>
        </div>

        {/* Linked Case Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Linked Recovery Case</span>
            </h3>

            {payment.recovery_case ? (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Case ID</span>
                  <span className="font-mono text-indigo-300">{payment.recovery_case.id}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Case Status</span>
                  <span className="font-bold text-amber-400">{payment.recovery_case.status}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-400">Correlation ID</span>
                  <span className="font-mono text-slate-400 text-[10px]">{payment.recovery_case.correlation_id}</span>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-slate-500 text-xs">
                No active recovery case linked to this payment.
              </div>
            )}
          </div>

          {payment.recovery_case && (
            <Link
              href={`/recovery/${payment.recovery_case.id}`}
              className="mt-6 w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <span>Inspect Recovery Case Chain</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
