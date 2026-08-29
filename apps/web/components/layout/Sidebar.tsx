"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  CreditCard, 
  RefreshCw, 
  CheckSquare, 
  TrendingUp, 
  Settings,
  ShieldCheck,
  Cpu
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/payments", label: "Payments", icon: CreditCard },
  { href: "/recovery", label: "Recovery Queue", icon: RefreshCw },
  { href: "/simulation", label: "AI Simulator", icon: Cpu },
  { href: "/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/analytics", label: "Analytics", icon: TrendingUp },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 bg-white border-r border-slate-200 flex flex-col z-30 shadow-xs">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-100 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-lg text-slate-900 tracking-tight">RazorRecover</h1>
          <p className="text-[11px] text-blue-600 font-bold uppercase tracking-wider">AI Recovery Agent</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-blue-50/90 text-blue-600 font-semibold border-l-4 border-blue-600 shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-100 text-xs text-slate-400 text-center font-medium">
        v3.0 — Production Ready
      </div>
    </aside>
  );
}
