import React, { useState } from 'react';
import {
  History as HistoryIcon,
  Search,
  Filter,
  ArrowUpRight,
  PlusCircle,
  Package,
  Calendar,
  Layers,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function History({
  inspections = [],
  onSelectInspection,
  onNewInspection,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredInspections = inspections.filter((insp) => {
    const pName = (insp.product?.product_name || insp.product?.generic_name || '').toLowerCase();
    const inspId = (insp.inspection_id || '').toLowerCase();
    const searchMatch = pName.includes(searchTerm.toLowerCase()) || inspId.includes(searchTerm.toLowerCase());

    if (statusFilter === 'ALL') return searchMatch;
    return searchMatch && insp.status === statusFilter;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search size={15} />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by product name or ID..."
            className="block w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-slate-900 bg-slate-50/50"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {['ALL', 'COMPLIANT', 'NON_COMPLIANT', 'NEEDS_REVIEW'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-colors ${
                statusFilter === st
                  ? 'bg-[#0F2942] text-white shadow-2xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st === 'ALL' ? 'All Records' : st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {filteredInspections.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-3">
              <Package size={22} />
            </div>
            <h4 className="text-sm font-bold text-slate-800">No matching inspections found</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Try adjusting your search query or filter settings.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <th className="py-3.5 px-6">Inspection Reference</th>
                  <th className="py-3.5 px-6">Packaged Commodity</th>
                  <th className="py-3.5 px-6">Category</th>
                  <th className="py-3.5 px-6">Legal Determination</th>
                  <th className="py-3.5 px-6">Screening Score</th>
                  <th className="py-3.5 px-6">Timestamp</th>
                  <th className="py-3.5 px-6 text-right">Review</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {filteredInspections.map((insp) => (
                  <tr
                    key={insp.inspection_id}
                    onClick={() => onSelectInspection(insp)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                  >
                    <td className="py-4 px-6 font-mono font-bold text-slate-800">
                      <div className="flex items-center gap-2">
                        <span>{insp.inspection_id}</span>
                        {insp.is_demo && (
                          <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.2 rounded border border-amber-200">
                            DEMO
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="font-bold text-slate-900">
                        {insp.product?.product_name || insp.product?.generic_name || 'Packaged Commodity'}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate max-w-xs">
                        {insp.product?.manufacturer?.name || 'Manufacturer Unverified'}
                      </div>
                    </td>
                    <td className="py-4 px-6 font-medium text-slate-700">
                      {insp.category || insp.product?.category || 'General'}
                    </td>
                    <td className="py-4 px-6">
                      <StatusBadge status={insp.status} size="sm" />
                    </td>
                    <td className="py-4 px-6">
                      <span className="font-mono font-bold text-slate-800">
                        {insp.score}%
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-500 font-mono text-[11px]">
                      {new Date(insp.created_at || Date.now()).toLocaleDateString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <span className="inline-flex items-center gap-1 font-semibold text-blue-800 hover:text-blue-900 text-xs">
                        <span>Open Details</span>
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
