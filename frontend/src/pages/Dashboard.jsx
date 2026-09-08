import React from 'react';
import {
  PlusCircle,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Clock,
  ArrowUpRight,
  Sparkles,
  ShieldAlert,
  Layers,
  ChevronRight,
  Package,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { DEMO_PRODUCTS } from '../data/demoSamples';

export default function Dashboard({
  inspections = [],
  onNavigate,
  onSelectInspection,
  onStartDemoInspection,
  systemConfig,
}) {
  // Aggregate statistics
  const totalCount = inspections.length;
  const compliantCount = inspections.filter(
    (i) => i.status === 'COMPLIANT'
  ).length;
  const nonCompliantCount = inspections.filter(
    (i) => i.status === 'NON_COMPLIANT'
  ).length;
  const reviewCount = inspections.filter(
    (i) => i.status === 'NEEDS_REVIEW'
  ).length;

  const statCards = [
    {
      label: 'Total Inspections',
      value: totalCount,
      icon: Layers,
      textColor: 'text-slate-900',
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      iconColor: 'text-slate-600',
    },
    {
      label: 'Compliant Packages',
      value: compliantCount,
      icon: CheckCircle2,
      textColor: 'text-emerald-700',
      bgColor: 'bg-emerald-50/50',
      borderColor: 'border-emerald-200',
      iconColor: 'text-emerald-600',
    },
    {
      label: 'Non-Compliant Packages',
      value: nonCompliantCount,
      icon: XCircle,
      textColor: 'text-rose-700',
      bgColor: 'bg-rose-50/50',
      borderColor: 'border-rose-200',
      iconColor: 'text-rose-600',
    },
    {
      label: 'Needs Manual Review',
      value: reviewCount,
      icon: AlertTriangle,
      textColor: 'text-amber-700',
      bgColor: 'bg-amber-50/50',
      borderColor: 'border-amber-200',
      iconColor: 'text-amber-600',
    },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner / Callout */}
      <div className="bg-[#0F2942] rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-blue-600/20 to-transparent pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/20 border border-amber-400/30 text-amber-300 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles size={12} />
              <span>Smart Legal Metrology Screening</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              Packaged Commodity Compliance Engine
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
              Automated AI extraction of visible label declarations with deterministic Legal Metrology rule evaluation (LM-001 to LM-009).
            </p>
          </div>

          <div className="shrink-0 flex items-center gap-3">
            <button
              onClick={() => onNavigate('new-inspection')}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-extrabold text-[#0F2942] bg-amber-400 hover:bg-amber-300 shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5"
            >
              <PlusCircle size={16} />
              <span>+ New Inspection</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border ${stat.borderColor} ${stat.bgColor} bg-white shadow-2xs`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {stat.label}
                </span>
                <Icon size={18} className={stat.iconColor} />
              </div>
              <div className={`text-2xl sm:text-3xl font-black mt-2 ${stat.textColor}`}>
                {stat.value}
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Demo Evaluation Panel */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
                DEMO MODE
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Pre-configured Demonstration Scenarios
              </h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Sample data — not an actual government inspection. Evaluates pre-configured label packages through the deterministic rule engine.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DEMO_PRODUCTS.map((prod) => {
            const isCompliant = prod.id === 'sample_compliant';
            return (
              <div
                key={prod.id}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 hover:border-slate-300 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-slate-500 uppercase">
                        {prod.category} Pack
                      </span>
                      <h4 className="text-sm font-bold text-slate-900 mt-0.5">
                        {prod.name}
                      </h4>
                    </div>
                    <StatusBadge status={prod.expected_status} size="sm" />
                  </div>

                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                    {prod.description}
                  </p>

                  <ul className="mt-3 space-y-1 text-[11px] text-slate-600">
                    {prod.highlights.slice(0, 3).map((hl, hIdx) => (
                      <li key={hIdx} className="flex items-center gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${isCompliant ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                        <span>{hl}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">
                    Expected Score: <strong className="text-slate-800">{prod.score_estimate}</strong>
                  </span>
                  <button
                    onClick={() => onStartDemoInspection(prod.id)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-blue-900 bg-blue-100 hover:bg-blue-200 rounded-lg transition-colors"
                  >
                    <span>Run Test Inspection</span>
                    <ChevronRight size={13} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Inspections Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-2">
            <Clock size={16} className="text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Recent Inspections
            </h3>
          </div>
          {inspections.length > 0 && (
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-bold text-blue-900 hover:underline inline-flex items-center gap-1"
            >
              <span>View All ({inspections.length})</span>
              <ChevronRight size={12} />
            </button>
          )}
        </div>

        {inspections.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-3">
              <Package size={22} />
            </div>
            <h4 className="text-sm font-bold text-slate-800">No inspections yet</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Upload a packaged commodity label image to begin automated compliance screening.
            </p>
            <button
              onClick={() => onNavigate('new-inspection')}
              className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-[#0F2942] hover:bg-[#18395B] rounded-lg shadow-xs transition-colors"
            >
              <PlusCircle size={14} />
              <span>Start First Inspection</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-6">Inspection ID</th>
                  <th className="py-3 px-6">Product</th>
                  <th className="py-3 px-6">Category</th>
                  <th className="py-3 px-6">Compliance Status</th>
                  <th className="py-3 px-6">Screening Score</th>
                  <th className="py-3 px-6">Date / Time</th>
                  <th className="py-3 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {inspections.slice(0, 8).map((insp) => (
                  <tr
                    key={insp.inspection_id}
                    onClick={() => onSelectInspection(insp)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-6 font-mono font-bold text-slate-800">
                      <div className="flex items-center gap-2">
                        <span>{insp.inspection_id}</span>
                        {insp.is_demo && (
                          <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.2 rounded border border-amber-200">
                            DEMO
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="font-bold text-slate-900">
                        {insp.product?.product_name || insp.product?.generic_name || 'Packaged Commodity'}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate max-w-xs">
                        {insp.product?.manufacturer?.name || 'Manufacturer Unverified'}
                      </div>
                    </td>
                    <td className="py-3.5 px-6 font-medium text-slate-700">
                      {insp.category || insp.product?.category || 'General'}
                    </td>
                    <td className="py-3.5 px-6">
                      <StatusBadge status={insp.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-6">
                      <span className="font-mono font-bold text-slate-800">
                        {insp.score}%
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-500 font-mono text-[11px]">
                      {new Date(insp.created_at || Date.now()).toLocaleDateString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <span className="inline-flex items-center gap-1 font-semibold text-blue-800 hover:text-blue-900 text-xs">
                        <span>Inspect</span>
                        <ArrowUpRight size={13} />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
