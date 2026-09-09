import React, { useState, useEffect, useRef } from "react";
import { CheckCircle2, Loader2, Scale, AlertOctagon, RotateCcw, ArrowLeft } from "lucide-react";
import { analyzePackageImage } from "../services/api";

export default function AnalysisProgress({ uploadData, onAnalysisSuccess, onComplete, onCancel }) {
  const stages = [
    "Image received & validated",
    "Reading package label via PaddleOCR",
    "Extracting mandatory declarations",
    "Structuring product data JSON schema",
    "Running deterministic compliance rule engine",
    "Preparing Legal Metrology assessment result",
  ];

  const [currentStage, setCurrentStage] = useState(0);
  const [error, setError] = useState(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const isFinishedRef = useRef(false);

  useEffect(() => {
    let isCancelled = false;
    let stageTimer = null;
    let legacyTimer = null;

    setError(null);
    setCurrentStage(0);
    isFinishedRef.current = false;

    // Concurrently animate stages 0..4 while waiting for backend
    stageTimer = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < 4 && !isFinishedRef.current) {
          return prev + 1;
        }
        return prev;
      });
    }, 450);

    if (uploadData) {
      const files = uploadData.files && uploadData.files.length > 0
        ? uploadData.files
        : (uploadData.file ? [uploadData.file] : []);

      analyzePackageImage({
        files,
        file: uploadData.file || files[0] || null,
        category: uploadData.category,
        demoSample: uploadData.demoSample,
      })
        .then((result) => {
          if (isCancelled) return;
          result.previewUrls = uploadData.previewUrls || (uploadData.previewUrl ? [uploadData.previewUrl] : []);
          result.previewUrl = uploadData.previewUrl || result.previewUrls[0] || null;
          isFinishedRef.current = true;
          clearInterval(stageTimer);
          setCurrentStage(stages.length);

          setTimeout(() => {
            if (isCancelled) return;
            if (onAnalysisSuccess) {
              onAnalysisSuccess(result);
            } else if (onComplete) {
              onComplete(result);
            }
          }, 350);
        })
        .catch((err) => {
          if (isCancelled) return;
          clearInterval(stageTimer);
          setError(err?.message || "Failed to analyze package image. Please check the image and try again.");
        });
    } else {
      let stageCount = 0;
      legacyTimer = setInterval(() => {
        stageCount++;
        if (stageCount < stages.length) {
          setCurrentStage(stageCount);
        } else {
          clearInterval(legacyTimer);
          setTimeout(() => {
            if (!isCancelled && onComplete) onComplete();
          }, 350);
        }
      }, 450);
    }

    return () => {
      isCancelled = true;
      if (stageTimer) clearInterval(stageTimer);
      if (legacyTimer) clearInterval(legacyTimer);
    };
  }, [uploadData, isRetrying]);

  return (
    <div className="max-w-xl mx-auto py-12 px-4 space-y-8 text-center">
      <div className="space-y-3">
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto shadow-xl border transition-colors ${
          error ? "bg-rose-900 text-rose-300 border-rose-700" : "bg-blue-900 text-amber-400 border-blue-700"
        }`}>
          {error ? (
            <AlertOctagon className="w-8 h-8 text-rose-400" />
          ) : (
            <Scale className="w-8 h-8 animate-pulse" />
          )}
        </div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">
          {error ? "Analysis Encountered An Issue" : "Analyzing Package Label..."}
        </h2>
        <p className="text-xs text-slate-500 font-medium">
          {error ? "The inspection pipeline could not complete processing" : "Extracting declarations and executing Legal Metrology rule checks"}
        </p>
      </div>

      {error ? (
        /* Error Card with Retry Action */
        <div className="bg-white rounded-2xl border border-rose-200 shadow-xl p-6 text-left space-y-5">
          <div className="flex items-start gap-3 p-4 bg-rose-50 rounded-xl border border-rose-200 text-rose-900">
            <AlertOctagon className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs">
              <span className="font-bold block">Processing Error:</span>
              <p className="text-rose-800 leading-relaxed">{error}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => setIsRetrying((v) => !v)}
              className="flex-1 py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retry Analysis</span>
            </button>

            {onCancel && (
              <button
                onClick={onCancel}
                className="py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Upload</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Progress Pipeline Container */
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-6 text-left space-y-4">
          <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Processing Pipeline</span>
            <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full">
              Stage {Math.min(currentStage + 1, stages.length)} of {stages.length}
            </span>
          </div>

          <div className="space-y-3">
            {stages.map((stageText, idx) => {
              const isCompleted = idx < currentStage;
              const isCurrent = idx === currentStage;

              return (
                <div
                  key={idx}
                  className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                    isCompleted
                      ? "bg-emerald-50/70 border-emerald-200 text-emerald-900"
                      : isCurrent
                      ? "bg-blue-50 border-blue-300 text-blue-900 shadow-sm"
                      : "bg-slate-50/40 border-slate-200/60 text-slate-400"
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin shrink-0" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-slate-300 shrink-0"></div>
                  )}

                  <span className={`text-xs font-bold ${isCurrent ? "text-blue-950" : isCompleted ? "text-emerald-950" : "text-slate-400"}`}>
                    {stageText}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
