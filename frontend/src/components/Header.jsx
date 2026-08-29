import React from "react";
import { ShieldCheck, Sparkles, Building2, Bell } from "lucide-react";

export default function Header({ title, subtitle }) {
  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shadow-xs no-print">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <span>{title}</span>
        </h1>
        {subtitle && <p className="text-xs font-medium text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Department Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-900 rounded-full border border-blue-200/80 text-xs font-semibold">
          <Building2 className="w-3.5 h-3.5 text-blue-700" />
          <span>Govt of India — Legal Metrology</span>
        </div>

        {/* Demo Indicator */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 text-amber-800 rounded-full border border-amber-300 text-xs font-bold shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-amber-600" />
          <span>DEMO MODE ACTIVE</span>
        </div>

        <button className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 relative transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full"></span>
        </button>
      </div>
    </header>
  );
}
