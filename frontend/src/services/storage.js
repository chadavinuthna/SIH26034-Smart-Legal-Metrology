/**
 * Local Storage abstraction for client-side inspection history caching and active session state.
 */

const STORAGE_KEY = 'sih26034_inspections_history';
const OFFICER_KEY = 'sih26034_officer_session';
const CURRENT_INSPECTION_KEY = 'sih26034_current_inspection';

export function getStoredInspections() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Failed to read from localStorage:', e);
    return [];
  }
}

export function saveInspectionToLocal(inspection) {
  try {
    const current = getStoredInspections();
    // Remove if already exists and prepend
    const filtered = current.filter(item => item.inspection_id !== inspection.inspection_id);
    filtered.unshift(inspection);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered.slice(0, 50))); // Keep last 50
    localStorage.setItem(CURRENT_INSPECTION_KEY, JSON.stringify(inspection));
  } catch (e) {
    console.error('Failed to write to localStorage:', e);
  }
}

export function getCurrentInspection() {
  try {
    const raw = localStorage.getItem(CURRENT_INSPECTION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function setCurrentInspection(inspection) {
  try {
    localStorage.setItem(CURRENT_INSPECTION_KEY, JSON.stringify(inspection));
  } catch (e) {}
}

export function getOfficerSession() {
  try {
    const raw = localStorage.getItem(OFFICER_KEY);
    return raw ? JSON.parse(raw) : { officer_id: 'LM-INSP-4092', name: 'Inspector A. Sharma', department: 'Legal Metrology Department' };
  } catch (e) {
    return { officer_id: 'LM-INSP-4092', name: 'Inspector A. Sharma', department: 'Legal Metrology Department' };
  }
}

export function setOfficerSession(sessionData) {
  try {
    localStorage.setItem(OFFICER_KEY, JSON.stringify(sessionData));
  } catch (e) {}
}

export function clearOfficerSession() {
  try {
    localStorage.removeItem(OFFICER_KEY);
  } catch (e) {}
}
