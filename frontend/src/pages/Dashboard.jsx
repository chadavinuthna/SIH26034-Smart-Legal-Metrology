import React, { useState, useEffect } from "react";
import StatusBadge from "../components/StatusBadge";
import { fetchInspectionHistory } from "../services/api";
import { getStoredHistory } from "../services/storage";
import {
  PlusCircle,
  FileCheck,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  ArrowUpRight,
  Eye,
  RefreshCw,
  Search,
} from "lucide-react";

export default function Dashboard({ onStartNewInspection, onViewInspectionResult }) {
  const [inspections, setInspections] = useState([]);
  const [stats, setStats] = useState({ total: 0, compliant: 0, non_compliant: 0, needs_review: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const apiData = await fetchInspectionHistory();
    if (apiData && apiData.inspections && apiData.inspections.length > 0) {
      setInspections(apiData.inspections);
      setStats(apiData.stats);
    } else {
      const local = getStoredHistory();
      setInspections(local);
      const total = local.length;
      const compliant = local.filter((i) => i.status === "COMPLIANT").length;
      const non_compliant = local.filter((i) => i.status === "NON_COMPLIANT").length;
      const needs_review = local.filter((i) => i.status === "NEEDS_REVIEW").length;
      setStats({ total, compliant, non_compliant, needs_review });
    }
  };

  return (
    <div className="space-y-8 pb-10">
      {/* Top Banner Action */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-8 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6 border border-slate-800">
        <div className="space-y-2">
          <span className="px-3 py-1 bg-amber-500/20 text-amber-300 font-bold text-xs rounded-full border border-amber-500/30">
            SIH26034 Prototype V1
          </span>
          <h2 className="text-2xl font-black tracking-tight">Packaged Commodity Compliance Screening</h2>
          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            AI-assisted label extraction with deterministic Legal Metrology Act rule enforcement. Upload package images to screen for mandatory declarations.
          </p>
        </div>

        <button
          onClick={onStartNewInspection}
          className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-xs shadow-lg shadow-blue-900/50 hover:shadow-blue-900/80 transition-all flex items-center gap-2.5 shrink-0"
        >
          <PlusCircle className="w-5 h-5" />
          <span>+ New Package Inspection</span>
        </button>
      </div>

      {/* Summary Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Inspections</p>
            <h3 className="text-2xl font-black text-slate-900 mt-1">{stats.total}</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Recorded screening sessions</p>
          </div>
          <div className="p-3 bg-blue-50 text-blue-700 rounded-xl">
            <FileCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-emerald-600 uppercase tracking-wider">Compliant</p>
            <h3 className="text-2xl font-black text-emerald-700 mt-1">{stats.compliant}</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">100% Rules Satisfied</p>
          </div>
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-rose-600 uppercase tracking-wider">Non-Compliant</p>
            <h3 className="text-2xl font-black text-rose-700 mt-1">{stats.non_compliant}</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Mandatory Rules Failed</p>
          </div>
          <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-amber-600 uppercase tracking-wider">Needs Review</p>
            <h3 className="text-2xl font-black text-amber-700 mt-1">{stats.needs_review}</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Requires Officer Verification</p>
          </div>
          <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Recent Inspections Table Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-4">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Package Inspections</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Historical Screening Records logged in local system storage
            </p>
          </div>
          <button
            onClick={loadData}
            className="p-2 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors flex items-center gap-1.5 text-xs font-semibold"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        {inspections.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <Search className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-700">No inspections logged yet</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click "+ New Package Inspection" above to analyze a commodity package label.
            </p>
            <button
              onClick={onStartNewInspection}
              className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-xs"
            >
              Start First Inspection
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Inspection ID</th>
                  <th className="py-3.5 px-6">Product / Commodity</th>
                  <th className="py-3.5 px-6">Category</th>
                  <th className="py-3.5 px-6">Result Status</th>
                  <th className="py-3.5 px-6">Screening Score</th>
                  <th className="py-3.5 px-6">Date / Time</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {inspections.map((item) => (
                  <tr key={item.inspection_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-mono font-bold text-blue-900">
                      {item.inspection_id}
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {item.product?.product_name || "Unidentified Commodity"}
                      {item.is_demo && (
                        <span className="ml-2 px-1.5 py-0.5 text-[10px] font-bold text-amber-700 bg-amber-50 rounded-md border border-amber-200">
                          DEMO
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-slate-600 font-medium">
                      {item.product?.category || "Food"}
                    </td>
                    <td className="py-4 px-6">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-4 px-6 font-extrabold text-slate-800">
                      {item.score}%
                    </td>
                    <td className="py-4 px-6 text-slate-500 text-[11px] font-medium">
                      {item.timestamp}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => onViewInspectionResult(item)}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-bold rounded-lg transition-colors inline-flex items-center gap-1.5 text-xs"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View</span>
                      </button>
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
