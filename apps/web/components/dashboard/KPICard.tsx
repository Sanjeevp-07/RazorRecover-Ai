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
    iconBg: "bg-rose-50 text-rose-600 border-rose-200",
    border: "hover:border-rose-300",
  },
  indigo: {
    iconBg: "bg-blue-50 text-blue-600 border-blue-200",
    border: "hover:border-blue-300",
  },
  emerald: {
    iconBg: "bg-emerald-50 text-emerald-600 border-emerald-200",
    border: "hover:border-emerald-300",
  },
  amber: {
    iconBg: "bg-amber-50 text-amber-600 border-amber-200",
    border: "hover:border-amber-300",
  },
  violet: {
    iconBg: "bg-violet-50 text-violet-600 border-violet-200",
    border: "hover:border-violet-300",
  },
};

export function KPICard({ title, value, subtitle, icon: Icon, color }: KPICardProps) {
  const styles = COLOR_MAPS[color];

  return (
    <div className={`glass-card p-5 rounded-2xl ${styles.border} flex flex-col justify-between shadow-xs bg-white`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${styles.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div>
        <div className="text-xl font-extrabold text-slate-900 tracking-tight">{value}</div>
        {subtitle && <p className="text-[11px] text-slate-500 mt-1 font-medium">{subtitle}</p>}
      </div>
    </div>
  );
}
