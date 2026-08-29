"use client";

import { useAuth } from "@/lib/auth/context";
import { LogOut, User, Lock } from "lucide-react";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
        <Lock className="w-3.5 h-3.5 text-emerald-600" />
        <span>Environment: <strong className="text-emerald-950 font-bold">Razorpay Test Mode</strong></span>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs shadow-2xs">
              <User className="w-4 h-4 text-blue-600" />
              <span className="text-slate-800 font-semibold">{user.email}</span>
              <span className="px-2 py-0.5 rounded-md bg-blue-100 text-blue-700 font-bold uppercase text-[10px]">
                {user.role}
              </span>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors cursor-pointer"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="text-xs font-bold px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-sm"
          >
            Login
          </a>
        )}
      </div>
    </header>
  );
}
