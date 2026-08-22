"use client";

import { useAuth } from "@/lib/auth/context";
import { LogOut, User, Lock } from "lucide-react";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-full border border-slate-700/50">
        <Lock className="w-3.5 h-3.5 text-emerald-400" />
        <span>Environment: <strong className="text-white">Razorpay Test Mode</strong></span>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-xs">
              <User className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-200 font-medium">{user.email}</span>
              <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold uppercase text-[10px]">
                {user.role}
              </span>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="text-xs font-medium px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
          >
            Login
          </a>
        )}
      </div>
    </header>
  );
}
