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
    setPendingUploadData(uploadData);
    setCurrentPage("progress");
  };

  const handleAnalysisCompleted = async () => {
    if (!pendingUploadData) return;
    const result = await analyzePackageImage({
      file: pendingUploadData.file,
      category: pendingUploadData.category,
      demoSample: pendingUploadData.demoSample,
    });
    // Attach preview URL for UI display
    result.previewUrl = pendingUploadData.previewUrl;
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
            <AnalysisProgress onComplete={handleAnalysisCompleted} />
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
