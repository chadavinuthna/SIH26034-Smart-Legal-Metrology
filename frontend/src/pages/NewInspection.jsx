import React, { useState, useRef } from 'react';
import {
  Upload,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  FileText,
  Sparkles,
  ArrowRight,
  Shield,
  Layers,
  Info,
} from 'lucide-react';
import ImagePreviewCard from '../components/ImagePreviewCard';
import { DEMO_PRODUCTS } from '../data/demoSamples';

export default function NewInspection({
  onStartAnalysis,
  systemConfig,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [category, setCategory] = useState('Auto Detect');
  const [activeDemoSample, setActiveDemoSample] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const fileInputRef = useRef(null);

  const categories = [
    'Auto Detect',
    'Food',
    'Cosmetics',
    'Household',
    'Electronics',
    'Other',
  ];

  const handleFileChange = (file) => {
    if (!file) return;
    setErrorMsg(null);

    // Validate mime type
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please upload a valid image file (JPEG, PNG, WEBP).');
      return;
    }

    // Validate size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('Image file size exceeds 10MB limit. Please upload an optimized label image.');
      return;
    }

    setSelectedFile(file);
    setActiveDemoSample(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSelectDemo = (demoProd) => {
    setSelectedFile(null);
    setActiveDemoSample(demoProd.id);
    setImagePreview(demoProd.image_url);
    setCategory(demoProd.category);
    setErrorMsg(null);
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setActiveDemoSample(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = () => {
    if (!imagePreview) {
      setErrorMsg('Please upload a package image or select a demo sample to proceed.');
      return;
    }

    onStartAnalysis({
      file: selectedFile,
      category: category,
      demoSampleId: activeDemoSample,
      previewUrl: imagePreview,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Notice Banner */}
      <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-xl flex items-start gap-3 text-xs text-blue-900">
        <Info size={18} className="text-blue-700 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-bold">Inspection Requirement:</strong> Ensure that the principal display panel, manufacturer declaration block, net weight, and MRP markings are clearly legible in the uploaded label image.
        </div>
      </div>

      {/* Error Callout if any */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800 animate-in fade-in duration-150">
          <AlertCircle size={18} className="text-rose-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Upload Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
        {/* Upload Dropzone / Preview */}
        {!imagePreview ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
              isDragging
                ? 'border-blue-500 bg-blue-50/50'
                : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50/60'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept="image/jpeg,image/png,image/webp,image/jpg"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files?.[0])}
            />

            <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto text-blue-900 mb-4 shadow-2xs">
              <Upload size={28} className="stroke-[2.2]" />
            </div>

            <h3 className="text-base font-bold text-slate-900">
              Drag & drop package label image here
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Supports high-resolution JPEG, PNG, or WebP images of packaged commodities.
            </p>

            <button
              type="button"
              className="mt-4 px-4 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg shadow-2xs transition-colors"
            >
              Browse Image from Device
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <ImagePreviewCard
              imageSrc={imagePreview}
              fileInfo={
                selectedFile
                  ? { name: selectedFile.name, size: selectedFile.size }
                  : { name: `${activeDemoSample || 'sample'}_package_mock.svg` }
              }
              imageMetadata={{
                width: selectedFile ? 1280 : 600,
                height: selectedFile ? 720 : 400,
                quality_label: 'GOOD',
                text_visibility: 'CLEAR',
              }}
              onRemove={handleRemoveImage}
              onReplace={() => fileInputRef.current?.click()}
            />
            <input
              type="file"
              ref={fileInputRef}
              accept="image/jpeg,image/png,image/webp,image/jpg"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files?.[0])}
            />
          </div>
        )}

        {/* Form Controls: Category Selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Product Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-2xs"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-slate-400 mt-1">
              Select category to tune statutory expiry / best-before rule applicability.
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Inspection Mode
            </label>
            <div className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 flex items-center justify-between">
              <span className="font-semibold">
                {activeDemoSample
                  ? 'Demo Simulation Sample'
                  : selectedFile
                  ? 'Custom Uploaded Package'
                  : 'Awaiting Image Selection'}
              </span>
              {systemConfig?.ai_service_configured && selectedFile && (
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                  Gemini Vision
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Start Analysis Button */}
        <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-500">
            {imagePreview
              ? 'Ready for automated declaration extraction.'
              : 'Select or upload an image to enable compliance screening.'}
          </div>

          <button
            type="button"
            disabled={!imagePreview}
            onClick={handleSubmit}
            className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-xs font-extrabold shadow-md transition-all ${
              imagePreview
                ? 'text-white bg-[#0F2942] hover:bg-[#18395B] hover:shadow-lg cursor-pointer transform hover:-translate-y-0.5'
                : 'text-slate-400 bg-slate-200 cursor-not-allowed shadow-none'
            }`}
          >
            <span>Start Compliance Analysis</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Demo Samples Quick Loader */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-[10px] font-black uppercase tracking-wider text-amber-800 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
            DEMO MODE
          </span>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Instant Test Packages (Zero Setup Required)
          </h4>
        </div>
        <p className="text-xs text-slate-500 mb-4">
          Sample data — not an actual government inspection. Click a demo package to automatically load its label image for immediate rule testing:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {DEMO_PRODUCTS.map((prod) => {
            const isSelected = activeDemoSample === prod.id;
            return (
              <button
                key={prod.id}
                type="button"
                onClick={() => handleSelectDemo(prod)}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/70 shadow-2xs'
                    : 'border-slate-200 bg-slate-50 hover:bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">
                    {prod.name}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      prod.expected_status === 'COMPLIANT'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {prod.expected_status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                  {prod.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
