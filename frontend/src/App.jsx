import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NewInspection from './pages/NewInspection';
import AnalysisProgress from './pages/AnalysisProgress';
import Results from './pages/Results';
import History from './pages/History';
import Report from './pages/Report';
import Settings from './pages/Settings';

import {
  analyzePackage,
  demoAnalyzePackage,
  getInspectionHistory,
  getSystemConfig,
} from './services/api';
import {
  getStoredInspections,
  saveInspectionToLocal,
  getCurrentInspection,
  setCurrentInspection,
  getOfficerSession,
  setOfficerSession,
  clearOfficerSession,
} from './services/storage';

export default function App() {
  const [officer, setOfficer] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [inspections, setInspections] = useState([]);
  const [currentInspection, setCurrentInspectionState] = useState(null);
  const [systemConfig, setSystemConfig] = useState(null);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Analysis Progress Transient State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzingImagePreview, setAnalyzingImagePreview] = useState(null);
  const [analyzingCategory, setAnalyzingCategory] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  // Load Session & System Diagnostics on mount
  useEffect(() => {
    const savedOfficer = getOfficerSession();
    if (savedOfficer) {
      setOfficer(savedOfficer);
    }

    const savedCurrent = getCurrentInspection();
    if (savedCurrent) {
      setCurrentInspectionState(savedCurrent);
    }

    // Load initial inspections from backend or local storage
    loadInspections();

    // Check system status
    getSystemConfig()
      .then((cfg) => setSystemConfig(cfg))
      .catch((_) => {});
  }, []);

  const loadInspections = async () => {
    try {
      const backendHistory = await getInspectionHistory();
      if (backendHistory && backendHistory.length > 0) {
        setInspections(backendHistory);
        return;
      }
    } catch (e) {
      console.warn('Backend history fetch failed, using local storage:', e);
    }

    // Fallback to local storage
    const local = getStoredInspections();
    setInspections(local);
  };

  const handleLogin = (sessionData) => {
    setOfficer(sessionData);
    setOfficerSession(sessionData);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    setOfficer(null);
    clearOfficerSession();
  };

  const handleStartAnalysis = async ({ file, category, demoSampleId, previewUrl }) => {
    setIsAnalyzing(true);
    setActiveTab('analysis');
    setAnalyzingImagePreview(previewUrl);
    setAnalyzingCategory(category);
    setAnalysisError(null);

    try {
      let result;
      if (demoSampleId) {
        // Run demo analysis through the deterministic compliance engine
        result = await demoAnalyzePackage(demoSampleId);
      } else {
        // Run live package analysis (image -> Gemini AI extraction -> Rule engine)
        result = await analyzePackage(file, category);
      }

      // Attach local preview URL if not present
      if (!result.product.image_url && previewUrl) {
        result.product.image_url = previewUrl;
      }

      // Small staged delay so user sees pipeline completing
      setTimeout(() => {
        setCurrentInspectionState(result);
        saveInspectionToLocal(result);
        setInspections((prev) => {
          const filtered = prev.filter((i) => i.inspection_id !== result.inspection_id);
          return [result, ...filtered];
        });
        setIsAnalyzing(false);
        setActiveTab('results');
      }, 3800);
    } catch (err) {
      console.error('Inspection analysis failed:', err);
      setAnalysisError(err.message || 'Inspection analysis failed. Please try again.');
      setIsAnalyzing(false);
    }
  };

  const handleStartDemoInspection = (demoId) => {
    setActiveTab('new-inspection');
    // Pre-populate and run
    handleStartAnalysis({
      file: null,
      category: 'Food',
      demoSampleId: demoId,
      previewUrl:
        demoId === 'sample_compliant'
          ? 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="%230F2942"/><text x="50" y="80" fill="%23FFF" font-size="28">ROYAL TREATS</text><text x="50" y="130" fill="%23FFF" font-size="20">Butter Delight Biscuits</text><text x="50" y="200" fill="%23FCD34D" font-size="16">Net Wt: 200g | MRP: Rs. 80.00 (Incl taxes)</text><text x="50" y="250" fill="%23FFF" font-size="14">Mfg: 07/2026 | Best Before: 6 mos</text><text x="50" y="300" fill="%23CBD5E1" font-size="12">ABC Foods, Hyderabad - 500076</text></svg>'
          : 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="%237F1D1D"/><text x="50" y="80" fill="%23FFF" font-size="28">CRUNCHY BITES</text><text x="50" y="130" fill="%23FECACA" font-size="18">Price: Rs. 120 | Net: 500g</text><text x="50" y="200" fill="%23FCA5A5" font-size="14">[MISSING ADDRESS, MFG DATE &amp; CARE]</text></svg>',
    });
  };

  const handleSelectInspection = (insp) => {
    setCurrentInspectionState(insp);
    setCurrentInspection(insp);
    setActiveTab('results');
  };

  const handlePrint = () => {
    window.print();
  };

  // If not logged in, render Login portal
  if (!officer) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onNavigate={(tab) => {
          if (!isAnalyzing) setActiveTab(tab);
        }}
        officer={officer}
        onLogout={handleLogout}
        systemConfig={systemConfig}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          onNavigate={(tab) => {
            if (!isAnalyzing) setActiveTab(tab);
          }}
          systemConfig={systemConfig}
          setIsMobileOpen={setIsMobileOpen}
          onPrint={handlePrint}
          hasActiveInspection={Boolean(currentInspection)}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'dashboard' && (
            <Dashboard
              inspections={inspections}
              onNavigate={setActiveTab}
              onSelectInspection={handleSelectInspection}
              onStartDemoInspection={handleStartDemoInspection}
              systemConfig={systemConfig}
            />
          )}

          {activeTab === 'new-inspection' && (
            <NewInspection
              onStartAnalysis={handleStartAnalysis}
              systemConfig={systemConfig}
            />
          )}

          {activeTab === 'analysis' && (
            <AnalysisProgress
              imagePreview={analyzingImagePreview}
              category={analyzingCategory}
              error={analysisError}
            />
          )}

          {activeTab === 'results' && (
            <Results
              inspection={currentInspection}
              onNewInspection={() => setActiveTab('new-inspection')}
              onViewReport={() => setActiveTab('reports')}
              onPrint={handlePrint}
            />
          )}

          {activeTab === 'history' && (
            <History
              inspections={inspections}
              onSelectInspection={handleSelectInspection}
              onNewInspection={() => setActiveTab('new-inspection')}
            />
          )}

          {activeTab === 'reports' && (
            <Report
              inspection={currentInspection || inspections[0]}
              officer={officer}
              onBack={() => setActiveTab('results')}
              onPrint={handlePrint}
            />
          )}

          {activeTab === 'settings' && (
            <Settings systemConfig={systemConfig} />
          )}
        </main>
      </div>
    </div>
  );
}
