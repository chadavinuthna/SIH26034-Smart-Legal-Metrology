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
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [currentInspection, setCurrentInspection] = useState(null);
  const [pendingUploadData, setPendingUploadData] = useState(null);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    setCurrentPage("dashboard");
    setCurrentInspection(null);
  };

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
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const isManufacturer = currentUser?.role === "MANUFACTURER";

  const titles = isManufacturer
    ? {
        dashboard: { title: "Manufacturer Compliance Portal", subtitle: "Pre-market packaging verification & self-audit dashboard" },
        new_inspection: { title: "Pre-Market Package Screening", subtitle: "Verify commodity packaging against Legal Metrology rules" },
        progress: { title: "Screening in Progress", subtitle: "Analyzing label declarations and verifying compliance" },
        results: { title: "Pre-Market Compliance Result", subtitle: "Packaging rule evaluation and defect breakdown" },
        history: { title: "Screening History", subtitle: "Record of prior pre-market commodity evaluations" },
        reports: { title: "Audit Report", subtitle: "Printable packaging compliance audit summary" },
        settings: { title: "System Settings", subtitle: "Rule engine and environment setup" },
      }
    : {
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
        currentUser={currentUser}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          currentUser={currentUser}
          title={currentMeta.title}
          subtitle={currentMeta.subtitle}
        />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {currentPage === "dashboard" && (
            <Dashboard
              currentUser={currentUser}
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
              currentUser={currentUser}
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
              currentUser={currentUser}
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

