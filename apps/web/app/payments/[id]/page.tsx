"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/context";
import Link from "next/link";
import { ArrowLeft, CreditCard, ShieldCheck, Clock, ExternalLink } from "lucide-react";

import { Skeleton } from "@/components/ui/Skeleton";
import { ShortIdBadge } from "@/components/ui/ShortIdBadge";

export default function PaymentDetailPage({ params }: { params: { id: string } }) {
  const { token } = useAuth();
  const paymentId = params.id;

  const { data: payment, isLoading } = useQuery<any>({
    queryKey: ["payment-detail", paymentId],
    queryFn: () => fetchApi<any>(`/payments/${paymentId}`, { method: "GET" }, token),
    refetchInterval: 4000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl animate-fade-in">
        <Skeleton className="h-4 w-32" />
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-60" />
          <Skeleton className="h-7 w-24 rounded-full" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-72 w-full rounded-2xl bg-white border border-slate-200" />
          <Skeleton className="h-72 w-full rounded-2xl bg-white border border-slate-200" />
        </div>
      </div>
    );
  }

  if (!payment) {
    return <div className="p-8 text-rose-600 font-bold">Payment not found.</div>;
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
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-blue-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Payments</span>
      </Link>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Payment Details</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-slate-500 font-medium">Payment ID:</span>
            <ShortIdBadge id={payment.id} prefix="pay" />
          </div>
        </div>
        <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase border ${
          payment.status === "captured" || payment.status === "recovered"
            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
            : "bg-rose-50 text-rose-700 border-rose-200"
        }`}>
          {payment.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Provider Fields Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-200 bg-white shadow-xs space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-blue-600" />
            <span>Provider Transaction Fields</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Amount</span>
              <span className="font-extrabold text-slate-900 text-sm">{formatCurrency(payment.amount_minor)}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">External Provider ID</span>
              <span className="font-mono font-bold text-slate-700">{payment.external_payment_id}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Currency</span>
              <span className="font-semibold text-slate-800">{payment.currency}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Payment Method</span>
              <span className="font-semibold text-slate-800">{payment.method || "N/A"}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Failure Reason</span>
              <span className="text-rose-600 font-bold">{payment.failure_reason || "None"}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500 font-medium">Ingested At</span>
              <span className="text-slate-700 font-medium">{new Date(payment.created_at).toLocaleString("en-IN")}</span>
            </div>
          </div>
        </div>

        {/* Linked Case Card */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-200 bg-white shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Linked Recovery Case</span>
            </h3>

            {payment.recovery_case ? (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Case ID</span>
                  <span className="font-mono font-bold text-blue-600">{payment.recovery_case.id}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Case Status</span>
                  <span className="font-extrabold text-amber-700">{payment.recovery_case.status}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-500 font-medium">Correlation ID</span>
                  <span className="font-mono text-slate-500 text-[10px]">{payment.recovery_case.correlation_id}</span>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-slate-400 text-xs font-medium">
                No active recovery case linked to this payment.
              </div>
            )}
          </div>

          {payment.recovery_case && (
            <Link
              href={`/recovery/${payment.recovery_case.id}`}
              className="mt-6 w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center justify-center gap-2 transition-colors shadow-sm"
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
