import React from "react";
import { CheckCircle2, Image as ImageIcon, FileText, Sparkles, X } from "lucide-react";

export default function ImageQualityPreview({ imageSrc, fileName, fileSize, onRemove }) {
  if (!imageSrc) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center relative">
            <img src={imageSrc} alt="Package preview" className="w-full h-full object-cover" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800 truncate max-w-xs">
              {fileName || "Package Label Image"}
            </h4>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              {fileSize ? `${(fileSize / 1024).toFixed(1)} KB` : "Image Loaded"} • Label Target
            </p>
          </div>
        </div>

        {onRemove && (
          <button
            onClick={onRemove}
            className="p-1 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Remove Image"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Metric Indicators */}
      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-100">
        <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/80 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
            <ImageIcon className="w-3.5 h-3.5 text-blue-600" />
            <span>Image Quality</span>
          </div>
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
            <CheckCircle2 className="w-3 h-3" /> GOOD
          </span>
        </div>

        <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/80 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            <span>Text Visibility</span>
          </div>
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
            <CheckCircle2 className="w-3 h-3" /> GOOD
          </span>
        </div>
      </div>
    </div>
  );
}
