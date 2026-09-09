import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import NewInspection from "./pages/NewInspection";
import AnalysisProgress from "./pages/AnalysisProgress";
import Results from "./pages/Results";
import History from "./pages/History";
import Report from "./pages/Report";
import SettingsPlaceholder from "./pages/SettingsPlaceholder";
import { analyzePackageImage } from "./services/api";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Default logged in for instant evaluation
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [currentInspection, setCurrentInspection] = useState(null);
  const [pendingUploadData, setPendingUploadData] = useState(null);

  // Flow handlers
  const handleStartAnalysis = (uploadData) => {
    const files = uploadData?.files || (uploadData?.file ? [uploadData.file] : []);
    const previewUrls = uploadData?.previewUrls || (uploadData?.previewUrl ? [uploadData.previewUrl] : []);

    setPendingUploadData({
      ...uploadData,
      files,
      previewUrls,
      file: uploadData?.file || files[0] || null,
      previewUrl: uploadData?.previewUrl || previewUrls[0] || null,
      category: uploadData?.category || "Auto Detect",
      demoSample: uploadData?.demoSample || null,
    });
    setCurrentPage("progress");
  };

  const handleAnalysisSuccess = (result) => {
    if (result && pendingUploadData) {
      if (!result.previewUrls && pendingUploadData.previewUrls?.length) {
        result.previewUrls = pendingUploadData.previewUrls;
      }
      if (!result.previewUrl && (pendingUploadData.previewUrl || pendingUploadData.previewUrls?.[0])) {
        result.previewUrl = pendingUploadData.previewUrl || pendingUploadData.previewUrls[0];
      }
    }
    setCurrentInspection(result);
    setCurrentPage("results");
  };

  const handleAnalysisCompleted = async () => {
    if (!pendingUploadData) return;
    const files = pendingUploadData.files && pendingUploadData.files.length > 0
      ? pendingUploadData.files
      : (pendingUploadData.file ? [pendingUploadData.file] : []);

    const result = await analyzePackageImage({
      files,
      file: pendingUploadData.file || files[0] || null,
      category: pendingUploadData.category,
      demoSample: pendingUploadData.demoSample,
    });

    // Attach both preview URLs array and primary preview URL for UI display
    result.previewUrls = pendingUploadData.previewUrls || (pendingUploadData.previewUrl ? [pendingUploadData.previewUrl] : []);
    result.previewUrl = pendingUploadData.previewUrl || result.previewUrls[0] || null;
    setCurrentInspection(result);
    setCurrentPage("results");
  };

  const handleViewInspectionResult = (inspection) => {
    setCurrentInspection(inspection);
    setCurrentPage("results");
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  const titles = {
    dashboard: { title: "Package Compliance Dashboard", subtitle: "Legal Metrology inspection and compliance screening" },
    new_inspection: { title: "New Package Inspection", subtitle: "Upload package image for Legal Metrology screening" },
    progress: { title: "Analysis in Progress", subtitle: "Reading package label and executing rule engine" },
    results: { title: "Compliance Assessment Result", subtitle: "Legal Metrology evaluation and rule breakdown" },
    history: { title: "Inspection History", subtitle: "Log of past packaged commodity screenings" },
    reports: { title: "Official Inspection Report", subtitle: "Printable Legal Metrology compliance document" },
    settings: { title: "System Settings", subtitle: "Rule engine and environment setup" },
  };

  const currentMeta = titles[currentPage] || titles.dashboard;

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar */}
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        onLogout={() => setIsAuthenticated(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={currentMeta.title} subtitle={currentMeta.subtitle} />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {currentPage === "dashboard" && (
            <Dashboard
              onStartNewInspection={() => setCurrentPage("new_inspection")}
              onViewInspectionResult={handleViewInspectionResult}
            />
          )}

          {currentPage === "new_inspection" && (
            <NewInspection onStartAnalysis={handleStartAnalysis} />
          )}

          {currentPage === "progress" && (
            <AnalysisProgress
              uploadData={pendingUploadData}
              onAnalysisSuccess={handleAnalysisSuccess}
              onComplete={handleAnalysisCompleted}
              onCancel={() => setCurrentPage("new_inspection")}
            />
          )}

          {currentPage === "results" && (
            <Results
              inspection={currentInspection}
              onNewInspection={() => setCurrentPage("new_inspection")}
              onViewReport={() => setCurrentPage("reports")}
              onBackToDashboard={() => setCurrentPage("dashboard")}
            />
          )}

          {currentPage === "history" && (
            <History onViewInspectionResult={handleViewInspectionResult} />
          )}

          {currentPage === "reports" && (
            <Report
              inspection={currentInspection}
              onBackToResults={() => setCurrentPage("results")}
            />
          )}

          {currentPage === "settings" && <SettingsPlaceholder />}
        </main>
      </div>
    </div>
  );
}
