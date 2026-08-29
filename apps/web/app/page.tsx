"use client";

import Link from "next/link";
import { 
  ShieldCheck, 
  ArrowRight, 
  TrendingUp, 
  RefreshCw, 
  CheckSquare, 
  Zap, 
  Sparkles, 
  Brain, 
  Lock, 
  Layers, 
  Activity, 
  CheckCircle2, 
  CreditCard 
} from "lucide-react";
import { useAuth } from "@/lib/auth/context";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="space-y-8 max-w-6xl mx-auto animate-fade-in">
      {/* Hero Welcome Banner */}
      <div className="glass-panel p-8 sm:p-10 rounded-3xl border border-blue-200 bg-gradient-to-r from-blue-50/80 via-white to-emerald-50/40 shadow-sm relative overflow-hidden space-y-6">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>AI Revenue Recovery Platform v3.0</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Welcome to <span className="text-blue-600">RazorRecover AI</span>
          </h1>

          <p className="text-sm text-slate-600 leading-relaxed font-medium">
            Autonomous revenue recovery & smart dunning platform engineered for Razorpay merchants. Automatically detect payment failures, evaluate LLM AI recovery treatments, and execute context-aware outreach with 100% deterministic safety guardrails.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              href="/dashboard"
              className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-blue-600/20 cursor-pointer"
            >
              <span>Go to Merchant Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/recovery"
              className="px-5 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs border border-slate-200 flex items-center gap-2 transition-all shadow-2xs cursor-pointer"
            >
              <RefreshCw className="w-4 h-4 text-blue-600" />
              <span>Inspect Recovery Queue</span>
            </Link>

            <Link
              href="/approvals"
              className="px-5 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs border border-slate-200 flex items-center gap-2 transition-all shadow-2xs cursor-pointer"
            >
              <CheckSquare className="w-4 h-4 text-amber-600" />
              <span>Pending Approvals</span>
            </Link>
          </div>
        </div>

        {/* Right Graphic / Live Badge */}
        <div className="hidden lg:block absolute right-8 top-1/2 -translate-y-1/2 space-y-3">
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-md w-64 space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500">
              <span>SYSTEM STATUS</span>
              <span className="flex items-center gap-1 text-emerald-600 text-[10px] font-extrabold uppercase">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                100% Operational
              </span>
            </div>
            <div className="text-xl font-extrabold text-slate-900">₹4,85,200</div>
            <div className="text-[11px] text-emerald-600 font-bold flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>+24.6% Incremental Lift Recovered</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Platform Architecture Health Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase text-slate-500">AI Intelligence Engine</span>
            <div className="p-2 rounded-xl bg-blue-50 text-blue-600 border border-blue-200">
              <Brain className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900">Hybrid NIM & LLM</div>
          <p className="text-[11px] text-slate-500 font-medium">Context-aware treatment selection & baseline fallback</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase text-slate-500">Safety Guardrails</span>
            <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900">Policy Engine v3</div>
          <p className="text-[11px] text-slate-500 font-medium">9-rule top-to-bottom ordered safety evaluation</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase text-slate-500">Database & Auth</span>
            <div className="p-2 rounded-xl bg-violet-50 text-violet-600 border border-violet-200">
              <Lock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900">Supabase Cloud</div>
          <p className="text-[11px] text-slate-500 font-medium">PostgreSQL & Google OAuth SSO integrated</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase text-slate-500">Causal Lift Metric</span>
            <div className="p-2 rounded-xl bg-amber-50 text-amber-600 border border-amber-200">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900">Holdout Experiment</div>
          <p className="text-[11px] text-slate-500 font-medium">Science-backed net incremental revenue measurement</p>
        </div>
      </div>

      {/* Feature Capabilities Showcase */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-200 bg-white shadow-xs space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Core Platform Capabilities</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Automated end-to-end payment recovery workflow for Razorpay</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
              <CreditCard className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">1. Instant Webhook Ingestion</h3>
            <p className="text-xs text-slate-600 font-medium leading-relaxed">
              Ingests failed Razorpay webhooks (`payment.failed`) with HMAC-SHA256 verification and failure classification.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <Brain className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">2. AI & Policy Evaluation</h3>
            <p className="text-xs text-slate-600 font-medium leading-relaxed">
              Evaluates risk signals, velocity flags, customer history, and 9 policy rules to output plain-English rationales.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
              <CheckSquare className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">3. Autonomous & Human Actions</h3>
            <p className="text-xs text-slate-600 font-medium leading-relaxed">
              Executes smart payment link retries automatically or escalates high-value cases (&gt; ₹50,000) for owner approval.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
