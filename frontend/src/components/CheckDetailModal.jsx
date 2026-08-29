import React from "react";
import StatusBadge from "./StatusBadge";
import { X, FileText, AlertCircle, Lightbulb, ShieldCheck, CheckCircle2 } from "lucide-react";

export default function CheckDetailModal({ check, onClose }) {
  if (!check) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in no-print">
      <div className="bg-white rounded-2xl max-w-xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="px-2 py-0.5 bg-blue-950 text-blue-300 font-mono text-xs font-bold rounded-md border border-blue-800">
              {check.rule_id}
            </span>
            <h3 className="font-bold text-base tracking-tight">{check.rule_name}</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-sm">
          {/* Status Banner */}
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Evaluation Result</p>
              <p className="text-xs font-medium text-slate-700 mt-0.5">
                Evaluated deterministically under Legal Metrology Act Rules
              </p>
            </div>
            <StatusBadge status={check.status} size="lg" />
          </div>

          {/* Detected Value */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Detected Value</h4>
            <div className="p-3 bg-slate-100/80 rounded-xl border border-slate-200 font-medium text-slate-800">
              {check.detected_value || "Not detected"}
            </div>
          </div>

          {/* Source Evidence */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-blue-600" />
              <span>Evidence & Source Label Text</span>
            </h4>
            <div className="p-3.5 bg-blue-50/50 rounded-xl border border-blue-100 font-mono text-xs text-blue-950 leading-relaxed whitespace-pre-wrap">
              {check.evidence || "Evidence not available."}
            </div>
          </div>

          {/* Reason / Explanation */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-slate-600" />
              <span>Why This Result Was Calculated</span>
            </h4>
            <p className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 text-slate-700 leading-relaxed text-xs">
              {check.reason}
            </p>
          </div>

          {/* Recommendation if any */}
          {check.recommendation && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-amber-600" />
                <span>Inspector Recommendation</span>
              </h4>
              <p className="p-3.5 bg-amber-50/80 rounded-xl border border-amber-200/80 text-amber-900 leading-relaxed text-xs font-medium">
                {check.recommendation}
              </p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 p-4 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-colors shadow-xs"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}
