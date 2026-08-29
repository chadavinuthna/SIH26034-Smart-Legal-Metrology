import React from "react";
import {
  LayoutDashboard,
  PlusCircle,
  History,
  FileSpreadsheet,
  Settings,
  UserCheck,
  Scale,
  LogOut,
} from "lucide-react";

export default function Sidebar({ currentPage, setCurrentPage, onLogout }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "new_inspection", label: "New Inspection", icon: PlusCircle },
    { id: "history", label: "Inspection History", icon: History },
    { id: "reports", label: "Reports", icon: FileSpreadsheet },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col h-screen sticky top-0 border-r border-slate-800 shadow-xl no-print">
      {/* Header Brand */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3 bg-slate-950/60">
        <div className="p-2 bg-blue-900/60 text-amber-400 rounded-xl border border-blue-700/50 shadow-inner">
          <Scale className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-sm text-white tracking-wide uppercase">Legal Metrology</h1>
          <p className="text-[11px] text-slate-400 font-medium">Compliance Portal (SIH26034)</p>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 py-6 px-3 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          Main Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                isActive
                  ? "bg-blue-600 text-white shadow-md shadow-blue-900/30"
                  : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Footer Navigation (Settings & Officer Profile) */}
      <div className="p-3 border-t border-slate-800 space-y-1 bg-slate-950/40">
        <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          System & Officer
        </div>
        <button
          onClick={() => setCurrentPage("settings")}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
            currentPage === "settings"
              ? "bg-slate-800 text-white"
              : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
          }`}
        >
          <Settings className="w-4 h-4 text-slate-400" />
          <span>Settings</span>
        </button>

        {/* Officer Card */}
        <div className="mt-3 p-3 bg-slate-800/80 rounded-xl border border-slate-700/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-blue-900/80 text-blue-200 flex items-center justify-center font-bold text-xs border border-blue-700">
              LM
            </div>
            <div className="truncate">
              <p className="text-xs font-bold text-slate-100 truncate">Insp. Vikram Singh</p>
              <p className="text-[10px] text-slate-400 truncate">ID: LM-OFF-8842</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            title="Sign Out"
            className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
