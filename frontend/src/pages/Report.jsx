import React from "react";
import StatusBadge from "../components/StatusBadge";
import { Printer, Scale, ArrowLeft, ShieldCheck, FileText } from "lucide-react";

export default function Report({ inspection, onBackToResults }) {
  if (!inspection) return null;

  const { inspection_id, status, score, product, checks, summary, timestamp, disclaimer, is_demo } = inspection;

  const handlePrint = () => {
    window.print();
  };

  const violations = (checks || []).filter((c) => c.status === "FAIL" || c.status === "REVIEW");

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Top Toolbar (Hidden on Print) */}
      <div className="flex items-center justify-between no-print">
        <button
          onClick={onBackToResults}
          className="px-3.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 shadow-2xs transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Assessment</span>
        </button>

        <button
          onClick={handlePrint}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-md transition-colors flex items-center gap-2"
        >
          <Printer className="w-4 h-4" />
          <span>Print / Save as PDF</span>
        </button>
      </div>

      {/* Official Report Document Body */}
      <div className="bg-white rounded-2xl border border-slate-300 p-10 shadow-lg print-card space-y-8">
        {/* Government Letterhead Header */}
        <div className="border-b-2 border-slate-900 pb-6 flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-slate-900">
              <Scale className="w-6 h-6 text-blue-900" />
              <h1 className="text-lg font-black tracking-wider uppercase">
                Legal Metrology Department — Govt. of India
              </h1>
            </div>
            <p className="text-xs font-bold text-slate-600 uppercase tracking-widest">
              OFFICIAL PACKAGED COMMODITY COMPLIANCE REPORT
            </p>
            <p className="text-[11px] text-slate-400">
              Screening evaluated under Legal Metrology (Packaged Commodities) Rules
            </p>
          </div>

          <div className="text-right space-y-1">
            <p className="font-mono text-sm font-black text-blue-950">{inspection_id}</p>
            <p className="text-xs font-semibold text-slate-500">{timestamp}</p>
            {is_demo && (
              <span className="inline-block px-2 py-0.5 text-[10px] font-bold text-amber-800 bg-amber-100 rounded-md border border-amber-300">
                DEMO EVALUATION
              </span>
            )}
          </div>
        </div>

        {/* Executive Summary Grid */}
        <div className="grid grid-cols-2 gap-6 bg-slate-50 p-5 rounded-xl border border-slate-200 text-xs">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Commodity Name:</span>
              <span className="font-bold text-slate-900">{product?.product_name || "Unidentified"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Brand Name:</span>
              <span className="font-bold text-slate-900">{product?.brand_name || "Unstated"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Generic Name:</span>
              <span className="font-bold text-slate-900">{product?.generic_name || "Unstated"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Product Category:</span>
              <span className="font-bold text-slate-900">{product?.category || "Food"}</span>
            </div>
          </div>

          <div className="space-y-2 border-l border-slate-200 pl-6">
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-semibold">Overall Compliance:</span>
              <StatusBadge status={status} size="md" />
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Prototype Screening Score:</span>
              <span className="font-black text-slate-900 text-sm">{score}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-semibold">Inspecting Officer:</span>
              <span className="font-bold text-slate-900">Insp. Vikram Singh (LM-8842)</span>
            </div>
          </div>
        </div>

        {/* Detailed Rule Evaluations Table */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
            Legal Metrology Rule Evaluations (LM-001 to LM-009)
          </h3>

          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100 text-slate-700 font-bold border-b border-slate-300">
                <th className="py-2.5 px-3 border border-slate-200">Rule ID</th>
                <th className="py-2.5 px-3 border border-slate-200">Requirement</th>
                <th className="py-2.5 px-3 border border-slate-200">Status</th>
                <th className="py-2.5 px-3 border border-slate-200">Detected Value</th>
                <th className="py-2.5 px-3 border border-slate-200">Evidence / Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {(checks || []).map((check) => (
                <tr key={check.rule_id} className="border-b border-slate-200">
                  <td className="py-2.5 px-3 font-mono font-bold border border-slate-200">{check.rule_id}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-900 border border-slate-200">{check.rule_name}</td>
                  <td className="py-2.5 px-3 border border-slate-200">
                    <StatusBadge status={check.status} size="sm" />
                  </td>
                  <td className="py-2.5 px-3 font-medium text-slate-800 border border-slate-200">
                    {check.detected_value || "Not detected"}
                  </td>
                  <td className="py-2.5 px-3 text-[11px] text-slate-600 border border-slate-200">
                    {check.reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Violations and Action Items */}
        {violations.length > 0 && (
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-bold text-rose-900 uppercase tracking-wider border-b border-rose-200 pb-2">
              Action Items & Required Corrections
            </h3>
            <div className="space-y-2">
              {violations.map((v) => (
                <div key={v.rule_id} className="p-3 bg-rose-50/60 rounded-xl border border-rose-200 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-rose-950">
                      [{v.rule_id}] {v.rule_name} — Status: {v.status}
                    </span>
                  </div>
                  <p className="text-rose-900 text-[11px]">{v.reason}</p>
                  {v.recommendation && (
                    <p className="text-rose-800 font-semibold text-[11px] mt-1">
                      <strong>Recommendation:</strong> {v.recommendation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Official Disclaimer */}
        <div className="pt-6 border-t border-slate-200 text-center">
          <p className="text-[11px] text-slate-500 italic">
            <strong>Legal Disclaimer:</strong> {disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}
