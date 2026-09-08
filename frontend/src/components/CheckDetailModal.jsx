import React, { useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, XCircle, Info, Quote, Lightbulb } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function CheckDetailModal({ check, isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !check) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      {/* Backdrop click */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Modal Card */}
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-10 animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs font-bold text-slate-600 bg-white border border-slate-200 px-2.5 py-1 rounded-md shadow-2xs">
              {check.rule_id}
            </span>
            <h3 className="text-base font-bold text-slate-900">
              {check.rule_name}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors"
            title="Close modal (Esc)"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-5 max-h-[80vh] overflow-y-auto">
          {/* Status Row */}
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Verification Status
            </span>
            <StatusBadge status={check.status} size="lg" />
          </div>

          {/* Detected Value */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Detected Declaration
            </label>
            <div className="p-3.5 rounded-xl bg-slate-900 text-slate-100 font-mono text-sm break-words border border-slate-800">
              {check.detected_value || (
                <span className="text-slate-400 italic">Not detected on visible package label</span>
              )}
            </div>
          </div>

          {/* Evidence / Verbatim Quote */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              <Quote size={13} className="text-blue-600" />
              <span>Verbatim Package Evidence</span>
            </div>
            <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100 text-slate-800 text-sm italic font-serif leading-relaxed">
              "{check.evidence || 'Evidence not available.'}"
            </div>
          </div>

          {/* Reason / Why */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              <Info size={13} className="text-slate-600" />
              <span>Regulatory Assessment Rationale</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-sm leading-relaxed">
              {check.reason}
            </div>
          </div>

          {/* Recommendation if any */}
          {check.recommendation && (
            <div>
              <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-amber-700 mb-1.5">
                <Lightbulb size={13} className="text-amber-600" />
                <span>Inspector Action / Compliance Recommendation</span>
              </div>
              <div className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-sm leading-relaxed">
                {check.recommendation}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-6 py-3.5 bg-slate-50 border-t border-slate-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-100 rounded-lg shadow-2xs transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}
