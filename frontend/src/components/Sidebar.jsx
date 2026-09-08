import React from 'react';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  FileText,
  Settings,
  UserCheck,
  LogOut,
  Shield,
  Layers,
  ChevronRight,
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  onNavigate,
  officer,
  onLogout,
  systemConfig,
  isMobileOpen,
  setIsMobileOpen,
}) {
  const navItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'new-inspection',
      label: 'New Inspection',
      icon: PlusCircle,
      badge: 'Primary',
    },
    {
      id: 'history',
      label: 'Inspection History',
      icon: History,
      badge: null,
    },
    {
      id: 'reports',
      label: 'Compliance Reports',
      icon: FileText,
      badge: null,
    },
  ];

  const bottomItems = [
    {
      id: 'settings',
      label: 'Settings & Rules',
      icon: Settings,
    },
  ];

  const handleNav = (tabId) => {
    onNavigate(tabId);
    if (setIsMobileOpen) setIsMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-[#0F2942] text-slate-100 flex flex-col justify-between border-r border-slate-800 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand & Emblem Header */}
        <div>
          <div className="p-5 border-b border-slate-700/80 bg-[#0B2034]">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-400/30 text-amber-400 shadow-sm shrink-0">
                <Shield size={22} className="stroke-[2.2]" />
              </div>
              <div className="min-w-0">
                <div className="text-[11px] font-bold tracking-widest text-amber-400 uppercase leading-none">
                  Legal Metrology
                </div>
                <h1 className="text-sm font-extrabold text-white tracking-tight mt-1 truncate">
                  Package Compliance
                </h1>
                <div className="text-[10px] text-slate-400 font-medium">
                  SIH26034 Prototype V1
                </div>
              </div>
            </div>
          </div>

          {/* System Mode Indicator */}
          <div className="px-5 py-2.5 bg-slate-900/50 border-b border-slate-800/80 flex items-center justify-between text-xs">
            <span className="text-slate-400 text-[11px] font-medium">Engine Mode</span>
            {systemConfig?.ai_service_configured ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Gemini Vision Live
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                Demo / Rule Engine
              </span>
            )}
          </div>

          {/* Main Navigation Links */}
          <nav className="p-3 space-y-1 mt-2">
            <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Inspection Operations
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNav(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 group ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-900/40'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      size={17}
                      className={isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'}
                    />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && !isActive && (
                    <span className="text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded">
                      {item.badge}
                    </span>
                  )}
                  {isActive && <ChevronRight size={14} className="text-blue-200" />}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Area: Settings & Officer Profile */}
        <div>
          {/* Bottom Settings Link */}
          <div className="p-3 border-t border-slate-800/80">
            {bottomItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNav(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:bg-slate-800/80 hover:text-white'
                  }`}
                >
                  <Icon size={16} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Officer Session Profile Card */}
          <div className="p-3 bg-[#0B2034] border-t border-slate-800">
            <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-blue-900/80 border border-blue-700/50 flex items-center justify-center text-blue-300 font-bold text-xs shrink-0">
                  <UserCheck size={16} />
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-bold text-slate-200 truncate">
                    {officer?.name || 'Inspector Officer'}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">
                    {officer?.officer_id || 'LM-INSP-4092'}
                  </div>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors shrink-0"
              >
                <LogOut size={15} />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
