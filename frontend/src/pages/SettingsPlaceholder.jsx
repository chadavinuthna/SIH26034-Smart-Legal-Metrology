import React from "react";
import { Settings, Shield, Sliders, Database, User } from "lucide-react";

export default function SettingsPlaceholder() {
  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-12">
      <div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">System Settings & Configuration</h2>
        <p className="text-xs text-slate-500 font-medium">
          Legal Metrology Rule Engine & Officer Environment Configuration (SIH26034 Prototype V1)
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
        <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div className="p-3 bg-blue-50 text-blue-700 rounded-xl">
            <Sliders className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Rule Engine Version</h3>
            <p className="text-xs text-slate-500">Legal Metrology (Packaged Commodities) Standard 2026</p>
          </div>
        </div>

        <div className="space-y-4 text-xs">
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-800">Deterministic Rule Engine</span>
              <p className="text-slate-500 text-[11px]">Enforcing LM-001 through LM-009</p>
            </div>
            <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 font-bold rounded-lg text-[11px]">
              Active v1.0
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-800">AI Vision Engine Provider</span>
              <p className="text-slate-500 text-[11px]">Google Gemini 2.5 Vision API</p>
            </div>
            <span className="px-2.5 py-1 bg-blue-100 text-blue-800 font-bold rounded-lg text-[11px]">
              Connected
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-800">Storage Abstraction Layer</span>
              <p className="text-slate-500 text-[11px]">In-Memory / Local JSON Store (Firebase ready)</p>
            </div>
            <span className="px-2.5 py-1 bg-amber-100 text-amber-800 font-bold rounded-lg text-[11px]">
              Standalone Local
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
