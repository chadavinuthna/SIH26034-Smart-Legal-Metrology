import React from 'react';
import {
  Printer,
  FileCheck2,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowLeft,
  Info,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function Report({
  inspection,
  officer,
  onBack,
  onPrint,
}) {
  if (!inspection) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <p className="text-slate-500">No inspection record available to generate a report.</p>
      </div>
    );
  }

  const {
    inspection_id,
    status,
    score = 0,
    category = 'Food',
    product = {},
    checks = [],
    summary = {},
    created_at,
    is_demo,
  } = inspection;

  const violations = checks.filter((c) => c.status === 'FAIL');
  const reviewItems = checks.filter((c) => c.status === 'REVIEW');

  const handleTriggerPrint = () => {
    if (onPrint) {
      onPrint();
    } else {
      window.print();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Top Action Bar (hidden in print) */}
      <div className="no-print flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-blue-900 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <ArrowLeft size={14} />
          <span>Back to Assessment</span>
        </button>

        <button
          onClick={handleTriggerPrint}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold text-white bg-[#0F2942] hover:bg-[#18395B] rounded-xl shadow-xs transition-colors"
        >
          <Printer size={15} className="text-amber-400" />
          <span>Print / Save as PDF</span>
        </button>
      </div>

      {/* Printable Report Document Card */}
      <div className="report-container bg-white rounded-2xl border border-slate-300 shadow-xl p-8 sm:p-12 text-slate-900 space-y-8">
        {/* Report Header & Emblem */}
        <div className="border-b-2 border-slate-900 pb-6 text-center space-y-1">
          <div className="text-xs font-black uppercase tracking-widest text-amber-800">
            Government of India • Ministry of Consumer Affairs, Food &amp; Public Distribution
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 uppercase tracking-tight">
            Packaged Commodity Compliance Report
          </h1>
          <div className="text-xs font-serif italic text-slate-600">
            Automated Inspection &amp; Statutory Legal Metrology (Packaged Commodities) Verification
          </div>
        </div>

        {/* Inspection Meta Information Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
          <div>
            <span className="text-slate-500 uppercase font-bold tracking-wider block text-[10px]">
              Inspection Reference
            </span>
            <span className="font-mono font-bold text-slate-900 text-sm mt-0.5 block">
              {inspection_id}
            </span>
          </div>

          <div>
            <span className="text-slate-500 uppercase font-bold tracking-wider block text-[10px]">
              Date &amp; Time
            </span>
            <span className="font-semibold text-slate-800 mt-0.5 block">
              {new Date(created_at || Date.now()).toLocaleDateString('en-IN', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>

          <div>
            <span className="text-slate-500 uppercase font-bold tracking-wider block text-[10px]">
              Inspecting Officer
            </span>
            <span className="font-semibold text-slate-800 mt-0.5 block">
              {officer?.name || 'Inspector A. Sharma'}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              {officer?.officer_id || 'LM-INSP-4092'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 uppercase font-bold tracking-wider block text-[10px]">
              Mode
            </span>
            <span className="font-semibold text-slate-800 mt-0.5 block">
              {is_demo ? 'Demo Simulation Sample' : 'Live Image Inspection'}
            </span>
          </div>
        </div>

        {/* Executive Summary Card */}
        <div className="p-5 rounded-xl border border-slate-300 bg-slate-50/50 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Statutory Determination
              </span>
              <div className="mt-1">
                <StatusBadge status={status} size="lg" />
              </div>
            </div>

            <div className="text-left sm:text-right">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Prototype Screening Score
              </span>
              <div className="text-2xl font-black text-slate-900 font-mono mt-0.5">
                {score}%
              </div>
            </div>
          </div>

          {/* Rule Breakdown Summary Bar */}
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div className="p-2 bg-emerald-50 rounded border border-emerald-200">
              <span className="font-bold text-emerald-800 block text-base">{summary.pass_count ?? summary.pass ?? 0}</span>
              <span className="text-[10px] uppercase font-bold text-emerald-700">Rules Passed</span>
            </div>
            <div className="p-2 bg-rose-50 rounded border border-rose-200">
              <span className="font-bold text-rose-800 block text-base">{summary.fail_count ?? summary.fail ?? 0}</span>
              <span className="text-[10px] uppercase font-bold text-rose-700">Violations</span>
            </div>
            <div className="p-2 bg-amber-50 rounded border border-amber-200">
              <span className="font-bold text-amber-800 block text-base">{summary.review_count ?? summary.review ?? 0}</span>
              <span className="text-[10px] uppercase font-bold text-amber-700">Needs Review</span>
            </div>
            <div className="p-2 bg-slate-100 rounded border border-slate-200">
              <span className="font-bold text-slate-700 block text-base">{summary.na_count ?? summary.na ?? 0}</span>
              <span className="text-[10px] uppercase font-bold text-slate-500">Not Applicable</span>
            </div>
          </div>
        </div>

        {/* Product Profile Declarations */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            1. Inspected Commodity Profile
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Product Brand &amp; Name:</span>
              <strong className="text-slate-900 block mt-0.5">
                {product.brand_name ? `${product.brand_name} — ` : ''}{product.product_name || 'Unspecified'}
              </strong>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Generic Commodity Identity:</span>
              <strong className="text-slate-900 block mt-0.5">
                {product.generic_name || <span className="text-rose-600">Not Declared</span>}
              </strong>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Manufacturer / Packer:</span>
              <strong className="text-slate-900 block mt-0.5">
                {product.manufacturer?.name || <span className="text-rose-600">Not Declared</span>}
              </strong>
              <div className="text-[11px] text-slate-600 mt-1">
                {product.manufacturer?.address || 'Address missing'}
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Net Quantity &amp; Maximum Retail Price:</span>
              <strong className="text-slate-900 block mt-0.5">
                {product.quantity?.value ? `${product.quantity.value} ${product.quantity.unit || ''}` : 'Qty Unverified'} • {product.mrp?.value ? `₹${product.mrp.value}` : 'MRP Unverified'}
              </strong>
              <div className="text-[11px] text-slate-600 mt-1">
                {product.mrp?.inclusive_of_taxes === true ? '(Inclusive of all taxes)' : 'Tax clause not verified'}
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Statutory Compliance Checks Table */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            2. Statutory Rule-by-Rule Audit Matrix
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border border-slate-300 text-xs">
              <thead className="bg-slate-100 text-[10px] uppercase font-bold tracking-wider text-slate-700">
                <tr className="border-b border-slate-300">
                  <th className="py-2 px-3 border-r border-slate-300">Rule ID</th>
                  <th className="py-2 px-3 border-r border-slate-300">Legal Requirement</th>
                  <th className="py-2 px-3 border-r border-slate-300">Status</th>
                  <th className="py-2 px-3 border-r border-slate-300">Detected Value</th>
                  <th className="py-2 px-3">Regulatory Assessment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-sans">
                {checks.map((chk) => (
                  <tr key={chk.rule_id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-700 border-r border-slate-200">
                      {chk.rule_id}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-slate-900 border-r border-slate-200">
                      {chk.rule_name}
                    </td>
                    <td className="py-2.5 px-3 border-r border-slate-200">
                      <StatusBadge status={chk.status} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-800 border-r border-slate-200 max-w-xs truncate">
                      {chk.detected_value || <span className="text-slate-400 italic font-sans">Not detected</span>}
                    </td>
                    <td className="py-2.5 px-3 text-slate-700 leading-tight">
                      {chk.reason}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Violations & Observations Notice */}
        {violations.length > 0 && (
          <div className="p-4 rounded-xl border border-rose-300 bg-rose-50/60 space-y-2">
            <div className="flex items-center gap-2 text-rose-900 font-bold text-xs uppercase tracking-wider">
              <XCircle size={15} className="text-rose-600" />
              <span>Statutory Non-Compliance Observations ({violations.length})</span>
            </div>
            <ul className="list-disc list-inside text-xs text-rose-900 space-y-1.5 pl-1">
              {violations.map((v) => (
                <li key={v.rule_id}>
                  <strong>{v.rule_name} ({v.rule_id}):</strong> {v.recommendation || v.reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Official Sign-off Block */}
        <div className="pt-8 border-t-2 border-slate-900 grid grid-cols-2 gap-8 text-xs">
          <div>
            <span className="text-slate-500 uppercase text-[10px] font-bold block">Generated By</span>
            <div className="mt-1 font-semibold text-slate-800">
              Smart Legal Metrology Package Compliance System
            </div>
            <div className="text-[10px] text-slate-500 font-mono">
              SIH26034 Automated Prototype Engine V1.0
            </div>
          </div>

          <div className="text-right">
            <div className="inline-block text-left">
              <div className="w-44 border-b border-slate-400 mb-1" />
              <span className="text-[10px] uppercase font-bold text-slate-600 block">
                Authorized Inspector Signature
              </span>
              <span className="text-xs font-bold text-slate-900 block">
                {officer?.name || 'Inspector A. Sharma'}
              </span>
              <span className="text-[10px] text-slate-500 font-mono block">
                {officer?.officer_id || 'LM-INSP-4092'}
              </span>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Footer */}
        <div className="text-center text-[10px] text-slate-500 border-t border-slate-200 pt-4 leading-relaxed">
          <p>
            <strong>Statutory Disclaimer:</strong> Prototype screening result. Final regulatory determination should be verified by an authorized Legal Metrology officer and applicable current regulations.
          </p>
        </div>
      </div>
    </div>
  );
}
