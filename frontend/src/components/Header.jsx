import React from 'react';
import { Menu, PlusCircle, ShieldAlert, Sparkles, Printer, FileText } from 'lucide-react';

export default function Header({
  activeTab,
  onNavigate,
  systemConfig,
  setIsMobileOpen,
  onPrint,
  hasActiveInspection,
}) {
  const titles = {
    dashboard: { title: 'Package Compliance Dashboard', subtitle: 'Legal Metrology inspection and compliance screening' },
    'new-inspection': { title: 'New Package Inspection', subtitle: 'Upload a clear image of the packaged commodity label for automated compliance screening' },
    analysis: { title: 'Automated Compliance Analysis', subtitle: 'Multi-stage declaration extraction and rule evaluation pipeline' },
    results: { title: 'Compliance Assessment', subtitle: 'Deterministic Legal Metrology rule verification and evidence audit' },
    history: { title: 'Inspection History', subtitle: 'Chronological audit log of evaluated packaged commodities' },
    reports: { title: 'Packaged Commodity Compliance Report', subtitle: 'Official regulatory inspection summary and violation notice' },
    settings: { title: 'System Settings & Rule Definitions', subtitle: 'Legal Metrology Act statutory rules (LM-001 to LM-009)' },
  };

  const current = titles[activeTab] || titles.dashboard;

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-xs border-b border-slate-200 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-2xs">
      {/* Left Title & Mobile Menu Toggle */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="lg:hidden p-2 -ml-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg"
          title="Open Menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <h2 className="text-base sm:text-lg font-bold text-[#0F2942] tracking-tight flex items-center gap-2">
            {current.title}
          </h2>
          <p className="text-xs text-slate-500 hidden sm:block">
            {current.subtitle}
          </p>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2.5">
        {/* Print Button (active on results/reports) */}
        {(activeTab === 'results' || activeTab === 'reports') && onPrint && (
          <button
            onClick={onPrint}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg shadow-2xs transition-colors"
          >
            <Printer size={14} className="text-slate-600" />
            <span className="hidden sm:inline">Print / Save as PDF</span>
          </button>
        )}

        {/* View Full Report Button if on Results tab */}
        {activeTab === 'results' && hasActiveInspection && (
          <button
            onClick={() => onNavigate('reports')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-900 bg-blue-50 border border-blue-200 hover:bg-blue-100/70 rounded-lg transition-colors"
          >
            <FileText size={14} className="text-blue-800" />
            <span className="hidden sm:inline">View Report</span>
          </button>
        )}

        {/* Prominent + New Inspection Button */}
        {activeTab !== 'new-inspection' && activeTab !== 'analysis' && (
          <button
            onClick={() => onNavigate('new-inspection')}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-white bg-[#0F2942] hover:bg-[#1A3A5B] rounded-lg shadow-xs transition-all duration-150 hover:shadow-md"
          >
            <PlusCircle size={14} className="text-amber-400" />
            <span>+ New Inspection</span>
          </button>
        )}
      </div>
    </header>
  );
}
