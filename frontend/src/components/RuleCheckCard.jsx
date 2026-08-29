import React from "react";
import StatusBadge from "./StatusBadge";
import { ChevronRight, FileSearch } from "lucide-react";

export default function RuleCheckCard({ check, onClick }) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border border-slate-200 p-4 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group flex items-center justify-between"
    >
      <div className="space-y-1 pr-4">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded-md">
            {check.rule_id}
          </span>
          <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
            {check.rule_name}
          </h4>
        </div>
        <p className="text-xs text-slate-500 line-clamp-1">
          <span className="font-semibold text-slate-700">Detected:</span>{" "}
          {check.detected_value || "Not detected"}
        </p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <StatusBadge status={check.status} />
        <div className="w-8 h-8 rounded-full bg-slate-50 group-hover:bg-blue-50 text-slate-400 group-hover:text-blue-600 flex items-center justify-center transition-colors">
          <ChevronRight className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
}
