import React, { useState, useEffect } from "react";
import StatusBadge from "../components/StatusBadge";
import { getStoredHistory } from "../services/storage";
import { fetchInspectionHistory } from "../services/api";
import { Search, Filter, Eye, History as HistoryIcon, Calendar } from "lucide-react";

export default function History({ onViewInspectionResult }) {
  const [inspections, setInspections] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    const apiData = await fetchInspectionHistory();
    if (apiData && apiData.inspections) {
      setInspections(apiData.inspections);
    } else {
      setInspections(getStoredHistory());
    }
  };

  const filteredItems = inspections.filter((item) => {
    const matchesSearch =
      (item.inspection_id || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.product?.product_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.product?.brand_name || "").toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" || item.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Inspection History</h2>
          <p className="text-xs text-slate-500 font-medium">
            Complete historical database of Legal Metrology package compliance screenings.
          </p>
        </div>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search ID, Product, or Brand..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 text-slate-900 text-xs font-medium rounded-xl border border-slate-300 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 text-slate-800 text-xs font-bold rounded-xl border border-slate-300 focus:outline-none"
          >
            <option value="ALL">All Compliance Statuses</option>
            <option value="COMPLIANT">COMPLIANT</option>
            <option value="NON_COMPLIANT">NON-COMPLIANT</option>
            <option value="NEEDS_REVIEW">NEEDS REVIEW</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {filteredItems.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No inspection records found matching your filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Inspection ID</th>
                  <th className="py-3.5 px-6">Product / Commodity</th>
                  <th className="py-3.5 px-6">Category</th>
                  <th className="py-3.5 px-6">Final Status</th>
                  <th className="py-3.5 px-6">Screening Score</th>
                  <th className="py-3.5 px-6">Date / Time</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredItems.map((item) => (
                  <tr key={item.inspection_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-mono font-bold text-blue-900">
                      {item.inspection_id}
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {item.product?.product_name || "Packaged Commodity"}
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
                        <span>View Result</span>
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
