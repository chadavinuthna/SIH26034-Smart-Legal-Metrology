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
  Plus,
  Trash2,
} from "lucide-react";

export default function NewInspection({ onStartAnalysis }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
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

  const addFiles = (filesToAdd) => {
    if (!filesToAdd || filesToAdd.length === 0) return;

    setCameraError(null);

    const incoming = Array.from(filesToAdd);
    // Validate image format and filter duplicate files based on name, size, and lastModified
    const validFiles = incoming.filter((file) => {
      const isImg =
        file.type?.startsWith("image/") ||
        /\.(jpe?g|png|webp|bmp)$/i.test(file.name);
      if (!isImg) return false;

      const isDup = selectedFiles.some(
        (existing) =>
          existing.name === file.name &&
          existing.size === file.size &&
          existing.lastModified === file.lastModified
      );
      return !isDup;
    });

    if (validFiles.length === 0) {
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    const isSwitchingFromDemo = Boolean(demoSample);
    if (isSwitchingFromDemo) {
      setDemoSample(null);
    }

    const readPromises = validFiles.map(
      (file) =>
        new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve({
              id: `img-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
              file,
              url: reader.result,
              name: file.name,
              size: file.size,
            });
          };
          reader.readAsDataURL(file);
        })
    );

    Promise.all(readPromises).then((newItems) => {
      setSelectedFiles((prev) => (isSwitchingFromDemo ? [...validFiles] : [...prev, ...validFiles]));
      setImagePreviews((prev) => (isSwitchingFromDemo ? [...newItems] : [...prev, ...newItems]));
      if (fileInputRef.current) fileInputRef.current.value = "";
    });
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      addFiles(files);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      addFiles(files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSelectDemoSample = (sampleType) => {
    if (isCameraOpen) closeCamera();
    setDemoSample(sampleType);
    setSelectedFiles([]);
    setCameraError(null);
    const preview = sampleType === "compliant" ? demoBiscuitsSvg : demoSnackSvg;
    const sampleName =
      sampleType === "compliant"
        ? "demo_biscuits_package.svg"
        : "demo_snack_package.svg";
    setImagePreviews([
      {
        id: `demo-${sampleType}`,
        file: null,
        url: preview,
        name: sampleName,
        size: null,
      },
    ]);
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
          addFiles([file]);
        },
        "image/jpeg",
        0.92
      );
    } catch (error) {
      console.error("Photo capture error:", error);
      setCameraError("Unable to capture photo. Please try again.");
    }
  };

  const handleRemove = (indexToRemove) => {
    if (isCameraOpen) closeCamera();
    if (demoSample) {
      handleClearAll();
      return;
    }

    const itemToRemove = imagePreviews[indexToRemove];
    const newPreviews = imagePreviews.filter((_, idx) => idx !== indexToRemove);
    const newFiles = itemToRemove?.file
      ? selectedFiles.filter((f) => f !== itemToRemove.file)
      : selectedFiles.filter((_, idx) => idx !== indexToRemove);

    setImagePreviews(newPreviews);
    setSelectedFiles(newFiles);
    setCameraError(null);

    if (newPreviews.length === 0) {
      handleClearAll();
    }
  };

  const handleClearAll = () => {
    if (isCameraOpen) closeCamera();
    setSelectedFiles([]);
    setImagePreviews([]);
    setDemoSample(null);
    setCameraError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (imagePreviews.length === 0 && !demoSample) return;
    const filesToSend = imagePreviews.map((p) => p.file).filter(Boolean);
    onStartAnalysis({
      files: filesToSend.length > 0 ? filesToSend : selectedFiles,
      previewUrls: imagePreviews.map((p) => p.url),
      // Backward compatibility for existing parent/services expecting a single file
      file: (filesToSend.length > 0 ? filesToSend[0] : selectedFiles[0]) || null,
      previewUrl: imagePreviews[0]?.url || null,
      category,
      demoSample,
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

        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              Package Label Images (Same Product)
            </label>
            {imagePreviews.length > 0 && (
              <span className="text-[11px] font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-md border border-blue-200 self-start sm:self-auto">
                {imagePreviews.length} {imagePreviews.length === 1 ? "Image" : "Images"} Attached
              </span>
            )}
          </div>
          <p className="text-[11px] text-slate-500 font-medium">
            Upload all sides and panels of the <strong>same packaged product</strong> (e.g. Front, Back, MRP/Date side panel, Nutrition declaration) to extract and combine compliance declarations.
          </p>

          {/* Always mounted hidden multi-file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />

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
          ) : imagePreviews.length === 0 ? (
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
                  Drag &amp; drop package label image(s) here, or browse files
                </p>
                <p className="text-xs text-slate-400">
                  Select one or multiple images for the same product (JPG, PNG, WEBP, BMP up to 10MB each)
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
                  <span>Browse Images</span>
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
            </div>
          ) : (
            <div className="space-y-4">
              {/* Product Multi-Image Toolbar */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 text-slate-700 font-medium">
                  <FileCheck className="w-4 h-4 text-blue-600 shrink-0" />
                  <span>
                    Product images: <strong>{imagePreviews.length} {imagePreviews.length === 1 ? "panel" : "panels"} ready</strong> for Legal Metrology screening.
                  </span>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-2xs transition-colors flex items-center gap-1.5 cursor-pointer text-xs"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Image</span>
                  </button>

                  <button
                    type="button"
                    onClick={openCamera}
                    className="px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-bold rounded-lg shadow-2xs transition-colors flex items-center gap-1.5 cursor-pointer text-xs"
                  >
                    <Camera className="w-3.5 h-3.5 text-blue-600" />
                    <span>Take Photo</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleClearAll}
                    className="px-2.5 py-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors font-semibold text-xs flex items-center gap-1 cursor-pointer"
                    title="Remove all uploaded images"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Clear All</span>
                  </button>
                </div>
              </div>

              {/* Gallery Grid */}
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"
              >
                {imagePreviews.map((img, idx) => (
                  <div
                    key={img.id || idx}
                    className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs hover:border-blue-400 transition-all flex flex-col group"
                  >
                    {/* Card Header */}
                    <div className="px-3 py-2 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between">
                      <span className="text-[11px] font-extrabold text-blue-900 bg-blue-100/70 px-2 py-0.5 rounded-md border border-blue-200/60">
                        Image {idx + 1}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemove(idx)}
                        className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                        title={`Remove Image ${idx + 1}`}
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    {/* Thumbnail Preview */}
                    <div className="w-full aspect-4/3 bg-slate-950 flex items-center justify-center p-2 relative overflow-hidden">
                      <img
                        src={img.url}
                        alt={`Product Image ${idx + 1}`}
                        className="w-full h-full object-contain"
                      />
                    </div>

                    {/* File Caption & Status */}
                    <div className="p-3 bg-white space-y-1 mt-auto border-t border-slate-100">
                      <p className="text-xs font-bold text-slate-800 truncate" title={img.name}>
                        {img.name || `Package Image ${idx + 1}`}
                      </p>
                      <div className="flex items-center justify-between text-[11px] text-slate-400">
                        <span>{img.size ? `${(img.size / 1024).toFixed(1)} KB` : "Demo Mockup"}</span>
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>Ready</span>
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Inline "Add Another Image" Tile */}
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-4 flex flex-col items-center justify-center text-center cursor-pointer bg-slate-50/50 hover:bg-blue-50/30 transition-all min-h-[200px] space-y-2 group"
                  title="Click or drop another image here"
                >
                  <div className="w-10 h-10 rounded-xl bg-blue-50 group-hover:bg-blue-100 text-blue-600 flex items-center justify-center transition-colors shadow-2xs">
                    <Plus className="w-5 h-5" />
                  </div>
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-slate-700 group-hover:text-blue-600 transition-colors">
                      + Add Another Image
                    </p>
                    <p className="text-[11px] text-slate-400 max-w-[180px]">
                      Upload or drop another side / panel of this same product
                    </p>
                  </div>
                </div>
              </div>
            </div>
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
            disabled={imagePreviews.length === 0 && !demoSample}
            className={`px-8 py-3.5 rounded-xl font-bold text-xs shadow-lg flex items-center gap-2.5 transition-all ${
              imagePreviews.length > 0 || demoSample
                ? "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/40 hover:shadow-blue-900/60 cursor-pointer"
                : "bg-slate-200 text-slate-400 cursor-not-allowed shadow-none"
            }`}
          >
            <Play className="w-4 h-4 fill-current" />
            <span>
              {imagePreviews.length > 1
                ? `Start Compliance Analysis (${imagePreviews.length} Images)`
                : "Start Compliance Analysis"}
            </span>
          </button>
        </div>
      </form>
    </div>
  );
}
