import React from "react";
import {
  LayoutDashboard,
  PlusCircle,
  History,
  FileSpreadsheet,
  Settings,
  Scale,
  LogOut,
} from "lucide-react";

export default function Sidebar({ currentUser, currentPage, setCurrentPage, onLogout }) {
  const isManufacturer = currentUser?.role === "MANUFACTURER";

  const navItems = isManufacturer
    ? [
        { id: "dashboard", label: "Portal Overview", icon: LayoutDashboard },
        { id: "new_inspection", label: "Pre-Market Check", icon: PlusCircle },
        { id: "history", label: "Screening History", icon: History },
        { id: "reports", label: "Audit Reports", icon: FileSpreadsheet },
      ]
    : [
        { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
        { id: "new_inspection", label: "New Inspection", icon: PlusCircle },
        { id: "history", label: "Inspection History", icon: History },
        { id: "reports", label: "Reports", icon: FileSpreadsheet },
      ];

  const displayName = currentUser?.full_name || (isManufacturer ? "Manufacturer QA" : "Insp. Vikram Singh");
  const displayRole = currentUser?.role || (isManufacturer ? "MANUFACTURER" : "INSPECTOR");
  const displayOrg = currentUser?.organization || (isManufacturer ? "Packaging Division" : "Legal Metrology Dept");
  const initials = isManufacturer ? "MF" : "LM";

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col h-screen sticky top-0 border-r border-slate-800 shadow-xl no-print">
      {/* Header Brand */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3 bg-slate-950/60">
        <div className={`p-2 rounded-xl border shadow-inner ${
          isManufacturer
            ? "bg-amber-950/60 text-amber-400 border-amber-700/50"
            : "bg-blue-900/60 text-amber-400 border-blue-700/50"
        }`}>
          <Scale className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-sm text-white tracking-wide uppercase">Legal Metrology</h1>
          <p className="text-[11px] text-slate-400 font-medium">
            {isManufacturer ? "Manufacturer Self-Audit" : "Compliance Portal (SIH26034)"}
          </p>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 py-6 px-3 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          {isManufacturer ? "Self-Audit Menu" : "Main Menu"}
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer ${
                isActive
                  ? isManufacturer
                    ? "bg-amber-600 text-white shadow-md shadow-amber-950/40"
                    : "bg-blue-600 text-white shadow-md shadow-blue-900/30"
                  : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Footer Navigation (Settings & User Profile) */}
      <div className="p-3 border-t border-slate-800 space-y-1 bg-slate-950/40">
        <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          {isManufacturer ? "Account & System" : "System & Officer"}
        </div>
        <button
          onClick={() => setCurrentPage("settings")}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
            currentPage === "settings"
              ? "bg-slate-800 text-white"
              : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
          }`}
        >
          <Settings className="w-4 h-4 text-slate-400" />
          <span>Settings</span>
        </button>

        {/* User Card */}
        <div className="mt-3 p-3 bg-slate-800/80 rounded-xl border border-slate-700/60 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 overflow-hidden min-w-0">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border shrink-0 ${
              isManufacturer
                ? "bg-amber-900/80 text-amber-200 border-amber-700"
                : "bg-blue-900/80 text-blue-200 border-blue-700"
            }`}>
              {initials}
            </div>
            <div className="truncate min-w-0">
              <p className="text-xs font-bold text-slate-100 truncate" title={displayName}>
                {displayName}
              </p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded-sm uppercase tracking-wider ${
                  isManufacturer
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                    : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                }`}>
                  {displayRole}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 truncate mt-0.5" title={displayOrg}>
                {displayOrg}
              </p>
            </div>
          </div>
          <button
            onClick={onLogout}
            title="Sign Out"
            className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-700 transition-colors shrink-0 cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
