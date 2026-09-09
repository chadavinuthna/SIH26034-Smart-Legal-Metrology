/**
 * API Service for communicating with the FastAPI Legal Metrology Backend.
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const API_BASE = '/api';

export async function analyzePackage(imageFiles, category = 'Auto Detect', demoSampleId = null) {
  const formData = new FormData();
  const files = Array.isArray(imageFiles) ? imageFiles : (imageFiles ? [imageFiles] : []);
  files.forEach((file) => formData.append('images', file));
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

export async function getComplianceRules() {
  const response = await fetch(`${API_BASE}/inspection/rules`);

  if (!response.ok) {
    throw new Error('Failed to load compliance rules.');
  }

  return await response.json();
}

export async function addComplianceRule(rule) {
  const response = await fetch(`${API_BASE}/inspection/rules`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(rule),
  });

  if (!response.ok) {
    let errorMsg = 'Failed to add compliance rule.';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function updateComplianceRule(ruleId, rule) {
  const response = await fetch(
    `${API_BASE}/inspection/rules/${encodeURIComponent(ruleId)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(rule),
    }
  );

  if (!response.ok) {
    let errorMsg = 'Failed to update compliance rule.';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function disableComplianceRule(ruleId) {
  const response = await fetch(
    `${API_BASE}/inspection/rules/${encodeURIComponent(ruleId)}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    let errorMsg = 'Failed to disable compliance rule.';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.json();
}



export async function loginUser(userId, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, password: password }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Invalid user ID or password.");
  }
  return response.json();
}
