import { LucideIcon } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  color: "rose" | "indigo" | "emerald" | "amber" | "violet";
}

const COLOR_MAPS = {
  rose: {
    iconBg: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    border: "hover:border-rose-500/30",
  },
  indigo: {
    iconBg: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    border: "hover:border-indigo-500/30",
  },
  emerald: {
    iconBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    border: "hover:border-emerald-500/30",
  },
  amber: {
    iconBg: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    border: "hover:border-amber-500/30",
  },
  violet: {
    iconBg: "bg-violet-500/10 text-violet-400 border-violet-500/20",
    border: "hover:border-violet-500/30",
  },
};

export function KPICard({ title, value, subtitle, icon: Icon, color }: KPICardProps) {
  const styles = COLOR_MAPS[color];

  return (
    <div className={`glass-card p-6 rounded-2xl ${styles.border} flex flex-col justify-between`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${styles.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div>
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}
