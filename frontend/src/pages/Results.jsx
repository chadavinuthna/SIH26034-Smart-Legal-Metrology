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
  Type,
} from "lucide-react";

export default function Results({ inspection, onNewInspection, onViewReport, onBackToDashboard }) {
  const [selectedCheck, setSelectedCheck] = useState(null);
  const [activeTab, setActiveTab] = useState("checks"); // 'checks' | 'extracted'
  const [filterStatus, setFilterStatus] = useState("ALL");

  if (!inspection) return null;

  const {
    status,
    score,
    product,
    checks,
    summary,
    is_demo,
    inspection_id,
    timestamp,
    disclaimer,
    font_size_screening,
  } = inspection;

  const filteredChecks = (checks || []).filter((check) => {
    if (filterStatus === "ALL") return true;
    return check.status === filterStatus;
  });

  // Human-readable labels for mandatory declaration fields in font size screening
  const formatFieldName = (field) => {
    switch (field) {
      case "net_quantity":
        return "Net Quantity";
      case "mrp":
        return "Maximum Retail Price (MRP)";
      case "manufacturer":
        return "Manufacturer / Packer";
      case "dates":
        return "Date Declarations";
      case "consumer_care":
        return "Consumer Care Details";
      case "country_of_origin":
        return "Country of Origin";
      default:
        return field
          .split("_")
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(" ");
    }
  };

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

          {inspection?.timings && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
              <span className="font-bold text-slate-700">⚡ Latency:</span>
              <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono font-medium">
                OCR: {inspection.timings.ocr_time_ms}ms
              </span>
              {inspection.timings.llm_time_ms > 0 && (
                <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded font-mono font-medium">
                  LLM: {inspection.timings.llm_time_ms}ms
                </span>
              )}
              <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono font-medium">
                Rules: {inspection.timings.rule_engine_time_ms}ms
              </span>
              <span className="bg-blue-50 text-blue-800 font-bold px-2 py-0.5 rounded font-mono">
                Total: {inspection.timings.total_time_ms}ms
              </span>
            </div>
          )}
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

      {/* Font Size Screening Section (Advisory Prototype Warning) */}
      {font_size_screening && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-6 space-y-4">
          {/* Section Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center border border-blue-200/60 shrink-0">
                <Type className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-extrabold text-slate-900 tracking-tight">
                    Font Size Screening
                  </h3>
                  <span className="text-[10px] font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                    Advisory Screening
                  </span>
                </div>
                <p className="text-xs text-slate-500 font-medium">
                  Estimated character/box height from OCR bounding boxes • Screening threshold:{" "}
                  <span className="font-bold text-slate-700">{font_size_screening.threshold_px || 14}px</span>
                </p>
              </div>
            </div>

            {/* Overall Status Badge */}
            <div className="shrink-0">
              {font_size_screening.overall_screening_status === "PASS" ? (
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs font-black shadow-2xs">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Font size appears OK</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs font-black shadow-2xs">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Font size needs verification</span>
                </div>
              )}
            </div>
          </div>

          {/* Declarations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 pt-1">
            {(font_size_screening.declarations || []).map((decl) => {
              const isPass = decl.status === "PASS";
              return (
                <div
                  key={decl.field}
                  className={`rounded-xl border p-4 space-y-2.5 transition-all ${
                    isPass
                      ? "bg-slate-50/60 border-slate-200/80 hover:border-emerald-200"
                      : "bg-amber-50/40 border-amber-200 hover:border-amber-300 shadow-2xs"
                  }`}
                >
                  {/* Field Name & Status Badge */}
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-slate-900 truncate">
                      {formatFieldName(decl.field)}
                    </span>
                    <span
                      className={`text-[10px] font-black px-2 py-0.5 rounded-md uppercase tracking-wider border shrink-0 ${
                        isPass
                          ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                          : "bg-amber-100 text-amber-900 border-amber-300"
                      }`}
                    >
                      {decl.status}
                    </span>
                  </div>

                  {/* Height & Detected Text */}
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center justify-between gap-2 text-slate-600">
                      <span className="text-slate-400 font-medium">Detected Height:</span>
                      <span className="font-mono font-black text-slate-800">
                        {decl.box_height_px != null ? `${decl.box_height_px} px` : "Unmatched"}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between gap-2 text-slate-600">
                      <span className="text-slate-400 font-medium shrink-0">Text:</span>
                      <span
                        className="font-mono text-[11px] text-slate-800 truncate text-right font-medium max-w-[180px]"
                        title={decl.detected_text || "Not detected"}
                      >
                        {decl.detected_text || "Not detected"}
                      </span>
                    </div>
                  </div>

                  {/* Advisory Message */}
                  <div
                    className={`text-[11px] font-medium leading-relaxed pt-2 border-t ${
                      isPass
                        ? "border-slate-100 text-emerald-700 flex items-start gap-1.5"
                        : "border-amber-100 text-amber-800 flex items-start gap-1.5"
                    }`}
                  >
                    {isPass ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                    )}
                    <span>{decl.message}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

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
