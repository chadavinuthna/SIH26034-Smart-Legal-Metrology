/**
 * API Service for communicating with the FastAPI Legal Metrology Backend.
 */

const API_BASE = '/api';

export async function analyzePackage(imageFile, category = 'Auto Detect', demoSampleId = null) {
  const formData = new FormData();
  if (imageFile) {
    formData.append('image', imageFile);
  }
  formData.append('category', category || 'Auto Detect');
  if (demoSampleId) {
    formData.append('demo_sample', demoSampleId);
  }

  const response = await fetch(`${API_BASE}/inspection/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = 'Failed to analyze package label.';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function demoAnalyzePackage(sampleType = 'sample_compliant') {
  const response = await fetch(`${API_BASE}/inspection/demo-analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ sample_type: sampleType }),
  });

  if (!response.ok) {
    let errorMsg = 'Demo simulation failed.';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function getInspectionHistory() {
  try {
    const response = await fetch(`${API_BASE}/inspection/history`);
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    console.warn('Backend history unreachable, using local storage cache:', err);
  }
  return [];
}

export async function getInspectionById(inspectionId) {
  const response = await fetch(`${API_BASE}/inspection/${inspectionId}`);
  if (!response.ok) {
    throw new Error(`Inspection record ${inspectionId} not found.`);
  }
  return await response.json();
}

export async function getSystemConfig() {
  try {
    const response = await fetch(`${API_BASE}/inspection/status/config`);
    if (response.ok) {
      return await response.json();
    }
  } catch (_) {}
  return {
    ai_service_configured: false,
    model: 'gemini-2.5-flash',
    compliance_rules_loaded: 9,
    storage_mode: 'local_json_memory',
    prototype_version: '1.0.0-SIH26034',
  };
}
