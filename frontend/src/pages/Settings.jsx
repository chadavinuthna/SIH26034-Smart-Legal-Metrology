import React from 'react';
import {
  Shield,
  BookOpen,
  Cpu,
  Database,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Layers,
} from 'lucide-react';

export default function Settings({ systemConfig }) {
  const rules = [
    {
      id: 'LM-001',
      title: 'Manufacturer / Packer / Importer Details',
      section: 'Rule 6(1)(a) — Legal Metrology (Packaged Commodities) Rules',
      desc: 'Mandatory declaration of complete name and registered/operational address of the manufacturer, packer, or importer.',
      applicability: 'All packaged commodities',
    },
    {
      id: 'LM-002',
      title: 'Country of Origin Declaration',
      section: 'Rule 6(1)(aa) — Mandatory Country of Origin / Import Declarations',
      desc: 'Mandatory declaration of country of origin for imported goods or clear domestic manufacturing indication.',
      applicability: 'Mandatory for imports; conditional for domestic goods',
    },
    {
      id: 'LM-003',
      title: 'Generic / Common Commodity Name',
      section: 'Rule 6(1)(b) — Generic Identity Requirement',
      desc: 'Common or generic name of the commodity must be declared distinctly on the principal display panel (separate from brand name).',
      applicability: 'All packaged commodities',
    },
    {
      id: 'LM-004',
      title: 'Net Quantity Declaration in SI Units',
      section: 'Rule 6(1)(c) — Standard Units of Weight/Measure',
      desc: 'Net quantity in standard SI units (g, kg, ml, L, N). Must not use non-standard units.',
      applicability: 'All packaged commodities',
    },
    {
      id: 'LM-005',
      title: 'Date of Manufacture or Pre-Packing',
      section: 'Rule 6(1)(d) — Manufacturing / Packing Timeline',
      desc: 'Month and year of manufacture or pre-packing must be explicitly declared.',
      applicability: 'All packaged commodities',
    },
    {
      id: 'LM-006',
      title: 'Best Before / Use By / Expiry Date',
      section: 'Rule 6(1)(e) — Perishable Commodity Expiry Regulation',
      desc: 'Statutory expiry period or best before date for food, cosmetics, pharmaceuticals, and perishable items.',
      applicability: 'Perishable & ingestible commodities (Food, Pharma, Cosmetics)',
    },
    {
      id: 'LM-007',
      title: 'Maximum Retail Price (MRP in INR)',
      section: 'Rule 6(1)(f) — Maximum Retail Price Regulation',
      desc: 'Conspicuous declaration of Maximum Retail Price (MRP) in Indian Rupees (₹).',
      applicability: 'All retail packaged commodities',
    },
    {
      id: 'LM-008',
      title: 'MRP Tax-Inclusive Indication',
      section: 'Rule 6(1)(f) — Tax Inclusivity Requirement',
      desc: "Requirement that MRP is accompanied by 'Inclusive of all taxes' or equivalent statutory wording.",
      applicability: 'All commodities where MRP is declared',
    },
    {
      id: 'LM-009',
      title: 'Consumer Care Helpline & Redressal',
      section: 'Rule 6(1)(g) — Grievance Redressal Mechanism',
      desc: 'Name, address, telephone number, and email address of the consumer redressal cell / officer.',
      applicability: 'All packaged commodities',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Architectural Core Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 bg-blue-100 text-blue-900 rounded-lg">
            <Cpu size={18} />
          </div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
            System Architecture Principle
          </h2>
        </div>
        <div className="p-4 bg-slate-900 text-slate-100 rounded-xl font-mono text-xs leading-relaxed border border-slate-800">
          <span className="text-amber-400 font-bold">PRINCIPLE:</span> AI EXTRACTS AND INTERPRETS. DETERMINISTIC RULES MAKE COMPLIANCE DECISIONS.
          <br /><br />
          Image &rarr; Gemini Vision Extraction &rarr; Structured Pydantic Model &rarr; Deterministic Rule Engine (LM-001..LM-009) &rarr; Legal Determination &amp; Prototype Score
        </div>
      </div>

      {/* Statutory Rules Catalog */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Configured Statutory Compliance Rules
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Rules derived from the Legal Metrology (Packaged Commodities) Rules, 2011 and statutory amendments.
          </p>
        </div>

        <div className="divide-y divide-slate-100">
          {rules.map((r) => (
            <div key={r.id} className="py-3.5 first:pt-0 last:pb-0">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    {r.id}
                  </span>
                  <h4 className="text-xs font-bold text-slate-900">{r.title}</h4>
                </div>
                <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  {r.applicability}
                </span>
              </div>
              <div className="text-[11px] font-mono text-blue-800 mt-1">{r.section}</div>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* System Runtime Configuration */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-4">
        <h3 className="text-base font-bold text-slate-900">System Diagnostic Information</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-slate-500 block">AI Service Status</span>
            <strong className={`block mt-1 ${systemConfig?.ai_service_configured ? 'text-emerald-700' : 'text-amber-700'}`}>
              {systemConfig?.ai_service_configured ? 'Configured (Gemini Active)' : 'Demo Mode (No API Key)'}
            </strong>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-slate-500 block">Active Model</span>
            <strong className="text-slate-800 block mt-1 font-mono">
              {systemConfig?.model || 'gemini-2.5-flash'}
            </strong>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-slate-500 block">Active Storage Engine</span>
            <strong className="text-slate-800 block mt-1">
              Local JSON / Memory Abstraction
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}
