import React, { useState, useEffect } from "react";
import StatusBadge from "../components/StatusBadge";
import {
  Printer,
  Scale,
  ArrowLeft,
  Pencil,
  Check,
  X,
  FileEdit,
  AlertCircle,
} from "lucide-react";

/**
 * Normalizes rule status values (e.g., handles "N/A" vs "NA").
 */
const normalizeStatus = (s) => {
  if (!s) return "";
  const upper = s.toUpperCase().trim();
  if (upper === "N/A") return "NA";
  return upper;
};

/**
 * Checks if a given rule has an active inspector override that differs from automated system status.
 */
const isRuleOverridden = (ruleId, systemStatus, overridesMap) => {
  const override = overridesMap?.[ruleId];
  if (!override || !override.decision) return false;
  return normalizeStatus(override.decision) !== normalizeStatus(systemStatus);
};

/**
 * Returns effective status for a rule given inspector overrides.
 */
const getEffectiveStatus = (ruleId, systemStatus, overridesMap) => {
  const override = overridesMap?.[ruleId];
  if (override && override.decision && normalizeStatus(override.decision) !== normalizeStatus(systemStatus)) {
    return override.decision;
  }
  return systemStatus;
};

export default function Report({ inspection, onBackToResults }) {
  const [isEditing, setIsEditing] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const checks = inspection?.checks || [];

  // Initialize report-level editable data from the inspection source of truth
  const [reportData, setReportData] = useState(() => {
    const obs = {};
    const recs = {};
    checks.forEach((c) => {
      obs[c.rule_id] = c.reason || "";
      if (c.recommendation) {
        recs[c.rule_id] = c.recommendation;
      }
    });
    return {
      officerName: "Insp. Vikram Singh (LM-8842)",
      notes: "",
      observations: obs,
      recommendations: recs,
      overrides: {}, // { [rule_id]: { decision: "", reason: "" } }
    };
  });

  // Temporary draft state for edit session (Cancel/Save behavior)
  const [tempData, setTempData] = useState(reportData);

  // Re-synchronize when inspection changes
  useEffect(() => {
    const obs = {};
    const recs = {};
    checks.forEach((c) => {
      obs[c.rule_id] = c.reason || "";
      if (c.recommendation) {
        recs[c.rule_id] = c.recommendation;
      }
    });
    const initial = {
      officerName: "Insp. Vikram Singh (LM-8842)",
      notes: "",
      observations: obs,
      recommendations: recs,
      overrides: {},
    };
    setReportData(initial);
    setTempData(initial);
    setValidationErrors({});
    setIsEditing(false);
  }, [inspection?.inspection_id]);

  if (!inspection) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
          <Scale className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-800">No Inspection Record Available</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Please complete an inspection or select an inspection from history to view and generate a compliance report.
        </p>
      </div>
    );
  }

  const {
    inspection_id,
    status,
    score,
    product,
    timestamp,
    disclaimer,
    is_demo,
  } = inspection;

  const handleStartEditing = () => {
    setTempData({
      ...reportData,
      observations: { ...reportData.observations },
      recommendations: { ...reportData.recommendations },
      overrides: Object.fromEntries(
        Object.entries(reportData.overrides || {}).map(([k, v]) => [k, { ...v }])
      ),
    });
    setValidationErrors({});
    setIsEditing(true);
  };

  const handleCancelEditing = () => {
    setTempData({
      ...reportData,
      observations: { ...reportData.observations },
      recommendations: { ...reportData.recommendations },
      overrides: Object.fromEntries(
        Object.entries(reportData.overrides || {}).map(([k, v]) => [k, { ...v }])
      ),
    });
    setValidationErrors({});
    setIsEditing(false);
  };

  const handleSaveEditing = () => {
    const errors = {};

    checks.forEach((check) => {
      const override = tempData.overrides?.[check.rule_id];
      const decision = normalizeStatus(override?.decision);
      const systemStatus = normalizeStatus(check.status);

      // If inspector decision != system result, reason is mandatory
      if (decision && decision !== systemStatus) {
        if (!override?.reason || !override.reason.trim()) {
          errors[check.rule_id] = `Override reason is required for rule ${check.rule_id}.`;
        }
      }
    });

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setValidationErrors({});
    setReportData({
      ...tempData,
      observations: { ...tempData.observations },
      recommendations: { ...tempData.recommendations },
      overrides: Object.fromEntries(
        Object.entries(tempData.overrides || {}).map(([k, v]) => [k, { ...v }])
      ),
    });
    setIsEditing(false);
  };

  const handlePrint = () => {
    window.print();
  };

  const getObservation = (ruleId, defaultReason) => {
    return reportData.observations[ruleId] !== undefined
      ? reportData.observations[ruleId]
      : defaultReason;
  };

  const getRecommendation = (ruleId, defaultRec) => {
    return reportData.recommendations[ruleId] !== undefined
      ? reportData.recommendations[ruleId]
      : defaultRec;
  };

  // Count active overrides in saved reportData
  const activeOverridesCount = checks.filter((c) =>
    isRuleOverridden(c.rule_id, c.status, reportData.overrides)
  ).length;

  // Filter checks that are violations or review items either systemically or via inspector decision
  const activeViolations = checks.filter((c) => {
    const currentOverrides = isEditing ? tempData.overrides : reportData.overrides;
    const eff = getEffectiveStatus(c.rule_id, c.status, currentOverrides);
    return eff === "FAIL" || eff === "REVIEW" || c.status === "FAIL" || c.status === "REVIEW";
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Top Toolbar (Hidden on Print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 no-print">
        <button
          onClick={onBackToResults}
          className="px-3.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 shadow-2xs transition-colors flex items-center gap-2 self-start"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Assessment</span>
        </button>

        <div className="flex items-center gap-2.5">
          {!isEditing ? (
            <>
              <button
                onClick={handleStartEditing}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
                title="Edit report notes, observations, recommendations, and compliance overrides"
              >
                <Pencil className="w-3.5 h-3.5 text-amber-400" />
                <span>Edit Report</span>
              </button>
              <button
                onClick={handlePrint}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-md transition-colors flex items-center gap-2"
              >
                <Printer className="w-4 h-4" />
                <span>Print / Save as PDF</span>
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleCancelEditing}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl border border-slate-300 transition-colors flex items-center gap-1.5"
              >
                <X className="w-3.5 h-3.5" />
                <span>Cancel</span>
              </button>
              <button
                onClick={handleSaveEditing}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-md transition-colors flex items-center gap-1.5"
              >
                <Check className="w-4 h-4" />
                <span>Save Report</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Edit Mode & Validation Notice Banners (Hidden on Print) */}
      {isEditing && (
        <div className="space-y-3 no-print">
          {Object.keys(validationErrors).length > 0 && (
            <div className="bg-rose-50 border border-rose-400 rounded-xl p-3.5 text-rose-900 text-xs font-semibold flex items-center gap-2.5 shadow-xs">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <div>
                <strong>Cannot Save Report:</strong> Override reason is mandatory for all rules where the inspector decision differs from the automated system result.
              </div>
            </div>
          )}

          <div className="bg-amber-50 border border-amber-300 rounded-xl p-3.5 text-amber-900 text-xs font-medium flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-2">
              <FileEdit className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Report Editing Mode:</strong> You can edit officer notes, observations, recommendations, and record official inspector overrides for individual rules.
              </span>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-200/70 text-amber-900 px-2 py-0.5 rounded shrink-0">
              Drafting Edits
            </span>
          </div>
        </div>
      )}

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
              <span className="text-slate-500 font-semibold">Overall Automated Compliance:</span>
              <StatusBadge status={status} size="md" />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-semibold">Prototype Screening Score:</span>
              <span className="font-black text-slate-900 text-sm">{score}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-semibold">Inspecting Officer:</span>
              {!isEditing ? (
                <span className="font-bold text-slate-900">{reportData.officerName}</span>
              ) : (
                <input
                  type="text"
                  value={tempData.officerName}
                  onChange={(e) => setTempData({ ...tempData, officerName: e.target.value })}
                  className="px-2 py-0.5 bg-white border border-blue-400 rounded text-xs font-bold text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 max-w-xs"
                  placeholder="Officer Name & ID"
                />
              )}
            </div>
            {activeOverridesCount > 0 && (
              <div className="flex justify-between items-center pt-1 border-t border-slate-200">
                <span className="text-slate-500 font-semibold">Officer Status Overrides:</span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                  <Scale className="w-3 h-3 text-amber-700" />
                  <span>{activeOverridesCount} {activeOverridesCount === 1 ? "Rule Overridden" : "Rules Overridden"}</span>
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Inspector Remarks & General Notes */}
        {!isEditing && reportData.notes.trim() && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
            <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
              Inspector Remarks &amp; Statutory Notes
            </h4>
            <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">
              {reportData.notes}
            </p>
          </div>
        )}

        {isEditing && (
          <div className="p-4 bg-blue-50/50 rounded-xl border border-blue-200 text-xs space-y-1.5 no-print">
            <label className="block font-bold text-blue-950 uppercase tracking-wider text-[10px]">
              Inspector Remarks &amp; General Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={tempData.notes}
              onChange={(e) => setTempData({ ...tempData, notes: e.target.value })}
              placeholder="Add contextual officer remarks, inspection premises, verification caveats, or additional notes..."
              className="w-full p-2.5 bg-white border border-blue-300 rounded-lg text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 leading-relaxed"
            />
          </div>
        )}

        {/* Detailed Rule Evaluations Table */}
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Legal Metrology Rule Evaluations (LM-001 to LM-009)
            </h3>
            {isEditing ? (
              <span className="text-[10px] text-blue-700 font-semibold no-print">
                Set Inspector Decision and mandatory justification where needed
              </span>
            ) : (
              activeOverridesCount > 0 && (
                <span className="text-[10px] text-amber-800 font-bold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  Contains {activeOverridesCount} Inspector {activeOverridesCount === 1 ? "Override" : "Overrides"}
                </span>
              )
            )}
          </div>

          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100 text-slate-700 font-bold border-b border-slate-300">
                <th className="py-2.5 px-3 border border-slate-200 w-20">Rule ID</th>
                <th className="py-2.5 px-3 border border-slate-200 w-44">Requirement</th>
                <th className="py-2.5 px-3 border border-slate-200 w-44">Compliance Status</th>
                <th className="py-2.5 px-3 border border-slate-200 w-36">Detected Value</th>
                <th className="py-2.5 px-3 border border-slate-200">Assessment / Override Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {checks.map((check) => {
                const isOverriddenInView = isRuleOverridden(check.rule_id, check.status, reportData.overrides);
                const viewOverride = reportData.overrides?.[check.rule_id] || {};

                const isOverriddenInEdit = isRuleOverridden(check.rule_id, check.status, tempData.overrides);
                const editOverride = tempData.overrides?.[check.rule_id] || { decision: "", reason: "" };
                const ruleError = validationErrors[check.rule_id];

                return (
                  <tr
                    key={check.rule_id}
                    className={`border-b border-slate-200 transition-colors ${
                      isEditing && isOverriddenInEdit
                        ? "bg-amber-50/30"
                        : isOverriddenInView
                        ? "bg-amber-50/20"
                        : ""
                    }`}
                  >
                    <td className="py-2.5 px-3 font-mono font-bold border border-slate-200 align-top">
                      {check.rule_id}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-slate-900 border border-slate-200 align-top">
                      {check.rule_name}
                    </td>
                    <td className="py-2.5 px-3 border border-slate-200 align-top min-w-[130px]">
                      {!isEditing ? (
                        !isOverriddenInView ? (
                          // Normal single system status
                          <StatusBadge status={check.status} size="sm" />
                        ) : (
                          // Clearly distinguish System Result vs Inspector Decision
                          <div className="space-y-1.5 py-0.5">
                            <div className="flex items-center gap-1.5 text-[10px]">
                              <span className="font-semibold text-slate-500">System Result:</span>
                              <StatusBadge status={check.status} size="sm" />
                            </div>
                            <div className="flex items-center gap-1.5 text-[10px]">
                              <span className="font-bold text-blue-950">Inspector Decision:</span>
                              <StatusBadge status={viewOverride.decision} size="sm" />
                            </div>
                            <span className="inline-block px-1.5 py-0.2 rounded text-[9px] font-extrabold uppercase tracking-wider bg-amber-100 text-amber-900 border border-amber-300">
                              Override Applied
                            </span>
                          </div>
                        )
                      ) : (
                        // Edit Mode Controls
                        <div className="space-y-2 no-print">
                          <div className="flex items-center gap-1.5 text-[10px]">
                            <span className="font-semibold text-slate-500">System:</span>
                            <StatusBadge status={check.status} size="sm" />
                          </div>

                          <div className="space-y-0.5">
                            <label className="block text-[10px] font-bold text-slate-700">
                              Inspector Decision:
                            </label>
                            <select
                              value={editOverride.decision || ""}
                              onChange={(e) => {
                                const val = e.target.value;
                                const newOverrides = {
                                  ...tempData.overrides,
                                  [check.rule_id]: {
                                    ...editOverride,
                                    decision: val,
                                  },
                                };
                                setTempData({ ...tempData, overrides: newOverrides });

                                // Clear validation error if returned to system default or empty
                                if (!val || normalizeStatus(val) === normalizeStatus(check.status)) {
                                  setValidationErrors((prev) => {
                                    const next = { ...prev };
                                    delete next[check.rule_id];
                                    return next;
                                  });
                                }
                              }}
                              className={`w-full px-2 py-1 bg-white border rounded text-xs font-semibold text-slate-900 focus:outline-none focus:ring-1 ${
                                isOverriddenInEdit
                                  ? "border-amber-400 bg-amber-50/60 text-amber-950 focus:ring-amber-500 font-bold"
                                  : "border-slate-300 focus:ring-blue-500"
                              }`}
                            >
                              <option value="">System Default ({check.status})</option>
                              <option value="PASS">PASS</option>
                              <option value="FAIL">FAIL</option>
                              <option value="REVIEW">REVIEW</option>
                              <option value="NA">N/A</option>
                            </select>
                          </div>

                          {isOverriddenInEdit && (
                            <span className="inline-block text-[9px] font-bold uppercase text-amber-900 bg-amber-100 px-1.5 py-0.5 rounded border border-amber-300">
                              Overriding System Result
                            </span>
                          )}
                        </div>
                      )}
                    </td>

                    <td className="py-2.5 px-3 font-medium text-slate-800 border border-slate-200 align-top">
                      {check.detected_value || "Not detected"}
                    </td>

                    <td className="py-2.5 px-3 text-[11px] text-slate-600 border border-slate-200 align-top">
                      {!isEditing ? (
                        <div className="space-y-2">
                          <div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase block mb-0.5">
                              Statutory Assessment:
                            </span>
                            <p className="text-slate-800 leading-relaxed">
                              {getObservation(check.rule_id, check.reason)}
                            </p>
                          </div>

                          {isOverriddenInView && (
                            <div className="p-2.5 bg-amber-50/90 border border-amber-300 rounded-lg text-[11px] text-amber-950 space-y-1">
                              <div className="flex items-center gap-1 font-bold text-amber-900 text-[10px] uppercase tracking-wide">
                                <Scale className="w-3.5 h-3.5 text-amber-700" />
                                <span>Inspector Override Reason:</span>
                              </div>
                              <p className="font-semibold text-amber-950 whitespace-pre-wrap leading-relaxed">
                                {viewOverride.reason}
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-2 no-print">
                          <div>
                            <label className="block text-[10px] font-bold text-slate-600 mb-0.5">
                              Statutory Assessment:
                            </label>
                            <textarea
                              rows={2}
                              value={tempData.observations[check.rule_id] ?? check.reason}
                              onChange={(e) => {
                                const newObs = { ...tempData.observations, [check.rule_id]: e.target.value };
                                setTempData({ ...tempData, observations: newObs });
                              }}
                              className="w-full p-1.5 bg-white border border-slate-300 rounded text-[11px] text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 leading-tight"
                            />
                          </div>

                          {isOverriddenInEdit && (
                            <div className="p-2.5 bg-amber-50 border border-amber-300 rounded-lg space-y-1">
                              <label className="flex items-center justify-between text-[10px] font-bold text-amber-950 uppercase tracking-wide">
                                <span className="flex items-center gap-1">
                                  <Scale className="w-3.5 h-3.5 text-amber-700" />
                                  <span>Override Reason (Mandatory):</span>
                                </span>
                                <span className="text-[9px] text-amber-800 font-bold lowercase italic">
                                  required for override
                                </span>
                              </label>
                              <textarea
                                rows={2}
                                value={editOverride.reason || ""}
                                onChange={(e) => {
                                  const val = e.target.value;
                                  const newOverrides = {
                                    ...tempData.overrides,
                                    [check.rule_id]: {
                                      ...editOverride,
                                      reason: val,
                                    },
                                  };
                                  setTempData({ ...tempData, overrides: newOverrides });
                                  if (val.trim()) {
                                    setValidationErrors((prev) => {
                                      const next = { ...prev };
                                      delete next[check.rule_id];
                                      return next;
                                    });
                                  }
                                }}
                                placeholder="Enter official statutory justification for overriding automated result..."
                                className={`w-full p-1.5 bg-white border rounded text-[11px] text-amber-950 placeholder:text-amber-800/50 focus:outline-none focus:ring-1 ${
                                  ruleError
                                    ? "border-rose-500 ring-1 ring-rose-500 bg-rose-50/40"
                                    : "border-amber-300 focus:ring-amber-500"
                                }`}
                              />
                              {ruleError && (
                                <p className="text-[10px] text-rose-600 font-bold flex items-center gap-1 pt-0.5">
                                  <AlertCircle className="w-3 h-3 shrink-0" />
                                  <span>{ruleError}</span>
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Action Items & Violations Section */}
        {activeViolations.length > 0 && (
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-2 flex items-center justify-between">
              <span>Action Items &amp; Statutory Directives</span>
              <span className="text-[10px] font-semibold text-slate-500">
                {activeViolations.length} {activeViolations.length === 1 ? "Item" : "Items"} Evaluated
              </span>
            </h3>
            <div className="space-y-2">
              {activeViolations.map((v) => {
                const currentOverrides = isEditing ? tempData.overrides : reportData.overrides;
                const isOverridden = isRuleOverridden(v.rule_id, v.status, currentOverrides);
                const ruleOverride = currentOverrides?.[v.rule_id] || {};
                const effStatus = getEffectiveStatus(v.rule_id, v.status, currentOverrides);

                const isResolvedByOverride = isOverridden && effStatus === "PASS";

                return (
                  <div
                    key={v.rule_id}
                    className={`p-3.5 rounded-xl border text-xs space-y-2 ${
                      isResolvedByOverride
                        ? "bg-emerald-50/60 border-emerald-300 text-emerald-950"
                        : effStatus === "FAIL"
                        ? "bg-rose-50/60 border-rose-200 text-rose-950"
                        : "bg-amber-50/60 border-amber-200 text-amber-950"
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-bold">
                        [{v.rule_id}] {v.rule_name}
                      </span>
                      <div className="flex items-center gap-2">
                        {!isOverridden ? (
                          <StatusBadge status={v.status} size="sm" />
                        ) : (
                          <div className="flex items-center gap-1.5 text-[10px]">
                            <span className="text-slate-500 font-semibold">System:</span>
                            <StatusBadge status={v.status} size="sm" />
                            <span className="text-slate-400 font-bold">&rarr;</span>
                            <span className="text-slate-700 font-bold">Inspector:</span>
                            <StatusBadge status={ruleOverride.decision} size="sm" />
                          </div>
                        )}
                      </div>
                    </div>

                    {!isEditing ? (
                      <div className="space-y-1.5">
                        <p className="text-[11px] leading-relaxed">
                          {getObservation(v.rule_id, v.reason)}
                        </p>
                        {isOverridden && (
                          <div className="p-2 bg-white/80 border border-amber-300 rounded text-[11px] text-amber-950">
                            <strong className="text-amber-900 uppercase text-[9px] block">
                              Inspector Override Reason:
                            </strong>
                            {ruleOverride.reason}
                          </div>
                        )}
                        {getRecommendation(v.rule_id, v.recommendation) && (
                          <p className="text-[11px] font-semibold mt-1">
                            <strong>Recommendation:</strong> {getRecommendation(v.rule_id, v.recommendation)}
                          </p>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-2 pt-1 no-print">
                        <div>
                          <label className="block text-[10px] font-bold uppercase mb-0.5 text-slate-700">
                            Observation / Assessment:
                          </label>
                          <textarea
                            rows={2}
                            value={tempData.observations[v.rule_id] ?? v.reason}
                            onChange={(e) => {
                              const newObs = { ...tempData.observations, [v.rule_id]: e.target.value };
                              setTempData({ ...tempData, observations: newObs });
                            }}
                            className="w-full p-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-bold uppercase mb-0.5 text-slate-700">
                            Inspector Recommendation:
                          </label>
                          <textarea
                            rows={2}
                            value={tempData.recommendations[v.rule_id] ?? (v.recommendation || "")}
                            onChange={(e) => {
                              const newRecs = { ...tempData.recommendations, [v.rule_id]: e.target.value };
                              setTempData({ ...tempData, recommendations: newRecs });
                            }}
                            placeholder="Enter corrective directive for manufacturer/packer..."
                            className="w-full p-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
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
                {reportData.officerName}
              </span>
            </div>
          </div>
        </div>

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
