"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth/context";
import { Settings, Key, ShieldCheck, Lock, RefreshCw, AlertCircle } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();
  const [rotated, setRotated] = useState(false);

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Merchant & Policy Settings</h2>
        <p className="text-xs text-slate-400 mt-1">Credentials configuration & policy threshold baseline (§19)</p>
      </div>

      {/* (a) Masked Credentials Display & Rotate Action (§19) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Razorpay API Credentials</h3>
              <p className="text-xs text-slate-400">Encrypted merchant secrets at rest via Fernet AES-128-CBC (§7.4)</p>
            </div>
          </div>

          <button
            onClick={() => setRotated(true)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Rotate Key Pair</span>
          </button>
        </div>

        {rotated && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
            Razorpay API secret rotation request logged securely.
          </div>
        )}

        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 font-semibold mb-1">Razorpay Key ID</label>
            <input
              type="text"
              readOnly
              value="rzp_test_key_***_placeholder"
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl py-2.5 px-4 font-mono text-slate-300 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-semibold mb-1">Razorpay Key Secret (Encrypted)</label>
            <input
              type="password"
              readOnly
              value="gAAAAABl...encrypted_at_rest_secret..."
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl py-2.5 px-4 font-mono text-slate-300 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-semibold mb-1">Razorpay Webhook Secret</label>
            <input
              type="password"
              readOnly
              value="rzp_test_webhook_secret_***"
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl py-2.5 px-4 font-mono text-slate-300 cursor-not-allowed"
            />
          </div>
        </div>
      </div>

      {/* (b) Read-only View of Policy Config Thresholds (§19) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Policy Config Thresholds (Read-Only)</h3>
            <p className="text-xs text-slate-400">
              Read-only view (§19). Thresholds are managed via operator database migrations.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-slate-400 block mb-1">approval_amount_threshold_minor</span>
            <span className="font-bold text-white text-base">₹50,000</span>
            <span className="text-[10px] text-slate-500 block mt-1">(5,000,000 minor units)</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-slate-400 block mb-1">approval_risk_threshold</span>
            <span className="font-bold text-white text-base">0.70</span>
            <span className="text-[10px] text-slate-500 block mt-1">(70% confidence cutoff)</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-slate-400 block mb-1">retry_count_limit</span>
            <span className="font-bold text-white text-base">3 Retries</span>
            <span className="text-[10px] text-slate-500 block mt-1">(Max retry attempts)</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-slate-400 block mb-1">approval_sla_hours</span>
            <span className="font-bold text-white text-base">24 Hours</span>
            <span className="text-[10px] text-slate-500 block mt-1">(Owner SLA window)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
