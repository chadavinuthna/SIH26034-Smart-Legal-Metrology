import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  Loader2,
  ScanLine,
  FileSearch,
  Scale,
  ShieldCheck,
  Package,
} from 'lucide-react';

export default function AnalysisProgress({
  imagePreview,
  category,
  onComplete,
  error,
}) {
  const stages = [
    {
      id: 1,
      title: 'Image Received & Validated',
      desc: 'Checking file format, resolution, and principal display panel orientation',
      icon: ScanLine,
    },
    {
      id: 2,
      title: 'Reading Package Label Declarations',
      desc: 'Multimodal vision model parsing visible label text and declarations',
      icon: FileSearch,
    },
    {
      id: 3,
      title: 'Extracting Structured Declarations',
      desc: 'Isolating manufacturer name/address, net quantity, MRP, and dates',
      icon: Package,
    },
    {
      id: 4,
      title: 'Structuring Product Information',
      desc: 'Validating data integrity and normalizing measurements in Pydantic schema',
      icon: Scale,
    },
    {
      id: 5,
      title: 'Executing Deterministic Compliance Engine',
      desc: 'Evaluating statutory Legal Metrology rules (LM-001 to LM-009)',
      icon: ShieldCheck,
    },
    {
      id: 6,
      title: 'Preparing Compliance Assessment',
      desc: 'Calculating Prototype Screening Score and formulating violation notes',
      icon: CheckCircle2,
    },
  ];

  const [currentStage, setCurrentStage] = useState(1);

  useEffect(() => {
    // Staged progression while backend API processes
    const timer1 = setTimeout(() => setCurrentStage(2), 600);
    const timer2 = setTimeout(() => setCurrentStage(3), 1400);
    const timer3 = setTimeout(() => setCurrentStage(4), 2200);
    const timer4 = setTimeout(() => setCurrentStage(5), 3000);
    const timer5 = setTimeout(() => setCurrentStage(6), 3700);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  }, []);

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6 sm:p-8">
        {/* Header Title */}
        <div className="text-center max-w-md mx-auto mb-8">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto text-blue-900 mb-3 shadow-2xs">
            <Loader2 size={24} className="animate-spin text-blue-800" />
          </div>
          <h2 className="text-lg sm:text-xl font-extrabold text-[#0F2942] tracking-tight">
            Analyzing Package Label...
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Category: <span className="font-semibold text-slate-700">{category || 'Auto Detect'}</span> • Running automated Legal Metrology inspection pipeline.
          </p>
        </div>

        {/* Image Thumbnail & Pipeline Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Package Preview Thumbnail */}
          {imagePreview && (
            <div className="md:col-span-1 flex flex-col items-center">
              <div className="relative w-full h-48 bg-slate-900 rounded-xl overflow-hidden border border-slate-200 flex items-center justify-center shadow-xs">
                <img
                  src={imagePreview}
                  alt="Analyzing Package"
                  className="w-full h-full object-contain"
                />
                <div className="absolute inset-0 bg-blue-600/10 pointer-events-none" />
                <div className="absolute top-2 right-2 px-2 py-0.5 rounded bg-slate-900/80 text-[10px] font-mono font-bold text-amber-300">
                  SCANNING
                </div>
              </div>
              <span className="text-[11px] text-slate-400 mt-2">Principal Display Panel</span>
            </div>
          )}

          {/* Processing Stages List */}
          <div className={`space-y-3.5 ${imagePreview ? 'md:col-span-2' : 'md:col-span-3'}`}>
            {stages.map((stage) => {
              const Icon = stage.icon;
              const isDone = currentStage > stage.id;
              const isCurrent = currentStage === stage.id;
              const isPending = currentStage < stage.id;

              return (
                <div
                  key={stage.id}
                  className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-200 ${
                    isDone
                      ? 'bg-emerald-50/40 border-emerald-200/80 text-emerald-900'
                      : isCurrent
                      ? 'bg-blue-50/60 border-blue-300 text-blue-900 shadow-2xs'
                      : 'bg-slate-50/40 border-slate-100 text-slate-400 opacity-60'
                  }`}
                >
                  <div className="shrink-0 mt-0.5">
                    {isDone ? (
                      <CheckCircle2 size={18} className="text-emerald-600" />
                    ) : isCurrent ? (
                      <Loader2 size={18} className="text-blue-600 animate-spin" />
                    ) : (
                      <div className="w-4.5 h-4.5 rounded-full border-2 border-slate-300 flex items-center justify-center text-[10px] font-mono text-slate-400">
                        {stage.id}
                      </div>
                    )}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-bold flex items-center justify-between">
                      <span>{stage.title}</span>
                      {isDone && <span className="text-[10px] font-mono text-emerald-700">COMPLETED</span>}
                      {isCurrent && <span className="text-[10px] font-mono text-blue-700 animate-pulse">PROCESSING</span>}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                      {stage.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Error message display if any */}
        {error && (
          <div className="mt-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
}
