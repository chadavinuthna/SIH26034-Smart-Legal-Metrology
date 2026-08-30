import React from 'react';
import { ChevronRight, FileSearch } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function CheckCard({ check, onClick }) {
  const norm = (check.status || '').toUpperCase();

  // Subtle border accent based on status
  const borderAccents = {
    PASS: 'hover:border-emerald-300 border-slate-200',
    FAIL: 'hover:border-rose-300 border-rose-200 bg-rose-50/20',
    REVIEW: 'hover:border-amber-300 border-amber-200 bg-amber-50/20',
    NA: 'border-slate-200 bg-slate-50/50',
  };

  const accentClass = borderAccents[norm] || borderAccents.REVIEW;

  return (
    <div
      onClick={onClick}
      className={`group relative p-4 rounded-xl border bg-white shadow-xs transition-all duration-200 hover:shadow-md cursor-pointer ${accentClass}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {check.rule_id}
            </span>
            <h4 className="text-sm font-bold text-slate-900 truncate">
              {check.rule_name}
            </h4>
          </div>

          {/* Detected Value Preview */}
          <div className="text-xs text-slate-600 mt-1.5 flex items-baseline gap-1.5">
            <span className="font-semibold text-slate-500">Detected:</span>
            <span className="font-mono text-slate-800 font-medium truncate max-w-md">
              {check.detected_value || <span className="text-slate-400 italic">Not detected</span>}
            </span>
          </div>

          {/* Reason Summary */}
          <p className="text-xs text-slate-500 mt-1 line-clamp-1">
            {check.reason}
          </p>
        </div>

        {/* Status Badge & Action Arrow */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          <StatusBadge status={check.status} size="sm" />
          <span className="inline-flex items-center text-xs font-semibold text-blue-800 group-hover:text-blue-900 transition-colors">
            <FileSearch size={13} className="mr-1" />
            Inspect
            <ChevronRight size={13} className="ml-0.5 transition-transform group-hover:translate-x-0.5" />
          </span>
        </div>
      </div>
    </div>
  );
}
