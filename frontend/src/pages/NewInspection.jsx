import React, { useState, useRef } from "react";
import ImageQualityPreview from "../components/ImageQualityPreview";
import demoBiscuitsSvg from "../assets/demo_biscuits.svg";
import demoSnackSvg from "../assets/demo_snack.svg";
import {
  Upload,
  Image as ImageIcon,
  Sparkles,
  Play,
  FileCheck,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
} from "lucide-react";

export default function NewInspection({ onStartAnalysis }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [category, setCategory] = useState("Auto Detect");
  const [demoSample, setDemoSample] = useState(null);
  const fileInputRef = useRef(null);

  const categories = [
    "Auto Detect",
    "Food",
    "Cosmetics",
    "Household",
    "Electronics",
    "Other",
  ];

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    setSelectedFile(file);
    setDemoSample(null);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSelectDemoSample = (sampleType) => {
    setDemoSample(sampleType);
    setSelectedFile(null);
    if (sampleType === "compliant") {
      setImagePreview(demoBiscuitsSvg);
    } else {
      setImagePreview(demoSnackSvg);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setDemoSample(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!imagePreview && !demoSample) return;
    onStartAnalysis({
      file: selectedFile,
      category,
      demoSample,
      previewUrl: imagePreview,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="space-y-1 text-center md:text-left">
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">New Package Inspection</h2>
        <p className="text-xs text-slate-500 font-medium">
          Upload a clear image of the packaged commodity label for automated Legal Metrology compliance screening.
        </p>
      </div>

      {/* Demo Sample Loader Cards */}
      <div className="bg-amber-50/80 rounded-2xl border border-amber-200/80 p-5 space-y-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
            <Sparkles className="w-4 h-4 text-amber-600" />
            <span>Instant Demo Mode — Pre-loaded Fictional Test Package Mockups</span>
          </div>
          <span className="text-[11px] text-amber-700 font-semibold">100% Visual Data Consistency</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          <button
            type="button"
            onClick={() => handleSelectDemoSample("compliant")}
            className={`p-4 rounded-xl border text-left transition-all ${
              demoSample === "compliant"
                ? "bg-emerald-600 text-white border-emerald-700 shadow-md"
                : "bg-white text-slate-800 border-amber-200 hover:border-emerald-500 hover:bg-emerald-50/30"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-xs font-bold ${demoSample === "compliant" ? "text-white" : "text-emerald-800"}`}>
                Sample 1: Compliant Package
              </span>
              <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-md ${
                demoSample === "compliant" ? "bg-emerald-700 text-white" : "bg-emerald-100 text-emerald-800"
              }`}>
                PASS EXPECTED
              </span>
            </div>
            <p className={`text-[11px] mt-1 ${demoSample === "compliant" ? "text-emerald-100" : "text-slate-500"}`}>
              Golden Harvest Butter Biscuits (200 g) — Full manufacturer address, MRP ₹80, dates, and consumer care.
            </p>
          </button>

          <button
            type="button"
            onClick={() => handleSelectDemoSample("non_compliant")}
            className={`p-4 rounded-xl border text-left transition-all ${
              demoSample === "non_compliant"
                ? "bg-rose-600 text-white border-rose-700 shadow-md"
                : "bg-white text-slate-800 border-amber-200 hover:border-rose-500 hover:bg-rose-50/30"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-xs font-bold ${demoSample === "non_compliant" ? "text-white" : "text-rose-800"}`}>
                Sample 2: Non-Compliant Package
              </span>
              <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-md ${
                demoSample === "non_compliant" ? "bg-rose-700 text-white" : "bg-rose-100 text-rose-800"
              }`}>
                FAIL EXPECTED
              </span>
            </div>
            <p className={`text-[11px] mt-1 ${demoSample === "non_compliant" ? "text-rose-100" : "text-slate-500"}`}>
              Spicy Crunchy Bites by XYZ Snacks (500 g) — Intentionally missing address, dates, generic name, & consumer care.
            </p>
          </button>
        </div>
      </div>

      {/* Primary Upload Form */}
      <form onSubmit={handleFormSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            Package Label Image Upload
          </label>

          {!imagePreview ? (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-10 text-center transition-all bg-slate-50/50 hover:bg-blue-50/30 cursor-pointer space-y-4"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto shadow-inner border border-blue-100">
                <Upload className="w-7 h-7" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-slate-800">
                  Drag & drop package label image here, or{" "}
                  <span className="text-blue-600 hover:underline">Browse Image</span>
                </p>
                <p className="text-xs text-slate-400">
                  Supports JPG, PNG, WEBP, BMP up to 10MB
                </p>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          ) : (
            <ImageQualityPreview
              imageSrc={imagePreview}
              fileName={selectedFile?.name || (demoSample === "compliant" ? "demo_biscuits_package.svg" : "demo_snack_package.svg")}
              fileSize={selectedFile?.size}
              onRemove={handleRemove}
            />
          )}
        </div>

        {/* Product Category Dropdown */}
        <div className="space-y-2 max-w-xs">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            Product Category Metadata
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-50 text-slate-900 rounded-xl border border-slate-300 focus:border-blue-500 focus:outline-none text-xs font-bold"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-400">
            Category is used for rule applicability evaluation (e.g. Best Before dates for perishables).
          </p>
        </div>

        {/* Start Analysis Button */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            disabled={!imagePreview && !demoSample}
            className={`px-8 py-3.5 rounded-xl font-bold text-xs shadow-lg flex items-center gap-2.5 transition-all ${
              imagePreview || demoSample
                ? "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/40 hover:shadow-blue-900/60 cursor-pointer"
                : "bg-slate-200 text-slate-400 cursor-not-allowed shadow-none"
            }`}
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Start Compliance Analysis</span>
          </button>
        </div>
      </form>
    </div>
  );
}
