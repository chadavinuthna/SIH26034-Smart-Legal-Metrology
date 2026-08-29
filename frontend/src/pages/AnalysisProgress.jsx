import React, { useState, useEffect } from "react";
import { CheckCircle2, Loader2, Scale, Sparkles } from "lucide-react";

export default function AnalysisProgress({ onComplete }) {
  const stages = [
    "Image received & validated",
    "Reading package label via AI vision",
    "Extracting mandatory declarations",
    "Structuring product data JSON schema",
    "Running deterministic compliance rule engine",
    "Preparing Legal Metrology assessment result",
  ];

  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < stages.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            onComplete();
          }, 400);
          return prev;
        }
      });
    }, 450);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-xl mx-auto py-12 px-4 space-y-8 text-center">
      <div className="space-y-3">
        <div className="w-16 h-16 rounded-2xl bg-blue-900 text-amber-400 flex items-center justify-center mx-auto shadow-xl border border-blue-700">
          <Scale className="w-8 h-8 animate-pulse" />
        </div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Analyzing Package Label...</h2>
        <p className="text-xs text-slate-500 font-medium">
          Extracting declarations and executing Legal Metrology rule checks
        </p>
      </div>

      {/* Progress Pipeline Container */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-6 text-left space-y-4">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Processing Pipeline</span>
          <span className="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full">
            Stage {currentStage + 1} of {stages.length}
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
    </div>
  );
}
