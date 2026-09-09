import React, { useState, useRef, useEffect } from "react";
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
  Camera,
  AlertCircle,
  X,
} from "lucide-react";

export default function NewInspection({ onStartAnalysis }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [category, setCategory] = useState("Auto Detect");
  const [demoSample, setDemoSample] = useState(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const categories = [
    "Auto Detect",
    "Food",
    "Cosmetics",
    "Household",
    "Electronics",
    "Other",
  ];

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [cameraStream]);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    setSelectedFile(file);
    setDemoSample(null);
    setCameraError(null);
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
    if (isCameraOpen) closeCamera();
    setDemoSample(sampleType);
    setSelectedFile(null);
    setCameraError(null);
    if (sampleType === "compliant") {
      setImagePreview(demoBiscuitsSvg);
    } else {
      setImagePreview(demoSnackSvg);
    }
  };

  const openCamera = async () => {
    try {
      setCameraError(null);

      if (!navigator.mediaDevices?.getUserMedia) {
        setCameraError("Camera access is not supported by this browser.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      });

      setCameraStream(stream);
      setIsCameraOpen(true);

      // Wait until the video element is mounted in DOM
      setTimeout(async () => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          try {
            await videoRef.current.play();
          } catch (err) {
            console.error("Video play error:", err);
          }
        }
      }, 100);
    } catch (error) {
      console.error("Camera error:", error);
      if (error.name === "NotAllowedError") {
        setCameraError("Camera permission was denied. Please allow camera access in your browser.");
      } else if (error.name === "NotFoundError") {
        setCameraError("No camera device was detected on this system.");
      } else {
        setCameraError("Unable to open the camera: " + (error.message || "Unknown error"));
      }
    }
  };

  const closeCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
    }
    setCameraStream(null);
    setIsCameraOpen(false);
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) {
      setCameraError("Camera is not ready. Please try again.");
      return;
    }

    const width = video.videoWidth;
    const height = video.videoHeight;

    if (!width || !height) {
      setCameraError("Camera stream is not ready. Please wait a moment and try again.");
      return;
    }

    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d");
    if (!context) {
      setCameraError("Unable to prepare photo capture.");
      return;
    }

    context.drawImage(video, 0, 0, width, height);

    try {
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            setCameraError("Unable to capture photo. Please try again.");
            return;
          }

          const file = new File(
            [blob],
            `camera-package-${Date.now()}.jpg`,
            { type: "image/jpeg" }
          );

          closeCamera();
          processFile(file);
        },
        "image/jpeg",
        0.92
      );
    } catch (error) {
      console.error("Photo capture error:", error);
      setCameraError("Unable to capture photo. Please try again.");
    }
  };

  const handleRemove = () => {
    if (isCameraOpen) closeCamera();
    setSelectedFile(null);
    setImagePreview(null);
    setDemoSample(null);
    setCameraError(null);
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
        {/* Camera Permission / Device Error Banner */}
        {cameraError && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center justify-between text-xs text-rose-800 animate-in fade-in">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{cameraError}</span>
            </div>
            <button
              type="button"
              onClick={() => setCameraError(null)}
              className="p-1 hover:bg-rose-100 rounded-lg text-rose-500 transition-colors cursor-pointer"
              title="Dismiss error"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            Package Label Image Upload & Camera Capture
          </label>

          {/* Live Camera Viewfinder */}
          {isCameraOpen ? (
            <div className="bg-slate-950 rounded-2xl p-4 space-y-4 border border-slate-800 shadow-inner">
              <div className="relative w-full max-w-2xl mx-auto bg-black rounded-xl overflow-hidden shadow-inner flex items-center justify-center min-h-[280px]">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-auto max-h-[420px] object-contain"
                />
                <canvas ref={canvasRef} className="hidden" />
              </div>

              <div className="flex justify-center gap-3 pt-1">
                <button
                  type="button"
                  onClick={capturePhoto}
                  className="px-6 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition-all shadow-md flex items-center gap-2 cursor-pointer"
                >
                  <Camera className="w-4 h-4" />
                  <span>Capture Photo</span>
                </button>

                <button
                  type="button"
                  onClick={closeCamera}
                  className="px-6 py-2.5 text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 rounded-xl transition-all shadow-xs cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : !imagePreview ? (
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
                  Drag & drop package label image here, or use the options below
                </p>
                <p className="text-xs text-slate-400">
                  Supports JPG, PNG, WEBP, BMP up to 10MB
                </p>
              </div>

              {/* Direct Action Buttons: Browse and Capture Photo */}
              <div className="flex items-center justify-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  className="px-4 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-xl shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Browse Image</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    openCamera();
                  }}
                  className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Capture Photo</span>
                </button>
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
