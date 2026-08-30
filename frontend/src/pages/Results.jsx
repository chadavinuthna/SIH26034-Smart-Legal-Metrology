import React, { useState } from 'react';
import {
  FileText,
  PlusCircle,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Printer,
  ChevronRight,
  Info,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  ArrowLeft,
  Calendar,
  Building2,
  Package,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import CheckCard from '../components/CheckCard';
import CheckDetailModal from '../components/CheckDetailModal';
import ScoreMeter from '../components/ScoreMeter';
import ExtractedInfoTable from '../components/ExtractedInfoTable';
import ImagePreviewCard from '../components/ImagePreviewCard';

export default function Results({
  inspection,
  onNewInspection,
  onViewReport,
  onPrint,
}) {
  const [activeView, setActiveView] = useState('checks'); // 'checks' | 'extracted'
  const [selectedCheck, setSelectedCheck] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!inspection) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <div className="text-slate-400 mb-2">No active inspection selected.</div>
        <button
          onClick={onNewInspection}
          className="px-4 py-2 text-xs font-bold text-white bg-[#0F2942] rounded-lg"
        >
          Start New Inspection
        </button>
      </div>
    );
  }

  const {
    inspection_id,
    status,
    score = 0,
    category = 'Food',
    product = {},
    checks = [],
    summary = {},
    image_metadata,
    created_at,
    is_demo,
  } = inspection;

  const handleOpenCheckModal = (chk) => {
    setSelectedCheck(chk);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedCheck(null);
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Top Banner: Product ID & Overall Status */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-xs font-bold text-slate-600 bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-md">
                {inspection_id}
              </span>
              <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                {category || product.category || 'General Commodity'}
              </span>
              {is_demo && (
                <span className="text-xs font-bold text-amber-800 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
                  DEMO MODE
                </span>
              )}
            </div>

            <h1 className="text-xl sm:text-2xl font-black text-[#0F2942] tracking-tight mt-2">
              {product.product_name || product.generic_name || 'Packaged Commodity'}
            </h1>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
              <span>Manufacturer: <strong className="text-slate-700">{product.manufacturer?.name || 'Unverified'}</strong></span>
              <span>•</span>
              <span className="font-mono">
                {new Date(created_at || Date.now()).toLocaleDateString('en-IN', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          </div>

          {/* Overall Status Badge & Action Controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-xl border border-slate-200">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 pl-2">
                Overall Determination:
              </span>
              <StatusBadge status={status} size="lg" />
            </div>

            <button
              onClick={onViewReport}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 text-xs font-bold text-blue-900 bg-blue-50 border border-blue-200 hover:bg-blue-100 rounded-xl shadow-2xs transition-colors"
            >
              <FileText size={15} />
              <span>Full Report</span>
            </button>

            <button
              onClick={onNewInspection}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 text-xs font-bold text-white bg-[#0F2942] hover:bg-[#18395B] rounded-xl shadow-xs transition-colors"
            >
              <PlusCircle size={15} className="text-amber-400" />
              <span>+ New Inspection</span>
            </button>
          </div>
        </div>
      </div>

      {/* Score Meter and Summary Badges */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prototype Compliance Score Meter */}
        <div className="lg:col-span-1">
          <ScoreMeter score={score} status={status} />
        </div>

        {/* Summary Count Breakdown Cards */}
        <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50 shadow-2xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">PASS</span>
              <CheckCircle2 size={16} className="text-emerald-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-700 mt-2">
              {summary.pass_count ?? summary.pass ?? 0}
            </div>
            <div className="text-[10px] text-emerald-700/80 mt-1 font-medium">
              Rules Verified
            </div>
          </div>

          <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/50 shadow-2xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-800">FAIL</span>
              <XCircle size={16} className="text-rose-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-rose-700 mt-2">
              {summary.fail_count ?? summary.fail ?? 0}
            </div>
            <div className="text-[10px] text-rose-700/80 mt-1 font-medium">
              Definite Violations
            </div>
          </div>

          <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/50 shadow-2xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-800">REVIEW</span>
              <AlertTriangle size={16} className="text-amber-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-amber-700 mt-2">
              {summary.review_count ?? summary.review ?? 0}
            </div>
            <div className="text-[10px] text-amber-700/80 mt-1 font-medium">
              Needs Officer Check
            </div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/80 shadow-2xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-600">N/A</span>
              <Layers size={16} className="text-slate-400" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-slate-700 mt-2">
              {summary.na_count ?? summary.na ?? 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-1 font-medium">
              Not Applicable
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs: Compliance Checks vs Extracted Information */}
      <div className="flex items-center gap-3 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveView('checks')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors ${
            activeView === 'checks'
              ? 'bg-[#0F2942] text-white shadow-xs'
              : 'text-slate-600 hover:bg-slate-200/60'
          }`}
        >
          Compliance Checks ({checks.length})
        </button>

        <button
          onClick={() => setActiveView('extracted')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors ${
            activeView === 'extracted'
              ? 'bg-[#0F2942] text-white shadow-xs'
              : 'text-slate-600 hover:bg-slate-200/60'
          }`}
        >
          Extracted Product Information
        </button>
      </div>

      {/* Tab 1: Compliance Checks (Two-column layout) */}
      {activeView === 'checks' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Image Preview & Details */}
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
              <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Inspected Label Image</span>
                {is_demo && (
                  <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.5 rounded">
                    DEMO MOCK
                  </span>
                )}
              </div>
              <div className="p-4 flex flex-col items-center">
                <div className="w-full h-56 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-200">
                  <img
                    src={
                      product.image_url ||
                      (is_demo ? (product.product_name?.includes('Butter') ? 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="%230F2942"/><text x="50" y="80" fill="%23FFF" font-size="28">ROYAL TREATS</text><text x="50" y="130" fill="%23FFF" font-size="20">Butter Delight Biscuits</text><text x="50" y="200" fill="%23FCD34D" font-size="16">Net Wt: 200g | MRP: Rs. 80.00 (Incl taxes)</text><text x="50" y="250" fill="%23FFF" font-size="14">Mfg: 07/2026 | Best Before: 6 mos</text><text x="50" y="300" fill="%23CBD5E1" font-size="12">ABC Foods, Hyderabad - 500076</text></svg>' : 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="%237F1D1D"/><text x="50" y="80" fill="%23FFF" font-size="28">CRUNCHY BITES</text><text x="50" y="130" fill="%23FECACA" font-size="18">Price: Rs. 120 | Net: 500g</text><text x="50" y="200" fill="%23FCA5A5" font-size="14">[MISSING ADDRESS, MFG DATE &amp; CARE]</text></svg>') : null) ||
                      '/package_placeholder.png'
                    }
                    alt="Package Label"
                    className="w-full h-full object-contain"
                  />
                </div>

                <div className="w-full mt-4 space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Image Quality</span>
                    <span className="font-semibold text-emerald-700">
                      {image_metadata?.quality_label || 'GOOD'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Text Visibility</span>
                    <span className="font-semibold text-blue-800">
                      {image_metadata?.text_visibility || 'CLEAR'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Dimensions</span>
                    <span className="font-mono text-slate-700">
                      {image_metadata?.width ? `${image_metadata.width} × ${image_metadata.height} px` : '1024 × 768 px'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Compliance Checks List */}
          <div className="lg:col-span-8 space-y-3">
            <div className="flex items-center justify-between px-1">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Statutory Legal Metrology Checks (LM-001 — LM-009)
              </h3>
              <span className="text-xs text-slate-500">
                Click any check for verbatim evidence & rationale
              </span>
            </div>

            <div className="space-y-3">
              {checks.map((chk) => (
                <CheckCard
                  key={chk.rule_id}
                  check={chk}
                  onClick={() => handleOpenCheckModal(chk)}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Extracted Product Information Table */}
      {activeView === 'extracted' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900">
              Extracted Package Declarations
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Structured representation of declarations identified by AI on visible label surfaces. Missing fields are preserved as 'Not detected'.
            </p>
          </div>
          <ExtractedInfoTable product={product} />
        </div>
      )}

      {/* Statutory Legal Disclaimer Notice */}
      <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-500 flex items-start gap-2.5">
        <Info size={16} className="text-slate-400 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>Legal Disclaimer:</strong> Prototype screening result. Final regulatory determination should be verified by an authorized Legal Metrology officer and applicable current regulations.
        </p>
      </div>

      {/* Interactive Check Details Modal */}
      <CheckDetailModal
        check={selectedCheck}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}
