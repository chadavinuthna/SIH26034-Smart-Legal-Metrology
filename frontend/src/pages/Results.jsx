import React, { useState } from "react";
import StatusBadge from "../components/StatusBadge";
import RuleCheckCard from "../components/RuleCheckCard";
import CheckDetailModal from "../components/CheckDetailModal";
import ExtractedDataPanel from "../components/ExtractedDataPanel";
import demoBiscuitsSvg from "../assets/demo_biscuits.svg";
import demoSnackSvg from "../assets/demo_snack.svg";
import {
  FileText,
  Printer,
  PlusCircle,
  Sparkles,
  AlertOctagon,
  CheckCircle2,
  AlertTriangle,
  ListFilter,
  ArrowLeft,
} from "lucide-react";

export default function Results({ inspection, onNewInspection, onViewReport, onBackToDashboard }) {
  const [selectedCheck, setSelectedCheck] = useState(null);
  const [activeTab, setActiveTab] = useState("checks"); // 'checks' | 'extracted'
  const [filterStatus, setFilterStatus] = useState("ALL");

  if (!inspection) return null;

  const { status, score, product, checks, summary, is_demo, inspection_id, timestamp, disclaimer } = inspection;

  const filteredChecks = (checks || []).filter((check) => {
    if (filterStatus === "ALL") return true;
    return check.status === filterStatus;
  });

  // Single Source of Truth: Format Country of Origin display strictly from ProductData
  const formatCountryDisplay = () => {
    if (product?.country_of_origin) {
      return product.country_of_origin;
    }
    if (product?.import_status === "DOMESTIC") {
      return "India (Domestic)";
    }
    return "Not detected";
  };

  // Image source: uses previewUrl or matches fictional SVG mockup
  const getImageSource = () => {
    if (inspection.previewUrl) return inspection.previewUrl;
    if (is_demo) {
      return product?.brand_name?.includes("XYZ") || product?.product_name?.includes("Spicy")
        ? demoSnackSvg
        : demoBiscuitsSvg;
    }
    return demoBiscuitsSvg;
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Navigation Top Action */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBackToDashboard}
          className="px-3.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 shadow-2xs transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={onViewReport}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Save PDF Report</span>
          </button>
          <button
            onClick={onNewInspection}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Inspection</span>
          </button>
        </div>
      </div>

      {/* Demo Banner */}
      {is_demo && (
        <div className="bg-amber-500/15 border border-amber-500/40 rounded-xl p-3.5 text-amber-900 text-xs font-bold flex items-center gap-2 shadow-xs">
          <Sparkles className="w-4 h-4 text-amber-600 shrink-0" />
          <span>DEMO MODE: Sample data — not an actual government inspection.</span>
        </div>
      )}

      {/* Main Overall Result Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs font-bold text-blue-900 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-200">
              {inspection_id}
            </span>
            <span className="text-xs text-slate-400 font-semibold">{timestamp}</span>
          </div>

          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            {product?.product_name || "Packaged Commodity Label"}
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Category: <span className="font-bold text-slate-700">{product?.category || "Food"}</span> • Brand:{" "}
            <span className="font-bold text-slate-700">{product?.brand_name || "Unstated"}</span>
          </p>
        </div>

        {/* Overall Score & Status */}
        <div className="flex items-center gap-6 bg-slate-50 p-5 rounded-2xl border border-slate-200/80 shrink-0">
          <div className="text-center pr-4 border-r border-slate-200">
            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Prototype Screening Score
            </p>
            <div className="text-3xl font-black text-slate-900 mt-0.5">{score}%</div>
          </div>

          <div className="space-y-1">
            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Final Decision</p>
            <StatusBadge status={status} size="lg" />
          </div>
        </div>
      </div>

      {/* Summary Stat Pills */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-emerald-50/80 border border-emerald-200 rounded-xl p-3.5 flex items-center justify-between">
          <span className="text-xs font-bold text-emerald-900">PASS Checks</span>
          <span className="text-lg font-black text-emerald-700">{summary?.pass_count || 0}</span>
        </div>
        <div className="bg-rose-50/80 border border-rose-200 rounded-xl p-3.5 flex items-center justify-between">
          <span className="text-xs font-bold text-rose-900">FAIL Checks</span>
          <span className="text-lg font-black text-rose-700">{summary?.fail_count || 0}</span>
        </div>
        <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-3.5 flex items-center justify-between">
          <span className="text-xs font-bold text-amber-900">REVIEW Checks</span>
          <span className="text-lg font-black text-amber-700">{summary?.review_count || 0}</span>
        </div>
        <div className="bg-slate-100/80 border border-slate-200 rounded-xl p-3.5 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700">N/A Checks</span>
          <span className="text-lg font-black text-slate-600">{summary?.na_count || 0}</span>
        </div>
      </div>

      {/* Two Column Layout: Image Left, Checks/Data Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Image Preview Card */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4 sticky top-6">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-3">
            Package Label Visual Evidence
          </h3>

          <div className="w-full aspect-4/3 rounded-xl bg-slate-950 overflow-hidden relative border border-slate-800 shadow-inner flex items-center justify-center p-2">
            <img
              src={getImageSource()}
              alt="Package Label Evidence"
              className="w-full h-full object-contain"
            />
          </div>

          <div className="space-y-2 text-xs bg-slate-50 p-3 rounded-xl border border-slate-200/80">
            <div className="flex justify-between text-slate-600">
              <span className="font-medium">Identified Brand:</span>
              <span className="font-bold text-slate-900">{product?.brand_name || "Unspecified"}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span className="font-medium">Generic Commodity Name:</span>
              <span className="font-bold text-slate-900">{product?.generic_name || "Not detected"}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span className="font-medium">Country of Origin:</span>
              <span className="font-bold text-slate-900">{formatCountryDisplay()}</span>
            </div>
          </div>
        </div>

        {/* Right Column: Tabbed Checks / Extracted Data */}
        <div className="lg:col-span-7 space-y-6">
          {/* Tab Navigation */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab("checks")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "checks"
                    ? "bg-blue-600 text-white shadow-md shadow-blue-900/30"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Compliance Checks ({checks?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab("extracted")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "extracted"
                    ? "bg-blue-600 text-white shadow-md shadow-blue-900/30"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Extracted Product Information
              </button>
            </div>

            {activeTab === "checks" && (
              <div className="flex items-center gap-1.5 pr-2">
                <ListFilter className="w-3.5 h-3.5 text-slate-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="text-xs font-bold text-slate-700 bg-slate-100 border border-slate-200 rounded-lg px-2.5 py-1 focus:outline-none"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="PASS">PASS</option>
                  <option value="FAIL">FAIL</option>
                  <option value="REVIEW">REVIEW</option>
                  <option value="NA">N/A</option>
                </select>
              </div>
            )}
          </div>

          {/* Tab Content 1: Compliance Rule Cards */}
          {activeTab === "checks" ? (
            <div className="space-y-3">
              {filteredChecks.length === 0 ? (
                <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-xs text-slate-500 font-medium">
                  No compliance checks found matching filter "{filterStatus}".
                </div>
              ) : (
                filteredChecks.map((check) => (
                  <RuleCheckCard
                    key={check.rule_id}
                    check={check}
                    onClick={() => setSelectedCheck(check)}
                  />
                ))
              )}
            </div>
          ) : (
            /* Tab Content 2: Extracted Product Data Panel */
            <ExtractedDataPanel product={product} />
          )}
        </div>
      </div>

      {/* Mandatory Legal Disclaimer */}
      <div className="bg-slate-100/90 rounded-2xl border border-slate-200/80 p-4 text-center">
        <p className="text-xs text-slate-600 font-medium leading-relaxed">
          <strong>LEGAL DISCLAIMER:</strong> {disclaimer}
        </p>
      </div>

      {/* Expandable Check Detail Modal */}
      <CheckDetailModal
        check={selectedCheck}
        onClose={() => setSelectedCheck(null)}
      />
    </div>
  );
}
