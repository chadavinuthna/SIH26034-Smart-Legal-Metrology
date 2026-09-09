import React, { useState, useEffect, useRef } from "react";
import StatusBadge from "./StatusBadge";
import { X, FileText, AlertCircle, Lightbulb, Crosshair } from "lucide-react";
import demoBiscuitsSvg from "../assets/demo_biscuits.svg";
import demoSnackSvg from "../assets/demo_snack.svg";

/**
 * Component to display a package image with scaled OCR bounding box highlighting.
 * Uses exact x_min, y_min, x_max, y_max from backend bbox and scales relative
 * to the intrinsic (natural) dimensions of the image.
 */
export function HighlightedBBoxImage({
  imageUrl,
  bbox,
  imageIndex = 1,
  status = "FAIL",
  label = null,
  alt = "Package label evidence",
  className = "",
}) {
  const [dimensions, setDimensions] = useState(null);
  const imgRef = useRef(null);

  useEffect(() => {
    if (imgRef.current && imgRef.current.complete && imgRef.current.naturalWidth) {
      setDimensions({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight,
      });
    }
  }, [imageUrl]);

  const handleImageLoad = (e) => {
    const { naturalWidth, naturalHeight } = e.target;
    if (naturalWidth && naturalHeight) {
      setDimensions({ width: naturalWidth, height: naturalHeight });
    }
  };

  const clamp = (val, min, max) => Math.max(min, Math.min(max, val));

  const getBoxStyles = (b) => {
    if (!dimensions || !b || dimensions.width === 0 || dimensions.height === 0) {
      return null;
    }
    const { x_min, y_min, x_max, y_max } = b;
    const left = clamp((x_min / dimensions.width) * 100, 0, 100);
    const top = clamp((y_min / dimensions.height) * 100, 0, 100);
    const width = clamp(((x_max - x_min) / dimensions.width) * 100, 0, 100 - left);
    const height = clamp(((y_max - y_min) / dimensions.height) * 100, 0, 100 - top);

    return {
      left: `${left}%`,
      top: `${top}%`,
      width: `${width}%`,
      height: `${height}%`,
      topPct: top,
    };
  };

  const primaryBoxStyles = bbox ? getBoxStyles(bbox) : null;

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="relative inline-block w-full overflow-hidden rounded-xl border border-slate-200 bg-slate-950 shadow-inner">
        {imageUrl ? (
          <img
            ref={imgRef}
            src={imageUrl}
            alt={alt}
            onLoad={handleImageLoad}
            className="block w-full h-auto object-contain mx-auto select-none"
          />
        ) : (
          <div className="w-full h-44 flex items-center justify-center text-slate-400 text-xs font-mono">
            Image not available
          </div>
        )}

        {/* Primary Highlighting Box */}
        {primaryBoxStyles && (
          <div
            style={{
              left: primaryBoxStyles.left,
              top: primaryBoxStyles.top,
              width: primaryBoxStyles.width,
              height: primaryBoxStyles.height,
            }}
            className={`absolute border-2 pointer-events-none transition-all rounded-xs ${
              status === "PASS"
                ? "border-emerald-500 bg-emerald-500/20 shadow-[0_0_0_1px_rgba(16,185,129,0.5)]"
                : status === "REVIEW"
                ? "border-amber-500 bg-amber-500/20 shadow-[0_0_0_1px_rgba(245,158,11,0.5)]"
                : "border-rose-600 bg-rose-500/25 shadow-[0_0_0_1px_rgba(225,29,72,0.5)] animate-pulse"
            }`}
          >
            {label && (
              <span
                className={`absolute px-1.5 py-0.5 text-[9px] font-mono font-bold rounded shadow-xs whitespace-nowrap z-10 ${
                  primaryBoxStyles.topPct > 12 ? "-top-5 left-0" : "top-full mt-1 left-0"
                } ${
                  status === "PASS"
                    ? "bg-emerald-700 text-white"
                    : status === "REVIEW"
                    ? "bg-amber-700 text-white"
                    : "bg-rose-700 text-white"
                }`}
              >
                {label}
              </span>
            )}
          </div>
        )}
      </div>

      {bbox && (
        <div className="flex flex-wrap items-center justify-between text-[10px] text-slate-500 px-0.5">
          <span className="font-semibold text-slate-600">
            Source Panel: <strong className="text-slate-800 font-mono">Image #{imageIndex}</strong>
          </span>
          <span className="font-mono text-slate-500">
            Coordinates: [{bbox.x_min}, {bbox.y_min}] &rarr; [{bbox.x_max}, {bbox.y_max}]
          </span>
        </div>
      )}
    </div>
  );
}

export default function CheckDetailModal({ check, onClose, inspection }) {
  if (!check) return null;

  const resolveImageUrl = () => {
    if (check.previewUrl) return check.previewUrl;
    if (inspection) {
      if (inspection.previewUrls && inspection.previewUrls.length > 0) {
        if (check.image_index && check.image_index > 0) {
          const idx = check.image_index - 1;
          if (idx < inspection.previewUrls.length) {
            return inspection.previewUrls[idx];
          }
        }
        return inspection.previewUrls[0];
      }
      if (inspection.previewUrl) return inspection.previewUrl;
      if (inspection.is_demo) {
        const isSnack =
          inspection.product?.brand_name?.includes("XYZ") ||
          inspection.product?.product_name?.includes("Spicy");
        return isSnack ? demoSnackSvg : demoBiscuitsSvg;
      }
    }
    return null;
  };

  const imageUrl = resolveImageUrl();

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

          {/* Visual Evidence & Label Error Highlighting */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Crosshair className="w-3.5 h-3.5 text-blue-600" />
                <span>Visual Evidence &amp; Error Highlighting</span>
              </h4>
              {check.image_index && (
                <span className="text-[10px] font-mono font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  Panel #{check.image_index}
                </span>
              )}
            </div>

            {check.bbox && check.image_index ? (
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                <HighlightedBBoxImage
                  imageUrl={imageUrl}
                  bbox={check.bbox}
                  imageIndex={check.image_index}
                  status={check.status}
                  label={`${check.rule_id}: ${check.detected_value || check.rule_name}`}
                  alt={`Visual evidence for ${check.rule_id}`}
                />
              </div>
            ) : (check.status === "FAIL" || check.status === "REVIEW") ? (
              <div className="p-3.5 bg-amber-50/80 border border-amber-200 rounded-xl text-xs space-y-1">
                <div className="flex items-center gap-1.5 font-bold text-amber-900 text-[11px] uppercase tracking-wide">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>No Source Location Available on Label</span>
                </div>
                <p className="text-amber-800 text-[11px] leading-relaxed">
                  No exact source location is available because the required information was not detected on the uploaded package images.
                </p>
              </div>
            ) : (
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-500 italic">
                Statutory declaration compliant. Visual bounding box coordinate not attached.
              </div>
            )}
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
              <span>Evidence &amp; Source Label Text</span>
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

