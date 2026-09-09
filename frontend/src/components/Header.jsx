import React from "react";
import { Sparkles, Building2, Bell } from "lucide-react";

export default function Header({ currentUser, title, subtitle }) {
  const isManufacturer = currentUser?.role === "MANUFACTURER";
  const orgName = currentUser?.organization || (isManufacturer ? "Packaging Manufacturer" : "Govt of India — Legal Metrology");

  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shadow-xs no-print">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <span>{title}</span>
        </h1>
        {subtitle && <p className="text-xs font-medium text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Organization / Department Badge */}
        <div className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${
          isManufacturer
            ? "bg-amber-50 text-amber-900 border-amber-200"
            : "bg-blue-50 text-blue-900 border-blue-200/80"
        }`}>
          <Building2 className={`w-3.5 h-3.5 ${isManufacturer ? "text-amber-700" : "text-blue-700"}`} />
          <span>{orgName}</span>
        </div>

        {/* Role Pill */}
        <div className={`hidden sm:inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-bold ${
          isManufacturer
            ? "bg-amber-100/80 text-amber-900 border-amber-300"
            : "bg-blue-100/80 text-blue-900 border-blue-300"
        }`}>
          {isManufacturer ? "MANUFACTURER" : "INSPECTOR"}
        </div>

        {/* Demo Indicator */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-700 rounded-full border border-slate-300 text-xs font-bold shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-amber-600" />
          <span>DEMO MODE</span>
        </div>

        <button className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 relative transition-colors cursor-pointer">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full"></span>
        </button>
      </div>
    </header>
  );
}

